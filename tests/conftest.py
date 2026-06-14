"""
Test configuration.

Sets safe default environment variables BEFORE the application settings are
imported, so unit tests run without a real .env / database / API keys.
"""

import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("GROQ_API_KEY", "")
