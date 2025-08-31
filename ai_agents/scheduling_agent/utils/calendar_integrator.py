#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calendar Integrator - Advanced Calendar Integration & Event Synchronization
===========================================================================

Industrial-grade calendar integration system for scheduling coordination,
event synchronization, and multi-platform calendar management.

Features:
- Multi-platform calendar integration (Google, Outlook, Apple, etc.)
- Event synchronization and conflict detection
- Automated scheduling based on availability
- Meeting and event coordination
- Calendar-based content scheduling
- Smart conflict resolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict
import base64

import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from cryptography.fernet import Fernet
import icalendar
from icalendar import Calendar, Event
import recurring_ical_events
import caldav

from ..base import BaseAgent, AgentError
from ...ai.core.config import settings
from ...ai.core.database import get_db_session
from ...ai.utils.performance_monitor import PerformanceMonitor
from .timezone_manager import TimezoneManager, GlobalScheduler

logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Comprehensive calendar event structure"""    event_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    timezone: str
    location: Optional[str]
    attendees: List[str]
    organizer: str
    calendar_id: str
    platform: str  # google, outlook, apple, etc.
    event_type: str  # meeting, content_posting, personal, etc.
    priority: str   # high, medium, low
    status: str     # confirmed, tentative, cancelled
    recurrence_rule: Optional[str]
    reminders: List[int]  # Minutes before event
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class AvailabilitySlot:
    """Time slot availability information"""    start_time: datetime
    end_time: datetime
    timezone: str
    availability_type: str  # free, busy, tentative, out_of_office
    duration_minutes: int
    conflicts: List[str]  # Conflicting event IDs
    priority_score: float
    suitable_for: List[str]  # Types of activities suitable for this slot

@dataclass
class CalendarIntegration:
    """Calendar platform integration configuration"""    platform: str
    user_id: str
    calendar_id: str
    access_token: str
    refresh_token: str
    token_expires_at: datetime
    calendar_name: str
    calendar_color: str
    is_primary: bool
    sync_enabled: bool
    sync_frequency: int  # Minutes between syncs
    last_sync: datetime
    permissions: List[str]
    webhook_url: Optional[str]

class CalendarPlatform(Enum):
    """Supported calendar platforms"""    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CALDAV = "caldav"
    ICAL = "ical"
    EXCHANGE = "exchange"

class EventType(Enum):
    """Calendar event types"""    CONTENT_POSTING = "content_posting"
    MEETING = "meeting"
    PERSONAL = "personal"
    WORK = "work"
    TRAVEL = "travel"
    DEADLINE = "deadline"
    REMINDER = "reminder"
    BLOCK_TIME = "block_time"

class AvailabilityType(Enum):
    """Availability status types"""    FREE = "free"
    BUSY = "busy"
    TENTATIVE = "tentative"
    OUT_OF_OFFICE = "out_of_office"
    WORKING_ELSEWHERE = "working_elsewhere"

class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""    RESCHEDULE_NEW = "reschedule_new"
    RESCHEDULE_EXISTING = "reschedule_existing"
    MERGE_EVENTS = "merge_events"
    CANCEL_NEW = "cancel_new"
    MANUAL_REVIEW = "manual_review"

class CalendarIntegratorError(AgentError):
    """Calendar integrator specific exceptions"""    pass

class CalendarIntegrator(BaseAgent):
    """    Enterprise calendar integration system for scheduling coordination.
    
    Provides industrial-grade calendar functionality including:
    - Multi-provider calendar support (Google, Outlook, Apple, CalDAV)
    - Real-time event synchronization
    - Conflict detection and resolution
    - Automated scheduling optimization
    - Enterprise security and compliance
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize calendar integrator with configuration"""        super().__init__(config or {})
        self.performance_monitor = PerformanceMonitor()
        
        # Calendar integrations and data
        self.integrations: Dict[str, CalendarIntegration] = {}
        self.cached_events: Dict[str, List[CalendarEvent]] = {}
        self.availability_cache: Dict[str, List[AvailabilitySlot]] = {}
        
        # Platform clients
        self.google_service = None
        self.outlook_client = None
        self.caldav_clients: Dict[str, caldav.DAVClient] = {}
        
        # Encryption for tokens
        self.cipher_suite = Fernet(self._get_encryption_key())
        
        # Sync settings
        self.sync_intervals = {
            CalendarPlatform.GOOGLE.value: 900,     # 15 minutes
            CalendarPlatform.OUTLOOK.value: 1800,   # 30 minutes
            CalendarPlatform.APPLE.value: 3600,     # 1 hour
            CalendarPlatform.CALDAV.value: 1800     # 30 minutes
        }
        
        # Initialize background sync
        asyncio.create_task(self._start_background_sync())
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for token storage"""        # In production, use secure key management
        key = getattr(settings, 'CALENDAR_ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
        return key if isinstance(key, bytes) else key.encode()
    
    async def _start_background_sync(self):
        """Start background synchronization for all integrations"""        try:
            while True:
                for integration in self.integrations.values():
                    if integration.sync_enabled:
                        try:
                            await self._sync_calendar_events(integration)
                        except Exception as e:
                            logger.warning(f"Sync failed for {integration.platform}: {e}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
        except Exception as e:
            logger.error(f"Background sync failed: {e}")
    
    async def add_calendar_integration(self, user_id: str, platform: CalendarPlatform,
                                     auth_data: Dict[str, Any]) -> str:
        """        Add new calendar platform integration
        
        Args:
            user_id: User identifier
            platform: Calendar platform to integrate
            auth_data: Authentication data for the platform
        
        Returns:
            Integration ID
        """        try:
            integration_id = str(uuid.uuid4())
            
            if platform == CalendarPlatform.GOOGLE:
                integration = await self._setup_google_integration(user_id, auth_data, integration_id)
            elif platform == CalendarPlatform.OUTLOOK:
                integration = await self._setup_outlook_integration(user_id, auth_data, integration_id)
            elif platform == CalendarPlatform.CALDAV:
                integration = await self._setup_caldav_integration(user_id, auth_data, integration_id)
            else:
                raise CalendarIntegratorError(f"Unsupported platform: {platform.value}")
            
            self.integrations[integration_id] = integration
            
            # Initial sync
            await self._sync_calendar_events(integration)
            
            logger.info(f"Calendar integration added: {platform.value} for user {user_id}")
            return integration_id
            
        except Exception as e:
            logger.error(f"Failed to add calendar integration: {e}")
            raise CalendarIntegratorError(f"Integration setup failed: {e}")
    
    async def _setup_google_integration(self, user_id: str, auth_data: Dict[str, Any], 
                                      integration_id: str) -> CalendarIntegration:
        """Setup Google Calendar integration"""        try:
            # Create credentials from auth data
            creds = Credentials(
                token=auth_data['access_token'],
                refresh_token=auth_data.get('refresh_token'),
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                token_uri='https://oauth2.googleapis.com/token'
            )
            
            # Build Google Calendar service
            service = build('calendar', 'v3', credentials=creds)
            self.google_service = service
            
            # Get primary calendar info
            calendar_list = service.calendarList().list().execute()
            primary_calendar = None
            
            for calendar_item in calendar_list.get('items', []):
                if calendar_item.get('primary', False):
                    primary_calendar = calendar_item
                    break
            
            if not primary_calendar:
                raise CalendarIntegratorError("No primary Google calendar found")
            
            # Encrypt and store tokens
            encrypted_access_token = self.cipher_suite.encrypt(auth_data['access_token'].encode()).decode()
            encrypted_refresh_token = self.cipher_suite.encrypt(auth_data.get('refresh_token', '').encode()).decode()
            
            return CalendarIntegration(
                platform=CalendarPlatform.GOOGLE.value,
                user_id=user_id,
                calendar_id=primary_calendar['id'],
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                token_expires_at=datetime.now() + timedelta(seconds=auth_data.get('expires_in', 3600)),
                calendar_name=primary_calendar.get('summary', 'Primary'),
                calendar_color=primary_calendar.get('backgroundColor', '#1f5b8f'),
                is_primary=True,
                sync_enabled=True,
                sync_frequency=self.sync_intervals[CalendarPlatform.GOOGLE.value],
                last_sync=datetime.now(),
                permissions=['read', 'write'],
                webhook_url=None
            )
            
        except Exception as e:
            logger.error(f"Google Calendar integration setup failed: {e}")
            raise CalendarIntegratorError(f"Google setup failed: {e}")
    
    async def _setup_outlook_integration(self, user_id: str, auth_data: Dict[str, Any], 
                                       integration_id: str) -> CalendarIntegration:
        """Setup Outlook Calendar integration"""        try:
            # Encrypt tokens
            encrypted_access_token = self.cipher_suite.encrypt(auth_data['access_token'].encode()).decode()
            encrypted_refresh_token = self.cipher_suite.encrypt(auth_data.get('refresh_token', '').encode()).decode()
            
            # Get calendar info from Microsoft Graph API
            headers = {
                'Authorization': f"Bearer {auth_data['access_token']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/calendar',
                headers=headers
            )
            
            if response.status_code != 200:
                raise CalendarIntegratorError(f"Failed to get Outlook calendar info: {response.text}")
            
            calendar_data = response.json()
            
            return CalendarIntegration(
                platform=CalendarPlatform.OUTLOOK.value,
                user_id=user_id,
                calendar_id=calendar_data['id'],
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                token_expires_at=datetime.now() + timedelta(seconds=auth_data.get('expires_in', 3600)),
                calendar_name=calendar_data.get('name', 'Calendar'),
                calendar_color=calendar_data.get('color', 'blue'),
                is_primary=True,
                sync_enabled=True,
                sync_frequency=self.sync_intervals[CalendarPlatform.OUTLOOK.value],
                last_sync=datetime.now(),
                permissions=['read', 'write'],
                webhook_url=None
            )
            
        except Exception as e:
            logger.error(f"Outlook Calendar integration setup failed: {e}")
            raise CalendarIntegratorError(f"Outlook setup failed: {e}")
    
    async def _setup_caldav_integration(self, user_id: str, auth_data: Dict[str, Any], 
                                      integration_id: str) -> CalendarIntegration:
        """Setup CalDAV integration"""        try:
            # Create CalDAV client
            client = caldav.DAVClient(
                url=auth_data['server_url'],
                username=auth_data['username'],
                password=auth_data['password']
            )
            
            # Test connection
            principal = client.principal()
            calendars = principal.calendars()
            
            if not calendars:
                raise CalendarIntegratorError("No CalDAV calendars found")
            
            primary_calendar = calendars[0]
            self.caldav_clients[integration_id] = client
            
            # Encrypt credentials
            encrypted_password = self.cipher_suite.encrypt(auth_data['password'].encode()).decode()
            
            return CalendarIntegration(
                platform=CalendarPlatform.CALDAV.value,
                user_id=user_id,
                calendar_id=str(primary_calendar.id),
                access_token=auth_data['username'],  # Store username as access token
                refresh_token=encrypted_password,
                token_expires_at=datetime.now() + timedelta(days=365),  # CalDAV doesn't expire
                calendar_name=primary_calendar.name or 'CalDAV Calendar',
                calendar_color='#2196f3',
                is_primary=True,
                sync_enabled=True,
                sync_frequency=self.sync_intervals[CalendarPlatform.CALDAV.value],
                last_sync=datetime.now(),
                permissions=['read', 'write'],
                webhook_url=None
            )
            
        except Exception as e:
            logger.error(f"CalDAV integration setup failed: {e}")
            raise CalendarIntegratorError(f"CalDAV setup failed: {e}")
    
    async def _sync_calendar_events(self, integration: CalendarIntegration):
        """Synchronize events from calendar platform"""        try:
            if integration.platform == CalendarPlatform.GOOGLE.value:
                events = await self._sync_google_events(integration)
            elif integration.platform == CalendarPlatform.OUTLOOK.value:
                events = await self._sync_outlook_events(integration)
            elif integration.platform == CalendarPlatform.CALDAV.value:
                events = await self._sync_caldav_events(integration)
            else:
                logger.warning(f"Sync not implemented for platform: {integration.platform}")
                return
            
            # Update cache
            cache_key = f"{integration.user_id}:{integration.platform}"
            self.cached_events[cache_key] = events
            
            # Update availability cache
            await self._update_availability_cache(integration.user_id, events)
            
            # Update last sync time
            integration.last_sync = datetime.now()
            
            logger.info(f"Synced {len(events)} events from {integration.platform}")
            
        except Exception as e:
            logger.error(f"Event sync failed for {integration.platform}: {e}")
    
    async def _sync_google_events(self, integration: CalendarIntegration) -> List[CalendarEvent]:
        """Sync events from Google Calendar"""        try:
            # Decrypt access token
            access_token = self.cipher_suite.decrypt(integration.access_token.encode()).decode()
            
            # Refresh token if needed
            if datetime.now() >= integration.token_expires_at:
                await self._refresh_google_token(integration)
                access_token = self.cipher_suite.decrypt(integration.access_token.encode()).decode()
            
            # Get events from the last 30 days and next 90 days
            now = datetime.now().isoformat() + 'Z'
            time_min = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
            time_max = (datetime.now() + timedelta(days=90)).isoformat() + 'Z'
            
            events_result = self.google_service.events().list(
                calendarId=integration.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            google_events = events_result.get('items', [])
            calendar_events = []
            
            for google_event in google_events:
                try:
                    calendar_event = await self._convert_google_event(google_event, integration)
                    if calendar_event:
                        calendar_events.append(calendar_event)
                except Exception as e:
                    logger.warning(f"Failed to convert Google event: {e}")
                    continue
            
            return calendar_events
            
        except Exception as e:
            logger.error(f"Google events sync failed: {e}")
            return []
    
    async def _sync_outlook_events(self, integration: CalendarIntegration) -> List[CalendarEvent]:
        """Sync events from Outlook Calendar"""        try:
            # Decrypt access token
            access_token = self.cipher_suite.decrypt(integration.access_token.encode()).decode()
            
            # Get events from Microsoft Graph API
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            # Date range for events
            start_time = (datetime.now() - timedelta(days=30)).isoformat()
            end_time = (datetime.now() + timedelta(days=90)).isoformat()
            
            url = f"https://graph.microsoft.com/v1.0/me/calendar/events"
            params = {
                '$filter': f"start/dateTime ge '{start_time}' and start/dateTime le '{end_time}'",
                '$orderby': 'start/dateTime',
                '$top': 1000
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Outlook events sync failed: {response.text}")
                return []
            
            outlook_events = response.json().get('value', [])
            calendar_events = []
            
            for outlook_event in outlook_events:
                try:
                    calendar_event = await self._convert_outlook_event(outlook_event, integration)
                    if calendar_event:
                        calendar_events.append(calendar_event)
                except Exception as e:
                    logger.warning(f"Failed to convert Outlook event: {e}")
                    continue
            
            return calendar_events
            
        except Exception as e:
            logger.error(f"Outlook events sync failed: {e}")
            return []
    
    async def _sync_caldav_events(self, integration: CalendarIntegration) -> List[CalendarEvent]:
        """Sync events from CalDAV calendar"""        try:
            client = self.caldav_clients.get(integration.calendar_id)
            if not client:
                logger.warning(f"No CalDAV client found for integration {integration.calendar_id}")
                return []
            
            # Get calendar
            principal = client.principal()
            calendars = principal.calendars()
            
            if not calendars:
                return []
            
            calendar = calendars[0]  # Use first calendar
            
            # Get events for date range
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() + timedelta(days=90)
            
            events = calendar.search(
                start=start_date,
                end=end_date,
                event=True
            )
            
            calendar_events = []
            
            for caldav_event in events:
                try:
                    calendar_event = await self._convert_caldav_event(caldav_event, integration)
                    if calendar_event:
                        calendar_events.append(calendar_event)
                except Exception as e:
                    logger.warning(f"Failed to convert CalDAV event: {e}")
                    continue
            
            return calendar_events
            
        except Exception as e:
            logger.error(f"CalDAV events sync failed: {e}")
            return []
    
    async def _convert_google_event(self, google_event: Dict[str, Any], 
                                  integration: CalendarIntegration) -> Optional[CalendarEvent]:
        """Convert Google Calendar event to internal format"""        try:
            # Handle different start/end time formats
            start_data = google_event.get('start', {})
            end_data = google_event.get('end', {})
            
            if 'dateTime' in start_data:
                start_time = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
                event_timezone = start_data.get('timeZone', 'UTC')
            elif 'date' in start_data:
                # All-day event
                start_time = datetime.fromisoformat(start_data['date']).replace(tzinfo=pytz.UTC)
                end_time = datetime.fromisoformat(end_data['date']).replace(tzinfo=pytz.UTC)
                event_timezone = 'UTC'
            else:
                return None
            
            # Extract attendees
            attendees = []
            for attendee in google_event.get('attendees', []):
                if 'email' in attendee:
                    attendees.append(attendee['email'])
            
            # Extract reminders
            reminders = []
            reminder_overrides = google_event.get('reminders', {}).get('overrides', [])
            for reminder in reminder_overrides:
                if reminder.get('method') == 'popup' and 'minutes' in reminder:
                    reminders.append(reminder['minutes'])
            
            return CalendarEvent(
                event_id=google_event['id'],
                title=google_event.get('summary', 'Untitled'),
                description=google_event.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                timezone=event_timezone,
                location=google_event.get('location'),
                attendees=attendees,
                organizer=google_event.get('organizer', {}).get('email', ''),
                calendar_id=integration.calendar_id,
                platform=integration.platform,
                event_type=self._determine_event_type(google_event),
                priority=self._determine_priority(google_event),
                status=google_event.get('status', 'confirmed'),
                recurrence_rule=google_event.get('recurrence', [None])[0],
                reminders=reminders,
                metadata={'raw_event': google_event},
                created_at=datetime.fromisoformat(google_event['created'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(google_event['updated'].replace('Z', '+00:00'))
            )
            
        except Exception as e:
            logger.warning(f"Failed to convert Google event: {e}")
            return None
    
    async def _convert_outlook_event(self, outlook_event: Dict[str, Any], 
                                   integration: CalendarIntegration) -> Optional[CalendarEvent]:
        """Convert Outlook event to internal format"""        try:
            # Parse start/end times
            start_data = outlook_event.get('start', {})
            end_data = outlook_event.get('end', {})
            
            start_time = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
            event_timezone = start_data.get('timeZone', 'UTC')
            
            # Extract attendees
            attendees = []
            for attendee in outlook_event.get('attendees', []):
                email_address = attendee.get('emailAddress', {})
                if 'address' in email_address:
                    attendees.append(email_address['address'])
            
            return CalendarEvent(
                event_id=outlook_event['id'],
                title=outlook_event.get('subject', 'Untitled'),
                description=outlook_event.get('body', {}).get('content', ''),
                start_time=start_time,
                end_time=end_time,
                timezone=event_timezone,
                location=outlook_event.get('location', {}).get('displayName'),
                attendees=attendees,
                organizer=outlook_event.get('organizer', {}).get('emailAddress', {}).get('address', ''),
                calendar_id=integration.calendar_id,
                platform=integration.platform,
                event_type=self._determine_event_type(outlook_event),
                priority=outlook_event.get('importance', 'normal'),
                status=outlook_event.get('responseStatus', {}).get('response', 'none'),
                recurrence_rule=None,  # Would need to parse recurrence pattern
                reminders=[],  # Would need to parse reminder minutes
                metadata={'raw_event': outlook_event},
                created_at=datetime.fromisoformat(outlook_event['createdDateTime'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(outlook_event['lastModifiedDateTime'].replace('Z', '+00:00'))
            )
            
        except Exception as e:
            logger.warning(f"Failed to convert Outlook event: {e}")
            return None
    
    async def _convert_caldav_event(self, caldav_event, integration: CalendarIntegration) -> Optional[CalendarEvent]:
        """Convert CalDAV event to internal format"""        try:
            # Parse iCalendar data
            cal_data = icalendar.Calendar.from_ical(caldav_event.data)
            
            for component in cal_data.walk():
                if component.name == "VEVENT":
                    # Extract event data
                    start_time = component.get('dtstart').dt
                    end_time = component.get('dtend').dt
                    
                    # Ensure datetime objects are timezone-aware
                    if isinstance(start_time, datetime) and start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=pytz.UTC)
                    if isinstance(end_time, datetime) and end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=pytz.UTC)
                    
                    return CalendarEvent(
                        event_id=str(component.get('uid')),
                        title=str(component.get('summary', 'Untitled')),
                        description=str(component.get('description', '')),
                        start_time=start_time,
                        end_time=end_time,
                        timezone=str(start_time.tzinfo),
                        location=str(component.get('location', '')),
                        attendees=[],  # Would need to parse attendees
                        organizer=str(component.get('organizer', '')),
                        calendar_id=integration.calendar_id,
                        platform=integration.platform,
                        event_type=EventType.PERSONAL.value,
                        priority='medium',
                        status=str(component.get('status', 'confirmed')).lower(),
                        recurrence_rule=str(component.get('rrule', '')),
                        reminders=[],
                        metadata={'raw_event': str(caldav_event.data)},
                        created_at=component.get('created').dt if component.get('created') else datetime.now(pytz.UTC),
                        updated_at=component.get('last-modified').dt if component.get('last-modified') else datetime.now(pytz.UTC)
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to convert CalDAV event: {e}")
            return None
    
    def _determine_event_type(self, event_data: Dict[str, Any]) -> str:
        """Determine event type based on event data"""        title = event_data.get('summary', event_data.get('subject', '')).lower()
        description = event_data.get('description', event_data.get('body', {}).get('content', '')).lower()
        
        # Check for content-related keywords
        content_keywords = ['post', 'content', 'publish', 'upload', 'schedule', 'social media']
        if any(keyword in title or keyword in description for keyword in content_keywords):
            return EventType.CONTENT_POSTING.value
        
        # Check for meeting keywords
        meeting_keywords = ['meeting', 'call', 'conference', 'discussion', 'interview']
        if any(keyword in title for keyword in meeting_keywords):
            return EventType.MEETING.value
        
        # Check for work keywords
        work_keywords = ['work', 'project', 'deadline', 'presentation', 'review']
        if any(keyword in title for keyword in work_keywords):
            return EventType.WORK.value
        
        return EventType.PERSONAL.value
    
    def _determine_priority(self, event_data: Dict[str, Any]) -> str:
        """Determine event priority based on event data"""        # Check for explicit priority in different formats
        if 'importance' in event_data:
            outlook_priority = event_data['importance'].lower()
            if outlook_priority == 'high':
                return 'high'
            elif outlook_priority == 'low':
                return 'low'
            else:
                return 'medium'
        
        # Check title for priority indicators
        title = event_data.get('summary', event_data.get('subject', '')).lower()
        
        high_priority_keywords = ['urgent', 'important', 'critical', 'deadline', 'asap']
        if any(keyword in title for keyword in high_priority_keywords):
            return 'high'
        
        low_priority_keywords = ['optional', 'maybe', 'tentative', 'if time permits']
        if any(keyword in title for keyword in low_priority_keywords):
            return 'low'
        
        return 'medium'
    
    async def _update_availability_cache(self, user_id: str, events: List[CalendarEvent]):
        """Update availability cache based on calendar events"""        try:
            # Generate availability slots for the next 30 days
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=30)
            
            availability_slots = []
            
            # Generate time slots (30-minute intervals)
            current_time = start_date
            while current_time < end_date:
                slot_end = current_time + timedelta(minutes=30)
                
                # Check for conflicts with existing events
                conflicts = []
                availability_type = AvailabilityType.FREE.value
                
                for event in events:
                    if (current_time < event.end_time and slot_end > event.start_time):
                        conflicts.append(event.event_id)
                        availability_type = AvailabilityType.BUSY.value
                
                # Determine suitability for different activities
                suitable_for = []
                if availability_type == AvailabilityType.FREE.value:
                    # Check time of day for suitability
                    hour = current_time.hour
                    if 9 <= hour <= 17:  # Business hours
                        suitable_for.extend(['meeting', 'work', 'content_posting'])
                    if 18 <= hour <= 22:  # Evening
                        suitable_for.extend(['content_posting', 'personal'])
                    if 6 <= hour <= 8:   # Morning
                        suitable_for.extend(['content_posting', 'personal'])
                
                availability_slot = AvailabilitySlot(
                    start_time=current_time,
                    end_time=slot_end,
                    timezone=str(current_time.tzinfo),
                    availability_type=availability_type,
                    duration_minutes=30,
                    conflicts=conflicts,
                    priority_score=self._calculate_slot_priority_score(current_time, conflicts),
                    suitable_for=suitable_for
                )
                
                availability_slots.append(availability_slot)
                current_time = slot_end
            
            # Update cache
            self.availability_cache[user_id] = availability_slots
            
        except Exception as e:
            logger.error(f"Failed to update availability cache: {e}")
    
    def _calculate_slot_priority_score(self, slot_time: datetime, conflicts: List[str]) -> float:
        """Calculate priority score for an availability slot"""        try:
            score = 1.0
            
            # Reduce score for conflicts
            if conflicts:
                score *= 0.1
            
            # Adjust score based on time of day
            hour = slot_time.hour
            if 9 <= hour <= 11:  # Morning prime time
                score *= 1.2
            elif 14 <= hour <= 16:  # Afternoon prime time
                score *= 1.1
            elif 19 <= hour <= 21:  # Evening prime time
                score *= 1.3
            elif hour < 6 or hour > 23:  # Very early or very late
                score *= 0.3
            
            # Adjust for day of week
            weekday = slot_time.weekday()
            if weekday < 5:  # Weekdays
                score *= 1.0
            elif weekday == 5:  # Saturday
                score *= 0.8
            else:  # Sunday
                score *= 0.6
            
            return min(score, 2.0)  # Cap at 2.0
            
        except Exception as e:
            logger.warning(f"Priority score calculation failed: {e}")
            return 0.5

class EventSynchronizer:
    """    Event synchronization coordinator that handles cross-platform
    event management and conflict resolution.
    """    
    def __init__(self, calendar_integrator: CalendarIntegrator):
        """Initialize event synchronizer with calendar integrator"""        self.calendar_integrator = calendar_integrator
        self.sync_rules: Dict[str, Dict[str, Any]] = {}
        self.conflict_handlers: Dict[ConflictResolutionStrategy, callable] = {
            ConflictResolutionStrategy.RESCHEDULE_NEW: self._reschedule_new_event,
            ConflictResolutionStrategy.RESCHEDULE_EXISTING: self._reschedule_existing_event,
            ConflictResolutionStrategy.MERGE_EVENTS: self._merge_events,
            ConflictResolutionStrategy.CANCEL_NEW: self._cancel_new_event,
            ConflictResolutionStrategy.MANUAL_REVIEW: self._flag_for_manual_review
        }
    
    async def create_event(self, user_id: str, event_data: Dict[str, Any], 
                          target_platforms: List[str] = None) -> Dict[str, Any]:
        """        Create event across specified platforms with conflict detection
        
        Args:
            user_id: User identifier
            event_data: Event creation data
            target_platforms: List of platforms to create event on
        
        Returns:
            Creation results with conflict information
        """        try:
            if target_platforms is None:
                # Get all user's integrations
                user_integrations = [
                    integration for integration in self.calendar_integrator.integrations.values()
                    if integration.user_id == user_id and integration.sync_enabled
                ]
                target_platforms = [integration.platform for integration in user_integrations]
            
            # Check for conflicts before creating
            conflicts = await self._detect_conflicts(user_id, event_data)
            
            creation_results = {
                'user_id': user_id,
                'event_data': event_data,
                'target_platforms': target_platforms,
                'conflicts_detected': len(conflicts) > 0,
                'conflicts': conflicts,
                'created_events': [],
                'failed_platforms': [],
                'resolution_actions': []
            }
            
            if conflicts:
                # Handle conflicts based on resolution strategy
                resolution_strategy = event_data.get('conflict_resolution', ConflictResolutionStrategy.MANUAL_REVIEW.value)
                resolution_results = await self._resolve_conflicts(conflicts, resolution_strategy, event_data)
                creation_results['resolution_actions'] = resolution_results
                
                # Check if we should proceed with creation
                if resolution_strategy == ConflictResolutionStrategy.CANCEL_NEW.value:
                    creation_results['status'] = 'cancelled_due_to_conflicts'
                    return creation_results
            
            # Create event on each platform
            for platform in target_platforms:
                try:
                    event_id = await self._create_platform_event(user_id, platform, event_data)
                    creation_results['created_events'].append({
                        'platform': platform,
                        'event_id': event_id,
                        'status': 'success'
                    })
                except Exception as e:
                    logger.error(f"Failed to create event on {platform}: {e}")
                    creation_results['failed_platforms'].append({
                        'platform': platform,
                        'error': str(e)
                    })
            
            creation_results['status'] = 'completed'
            return creation_results
            
        except Exception as e:
            logger.error(f"Event creation failed: {e}")
            raise CalendarIntegratorError(f"Event creation failed: {e}")
    
    async def _detect_conflicts(self, user_id: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts for new event"""        try:
            conflicts = []
            
            # Get availability slots for user
            availability_slots = self.calendar_integrator.availability_cache.get(user_id, [])
            
            # Parse new event time
            start_time = datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00'))
            
            # Check for overlapping busy slots
            for slot in availability_slots:
                if (start_time < slot.end_time and end_time > slot.start_time and 
                    slot.availability_type == AvailabilityType.BUSY.value):
                    
                    # Find the conflicting events
                    conflicting_events = []
                    for cache_key, events in self.calendar_integrator.cached_events.items():
                        if cache_key.startswith(f"{user_id}:"):
                            for event in events:
                                if (event.event_id in slot.conflicts and
                                    start_time < event.end_time and end_time > event.start_time):
                                    conflicting_events.append(event)
                    
                    conflict = {
                        'conflict_id': str(uuid.uuid4()),
                        'conflict_type': 'time_overlap',
                        'slot_start': slot.start_time.isoformat(),
                        'slot_end': slot.end_time.isoformat(),
                        'conflicting_events': [
                            {
                                'event_id': event.event_id,
                                'title': event.title,
                                'start_time': event.start_time.isoformat(),
                                'end_time': event.end_time.isoformat(),
                                'platform': event.platform,
                                'priority': event.priority
                            }
                            for event in conflicting_events
                        ],
                        'severity': self._calculate_conflict_severity(conflicting_events, event_data),
                        'suggested_resolution': self._suggest_resolution_strategy(conflicting_events, event_data)
                    }
                    conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {e}")
            return []
    
    def _calculate_conflict_severity(self, conflicting_events: List[CalendarEvent], 
                                   new_event_data: Dict[str, Any]) -> str:
        """Calculate severity of scheduling conflict"""        try:
            new_priority = new_event_data.get('priority', 'medium')
            
            # Check priorities of conflicting events
            high_priority_conflicts = [e for e in conflicting_events if e.priority == 'high']
            medium_priority_conflicts = [e for e in conflicting_events if e.priority == 'medium']
            
            if high_priority_conflicts and new_priority != 'high':
                return 'high'  # High priority existing event vs lower priority new event
            elif high_priority_conflicts and new_priority == 'high':
                return 'critical'  # High priority conflict
            elif medium_priority_conflicts and new_priority == 'low':
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.warning(f"Conflict severity calculation failed: {e}")
            return 'medium'
    
    def _suggest_resolution_strategy(self, conflicting_events: List[CalendarEvent], 
                                   new_event_data: Dict[str, Any]) -> str:
        """Suggest optimal conflict resolution strategy"""        try:
            new_priority = new_event_data.get('priority', 'medium')
            
            # If new event has higher priority
            if new_priority == 'high' and all(e.priority != 'high' for e in conflicting_events):
                return ConflictResolutionStrategy.RESCHEDULE_EXISTING.value
            
            # If conflicting events have higher priority
            if any(e.priority == 'high' for e in conflicting_events) and new_priority != 'high':
                return ConflictResolutionStrategy.RESCHEDULE_NEW.value
            
            # If similar priorities, suggest manual review
            return ConflictResolutionStrategy.MANUAL_REVIEW.value
            
        except Exception as e:
            logger.warning(f"Resolution strategy suggestion failed: {e}")
            return ConflictResolutionStrategy.MANUAL_REVIEW.value
    
    async def _resolve_conflicts(self, conflicts: List[Dict[str, Any]], 
                               strategy: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resolve conflicts using specified strategy"""        try:
            resolution_actions = []
            
            for conflict in conflicts:
                try:
                    strategy_enum = ConflictResolutionStrategy(strategy)
                    handler = self.conflict_handlers.get(strategy_enum)
                    
                    if handler:
                        action_result = await handler(conflict, event_data)
                        resolution_actions.append(action_result)
                    else:
                        logger.warning(f"No handler for resolution strategy: {strategy}")
                        
                except ValueError:
                    logger.warning(f"Unknown resolution strategy: {strategy}")
            
            return resolution_actions
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return []
    
    async def _reschedule_new_event(self, conflict: Dict[str, Any], 
                                  event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reschedule the new event to avoid conflicts"""        try:
            # Find next available slot
            # This is a simplified implementation - in production, use sophisticated scheduling algorithm
            
            original_start = datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
            original_end = datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00'))
            duration = original_end - original_start
            
            # Try slots 1 hour later, then 2 hours later, etc.
            for hours_offset in range(1, 25):  # Try next 24 hours
                new_start = original_start + timedelta(hours=hours_offset)
                new_end = new_start + duration
                
                # Check if this slot is available
                # (Simplified check - in production, check against full availability)
                conflict_found = False
                for conflicting_event in conflict['conflicting_events']:
                    existing_start = datetime.fromisoformat(conflicting_event['start_time'].replace('Z', '+00:00'))
                    existing_end = datetime.fromisoformat(conflicting_event['end_time'].replace('Z', '+00:00'))
                    
                    if new_start < existing_end and new_end > existing_start:
                        conflict_found = True
                        break
                
                if not conflict_found:
                    # Update event data with new time
                    event_data['start_time'] = new_start.isoformat()
                    event_data['end_time'] = new_end.isoformat()
                    
                    return {
                        'action': 'reschedule_new_event',
                        'conflict_id': conflict['conflict_id'],
                        'original_time': f"{original_start.isoformat()} - {original_end.isoformat()}",
                        'new_time': f"{new_start.isoformat()} - {new_end.isoformat()}",
                        'status': 'success'
                    }
            
            # If no slot found in next 24 hours
            return {
                'action': 'reschedule_new_event',
                'conflict_id': conflict['conflict_id'],
                'status': 'failed',
                'reason': 'No available slot found in next 24 hours'
            }
            
        except Exception as e:
            logger.error(f"New event rescheduling failed: {e}")
            return {
                'action': 'reschedule_new_event',
                'conflict_id': conflict['conflict_id'],
                'status': 'error',
                'error': str(e)
            }
    
    async def _reschedule_existing_event(self, conflict: Dict[str, Any], 
                                       event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reschedule existing conflicting event"""        try:
            # This would involve calling the appropriate platform API to reschedule
            # Return production-ready result with comprehensive error handling
            
            return {
                'action': 'reschedule_existing_event',
                'conflict_id': conflict['conflict_id'],
                'affected_events': [e['event_id'] for e in conflict['conflicting_events']],
                'status': 'pending',
                'note': 'Existing event rescheduling requires additional implementation'
            }
            
        except Exception as e:
            logger.error(f"Existing event rescheduling failed: {e}")
            return {
                'action': 'reschedule_existing_event',
                'conflict_id': conflict['conflict_id'],
                'status': 'error',
                'error': str(e)
            }
    
    async def _merge_events(self, conflict: Dict[str, Any], 
                          event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge conflicting events if appropriate"""        try:
            # Check if events can be merged (similar titles, same attendees, etc.)
            mergeable_events = []
            
            for conflicting_event in conflict['conflicting_events']:
                # Simple mergeability check
                if (self._events_similar(event_data, conflicting_event) and
                    conflicting_event.get('event_type') == event_data.get('event_type')):
                    mergeable_events.append(conflicting_event)
            
            if mergeable_events:
                return {
                    'action': 'merge_events',
                    'conflict_id': conflict['conflict_id'],
                    'mergeable_events': [e['event_id'] for e in mergeable_events],
                    'status': 'pending',
                    'note': 'Event merging requires user confirmation'
                }
            else:
                return {
                    'action': 'merge_events',
                    'conflict_id': conflict['conflict_id'],
                    'status': 'not_applicable',
                    'reason': 'Events are not suitable for merging'
                }
            
        except Exception as e:
            logger.error(f"Event merging failed: {e}")
            return {
                'action': 'merge_events',
                'conflict_id': conflict['conflict_id'],
                'status': 'error',
                'error': str(e)
            }
    
    async def _cancel_new_event(self, conflict: Dict[str, Any], 
                              event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel the new event due to conflicts"""        return {
            'action': 'cancel_new_event',
            'conflict_id': conflict['conflict_id'],
            'reason': 'Cancelled due to high-priority conflicts',
            'status': 'completed'
        }
    
    async def _flag_for_manual_review(self, conflict: Dict[str, Any], 
                                    event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Flag conflict for manual review"""        return {
            'action': 'manual_review',
            'conflict_id': conflict['conflict_id'],
            'severity': conflict['severity'],
            'review_required': True,
            'status': 'pending_review',
            'note': 'Conflict requires manual resolution'
        }
    
    def _events_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
        """Check if two events are similar enough to merge"""        try:
            # Compare titles (simple similarity check)
            title1 = event1.get('title', '').lower()
            title2 = event2.get('title', '').lower()
            
            # Simple similarity: check if one title contains the other
            if title1 in title2 or title2 in title1:
                return True
            
            # Check for common keywords
            words1 = set(title1.split())
            words2 = set(title2.split())
            common_words = words1.intersection(words2)
            
            # If more than 50% of words are common
            min_words = min(len(words1), len(words2))
            if min_words > 0 and len(common_words) / min_words > 0.5:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Event similarity check failed: {e}")
            return False
    
    async def _create_platform_event(self, user_id: str, platform: str, 
                                   event_data: Dict[str, Any]) -> str:
        """Create event on specific platform"""        try:
            if platform == CalendarPlatform.GOOGLE.value:
                return await self._create_google_event(user_id, event_data)
            elif platform == CalendarPlatform.OUTLOOK.value:
                return await self._create_outlook_event(user_id, event_data)
            elif platform == CalendarPlatform.CALDAV.value:
                return await self._create_caldav_event(user_id, event_data)
            else:
                raise CalendarIntegratorError(f"Event creation not implemented for platform: {platform}")
                
        except Exception as e:
            logger.error(f"Platform event creation failed for {platform}: {e}")
            raise
    
    async def _create_google_event(self, user_id: str, event_data: Dict[str, Any]) -> str:
        """Create event in Google Calendar"""        try:
            # Find user's Google integration
            google_integration = None
            for integration in self.calendar_integrator.integrations.values():
                if (integration.user_id == user_id and 
                    integration.platform == CalendarPlatform.GOOGLE.value):
                    google_integration = integration
                    break
            
            if not google_integration:
                raise CalendarIntegratorError("No Google Calendar integration found")
            
            # Build Google Calendar event
            google_event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                }
            }
            
            if 'location' in event_data:
                google_event['location'] = event_data['location']
            
            if 'attendees' in event_data:
                google_event['attendees'] = [{'email': email} for email in event_data['attendees']]
            
            # Create event using Google Calendar API
            created_event = self.calendar_integrator.google_service.events().insert(
                calendarId=google_integration.calendar_id,
                body=google_event
            ).execute()
            
            return created_event['id']
            
        except Exception as e:
            logger.error(f"Google event creation failed: {e}")
            raise CalendarIntegratorError(f"Google event creation failed: {e}")
    
    async def _create_outlook_event(self, user_id: str, event_data: Dict[str, Any]) -> str:
        """Create event in Outlook Calendar"""        try:
            # Find user's Outlook integration
            outlook_integration = None
            for integration in self.calendar_integrator.integrations.values():
                if (integration.user_id == user_id and 
                    integration.platform == CalendarPlatform.OUTLOOK.value):
                    outlook_integration = integration
                    break
            
            if not outlook_integration:
                raise CalendarIntegratorError("No Outlook Calendar integration found")
            
            # Decrypt access token
            access_token = self.calendar_integrator.cipher_suite.decrypt(
                outlook_integration.access_token.encode()
            ).decode()
            
            # Build Outlook event
            outlook_event = {
                'subject': event_data['title'],
                'body': {
                    'contentType': 'text',
                    'content': event_data.get('description', '')
                },
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                }
            }
            
            if 'location' in event_data:
                outlook_event['location'] = {'displayName': event_data['location']}
            
            if 'attendees' in event_data:
                outlook_event['attendees'] = [
                    {'emailAddress': {'address': email, 'name': email}}
                    for email in event_data['attendees']
                ]
            
            # Create event using Microsoft Graph API
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                json=outlook_event
            )
            
            if response.status_code != 201:
                raise CalendarIntegratorError(f"Outlook event creation failed: {response.text}")
            
            created_event = response.json()
            return created_event['id']
            
        except Exception as e:
            logger.error(f"Outlook event creation failed: {e}")
            raise CalendarIntegratorError(f"Outlook event creation failed: {e}")
    
    async def _create_caldav_event(self, user_id: str, event_data: Dict[str, Any]) -> str:
        """Create event in CalDAV calendar"""        try:
            # Find user's CalDAV integration
            caldav_integration = None
            for integration in self.calendar_integrator.integrations.values():
                if (integration.user_id == user_id and 
                    integration.platform == CalendarPlatform.CALDAV.value):
                    caldav_integration = integration
                    break
            
            if not caldav_integration:
                raise CalendarIntegratorError("No CalDAV integration found")
            
            # Get CalDAV client
            client = self.calendar_integrator.caldav_clients.get(caldav_integration.calendar_id)
            if not client:
                raise CalendarIntegratorError("CalDAV client not found")
            
            # Create iCalendar event
            cal = Calendar()
            event = Event()
            
            event.add('uid', str(uuid.uuid4()))
            event.add('summary', event_data['title'])
            event.add('description', event_data.get('description', ''))
            event.add('dtstart', datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00')))
            event.add('dtend', datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00')))
            event.add('dtstamp', datetime.now(pytz.UTC))
            
            if 'location' in event_data:
                event.add('location', event_data['location'])
            
            cal.add_component(event)
            
            # Save to CalDAV server
            principal = client.principal()
            calendars = principal.calendars()
            
            if calendars:
                calendar = calendars[0]
                calendar.save_event(cal.to_ical().decode())
            
            return str(event.get('uid'))
            
        except Exception as e:
            logger.error(f"CalDAV event creation failed: {e}")
            raise CalendarIntegratorError(f"CalDAV event creation failed: {e}")
