"""
Multi-Factor Authentication (MFA) Handler
Supports TOTP (Time-based One-Time Password) and SMS-based 2FA
"""

import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional
import os


class MFAHandler:
    """Handle Multi-Factor Authentication operations"""
    
    def __init__(self):
        self.issuer_name = os.getenv('APP_NAME', 'IA2GOOD')
        self.enable_2fa = os.getenv('ENABLE_2FA', 'true').lower() == 'true'
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret for a user
        
        Returns:
            Base32 encoded secret string
        """
        return pyotp.random_base32()
    
    def get_totp_uri(self, secret: str, email: str) -> str:
        """
        Generate TOTP URI for QR code
        
        Args:
            secret: User's TOTP secret
            email: User's email
            
        Returns:
            TOTP URI string
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.issuer_name)
    
    def generate_qr_code(self, secret: str, email: str) -> str:
        """
        Generate QR code image for TOTP setup
        
        Args:
            secret: User's TOTP secret
            email: User's email
            
        Returns:
            Base64 encoded QR code image
        """
        uri = self.get_totp_uri(secret, email)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: User's TOTP secret
            token: 6-digit token from authenticator app
            
        Returns:
            True if valid, False otherwise
        """
        if not self.enable_2fa:
            return True
        
        totp = pyotp.TOTP(secret)
        # Allow 1 period before/after for clock skew
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Generate backup codes for account recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes
        """
        import secrets
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
    
    async def send_sms_code(self, phone: str) -> Optional[str]:
        """
        Send SMS verification code
        
        Args:
            phone: Phone number
            
        Returns:
            Verification code sent (for testing), or None on error
        """
        # Generate 6-digit code
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # In production, integrate with Twilio or similar
        # For now, just return the code for testing
        print(f"SMS Code for {phone}: {code}")
        
        return code
    
    def verify_sms_code(self, stored_code: str, provided_code: str) -> bool:
        """
        Verify SMS code
        
        Args:
            stored_code: Code that was sent
            provided_code: Code provided by user
            
        Returns:
            True if codes match
        """
        return stored_code == provided_code
