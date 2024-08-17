from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secretive-key'
    
    # JWT configuration
    app.config['JWT_SECRET_KEY'] = 'chaiorcode'  # Change this to a random secret key
    jwt = JWTManager(app)

    # MongoDB configuration
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/employee_database'
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client['employee_database']

    # Rate limiting configuration
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[]  # We'll define custom limits in the route decorators
    )
    app.limiter = limiter

    # Register blueprints
    from .auth.routes import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from .employee.routes import employee
    app.register_blueprint(employee, url_prefix='/employee')

    return app
