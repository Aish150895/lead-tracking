from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the parent directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your main FastAPI app 
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

# Middleware and exception handlers from main app
app.middleware = main_app.middleware
app.exception_handlers = main_app.exception_handlers

# Add a health check endpoint
@app.get("/__health")
async def health_check():
    return {
        "status": "ok", 
        "database": settings.DATABASE_URL.split("@")[-1].split("/")[-1] if "@" in settings.DATABASE_URL else "sqlite"
    }

# Handler function for Vercel serverless environment
def handler(request, context):
    return app