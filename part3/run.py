#!/usr/bin/env python3
"""
Entry point for the HBnB application.
Starts the Flask development server.
"""
import os
from app import create_app

# Get configuration from environment variable, default to development
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    # Host 0.0.0.0 makes it accessible from other machines
    # Port 5000 is the default Flask port
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
