"""
Flask application factory.
"""
from flask import Flask
from flask_restx import Api
from config import config


def create_app(config_name='development'):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration to use (development, testing, production)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize Flask-RESTX API
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/docs'
    )

    # Import and register namespaces
    from app.api.v1.users import api as users_ns

    api.add_namespace(users_ns, path='/api/v1/users')

    return app
