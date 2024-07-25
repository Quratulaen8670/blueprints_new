from flask import Blueprint, request, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

employee = Blueprint('employee', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_database']
employees = db['employees']


@employee.route('/list', methods=['GET'])
def employee_list():
    if 'username' not in session:
        return jsonify({"error": "You need to log in first."}), 401

    user_is_admin = session.get('is_admin', False)
    employees_data = list(employees.find())

    for emp in employees_data:
        emp['_id'] = str(emp['_id'])

    return jsonify({"employees": employees_data, "is_admin": user_is_admin})


@employee.route('/edit_employee/<employee_id>', methods=['POST'])
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


@employee.route('/create_employee', methods=['POST'])
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


@employee.route('/delete_employee/<employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({"error": "You do not have permission to access this page."}), 403

    employees.delete_one({'_id': ObjectId(employee_id)})
    return jsonify({"message": "Employee deleted successfully."})



