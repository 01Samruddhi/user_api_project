from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from jose import JWTError, jwt
from datetime import datetime
from app.models import User, UserLogin, UserOut, UserUpdate, TokenRefresh, UserWithTokens
from app.database import users_collection, users_token
from app.utils import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, store_tokens, user_helper,
    SECRET_KEY, ALGORITHM
)
import uuid

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Debug logs
        print("Token payload:", payload)
        print("Current UTC time:", datetime.utcnow())
        print("Token EXP (UTC):", datetime.utcfromtimestamp(payload["exp"]))

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError as e:
        print("JWT Error:", str(e))
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
@router.post("/", response_model=UserOut)
def register_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user.password)

    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "password": hashed_pwd,
        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(user_data)

    return user_helper(user_data)

@router.post("/login", response_model=UserWithTokens)
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = db_user["id"]
    access_token, access_exp = create_access_token(data={"sub": user_id})
    refresh_token, refresh_exp = create_refresh_token(data={"sub": user_id})
    store_tokens(user_id, access_token, refresh_token, access_exp)

    return {
        **user_helper(db_user),
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.get("/", response_model=List[UserOut])
def get_users(current_user: dict = Depends(get_current_user)):
    users = users_collection.find()
    return [user_helper(u) for u in users]

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, updated_user: UserUpdate, current_user: dict = Depends(get_current_user)):
    hashed_pwd = hash_password(updated_user.password)
    users_collection.update_one({"id": user_id}, {"$set": {
        "name": updated_user.name,
        "email": updated_user.email,
        "password": hashed_pwd
    }})
    user = users_collection.find_one({"id": user_id})
    return user_helper(user)

@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    result = users_collection.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

@router.post("/refresh", response_model=UserOut)
def refresh_token(refresh_data: TokenRefresh):
    token_doc = users_token.find_one({"refresh_token": refresh_data.refresh_token})
    if not token_doc or token_doc["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user_id = token_doc["user_id"]
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token, access_exp = create_access_token(data={"sub": user_id})
    refresh_token, refresh_exp = create_refresh_token(data={"sub": user_id})

    store_tokens(user_id, access_token, refresh_token, access_exp)

    return {
        **user_helper(user),
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }