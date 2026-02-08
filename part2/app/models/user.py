"""
User model for the HBnB application.
Defines the User entity with validation and business logic.
"""
import re
from app.models.base_model import BaseModel


class User(BaseModel):
    """
    User class represents a user in the HBnB application.

    Attributes:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address (unique)
        is_admin (bool): Whether the user has admin privileges
    """

    def __init__(self, first_name, last_name, email, is_admin=False):
        """
        Initialize a User instance.

        Args:
            first_name (str): User's first name
            last_name (str): User's last name
            email (str): User's email address
            is_admin (bool): Admin status (default: False)

        Raises:
            ValueError: If validation fails
        """
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

        # Validate all attributes
        self.validate()

    def validate(self):
        """
        Validate user attributes.

        Raises:
            ValueError: If any attribute is invalid
        """
        # Validate first_name
        if not isinstance(self.first_name, str) or \
           not self.first_name.strip():
            raise ValueError("First name must be a non-empty string")
        if len(self.first_name) > 50:
            raise ValueError("First name must not exceed 50 characters")

        # Validate last_name
        if not isinstance(self.last_name, str) or \
           not self.last_name.strip():
            raise ValueError("Last name must be a non-empty string")
        if len(self.last_name) > 50:
            raise ValueError("Last name must not exceed 50 characters")

        # Validate email
        if not isinstance(self.email, str) or not self.email.strip():
            raise ValueError("Email must be a non-empty string")
        if not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")

        # Validate is_admin
        if not isinstance(self.is_admin, bool):
            raise ValueError("is_admin must be a boolean")

    @staticmethod
    def _is_valid_email(email):
        """
        Validate email format using regex.

        Args:
            email (str): Email address to validate

        Returns:
            bool: True if valid, False otherwise
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def to_dict(self):
        """
        Convert User instance to dictionary.

        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        """String representation of User."""
        return f"<User {self.id} - {self.email}>"
