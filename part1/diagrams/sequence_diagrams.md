# HBnB Evolution - API Sequence Diagrams

## Overview
This document presents sequence diagrams for four critical API operations in the HBnB Evolution application. Each diagram illustrates the step-by-step interaction between the Presentation Layer (API), Business Logic Layer (Models & Facade), and Persistence Layer (Database) to fulfill user requests.

---

## 1. User Registration

### Use Case Description
A new user creates an account on the HBnB platform by providing their personal information (first name, last name, email, and password). The system validates the data, ensures the email is unique, securely hashes the password, and stores the user information in the database.

### API Endpoint
```
POST /api/v1/users/register
```

### Request Body
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

### Sequence Diagram
```mermaid
sequenceDiagram
    actor User
    participant API as Presentation Layer<br/>(UserAPI)
    participant Facade as Business Logic Layer<br/>(BLFacade)
    participant UserModel as User Model
    participant DBFacade as Persistence Layer<br/>(DatabaseFacade)
    participant UserRepo as UserRepository
    participant DB as Database

    User->>API: POST /api/v1/users/register<br/>{first_name, last_name, email, password}
    
    Note over API: Receive registration request
    API->>API: Validate request format<br/>(required fields present)
    
    API->>Facade: register_user(user_data)
    
    Note over Facade: Coordinate registration process
    Facade->>UserModel: create_instance(user_data)
    
    Note over UserModel: Create User object
    UserModel->>UserModel: validate_email(email)
    UserModel->>UserModel: validate_password_strength(password)
    
    alt Validation Fails
        UserModel-->>Facade: ValidationError
        Facade-->>API: Error: Invalid data
        API-->>User: 400 Bad Request<br/>{error: "Invalid email or password"}
    end
    
    Facade->>DBFacade: check_email_exists(email)
    DBFacade->>UserRepo: find_by_email(email)
    UserRepo->>DB: SELECT * FROM users WHERE email = ?
    DB-->>UserRepo: Query result
    UserRepo-->>DBFacade: User or None
    
    alt Email Already Exists
        DBFacade-->>Facade: Email exists
        Facade-->>API: Error: Email taken
        API-->>User: 409 Conflict<br/>{error: "Email already registered"}
    end
    
    Note over UserModel: Email is unique, proceed
    UserModel->>UserModel: hash_password(password)
    
    Facade->>DBFacade: save_user(user_object)
    DBFacade->>UserRepo: save(user)
    UserRepo->>DB: INSERT INTO users VALUES (...)
    DB-->>UserRepo: Insert successful, user_id returned
    UserRepo-->>DBFacade: User saved successfully
    DBFacade-->>Facade: User object with ID
    
    Facade->>Facade: generate_auth_token(user)
    Facade-->>API: Success: User created + auth_token
    
    API->>API: Format response (exclude password_hash)
    API-->>User: 201 Created<br/>{id, first_name, last_name, email, token}
```

### Step-by-Step Flow

1. **User Submits Registration Request**
   - User sends POST request with personal information
   - Data includes: first_name, last_name, email, password

2. **Presentation Layer Validation**
   - UserAPI receives the request
   - Validates request format (all required fields present, proper JSON)
   - Checks basic structure before passing to business logic

3. **Business Logic Processing**
   - BLFacade coordinates the registration process
   - Creates a User model instance with provided data
   - User model validates email format (regex check)
   - User model validates password strength (min 8 chars, complexity)

4. **Email Uniqueness Check**
   - BLFacade requests email existence check from DatabaseFacade
   - DatabaseFacade delegates to UserRepository
   - UserRepository queries database for existing email
   - If email exists: returns 409 Conflict error
   - If email is unique: proceeds to next step

5. **Password Security**
   - User model hashes the password using bcrypt/argon2
   - Original password is discarded, only hash is kept
   - Hash is irreversible for security

