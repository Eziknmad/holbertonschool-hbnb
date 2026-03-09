erDiagram
    USER {
        char id PK
        varchar first_name
        varchar last_name
        varchar email
        varchar password
        boolean is_admin
        datetime created_at
        datetime updated_at
    }

    PLACE {
        char id PK
        varchar title
        text description
        decimal price
        float latitude
        float longitude
        char owner_id FK
        datetime created_at
        datetime updated_at
    }

    REVIEW {
        char id PK
        text text
        int rating
        char user_id FK
        char place_id FK
        datetime created_at
        datetime updated_at
    }

    AMENITY {
        char id PK
        varchar name
        datetime created_at
        datetime updated_at
    }

    PLACE_AMENITY {
        char place_id FK
        char amenity_id FK
    }

    USER ||--o{ REVIEW : "writes"
    USER ||--o{ PLACE : "owns"
    PLACE ||--o{ REVIEW : "receives"
    PLACE ||--o{ PLACE_AMENITY : "has"
    AMENITY ||--o{ PLACE_AMENITY : "available_in"
