"""
SMS Service
Handles SMS notifications via Twilio
"""

import os
from typing import Optional


class SMSService:
    """Send SMS messages via Twilio"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_SMS_NOTIFICATIONS', 'true').lower() == 'true'
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        
        # In production, initialize Twilio client
        # from twilio.rest import Client
        # self.client = Client(self.account_sid, self.auth_token)
    
    async def send_sms(
        self,
        to_number: str,
        message: str,
        priority: str = "normal"
    ) -> bool:
        """
        Send SMS to a phone number
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: SMS message body
            priority: Message priority (normal, high)
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            print(f"SMS disabled. Would send to {to_number}: {message}")
            return False
        
        if not self.from_number:
            print("Twilio phone number not configured")
            return False
        
        try:
            # In production:
            # message = self.client.messages.create(
            #     body=message,
            #     from_=self.from_number,
            #     to=to_number
            # )
            
            print(f"[SMS] To: {to_number} | Message: {message[:50]}...")
            return True
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    async def send_verification_code(
        self,
        to_number: str,
        code: str,
        app_name: str = "IA2GOOD"
    ) -> bool:
        """
        Send verification code via SMS
        
        Args:
            to_number: Recipient phone number
            code: Verification code
            app_name: Application name
            
        Returns:
            True if sent successfully
        """
        message = f"Your {app_name} verification code is: {code}. Valid for 10 minutes."
        return await self.send_sms(to_number, message, priority="high")
    
    async def send_alert(
        self,
        to_number: str,
        alert_message: str,
        module: str = ""
    ) -> bool:
        """
        Send alert SMS
        
        Args:
            to_number: Recipient phone number
            alert_message: Alert message
            module: Module name (ia2good, guardian, etc.)
            
        Returns:
            True if sent successfully
        """
        prefix = f"[{module.upper()}] " if module else ""
        message = f"{prefix}ALERT: {alert_message}"
        return await self.send_sms(to_number, message, priority="high")
    
    async def send_bulk_sms(
        self,
        phone_numbers: list[str],
        message: str
    ) -> dict:
        """
        Send SMS to multiple recipients
        
        Args:
            phone_numbers: List of phone numbers
            message: Message to send
            
        Returns:
            Dict with success_count and failure_count
        """
        success_count = 0
        failure_count = 0
        
        for number in phone_numbers:
            success = await self.send_sms(number, message)
            if success:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count
        }
