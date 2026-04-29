"""
Lost & Finder — FastAPI Backend
config.py: Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Settings:
    # Raw URI (preferred). If empty, fall back to component-based build below.
    MONGO_URI: str = os.getenv("MONGO_URI", "")

    # Component-based connection options (optional)
    MONGO_USER: str = os.getenv("MONGO_USER", "")
    MONGO_PASS: str = os.getenv("MONGO_PASS", "")
    MONGO_HOST: str = os.getenv("MONGO_HOST", "127.0.0.1")
    MONGO_PORT: str = os.getenv("MONGO_PORT", "27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "lostfinder")

    def get_mongo_uri(self) -> str:
        """Return a safe Mongo URI.

        Priority:
        1. If MONGO_URI provided, return it unchanged.
        2. If MONGO_USER present, build a URI and URL-encode credentials.
        3. Else return a localhost URI using host/port/db.
        """
        if self.MONGO_URI:
            return self.MONGO_URI
        if self.MONGO_USER:
            user = quote_plus(self.MONGO_USER)
            pwd = quote_plus(self.MONGO_PASS or "")
            return f"mongodb://{user}:{pwd}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", 24))

    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@lostfinder.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@123456")

    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500,http://127.0.0.1:3000"
    ).split(",")

settings = Settings()
