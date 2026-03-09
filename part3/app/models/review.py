"""
Review model for the HBnB application.
Defines reviews mapped to SQLAlchemy with foreign keys to
User and Place.
"""
from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import reconstructor


class Review(BaseModel):
    """
    Review class represents user feedback for a place.

    Attributes:
        rating (int): Rating from 1 to 5
        comment (str): Written review
        user_id (str): FK to users.id
        place_id (str): FK to places.id
    """

    __tablename__ = 'reviews'

    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=False)

    # Foreign keys
    user_id = db.Column(
        db.String(36), db.ForeignKey('users.id'), nullable=False
    )
    place_id = db.Column(
        db.String(36), db.ForeignKey('places.id'), nullable=False
    )

    def __init__(self, rating, comment, user_id, place_id):
        super().__init__()
        self.rating = int(rating)
        self.comment = comment
        self.user_id = user_id
        self.place_id = place_id
        self.validate()

    @reconstructor
    def init_on_load(self):
        pass

    def validate(self):
        if not isinstance(self.rating, int):
            raise ValueError("Rating must be an integer")
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        if not isinstance(self.comment, str) or not self.comment.strip():
            raise ValueError("Comment must be a non-empty string")
        if len(self.comment) < 10:
            raise ValueError("Comment must be at least 10 characters long")
        if len(self.comment) > 500:
            raise ValueError("Comment must not exceed 500 characters")
        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise ValueError("User ID must be a non-empty string")
        if not isinstance(self.place_id, str) or not self.place_id.strip():
            raise ValueError("Place ID must be a non-empty string")

    def to_dict(self, include_user=False, include_place=False):
        result = {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'user_id': self.user_id,
            'place_id': self.place_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_user and self.author:
            result['user'] = {
                'id': self.author.id,
                'first_name': self.author.first_name,
                'last_name': self.author.last_name
            }
        if include_place and self.place:
            result['place'] = {
                'id': self.place.id,
                'title': self.place.title
            }
        return result

    def __repr__(self):
        return f"<Review {self.id} - Rating: {self.rating}>"
