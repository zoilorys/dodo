import os
from dotenv import load_dotenv

from celery import Celery

load_dotenv()

celery = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL"),
    include=["src.celery.tasks"]
)
