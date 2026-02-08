"""
Base model for all entities in the application.
Provides common attributes and methods.
"""
import uuid
from datetime import datetime
from typing import Dict


class BaseModel:
    """
    Base class for all models in the application.
    Provides common attributes: id, created_at, updated_at.
    """

    def __init__(self):
        """Initialize base model with unique ID and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """
        Convert the object to a dictionary representation.

        Returns:
            Dictionary containing all object attributes
        """
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        return result

    def __repr__(self) -> str:
        """String representation of the object."""
        return f"<{self.__class__.__name__} {self.id}>"
