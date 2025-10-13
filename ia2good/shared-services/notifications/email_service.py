"""
Email Service
Handles email notifications via SendGrid
"""

import os
from typing import Optional, List, Dict, Any


class EmailService:
    """Send emails via SendGrid"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
        self.api_key = os.getenv('SENDGRID_API_KEY', '')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@ia2good.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'IA2GOOD')
        
        # In production, initialize SendGrid client
        # from sendgrid import SendGridAPIClient
        # self.client = SendGridAPIClient(self.api_key)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send email to a recipient
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text email body (fallback)
            attachments: List of attachment dicts
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            print(f"Email disabled. Would send to {to_email}: {subject}")
            return False
        
        if not self.api_key:
            print("SendGrid API key not configured")
            return False
        
        try:
            # In production:
            # from sendgrid.helpers.mail import Mail
            # message = Mail(
            #     from_email=(self.from_email, self.from_name),
            #     to_emails=to_email,
            #     subject=subject,
            #     html_content=html_content,
            #     plain_text_content=plain_content
            # )
            # response = self.client.send(message)
            
            print(f"[EMAIL] To: {to_email} | Subject: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        module: str = "IA2GOOD"
    ) -> bool:
        """
        Send welcome email to new user
        
        Args:
            to_email: Recipient email
            user_name: User's name
            module: Module name
            
        Returns:
            True if sent successfully
        """
        subject = f"Welcome to {module}!"
        html_content = f"""
        <html>
            <body>
                <h1>Welcome to {module}, {user_name}!</h1>
                <p>Thank you for joining our platform.</p>
                <p>You can now access all features of {module}.</p>
                <p>Best regards,<br>The {module} Team</p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_verification_email(
        self,
        to_email: str,
        verification_link: str,
        user_name: str = ""
    ) -> bool:
        """
        Send email verification link
        
        Args:
            to_email: Recipient email
            verification_link: Verification URL
            user_name: User's name
            
        Returns:
            True if sent successfully
        """
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        subject = "Verify your email address"
        html_content = f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>{greeting}</p>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email Address</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        user_name: str = ""
    ) -> bool:
        """
        Send password reset link
        
        Args:
            to_email: Recipient email
            reset_link: Password reset URL
            user_name: User's name
            
        Returns:
            True if sent successfully
        """
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        subject = "Reset your password"
        html_content = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>{greeting}</p>
                <p>You requested to reset your password. Click the link below:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_notification_email(
        self,
        to_email: str,
        notification_title: str,
        notification_body: str,
        action_url: Optional[str] = None
    ) -> bool:
        """
        Send notification email
        
        Args:
            to_email: Recipient email
            notification_title: Notification title
            notification_body: Notification message
            action_url: Optional action URL
            
        Returns:
            True if sent successfully
        """
        action_button = ""
        if action_url:
            action_button = f'<p><a href="{action_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Details</a></p>'
        
        html_content = f"""
        <html>
            <body>
                <h2>{notification_title}</h2>
                <p>{notification_body}</p>
                {action_button}
            </body>
        </html>
        """
        
        return await self.send_email(to_email, notification_title, html_content)
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str
    ) -> Dict[str, int]:
        """
        Send email to multiple recipients
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML content
            
        Returns:
            Dict with success_count and failure_count
        """
        success_count = 0
        failure_count = 0
        
        for email in recipients:
            success = await self.send_email(email, subject, html_content)
            if success:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count
        }
