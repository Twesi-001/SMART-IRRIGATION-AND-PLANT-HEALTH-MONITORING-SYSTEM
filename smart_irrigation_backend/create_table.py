
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import FarmerNode
from sqlalchemy import inspect # type: ignore

print("🔄 Connecting to database...")
app = create_app()

with app.app_context():
    print("📡 Creating tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Verify
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📡 Tables in database: {tables}")
    
    if 'farmer_nodes' in tables:
        print("✅ farmer_nodes table exists!")
    else:
        print("❌ farmer_nodes table not found!")