"""
Place model for the HBnB application.
Defines property listings with their attributes and relationships.
"""
from app.models.base_model import BaseModel


class Place(BaseModel):
    """
    Place class represents a property listing.

    Attributes:
        title (str): Title of the place
        description (str): Detailed description
        price (float): Price per night
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        owner_id (str): ID of the user who owns the place
        owner (User): Reference to the owner (for composition)
        amenities (list): List of amenity IDs or objects
        reviews (list): List of review IDs or objects
    """

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
        self.owner = None  # Will be set when retrieved with owner details
        self.amenities = []  # List to store amenity objects
        self.reviews = []  # List to store review objects

        # Validate attributes
        self.validate()

    def validate(self):
        """
        Validate place attributes.

        Raises:
            ValueError: If any attribute is invalid
        """
        # Validate title
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string")
        if len(self.title) > 100:
            raise ValueError("Title must not exceed 100 characters")

        # Validate description
        if not isinstance(self.description, str):
            raise ValueError("Description must be a string")
        if len(self.description) > 1000:
            raise ValueError("Description must not exceed 1000 characters")

        # Validate price
        if not isinstance(self.price, (int, float)):
            raise ValueError("Price must be a number")
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")

        # Validate latitude
        if not isinstance(self.latitude, (int, float)):
            raise ValueError("Latitude must be a number")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")

        # Validate longitude
        if not isinstance(self.longitude, (int, float)):
            raise ValueError("Longitude must be a number")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Validate owner_id
        if not isinstance(self.owner_id, str) or not self.owner_id.strip():
            raise ValueError("Owner ID must be a non-empty string")

    def add_amenity(self, amenity):
        """
        Add an amenity to the place.

        Args:
            amenity: Amenity object or ID to add

        Returns:
            bool: True if added, False if already exists
        """
        amenity_id = amenity.id if hasattr(amenity, 'id') else amenity

        # Check if amenity already exists
        existing_ids = [a.id if hasattr(a, 'id') else a
                        for a in self.amenities]
        if amenity_id in existing_ids:
            return False

        self.amenities.append(amenity)
        self.save()
        return True

    def remove_amenity(self, amenity_id):
        """
        Remove an amenity from the place.

        Args:
            amenity_id (str): ID of the amenity to remove

        Returns:
            bool: True if removed, False if not found
        """
        initial_length = len(self.amenities)
        self.amenities = [
            a for a in self.amenities
            if (a.id if hasattr(a, 'id') else a) != amenity_id
        ]
        if len(self.amenities) < initial_length:
            self.save()
            return True
        return False

    def add_review(self, review):
        """
        Add a review to the place.

        Args:
            review: Review object to add
        """
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()

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

        # Include owner details if requested and available
        if include_owner and self.owner:
            result['owner'] = {
                'id': self.owner.id,
                'first_name': self.owner.first_name,
                'last_name': self.owner.last_name,
                'email': self.owner.email
            }

        # Include amenities if requested
        if include_amenities:
            result['amenities'] = [
                {'id': a.id, 'name': a.name}
                if hasattr(a, 'name') else a
                for a in self.amenities
            ]

        # Include reviews if requested
        if include_reviews:
            result['reviews'] = [
                r.to_dict() if hasattr(r, 'to_dict') else r
                for r in self.reviews
            ]

        return result

    def __repr__(self):
        """String representation of Place."""
        return f"<Place {self.id} - {self.title}>"
