# create_nodes.py
from app import create_app
from app.extensions import db
from app.models import SensorNode

app = create_app()

with app.app_context():
    # Define the 20 crops
    crops = [
        ("Maize", 35.0),
        ("Tomato", 45.0),
        ("Onion", 40.0),
        ("Cabbage", 55.0),
        ("Mango", 35.0),
        ("Banana", 60.0),
        ("Pineapple", 40.0),
        ("Passion Fruit", 45.0),
        ("Carrot", 50.0),
        ("Capsicum", 45.0),
        ("Eggplant", 50.0),
        ("Sukuma Wiki", 55.0),
        ("Spinach", 55.0),
        ("Beans", 40.0),
        ("Garlic", 40.0),
        ("Strawberry", 50.0),
        ("Lettuce", 55.0),
        ("Cucumber", 50.0),
        ("Watermelon", 40.0),
        ("Pumpkin", 45.0),
    ]
    
    print("🌱 Creating 20 crop nodes...")
    
    for i, (crop_name, threshold) in enumerate(crops, start=1):
        # Check if node already exists
        existing = SensorNode.query.filter_by(crop_type=crop_name).first()
        if existing:
            print(f"   ⏭️ Node {i} ({crop_name}) already exists (ID: {existing.id})")
            continue
        
        node = SensorNode(
            node_name=f"Node-{i:02d}",
            crop_type=crop_name,
            moisture_threshold=threshold,
            location="Avodah Innovations Training Facility, Kiyanja, Mbarara City",
            user_id=1,  # testuser owns all nodes
            is_active=True
        )
        db.session.add(node)
        print(f"   ✅ Created Node {i}: {crop_name}")
    
    db.session.commit()
    print("\n✅ All 20 nodes created!")
    
    # Verify
    nodes = SensorNode.query.all()
    print(f"\n📊 Total nodes in database: {len(nodes)}")
    for node in nodes:
        print(f"   Node {node.id}: {node.crop_type} (user_id: {node.user_id})")