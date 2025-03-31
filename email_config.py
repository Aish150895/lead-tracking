"""
Email configuration module that sets up the appropriate email functions
based on debug mode setting
"""
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import settings
from config import settings

# Determine if we should use debug email mode
# Set DEBUG_EMAIL=false in environment to send real emails instead of logging them
DEBUG_EMAIL = settings.DEBUG_EMAIL.lower() in ("true", "1", "t")

# Log the email configuration
if not DEBUG_EMAIL:
    logger.info(f"SMTP Server: {settings.SMTP_SERVER}")
    logger.info(f"SMTP Port: {settings.SMTP_PORT}")
    logger.info(
        f"SMTP Username: {'*' * 8 if settings.SMTP_USERNAME else '[not set]'}")
    logger.info(
        f"SMTP Password: {'*' * 8 if settings.SMTP_PASSWORD else '[not set]'}")
    logger.info(f"Email From: {settings.EMAIL_FROM}")

if DEBUG_EMAIL:
    logger.info(
        "Using DEBUG email mode - emails will be logged instead of sent")
    from email_debug import send_prospect_notification_debug as send_prospect_notification
    from email_debug import send_attorney_notification_debug as send_attorney_notification
    from email_debug import get_sent_emails
else:
    logger.info("Using PRODUCTION email mode - emails will be sent via SMTP")
    from email_service import send_prospect_notification, send_attorney_notification

    # Provide a dummy function for compatibility in production mode
    def get_sent_emails():
        return []
