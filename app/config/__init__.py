"""
Configuration Package.

This package is responsible for managing application configurations,
such as database connection details, secret keys, and other
environment-specific settings. Configurations are typically loaded
from environment variables or .env files using Pydantic's settings management.

Modules:
- db.py: Handles database configuration (e.g., MongoDB URI, database name).
- log.py: Configures logging for the application.
- secret.py: Manages secret keys used for security purposes (e.g., API key signing).
"""