6. **Data Persistence**
   - BLFacade requests user save operation
   - DatabaseFacade delegates to UserRepository
   - UserRepository executes INSERT SQL statement
   - Database confirms successful insertion and returns generated user ID
   - User object is updated with the ID

7. **Response Generation**
   - BLFacade generates authentication token for the new user
   - Returns success confirmation to API layer
   - API formats response (removes sensitive data like password_hash)
   - Returns 201 Created with user details and authentication token

### Success Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "created_at": "2025-01-25T14:30:00Z",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Possible Error Responses

**400 Bad Request** - Invalid data format
```json
{
  "error": "Invalid email format"
}
```

**409 Conflict** - Email already exists
```json
{
  "error": "Email already registered"
}
```

---

## 2. Place Creation

### Use Case Description
An authenticated user (property owner) creates a new property listing by providing details such as title, description, price, location coordinates, and amenities. The system validates the data, associates the place with the owner, links selected amenities, and stores the place in the database.

### API Endpoint
```
POST /api/v1/places
```

### Request Headers
```
Authorization: Bearer {token}
```

### Request Body
```json
{
  "title": "Cozy Beachfront Apartment",
  "description": "Beautiful 2-bedroom apartment with ocean views",
  "price": 150.00,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "amenity_ids": ["amenity-uuid-1", "amenity-uuid-2"]
}
```

### Sequence Diagram
```mermaid
sequenceDiagram
    actor Owner
    participant API as Presentation Layer<br/>(PlaceAPI)
    participant AuthMiddleware as Auth Middleware
    participant Facade as Business Logic Layer<br/>(BLFacade)
    participant PlaceModel as Place Model
    participant AmenityModel as Amenity Model
    participant DBFacade as Persistence Layer<br/>(DatabaseFacade)
    participant PlaceRepo as PlaceRepository
    participant AmenityRepo as AmenityRepository
    participant DB as Database

    Owner->>API: POST /api/v1/places<br/>Header: Authorization: Bearer {token}<br/>{title, description, price, coordinates, amenity_ids}
    
    Note over API: Receive place creation request
    API->>AuthMiddleware: verify_token(token)
    AuthMiddleware->>AuthMiddleware: Decode and validate JWT
    
    alt Invalid or Expired Token
        AuthMiddleware-->>API: Unauthorized
        API-->>Owner: 401 Unauthorized<br/>{error: "Invalid token"}
    end
    
    AuthMiddleware-->>API: Valid token, user_id extracted
    
    API->>Facade: create_place(place_data, user_id)
    
    Note over Facade: Coordinate place creation
    Facade->>DBFacade: get_user(user_id)
    DBFacade->>DB: SELECT user WHERE id = user_id
    DB-->>DBFacade: User object
    DBFacade-->>Facade: Owner object retrieved
    
    Facade->>PlaceModel: create_instance(place_data, owner)
    
    Note over PlaceModel: Create Place object
    PlaceModel->>PlaceModel: validate_coordinates(lat, lon)
    PlaceModel->>PlaceModel: validate_price(price)
    PlaceModel->>PlaceModel: validate_title_length()
    
    alt Validation Fails
        PlaceModel-->>Facade: ValidationError
        Facade-->>API: Error: Invalid data
        API-->>Owner: 400 Bad Request<br/>{error: "Invalid coordinates or price"}
    end
    
    Note over Facade: Validate and fetch amenities
    loop For each amenity_id
        Facade->>DBFacade: get_amenity(amenity_id)
        DBFacade->>AmenityRepo: find_by_id(amenity_id)
        AmenityRepo->>DB: SELECT * FROM amenities WHERE id = ?
        DB-->>AmenityRepo: Amenity data
        AmenityRepo-->>DBFacade: Amenity object
        DBFacade-->>Facade: Amenity object
        
        alt Amenity Not Found
            Facade-->>API: Error: Amenity not found
            API-->>Owner: 404 Not Found<br/>{error: "Amenity {id} not found"}
        end
        
        Facade->>PlaceModel: add_amenity(amenity)
    end
    
    Note over Facade: All validations passed, save place
    Facade->>DBFacade: save_place(place_object)
    DBFacade->>PlaceRepo: save(place)
    PlaceRepo->>DB: INSERT INTO places VALUES (...)
    DB-->>PlaceRepo: Place saved, place_id returned
    
    Note over PlaceRepo: Save place-amenity associations
    PlaceRepo->>DB: INSERT INTO place_amenities (place_id, amenity_id)
    DB-->>PlaceRepo: Associations saved
    
    PlaceRepo-->>DBFacade: Place saved successfully
    DBFacade-->>Facade: Place object with ID
    Facade-->>API: Success: Place created
    
    API->>API: Format response with amenity details
    API-->>Owner: 201 Created<br/>{place_id, title, price, amenities, ...}
```

