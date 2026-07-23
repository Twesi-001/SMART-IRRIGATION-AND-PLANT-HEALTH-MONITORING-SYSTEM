# test_nodes.py
from app import create_app, db
from app.models import SensorNode

app = create_app()

with app.app_context():
    nodes = SensorNode.query.order_by(SensorNode.id).all()
    print(f"📡 Total nodes: {len(nodes)}")
    for node in nodes:
        print(f"   Node {node.id}: {node.node_name}")