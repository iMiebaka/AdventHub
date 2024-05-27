
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

MotorClient = AsyncIOMotorClient(SETTINGS.MONGO_URI)
Engine = AIOEngine(client=MotorClient, database="advent-hub")