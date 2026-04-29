"""
Lost & Finder — FastAPI Backend
database.py: Async MongoDB connection using Motor
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    uri = settings.get_mongo_uri() if hasattr(settings, 'get_mongo_uri') else settings.MONGO_URI
    client = AsyncIOMotorClient(uri)
    db = client.lostfinder
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.reports.create_index("report_id", unique=True)
    await db.admins.create_index("email", unique=True)
    print("Connected to MongoDB")

async def close_db():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_db():
    return db
