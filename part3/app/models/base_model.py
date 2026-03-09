"""
Base model for all entities in the application.
Provides common attributes and methods via SQLAlchemy ORM.
"""
import uuid
from datetime import datetime
from app import db


class BaseModel(db.Model):
    """
    Base class for all SQLAlchemy models in the application.
    Provides common columns: id, created_at, updated_at.
    __abstract__ ensures SQLAlchemy does not create a table for BaseModel.
    """

    __abstract__ = True

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def save(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.

        Returns:
            Dictionary containing all object attributes
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        """String representation of the object."""
        return f"<{self.__class__.__name__} {self.id}>"
