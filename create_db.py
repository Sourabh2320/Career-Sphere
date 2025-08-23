# create_db.py

from app import app, db

# Create an application context
with app.app_context():
    # This will create all the tables defined in your models
    db.create_all()
    print("Database tables created successfully!")