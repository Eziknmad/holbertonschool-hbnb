#!/usr/bin/env python3
"""Test script for Amenity API endpoints."""

import json
import requests

BASE_URL = "http://localhost:5000/api/v1/amenities"


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


def test_create_amenity():
    """Test amenity creation."""
    print("\n### TEST 1: Create Amenity ###")
    amenity_data = {
        "name": "WiFi",
        "description": "High-speed wireless internet"
    }
    response = requests.post(BASE_URL + "/", json=amenity_data)
    print_response(response, "POST /api/v1/amenities/")
    return response.json().get("id") if response.status_code == 201 else None


def test_get_all_amenities():
    """Test getting all amenities."""
    print("\n### TEST 2: Get All Amenities ###")
    response = requests.get(BASE_URL + "/")
    print_response(response, "GET /api/v1/amenities/")


def test_get_amenity(amenity_id):
    """Test getting amenity by ID."""
    print("\n### TEST 3: Get Amenity by ID ###")
    response = requests.get(f"{BASE_URL}/{amenity_id}")
    print_response(response, f"GET /api/v1/amenities/{amenity_id}")


def test_update_amenity(amenity_id):
    """Test updating amenity."""
    print("\n### TEST 4: Update Amenity ###")
    update_data = {
        "name": "WiFi",
        "description": "Ultra-fast fiber optic internet connection"
    }
    response = requests.put(f"{BASE_URL}/{amenity_id}", json=update_data)
    print_response(response, f"PUT /api/v1/amenities/{amenity_id}")


def test_create_amenity_without_description():
    """Test creating amenity without description."""
    print("\n### TEST 5: Create Amenity Without Description ###")
    amenity_data = {
        "name": "Swimming Pool"
    }
    response = requests.post(BASE_URL + "/", json=amenity_data)
    print_response(response, "POST /api/v1/amenities/ (No Description)")
    return response.json().get("id") if response.status_code == 201 else None


def test_missing_name():
    """Test missing name validation."""
    print("\n### TEST 6: Missing Name (Should Fail) ###")
    amenity_data = {
        "description": "This should fail"
    }
    response = requests.post(BASE_URL + "/", json=amenity_data)
    print_response(response, "POST /api/v1/amenities/ (Missing Name)")


def test_amenity_not_found():
    """Test getting non-existent amenity."""
    print("\n### TEST 7: Amenity Not Found (Should Fail) ###")
    response = requests.get(f"{BASE_URL}/nonexistent-id-12345")
    print_response(response, "GET /api/v1/amenities/nonexistent-id")


def test_invalid_name_length():
    """Test name length validation."""
    print("\n### TEST 8: Invalid Name Length (Should Fail) ###")
    amenity_data = {
        "name": "A" * 51,  # Exceeds 50 character limit
        "description": "This should fail"
    }
    response = requests.post(BASE_URL + "/", json=amenity_data)
    print_response(response, "POST /api/v1/amenities/ (Name Too Long)")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING AMENITY API ENDPOINTS")
    print("=" * 60)
    print("\nMake sure the Flask server is running on port 5000!")
    print("Run: python3 run.py")
    input("\nPress Enter to continue...")

    amenity_id = test_create_amenity()

    if amenity_id:
        test_get_all_amenities()
        test_get_amenity(amenity_id)
        test_update_amenity(amenity_id)

    test_create_amenity_without_description()
    test_missing_name()
    test_amenity_not_found()
    test_invalid_name_length()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
