"""Email notification service using SendGrid or SMTP."""

import os
from typing import Dict, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailNotifier:
    def __init__(self, provider: str = "smtp"):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def send_email(self, 
                        to_email: str, 
                        subject: str, 
                        content: str, 
                        content_type: str = "html",
                        from_email: Optional[str] = None,
                        attachments: Optional[List[Dict]] = None) -> Dict:
        """Send an email using the configured provider."""
        
        if self.provider == "sendgrid" and self.sendgrid_api_key:
            return await self._send_via_sendgrid(to_email, subject, content, content_type, from_email, attachments)
        else:
            return await self._send_via_smtp(to_email, subject, content, content_type, from_email, attachments)

    async def _send_via_smtp(self, to_email: str, subject: str, content: str, 
                           content_type: str, from_email: Optional[str], 
                           attachments: Optional[List[Dict]]) -> Dict:
        """Send email via SMTP."""
        try:
            sender_email = from_email or self.default_sender
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if content_type.lower() == "html":
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
                if self.smtp_config["use_tls"]:
                    server.starttls()
                
                if self.smtp_config["username"] and self.smtp_config["password"]:
                    server.login(self.smtp_config["username"], self.smtp_config["password"])
                
                server.send_message(msg)
            
            return {
                "success": True,
                "message_id": f"smtp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "provider": "smtp",
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "smtp",
                "attempted_at": datetime.utcnow().isoformat()
            }

    async def _send_via_sendgrid(self, to_email: str, subject: str, content: str,
                               content_type: str, from_email: Optional[str],
                               attachments: Optional[List[Dict]]) -> Dict:
        """Send email via SendGrid API."""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType
            
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            sender_email = from_email or self.default_sender
            
            message = Mail(
                from_email=sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=content if content_type.lower() == "html" else None,
                plain_text_content=content if content_type.lower() != "html" else None
            )
            
            # Add attachments
            if attachments:
                for attachment_info in attachments:
                    attachment = Attachment(
                        FileContent(attachment_info.get("content", "")),
                        FileName(attachment_info.get("filename", "attachment")),
                        FileType(attachment_info.get("type", "application/octet-stream"))
                    )
                    message.attachment = attachment
            
            response = sg.send(message)
            
            return {
                "success": True,
                "message_id": response.headers.get("X-Message-Id", "unknown"),
                "status_code": response.status_code,
                "provider": "sendgrid",
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "sendgrid",
                "attempted_at": datetime.utcnow().isoformat()
            }

    def _add_attachment(self, msg: MIMEMultipart, attachment_info: Dict):
        """Add attachment to email message."""
        try:
            filename = attachment_info.get("filename", "attachment")
            content = attachment_info.get("content", "")
            mime_type = attachment_info.get("type", "application/octet-stream")
            
            # Create attachment
            part = MIMEBase(*mime_type.split('/'))
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
        except Exception as e:
            print(f"Failed to add attachment {attachment_info.get('filename', 'unknown')}: {e}")

    async def send_welcome_email(self, user_email: str, user_name: str) -> Dict:
        """Send welcome email to new user."""
        subject = "Welcome to IA Influencer Agent!"
        
        content = f"""
        <html>
        <body>
            <h2>Welcome, {user_name}!</h2>
            <p>Thank you for joining IA Influencer Agent - the revolutionary AI platform for content creators.</p>
            
            <h3>What you can do:</h3>
            <ul>
                <li>📤 Upload multi-format content (audio, video, images, text)</li>
                <li>🛡️ Protect your content with AI-powered rights management</li>
                <li>🚀 Optimize your content for maximum SEO impact</li>
                <li>🤝 Find collaboration opportunities with other creators</li>
                <li>📊 Distribute across multiple platforms automatically</li>
            </ul>
            
            <p>Get started by uploading your first piece of content!</p>
            
            <p>Best regards,<br>
            The IA Influencer Agent Team</p>
            
            <hr>
            <p><small>Copyright (c) 2025 Fahed Mlaiel. All rights reserved.</small></p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, content, "html")

    async def send_content_processed_email(self, user_email: str, content_info: Dict) -> Dict:
        """Send notification when content processing is complete."""
        subject = f"Content Processing Complete: {content_info.get('title', 'Your Content')}"
        
        content = f"""
        <html>
        <body>
            <h2>Content Processing Complete! ✅</h2>
            <p>Your content "<strong>{content_info.get('title', 'Unknown')}</strong>" has been successfully processed.</p>
            
            <h3>Processing Results:</h3>
            <ul>
                <li>🛡️ Rights Protection: {content_info.get('protection_status', 'Enabled')}</li>
                <li>🔍 SEO Optimization: {content_info.get('seo_score', 'High')}</li>
                <li>🤝 Collaboration Matches: {content_info.get('collaboration_count', 3)} found</li>
                <li>📱 Distribution Ready: {content_info.get('platform_count', 5)} platforms</li>
            </ul>
            
            <p>Your content is now ready for distribution!</p>
            
            <p>Best regards,<br>
            The IA Influencer Agent Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, content, "html")

    async def send_protection_alert_email(self, user_email: str, alert_info: Dict) -> Dict:
        """Send alert when content protection issue is detected."""
        subject = f"🚨 Content Protection Alert: {alert_info.get('content_title', 'Your Content')}"
        
        content = f"""
        <html>
        <body>
            <h2 style="color: #ff6b6b;">🚨 Content Protection Alert</h2>
            <p>We've detected potential unauthorized use of your content:</p>
            
            <h3>Content Details:</h3>
            <ul>
                <li><strong>Title:</strong> {alert_info.get('content_title', 'Unknown')}</li>
                <li><strong>Type:</strong> {alert_info.get('content_type', 'Unknown')}</li>
                <li><strong>Platform:</strong> {alert_info.get('detected_platform', 'Unknown')}</li>
                <li><strong>Similarity Score:</strong> {alert_info.get('similarity_score', 'N/A')}%</li>
            </ul>
            
            <h3>Recommended Actions:</h3>
            <ul>
                <li>Review the detected usage</li>
                <li>Contact the platform for takedown if unauthorized</li>
                <li>Update your content protection settings if needed</li>
            </ul>
            
            <p><strong>We're here to help protect your creative work!</strong></p>
            
            <p>Best regards,<br>
            The IA Influencer Agent Protection Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, content, "html")

    async def send_collaboration_opportunity_email(self, user_email: str, opportunity_info: Dict) -> Dict:
        """Send notification about new collaboration opportunity."""
        subject = f"🤝 New Collaboration Opportunity: {opportunity_info.get('partner_name', 'Creator')}"
        
        content = f"""
        <html>
        <body>
            <h2>🤝 New Collaboration Opportunity!</h2>
            <p>We've found a great collaboration match for you:</p>
            
            <h3>Partner Details:</h3>
            <ul>
                <li><strong>Name:</strong> {opportunity_info.get('partner_name', 'Unknown')}</li>
                <li><strong>Type:</strong> {opportunity_info.get('partner_type', 'Content Creator')}</li>
                <li><strong>Specialization:</strong> {opportunity_info.get('specialization', 'General')}</li>
                <li><strong>Compatibility Score:</strong> {opportunity_info.get('compatibility_score', 85)}%</li>
                <li><strong>Audience Size:</strong> {opportunity_info.get('audience_size', 'N/A'):,}</li>
            </ul>
            
            <h3>Why This Match?</h3>
            <p>{opportunity_info.get('match_reason', 'Similar content style and complementary skills.')}</p>
            
            <p>Ready to connect and create something amazing together?</p>
            
            <p>Best regards,<br>
            The IA Influencer Agent Collaboration Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, content, "html")
