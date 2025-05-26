from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import uuid
from app.database import users_token

SECRET_KEY = "986d3a1cdc13c24f14927531b31cb2e47a4025f88385e6c67551c704613a689e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2
REFRESH_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM), expire

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    token = str(uuid.uuid4())
    return token, expire

def store_tokens(user_id: str, access_token: str, refresh_token: str, expires_at: datetime):
    users_token.insert_one({
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": expires_at
    })

def user_helper(user) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
        "created_at": user["created_at"]
    }