# HBnB Evolution - Part 3: Database Integration

## Overview

Part 3 of the HBnB Evolution project introduces persistent storage using
SQLAlchemy ORM and SQLite, JWT authentication, and role-based access control
(RBAC). This builds on Part 2's in-memory implementation by replacing it with
a real relational database.

---

## Project Structure
```
part3/
├── app/
│   ├── __init__.py                  # App factory, SQLAlchemy + JWT setup
│   ├── api/v1/
│   │   ├── auth.py                  # JWT login endpoint
│   │   ├── users.py                 # User CRUD + admin RBAC
│   │   ├── places.py                # Place CRUD + ownership checks
│   │   ├── reviews.py               # Review CRUD + authorship checks
│   │   └── amenities.py             # Amenity CRUD + admin RBAC
│   ├── models/
│   │   ├── base_model.py            # SQLAlchemy base with UUID + timestamps
│   │   ├── user.py                  # User model + bcrypt password hashing
│   │   ├── place.py                 # Place model + owner FK + amenities M2M
│   │   ├── review.py                # Review model + user/place FKs
│   │   └── amenity.py               # Amenity model + place_amenity table
│   ├── persistence/
│   │   └── repository.py            # SQLAlchemyRepository + InMemoryRepository
│   └── services/
│       ├── facade.py                # Business logic layer
│       └── repositories/
│           └── user_repository.py   # UserRepository with get_by_email
├── scripts/
│   ├── create_tables.sql            # Raw SQL schema creation
│   └── initial_data.sql             # Admin user + default amenities seed
├── docs/
│   └── er_diagram.md                # Mermaid.js ER diagram
├── instance/
│   └── development.db               # SQLite database (auto-generated)
├── config.py                        # Flask + SQLAlchemy configuration
├── run.py                           # Application entry point
└── requirements.txt                 # Python dependencies
```

---

## Features

- **SQLAlchemy ORM** — All entities mapped to SQLite with proper foreign keys
  and relationships
- **JWT Authentication** — Login returns a signed token; protected endpoints
  require `Authorization: Bearer <token>`
- **Role-Based Access Control** — Admin users bypass ownership checks and can
  manage all resources
- **Persistent Storage** — Data survives server restarts via SQLite
- **Relationship Mapping** — One-to-many and many-to-many relationships
  between User, Place, Review, and Amenity

---

## Database Relationships

| Relationship | Type |
|---|---|
| User → Place | One-to-many (a user owns many places) |
| User → Review | One-to-many (a user writes many reviews) |
| Place → Review | One-to-many (a place receives many reviews) |
| Place ↔ Amenity | Many-to-many via `place_amenity` table |

See `docs/er_diagram.md` for the full ER diagram.

---

## Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()

# Seed admin user
flask shell
>>> from app.services.facade import facade
>>> facade.create_user({
...     'first_name': 'Admin',
...     'last_name': 'HBnB',
...     'email': 'admin@hbnb.io',
...     'password': 'admin1234',
...     'is_admin': True
... })
>>> exit()

# Run the server
python run.py
```

API available at: `http://127.0.0.1:5000`
Swagger UI: `http://127.0.0.1:5000/api/v1/docs`

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Login and receive JWT token |

### Users
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/users/` | Public | List all users |
| GET | `/api/v1/users/<id>` | Public | Get user by ID |
| POST | `/api/v1/users/` | Admin | Create user |
| PUT | `/api/v1/users/<id>` | Owner/Admin | Update user |

### Places
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/places/` | Public | List all places |
| GET | `/api/v1/places/<id>` | Public | Get place by ID |
| POST | `/api/v1/places/` | JWT | Create place |
| PUT | `/api/v1/places/<id>` | Owner/Admin | Update place |

### Reviews
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/reviews/` | Public | List all reviews |
| GET | `/api/v1/reviews/<id>` | Public | Get review by ID |
| GET | `/api/v1/places/<id>/reviews` | Public | Reviews for a place |
| POST | `/api/v1/reviews/` | JWT | Create review |
| PUT | `/api/v1/reviews/<id>` | Author/Admin | Update review |
| DELETE | `/api/v1/reviews/<id>` | Author/Admin | Delete review |

### Amenities
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/amenities/` | Public | List all amenities |
| GET | `/api/v1/amenities/<id>` | Public | Get amenity by ID |
| POST | `/api/v1/amenities/` | Admin | Create amenity |
| PUT | `/api/v1/amenities/<id>` | Admin | Update amenity |

---

## SQL Scripts

To recreate the schema from scratch using raw SQL:
```bash
sqlite3 my_database.db < scripts/create_tables.sql
sqlite3 my_database.db < scripts/initial_data.sql
```

---

## Authors

Kevin Galarza — HBnB Evolution Project
