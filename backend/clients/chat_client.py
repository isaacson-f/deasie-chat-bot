import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
import logging

load_dotenv()

logger = logging.getLogger(__name__)


async def get_openai_client():
    gpt_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    logger.info("Connected to OpenAI client")
    try:
        yield gpt_client
    finally:
        gpt_client.close()
        logger.info("Disconnected from the gpt client")



