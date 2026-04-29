import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

async def main():
    db = AsyncIOMotorClient(settings.get_mongo_uri())[settings.MONGO_DB]
    admins = await db.admins.find().to_list(10)
    for a in admins:
        a["password_hash"] = "***"
        print("Admin:", a)
    reports = await db.reports.find({}, {"name": 1, "_id": 0}).to_list(10)
    print("Reports:", reports)

asyncio.run(main())
