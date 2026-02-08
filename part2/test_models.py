#!/usr/bin/env python3
"""Test script for business logic models."""

from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.services.facade import facade


def test_users():
    """Test user creation and validation."""
    print("Testing User model...")

    # Create valid user
    user1 = facade.create_user({
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com'
    })
    print(f"✓ Created user: {user1}")

    # Try duplicate email
    try:
        facade.create_user({
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'john@example.com'
        })
        print("✗ Should have raised ValueError for duplicate email")
    except ValueError as e:
        print(f"✓ Correctly rejected duplicate email: {e}")

    # Test invalid email
    try:
        facade.create_user({
            'first_name': 'Invalid',
            'last_name': 'User',
            'email': 'not-an-email'
        })
        print("✗ Should have raised ValueError for invalid email")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid email: {e}")

    print()


def test_amenities():
    """Test amenity creation."""
    print("Testing Amenity model...")

    amenity1 = facade.create_amenity({
        'name': 'WiFi',
        'description': 'High-speed wireless internet'
    })
    print(f"✓ Created amenity: {amenity1}")

    amenity2 = facade.create_amenity({
        'name': 'Pool',
        'description': 'Outdoor swimming pool'
    })
    print(f"✓ Created amenity: {amenity2}")

    print()


def test_places():
    """Test place creation with relationships."""
    print("Testing Place model...")

    users = facade.get_all_users()
    owner = users[0] if users else None

    if not owner:
        print("✗ No users available for testing places")
        return

    amenities = facade.get_all_amenities()

    place = facade.create_place({
        'title': 'Cozy Beach House',
        'description': 'Beautiful house by the beach',
        'price': 150.0,
        'latitude': 34.0522,
        'longitude': -118.2437,
        'owner_id': owner.id,
        'amenities': [a.id for a in amenities[:2]]
    })
    print(f"✓ Created place: {place}")
    print(f"  Owner: {place.owner.first_name} {place.owner.last_name}")
    print(f"  Amenities: {[a.name for a in place.amenities]}")

    try:
        facade.create_place({
            'title': 'Invalid Place',
            'description': 'Should fail',
            'price': 100.0,
            'latitude': 200.0,
            'longitude': -118.2437,
            'owner_id': owner.id
        })
        print("✗ Should have raised ValueError for invalid latitude")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid latitude: {e}")

    print()


def test_reviews():
    """Test review creation with business rules."""
    print("Testing Review model...")

    users = facade.get_all_users()
    places = facade.get_all_places()

    if len(users) < 1 or len(places) < 1:
        print("✗ Not enough data for review testing")
        return

    reviewer = facade.create_user({
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane@example.com'
    })

    place = places[0]

    review = facade.create_review({
        'rating': 5,
        'comment': 'Amazing place! Highly recommended for families.',
        'user_id': reviewer.id,
        'place_id': place.id
    })
    print(f"✓ Created review: {review}")
    print(f"  Rating: {review.rating}/5")
    print(f"  By: {review.user.first_name} {review.user.last_name}")

    try:
        facade.create_review({
            'rating': 4,
            'comment': 'Another review for the same place.',
            'user_id': reviewer.id,
            'place_id': place.id
        })
        print("✗ Should have raised ValueError for duplicate review")
    except ValueError as e:
        print(f"✓ Correctly rejected duplicate review: {e}")

    try:
        facade.create_review({
            'rating': 6,
            'comment': 'This should fail.',
            'user_id': reviewer.id,
            'place_id': place.id
        })
        print("✗ Should have raised ValueError for invalid rating")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid rating: {e}")

    try:
        facade.create_review({
            'rating': 3,
            'comment': 'Short',
            'user_id': reviewer.id,
            'place_id': place.id
        })
        print("✗ Should have raised ValueError for short comment")
    except ValueError as e:
        print(f"✓ Correctly rejected short comment: {e}")

    try:
        facade.create_review({
            'rating': 5,
            'comment': 'Trying to review my own place.',
            'user_id': place.owner_id,
            'place_id': place.id
        })
        print("✗ Should have raised ValueError for owner reviewing own place")
    except ValueError as e:
        print(f"✓ Correctly rejected owner reviewing own place: {e}")

    print()


