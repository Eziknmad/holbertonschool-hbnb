"""
Place API endpoints for HBnB application.
Handles CRUD operations for Place entities.
"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

# Create namespace for places
api = Namespace('places', description='Place operations')

# Define amenity model for nested representation
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Amenity name')
})

# Define user model for nested representation (owner)
user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='User first name'),
    'last_name': fields.String(description='User last name'),
    'email': fields.String(description='User email')
})

# Define place model for API documentation and validation
place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=True),
    'amenities': fields.List(fields.String, required=False)
})

# Define response model
place_response_model = api.model('PlaceResponse', {
    'id': fields.String(),
    'title': fields.String(),
    'description': fields.String(),
    'price': fields.Float(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'owner_id': fields.String(),
    'owner': fields.Nested(user_model),
    'amenities': fields.List(fields.Nested(amenity_model)),
    'created_at': fields.String(),
    'updated_at': fields.String()
})


@api.route('/')
class PlaceList(Resource):
    """Handles operations on the place collection."""

    @api.marshal_list_with(place_response_model)
    def get(self):
        """Retrieve all places."""
        places = facade.get_all_places()
        return [
            place.to_dict(include_owner=True, include_amenities=True)
            for place in places
        ], 200

    @api.expect(place_model, validate=True)
    @api.marshal_with(place_response_model, code=201)
    def post(self):
        """
        Create a new place.

        Returns:
            201: Place successfully created
            400: Invalid input data
            404: Owner or amenity not found
            500: Internal server error
        """
        place_data = api.payload

        required_fields = [
            'title', 'description', 'price',
            'latitude', 'longitude', 'owner_id'
        ]
        for field in required_fields:
            if field not in place_data or place_data[field] is None:
                api.abort(400, f"Missing required field: {field}")

        try:
            price = float(place_data['price'])
            latitude = float(place_data['latitude'])
            longitude = float(place_data['longitude'])
        except (ValueError, TypeError) as e:
            api.abort(400, f"Invalid numeric value: {str(e)}")

        if price <= 0:
            api.abort(400, "Price must be greater than 0")
        if not -90 <= latitude <= 90:
            api.abort(400, "Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            api.abort(400, "Longitude must be between -180 and 180")

        try:
            new_place = facade.create_place(place_data)
            return new_place.to_dict(
                include_owner=True,
                include_amenities=True
            ), 201
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                api.abort(404, error_message)
            api.abort(400, error_message)
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/<string:place_id>')
@api.param('place_id', 'The place unique identifier')
class PlaceResource(Resource):
    """Handles operations on a single place."""

    @api.marshal_with(place_response_model)
    def get(self, place_id):
        """Retrieve a place by ID."""
        place = facade.get_place(place_id)
        if place is None:
            api.abort(404, f"Place with ID {place_id} not found")

        return place.to_dict(
            include_owner=True,
            include_amenities=True
        ), 200

    @api.expect(place_model, validate=False)
    @api.marshal_with(place_response_model)
    def put(self, place_id):
        """
        Update place information.
        """
        place_data = api.payload

        existing_place = facade.get_place(place_id)
        if not existing_place:
            api.abort(404, f"Place with ID {place_id} not found")

        if 'owner_id' in place_data:
            api.abort(400, "Cannot update owner_id")

        if 'price' in place_data:
            try:
                price = float(place_data['price'])
                if price <= 0:
                    api.abort(400, "Price must be greater than 0")
            except (ValueError, TypeError):
                api.abort(400, "Invalid price value")

        if 'latitude' in place_data:
            try:
                latitude = float(place_data['latitude'])
                if not -90 <= latitude <= 90:
                    api.abort(400, "Latitude must be between -90 and 90")
            except (ValueError, TypeError):
                api.abort(400, "Invalid latitude value")

        if 'longitude' in place_data:
            try:
                longitude = float(place_data['longitude'])
                if not -180 <= longitude <= 180:
                    api.abort(400, "Longitude must be between -180 and 180")
            except (ValueError, TypeError):
                api.abort(400, "Invalid longitude value")

        allowed_fields = [
            'title', 'description', 'price',
            'latitude', 'longitude', 'amenities'
        ]
        filtered_data = {
            k: v for k, v in place_data.items()
            if k in allowed_fields
        }

        if not filtered_data:
            api.abort(400, "No valid fields to update")

        try:
            updated_place = facade.update_place(place_id, filtered_data)
            if not updated_place:
                api.abort(404, f"Place with ID {place_id} not found")

            return updated_place.to_dict(
                include_owner=True,
                include_amenities=True
            ), 200
        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                api.abort(404, error_message)
            api.abort(400, error_message)
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/<string:place_id>/reviews')
@api.param('place_id', 'The place unique identifier')
class PlaceReviewList(Resource):
    """Handles getting reviews for a specific place."""

    def get(self, place_id):
        """Retrieve all reviews for a specific place."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, f"Place with ID {place_id} not found")

        reviews = facade.get_reviews_by_place(place_id)

        return [
            {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'user_id': review.user_id,
                'created_at': review.created_at.isoformat(),
                'updated_at': review.updated_at.isoformat()
            }
            for review in reviews
        ], 200
