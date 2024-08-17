from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, current_app

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        db = current_app.db  # Access the db object from the current app
        current_user = get_jwt_identity()
        user = db.users.find_one({'username': current_user})
        if user and user.get('is_admin', False):
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Admin access required."}), 403
    return wrapper
