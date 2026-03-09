-- =============================================================
-- HBnB Database Schema
-- Creates all tables with constraints and relationships
-- =============================================================

-- User table
CREATE TABLE IF NOT EXISTS User (
    id          CHAR(36)        PRIMARY KEY,
    first_name  VARCHAR(255)    NOT NULL,
    last_name   VARCHAR(255)    NOT NULL,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    password    VARCHAR(255)    NOT NULL,
    is_admin    BOOLEAN         DEFAULT FALSE,
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- Place table
CREATE TABLE IF NOT EXISTS Place (
    id          CHAR(36)        PRIMARY KEY,
    title       VARCHAR(255)    NOT NULL,
    description TEXT,
    price       DECIMAL(10, 2)  NOT NULL,
    latitude    FLOAT           NOT NULL,
    longitude   FLOAT           NOT NULL,
    owner_id    CHAR(36)        NOT NULL,
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES User(id)
);

-- Review table
CREATE TABLE IF NOT EXISTS Review (
    id          CHAR(36)        PRIMARY KEY,
    text        TEXT            NOT NULL,
    rating      INT             NOT NULL CHECK (rating BETWEEN 1 AND 5),
    user_id     CHAR(36)        NOT NULL,
    place_id    CHAR(36)        NOT NULL,
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES User(id),
    FOREIGN KEY (place_id) REFERENCES Place(id),
    UNIQUE (user_id, place_id)
);

-- Amenity table
CREATE TABLE IF NOT EXISTS Amenity (
    id          CHAR(36)        PRIMARY KEY,
    name        VARCHAR(255)    NOT NULL UNIQUE,
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- Place_Amenity association table (many-to-many)
CREATE TABLE IF NOT EXISTS Place_Amenity (
    place_id    CHAR(36)        NOT NULL,
    amenity_id  CHAR(36)        NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id)   REFERENCES Place(id),
    FOREIGN KEY (amenity_id) REFERENCES Amenity(id)
);
