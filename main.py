import os
import logging
import traceback
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, status, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

import schemas
import models
from utils.database import engine, get_db
from routers import leads, auth
from utils.auth import get_current_user, get_current_attorney, get_current_user_from_header_or_cookie, get_current_attorney_from_header_or_cookie
from config import settings

# Import email functions from our config module
from services.email_config import DEBUG_EMAIL, get_sent_emails

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Custom exception middleware
class ExceptionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Exception in request: {request.url.path}")
            logger.error(f"Exception details: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal Server Error: {str(e)}"})


# Create the database tables
models.Base.metadata.create_all(bind=engine)
logger.info("Database tables created or verified")

# Run database schema update for role column
try:
    from update_db_schema import update_database_schema
    update_database_schema()
    logger.info("Database schema update for role column completed")

    # Create default attorney user AFTER schema update
    from create_attorney import create_attorney_user
    from utils.database import SessionLocal
    db = SessionLocal()
    try:
        # Get attorney credentials from settings
        # (already imported at the top)

        # Use settings which already have defaults configured
        attorney_email = settings.DEFAULT_ATTORNEY_EMAIL
        attorney_password = settings.DEFAULT_ATTORNEY_PASSWORD
        attorney_name = settings.DEFAULT_ATTORNEY_NAME

        create_attorney_user(db=db,
                             email=attorney_email,
                             password=attorney_password,
                             full_name=attorney_name)
        logger.info("Default attorney user verified/created")
    finally:
        db.close()
except Exception as e:
    logger.error(f"Error updating database schema for role column: {str(e)}")
    # Continue execution to not break completely

# Create the FastAPI app
app = FastAPI(title=settings.APP_NAME,
              description=settings.APP_DESCRIPTION,
              version=settings.APP_VERSION)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception middleware
app.add_middleware(ExceptionMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend static files if they exist
frontend_dist_path = os.path.join(os.path.dirname(__file__), "frontend",
                                  "dist")
if os.path.exists(frontend_dist_path):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dist_path, "assets")),
        name="assets")

# Include routers with API prefix
app.include_router(leads.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

# Add debugging endpoint for emails if in debug mode
if DEBUG_EMAIL:

    @app.get("/debug/emails", response_model=List[Dict[str, Any]])
    async def debug_view_emails(
            current_user: models.User = Depends(get_current_attorney)):
        """View all emails sent in debug mode - only accessible to attorneys"""
        return get_sent_emails()


# Add a direct route for the lead form submission
@app.post("/api/leads/direct",
          response_model=schemas.LeadResponse,
          status_code=status.HTTP_201_CREATED)
async def submit_lead_direct(request: Request,
                             first_name: str = Form(...),
                             last_name: str = Form(...),
                             email: str = Form(...),
                             resume: UploadFile = File(...),
                             db: Session = Depends(get_db)):
    # Validate that resume is provided
    if not resume or not resume.filename:
        logger.warning("Resume file is required but was not provided")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Resume file is required")

    # Forward to the existing handler in the router
    return await leads.submit_lead(request, first_name, last_name, email,
                                   resume, db)


# Add a direct route for token login
@app.post("/api/auth/token", response_model=schemas.Token)
async def login_direct(form_data: OAuth2PasswordRequestForm = Depends(),
                       db: Session = Depends(get_db)):
    from routers.auth import login_for_access_token
    return await login_for_access_token(form_data, db)


# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# Define routes to serve the React SPA
@app.get("/")
@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str = ""):
    # For all non-API routes, serve the index.html for React's client-side routing
    if not (full_path.startswith("api/") or full_path == "api"
            or full_path.startswith("assets/")):
        frontend_index_path = os.path.join(os.path.dirname(__file__),
                                           "frontend", "dist", "index.html")

        if os.path.exists(frontend_index_path):
            with open(frontend_index_path, "r") as f:
                return HTMLResponse(content=f.read())
        else:
            # If frontend is not built yet, return a message
            return HTMLResponse(content="""
            <html>
                <head><title>Lead Management System</title></head>
                <body>
                    <h1>Frontend Not Built</h1>
                    <p>The React frontend has not been built yet. Please build it first.</p>
                    <p>Run the following command:</p>
                    <pre>cd frontend && npm install && npm run build</pre>
                </body>
            </html>
            """)
    # For API routes, continue to next route handler (should be handled by included routers)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server on port 5000")
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
