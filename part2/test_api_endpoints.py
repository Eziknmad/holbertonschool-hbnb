#!/usr/bin/env python3
"""
Comprehensive unit tests for HBnB API endpoints.
Tests all CRUD operations and validation rules.
"""
import unittest
import json
import uuid
from app import create_app


def unique_email(prefix="test"):
    """Generate a unique email for each test."""
    return f"{prefix}.{uuid.uuid4().hex[:8]}@example.com"


class TestUserEndpoints(unittest.TestCase):
    """Test cases for User endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def test_create_user_success(self):
        """Test successful user creation."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": unique_email("john")
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'John')

    def test_create_user_missing_fields(self):
        """Test user creation with missing fields."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_email(self):
        """Test duplicate email rejection."""
        email = unique_email("duplicate")
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": email
        }
        self.client.post('/api/v1/users/', json=user_data)
        response = self.client.post('/api/v1/users/', json=user_data)
        self.assertEqual(response.status_code, 409)

    def test_get_all_users(self):
        """Test retrieving all users."""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_user_by_id(self):
        """Test retrieving user by ID."""
        create_response = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": unique_email("jane")
        })
        user_id = json.loads(create_response.data)['id']

        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], user_id)

    def test_get_user_not_found(self):
        """Test retrieving non-existent user."""
        response = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        """Test updating user."""
        create_response = self.client.post('/api/v1/users/', json={
            "first_name": "Update",
            "last_name": "Test",
            "email": unique_email("update")
        })
        user_id = json.loads(create_response.data)['id']

        response = self.client.put(f'/api/v1/users/{user_id}', json={
            "first_name": "Updated"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Updated')


class TestAmenityEndpoints(unittest.TestCase):
    """Test cases for Amenity endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def test_create_amenity_success(self):
        """Test successful amenity creation."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": f"WiFi-{uuid.uuid4().hex[:6]}",
            "description": "High-speed internet"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_create_amenity_missing_name(self):
        """Test amenity creation without name."""
        response = self.client.post('/api/v1/amenities/', json={
            "description": "Test"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_name_too_long(self):
        """Test amenity with name exceeding 50 characters."""
        response = self.client.post('/api/v1/amenities/', json={
            "name": "A" * 51
        })
        self.assertEqual(response.status_code, 400)

    def test_get_all_amenities(self):
        """Test retrieving all amenities."""
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_amenity_not_found(self):
        """Test retrieving non-existent amenity."""
        response = self.client.get('/api/v1/amenities/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_amenity(self):
        """Test updating amenity."""
        create_response = self.client.post('/api/v1/amenities/', json={
            "name": f"Pool-{uuid.uuid4().hex[:6]}"
        })
        amenity_id = json.loads(create_response.data)['id']

        response = self.client.put(
            f'/api/v1/amenities/{amenity_id}',
            json={"description": "Updated description"}
        )
        self.assertEqual(response.status_code, 200)


class TestPlaceEndpoints(unittest.TestCase):
    """Test cases for Place endpoints."""

    def setUp(self):
        """Set up test client and create unique test user."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        user_response = self.client.post('/api/v1/users/', json={
            "first_name": "Owner",
            "last_name": "Test",
            "email": unique_email("owner.place")
        })
        data = json.loads(user_response.data)
        self.assertIn(
            'id', data,
            f"User creation failed: {data}"
        )
        self.owner_id = data['id']

    def test_create_place_success(self):
        """Test successful place creation."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Test Place",
            "description": "A nice place",
            "price": 100.00,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "owner_id": self.owner_id
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['title'], 'Test Place')

    def test_create_place_negative_price(self):
        """Test place creation with negative price."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Test",
            "description": "Test",
            "price": -10.00,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": self.owner_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_latitude(self):
        """Test place with latitude out of range."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Test",
            "description": "Test",
            "price": 100.00,
            "latitude": 91.0,
            "longitude": 0.0,
            "owner_id": self.owner_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_longitude(self):
        """Test place with longitude out of range."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Test",
            "description": "Test",
            "price": 100.00,
            "latitude": 0.0,
            "longitude": 181.0,
            "owner_id": self.owner_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_place_nonexistent_owner(self):
        """Test place creation with invalid owner."""
        response = self.client.post('/api/v1/places/', json={
            "title": "Test",
            "description": "Test",
            "price": 100.00,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": "nonexistent-id"
        })
        self.assertEqual(response.status_code, 404)

    def test_get_all_places(self):
        """Test retrieving all places."""
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_place_not_found(self):
        """Test retrieving non-existent place."""
        response = self.client.get('/api/v1/places/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_place(self):
        """Test updating place."""
        create_response = self.client.post('/api/v1/places/', json={
            "title": "Update Test",
            "description": "Test",
            "price": 100.00,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": self.owner_id
        })
        place_id = json.loads(create_response.data)['id']

        response = self.client.put(f'/api/v1/places/{place_id}', json={
            "price": 150.00
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['price'], 150.00)

    def test_update_place_owner_id_protected(self):
        """Test that owner_id cannot be updated."""
        create_response = self.client.post('/api/v1/places/', json={
            "title": "Test",
            "description": "Test",
            "price": 100.00,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": self.owner_id
        })
        place_id = json.loads(create_response.data)['id']

        response = self.client.put(f'/api/v1/places/{place_id}', json={
            "owner_id": "different-owner"
        })
        self.assertEqual(response.status_code, 400)


class TestReviewEndpoints(unittest.TestCase):
    """Test cases for Review endpoints."""

    def setUp(self):
        """Set up test client and create unique test data."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        owner_response = self.client.post('/api/v1/users/', json={
            "first_name": "Owner",
            "last_name": "Review",
            "email": unique_email("owner.review")
        })
        owner_data = json.loads(owner_response.data)
        self.assertIn(
            'id', owner_data,
            f"Owner creation failed: {owner_data}"
        )
        self.owner_id = owner_data['id']

        reviewer_response = self.client.post('/api/v1/users/', json={
            "first_name": "Reviewer",
            "last_name": "Test",
            "email": unique_email("reviewer")
        })
        reviewer_data = json.loads(reviewer_response.data)
        self.assertIn(
            'id', reviewer_data,
            f"Reviewer creation failed: {reviewer_data}"
        )
        self.reviewer_id = reviewer_data['id']

        place_response = self.client.post('/api/v1/places/', json={
            "title": "Review Test Place",
            "description": "Test",
            "price": 100.00,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": self.owner_id
        })
        place_data = json.loads(place_response.data)
        self.assertIn(
            'id', place_data,
            f"Place creation failed: {place_data}"
        )
        self.place_id = place_data['id']

    def test_create_review_success(self):
        """Test successful review creation."""
        response = self.client.post('/api/v1/reviews/', json={
            "rating": 5,
            "comment": "Great place to stay!",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['rating'], 5)

    def test_create_review_invalid_rating(self):
        """Test review with rating out of range."""
        response = self.client.post('/api/v1/reviews/', json={
            "rating": 6,
            "comment": "This should fail",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_review_owner_cannot_review(self):
        """Test that owner cannot review own place."""
        response = self.client.post('/api/v1/reviews/', json={
            "rating": 5,
            "comment": "My place is great!",
            "user_id": self.owner_id,
            "place_id": self.place_id
        })
        self.assertEqual(response.status_code, 409)

    def test_create_review_duplicate(self):
        """Test duplicate review prevention."""
        review_data = {
            "rating": 5,
            "comment": "First review here",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        }
        self.client.post('/api/v1/reviews/', json=review_data)

        review_data['comment'] = "Second review attempt"
        response = self.client.post('/api/v1/reviews/', json=review_data)
        self.assertEqual(response.status_code, 409)

    def test_get_all_reviews(self):
        """Test retrieving all reviews."""
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_review_not_found(self):
        """Test retrieving non-existent review."""
        response = self.client.get('/api/v1/reviews/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_review(self):
        """Test updating review."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "rating": 4,
            "comment": "Good place overall",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        review_id = json.loads(create_response.data)['id']

        response = self.client.put(f'/api/v1/reviews/{review_id}', json={
            "rating": 5,
            "comment": "Updated: Excellent place!"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['rating'], 5)

    def test_delete_review(self):
        """Test deleting review."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "rating": 3,
            "comment": "Average place overall",
            "user_id": self.reviewer_id,
            "place_id": self.place_id
        })
        review_id = json.loads(create_response.data)['id']

        response = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(response.status_code, 204)

        get_response = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(get_response.status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
