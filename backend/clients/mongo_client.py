import os
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

load_dotenv()

logger = logging.getLogger(__name__)


async def get_db():
    CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING")
    client = MongoClient(CONNECTION_STRING)
    logger.info("Connected to mongo")
    try:
        yield client
    finally:
        client.close()
        logger.info("Disconnected from mongo")


