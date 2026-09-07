import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

# Load environment variables from the .env file
load_dotenv()

# Create a SQLAlchemy engine db url from the .env file
engine = create_engine(
    os.getenv("DB_URL"), 
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()