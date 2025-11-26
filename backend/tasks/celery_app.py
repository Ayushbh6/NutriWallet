"""Celery app configuration for scheduled scraping."""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
app = Celery(
    "nutriwallet",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    "scrape-spar-weekly": {
        "task": "tasks.scrape_tasks.scrape_store",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
        "args": ("spar", "vienna"),
    },
    "scrape-tesco-biweekly": {
        "task": "tasks.scrape_tasks.scrape_store",
        "schedule": crontab(hour=2, minute=0, day_of_week="0,3"),  # Sunday and Wednesday 2 AM
        "args": ("tesco", "london"),
    },
    "scrape-bigbasket-biweekly": {
        "task": "tasks.scrape_tasks.scrape_store",
        "schedule": crontab(hour=2, minute=0, day_of_week="0,3"),  # Sunday and Wednesday 2 AM
        "args": ("bigbasket", "mumbai"),
    },
}

