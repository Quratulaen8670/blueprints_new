from flask import Flask
from .auth.routes import auth
from .employee.routes import employee

def create_app():
    app = Flask(__name__)
    app.secret_key = 'Secretive-key'

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(employee, url_prefix='/employee')

    return app
