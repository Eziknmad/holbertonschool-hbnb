"""
Review API endpoints for HBnB application.
Handles CRUD operations for Review entities.
"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade

api = Namespace('reviews', description='Review operations')

review_user_model = api.model('ReviewUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='User first name'),
    'last_name': fields.String(description='User last name')
})

review_place_model = api.model('ReviewPlace', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Place title')
})

# Input model — user_id comes from the token, not the request body
review_model = api.model('Review', {
    'rating': fields.Integer(
        required=True,
        description='Rating (1-5)',
        example=5
    ),
    'comment': fields.String(
        required=True,
        description='Review comment',
        example='Great place to stay!'
    ),
    'place_id': fields.String(
        required=True,
        description='ID of the place being reviewed',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    )
})

review_update_model = api.model('ReviewUpdate', {
    'rating': fields.Integer(
        description='Rating (1-5)',
        example=4
    ),
    'comment': fields.String(
        description='Review comment',
        example='Updated comment'
    )
})

review_response_model = api.model('ReviewResponse', {
    'id': fields.String(description='Review ID'),
    'rating': fields.Integer(description='Rating (1-5)'),
    'comment': fields.String(description='Review comment'),
    'user_id': fields.String(description='User ID'),
    'place_id': fields.String(description='Place ID'),
    'user': fields.Nested(review_user_model, description='Reviewer'),
    'place': fields.Nested(review_place_model, description='Place'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Update timestamp')
})


@api.route('/')
class ReviewList(Resource):
    """Handles operations on the review collection."""

    @api.doc('list_reviews')
    @api.marshal_list_with(review_response_model, code=200)
    def get(self):
        """Retrieve all reviews — PUBLIC endpoint, no token required."""
        try:
            reviews = facade.get_all_reviews()
            return [
                review.to_dict(include_user=True, include_place=True)
                for review in reviews
            ], 200
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('create_review')
    @api.expect(review_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def post(self):
        """
        Create a new review — AUTHENTICATED users only.
        user_id is taken from the JWT token.
        Users cannot review their own places or review a place twice.
        Admins are not restricted by these rules.
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            review_data = api.payload

            required_fields = ['rating', 'comment', 'place_id']
            for field in required_fields:
                if field not in review_data or review_data[field] is None:
                    api.abort(400, f"Missing required field: {field}")

            try:
                rating = int(review_data['rating'])
                if not 1 <= rating <= 5:
                    api.abort(400, "Rating must be between 1 and 5")
            except (ValueError, TypeError):
                api.abort(400, "Rating must be an integer")

            # user_id comes from JWT token, not request body
            review_data['user_id'] = current_user_id

            # Check place exists
            place = facade.get_place(review_data['place_id'])
            if not place:
                api.abort(404, "Place not found")

            if not is_admin:
                # Cannot review own place
                if place.owner_id == current_user_id:
                    return {
                        'error': 'You cannot review your own place'
                    }, 400

                # Cannot review same place twice
                existing_reviews = facade.get_reviews_by_place(
                    review_data['place_id']
                )
                for review in existing_reviews:
                    if review.user_id == current_user_id:
                        return {
                            'error': 'You have already reviewed this place'
                        }, 400

            new_review = facade.create_review(review_data)
            return new_review.to_dict(
                include_user=True,
                include_place=True
            ), 201

        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                api.abort(404, error_message)
            else:
                api.abort(400, error_message)
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/<string:review_id>')
@api.param('review_id', 'The review unique identifier')
class ReviewResource(Resource):
    """Handles operations on a single review."""

    @api.doc('get_review')
    @api.marshal_with(review_response_model, code=200)
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Retrieve a review by ID — PUBLIC endpoint."""
        try:
            review = facade.get_review(review_id)
            if not review:
                api.abort(404, f"Review with ID {review_id} not found")
            return review.to_dict(
                include_user=True,
                include_place=True
            ), 200
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('update_review')
    @api.expect(review_update_model, validate=False)
    @api.marshal_with(review_response_model, code=200)
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """
        Update a review — review owner or admin only.
        Admins can update any review regardless of ownership.
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            review_data = api.payload

            existing_review = facade.get_review(review_id)
            if not existing_review:
                api.abort(404, f"Review with ID {review_id} not found")

            # Admins bypass ownership check
            if not is_admin and existing_review.user_id != current_user_id:
                return {'error': 'Unauthorized action'}, 403

            if 'rating' in review_data:
                try:
                    rating = int(review_data['rating'])
                    if not 1 <= rating <= 5:
                        api.abort(400, "Rating must be between 1 and 5")
                except (ValueError, TypeError):
                    api.abort(400, "Rating must be an integer")

            # Block attempts to change user_id or place_id
            if 'user_id' in review_data or 'place_id' in review_data:
                api.abort(400, "Cannot update user_id or place_id")

            allowed_fields = ['rating', 'comment']
            filtered_data = {
                k: v for k, v in review_data.items()
                if k in allowed_fields
            }

            if not filtered_data:
                api.abort(400, "No valid fields to update")

            updated_review = facade.update_review(review_id, filtered_data)
            if not updated_review:
                api.abort(404, f"Review with ID {review_id} not found")

            return updated_review.to_dict(
                include_user=True,
                include_place=True
            ), 200

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")

    @jwt_required()
    @api.doc('delete_review')
    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """
        Delete a review — review owner or admin only.
        Admins can delete any review regardless of ownership.
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            review = facade.get_review(review_id)
            if not review:
                api.abort(404, f"Review with ID {review_id} not found")

            # Admins bypass ownership check
            if not is_admin and review.user_id != current_user_id:
                return {'error': 'Unauthorized action'}, 403

            success = facade.delete_review(review_id)
            if not success:
                api.abort(404, f"Review with ID {review_id} not found")

            return {'message': 'Review deleted successfully'}, 200

        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")


@api.route('/places/<string:place_id>/reviews')
@api.param('place_id', 'The place unique identifier')
class PlaceReviewList(Resource):
    """Handles operations on reviews for a specific place."""

    @api.doc('get_place_reviews')
    @api.marshal_list_with(review_response_model, code=200)
    def get(self, place_id):
        """Retrieve all reviews for a place — PUBLIC endpoint."""
        try:
            place = facade.get_place(place_id)
            if not place:
                api.abort(404, f"Place with ID {place_id} not found")
            reviews = facade.get_reviews_by_place(place_id)
            return [
                review.to_dict(include_user=True, include_place=True)
                for review in reviews
            ], 200
        except Exception as e:
            if "not found" in str(e).lower():
                api.abort(404, str(e))
            api.abort(500, f"Internal server error: {str(e)}")
