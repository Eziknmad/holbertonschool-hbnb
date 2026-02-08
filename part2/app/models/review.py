"""
Review model for the HBnB application.
Defines reviews that users can leave for places.
"""
from app.models.base_model import BaseModel


class Review(BaseModel):
    """
    Review class represents user feedback for a place.

    Attributes:
        rating (int): Rating from 1 to 5
        comment (str): Written review
        user_id (str): ID of the user who wrote the review
        place_id (str): ID of the place being reviewed
        user (User): Reference to the user (for composition)
        place (Place): Reference to the place (for composition)
    """

    def __init__(self, rating, comment, user_id, place_id):
        """
        Initialize a Review instance.

        Args:
            rating (int): Rating value (1-5)
            comment (str): Review comment
            user_id (str): ID of the reviewer
            place_id (str): ID of the place being reviewed

        Raises:
            ValueError: If validation fails
        """
        super().__init__()
        self.rating = int(rating)
        self.comment = comment
        self.user_id = user_id
        self.place_id = place_id
        self.user = None  # Will be set when retrieved with user details
        self.place = None  # Will be set when retrieved with place details

        # Validate attributes
        self.validate()

    def validate(self):
        """
        Validate review attributes.

        Raises:
            ValueError: If any attribute is invalid
        """
        # Validate rating
        if not isinstance(self.rating, int):
            raise ValueError("Rating must be an integer")
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Validate comment
        if not isinstance(self.comment, str) or not self.comment.strip():
            raise ValueError("Comment must be a non-empty string")
        if len(self.comment) < 10:
            raise ValueError("Comment must be at least 10 characters long")
        if len(self.comment) > 500:
            raise ValueError("Comment must not exceed 500 characters")

        # Validate user_id
        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise ValueError("User ID must be a non-empty string")

        # Validate place_id
        if not isinstance(self.place_id, str) or \
           not self.place_id.strip():
            raise ValueError("Place ID must be a non-empty string")

    def to_dict(self, include_user=False, include_place=False):
        """
        Convert Review instance to dictionary.

        Args:
            include_user (bool): Include user details
            include_place (bool): Include place details

        Returns:
            dict: Dictionary representation of the review
        """
        result = {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'user_id': self.user_id,
            'place_id': self.place_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        # Include user details if requested and available
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            }

        # Include place details if requested and available
        if include_place and self.place:
            result['place'] = {
                'id': self.place.id,
                'title': self.place.title
            }

        return result

    def __repr__(self):
        """String representation of Review."""
        return f"<Review {self.id} - Rating: {self.rating}>"
