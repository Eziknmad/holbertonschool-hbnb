"""
User API endpoints for HBnB application.
Handles CRUD operations for User entities.
"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade

# Create namespace for users
api = Namespace('users', description='User operations')

# Define user input model — now includes password
user_model = api.model('User', {
    'first_name': fields.String(
        required=True,
        description='User first name',
        example='John'
    ),
    'last_name': fields.String(
        required=True,
        description='User last name',
        example='Doe'
    ),
    'email': fields.String(
        required=True,
        description='User email address',
        example='john.doe@example.com'
    ),
    'password': fields.String(
        required=True,
        description='User password (min 6 characters)',
        example='securepassword123'
    )
})

# Full response model — password intentionally excluded
user_response_model = api.model('UserResponse', {
    'id': fields.String(
        description='User unique identifier',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
    'first_name': fields.String(
        description='User first name',
        example='John'
    ),
    'last_name': fields.String(
        description='User last name',
        example='Doe'
    ),
    'email': fields.String(
        description='User email address',
        example='john.doe@example.com'
    ),
    'created_at': fields.String(
        description='User creation timestamp',
        example='2024-01-01T12:00:00'
    ),
    'updated_at': fields.String(
        description='User last update timestamp',
        example='2024-01-01T12:00:00'
    )
})

# Minimal response model for POST — only ID and success message
user_created_model = api.model('UserCreated', {
    'id': fields.String(
        description='User unique identifier',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
    'message': fields.String(
        description='Success message',
        example='User created successfully'
    )
})


@api.route('/')
class UserList(Resource):
    """Handles operations on the user collection."""

    @api.doc('list_users')
    @api.marshal_list_with(user_response_model, code=200)
    def get(self):
        """
        Retrieve a list of all users — PUBLIC endpoint.

        Returns:
            200: List of all users (passwords excluded)
            500: Internal server error
        """
        try:
            users = facade.get_all_users()
            return [user.to_dict() for user in users], 200
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('create_user')
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_created_model, code=201)
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """
        Create a new user — ADMIN only.
        Password is hashed before storage and never returned.

        Returns:
            201: User ID and success message only
            400: Invalid input data or email already registered
            403: Admin privileges required
            500: Internal server error
        """
        claims = get_jwt()

        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            user_data = api.payload

            required_fields = ['first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    api.abort(400, f"Missing required field: {field}")

            # Check email uniqueness
            if facade.get_user_by_email(user_data.get('email')):
                return {'error': 'Email already registered'}, 400

            new_user = facade.create_user(user_data)

            return {
                'id': new_user.id,
                'message': 'User created successfully'
            }, 201

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/<string:user_id>')
@api.param('user_id', 'The user unique identifier')
class UserResource(Resource):
    """Handles operations on a single user."""

    @api.doc('get_user')
    @api.marshal_with(user_response_model, code=200)
    @api.response(404, 'User not found')
    def get(self, user_id):
        """
        Retrieve a user by ID — PUBLIC endpoint.
        Password is excluded from response.

        Returns:
            200: User details (password excluded)
            404: User not found
            500: Internal server error
        """
        try:
            user = facade.get_user(user_id)
            if not user:
                api.abort(404, f"User with ID {user_id} not found")
            return user.to_dict(), 200
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('update_user')
    @api.expect(user_model, validate=False)
    @api.marshal_with(user_response_model, code=200)
    @api.response(400, 'Invalid input data or forbidden field')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """
        Update user information — authenticated users or admins.

        Regular users:
          - Can only update their own profile.
          - Cannot change email or password.

        Admins:
          - Can update any user's profile.
          - Can change email and password.
          - Email must remain unique.

        Returns:
            200: User successfully updated (password excluded)
            400: Invalid input or forbidden field change
            403: Unauthorized action
            404: User not found
            500: Internal server error
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Regular users can only modify their own data
        if not is_admin and current_user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            user_data = api.payload

            existing_user = facade.get_user(user_id)
            if not existing_user:
                api.abort(404, f"User with ID {user_id} not found")

            if is_admin:
                # Admins can update email and password
                # but must ensure email uniqueness
                if 'email' in user_data:
                    existing = facade.get_user_by_email(user_data['email'])
                    if existing and existing.id != user_id:
                        return {'error': 'Email already in use'}, 400

                allowed_fields = [
                    'first_name', 'last_name', 'email', 'password'
                ]
            else:
                # Regular users cannot change email or password
                if 'email' in user_data or 'password' in user_data:
                    return {
                        'error': 'You cannot modify email or password'
                    }, 400

                allowed_fields = ['first_name', 'last_name']

            filtered_data = {
                k: v for k, v in user_data.items()
                if k in allowed_fields
            }

            if not filtered_data:
                api.abort(400, "No valid fields to update")

            updated_user = facade.update_user(user_id, filtered_data)
            if not updated_user:
                api.abort(404, f"User with ID {user_id} not found")

            return updated_user.to_dict(), 200

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('delete_user')
    @api.response(200, 'User deleted successfully')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """
        Delete a user — ADMIN only.

        Admins can delete any user except themselves.

        Returns:
            200: User deleted successfully
            403: Admin privileges required
            404: User not found
            500: Internal server error
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Prevent admin from deleting themselves
        if current_user_id == user_id:
            return {'error': 'Cannot delete your own account'}, 400

        try:
            user = facade.get_user(user_id)
            if not user:
                api.abort(404, f"User with ID {user_id} not found")

            success = facade.delete_user(user_id)
            if success:
                return {'message': 'User deleted successfully'}, 200
            else:
                api.abort(500, "Failed to delete user")

        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")
