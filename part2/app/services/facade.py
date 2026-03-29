"""
Facade pattern implementation for HBnB application.
Provides a simplified interface to the business logic layer.
"""
from typing import List, Optional
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    """
    Facade class to handle business logic and coordinate between layers.
    """

    def __init__(self):
        """Initialize the facade with repositories for each entity type."""
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

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
        # Check if email already exists
        existing_user = self.user_repo.get_by_attribute(
            'email', user_data.get('email')
        )
        if existing_user:
            raise ValueError("Email already registered")

        # Create user — password is hashed inside User.__init__()
        user = User(
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            is_admin=user_data.get('is_admin', False)
        )

        # Save to repository
        self.user_repo.add(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update user information."""
        user = self.get_user(user_id)
        if not user:
            return None

        # Check email uniqueness if email is being updated
        if 'email' in user_data and user_data['email'] != user.email:
            existing = self.get_user_by_email(user_data['email'])
            if existing:
                raise ValueError("Email already registered")

        # Handle password separately — must be hashed, not stored plain
        if 'password' in user_data:
            user.hash_password(user_data.pop('password'))

        # Update and validate
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
        # Verify owner exists
        owner = self.get_user(place_data.get('owner_id'))
        if not owner:
            raise ValueError("Owner not found")

        # Create place
        place = Place(
            title=place_data.get('title'),
            description=place_data.get('description'),
            price=place_data.get('price'),
            latitude=place_data.get('latitude'),
            longitude=place_data.get('longitude'),
            owner_id=owner.id
        )

        # Set owner reference for composition
        place.owner = owner

        # Add amenities if provided
        amenity_ids = place_data.get('amenities', [])
        for amenity_id in amenity_ids:
            amenity = self.get_amenity(amenity_id)
            if amenity:
                place.add_amenity(amenity)

        # Save to repository
        self.place_repo.add(place)
        return place

    def get_place(self, place_id: str) -> Optional[Place]:
        """Retrieve a place by ID with owner and amenities."""
        place = self.place_repo.get(place_id)
        if place:
            # Set owner reference
            place.owner = self.get_user(place.owner_id)
            # Set amenity references
            amenity_objects = []
            for amenity in place.amenities:
                amenity_id = amenity.id if hasattr(amenity, 'id') \
                    else amenity
                amenity_obj = self.get_amenity(amenity_id)
                if amenity_obj:
                    amenity_objects.append(amenity_obj)
            place.amenities = amenity_objects
        return place

    def get_all_places(self) -> List[Place]:
        """Retrieve all places."""
        places = self.place_repo.get_all()
        # Populate owner and amenities for each place
        for place in places:
            place.owner = self.get_user(place.owner_id)
            amenity_objects = []
            for amenity in place.amenities:
                amenity_id = amenity.id if hasattr(amenity, 'id') \
                    else amenity
                amenity_obj = self.get_amenity(amenity_id)
                if amenity_obj:
                    amenity_objects.append(amenity_obj)
            place.amenities = amenity_objects
        return places

    def update_place(self, place_id: str,
                     place_data: dict) -> Optional[Place]:
        """Update place information."""
        place = self.get_place(place_id)
        if not place:
            return None

        # Handle amenities update separately
        if 'amenities' in place_data:
            amenity_ids = place_data.pop('amenities')
            place.amenities = []
            for amenity_id in amenity_ids:
                amenity = self.get_amenity(amenity_id)
                if amenity:
                    place.add_amenity(amenity)

        # Update other fields
        updated_place = self.place_repo.update(place_id, place_data)
        if updated_place:
            updated_place.validate()
            updated_place.owner = self.get_user(updated_place.owner_id)
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
        # Verify user exists
        user = self.get_user(review_data.get('user_id'))
        if not user:
            raise ValueError("User not found")

        # Verify place exists
        place = self.get_place(review_data.get('place_id'))
        if not place:
            raise ValueError("Place not found")

        # Business rule: Users cannot review their own places
        if place.owner_id == user.id:
            raise ValueError("You cannot review your own place")

        # Business rule: Each user can only review a place once
        existing_reviews = self.get_reviews_by_place(place.id)
        for review in existing_reviews:
            if review.user_id == user.id:
                raise ValueError(
                    "You have already reviewed this place"
                )

        # Create review
        review = Review(
            rating=review_data.get('rating'),
            comment=review_data.get('comment'),
            user_id=user.id,
            place_id=place.id
        )

        # Set references for composition
        review.user = user
        review.place = place

        # Save to repository
        self.review_repo.add(review)

        # Add review to place
        place.add_review(review)

        return review

    def get_review(self, review_id: str) -> Optional[Review]:
        """Retrieve a review by ID."""
        review = self.review_repo.get(review_id)
        if review:
            review.user = self.get_user(review.user_id)
            review.place = self.get_place(review.place_id)
        return review

    def get_all_reviews(self) -> List[Review]:
        """Retrieve all reviews."""
        reviews = self.review_repo.get_all()
        for review in reviews:
            review.user = self.get_user(review.user_id)
            review.place = self.get_place(review.place_id)
        return reviews

    def get_reviews_by_place(self, place_id: str) -> List[Review]:
        """Retrieve all reviews for a specific place."""
        all_reviews = self.review_repo.get_all()
        place_reviews = [r for r in all_reviews if r.place_id == place_id]
        for review in place_reviews:
            review.user = self.get_user(review.user_id)
            review.place = self.get_place(review.place_id)
        return place_reviews

    def update_review(self, review_id: str,
                      review_data: dict) -> Optional[Review]:
        """Update review information."""
        review = self.get_review(review_id)
        if not review:
            return None

        updated_review = self.review_repo.update(review_id, review_data)
        if updated_review:
            updated_review.validate()
            updated_review.user = self.get_user(updated_review.user_id)
            updated_review.place = self.get_place(updated_review.place_id)
        return updated_review

    def delete_review(self, review_id: str) -> bool:
        """Delete a review."""
        return self.review_repo.delete(review_id)


# Create a singleton instance
facade = HBnBFacade()
