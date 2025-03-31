"""
Email service module for sending real emails using SMTP
"""
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional

from jinja2 import Template

from config import settings
from models import Lead

# Set up logging
logger = logging.getLogger(__name__)

async def send_email(recipient_email: str, subject: str, html_content: str, attachment_path: Optional[str] = None):
    """
    Send an email with optional attachment
    """
    try:
        # Create message container
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = settings.EMAIL_FROM
        message['To'] = recipient_email

        # Attach HTML part
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as file:
                    attachment = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                    attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    message.attach(attachment)
            except Exception as e:
                logger.error(f"Error attaching file: {str(e)}")
                # Continue without attachment

        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Login with credentials
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # Send email
        server.sendmail(settings.EMAIL_FROM, recipient_email, message.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

async def send_prospect_notification(lead: Lead):
    """
    Send confirmation email to the prospect after submission
    """
    try:
        # Create the email content
        subject = f"Thank you for your application - {settings.APP_NAME}"
        html_content = f"""
        <html>
            <body>
                <h1>Thank you for your application!</h1>
                <p>Dear {lead.first_name},</p>
                <p>We have received your application and will review it shortly.</p>
                <p>We will contact you as soon as possible with an update.</p>
                <p>Best regards,<br/>{settings.APP_NAME} Team</p>
            </body>
        </html>
        """
        
        # Send the email
        success = await send_email(lead.email, subject, html_content)
        
        if success:
            logger.info(f"Confirmation email sent to prospect {lead.email}")
        else:
            logger.error(f"Failed to send confirmation email to prospect {lead.email}")
            
        return success
    except Exception as e:
        logger.error(f"Error sending prospect notification: {str(e)}")
        return False

async def send_attorney_notification(lead: Lead):
    """
    Send notification email to attorney when a new lead is submitted
    """
    try:
        # Get attorney email from settings
        attorney_email = settings.ATTORNEY_EMAIL
        
        # Create the email content
        subject = f"New lead submitted - {lead.first_name} {lead.last_name}"
        html_content = f"""
        <html>
            <body>
                <h1>New Lead Submission</h1>
                <p>A new lead has been submitted:</p>
                <ul>
                    <li><strong>Name:</strong> {lead.first_name} {lead.last_name}</li>
                    <li><strong>Email:</strong> {lead.email}</li>
                    <li><strong>Time:</strong> {lead.created_at.strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
                <p>Please log in to the dashboard to review this lead.</p>
            </body>
        </html>
        """
        
        # Find the resume path to include as an attachment
        attachment_path = None
        if lead.resume_path:
            # Check if it's a full path or just a filename
            if os.path.exists(lead.resume_path):
                attachment_path = lead.resume_path
            else:
                attachment_path = os.path.join(settings.UPLOAD_DIR, lead.resume_path)
                if not os.path.exists(attachment_path):
                    logger.warning(f"Resume file not found: {attachment_path}")
                    attachment_path = None
        
        # Send the email with attachment
        success = await send_email(attorney_email, subject, html_content, attachment_path)
        
        if success:
            logger.info(f"Notification email sent to attorney {attorney_email}")
        else:
            logger.error(f"Failed to send notification email to attorney {attorney_email}")
            
        return success
    except Exception as e:
        logger.error(f"Error sending attorney notification: {str(e)}")
        return False