"""
Amenity API endpoints for HBnB application.
Handles CRUD operations for Amenity entities.
"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

# Create namespace for amenities
api = Namespace('amenities', description='Amenity operations')

# Define amenity model for API documentation and validation
amenity_model = api.model('Amenity', {
    'name': fields.String(
        required=True,
        description='Amenity name',
        example='WiFi'
    ),
    'description': fields.String(
        required=False,
        description='Amenity description',
        example='High-speed wireless internet'
    )
})

# Define response model
amenity_response_model = api.model('AmenityResponse', {
    'id': fields.String(
        description='Amenity unique identifier',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
    'name': fields.String(
        description='Amenity name',
        example='WiFi'
    ),
    'description': fields.String(
        description='Amenity description',
        example='High-speed wireless internet'
    ),
    'created_at': fields.String(
        description='Amenity creation timestamp',
        example='2024-01-01T12:00:00'
    ),
    'updated_at': fields.String(
        description='Amenity last update timestamp',
        example='2024-01-01T12:00:00'
    )
})


@api.route('/')
class AmenityList(Resource):
    """Handles operations on the amenity collection."""

    @api.doc('list_amenities')
    @api.marshal_list_with(amenity_response_model, code=200)
    def get(self):
        """
        Retrieve a list of all amenities.

        Returns:
            200: List of all amenities
            500: Internal server error
        """
        try:
            amenities = facade.get_all_amenities()
            return [amenity.to_dict() for amenity in amenities], 200
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")

    @api.doc('create_amenity')
    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    @api.response(400, 'Invalid input data')
    def post(self):
        """
        Create a new amenity.

        Returns:
            201: Amenity successfully created
            400: Invalid input data
            500: Internal server error
        """
        try:
            amenity_data = api.payload

            # Validate required fields
            if 'name' not in amenity_data or not amenity_data['name']:
                api.abort(400, "Missing required field: name")

            # Create amenity through facade
            new_amenity = facade.create_amenity(amenity_data)

            return new_amenity.to_dict(), 201

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/<string:amenity_id>')
@api.param('amenity_id', 'The amenity unique identifier')
class AmenityResource(Resource):
    """Handles operations on a single amenity."""

    @api.doc('get_amenity')
    @api.marshal_with(amenity_response_model, code=200)
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Retrieve an amenity by ID.

        Args:
            amenity_id: The unique identifier of the amenity

        Returns:
            200: Amenity details
            404: Amenity not found
            500: Internal server error
        """
        try:
            amenity = facade.get_amenity(amenity_id)

            if not amenity:
                api.abort(404, f"Amenity with ID {amenity_id} not found")

            return amenity.to_dict(), 200

        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")

    @api.doc('update_amenity')
    @api.expect(amenity_model, validate=False)
    @api.marshal_with(amenity_response_model, code=200)
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """
        Update amenity information.

        Args:
            amenity_id: The unique identifier of the amenity

        Returns:
            200: Amenity successfully updated
            400: Invalid input data
            404: Amenity not found
            500: Internal server error
        """
        try:
            amenity_data = api.payload

            # Check if amenity exists
            existing_amenity = facade.get_amenity(amenity_id)
            if not existing_amenity:
                api.abort(404, f"Amenity with ID {amenity_id} not found")

            # Filter out fields that shouldn't be updated
            allowed_fields = ['name', 'description']
            filtered_data = {
                k: v for k, v in amenity_data.items()
                if k in allowed_fields
            }

            if not filtered_data:
                api.abort(400, "No valid fields to update")

            # Update amenity through facade
            updated_amenity = facade.update_amenity(
                amenity_id,
                filtered_data
            )

            if not updated_amenity:
                api.abort(404, f"Amenity with ID {amenity_id} not found")

            return updated_amenity.to_dict(), 200

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")
