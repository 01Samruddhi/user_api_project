from fastapi import APIRouter, HTTPException
from app.models import User, UserOut
from app.database import users_collection
from app.utils import user_helper
from typing import List
from datetime import datetime
import uuid
from faker import Faker

router = APIRouter(prefix="/users", tags=["users"])
faker = Faker()

@router.post("/", response_model=UserOut)
def create_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    user_data = user.dict()
    user_data["id"] = str(uuid.uuid4())
    user_data["created_at"] = datetime.utcnow()

    users_collection.insert_one(user_data)
    return user_helper(user_data)

@router.get("/", response_model=List[UserOut])
def get_users():
    users = users_collection.find()
    return [user_helper(u) for u in users]

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, updated_user: User):
    result = users_collection.update_one(
        {"id": user_id},
        {"$set": updated_user.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    user = users_collection.find_one({"id": user_id})
    return user_helper(user)

@router.delete("/{user_id}")
def delete_user(user_id: str):
    result = users_collection.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

@router.post("/generate-fake", response_model=List[UserOut])
def generate_fake_users():
    users = []
    for _ in range(10):
        user_data = {
            "id": str(uuid.uuid4()),
            "name": faker.name(),
            "email": faker.unique.email(),
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(user_data)
        users.append(user_helper(user_data))
    return users