import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# -------------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------------

# Load database URL from environment or fallback
# Example for MySQL:
# export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/nirix"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for development (change as needed)
    DATABASE_URL = "mysql+pymysql://nirix_user:journey%40123%21@127.0.0.1:3306/nirix_diagnostics"

# Create SQLAlchemy engine
# Pool settings prevent dropped MySQL connections causing crashes.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,            # Detect dead MySQL connections
    pool_recycle=3600,             # Recycle connections every hour
    pool_size=10,                  # Max DB connections
    max_overflow=20,               # Can spike during load
    echo=False                     # Set True only for SQL debugging
)

# Thread-safe session
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# Base class for all ORM models
Base = declarative_base()
Base.query = db_session.query_property()

# -------------------------------------------------------------------
# Database initialization
# -------------------------------------------------------------------

def init_db():
    """Create all tables (ONLY if they do not exist)."""
    import app.models  # This loads all models so SQLAlchemy knows them

    try:
        Base.metadata.create_all(bind=engine)
        print("[DB] Tables created or already exist.")
    except OperationalError as e:
        print("[DB] ERROR: Could not create tables.")
        print(e)

# -------------------------------------------------------------------
# Cleanup (used by Flask app teardown)
# -------------------------------------------------------------------

def shutdown_session(exception=None):
    """Ensure DB sessions are cleaned after each request."""
    db_session.remove()
