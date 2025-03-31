from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the parent directory to the Python path to import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from main.py
from main import app as main_app

# Create a new FastAPI app for Vercel
app = FastAPI()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes from the main app
app.include_router(main_app.router)

# Create a handler for Vercel serverless functions
def handler(request, context):
    return app