"""
Repository implementations for object storage.
Contains both in-memory and SQLAlchemy-backed implementations.
"""
from typing import Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """Abstract base class for repository pattern."""

    @abstractmethod
    def add(self, obj: T) -> None:
        """Add an object to the repository."""
        pass

    @abstractmethod
    def get(self, obj_id: str) -> Optional[T]:
        """Retrieve an object by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all objects."""
        pass

    @abstractmethod
    def update(self, obj_id: str, data: dict) -> Optional[T]:
        """Update an object."""
        pass

    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        """Delete an object by ID."""
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name: str, attr_value) -> Optional[T]:
        """Retrieve an object by a specific attribute."""
        pass


class InMemoryRepository(Repository[T]):
    """
    In-memory implementation of the repository pattern.
    Uses a dictionary to store objects with their IDs as keys.
    """

    def __init__(self):
        """Initialize the repository with an empty storage dictionary."""
        self._storage: Dict[str, T] = {}

    def add(self, obj: T) -> None:
        """
        Add an object to the repository.

        Args:
            obj: Object to add (must have an 'id' attribute)

        Raises:
            ValueError: If object with the same ID already exists
        """
        if not hasattr(obj, 'id'):
            raise ValueError("Object must have an 'id' attribute")

        if obj.id in self._storage:
            raise ValueError(f"Object with id {obj.id} already exists")

        self._storage[obj.id] = obj

    def get(self, obj_id: str) -> Optional[T]:
        """
        Retrieve an object by its ID.

        Args:
            obj_id: The unique identifier of the object

        Returns:
            The object if found, None otherwise
        """
        return self._storage.get(obj_id)

    def get_all(self) -> List[T]:
        """
        Retrieve all objects from the repository.

        Returns:
            List of all stored objects
        """
        return list(self._storage.values())

    def update(self, obj_id: str, data: dict) -> Optional[T]:
        """
        Update an object with new data.

        Args:
            obj_id: The unique identifier of the object
            data: Dictionary containing the attributes to update

        Returns:
            The updated object if found, None otherwise
        """
        obj = self.get(obj_id)
        if obj is None:
            return None

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        if hasattr(obj, 'updated_at'):
            from datetime import datetime
            obj.updated_at = datetime.now()

        return obj

    def delete(self, obj_id: str) -> bool:
        """
        Delete an object from the repository.

        Args:
            obj_id: The unique identifier of the object

        Returns:
            True if object was deleted, False if not found
        """
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(
        self, attr_name: str, attr_value
    ) -> Optional[T]:
        """
        Retrieve an object by a specific attribute value.

        Args:
            attr_name: Name of the attribute to search by
            attr_value: Value of the attribute to match

        Returns:
            The first object matching the criteria, None if not found
        """
        for obj in self._storage.values():
            if hasattr(obj, attr_name) and \
               getattr(obj, attr_name) == attr_value:
                return obj
        return None


class SQLAlchemyRepository(Repository[T]):
    """
    SQLAlchemy-backed implementation of the repository pattern.
    Uses SQLAlchemy session management for database interactions.
    NOTE: Models must be mapped before this repository can be used.
    """

    def __init__(self, model):
        """
        Initialize the repository with a SQLAlchemy model class.

        Args:
            model: The SQLAlchemy model class this repository manages
        """
        self.model = model

    def add(self, obj: T) -> None:
        """
        Add an object to the database.

        Args:
            obj: SQLAlchemy model instance to persist
        """
        from app import db
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id: str) -> Optional[T]:
        """
        Retrieve an object by its primary key.

        Args:
            obj_id: The primary key of the object

        Returns:
            The object if found, None otherwise
        """
        return self.model.query.get(obj_id)

    def get_all(self) -> List[T]:
        """
        Retrieve all objects of this model type.

        Returns:
            List of all model instances
        """
        return self.model.query.all()

    def update(self, obj_id: str, data: dict) -> Optional[T]:
        """
        Update an object with new data.

        Args:
            obj_id: The primary key of the object
            data: Dictionary of attributes to update

        Returns:
            The updated object if found, None otherwise
        """
        from app import db
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()
        return obj

    def delete(self, obj_id: str) -> bool:
        """
        Delete an object from the database.

        Args:
            obj_id: The primary key of the object

        Returns:
            True if deleted, False if not found
        """
        from app import db
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False

    def get_by_attribute(
        self, attr_name: str, attr_value
    ) -> Optional[T]:
        """
        Retrieve an object by a specific attribute value.

        Args:
            attr_name: Name of the model attribute to filter by
            attr_value: Value to match

        Returns:
            The first matching object, None if not found
        """
        return self.model.query.filter_by(
            **{attr_name: attr_value}
        ).first()
