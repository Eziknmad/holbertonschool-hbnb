"""
API v1 package.
"""
from flask_restx import Namespace
# Import routes
from app.api.v1 import users, amenities, places, reviews

api_v1 = Namespace('api_v1', description='HBnB API v1')

__all__ = ['api_v1']
