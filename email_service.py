import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from config import settings
from models import Lead

# Get email settings directly from environment
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
EMAIL_FROM = settings.EMAIL_FROM
ATTORNEY_EMAIL = settings.ATTORNEY_EMAIL

# Set up logging
logger = logging.getLogger(__name__)

# Log email settings (only username, not password)
logger.info(f"Email configuration loaded from environment:")
logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
logger.info(f"SMTP_PORT: {SMTP_PORT}")
logger.info(f"SMTP_USERNAME: {'*' * 8 if SMTP_USERNAME else 'not set'}")
logger.info(f"EMAIL_FROM: {EMAIL_FROM}")
logger.info(f"ATTORNEY_EMAIL: {ATTORNEY_EMAIL}")

# Set up Jinja2 environment for email templates
templates_env = Environment(loader=FileSystemLoader('templates/email'))

async def send_email(recipient_email: str, subject: str, html_content: str, attachment_path: Optional[str] = None):
    """
    Send an email with optional attachment
    """
    # Skip sending emails if SMTP settings are not configured
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
        logger.warning("Email sending skipped: SMTP settings not fully configured")
        return
    
    try:
        # Log SMTP connection details (without showing password)
        # Use directly loaded environment variables
        logger.info(f"Preparing to send email to {recipient_email} via {SMTP_SERVER}:{SMTP_PORT}")
        logger.info(f"Current SMTP settings: SERVER={SMTP_SERVER}, PORT={SMTP_PORT}, USERNAME={SMTP_USERNAME}")
        
        # Create message container
        msg = MIMEMultipart()
        # Use EMAIL_FROM from environment settings
        msg['From'] = EMAIL_FROM
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)
        
        # Connect to SMTP server with more verbosity and better error handling
        logger.debug(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        
        # Set up SMTP connection with simplified settings
        try:
            # Create SMTP connection with simplest approach
            logger.debug("Creating SMTP connection")
            logger.debug(f"Using standard SMTP connection to {SMTP_SERVER}:{SMTP_PORT}")
            
            # Create server and enable debug output
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.set_debuglevel(1)
            
            # Say hello to the server
            server.ehlo()
            
            # Check if we need to use TLS
            if SMTP_PORT == 587:  # Standard TLS port
                logger.debug("Starting TLS session")
                server.starttls()
                server.ehlo()  # Re-identify after TLS
            
            # Simple login - let SMTP library handle the details
            if SMTP_USERNAME and SMTP_PASSWORD:
                logger.debug(f"Logging in as {SMTP_USERNAME}")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            else:
                logger.error("Missing SMTP credentials - username or password is None")
                raise ValueError("SMTP credentials not properly configured")
            
        except Exception as e:
            logger.error(f"SMTP connection error: {str(e)}")
            raise
        
        # Send email
        logger.debug(f"Sending message to {recipient_email}")
        server.send_message(msg)
        
        # Close connection
        logger.debug("Closing SMTP connection")
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email to {recipient_email}: {str(e)}")
        # Don't re-raise exception, as email sending is not critical
        # and shouldn't block other operations
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        # Don't re-raise exception, as email sending is not critical
        # and shouldn't block other operations
        return False

async def send_prospect_notification(lead: Lead):
    """
    Send confirmation email to the prospect after submission
    """
    try:
        # Get email template
        template = templates_env.get_template('prospect_notification.html')
        
        # Render template with lead data
        html_content = template.render(
            lead=lead,
            current_year=datetime.now().year
        )
        
        # Send email to the prospect's email address
        await send_email(
            recipient_email=lead.email,  # Send to the prospect's email
            subject="Thank You for Your Submission",
            html_content=html_content
        )
        
        logger.info(f"Prospect notification sent to {lead.email}")
    except Exception as e:
        logger.error(f"Failed to send prospect notification: {str(e)}")

async def send_attorney_notification(lead: Lead):
    """
    Send notification email to attorney when a new lead is submitted
    """
    try:
        # Get email template
        template = templates_env.get_template('attorney_notification.html')
        
        # Render template with lead data
        html_content = template.render(
            lead=lead,
            domain=os.environ.get('REPLIT_DOMAIN', 'localhost:5000'),
            current_year=datetime.now().year
        )
        
        # Get resume path for attachment
        resume_path = None
        if lead.resume_path:
            resume_path = os.path.join(settings.UPLOAD_DIR, lead.resume_path)
            if not os.path.exists(resume_path):
                logger.warning(f"Resume file not found at {resume_path}")
                resume_path = None
        
        # Send email with resume attachment
        await send_email(
            recipient_email=ATTORNEY_EMAIL,
            subject=f"New Lead Submission: {lead.first_name} {lead.last_name}",
            html_content=html_content,
            attachment_path=resume_path
        )
        
        logger.info(f"Attorney notification sent to {ATTORNEY_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send attorney notification: {str(e)}")