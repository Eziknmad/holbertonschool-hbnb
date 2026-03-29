"""
Flask application factory.
"""
import os
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from config import config

bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_name='development'):
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/docs'
    )

    # Register namespaces
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    # ===== SEED ADMIN USER =====
    from app.services.facade import facade

    existing_admin = facade.get_user_by_email('admin@hbnb.io')

    if not existing_admin:
        try:
            facade.create_user({
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@hbnb.io',
                'password': 'admin1234',
                'is_admin': True
            })
            print("Admin user created: admin@hbnb.io / admin1234")
        except Exception as e:
            print(f"Could not create admin user: {e}")
    else:
        print("Admin user already exists")
    # ===== END SEED ADMIN USER =====

    return app
