"""
Facade pattern implementation for HBnB application.
Provides a simplified interface to the business logic layer.
Now that SQLAlchemy manages relationships, the facade no longer
needs to manually resolve owner/amenity/review references.
"""
from typing import List, Optional
from app.persistence.repository import SQLAlchemyRepository
from app.services.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    """
    Facade class to handle business logic and coordinate between layers.
    Uses UserRepository for user operations and SQLAlchemyRepository
    for all other entities.
    """

    def __init__(self):
        """Initialize the facade with repositories for each entity."""
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # ===================== USER OPERATIONS =====================

    def create_user(self, user_data: dict) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary with user information

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists or validation fails
        """
        existing_user = self.user_repo.get_user_by_email(
            user_data.get('email')
        )
        if existing_user:
            raise ValueError("Email already registered")
        user = User(
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            is_admin=user_data.get('is_admin', False)
        )
        self.user_repo.add(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update user information."""
        user = self.get_user(user_id)
        if not user:
            return None
        if 'email' in user_data and user_data['email'] != user.email:
            existing = self.get_user_by_email(user_data['email'])
            if existing:
                raise ValueError("Email already registered")
        if 'password' in user_data:
            user.hash_password(user_data.pop('password'))
        updated_user = self.user_repo.update(user_id, user_data)
        if updated_user:
            updated_user.validate()
        return updated_user

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self.user_repo.delete(user_id)

    # ===================== AMENITY OPERATIONS =====================

    def create_amenity(self, amenity_data: dict) -> Amenity:
        """
        Create a new amenity.

        Args:
            amenity_data: Dictionary with amenity information

        Returns:
            Created Amenity object

        Raises:
            ValueError: If validation fails
        """
        amenity = Amenity(
            name=amenity_data.get('name'),
            description=amenity_data.get('description', '')
        )
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id: str) -> Optional[Amenity]:
        """Retrieve an amenity by ID."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self) -> List[Amenity]:
        """Retrieve all amenities."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id: str,
                       amenity_data: dict) -> Optional[Amenity]:
        """Update amenity information."""
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        updated_amenity = self.amenity_repo.update(amenity_id, amenity_data)
        if updated_amenity:
            updated_amenity.validate()
        return updated_amenity

    def delete_amenity(self, amenity_id: str) -> bool:
        """Delete an amenity."""
        return self.amenity_repo.delete(amenity_id)

    # ===================== PLACE OPERATIONS =====================

    def create_place(self, place_data: dict) -> Place:
        """
        Create a new place.

        Args:
            place_data: Dictionary with place information

        Returns:
            Created Place object

        Raises:
            ValueError: If owner doesn't exist or validation fails
        """
        owner = self.get_user(place_data.get('owner_id'))
        if not owner:
            raise ValueError("Owner not found")

        place = Place(
            title=place_data.get('title'),
            description=place_data.get('description'),
            price=place_data.get('price'),
            latitude=place_data.get('latitude'),
            longitude=place_data.get('longitude'),
            owner_id=owner.id
        )

        # Attach amenities via SQLAlchemy relationship
        amenity_ids = place_data.get('amenities', [])
        for amenity_id in amenity_ids:
            amenity = self.get_amenity(amenity_id)
            if amenity:
                place.amenities.append(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id: str) -> Optional[Place]:
        """
        Retrieve a place by ID.
        Owner and amenities are loaded automatically by SQLAlchemy.
        """
        return self.place_repo.get(place_id)

    def get_all_places(self) -> List[Place]:
        """
        Retrieve all places.
        Owner and amenities are loaded automatically by SQLAlchemy.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id: str,
                     place_data: dict) -> Optional[Place]:
        """Update place information."""
        place = self.get_place(place_id)
        if not place:
            return None

        # Update amenities via SQLAlchemy relationship
        if 'amenities' in place_data:
            amenity_ids = place_data.pop('amenities')
            place.amenities = []
            for amenity_id in amenity_ids:
                amenity = self.get_amenity(amenity_id)
                if amenity:
                    place.amenities.append(amenity)

        updated_place = self.place_repo.update(place_id, place_data)
        if updated_place:
            updated_place.validate()
        return updated_place

    def delete_place(self, place_id: str) -> bool:
        """Delete a place."""
        return self.place_repo.delete(place_id)

    # ===================== REVIEW OPERATIONS =====================

    def create_review(self, review_data: dict) -> Review:
        """
        Create a new review.

        Args:
            review_data: Dictionary with review information

        Returns:
            Created Review object

        Raises:
            ValueError: If validation fails or business rules violated
        """
        user = self.get_user(review_data.get('user_id'))
        if not user:
            raise ValueError("User not found")

        place = self.get_place(review_data.get('place_id'))
        if not place:
            raise ValueError("Place not found")

        if place.owner_id == user.id:
            raise ValueError("You cannot review your own place")

        existing_reviews = self.get_reviews_by_place(place.id)
        for review in existing_reviews:
            if review.user_id == user.id:
                raise ValueError(
                    "You have already reviewed this place"
                )

        review = Review(
            rating=review_data.get('rating'),
            comment=review_data.get('comment'),
            user_id=user.id,
            place_id=place.id
        )
        self.review_repo.add(review)
        return review

    def get_review(self, review_id: str) -> Optional[Review]:
        """
        Retrieve a review by ID.
        Author and place are loaded automatically by SQLAlchemy.
        """
        return self.review_repo.get(review_id)

    def get_all_reviews(self) -> List[Review]:
        """Retrieve all reviews."""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id: str) -> List[Review]:
        """Retrieve all reviews for a specific place."""
        all_reviews = self.review_repo.get_all()
        return [r for r in all_reviews if r.place_id == place_id]

    def update_review(self, review_id: str,
                      review_data: dict) -> Optional[Review]:
        """Update review information."""
        review = self.get_review(review_id)
        if not review:
            return None
        updated_review = self.review_repo.update(review_id, review_data)
        if updated_review:
            updated_review.validate()
        return updated_review

    def delete_review(self, review_id: str) -> bool:
        """Delete a review."""
        return self.review_repo.delete(review_id)


# Create a singleton instance
facade = HBnBFacade()
