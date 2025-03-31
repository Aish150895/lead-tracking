import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import uuid4

from utils.database import get_db
from models import Lead, LeadState, User
from schemas import LeadCreate, LeadResponse, LeadUpdate, LeadList
from utils.auth import get_current_user, get_current_attorney, get_current_user_from_header_or_cookie, get_current_attorney_from_header_or_cookie
from config import settings

# Import email functions from our config module
from services.email_config import send_prospect_notification, send_attorney_notification

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["leads"],
)

# Public endpoint for lead submission
@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def submit_lead(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Received lead submission for {first_name} {last_name} ({email})")
    
    try:
        # Create a new lead
        lead = Lead(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        # Ensure resume is provided
        if not resume or not resume.filename:
            logger.warning("Resume file is required but was not provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file is required"
            )
            
        logger.info(f"Processing resume upload: {resume.filename}")
        
        # Process the resume file
        try:
            # Check file size
            file_size = 0
            content = await resume.read()
            file_size = len(content)
            await resume.seek(0)
            
            logger.debug(f"Resume file size: {file_size/1024:.2f} KB")
            
            # Check if file is empty
            if file_size == 0:
                logger.warning("Resume file is empty")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resume file cannot be empty"
                )
                
            if file_size > settings.MAX_UPLOAD_SIZE:
                logger.warning(f"File size exceeds limit: {file_size/1024/1024:.2f}MB > {settings.MAX_UPLOAD_SIZE/1024/1024}MB")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE/1024/1024:.2f}MB"
                )
            
            # Create uploads directory if it doesn't exist
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Generate a unique filename
            file_extension = os.path.splitext(resume.filename)[1] if resume.filename else ".pdf"
            unique_filename = f"{uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
            
            logger.info(f"Resume saved successfully: {file_path}")
            # Store just the filename instead of the full path
            lead.resume_path = unique_filename
            
        except Exception as error:
            logger.error(f"Error processing resume: {str(error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing resume: {str(error)}"
            )
        
        # Save the lead to the database
        try:
            db.add(lead)
            db.commit()
            db.refresh(lead)
            logger.info(f"Lead created successfully with ID: {lead.id}")
        except Exception as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error saving lead to database: {str(e)}"
            )
        
        # Send email notifications asynchronously
        try:
            await send_prospect_notification(lead)
            await send_attorney_notification(lead)
            logger.info(f"Email notifications sent for lead ID: {lead.id}")
        except Exception as e:
            logger.error(f"Email notification error: {str(e)}", exc_info=True)
            # Don't fail the request if email sending fails
            # but log the error for troubleshooting
        
        return lead
    except HTTPException:
        # Re-raise HTTP exceptions without modifying them
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_lead: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Protected endpoint to get all leads (attorneys only)
@router.get("/leads", response_model=LeadList)
def get_all_leads(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    state: Optional[LeadState] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_attorney_from_header_or_cookie)
):
    logger.info(f"Getting leads for attorney ID: {current_user.id} | Params: skip={skip}, limit={limit}, state={state}, start_date={start_date}, end_date={end_date}, search={search}")
    
    try:
        # Build query
        query = db.query(Lead)
        
        # Filter by state if provided
        if state:
            logger.debug(f"Filtering leads by state: {state}")
            query = query.filter(Lead.state == state)
            
        # Filter by date range if provided
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                logger.debug(f"Filtering leads from date: {start_datetime}")
                query = query.filter(Lead.created_at >= start_datetime)
            except ValueError as e:
                logger.warning(f"Invalid start_date format: {start_date}. Error: {str(e)}")
                # Continue without applying this filter
                
        if end_date:
            try:
                # Add one day to include the entire end date
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                logger.debug(f"Filtering leads until date: {end_datetime}")
                query = query.filter(Lead.created_at < end_datetime)
            except ValueError as e:
                logger.warning(f"Invalid end_date format: {end_date}. Error: {str(e)}")
                # Continue without applying this filter
                
        # Search by name or email if provided
        if search:
            search_term = f"%{search}%"
            logger.debug(f"Searching leads with term: {search}")
            query = query.filter(
                or_(
                    Lead.first_name.ilike(search_term),
                    Lead.last_name.ilike(search_term),
                    Lead.email.ilike(search_term)
                )
            )
        
        # Count total matching leads
        try:
            total = query.count()
            logger.debug(f"Total matching leads: {total}")
        except Exception as e:
            logger.error(f"Error counting leads: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving lead count: {str(e)}"
            )
        
        # Apply pagination and get results
        try:
            leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
            logger.info(f"Successfully retrieved {len(leads)} leads")
        except Exception as e:
            logger.error(f"Error fetching leads: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving leads: {str(e)}"
            )
        
        return {"leads": leads, "total": total}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_all_leads: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Protected endpoint to update lead state
@router.patch("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(
    request: Request,
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_attorney_from_header_or_cookie)
):
    logger.info(f"Attorney ID {current_user.id} is updating lead ID {lead_id} | Update: {lead_update.dict(exclude_unset=True)}")
    
    try:
        # Get the lead
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                logger.warning(f"Lead ID {lead_id} not found during update attempt")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lead not found"
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            logger.error(f"Database error fetching lead ID {lead_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving lead: {str(e)}"
            )
        
        # Track what has changed
        changes = []
        
        # Update the state if provided
        if lead_update.state is not None:
            old_state = lead.state
            
            # If moving from PENDING to REACHED_OUT, record the attorney and timestamp
            if lead.state == LeadState.PENDING and lead_update.state == LeadState.REACHED_OUT:
                lead.reached_out_by = current_user.id
                lead.reached_out_at = datetime.utcnow()
                logger.info(f"Setting reached_out info: attorney={current_user.id}, time={lead.reached_out_at}")
            
            lead.state = lead_update.state
            changes.append(f"state: {old_state} -> {lead_update.state}")
            logger.info(f"Updated lead state from {old_state} to {lead_update.state}")
        
        # Update notes if provided
        if lead_update.notes is not None:
            old_notes = lead.notes
            lead.notes = lead_update.notes
            # Don't log full notes to avoid verbosity
            changes.append("notes updated")
            logger.info(f"Notes updated for lead ID {lead_id}")
        
        # Save changes
        try:
            db.commit()
            db.refresh(lead)
            logger.info(f"Successfully updated lead ID {lead_id}: {', '.join(changes)}")
        except Exception as e:
            logger.error(f"Error saving lead updates: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving lead updates: {str(e)}"
            )
        
        return lead
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_lead: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
