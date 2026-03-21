from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./myai.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)  # Telegram/Discord user ID
    api_key = Column(String, unique=True, index=True, nullable=True)
    plan = Column(String, default="free")  # free, basic, vip
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Usage(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    tool_name = Column(String)  # imagegen, imageedit, songgen
    date = Column(String)  # YYYY-MM-DD format for easy querying
    count = Column(Integer, default=0)
    
    __table_args__ = (
        # Unique constraint for user+tool+date
        {'sqlite_autoincrement': True}
    )

class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    tool_type = Column(String)  # image or song
    prompt = Column(Text)
    file_path = Column(String)
    file_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize DB
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()