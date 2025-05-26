from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta

client = MongoClient("mongodb://localhost:27017")
db = client["user_db"]
users_collection = db["users"]
users_token = db["user_token"]

users_token.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)