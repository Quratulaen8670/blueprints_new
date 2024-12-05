from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth.decorators import admin_required

employee = Blueprint('employee', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_database']
employees = db['employees']
users = db['users']

def rate_limit_decorator(limit_key):
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user = current_app.db.users.find_one({'username': current_user})
            is_admin = user.get('is_admin', False) if user else False
            
            # Set rate limits based on role
            if is_admin:
                rate_limit = "10/hour"
            else:
                rate_limit = "5/hour"

            # Use the determined rate limit
            return current_app.limiter.limit(rate_limit)(func)(*args, **kwargs)
        return wrapper
    return decorator

@employee.route('/read', methods=['GET'], endpoint='employee_list')
@rate_limit_decorator("employee_list")
@jwt_required()
def employee_list():
    db = current_app.db
    users = db.users
    employees = db.employees
    
    current_user = get_jwt_identity()
    user_is_admin = users.find_one({'username': current_user}).get('is_admin', False)
    
    employees_data = list(employees.find())

    def filter_employee_data(employee, is_admin):
        # Convert ObjectId to string
        employee['_id'] = str(employee['_id'])
        if is_admin:
            return employee
        else:
            return {
                '_id': employee['_id'],
                'name': employee.get('name'),
                'designation': employee.get('designation'),
                'department': employee.get('department')
            }

    filtered_employees_data = [filter_employee_data(emp, user_is_admin) for emp in employees_data]

    return jsonify({"employees": filtered_employees_data}), 200


@employee.route('/update/<employee_id>', methods=['POST'], endpoint='edit_employee')
@admin_required
def edit_employee(employee_id):
    data = request.json
    name = data.get('name')
    designation = data.get('designation')
    department = data.get('department')
    joining_date = data.get('joining_date')
    status = data.get('status')
    salary = data.get('salary')

    employees.update_one(
        {'_id': ObjectId(employee_id)},
        {'$set': {
            'name': name,
            'designation': designation,
            'department': department,
            'joining_date': datetime.datetime.strptime(joining_date, '%Y-%m-%d'),
            'status': status,
            'salary': salary
        }}
    )

    return jsonify({"message": "Employee details updated successfully."}), 200

@employee.route('/create', methods=['POST'], endpoint='create_employee')
@admin_required
def create_employee():
    data = request.json
    name = data.get('name')
    designation = data.get('designation')
    department = data.get('department')
    joining_date = data.get('joining_date')
    status = data.get('status')
    salary = data.get('salary')

    new_employee = {
        'name': name,
        'designation': designation,
        'department': department,
        'joining_date': datetime.datetime.strptime(joining_date, '%Y-%m-%d'),
        'status': status,
        'salary': salary
    }

    result = employees.insert_one(new_employee)
    return jsonify({"message": "New employee created successfully.", "employee_id": str(result.inserted_id)}), 201

@employee.route('/delete/<employee_id>', methods=['POST'], endpoint='delete_employee')
@admin_required
def delete_employee(employee_id):
    employees.delete_one({'_id': ObjectId(employee_id)})
    return jsonify({"message": "Employee deleted successfully."}), 200

@employee.route('/search', methods=['GET'], endpoint='search_employee')
@rate_limit_decorator("search_employee")
@jwt_required()
def search_employee():
    current_user = get_jwt_identity()

    # Retrieve query parameters
    name = request.args.get('name')
    designation = request.args.get('designation')
    department = request.args.get('department')

    # Check if at least one parameter is provided
    if not name and not designation and not department:
        return jsonify({"error": "Please provide at least one search parameter (name, designation, or department)."}), 400

    # Construct the query
    query = {}
    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    if designation:
        query['designation'] = {'$regex': designation, '$options': 'i'}
    if department:
        query['department'] = {'$regex': department, '$options': 'i'}

    # Execute the aggregation pipeline
    employees_data = list(employees.find(query))

    # Convert ObjectId to string for JSON serialization
    for emp in employees_data:
        emp['_id'] = str(emp['_id'])

    return jsonify({"employees": employees_data}), 200

