"""
Place API endpoints for HBnB application.
Handles CRUD operations for Place entities.
"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade

api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Amenity name')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='User first name'),
    'last_name': fields.String(description='User last name'),
    'email': fields.String(description='User email')
})

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'amenities': fields.List(fields.String, required=False)
})

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
        """Retrieve all places — PUBLIC endpoint, no token required."""
        places = facade.get_all_places()
        return [
            place.to_dict(include_owner=True, include_amenities=True)
            for place in places
        ], 200

    @jwt_required()
    @api.expect(place_model, validate=True)
    @api.marshal_with(place_response_model, code=201)
    def post(self):
        """
        Create a new place — AUTHENTICATED users only.
        The owner_id is taken from the JWT token, not the request body.
        """
        current_user_id = get_jwt_identity()
        place_data = api.payload

        # owner_id comes from token, not payload
        place_data['owner_id'] = current_user_id

        required_fields = [
            'title', 'description', 'price', 'latitude', 'longitude'
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
        """Retrieve a place by ID — PUBLIC endpoint, no token required."""
        place = facade.get_place(place_id)
        if place is None:
            api.abort(404, f"Place with ID {place_id} not found")
        return place.to_dict(
            include_owner=True,
            include_amenities=True
        ), 200

    @jwt_required()
    @api.expect(place_model, validate=False)
    @api.marshal_with(place_response_model)
    def put(self, place_id):
        """
        Update place information.
        Owners can update their own places.
        Admins can update any place regardless of ownership.
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        place_data = api.payload

        existing_place = facade.get_place(place_id)
        if not existing_place:
            api.abort(404, f"Place with ID {place_id} not found")

        # Admins bypass ownership check
        if not is_admin and existing_place.owner_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        # Prevent changing owner_id
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
        """Retrieve all reviews for a place — PUBLIC endpoint."""
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
