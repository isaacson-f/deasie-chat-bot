import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pymongo import MongoClient
import logging

load_dotenv()

logger = logging.getLogger(__name__)


async def get_openai_client():
    gpt_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    logger.info("Connected to OpenAI client")
    try:
        yield gpt_client
    finally:
        await gpt_client.close()
        logger.info("Disconnected from the OpenAI client")



