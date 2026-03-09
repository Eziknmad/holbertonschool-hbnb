#!/usr/bin/env python3
"""Test script for User API endpoints."""

import requests
import json

BASE_URL = "http://localhost:5000/api/v1/users"


def print_response(response, operation):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{operation}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_create_user():
    """Test user creation."""
    print("\n### TEST 1: Create User ###")
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    response = requests.post(BASE_URL + "/", json=user_data)
    print_response(response, "POST /api/v1/users/")
    return response.json().get('id') if response.status_code == 201 else None


def test_get_all_users():
    """Test getting all users."""
    print("\n### TEST 2: Get All Users ###")
    response = requests.get(BASE_URL + "/")
    print_response(response, "GET /api/v1/users/")


def test_get_user(user_id):
    """Test getting user by ID."""
    print("\n### TEST 3: Get User by ID ###")
    response = requests.get(f"{BASE_URL}/{user_id}")
    print_response(response, f"GET /api/v1/users/{user_id}")


def test_update_user(user_id):
    """Test updating user."""
    print("\n### TEST 4: Update User ###")
    update_data = {
        "first_name": "Johnny",
        "last_name": "Updated"
    }
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data)
    print_response(response, f"PUT /api/v1/users/{user_id}")


def test_duplicate_email():
    """Test duplicate email validation."""
    print("\n### TEST 5: Duplicate Email (Should Fail) ###")
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "john.doe@example.com"
    }
    response = requests.post(BASE_URL + "/", json=user_data)
    print_response(response, "POST /api/v1/users/ (Duplicate)")


def test_invalid_email():
    """Test invalid email validation."""
    print("\n### TEST 6: Invalid Email (Should Fail) ###")
    user_data = {
        "first_name": "Invalid",
        "last_name": "User",
        "email": "not-an-email"
    }
    response = requests.post(BASE_URL + "/", json=user_data)
    print_response(response, "POST /api/v1/users/ (Invalid Email)")


def test_user_not_found():
    """Test getting non-existent user."""
    print("\n### TEST 7: User Not Found (Should Fail) ###")
    response = requests.get(f"{BASE_URL}/nonexistent-id-12345")
    print_response(response, "GET /api/v1/users/nonexistent-id")


if __name__ == '__main__':
    print("="*60)
    print("TESTING USER API ENDPOINTS")
    print("="*60)
    print("\nMake sure the Flask server is running on port 5000!")
    print("Run: python3 run.py")
    input("\nPress Enter to continue...")

    # Run tests
    user_id = test_create_user()

    if user_id:
        test_get_all_users()
        test_get_user(user_id)
        test_update_user(user_id)

    test_duplicate_email()
    test_invalid_email()
    test_user_not_found()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
