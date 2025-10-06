# This file handles connecting to the PostgreSQL database

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build the database URL from environment variables
# Format: postgresql://username:password@host/database_name
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

# Create the engine - this is the connection to PostgreSQL
# echo=True means it will print SQL queries to console (helpful for learning!)
engine = create_engine(DATABASE_URL, echo=True)

# Create a session maker - used to create database sessions
# Think of a session as a "conversation" with the database
SessionLocal = sessionmaker(bind=engine)


# Function to get a database session
# We'll use this in our API endpoints
def get_db():
    """
    Creates a database session, uses it, then closes it.
    This is a "dependency" that FastAPI will call for us.
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to whoever needs it
    finally:
        db.close()  # Always close the connection when done


# Test function - let's verify the connection works
def test_connection():
    """Test if we can connect to the database"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Run a test when this file is executed directly
if __name__ == "__main__":
    test_connection()

