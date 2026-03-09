#!/usr/bin/env python3
"""Test script for Review API endpoints."""
import json
import requests

BASE_URL = "http://localhost:5000/api/v1"
USERS_URL = f"{BASE_URL}/users"
PLACES_URL = f"{BASE_URL}/places"
REVIEWS_URL = f"{BASE_URL}/reviews"
AMENITIES_URL = f"{BASE_URL}/amenities"


def print_response(response, operation):
    """Print formatted response."""
    print(f"\n{'=' * 60}")
    print(operation)
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        if response.status_code != 204:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("Response: No content (204)")
    except ValueError:
        print(f"Response: {response.text}")


def setup_test_data():
    """Create test users and place."""
    print("\n### SETUP: Creating Test Data ###")

    owner_data = {
        "first_name": "John",
        "last_name": "Owner",
        "email": "john.owner@example.com"
    }
    owner_response = requests.post(f"{USERS_URL}/", json=owner_data)
    owner_id = owner_response.json().get("id") if \
        owner_response.status_code == 201 else None

    reviewer_data = {
        "first_name": "Jane",
        "last_name": "Reviewer",
        "email": "jane.reviewer@example.com"
    }
    reviewer_response = requests.post(f"{USERS_URL}/", json=reviewer_data)
    reviewer_id = reviewer_response.json().get("id") if \
        reviewer_response.status_code == 201 else None

    place_data = {
        "title": "Test Place",
        "description": "A place to review",
        "price": 100.00,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner_id": owner_id
    }
    place_response = requests.post(f"{PLACES_URL}/", json=place_data)
    place_id = place_response.json().get("id") if \
        place_response.status_code == 201 else None

    return owner_id, reviewer_id, place_id


def test_create_review(user_id, place_id):
    """Test review creation."""
    print("\n### TEST 1: Create Review ###")
    review_data = {
        "rating": 5,
        "comment": "Amazing place! Highly recommended.",
        "user_id": user_id,
        "place_id": place_id
    }
    response = requests.post(f"{REVIEWS_URL}/", json=review_data)
    print_response(response, "POST /api/v1/reviews/")
    return response.json().get("id") if response.status_code == 201 \
        else None


def test_get_all_reviews():
    """Test getting all reviews."""
    print("\n### TEST 2: Get All Reviews ###")
    response = requests.get(f"{REVIEWS_URL}/")
    print_response(response, "GET /api/v1/reviews/")


def test_get_review(review_id):
    """Test getting review by ID."""
    print("\n### TEST 3: Get Review by ID ###")
    response = requests.get(f"{REVIEWS_URL}/{review_id}")
    print_response(response, f"GET /api/v1/reviews/{review_id}")


def test_get_place_reviews(place_id):
    """Test getting reviews for a specific place."""
    print("\n### TEST 4: Get Reviews for Place ###")
    response = requests.get(f"{REVIEWS_URL}/places/{place_id}/reviews")
    print_response(response, f"GET /api/v1/reviews/places/{place_id}/reviews")


def test_update_review(review_id):
    """Test updating review."""
    print("\n### TEST 5: Update Review ###")
    update_data = {
        "rating": 4,
        "comment": "Updated: Still great but a bit pricey."
    }
    response = requests.put(f"{REVIEWS_URL}/{review_id}", json=update_data)
    print_response(response, f"PUT /api/v1/reviews/{review_id}")


def test_delete_review(review_id):
    """Test deleting review."""
    print("\n### TEST 6: Delete Review ###")
    response = requests.delete(f"{REVIEWS_URL}/{review_id}")
    print_response(response, f"DELETE /api/v1/reviews/{review_id}")


def test_owner_cannot_review(owner_id, place_id):
    """Test that owner cannot review own place."""
    print("\n### TEST 7: Owner Review Own Place (Should Fail) ###")
    review_data = {
        "rating": 5,
        "comment": "My own place is great!",
        "user_id": owner_id,
        "place_id": place_id
    }
    response = requests.post(f"{REVIEWS_URL}/", json=review_data)
    print_response(response, "POST /api/v1/reviews/ (Owner)")


def test_duplicate_review(user_id, place_id):
    """Test duplicate review prevention."""
    print("\n### TEST 8: Duplicate Review (Should Fail) ###")
    review_data = {
        "rating": 4,
        "comment": "Another review for the same place",
        "user_id": user_id,
        "place_id": place_id
    }
    response = requests.post(f"{REVIEWS_URL}/", json=review_data)
    print_response(response, "POST /api/v1/reviews/ (Duplicate)")


def test_invalid_rating(user_id, place_id):
    """Test invalid rating."""
    print("\n### TEST 9: Invalid Rating (Should Fail) ###")
    review_data = {
        "rating": 6,
        "comment": "This should fail",
        "user_id": user_id,
        "place_id": place_id
    }
    response = requests.post(f"{REVIEWS_URL}/", json=review_data)
    print_response(response, "POST /api/v1/reviews/ (Invalid Rating)")


def test_review_not_found():
    """Test getting non-existent review."""
    print("\n### TEST 10: Review Not Found (Should Fail) ###")
    response = requests.get(f"{REVIEWS_URL}/nonexistent-id")
    print_response(response, "GET /api/v1/reviews/nonexistent-id")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING REVIEW API ENDPOINTS")
    print("=" * 60)
    print("\nMake sure the Flask server is running on port 5000!")
    print("Run: python3 run.py")
    input("\nPress Enter to continue...")

    owner_id, reviewer_id, place_id = setup_test_data()

    if not all([owner_id, reviewer_id, place_id]):
        print("\n❌ Failed to create test data. Aborting tests.")
        exit(1)

    review_id = test_create_review(reviewer_id, place_id)

    if review_id:
        test_get_all_reviews()
        test_get_review(review_id)
        test_get_place_reviews(place_id)
        test_update_review(review_id)

    test_owner_cannot_review(owner_id, place_id)
    test_duplicate_review(reviewer_id, place_id)
    test_invalid_rating(reviewer_id, place_id)
    test_review_not_found()

    if review_id:
        test_delete_review(review_id)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
