-- =============================================================
-- HBnB Initial Data
-- Admin user and default amenities
-- =============================================================

-- Administrator user (fixed UUID as required by the task)
INSERT INTO User (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$m8T86AnFXB5XFYvmxnHRHeDl8MpQPKild4UNu/Z5JBcLYymPvWz8q',
    TRUE
);

-- Initial amenities (random UUID4 for each)
INSERT INTO Amenity (id, name) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'WiFi'),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Swimming Pool'),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'Air Conditioning');
