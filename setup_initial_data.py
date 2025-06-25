# setup_initial_data.py
from app.utils.db import db
from werkzeug.security import generate_password_hash

def setup_data():
    users_collection = db["users"]
    
    # Clear existing users to avoid duplicates on re-run
    users_collection.delete_many({})
    
    # Create an HR user
    hr_user = {
        "username": "hr_manager",
        "password": generate_password_hash("hr_password", method='pbkdf2:sha256'),
        "role": "hr",
        "employee_id": "HR001"
    }
    
    # Create a Supervisor user
    supervisor_user = {
        "username": "supervisor_john",
        "password": generate_password_hash("sup_password", method='pbkdf2:sha256'),
        "role": "supervisor",
        "employee_id": "SUP001"
    }

    # Create an Employee user reporting to the supervisor
    employee_user = {
        "username": "employee_kamal",
        "password": generate_password_hash("emp_password", method='pbkdf2:sha256'),
        "role": "employee",
        "employee_id": "EMP123",
        "supervisor_id": "SUP001" # This employee reports to supervisor_john
    }

    users_collection.insert_many([hr_user, supervisor_user, employee_user])
    print("✅ Initial users created successfully!")
    print("\n--- Test Users ---")
    print("HR:       username='hr_manager', password='hr_password'")
    print("Supervisor: username='supervisor_john', password='sup_password'")
    print("Employee:   username='employee_kamal', password='emp_password'")

if __name__ == "__main__":
    setup_data()