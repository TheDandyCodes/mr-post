"""
Database models for user management and preferences
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import os

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    writing_style = Column(String, default="professional")  # professional, casual, creative, etc.
    tone = Column(String, default="neutral")  # formal, friendly, humorous, etc.
    target_audience = Column(String, default="general")
    post_length = Column(String, default="medium")  # short, medium, long
    topics_of_interest = Column(Text)  # JSON string of topics
    ai_creativity_level = Column(String, default="balanced")  # conservative, balanced, creative
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    original_idea = Column(Text)  # User's original idea/prompt
    writer_output = Column(Text)  # Output from writer agent
    reviewer_feedback = Column(Text)  # Feedback from reviewer agent
    final_content = Column(Text)  # Final reviewed content
    status = Column(String, default="draft")  # draft, reviewing, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mr_post.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()