from motor.motor_asyncio import AsyncIOMotorClient
import os

# Connect to MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.analyzer_db

users_collection = db.get_collection("users")