### Step-by-Step Flow

1. **Owner Submits Place Creation Request**
   - Authenticated user sends POST request with place details
   - Includes authorization token in header
   - Provides title, description, price, coordinates, and amenity IDs

2. **Authentication**
   - API layer extracts token from Authorization header
   - AuthMiddleware verifies token validity
   - Decodes JWT to extract user_id
   - If token is invalid/expired: returns 401 Unauthorized
   - If valid: proceeds with user_id

3. **User Verification**
   - BLFacade retrieves user object using user_id
   - Confirms user exists and is active
   - This user becomes the place owner

4. **Place Model Creation**
   - Creates Place model instance with provided data
   - Associates owner (User object) with the place

5. **Data Validation**
   - Validates coordinates (latitude: -90 to +90, longitude: -180 to +180)
   - Validates price (must be positive number)
   - Validates title length (min 10, max 100 characters)
   - Validates description length (min 20 characters)
   - If any validation fails: returns 400 Bad Request

6. **Amenity Processing**
   - For each amenity_id in the request:
     - Queries database to fetch amenity object
     - If amenity doesn't exist: returns 404 Not Found
     - If amenity exists: adds to place's amenity list
   - Creates many-to-many relationship between place and amenities

7. **Data Persistence**
   - DatabaseFacade delegates to PlaceRepository
   - PlaceRepository executes INSERT for place data
   - Database returns generated place_id
   - PlaceRepository inserts records in place_amenities join table
   - Links place with all selected amenities

8. **Response Generation**
   - BLFacade confirms successful creation
   - API formats response including full amenity details
   - Returns 201 Created with complete place information

### Success Response (201 Created)
```json
{
  "id": "place-uuid-123",
  "title": "Cozy Beachfront Apartment",
  "description": "Beautiful 2-bedroom apartment with ocean views",
  "price": 150.00,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "owner": {
    "id": "owner-uuid-456",
    "first_name": "John",
    "last_name": "Doe"
  },
  "amenities": [
    {
      "id": "amenity-uuid-1",
      "name": "WiFi"
    },
    {
      "id": "amenity-uuid-2",
      "name": "Parking"
    }
  ],
  "created_at": "2025-01-25T15:00:00Z"
}
```

### Possible Error Responses

**401 Unauthorized** - Invalid/missing token
```json
{
  "error": "Invalid or expired authentication token"
}
```

**400 Bad Request** - Invalid data
```json
{
  "error": "Invalid coordinates: latitude must be between -90 and 90"
}
```

**404 Not Found** - Amenity doesn't exist
```json
{
  "error": "Amenity with ID 'amenity-uuid-1' not found"
}
```

---

## 3. Review Submission

### Use Case Description
An authenticated user submits a review for a place they have visited. The review includes a numerical rating (1-5) and written feedback. The system validates that the user is not the place owner, hasn't already reviewed this place, and that the rating is within the valid range before storing the review.

### API Endpoint
```
POST /api/v1/reviews
```

