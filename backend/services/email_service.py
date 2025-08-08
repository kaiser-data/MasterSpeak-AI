# backend/services/email_service.py

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications and verification emails"""
    
    def __init__(self):
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.use_tls = settings.MAIL_USE_TLS
        self.use_ssl = settings.MAIL_USE_SSL
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM
        
    def _get_smtp_connection(self):
        """Create and configure SMTP connection"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            if self.username and self.password:
                server.login(self.username, self.password)
                
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Send an email with HTML and optional text content"""
        try:
            if not self.username or not self.password:
                logger.warning("Email credentials not configured - email sending disabled")
                return False
                
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, to_email: str, token: str, user_name: str = None):
        """Send email verification email"""
        # Create verification URL - adjust domain based on environment
        if settings.ENV == "production":
            base_url = "https://master-speak-gr57j6rdr-martins-projects-5db7b2b8.vercel.app"
        else:
            base_url = "http://localhost:3000"
            
        verify_url = f"{base_url}/auth/verify-email?token={token}"
        
        subject = "Verify your MasterSpeak AI account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90E2;">Welcome to MasterSpeak AI!</h2>
                
                <p>Hello{" " + user_name if user_name else ""},</p>
                
                <p>Thank you for registering with MasterSpeak AI. To complete your registration and start improving your speaking skills with AI-powered feedback, please verify your email address.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" 
                       style="background-color: #4A90E2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Verify Your Email
                    </a>
                </div>
                
                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">
                    {verify_url}
                </p>
                
                <p>This verification link will expire in 24 hours for security reasons.</p>
                
                <p>If you didn't create an account with MasterSpeak AI, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 12px;">
                    Best regards,<br>
                    The MasterSpeak AI Team
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to MasterSpeak AI!
        
        Hello{" " + user_name if user_name else ""},
        
        Thank you for registering with MasterSpeak AI. To complete your registration and start improving your speaking skills with AI-powered feedback, please verify your email address.
        
        Please click this link to verify your email:
        {verify_url}
        
        This verification link will expire in 24 hours for security reasons.
        
        If you didn't create an account with MasterSpeak AI, please ignore this email.
        
        Best regards,
        The MasterSpeak AI Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, token: str, user_name: str = None):
        """Send password reset email"""
        # Create reset URL - adjust domain based on environment
        if settings.ENV == "production":
            base_url = "https://master-speak-gr57j6rdr-martins-projects-5db7b2b8.vercel.app"
        else:
            base_url = "http://localhost:3000"
            
        reset_url = f"{base_url}/auth/reset-password?token={token}"
        
        subject = "Reset your MasterSpeak AI password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90E2;">Password Reset Request</h2>
                
                <p>Hello{" " + user_name if user_name else ""},</p>
                
                <p>We received a request to reset your password for your MasterSpeak AI account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #E74C3C; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                
                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">
                    {reset_url}
                </p>
                
                <p>This password reset link will expire in 1 hour for security reasons.</p>
                
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 12px;">
                    Best regards,<br>
                    The MasterSpeak AI Team
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hello{" " + user_name if user_name else ""},
        
        We received a request to reset your password for your MasterSpeak AI account.
        
        Please click this link to reset your password:
        {reset_url}
        
        This password reset link will expire in 1 hour for security reasons.
        
        If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
        
        Best regards,
        The MasterSpeak AI Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Create singleton instance
email_service = EmailService()