"""
Email service for user verification and notifications.
Supports both development (file-based) and production (SMTP) email sending.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional
from datetime import datetime

from afsp_app.app.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service that adapts behavior based on environment."""
    
    def __init__(self):
        self.is_production = settings.ENVIRONMENT == "production"
        self.smtp_configured = bool(settings.SMTP_SERVER and settings.SMTP_USERNAME)
        
    async def send_verification_email(self, email: str, verification_token: str, user_id: str) -> bool:
        """
        Send email verification email.
        In development: saves to file.
        In production: sends via SMTP.
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}&user={user_id}"
        
        subject = settings.EMAIL_VERIFICATION_SUBJECT
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .button {{ 
                    display: inline-block; 
                    background-color: #2563eb; 
                    color: white; 
                    padding: 12px 30px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to AFSP</h1>
                    <p>Automated Financial Statement Processor</p>
                </div>
                <div class="content">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering with AFSP! To complete your account setup, please verify your email address by clicking the button below:</p>
                    
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #e5e7eb; padding: 10px; border-radius: 3px;">
                        {verification_url}
                    </p>
                    
                    <p><strong>Important:</strong> This verification link will expire in 24 hours for security purposes.</p>
                    
                    <p>If you didn't create an account with AFSP, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from AFSP. Please do not reply to this email.</p>
                    <p>If you have questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_content = f"""
        Welcome to AFSP - Automated Financial Statement Processor
        
        Thank you for registering! To complete your account setup, please verify your email address.
        
        Verification Link: {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account with AFSP, you can safely ignore this email.
        """
        
        if self.is_production and self.smtp_configured:
            return await self._send_smtp_email(email, subject, html_content, text_content)
        else:
            return await self._save_email_to_file(email, subject, html_content, verification_url)
    
    async def _send_smtp_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """Send email via SMTP server (production)."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Verification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False
    
    async def _save_email_to_file(self, to_email: str, subject: str, html_content: str, verification_url: str) -> bool:
        """Save email to file (development)."""
        try:
            # Create email directory
            email_dir = Path(settings.BASE_DIR) / "emails"
            email_dir.mkdir(exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"verification_{to_email.replace('@', '_at_')}_{timestamp}.html"
            file_path = email_dir / filename
            
            # Add development notice to HTML
            dev_notice = f"""
            <div style="background-color: #fbbf24; color: #92400e; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                <strong>DEVELOPMENT MODE:</strong> This email would be sent to {to_email} in production.
                <br>
                <strong>Quick Verification Link:</strong> 
                <a href="{verification_url}" style="color: #92400e; text-decoration: underline;">
                    Click here to verify (dev mode)
                </a>
            </div>
            """
            
            full_html = html_content.replace('<div class="content">', f'<div class="content">{dev_notice}')
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            logger.info(f"Development verification email saved to: {file_path}")
            logger.info(f"Verification URL: {verification_url}")
            
            # Also log to console for easy access during development
            print(f"\n" + "="*80)
            print(f"📧 EMAIL VERIFICATION (Development Mode)")
            print(f"="*80)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Verification URL: {verification_url}")
            print(f"Saved to: {file_path}")
            print(f"="*80 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save verification email to file: {e}")
            return False

# Global email service instance
email_service = EmailService()