### Request Headers
```
Authorization: Bearer {token}
```

### Request Body
```json
{
  "place_id": "place-uuid-123",
  "rating": 5,
  "comment": "Amazing place with stunning views! Host was very responsive and accommodating."
}
```

### Sequence Diagram
```mermaid
sequenceDiagram
    actor Guest
    participant API as Presentation Layer<br/>(ReviewAPI)
    participant AuthMiddleware as Auth Middleware
    participant Facade as Business Logic Layer<br/>(BLFacade)
    participant ReviewModel as Review Model
    participant PlaceModel as Place Model
    participant DBFacade as Persistence Layer<br/>(DatabaseFacade)
    participant ReviewRepo as ReviewRepository
    participant PlaceRepo as PlaceRepository
    participant DB as Database

    Guest->>API: POST /api/v1/reviews<br/>Header: Authorization: Bearer {token}<br/>{place_id, rating, comment}
    
    Note over API: Receive review submission
    API->>AuthMiddleware: verify_token(token)
    AuthMiddleware->>AuthMiddleware: Validate JWT
    
    alt Invalid Token
        AuthMiddleware-->>API: Unauthorized
        API-->>Guest: 401 Unauthorized
    end
    
    AuthMiddleware-->>API: Valid token, user_id extracted
    
    API->>Facade: create_review(review_data, user_id)
    
    Note over Facade: Coordinate review creation
    Facade->>DBFacade: get_place(place_id)
    DBFacade->>PlaceRepo: find_by_id(place_id)
    PlaceRepo->>DB: SELECT * FROM places WHERE id = ?
    DB-->>PlaceRepo: Place data
    PlaceRepo-->>DBFacade: Place object
    
    alt Place Not Found
        DBFacade-->>Facade: None
        Facade-->>API: Error: Place not found
        API-->>Guest: 404 Not Found<br/>{error: "Place does not exist"}
    end
    
    DBFacade-->>Facade: Place object
    
    Note over Facade: Check business rules
    Facade->>PlaceModel: is_owned_by(user_id)
    PlaceModel-->>Facade: Boolean result
    
    alt User is Place Owner
        Facade-->>API: Error: Cannot review own place
        API-->>Guest: 403 Forbidden<br/>{error: "You cannot review your own place"}
    end
    
    Facade->>DBFacade: check_existing_review(user_id, place_id)
    DBFacade->>ReviewRepo: find_by_user_and_place(user_id, place_id)
    ReviewRepo->>DB: SELECT * FROM reviews<br/>WHERE user_id = ? AND place_id = ?
    DB-->>ReviewRepo: Query result
    ReviewRepo-->>DBFacade: Review or None
    
    alt Review Already Exists
        DBFacade-->>Facade: Existing review found
        Facade-->>API: Error: Already reviewed
        API-->>Guest: 409 Conflict<br/>{error: "You have already reviewed this place"}
    end
    
    Note over Facade: Create and validate review
    Facade->>ReviewModel: create_instance(rating, comment, user, place)
    ReviewModel->>ReviewModel: validate_rating(rating)
    ReviewModel->>ReviewModel: validate_comment(comment)
    
    alt Validation Fails
        ReviewModel-->>Facade: ValidationError
        Facade-->>API: Error: Invalid data
        API-->>Guest: 400 Bad Request<br/>{error: "Rating must be between 1 and 5"}
    end
    
    Note over Facade: Save review
    Facade->>DBFacade: save_review(review_object)
    DBFacade->>ReviewRepo: save(review)
    ReviewRepo->>DB: INSERT INTO reviews VALUES (...)
    DB-->>ReviewRepo: Review saved, review_id returned
    ReviewRepo-->>DBFacade: Review object with ID
    
    Note over Facade: Update place's average rating
    Facade->>PlaceModel: calculate_average_rating()
    PlaceModel->>DBFacade: get_all_reviews(place_id)
    DBFacade->>ReviewRepo: find_by_place(place_id)
    ReviewRepo->>DB: SELECT rating FROM reviews WHERE place_id = ?
    DB-->>ReviewRepo: All ratings
    ReviewRepo-->>DBFacade: List of ratings
    DBFacade-->>PlaceModel: Ratings list
    PlaceModel->>PlaceModel: Calculate average
    PlaceModel->>DBFacade: update_place_rating(place_id, avg_rating)
    DBFacade->>PlaceRepo: update(place)
    PlaceRepo->>DB: UPDATE places SET avg_rating = ? WHERE id = ?
    DB-->>PlaceRepo: Update successful
    
    DBFacade-->>Facade: Review saved and rating updated
    Facade-->>API: Success: Review created
    
    API->>API: Format response with user and place details
    API-->>Guest: 201 Created<br/>{review_id, rating, comment, place, user}
```

