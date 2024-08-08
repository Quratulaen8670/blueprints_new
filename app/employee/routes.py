from flask import Blueprint, request, jsonify,session
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

@employee.route('/read', methods=['GET'])
@jwt_required()
def employee_list():
    current_user = get_jwt_identity()
    user_is_admin = users.find_one({'username': current_user}).get('is_admin', False)
    employees_data = list(employees.find())

    def filter_employee_data(employee, is_admin):
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

    for emp in filtered_employees_data:
        emp['_id'] = str(emp['_id'])

    return jsonify({"employees": filtered_employees_data})



@employee.route('/update_employee/<employee_id>', methods=['POST'])
@admin_required
def edit_employee(employee_id):
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({"error": "You do not have permission to access this page."}), 403

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

    return jsonify({"message": "Employee details updated successfully."})


@employee.route('/create_employee', methods=['POST'], endpoint='create_employee')
@admin_required
def create_employee():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({"error": "You do not have permission to access this page."}), 403

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
    return jsonify({"message": "New employee created successfully.", "employee_id": str(result.inserted_id)})


@employee.route('/delete_employee/<employee_id>', methods=['POST'],endpoint='delete_employee')
@admin_required
def delete_employee(employee_id):
    employees.delete_one({'_id': ObjectId(employee_id)})
    return jsonify({"message": "Employee deleted successfully."})


@employee.route('/search_employee', methods=['GET'])
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

    # Create the aggregation pipeline
    pipeline = [
        {'$match': query}
    ]

    # Execute the aggregation pipeline
    employees_data = list(employees.aggregate(pipeline))

    # Convert ObjectId to string for JSON serialization
    for emp in employees_data:
        emp['_id'] = str(emp['_id'])

    return jsonify({"employees": employees_data})


