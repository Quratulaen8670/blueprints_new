from flask import Flask
from flask_jwt_extended import JWTManager
from .auth.routes import auth
from .employee.routes import employee

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secretive-key'
    
    # JWT configuration
    app.config['JWT_SECRET_KEY'] = 'chaiorcode'  # Change this to a random secret key
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(employee, url_prefix='/employee')
    
    return app
