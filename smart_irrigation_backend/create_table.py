# create_table.py
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if table exists
        result = db.session.execute(text("SHOW TABLES LIKE 'farmer_nodes'"))
        exists = result.fetchone()
        
        if not exists:
            print("📝 Creating farmer_nodes table...")
            # Create the table
            db.session.execute(text("""
                CREATE TABLE farmer_nodes (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    farmer_id INT NOT NULL,
                    node_id INT NOT NULL,
                    custom_name VARCHAR(100),
                    location VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farmer_id) REFERENCES users(id),
                    FOREIGN KEY (node_id) REFERENCES sensor_nodes(id),
                    UNIQUE KEY unique_farmer_crop (farmer_id, node_id)
                )
            """))
            db.session.commit()
            print("✅ farmer_nodes table created successfully!")
        else:
            print("✅ farmer_nodes table already exists!")
            
        # Verify it worked
        result = db.session.execute(text("SELECT COUNT(*) FROM farmer_nodes"))
        count = result.fetchone()[0]
        print(f"📊 farmer_nodes has {count} records")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()