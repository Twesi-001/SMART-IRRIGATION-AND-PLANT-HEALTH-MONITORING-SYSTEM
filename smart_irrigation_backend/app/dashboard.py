from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required # type: ignore
from sqlalchemy import func, desc # type: ignore

from app.extensions import db
from app.models import SensorReading, SensorNode, Alert, PumpCommand

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Get all dashboard data in one call for a specific node"""
    node_id = request.args.get('node_id', 1, type=int)
    
    # Check if node exists
    node = SensorNode.query.get(node_id)
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # 1. Latest reading
    latest = SensorReading.query.filter_by(node_id=node_id)\
                               .order_by(desc(SensorReading.recorded_at)).first()
    
    # 2. Recent readings (last 24 hours)
    day_ago = datetime.utcnow() - timedelta(days=1)
    recent = SensorReading.query.filter(
        SensorReading.node_id == node_id,
        SensorReading.recorded_at >= day_ago
    ).order_by(SensorReading.recorded_at).all()
    
    # 3. Active alerts (unresolved)
    alerts = Alert.query.filter_by(node_id=node_id, resolved=False).all()
    
    # 4. Latest pump command
    latest_pump = PumpCommand.query.filter_by(node_id=node_id)\
                                   .order_by(desc(PumpCommand.issued_at)).first()
    
    # 5. Statistics
    stats = db.session.query(
        func.avg(SensorReading.soil_moisture).label('avg_moisture'),
        func.max(SensorReading.soil_moisture).label('max_moisture'),
        func.min(SensorReading.soil_moisture).label('min_moisture'),
        func.avg(SensorReading.temperature).label('avg_temp'),
        func.avg(SensorReading.humidity).label('avg_humidity'),
        func.count(SensorReading.id).label('total_readings')
    ).filter_by(node_id=node_id).first()
    
    # 6. Recent pump commands (last 24 hours)
    recent_pump_commands = PumpCommand.query.filter(
        PumpCommand.node_id == node_id,
        PumpCommand.issued_at >= day_ago
    ).order_by(desc(PumpCommand.issued_at)).limit(10).all()
    
    return jsonify({
        'node': node.to_dict(),
        'latest_reading': latest.to_dict() if latest else None,
        'recent_readings': [r.to_dict() for r in recent[-20:]] if recent else [],
        'active_alerts': [a.to_dict() for a in alerts],
        'pump_status': latest_pump.command if latest_pump else 'OFF',
        'pump_last_changed': latest_pump.issued_at.isoformat() if latest_pump else None,
        'statistics': {
            'avg_soil_moisture': float(stats.avg_moisture or 0),
            'max_soil_moisture': float(stats.max_moisture or 0),
            'min_soil_moisture': float(stats.min_moisture or 0),
            'avg_temperature': float(stats.avg_temp or 0),
            'avg_humidity': float(stats.avg_humidity or 0),
            'total_readings': stats.total_readings or 0
        },
        'recent_pump_commands': [p.to_dict() for p in recent_pump_commands]
    }), 200


@dashboard_bp.route('/nodes', methods=['GET'])
@jwt_required()
def get_all_nodes_summary():
    """Get summary for all nodes"""
    nodes = SensorNode.query.all()
    
    result = []
    for node in nodes:
        latest = SensorReading.query.filter_by(node_id=node.id)\
                                   .order_by(desc(SensorReading.recorded_at)).first()
        
        active_alerts = Alert.query.filter_by(node_id=node.id, resolved=False).count()
        
        latest_pump = PumpCommand.query.filter_by(node_id=node.id)\
                                      .order_by(desc(PumpCommand.issued_at)).first()
        
        result.append({
            'node': node.to_dict(),
            'latest_reading': latest.to_dict() if latest else None,
            'active_alerts': active_alerts,
            'pump_status': latest_pump.command if latest_pump else 'OFF'
        })
    
    return jsonify(result), 200