# This file handles connecting to the PostgreSQL database
# Manages connections to both production (read-only) and aggregation (local) databases

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
load_dotenv()


# PRODUCTION DATABASE (Read-Only) - Remote server with raw sensor data

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")

PROD_DATABASE_URL = f'postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

prod_engine = create_engine(
    PROD_DATABASE_URL,
    pool_size=10,          # Number of persistent connections in the pool
    max_overflow=20,       # Additional temporary connections allowed
    pool_pre_ping=True,    # Check connections before use
    pool_recycle=1800      # Recycle connections every 30 minutes
)

ProductionSession = sessionmaker(autocommit=False, autoflush=False, bind=prod_engine)


def get_prod_db():
    """Dependency for FastAPI endpoints that read from production database"""
    db = ProductionSession()
    try:
        yield db
    finally:
        db.close()


# AGGREGATION DATABASE - Stores pre-computed results

agg_db_user = os.getenv("DB_USER") # Add second parameter for defaults
agg_db_password = os.getenv("DB_PASSWORD") 
agg_db_host = os.getenv("DB_HOST")
agg_db_name = os.getenv("AGG_DB_NAME")
agg_db_port = os.getenv("DB_PORT")

AGG_DATABASE_URL = f'postgresql+psycopg://{agg_db_user}:{agg_db_password}@{agg_db_host}:{agg_db_port}/{agg_db_name}'

agg_engine = create_engine(
    AGG_DATABASE_URL,
    pool_size=5,           # Smaller pool for local DB
    max_overflow=10,
    pool_pre_ping=True
)

AggregationSession = sessionmaker(autocommit=False, autoflush=False, bind=agg_engine)


def get_agg_db():
    """Dependency for FastAPI endpoints that read from aggregation database"""
    db = AggregationSession()
    try:
        yield db
    finally:
        db.close()