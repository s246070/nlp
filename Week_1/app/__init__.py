"""Application entry points for Uvicorn."""

from .main import app as sentiment_service_app
from .sentiment_analysis_ui import app

__all__ = ["app", "sentiment_service_app"]
