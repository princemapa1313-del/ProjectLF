import asyncio
from backend.auth.utils import verify_password
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

async def main():
    db = AsyncIOMotorClient(settings.get_mongo_uri())[settings.MONGO_DB]
    admin = await db.admins.find_one({"email": "admin@lostfinder.com"})
    print("Hash from DB:", admin["password_hash"])
    is_valid = verify_password("Admin@123456", admin["password_hash"])
    print("Is valid?", is_valid)

asyncio.run(main())
