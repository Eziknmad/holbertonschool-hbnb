"""
Amenity model for the HBnB application.
Defines amenities that can be associated with places.
"""
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """
    Amenity class represents a feature/service available at a place.

    Attributes:
        name (str): Name of the amenity
        description (str): Description of the amenity
    """

    def __init__(self, name, description=""):
        """
        Initialize an Amenity instance.

        Args:
            name (str): Name of the amenity
            description (str): Description of the amenity (optional)

        Raises:
            ValueError: If validation fails
        """
        super().__init__()
        self.name = name
        self.description = description

        # Validate attributes
        self.validate()

    def validate(self):
        """
        Validate amenity attributes.

        Raises:
            ValueError: If any attribute is invalid
        """
        # Validate name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Amenity name must be a non-empty string")
        if len(self.name) > 50:
            raise ValueError("Amenity name must not exceed 50 characters")

        # Validate description
        if not isinstance(self.description, str):
            raise ValueError("Description must be a string")
        if len(self.description) > 200:
            raise ValueError("Description must not exceed 200 characters")

    def to_dict(self):
        """
        Convert Amenity instance to dictionary.

        Returns:
            dict: Dictionary representation of the amenity
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        """String representation of Amenity."""
        return f"<Amenity {self.id} - {self.name}>"