### Step-by-Step Flow

1. **Guest Submits Review**
   - Authenticated user sends POST request with review data
   - Includes authorization token in header
   - Provides place_id, rating (1-5), and comment

2. **Authentication**
   - API extracts and verifies token
   - AuthMiddleware validates JWT
   - Extracts user_id from token
   - If invalid: returns 401 Unauthorized

3. **Place Existence Check**
   - BLFacade queries database for place using place_id
   - If place doesn't exist: returns 404 Not Found
   - If exists: retrieves place object with owner information

4. **Ownership Validation**
   - Checks if user_id matches place.owner_id
   - **Business Rule**: Users cannot review their own places
   - If user is owner: returns 403 Forbidden

5. **Duplicate Review Check**
   - Queries database for existing review by this user for this place
   - **Business Rule**: Each user can only review a place once
   - If review exists: returns 409 Conflict

6. **Review Validation**
   - Creates Review model instance
   - Validates rating is integer between 1 and 5
   - Validates comment length (min 10 chars, max 500 chars)
   - If validation fails: returns 400 Bad Request

7. **Review Persistence**
   - DatabaseFacade delegates to ReviewRepository
   - ReviewRepository executes INSERT statement
   - Database returns generated review_id
   - Review object is updated with ID

8. **Average Rating Update**
   - Place model calculates new average rating
   - Fetches all reviews for this place
   - Computes average of all ratings
   - Updates place record with new average rating
   - This keeps place ratings current for searches/sorting

9. **Response Generation**
   - API formats response with review details
   - Includes user information (reviewer name)
   - Includes place information (place title)
   - Returns 201 Created with complete review data

### Success Response (201 Created)
```json
{
  "id": "review-uuid-789",
  "rating": 5,
  "comment": "Amazing place with stunning views! Host was very responsive and accommodating.",
  "user": {
    "id": "user-uuid-456",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "place": {
    "id": "place-uuid-123",
    "title": "Cozy Beachfront Apartment"
  },
  "created_at": "2025-01-25T16:00:00Z"
}
```

### Possible Error Responses

**401 Unauthorized** - Invalid token
```json
{
  "error": "Invalid or expired authentication token"
}
```

**403 Forbidden** - Reviewing own place
```json
{
  "error": "You cannot review your own place"
}
```

**404 Not Found** - Place doesn't exist
```json
{
  "error": "Place with ID 'place-uuid-123' does not exist"
}
```

**409 Conflict** - Duplicate review
```json
{
  "error": "You have already reviewed this place"
}
```

**400 Bad Request** - Invalid rating
```json
{
  "error": "Rating must be between 1 and 5"
}
```

---

## 4. Fetching a List of Places

### Use Case Description
A user (authenticated or guest) requests a list of available places based on optional filtering criteria such as location, price range, amenities, and minimum rating. The system queries the database, applies filters, and returns a paginated list of places matching the criteria.

