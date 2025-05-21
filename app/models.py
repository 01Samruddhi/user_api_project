from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr

class UserOut(User):
    id: str
    created_at: datetime

