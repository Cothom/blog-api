"""FastAPI defaults to launching app from 'main' module."""

# Logging configuration must occur before anything else
import app.logger  # pyright: ignore [reportUnusedImport]

# 'app' object must then be in main's namespace
from app.routes import app  # pyright: ignore [reportUnusedImport]