### API Endpoint
```
GET /api/v1/places?latitude=40.7128&longitude=-74.0060&max_distance=10&min_price=50&max_price=200&amenities=wifi,parking&min_rating=4&page=1&limit=20
```

### Query Parameters
- `latitude` (optional): Center point latitude for location-based search
- `longitude` (optional): Center point longitude for location-based search
- `max_distance` (optional): Maximum distance in km from center point
- `min_price` (optional): Minimum nightly price
- `max_price` (optional): Maximum nightly price
- `amenities` (optional): Comma-separated list of required amenities
- `min_rating` (optional): Minimum average rating (1-5)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)

### Sequence Diagram
```mermaid
sequenceDiagram
    actor User
    participant API as Presentation Layer<br/>(PlaceAPI)
    participant Facade as Business Logic Layer<br/>(BLFacade)
    participant PlaceModel as Place Model
    participant DBFacade as Persistence Layer<br/>(DatabaseFacade)
    participant PlaceRepo as PlaceRepository
    participant DB as Database

    User->>API: GET /api/v1/places?filters&page=1&limit=20
    
    Note over API: Receive places list request
    API->>API: Parse and validate query parameters
    API->>API: Build filter criteria object
    
    alt Invalid Parameters
        API-->>User: 400 Bad Request<br/>{error: "Invalid parameter values"}
    end
    
    API->>Facade: get_places(filters, page, limit)
    
    Note over Facade: Coordinate query building
    Facade->>Facade: Validate filter values
    Facade->>Facade: Build query criteria
    
    alt Location-based Search
        Note over Facade: Calculate distance from coordinates
        Facade->>PlaceModel: calculate_distance_bounds(lat, lon, max_distance)
        PlaceModel-->>Facade: Latitude/Longitude ranges
    end
    
    Note over Facade: Query database with filters
    Facade->>DBFacade: find_places(criteria, pagination)
    DBFacade->>PlaceRepo: query_with_filters(criteria, page, limit)
    
    Note over PlaceRepo: Build complex SQL query
    PlaceRepo->>PlaceRepo: Build SELECT with JOINs<br/>(places, amenities, reviews)
    PlaceRepo->>PlaceRepo: Apply WHERE clauses (price, rating, location)
    PlaceRepo->>PlaceRepo: Apply GROUP BY and HAVING
    PlaceRepo->>PlaceRepo: Apply ORDER BY (rating, price)
    PlaceRepo->>PlaceRepo: Apply LIMIT and OFFSET for pagination
    
    PlaceRepo->>DB: Execute complex query<br/>SELECT places.*, AVG(reviews.rating)<br/>FROM places<br/>LEFT JOIN reviews ON places.id = reviews.place_id<br/>INNER JOIN place_amenities ON places.id = place_amenities.place_id<br/>WHERE ... GROUP BY ... ORDER BY ... LIMIT ...
    
    DB-->>PlaceRepo: Result set (places data)
    
    Note over PlaceRepo: Also get total count for pagination
    PlaceRepo->>DB: SELECT COUNT(*) FROM places WHERE ...
    DB-->>PlaceRepo: Total count
    
    PlaceRepo-->>DBFacade: List of Place objects + total count
    
    Note over Facade: Enrich place data
    loop For each place
        Facade->>DBFacade: get_place_amenities(place_id)
        DBFacade->>DB: SELECT amenities WHERE place_id = ?
        DB-->>DBFacade: Amenity list
        Facade->>PlaceModel: add_amenities(amenities)
        
        Facade->>DBFacade: get_place_owner(owner_id)
        DBFacade->>DB: SELECT user WHERE id = owner_id
        DB-->>DBFacade: Owner data
        Facade->>PlaceModel: set_owner(owner)
    end
    
    Note over Facade: Calculate pagination metadata
    Facade->>Facade: Calculate total_pages = total_count / limit
    Facade->>Facade: Build pagination object
    
    DBFacade-->>Facade: Enriched places list + metadata
    Facade-->>API: Places list + pagination data
    
    API->>API: Format response with pagination
    API->>API: Remove sensitive data (owner passwords, etc.)
    API-->>User: 200 OK<br/>{places: [...], pagination: {...}}
```

