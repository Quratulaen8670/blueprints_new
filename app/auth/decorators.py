from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        from .routes import users  # Import locally to avoid circular import
        current_user = get_jwt_identity()
        user = users.find_one({'username': current_user})
        if user and user.get('is_admin', False):
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Admin access required."}), 403
    return wrapper
