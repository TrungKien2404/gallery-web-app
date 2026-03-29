from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PhotoOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    uploaded_at: datetime
    user_id: int
    
    like_count: int = 0
    liked: bool = False
    class Config:
        from_attributes = True

class PhotoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
class LikeOut(BaseModel):
    user_id: int
    photo_id: int
    class Config:
        from_attributes = True