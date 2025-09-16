# Configuration file for Career Advisor
import os

# Database Configuration (Optional - will use JSON fallback if not available)
DB_NAME = os.getenv("DB_NAME", "career_advisor")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# API Keys - You can set these as environment variables or replace directly
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBvOkBwL7iMx9zF8nE3qR2sT5uY7wX1cV4")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "career_advisor_2024")

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
