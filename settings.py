from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pydantic import Field
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings
import  os
from dotenv import load_dotenv

load_dotenv()
ENV = os.environ.get("ENV", "default")


class _Settings(BaseSettings):
    SECRET_KEY: SecretStr = Field(
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7lsklkl"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_URI: Optional[str] = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "advent-hub"

class Development(_Settings):
    ENV: str = "development"

class Testing(_Settings):
    ENV: str = "testing"
    DATABASE_NAME: str = "advent-hub-test"

class Production(_Settings):
    ENV: str = "production"


config = {
    "development": Development,
    "production": Production,
    "default": Development,
    "testing": Testing,
}


# Make this a singleton to avoid reloading it from the env everytime
SETTINGS:_Settings = config[ENV]()

MotorClient = AsyncIOMotorClient(SETTINGS.MONGO_URI)
Engine = AIOEngine(client=MotorClient, database=SETTINGS.DATABASE_NAME)