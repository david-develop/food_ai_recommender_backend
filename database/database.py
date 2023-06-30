from motor.motor_asyncio import AsyncIOMotorClient
import os

def get_mongo_client(enviroment: str):
    if enviroment != "prod":
        MONGODB_URL = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASS')}@{os.getenv('MONGO_URI')}/{os.getenv('MONGO_DB')}?retryWrites=true&w=majority"
    else:
        MONGODB_URL = f"mongodb://{os.getenv('MONGO_URI')}?retryWrites=true&w=majority"
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    return mongo_client
