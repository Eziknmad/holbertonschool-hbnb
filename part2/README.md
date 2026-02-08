# HBnB Evolution - Part 2

## Project Overview

This is Part 2 of the HBnB Evolution project, focusing on implementing the Business Logic and API layers using Flask and flask-restx.

## Project Structure
```
part2/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py   # API v1 namespace
│   │       ├── users.py      # User endpoints
│   │       ├── places.py     # Place endpoints
│   │       ├── reviews.py    # Review endpoints
│   │       └── amenities.py  # Amenity endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py     # Base model for all entities
│   │   ├── user.py           # User model
│   │   ├── place.py          # Place model
│   │   ├── review.py         # Review model
│   │   └── amenity.py        # Amenity model
│   ├── services/
│   │   ├── __init__.py
│   │   └── facade.py         # Facade pattern implementation
│   └── persistence/
│       ├── __init__.py
│       └── repository.py     # In-memory repository
├── run.py                    # Application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```

Or using Flask CLI:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

### 4. Access the Application

- **API Base URL**: http://localhost:5000/api/v1
- **API Documentation**: http://localhost:5000/api/docs

## API Endpoints

### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Places
- `POST /api/v1/places/` - Create a new place
- `GET /api/v1/places/` - Get all places
- `GET /api/v1/places/{id}` - Get place by ID
- `PUT /api/v1/places/{id}` - Update place
- `DELETE /api/v1/places/{id}` - Delete place

### Reviews
- `POST /api/v1/reviews/` - Create a new review
- `GET /api/v1/reviews/` - Get all reviews
- `GET /api/v1/reviews/{id}` - Get review by ID
- `PUT /api/v1/reviews/{id}` - Update review
- `DELETE /api/v1/reviews/{id}` - Delete review

### Amenities
- `POST /api/v1/amenities/` - Create a new amenity
- `GET /api/v1/amenities/` - Get all amenities
- `GET /api/v1/amenities/{id}` - Get amenity by ID
- `PUT /api/v1/amenities/{id}` - Update amenity
- `DELETE /api/v1/amenities/{id}` - Delete amenity

## Testing

### Using cURL
```bash
# Create a user
curl -X POST http://localhost:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "secure123"
  }'

# Get all users
curl -X GET http://localhost:5000/api/v1/users/
```

### Using Postman

1. Import the API from: http://localhost:5000/api/docs (Swagger documentation)
2. Create requests for each endpoint
3. Test CRUD operations

## Architecture

### Layered Architecture

The application follows a three-layer architecture:

1. **Presentation Layer** (`app/api/`): RESTful API endpoints
2. **Business Logic Layer** (`app/models/`, `app/services/`): Core business logic and models
3. **Persistence Layer** (`app/persistence/`): Data storage (in-memory for Part 2)

### Facade Pattern

The `HBnBFacade` class (`app/services/facade.py`) provides a simplified interface for communication between the Presentation and Business Logic layers.

## Development

### Adding a New Model

1. Create model file in `app/models/`
2. Inherit from `BaseModel`
3. Implement required methods
4. Add to `app/models/__init__.py`

### Adding New Endpoints

1. Create endpoint file in `app/api/v1/`
2. Define Resource classes
3. Register with API namespace
4. Import in `app/api/v1/__init__.py`

## Next Steps (Part 3)

- Implement JWT authentication
- Add role-based access control
- Replace in-memory repository with database (SQLAlchemy)
- Add database migrations

## Notes

- **In-Memory Storage**: Data is lost when the server restarts
- **No Authentication**: All endpoints are currently public
- **Validation**: Basic validation is implemented in models

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit: `git commit -m "Description"`
3. Push to GitHub: `git push origin feature/name`
4. Create pull request

## License

Educational project for Holberton School.
