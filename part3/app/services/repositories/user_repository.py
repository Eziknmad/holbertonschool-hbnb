"""
User-specific repository for HBnB application.
Extends SQLAlchemyRepository with user-specific query methods.
"""
from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """
    User-specific repository extending the generic SQLAlchemyRepository.

    Provides user-specific queries beyond the standard CRUD operations,
    such as email-based lookups used for authentication and uniqueness checks.
    """

    def __init__(self):
        """Initialize the UserRepository with the User model."""
        super().__init__(User)

    def get_user_by_email(self, email):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address to search for

        Returns:
            User instance if found, None otherwise
        """
        return self.model.query.filter_by(email=email).first()
