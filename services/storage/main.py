"""
Storage microservice API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
import json
from typing import Optional, List

from .models import init_db, get_db, User, UserPreferences, UserSession, Post

# Initialize database on startup
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Mr. Post Storage Service", version="1.0.0", lifespan=lifespan)

# Security
security = HTTPBearer()
import hashlib

def get_password_hash(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """Simple password verification for demo purposes"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PreferencesCreate(BaseModel):
    writing_style: str = "professional"
    tone: str = "neutral"
    target_audience: str = "general"
    post_length: str = "medium"
    topics_of_interest: List[str] = []
    ai_creativity_level: str = "balanced"

class PreferencesResponse(BaseModel):
    id: int
    user_id: int
    writing_style: str
    tone: str
    target_audience: str
    post_length: str
    topics_of_interest: str
    ai_creativity_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    original_idea: str

class PostUpdate(BaseModel):
    writer_output: Optional[str] = None
    reviewer_feedback: Optional[str] = None
    final_content: Optional[str] = None
    status: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    original_idea: Optional[str]
    writer_output: Optional[str]
    reviewer_feedback: Optional[str]
    final_content: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic models

def create_session_token():
    return secrets.token_urlsafe(32)

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default preferences
    preferences = UserPreferences(user_id=user.id)
    db.add(preferences)
    db.commit()
    
    return user

@app.post("/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session
    token = create_session_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    session = UserSession(
        user_id=user.id,
        session_token=token,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": UserResponse.from_orm(user)
    }

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_user_from_token), db: Session = Depends(get_db)):
    # Remove current session
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Logged out successfully"}

# User preferences endpoints
@app.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(current_user: User = Depends(get_user_from_token), db: Session = Depends(get_db)):
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    return preferences

@app.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    preferences_data: PreferencesCreate,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not preferences:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
    
    preferences.writing_style = preferences_data.writing_style
    preferences.tone = preferences_data.tone
    preferences.target_audience = preferences_data.target_audience
    preferences.post_length = preferences_data.post_length
    preferences.topics_of_interest = json.dumps(preferences_data.topics_of_interest)
    preferences.ai_creativity_level = preferences_data.ai_creativity_level
    preferences.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(preferences)
    
    return preferences

# Posts endpoints
@app.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    post = Post(
        user_id=current_user.id,
        title=post_data.title,
        content="",  # Will be filled by agents
        original_idea=post_data.original_idea,
        status="draft"
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return post

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()
    return posts

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Update fields if provided
    if post_data.writer_output is not None:
        post.writer_output = post_data.writer_output
    if post_data.reviewer_feedback is not None:
        post.reviewer_feedback = post_data.reviewer_feedback
    if post_data.final_content is not None:
        post.final_content = post_data.final_content
        post.content = post_data.final_content  # Set final content as main content
    if post_data.status is not None:
        post.status = post_data.status
    
    post.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    
    return post

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "storage"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)