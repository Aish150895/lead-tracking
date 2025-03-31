# Lead Management System

A FastAPI-based lead management system with public submission form, email notifications, and internal authenticated dashboard.
Demo: https://lead-tracker-laturkaraishvar.replit.app/

## Features

- Public lead submission form with required resume/CV upload
- Email notification system for both prospects and attorneys
- Internal authenticated dashboard for lead management
- Lead state management (PENDING → REACHED_OUT)
- JWT-based authentication for internal access
- Data persistence with SQLite database

## Tech Stack

- **Backend**: Python 3.9+, FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with role-based access control
- **Email**: SMTP with Jinja2 templates
- **Frontend**: React frontend with Bootstrap CSS
- **API**: RESTful JSON API with proper error handling
- **File Handling**: Python-multipart for file uploads

## Tools
- Cursor
- Replit

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- SQLite for development
- Node.js (for the React frontend)

### Environment Variables

Create a `.env` file with the env.example file as a template.

### Installation

1. Install Python dependencies
```bash
pip install -r requirements.txt
```

2. Set up the database
```bash
python3 -c "from utils.database import engine, Base; from models import User, Lead; Base.metadata.create_all(bind=engine)"
```

3. Create an attorney account
```bash
python3 create_attorney.py
```

4. Build the frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

5. Start the server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Default Credentials

The system is pre-configured with an attorney account for testing:

- **Email**: attorney@leadtracker.com
- **Password**: attorney@leadtracker
  
## Routes and Access

- **Public Form**: http://localhost:5000/
- **Login**: http://localhost:5000/login
- **Dashboard**: http://localhost:5000/dashboard (Attorney access only)
- **API Documentation**: http://localhost:5000/docs

## Project Structure

```
├── api/                   # Vercel serverless functions
│   ├── index.py           # Primary API handler for Vercel
│   └── vercel.py          # Support functions for Vercel deployment
├── config.py              # Configuration settings
├── create_attorney.py     # Script to create attorney users
├── frontend/              # React frontend application
├── main.py                # Main application entry point
├── models.py              # SQLAlchemy database models
├── routers/               # API route modules
│   ├── auth.py            # Authentication endpoints
│   └── leads.py           # Lead management endpoints
├── schemas.py             # Pydantic data schemas
├── services/              # Service modules
│   ├── __init__.py        # Package initialization
│   ├── email_config.py    # Email configuration selector (debug vs production)
│   ├── email_debug.py     # Development mode email logging
│   └── email_service.py   # Production email sending functionality
├── static/                # Static assets
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Attorney dashboard
│   ├── email/             # Email templates
│   │   ├── attorney_notification.html
│   │   └── prospect_notification.html
│   ├── lead_form.html     # Public submission form
│   └── login.html         # Login page
├── tests/                 # Test modules
├── uploads/               # Directory for uploaded files
├── utils/                 # Utility modules
│   ├── __init__.py        # Package initialization
│   ├── auth.py            # Authentication utilities
│   └── database.py        # Database connection and utilities
└── vercel_database.py     # Database configuration for Vercel deployment
```


