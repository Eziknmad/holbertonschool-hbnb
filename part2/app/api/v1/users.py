"""
User API endpoints for HBnB application.
Handles CRUD operations for User entities.
"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

# Create namespace for users
api = Namespace('users', description='User operations')

# Define user model for API documentation and validation
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
    )
})

# Define response model (excludes sensitive data)
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


@api.route('/')
class UserList(Resource):
    """Handles operations on the user collection."""

    @api.doc('list_users')
    @api.marshal_list_with(user_response_model, code=200)
    def get(self):
        """
        Retrieve a list of all users.

        Returns:
            200: List of all users (without passwords)
            500: Internal server error
        """
        try:
            users = facade.get_all_users()
            return [user.to_dict() for user in users], 200
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")

    @api.doc('create_user')
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    @api.response(400, 'Invalid input data')
    @api.response(409, 'Email already registered')
    def post(self):
        """
        Create a new user.

        Returns:
            201: User successfully created
            400: Invalid input data
            409: Email already registered
            500: Internal server error
        """
        try:
            user_data = api.payload

            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    api.abort(400, f"Missing required field: {field}")

            # Create user through facade
            new_user = facade.create_user(user_data)

            return new_user.to_dict(), 201

        except ValueError as e:
            # Handle validation errors and duplicate email
            error_message = str(e)
            if "already registered" in error_message.lower():
                api.abort(409, error_message)
            else:
                api.abort(400, error_message)
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
        Retrieve a user by ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            200: User details (without password)
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

    @api.doc('update_user')
    @api.expect(user_model, validate=False)
    @api.marshal_with(user_response_model, code=200)
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(409, 'Email already registered')
    def put(self, user_id):
        """
        Update user information.

        Args:
            user_id: The unique identifier of the user

        Returns:
            200: User successfully updated
            400: Invalid input data
            404: User not found
            409: Email already registered
            500: Internal server error
        """
        try:
            user_data = api.payload

            # Check if user exists
            existing_user = facade.get_user(user_id)
            if not existing_user:
                api.abort(404, f"User with ID {user_id} not found")

            # Filter out fields that shouldn't be updated
            allowed_fields = ['first_name', 'last_name', 'email']
            filtered_data = {
                k: v for k, v in user_data.items()
                if k in allowed_fields
            }

            if not filtered_data:
                api.abort(400, "No valid fields to update")

            # Update user through facade
            updated_user = facade.update_user(user_id, filtered_data)

            if not updated_user:
                api.abort(404, f"User with ID {user_id} not found")

            return updated_user.to_dict(), 200

        except ValueError as e:
            # Handle validation errors and duplicate email
            error_message = str(e)
            if "already registered" in error_message.lower():
                api.abort(409, error_message)
            else:
                api.abort(400, error_message)
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")
