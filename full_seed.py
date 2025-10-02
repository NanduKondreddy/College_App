# full_seed.py

from models import db
from seed import seed_users, seed_demo_data

def full_refresh():
    """
    Drop all tables, recreate the schema, 
    then seed users and demo data.
    """
    db.drop_all()
    db.create_all()
    seed_users()
    seed_demo_data()
    db.session.commit()

def main():
    """
    Load the Flask app context and run full_refresh().
    """
    # Defer app import until runtime to avoid circular imports
    from app import app
    with app.app_context():
        full_refresh()
        print("✅ Full refresh complete.")

if __name__ == "__main__":
    main()
