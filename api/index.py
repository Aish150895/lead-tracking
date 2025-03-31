# api/index.py
import sys
import os

# Add the parent directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import your main FastAPI app and configuration
from main import app as main_app
from config import settings

# Create a new FastAPI app for Vercel
app = FastAPI(
    title="Lead Management System API",
    description="API for the Lead Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes from the main app
for route in main_app.routes:
    app.routes.append(route)

# Copy over middleware and exception handlers
app.middleware = main_app.middleware
app.exception_handlers = main_app.exception_handlers

# Add a health check endpoint
@app.get("/__health")
async def health_check():
    return {
        "status": "ok",
        "database": settings.DATABASE_URL.split("@")[-1].split("/")[-1] if "@" in settings.DATABASE_URL else "sqlite"
    }

# Create a handler for Vercel using Mangum
handler = Mangum(app)
