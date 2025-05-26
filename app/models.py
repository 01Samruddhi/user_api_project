from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    password: str
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserWithTokens(UserOut):
    access_token: str
    token_type: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str