"""Validation utilities for IA2GOOD module"""
from typing import List, Optional
import re


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (French format)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # French phone: +33 or 0, followed by 9 digits
    pattern = r'^(\+33|0)[1-9](\d{2}){4}$'
    cleaned = phone.replace(' ', '').replace('-', '').replace('.', '')
    return bool(re.match(pattern, cleaned))


def validate_title_length(title: str, min_len: int = 5, max_len: int = 255) -> bool:
    """
    Validate title length
    
    Args:
        title: Title to validate
        min_len: Minimum length (default: 5)
        max_len: Maximum length (default: 255)
        
    Returns:
        True if valid, False otherwise
    """
    if not title or not title.strip():
        return False
    return min_len <= len(title.strip()) <= max_len


def validate_description_length(description: str, min_len: int = 20) -> bool:
    """
    Validate description length
    
    Args:
        description: Description to validate
        min_len: Minimum length (default: 20)
        
    Returns:
        True if valid, False otherwise
    """
    if not description or not description.strip():
        return False
    return len(description.strip()) >= min_len


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        True if valid, False otherwise
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_urgency_level(level: int) -> bool:
    """
    Validate urgency level
    
    Args:
        level: Urgency level (1-10)
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= level <= 10


def validate_rating(rating: int) -> bool:
    """
    Validate rating value
    
    Args:
        rating: Rating (1-5 stars)
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= rating <= 5


def validate_skills(skills: List[str], allowed_skills: Optional[List[str]] = None) -> bool:
    """
    Validate skills list
    
    Args:
        skills: List of skills to validate
        allowed_skills: List of allowed skills (optional)
        
    Returns:
        True if valid, False otherwise
    """
    if not skills or len(skills) < 1:
        return False
    
    if len(skills) > 10:
        return False
    
    if allowed_skills:
        return all(skill in allowed_skills for skill in skills)
    
    return True


def validate_distance(distance_km: int, min_km: int = 1, max_km: int = 100) -> bool:
    """
    Validate distance in kilometers
    
    Args:
        distance_km: Distance in km
        min_km: Minimum distance (default: 1)
        max_km: Maximum distance (default: 100)
        
    Returns:
        True if valid, False otherwise
    """
    return min_km <= distance_km <= max_km


def validate_photo_count(photos: List[str], max_count: int = 5) -> bool:
    """
    Validate number of photos
    
    Args:
        photos: List of photo URLs
        max_count: Maximum allowed photos (default: 5)
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= len(photos) <= max_count


def sanitize_text(text: str) -> str:
    """
    Sanitize text input (remove dangerous characters)
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential XSS characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def validate_tags(tags: List[str], max_count: int = 10, max_length: int = 50) -> bool:
    """
    Validate tags list
    
    Args:
        tags: List of tags
        max_count: Maximum number of tags (default: 10)
        max_length: Maximum length per tag (default: 50)
        
    Returns:
        True if valid, False otherwise
    """
    if len(tags) > max_count:
        return False
    
    return all(len(tag) <= max_length for tag in tags)
