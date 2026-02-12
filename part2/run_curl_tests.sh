#!/bin/bash
# Comprehensive cURL testing script for HBnB API

echo "=========================================="
echo "HBnB API - cURL Testing Suite"
echo "=========================================="
echo ""

BASE_URL="http://127.0.0.1:5000/api/v1"

echo "Testing User Endpoints..."
echo "1. Create User (Valid)"
curl -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john.curl@example.com"}'
echo -e "\n"

echo "2. Create User (Invalid Email)"
curl -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Doe","email":"invalid"}'
echo -e "\n"

echo "3. Get All Users"
curl -X GET "$BASE_URL/users/"
echo -e "\n"

echo "=========================================="
echo "Testing Amenity Endpoints..."
echo "1. Create Amenity"
curl -X POST "$BASE_URL/amenities/" \
  -H "Content-Type: application/json" \
  -d '{"name":"WiFi","description":"High-speed internet"}'
echo -e "\n"

echo "2. Create Amenity (Name Too Long)"
curl -X POST "$BASE_URL/amenities/" \
  -H "Content-Type: application/json" \
  -d '{"name":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}'
echo -e "\n"

echo "=========================================="
echo "All cURL tests completed!"