### Step-by-Step Flow

1. **User Requests Place List**
   - User sends GET request with optional filter parameters
   - No authentication required (public search)
   - Query parameters define search criteria

2. **Parameter Validation**
   - API parses all query parameters
   - Validates data types (numbers, coordinates, etc.)
   - Validates value ranges (prices > 0, rating 1-5, coordinates valid)
   - If invalid parameters: returns 400 Bad Request
   - Builds structured filter criteria object

3. **Filter Criteria Building**
   - BLFacade receives validated filters
   - Organizes filters by type:
     - Location filters (latitude, longitude, distance)
     - Price filters (min_price, max_price)
     - Amenity filters (required amenities)
     - Rating filter (min_rating)
   - Determines query complexity

4. **Location-Based Search** (if coordinates provided)
   - Calculates geographic boundaries
   - Uses Haversine formula for distance calculation
   - Determines latitude/longitude ranges within max_distance
   - Creates bounding box for efficient querying

5. **Database Query Construction**
   - PlaceRepository builds complex SQL query
   - **JOINs**:
     - LEFT JOIN with reviews (to calculate average rating)
     - INNER JOIN with place_amenities (to filter by amenities)
     - LEFT JOIN with users (to get owner information)
   - **WHERE clauses**:
     - Price range: `price BETWEEN min_price AND max_price`
     - Location: `latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?`
     - Amenities: `place_id IN (SELECT place_id WHERE amenity_id IN (...))`
   - **GROUP BY**: Groups by place_id to aggregate reviews
   - **HAVING**: Filters by average rating: `AVG(rating) >= min_rating`
   - **ORDER BY**: Sorts by rating (DESC) then price (ASC)
   - **LIMIT/OFFSET**: Implements pagination

6. **Query Execution**
   - Database executes the complex query
   - Returns matching places with aggregated data
   - Separate query gets total count (for pagination metadata)

7. **Data Enrichment**
   - For each place in results:
     - Fetches full amenity details (names, descriptions)
     - Fetches owner information (name, contact)
     - Calculates average rating from all reviews
     - Assembles complete place object

8. **Pagination Metadata**
   - Calculates total pages: `total_count / limit` (rounded up)
   - Builds pagination object with:
     - Current page
     - Total pages
     - Total results
     - Results per page
     - Has next/previous page flags

9. **Response Formatting**
   - API removes sensitive data (password hashes, etc.)
   - Formats each place with owner and amenity details
   - Includes pagination metadata
   - Returns 200 OK with complete data

### Success Response (200 OK)
```json
{
  "places": [
    {
      "id": "place-uuid-123",
      "title": "Cozy Beachfront Apartment",
      "description": "Beautiful 2-bedroom apartment with ocean views",
      "price": 150.00,
      "latitude": 40.7128,
      "longitude": -74.0060,
      "owner": {
        "id": "owner-uuid-456",
        "first_name": "John",
        "last_name": "Doe"
      },
      "amenities": [
        {
          "id": "amenity-uuid-1",
          "name": "WiFi"
        },
        {
          "id": "amenity-uuid-2",
          "name": "Parking"
        }
      ],
      "average_rating": 4.8,
      "review_count": 24,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": "place-uuid-124",
      "title": "Modern Downtown Loft",
      "description": "Stylish loft in the heart of the city",
      "price": 180.00,
      "latitude": 40.7589,
      "longitude": -73.9851,
      "owner": {
        "id": "owner-uuid-457",
        "first_name": "Sarah",
        "last_name": "Johnson"
      },
      "amenities": [
        {
          "id": "amenity-uuid-1",
          "name": "WiFi"
        },
        {
          "id": "amenity
