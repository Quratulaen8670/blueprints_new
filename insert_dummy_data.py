from pymongo import MongoClient
import datetime
from faker import Faker

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_database']
employees = db['employees']

# Clear existing employees
employees.delete_many({})

# Initialize Faker
fake = Faker()

# Create and insert 100+ dummy employees
for _ in range(100):
    employee = {
        'name': fake.name(),
        'designation': fake.job(),
        'department': fake.company(),
        'joining_date': fake.date_this_decade().strftime('%Y-%m-%d'),  # Convert to string
        'status': fake.random_element(elements=('Active', 'Inactive')),
        'salary': fake.random_int(min=30000, max=120000)
    }
    employees.insert_one(employee)

print("Inserted dummy data successfully.")
