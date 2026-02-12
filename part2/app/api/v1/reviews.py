"""
Review API endpoints for HBnB application.
Handles CRUD operations for Review entities.
"""
from flask_restx import Namespace, Resource, fields
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

review_model = api.model('Review', {
    'rating': fields.Integer(
        required=True,
        description='Rating (1-5)',
        min=1,
        max=5,
        example=5
    ),
    'comment': fields.String(
        required=True,
        description='Review comment',
        example='Great place to stay!'
    ),
    'user_id': fields.String(
        required=True,
        description='ID of the reviewer',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
    'place_id': fields.String(
        required=True,
        description='ID of the place being reviewed',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
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
        """
        Retrieve a list of all reviews.

        Returns:
            200: List of all reviews
            500: Internal server error
        """
        try:
            reviews = facade.get_all_reviews()
            return [
                review.to_dict(include_user=True, include_place=True)
                for review in reviews
            ], 200
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")

    @api.doc('create_review')
    @api.expect(review_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User or place not found')
    @api.response(409, 'Review already exists or user is owner')
    def post(self):
        """
        Create a new review.

        Returns:
            201: Review successfully created
            400: Invalid input data
            404: User or place not found
            409: User already reviewed place or user is owner
            500: Internal server error
        """
        try:
            review_data = api.payload

            required_fields = ['rating', 'comment', 'user_id', 'place_id']
            for field in required_fields:
                if field not in review_data or review_data[field] is None:
                    api.abort(400, f"Missing required field: {field}")

            try:
                rating = int(review_data['rating'])
                if not 1 <= rating <= 5:
                    api.abort(400, "Rating must be between 1 and 5")
            except (ValueError, TypeError):
                api.abort(400, "Rating must be an integer")

            new_review = facade.create_review(review_data)

            return new_review.to_dict(
                include_user=True,
                include_place=True
            ), 201

        except ValueError as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                api.abort(404, error_message)
            elif "already reviewed" in error_message.lower() or \
                    "cannot review" in error_message.lower():
                api.abort(409, error_message)
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
        """
        Retrieve a review by ID.

        Args:
            review_id: The unique identifier of the review

        Returns:
            200: Review details
            404: Review not found
            500: Internal server error
        """
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

    @api.doc('update_review')
    @api.expect(review_model, validate=False)
    @api.marshal_with(review_response_model, code=200)
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """
        Update review information.

        Args:
            review_id: The unique identifier of the review

        Returns:
            200: Review successfully updated
            400: Invalid input data
            404: Review not found
            500: Internal server error
        """
        try:
            review_data = api.payload

            existing_review = facade.get_review(review_id)
            if not existing_review:
                api.abort(404, f"Review with ID {review_id} not found")

            if 'rating' in review_data:
                try:
                    rating = int(review_data['rating'])
                    if not 1 <= rating <= 5:
                        api.abort(400, "Rating must be between 1 and 5")
                except (ValueError, TypeError):
                    api.abort(400, "Rating must be an integer")

            allowed_fields = ['rating', 'comment']
            filtered_data = {
                k: v for k, v in review_data.items()
                if k in allowed_fields
            }

            if 'user_id' in review_data or 'place_id' in review_data:
                api.abort(400, "Cannot update user_id or place_id")

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

    @api.doc('delete_review')
    @api.response(204, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """
        Delete a review.

        Args:
            review_id: The unique identifier of the review

        Returns:
            204: Review successfully deleted
            404: Review not found
            500: Internal server error
        """
        try:
            review = facade.get_review(review_id)
            if not review:
                api.abort(404, f"Review with ID {review_id} not found")

            success = facade.delete_review(review_id)

            if not success:
                api.abort(404, f"Review with ID {review_id} not found")

            return '', 204

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
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve all reviews for a specific place.

        Args:
            place_id: The unique identifier of the place

        Returns:
            200: List of reviews for the place
            404: Place not found
            500: Internal server error
        """
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
