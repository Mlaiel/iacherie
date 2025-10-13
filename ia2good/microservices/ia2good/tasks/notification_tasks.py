"""
Celery tasks for notifications in IA2GOOD module
"""
import os
import sys
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from celery import Task
from .celery_app import celery_app

# Add shared-services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from shared_services.notifications.push_service import PushNotificationService
    from shared_services.notifications.sms_service import SMSService
    from shared_services.notifications.email_service import EmailService
except ImportError:
    # Fallback for development
    print("Warning: Could not import shared notification services")
    PushNotificationService = None
    SMSService = None
    EmailService = None


class NotificationTask(Task):
    """Base task with notification service setup"""
    _push_service = None
    _sms_service = None
    _email_service = None
    
    @property
    def push_service(self):
        if self._push_service is None and PushNotificationService:
            self._push_service = PushNotificationService()
        return self._push_service
    
    @property
    def sms_service(self):
        if self._sms_service is None and SMSService:
            self._sms_service = SMSService()
        return self._sms_service
    
    @property
    def email_service(self):
        if self._email_service is None and EmailService:
            self._email_service = EmailService()
        return self._email_service


@celery_app.task(base=NotificationTask, bind=True, max_retries=3)
def notify_volunteers_nearby(
    self,
    case_id: str,
    case_title: str,
    case_type: str,
    urgency_level: int,
    location: Dict[str, float],
    volunteer_ids: List[str]
) -> Dict[str, Any]:
    """
    Notify nearby volunteers about a new case
    
    Args:
        case_id: UUID of the case
        case_title: Title of the case
        case_type: Type of case (homeless, animal, emergency)
        urgency_level: Urgency level (1-10)
        location: Dict with lat/lng
        volunteer_ids: List of volunteer UUIDs to notify
        
    Returns:
        Dict with notification results
    """
    try:
        title = f"🆘 Nouveau cas {case_type.upper()}"
        
        # Adjust message based on urgency
        if urgency_level >= 8:
            body = f"⚠️ URGENT ({urgency_level}/10) - {case_title}"
        else:
            body = f"Nouveau cas ({urgency_level}/10) - {case_title}"
        
        # Data payload for mobile app
        data = {
            'type': 'new_case',
            'case_id': case_id,
            'case_type': case_type,
            'urgency_level': str(urgency_level),
            'action_url': f'/ia2good/cases/{case_id}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send push notifications
        results = {
            'push_sent': 0,
            'push_failed': 0,
            'sms_sent': 0,
            'email_sent': 0,
            'total_volunteers': len(volunteer_ids)
        }
        
        # For high urgency cases, also send SMS
        send_sms = urgency_level >= 8
        
        for volunteer_id in volunteer_ids:
            # TODO: Fetch volunteer device tokens and contact info from DB
            # For now, simulate notification
            
            # Push notification
            try:
                if self.push_service:
                    # In production, fetch actual device token
                    device_token = f"volunteer_{volunteer_id}_token"
                    # Note: This is async in production
                    success = True  # Simulated
                    if success:
                        results['push_sent'] += 1
                    else:
                        results['push_failed'] += 1
            except Exception as e:
                print(f"Error sending push to volunteer {volunteer_id}: {e}")
                results['push_failed'] += 1
            
            # SMS for urgent cases
            if send_sms and self.sms_service:
                try:
                    # In production, fetch actual phone number
                    phone_number = f"+33600000{volunteer_id[:3]}"  # Simulated
                    sms_body = f"{title}: {body}. Voir app IA2GOOD"
                    # success = await self.sms_service.send_sms(phone_number, sms_body)
                    results['sms_sent'] += 1
                except Exception as e:
                    print(f"Error sending SMS to volunteer {volunteer_id}: {e}")
        
        print(f"Notified {results['push_sent']} volunteers about case {case_id}")
        return results
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=NotificationTask, bind=True, max_retries=2)
def notify_assignment_accepted(
    self,
    assignment_id: str,
    case_id: str,
    case_title: str,
    volunteer_name: str,
    reporter_id: str,
    estimated_arrival_minutes: int = None
) -> bool:
    """
    Notify reporter that a volunteer has accepted their case
    
    Args:
        assignment_id: UUID of the assignment
        case_id: UUID of the case
        case_title: Title of the case
        volunteer_name: Name of the volunteer
        reporter_id: UUID of the reporter
        estimated_arrival_minutes: ETA in minutes
        
    Returns:
        True if notification sent successfully
    """
    try:
        title = "✅ Volontaire en route !"
        
        if estimated_arrival_minutes:
            body = f"{volunteer_name} a accepté votre cas '{case_title}'. Arrivée prévue dans {estimated_arrival_minutes} min."
        else:
            body = f"{volunteer_name} a accepté de prendre en charge votre cas '{case_title}'."
        
        data = {
            'type': 'assignment_accepted',
            'assignment_id': assignment_id,
            'case_id': case_id,
            'volunteer_name': volunteer_name,
            'action_url': f'/ia2good/cases/{case_id}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send push notification to reporter
        if self.push_service:
            # TODO: Fetch reporter device token from DB
            device_token = f"reporter_{reporter_id}_token"
            # success = await self.push_service.send_push_notification(device_token, title, body, data, priority="high")
            print(f"Notified reporter {reporter_id} about accepted assignment {assignment_id}")
        
        # Send email notification
        if self.email_service:
            # TODO: Fetch reporter email from DB
            email = f"reporter_{reporter_id}@example.com"
            # success = await self.email_service.send_email(email, title, body)
            print(f"Sent email to reporter {reporter_id}")
        
        return True
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@celery_app.task(base=NotificationTask, bind=True)
def notify_case_completed(
    self,
    case_id: str,
    case_title: str,
    volunteer_name: str,
    reporter_id: str,
    completion_notes: str = None
) -> bool:
    """
    Notify reporter that case has been completed
    
    Args:
        case_id: UUID of the case
        case_title: Title of the case
        volunteer_name: Name of the volunteer who completed it
        reporter_id: UUID of the reporter
        completion_notes: Optional completion notes
        
    Returns:
        True if notification sent successfully
    """
    try:
        title = "🎉 Cas résolu !"
        body = f"{volunteer_name} a marqué votre cas '{case_title}' comme complété."
        
        if completion_notes:
            body += f"\n\nNotes: {completion_notes[:100]}"
        
        body += "\n\nMerci de noter l'intervention."
        
        data = {
            'type': 'case_completed',
            'case_id': case_id,
            'volunteer_name': volunteer_name,
            'action_url': f'/ia2good/cases/{case_id}/rate',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send push notification
        if self.push_service:
            device_token = f"reporter_{reporter_id}_token"
            # success = await self.push_service.send_push_notification(device_token, title, body, data, priority="high")
            print(f"Notified reporter {reporter_id} about completed case {case_id}")
        
        # Send email with rating link
        if self.email_service:
            email = f"reporter_{reporter_id}@example.com"
            email_body = f"""
            <h2>{title}</h2>
            <p>{body}</p>
            <p><a href="https://ia2good.com/cases/{case_id}/rate">Noter l'intervention</a></p>
            """
            # success = await self.email_service.send_html_email(email, title, email_body)
            print(f"Sent completion email to reporter {reporter_id}")
        
        return True
        
    except Exception as exc:
        print(f"Error sending completion notification: {exc}")
        return False


@celery_app.task(base=NotificationTask, bind=True)
def notify_rating_request(
    self,
    assignment_id: str,
    case_id: str,
    case_title: str,
    volunteer_id: str,
    rater_id: str,
    rater_type: str
) -> bool:
    """
    Request rating for an assignment
    
    Args:
        assignment_id: UUID of the assignment
        case_id: UUID of the case
        case_title: Title of the case
        volunteer_id: UUID of the volunteer
        rater_id: UUID of the person who should rate
        rater_type: 'reporter' or 'volunteer'
        
    Returns:
        True if notification sent successfully
    """
    try:
        if rater_type == 'reporter':
            title = "⭐ Noter l'intervention"
            body = f"Merci de noter l'intervention pour le cas '{case_title}'"
        else:  # volunteer
            title = "⭐ Noter le signalement"
            body = f"Merci de noter votre expérience pour le cas '{case_title}'"
        
        data = {
            'type': 'rating_request',
            'assignment_id': assignment_id,
            'case_id': case_id,
            'action_url': f'/ia2good/assignments/{assignment_id}/rate',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send push notification
        if self.push_service:
            device_token = f"{rater_type}_{rater_id}_token"
            # success = await self.push_service.send_push_notification(device_token, title, body, data)
            print(f"Sent rating request to {rater_type} {rater_id}")
        
        return True
        
    except Exception as exc:
        print(f"Error sending rating request: {exc}")
        return False


@celery_app.task(base=NotificationTask, bind=True)
def notify_case_cancelled(
    self,
    case_id: str,
    case_title: str,
    volunteer_ids: List[str],
    reason: str = None
) -> Dict[str, int]:
    """
    Notify volunteers that a case has been cancelled
    
    Args:
        case_id: UUID of the case
        case_title: Title of the case
        volunteer_ids: List of volunteer UUIDs to notify
        reason: Optional cancellation reason
        
    Returns:
        Dict with notification results
    """
    try:
        title = "❌ Cas annulé"
        body = f"Le cas '{case_title}' a été annulé."
        
        if reason:
            body += f"\n\nRaison: {reason}"
        
        data = {
            'type': 'case_cancelled',
            'case_id': case_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        results = {'sent': 0, 'failed': 0}
        
        for volunteer_id in volunteer_ids:
            try:
                if self.push_service:
                    device_token = f"volunteer_{volunteer_id}_token"
                    # success = await self.push_service.send_push_notification(device_token, title, body, data)
                    results['sent'] += 1
            except Exception as e:
                print(f"Error notifying volunteer {volunteer_id}: {e}")
                results['failed'] += 1
        
        print(f"Notified {results['sent']} volunteers about cancelled case {case_id}")
        return results
        
    except Exception as exc:
        print(f"Error sending cancellation notifications: {exc}")
        return {'sent': 0, 'failed': len(volunteer_ids)}


@celery_app.task(bind=True)
def cleanup_old_notifications(self) -> Dict[str, int]:
    """
    Clean up old read notifications (> 30 days)
    
    Returns:
        Dict with cleanup statistics
    """
    try:
        # TODO: Connect to database and delete old notifications
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # DELETE FROM notifications 
        # WHERE read = true 
        # AND read_at < cutoff_date
        
        deleted_count = 0  # Simulated
        
        print(f"Cleaned up {deleted_count} old notifications")
        return {'deleted': deleted_count, 'cutoff_date': cutoff_date.isoformat()}
        
    except Exception as exc:
        print(f"Error cleaning up notifications: {exc}")
        return {'deleted': 0, 'error': str(exc)}
