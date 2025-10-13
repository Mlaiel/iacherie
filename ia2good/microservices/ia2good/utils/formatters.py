"""Formatting utilities for IA2GOOD module"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string
    
    Args:
        dt: Datetime object
        format_str: Format string (default: ISO-like format)
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""
    return dt.strftime(format_str)


def format_time_ago(dt: datetime) -> str:
    """
    Format datetime as "time ago" (e.g., "2 hours ago")
    
    Args:
        dt: Datetime object
        
    Returns:
        Human-readable time ago string
    """
    if not dt:
        return "Unknown"
    
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} secondes"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} heure{'s' if hours > 1 else ''}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} jour{'s' if days > 1 else ''}"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} semaine{'s' if weeks > 1 else ''}"
    else:
        months = int(seconds / 2592000)
        return f"{months} mois"


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to readable string
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration (e.g., "2h 30min")
    """
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}min"


def format_distance(distance_km: float) -> str:
    """
    Format distance to readable string
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        Formatted distance (e.g., "1.5 km" or "500 m")
    """
    if distance_km < 1:
        meters = int(distance_km * 1000)
        return f"{meters} m"
    return f"{distance_km:.1f} km"


def format_score(score: float, max_score: float = 100.0) -> str:
    """
    Format score as percentage
    
    Args:
        score: Score value
        max_score: Maximum possible score (default: 100)
        
    Returns:
        Formatted score (e.g., "85.5%")
    """
    percentage = (score / max_score) * 100
    return f"{percentage:.1f}%"


def format_phone_number(phone: str) -> str:
    """
    Format phone number to French standard
    
    Args:
        phone: Raw phone number
        
    Returns:
        Formatted phone number (e.g., "06 12 34 56 78")
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # If starts with 33, replace with 0
    if digits.startswith('33'):
        digits = '0' + digits[2:]
    
    # Format as XX XX XX XX XX
    if len(digits) == 10:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"
    
    return phone  # Return as-is if can't format


def format_address(address: Optional[str], city: Optional[str], country: str = "France") -> str:
    """
    Format full address
    
    Args:
        address: Street address
        city: City name
        country: Country name (default: France)
        
    Returns:
        Formatted address
    """
    parts = []
    if address:
        parts.append(address)
    if city:
        parts.append(city)
    if country:
        parts.append(country)
    
    return ", ".join(parts)


def format_case_type(case_type: str) -> str:
    """
    Format case type to display name
    
    Args:
        case_type: Case type code
        
    Returns:
        Display name
    """
    type_names = {
        'homeless': 'Sans-abri',
        'animal': 'Aide animale',
        'emergency': 'Urgence',
        'other': 'Autre'
    }
    return type_names.get(case_type, case_type.capitalize())


def format_case_status(status: str) -> str:
    """
    Format case status to display name
    
    Args:
        status: Status code
        
    Returns:
        Display name
    """
    status_names = {
        'open': 'Ouvert',
        'claimed': 'Attribué',
        'in_progress': 'En cours',
        'completed': 'Terminé',
        'cancelled': 'Annulé'
    }
    return status_names.get(status, status.capitalize())


def format_list(items: list, separator: str = ", ", max_items: int = 3) -> str:
    """
    Format list to readable string with limit
    
    Args:
        items: List of items
        separator: Separator between items (default: ", ")
        max_items: Maximum items to display (default: 3)
        
    Returns:
        Formatted string (e.g., "item1, item2, item3 +2")
    """
    if not items:
        return ""
    
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    
    displayed = separator.join(str(item) for item in items[:max_items])
    remaining = len(items) - max_items
    return f"{displayed} +{remaining}"


def format_uuid_short(uuid: UUID) -> str:
    """
    Format UUID to short version (first 8 chars)
    
    Args:
        uuid: UUID object
        
    Returns:
        Short UUID string
    """
    return str(uuid)[:8]


def format_json_summary(data: Dict[str, Any], max_length: int = 100) -> str:
    """
    Format JSON data as summary string
    
    Args:
        data: Dictionary data
        max_length: Maximum length of summary
        
    Returns:
        Summary string
    """
    import json
    
    summary = json.dumps(data, ensure_ascii=False)
    if len(summary) > max_length:
        return summary[:max_length-3] + "..."
    return summary