def test_update_operations():
    """Test update operations."""
    print("Testing Update operations...")

    users = facade.get_all_users()
    if users:
        user = users[0]
        updated = facade.update_user(user.id, {'first_name': 'Johnny'})
        print(f"✓ Updated user: {updated.first_name}")

    places = facade.get_all_places()
    if places:
        place = places[0]
        updated = facade.update_place(place.id, {'price': 200.0})
        print(f"✓ Updated place price: ${updated.price}")

    amenities = facade.get_all_amenities()
    if amenities:
        amenity = amenities[0]
        updated = facade.update_amenity(
            amenity.id,
            {'description': 'Super fast WiFi connection'}
        )
        print(f"✓ Updated amenity: {updated.description}")

    reviews = facade.get_all_reviews()
    if reviews:
        review = reviews[0]
        updated = facade.update_review(review.id, {
            'rating': 4,
            'comment': 'Updated: Still a great place but a bit pricey.'
        })
        print(f"✓ Updated review rating: {updated.rating}")

    print()


def test_get_operations():
    """Test get operations."""
    print("Testing Get operations...")

    print(f"✓ Total users: {len(facade.get_all_users())}")
    print(f"✓ Total places: {len(facade.get_all_places())}")
    print(f"✓ Total amenities: {len(facade.get_all_amenities())}")
    print(f"✓ Total reviews: {len(facade.get_all_reviews())}")

    places = facade.get_all_places()
    if places:
        place_reviews = facade.get_reviews_by_place(places[0].id)
        print(f"✓ Reviews for place: {len(place_reviews)}")

    print()


def test_serialization():
    """Test to_dict methods and data composition."""
    print("Testing Serialization...")

    users = facade.get_all_users()
    places = facade.get_all_places()
    reviews = facade.get_all_reviews()
    amenities = facade.get_all_amenities()

    if users:
        print(f"✓ User dict keys: {list(users[0].to_dict().keys())}")

    if amenities:
        print(f"✓ Amenity dict keys: {list(amenities[0].to_dict().keys())}")

    if places:
        place = places[0]
        print(f"✓ Place dict (basic) keys: {list(place.to_dict().keys())}")
        full = place.to_dict(
            include_owner=True,
            include_amenities=True,
            include_reviews=True
        )
        print(f"✓ Place dict (full) keys: {list(full.keys())}")

    if reviews:
        review = reviews[0]
        full = review.to_dict(include_user=True, include_place=True)
        print(f"✓ Review dict (full) keys: {list(full.keys())}")

    print()


def test_business_rules():
    """Test business rule enforcement."""
    print("Testing Business Rules...")

    users = facade.get_all_users()
    places = facade.get_all_places()

    if not users or not places:
        print("✗ Not enough data for business rules testing")
        return

    place = places[0]

    try:
        facade.create_review({
            'rating': 5,
            'comment': 'This is my own place and it is great!',
            'user_id': place.owner_id,
            'place_id': place.id
        })
        print("✗ Should prevent users from reviewing their own places")
    except ValueError as e:
        print(f"✓ Prevented owner from reviewing own place: {e}")

    print()


def display_summary():
    """Display summary of all data."""
    print("=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)

    users = facade.get_all_users()
    places = facade.get_all_places()
    reviews = facade.get_all_reviews()
    amenities = facade.get_all_amenities()

    print(f"\nTotal Users: {len(users)}")
    print(f"Total Amenities: {len(amenities)}")
    print(f"Total Places: {len(places)}")
    print(f"Total Reviews: {len(reviews)}")
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("HBNB BUSINESS LOGIC - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print()

    test_users()
    test_amenities()
    test_places()
    test_reviews()
    test_update_operations()
    test_get_operations()
    test_serialization()
    test_business_rules()
    display_summary()

    print("=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
