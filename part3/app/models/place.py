"""
Place model for the HBnB application.
Defines property listings mapped to SQLAlchemy with relationships
to User, Review, and Amenity.
"""
from app import db
from app.models.base_model import BaseModel
from app.models.amenity import place_amenity
from sqlalchemy.orm import reconstructor


class Place(BaseModel):
    """
    Place class represents a property listing.

    Attributes:
        title (str): Title of the place
        description (str): Detailed description
        price (float): Price per night
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        owner_id (str): FK to users.id
    """

    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Foreign key to User
    owner_id = db.Column(
        db.String(36), db.ForeignKey('users.id'), nullable=False
    )

    # One-to-many: a place has many reviews
    reviews = db.relationship('Review', backref='place', lazy=True)

    # Many-to-many: a place has many amenities
    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        lazy='subquery',
        backref=db.backref('places', lazy=True)
    )

    def __init__(self, title, description, price, latitude,
                 longitude, owner_id):
        """
        Initialize a Place instance.

        Args:
            title (str): Title of the place
            description (str): Description of the place
            price (float): Nightly price
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            owner_id (str): ID of the place owner

        Raises:
            ValueError: If validation fails
        """
        super().__init__()
        self.title = title
        self.description = description
        self.price = float(price)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.owner_id = owner_id

        self.validate()

    @reconstructor
    def init_on_load(self):
        """
        Called by SQLAlchemy when loading from DB (bypasses __init__).
        No extra runtime attributes needed — relationships are handled
        by SQLAlchemy directly.
        """
        pass

    def validate(self):
        """
        Validate place attributes.

        Raises:
            ValueError: If any attribute is invalid
        """
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string")
        if len(self.title) > 100:
            raise ValueError("Title must not exceed 100 characters")

        if not isinstance(self.description, str):
            raise ValueError("Description must be a string")
        if len(self.description) > 1000:
            raise ValueError(
                "Description must not exceed 1000 characters"
            )

        if not isinstance(self.price, (int, float)):
            raise ValueError("Price must be a number")
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")

        if not isinstance(self.latitude, (int, float)):
            raise ValueError("Latitude must be a number")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")

        if not isinstance(self.longitude, (int, float)):
            raise ValueError("Longitude must be a number")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        if not isinstance(self.owner_id, str) or \
                not self.owner_id.strip():
            raise ValueError("Owner ID must be a non-empty string")

    def to_dict(self, include_owner=False, include_amenities=False,
                include_reviews=False):
        """
        Convert Place instance to dictionary.

        Args:
            include_owner (bool): Include owner details
            include_amenities (bool): Include amenity details
            include_reviews (bool): Include review details

        Returns:
            dict: Dictionary representation of the place
        """
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_owner and self.owner:
            result['owner'] = {
                'id': self.owner.id,
                'first_name': self.owner.first_name,
                'last_name': self.owner.last_name,
                'email': self.owner.email
            }

        if include_amenities:
            result['amenities'] = [
                {'id': a.id, 'name': a.name}
                for a in self.amenities
            ]

        if include_reviews:
            result['reviews'] = [
                r.to_dict() for r in self.reviews
            ]

        return result

    def __repr__(self):
        """String representation of Place."""
        return f"<Place {self.id} - {self.title}>"
