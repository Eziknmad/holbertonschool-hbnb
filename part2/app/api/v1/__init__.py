"""
API v1 package.
"""

from flask_restx import Namespace
from app.api.v1 import users  # noqa: F401 (imported for side effects)

api_v1 = Namespace('api_v1', description='HBnB API v1')

__all__ = ['api_v1']
