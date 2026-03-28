from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

# SQLite file will be created at project root as symptom_checker.db
DATABASE_URL = "sqlite:///./symptom_checker.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Database Table

class SymptomQuery(Base):
    __tablename__ = "symptom_queries"

    id            = Column(Integer, primary_key=True, index=True)
    symptoms      = Column(Text, nullable=False)
    conditions    = Column(Text, nullable=False)   # stored as JSON string
    recommended_steps = Column(Text, nullable=False)  # stored as JSON string
    urgency_level = Column(String(50), nullable=False)
    disclaimer    = Column(Text, nullable=False)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def create_tables():
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency injected into FastAPI routes.
    Yields a DB session and ensures it's closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()