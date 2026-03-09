#!/usr/bin/env python3
"""Test script for Place API endpoints."""

import json
import requests

BASE_URL = "http://localhost:5000/api/v1"
USERS_URL = f"{BASE_URL}/users"
AMENITIES_URL = f"{BASE_URL}/amenities"
PLACES_URL = f"{BASE_URL}/places"


def print_response(response, operation):
    """Print formatted response."""
    print(f"\n{'=' * 60}")
    print(operation)
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Response: {response.text}")


def setup_test_data():
    """Create test user and amenities."""
    print("\n### SETUP: Creating Test Data ###")

    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.place.owner@example.com"
    }
    user_response = requests.post(f"{USERS_URL}/", json=user_data)
    print_response(user_response, "Create Test User")
    user_id = user_response.json().get("id") if \
        user_response.status_code == 201 else None

    amenity1_data = {"name": "WiFi", "description": "High-speed internet"}
    amenity1_response = requests.post(
        f"{AMENITIES_URL}/",
        json=amenity1_data
    )
    amenity1_id = amenity1_response.json().get("id") if \
        amenity1_response.status_code == 201 else None

    amenity2_data = {
        "name": "Parking",
        "description": "Free parking space"
    }
    amenity2_response = requests.post(
        f"{AMENITIES_URL}/",
        json=amenity2_data
    )
    amenity2_id = amenity2_response.json().get("id") if \
        amenity2_response.status_code == 201 else None

    return user_id, [amenity1_id, amenity2_id]


def test_create_place(owner_id, amenity_ids):
    """Test place creation."""
    print("\n### TEST 1: Create Place ###")
    place_data = {
        "title": "Cozy Beach House",
        "description": "A beautiful beachfront property",
        "price": 150.00,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "owner_id": owner_id,
        "amenities": amenity_ids
    }
    response = requests.post(f"{PLACES_URL}/", json=place_data)
    print_response(response, "POST /api/v1/places/")
    return response.json().get("id") if response.status_code == 201 else None


def test_get_all_places():
    """Test getting all places."""
    print("\n### TEST 2: Get All Places ###")
    response = requests.get(f"{PLACES_URL}/")
    print_response(response, "GET /api/v1/places/")


def test_get_place(place_id):
    """Test getting place by ID."""
    print("\n### TEST 3: Get Place by ID ###")
    response = requests.get(f"{PLACES_URL}/{place_id}")
    print_response(response, f"GET /api/v1/places/{place_id}")


def test_update_place(place_id):
    """Test updating place."""
    print("\n### TEST 4: Update Place ###")
    update_data = {
        "title": "Luxury Beach House",
        "price": 200.00
    }
    response = requests.put(f"{PLACES_URL}/{place_id}", json=update_data)
    print_response(response, f"PUT /api/v1/places/{place_id}")


def test_invalid_price(owner_id):
    """Test invalid price validation."""
    print("\n### TEST 5: Invalid Price (Should Fail) ###")
    place_data = {
        "title": "Test Place",
        "description": "Test",
        "price": -10.00,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner_id": owner_id
    }
    response = requests.post(f"{PLACES_URL}/", json=place_data)
    print_response(response, "POST /api/v1/places/ (Negative Price)")


def test_invalid_coordinates(owner_id):
    """Test invalid coordinates validation."""
    print("\n### TEST 6: Invalid Coordinates (Should Fail) ###")
    place_data = {
        "title": "Test Place",
        "description": "Test",
        "price": 100.00,
        "latitude": 200.0,
        "longitude": 0.0,
        "owner_id": owner_id
    }
    response = requests.post(f"{PLACES_URL}/", json=place_data)
    print_response(response, "POST /api/v1/places/ (Invalid Latitude)")


def test_nonexistent_owner():
    """Test creating place with non-existent owner."""
    print("\n### TEST 7: Non-existent Owner (Should Fail) ###")
    place_data = {
        "title": "Test Place",
        "description": "Test",
        "price": 100.00,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner_id": "nonexistent-owner-id"
    }
    response = requests.post(f"{PLACES_URL}/", json=place_data)
    print_response(response, "POST /api/v1/places/ (Invalid Owner)")


def test_place_not_found():
    """Test getting non-existent place."""
    print("\n### TEST 8: Place Not Found (Should Fail) ###")
    response = requests.get(f"{PLACES_URL}/nonexistent-id-12345")
    print_response(response, "GET /api/v1/places/nonexistent-id")


def test_update_owner_id(place_id):
    """Test that owner_id cannot be updated."""
    print("\n### TEST 9: Update Owner ID (Should Fail) ###")
    update_data = {
        "owner_id": "different-owner-id"
    }
    response = requests.put(f"{PLACES_URL}/{place_id}", json=update_data)
    print_response(response, "PUT /api/v1/places/ (Try Update Owner)")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING PLACE API ENDPOINTS")
    print("=" * 60)
    print("\nMake sure the Flask server is running on port 5000!")
    print("Run: python3 run.py")
    input("\nPress Enter to continue...")

    owner_id, amenity_ids = setup_test_data()

    if not owner_id:
        print("\n❌ Failed to create test user. Aborting tests.")
        exit(1)

    place_id = test_create_place(owner_id, amenity_ids)

    if place_id:
        test_get_all_places()
        test_get_place(place_id)
        test_update_place(place_id)
        test_update_owner_id(place_id)

    test_invalid_price(owner_id)
    test_invalid_coordinates(owner_id)
    test_nonexistent_owner()
    test_place_not_found()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
