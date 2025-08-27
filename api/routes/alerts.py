"""
Alerts API Routes
Real-time alerting and notification system endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import json

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monitoring.alerts.notification_manager import NotificationManager
from ...monitoring.alerts.escalation_system import EscalationSystem
from ...integrations.services.sendgrid_integration import SendGridIntegration
from ...integrations.services.twilio_integration import TwilioIntegration


# Enums
class AlertType(str, Enum):
    VIOLATION_DETECTED = "violation_detected"
    COPYRIGHT_CLAIM = "copyright_claim"
    REVENUE_MILESTONE = "revenue_milestone"
    COLLABORATION_REQUEST = "collaboration_request"
    SYSTEM_ALERT = "system_alert"
    SECURITY_ALERT = "security_alert"
    PROCESSING_COMPLETE = "processing_complete"
    ACCOUNT_UPDATE = "account_update"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class AlertStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DISMISSED = "dismissed"
    FAILED = "failed"


# Pydantic models
class AlertRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    alert_type: AlertType
    severity: AlertSeverity = Field(default=AlertSeverity.MEDIUM)
    conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    enabled: bool = Field(default=True)
    throttle_minutes: int = Field(default=60, ge=0, le=1440)
    escalation_rules: Optional[List[Dict[str, Any]]] = None
    custom_message_template: Optional[str] = None


class Alert(BaseModel):
    alert_id: str
    user_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metadata: Dict[str, Any]
    status: AlertStatus
    channels_sent: List[str]
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None


class NotificationPreferences(BaseModel):
    user_id: str
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    slack_enabled: bool = Field(default=False)
    webhook_enabled: bool = Field(default=False)
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    custom_webhook_url: Optional[str] = None
    quiet_hours: Optional[Dict[str, str]] = None
    alert_frequency: str = Field(default="immediate", regex="^(immediate|hourly|daily|weekly)$")


class ManualAlert(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    channels: List[NotificationChannel]
    target_users: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    schedule_at: Optional[datetime] = None


class AlertStatistics(BaseModel):
    total_alerts: int
    alerts_by_type: Dict[str, int]
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    response_times: Dict[str, float]
    delivery_rates: Dict[str, float]
    period: str


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize alert components
notification_manager = NotificationManager()
escalation_system = EscalationSystem()
sendgrid_integration = SendGridIntegration()
twilio_integration = TwilioIntegration()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/rules", response_model=Dict[str, str])
async def create_alert_rule(
    rule: AlertRule,
    user: dict = Depends(get_current_user)
):
    """Create a new alert rule"""
    try:
        # Validate conditions based on alert type
        if not _validate_alert_conditions(rule.alert_type, rule.conditions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conditions for alert type"
            )
        
        # Create alert rule
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO alert_rules (rule_id, user_id, name, description, alert_type,
                                       severity, conditions, channels, enabled, throttle_minutes,
                                       escalation_rules, custom_message_template, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                rule.rule_id, user['user_id'], rule.name, rule.description,
                rule.alert_type.value, rule.severity.value, rule.conditions,
                [ch.value for ch in rule.channels], rule.enabled, rule.throttle_minutes,
                rule.escalation_rules, rule.custom_message_template, datetime.utcnow()
            ))
            await session.commit()
        
        # Register rule with monitoring system
        await notification_manager.register_alert_rule(rule.rule_id, rule)
        
        logger.info(f"Alert rule created: {rule.rule_id} by user {user['user_id']}")
        
        return {
            "rule_id": rule.rule_id,
            "message": "Alert rule created successfully",
            "status": "enabled" if rule.enabled else "disabled"
        }
        
    except Exception as e:
        logger.error(f"Create alert rule failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert rule"
        )


@router.get("/rules", response_model=List[Dict[str, Any]])
async def get_alert_rules(
    alert_type: Optional[AlertType] = None,
    enabled: Optional[bool] = None,
    user: dict = Depends(get_current_user)
):
    """Get user's alert rules"""
    try:
        query = """
            SELECT rule_id, name, description, alert_type, severity, conditions,
                   channels, enabled, throttle_minutes, escalation_rules,
                   custom_message_template, created_at, updated_at
            FROM alert_rules
            WHERE user_id = %s
        """
        params = [user['user_id']]
        
        if alert_type:
            query += " AND alert_type = %s"
            params.append(alert_type.value)
        
        if enabled is not None:
            query += " AND enabled = %s"
            params.append(enabled)
            
        query += " ORDER BY created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            rules = result.fetchall()
        
        rule_list = []
        for rule in rules:
            rule_list.append({
                "rule_id": rule[0],
                "name": rule[1],
                "description": rule[2],
                "alert_type": rule[3],
                "severity": rule[4],
                "conditions": rule[5],
                "channels": rule[6],
                "enabled": rule[7],
                "throttle_minutes": rule[8],
                "escalation_rules": rule[9],
                "custom_message_template": rule[10],
                "created_at": rule[11],
                "updated_at": rule[12]
            })
        
        return rule_list
        
    except Exception as e:
        logger.error(f"Get alert rules failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert rules"
        )


@router.put("/rules/{rule_id}", response_model=Dict[str, str])
async def update_alert_rule(
    rule_id: str,
    rule_update: AlertRule,
    user: dict = Depends(get_current_user)
):
    """Update an alert rule"""
    try:
        # Verify rule ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT rule_id FROM alert_rules
                WHERE rule_id = %s AND user_id = %s
            """, (rule_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert rule not found or access denied"
                )
            
            # Update rule
            await session.execute("""
                UPDATE alert_rules 
                SET name = %s, description = %s, alert_type = %s, severity = %s,
                    conditions = %s, channels = %s, enabled = %s, throttle_minutes = %s,
                    escalation_rules = %s, custom_message_template = %s, updated_at = %s
                WHERE rule_id = %s
            """, (
                rule_update.name, rule_update.description, rule_update.alert_type.value,
                rule_update.severity.value, rule_update.conditions,
                [ch.value for ch in rule_update.channels], rule_update.enabled,
                rule_update.throttle_minutes, rule_update.escalation_rules,
                rule_update.custom_message_template, datetime.utcnow(), rule_id
            ))
            await session.commit()
        
        # Update rule in monitoring system
        await notification_manager.update_alert_rule(rule_id, rule_update)
        
        logger.info(f"Alert rule updated: {rule_id}")
        
        return {
            "rule_id": rule_id,
            "message": "Alert rule updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Update alert rule failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert rule"
        )


@router.post("/send", response_model=Dict[str, str])
async def send_manual_alert(
    alert: ManualAlert,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Send a manual alert"""
    try:
        alert_id = str(uuid.uuid4())
        
        # Determine target users
        target_users = alert.target_users or [user['user_id']]
        
        # Validate user permissions for sending to other users
        if len(target_users) > 1 or (len(target_users) == 1 and target_users[0] != user['user_id']):
            # Check if user has admin permissions
            if not user.get('is_admin', False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to send alerts to other users"
                )
        
        # Create alert records for each target user
        async with database_manager.get_postgres_session() as session:
            for target_user_id in target_users:
                await session.execute("""
                    INSERT INTO alerts (alert_id, user_id, sender_id, alert_type, severity,
                                      title, message, metadata, status, channels_requested,
                                      created_at, scheduled_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"{alert_id}_{target_user_id}", target_user_id, user['user_id'],
                    alert.alert_type.value, alert.severity.value, alert.title,
                    alert.message, alert.metadata or {}, AlertStatus.PENDING.value,
                    [ch.value for ch in alert.channels], datetime.utcnow(), alert.schedule_at
                ))
            await session.commit()
        
        # Schedule alert delivery
        if alert.schedule_at and alert.schedule_at > datetime.utcnow():
            background_tasks.add_task(
                _schedule_alert_delivery, alert_id, alert, target_users
            )
        else:
            background_tasks.add_task(
                _send_alert_immediately, alert_id, alert, target_users
            )
        
        logger.info(f"Manual alert created: {alert_id} by user {user['user_id']}")
        
        return {
            "alert_id": alert_id,
            "target_users": len(target_users),
            "status": "scheduled" if alert.schedule_at else "sending",
            "message": "Alert queued for delivery"
        }
        
    except Exception as e:
        logger.error(f"Send manual alert failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send manual alert"
        )


@router.get("/list", response_model=List[Alert])
async def get_alerts(
    alert_type: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    days: int = Field(default=7, ge=1, le=90),
    limit: int = Field(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """Get user's alerts"""
    try:
        query = """
            SELECT alert_id, user_id, alert_type, severity, title, message, metadata,
                   status, channels_sent, created_at, sent_at, read_at, dismissed_at
            FROM alerts
            WHERE user_id = %s AND created_at >= %s
        """
        params = [user['user_id'], datetime.utcnow() - timedelta(days=days)]
        
        if alert_type:
            query += " AND alert_type = %s"
            params.append(alert_type.value)
        
        if severity:
            query += " AND severity = %s"
            params.append(severity.value)
        
        if status:
            query += " AND status = %s"
            params.append(status.value)
            
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            alerts = result.fetchall()
        
        alert_list = []
        for alert in alerts:
            alert_list.append(Alert(
                alert_id=alert[0],
                user_id=alert[1],
                alert_type=AlertType(alert[2]),
                severity=AlertSeverity(alert[3]),
                title=alert[4],
                message=alert[5],
                metadata=alert[6],
                status=AlertStatus(alert[7]),
                channels_sent=alert[8] or [],
                created_at=alert[9],
                sent_at=alert[10],
                read_at=alert[11],
                dismissed_at=alert[12]
            ))
        
        return alert_list
        
    except Exception as e:
        logger.error(f"Get alerts failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts"
        )


@router.put("/preferences", response_model=Dict[str, str])
async def update_notification_preferences(
    preferences: NotificationPreferences,
    user: dict = Depends(get_current_user)
):
    """Update user notification preferences"""
    try:
        # Validate phone number format if SMS enabled
        if preferences.sms_enabled and preferences.phone_number:
            if not _validate_phone_number(preferences.phone_number):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format"
                )
        
        # Validate email if email enabled
        if preferences.email_enabled and preferences.email_address:
            if not _validate_email(preferences.email_address):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email address format"
                )
        
        # Update preferences
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO notification_preferences (user_id, email_enabled, sms_enabled,
                                                    push_enabled, slack_enabled, webhook_enabled,
                                                    email_address, phone_number, slack_webhook_url,
                                                    custom_webhook_url, quiet_hours, alert_frequency,
                                                    updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    email_enabled = EXCLUDED.email_enabled,
                    sms_enabled = EXCLUDED.sms_enabled,
                    push_enabled = EXCLUDED.push_enabled,
                    slack_enabled = EXCLUDED.slack_enabled,
                    webhook_enabled = EXCLUDED.webhook_enabled,
                    email_address = EXCLUDED.email_address,
                    phone_number = EXCLUDED.phone_number,
                    slack_webhook_url = EXCLUDED.slack_webhook_url,
                    custom_webhook_url = EXCLUDED.custom_webhook_url,
                    quiet_hours = EXCLUDED.quiet_hours,
                    alert_frequency = EXCLUDED.alert_frequency,
                    updated_at = EXCLUDED.updated_at
            """, (
                user['user_id'], preferences.email_enabled, preferences.sms_enabled,
                preferences.push_enabled, preferences.slack_enabled, preferences.webhook_enabled,
                preferences.email_address, preferences.phone_number, preferences.slack_webhook_url,
                preferences.custom_webhook_url, preferences.quiet_hours, preferences.alert_frequency,
                datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Notification preferences updated for user {user['user_id']}")
        
        return {"message": "Notification preferences updated successfully"}
        
    except Exception as e:
        logger.error(f"Update notification preferences failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.put("/{alert_id}/read", response_model=Dict[str, str])
async def mark_alert_as_read(
    alert_id: str,
    user: dict = Depends(get_current_user)
):
    """Mark an alert as read"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                UPDATE alerts 
                SET status = %s, read_at = %s
                WHERE alert_id = %s AND user_id = %s AND status != %s
            """, (
                AlertStatus.READ.value, datetime.utcnow(), alert_id,
                user['user_id'], AlertStatus.READ.value
            ))
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found or already read"
                )
            
            await session.commit()
        
        logger.info(f"Alert marked as read: {alert_id}")
        
        return {"message": "Alert marked as read"}
        
    except Exception as e:
        logger.error(f"Mark alert as read failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark alert as read"
        )


@router.put("/{alert_id}/dismiss", response_model=Dict[str, str])
async def dismiss_alert(
    alert_id: str,
    user: dict = Depends(get_current_user)
):
    """Dismiss an alert"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                UPDATE alerts 
                SET status = %s, dismissed_at = %s
                WHERE alert_id = %s AND user_id = %s AND status != %s
            """, (
                AlertStatus.DISMISSED.value, datetime.utcnow(), alert_id,
                user['user_id'], AlertStatus.DISMISSED.value
            ))
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found or already dismissed"
                )
            
            await session.commit()
        
        logger.info(f"Alert dismissed: {alert_id}")
        
        return {"message": "Alert dismissed"}
        
    except Exception as e:
        logger.error(f"Dismiss alert failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss alert"
        )


@router.get("/statistics", response_model=AlertStatistics)
async def get_alert_statistics(
    days: int = Field(default=30, ge=1, le=365),
    user: dict = Depends(get_current_user)
):
    """Get alert statistics for user"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        async with database_manager.get_postgres_session() as session:
            # Total alerts
            result = await session.execute("""
                SELECT COUNT(*) FROM alerts
                WHERE user_id = %s AND created_at >= %s
            """, (user['user_id'], start_date))
            total_alerts = result.fetchone()[0]
            
            # Alerts by type
            result = await session.execute("""
                SELECT alert_type, COUNT(*) FROM alerts
                WHERE user_id = %s AND created_at >= %s
                GROUP BY alert_type
            """, (user['user_id'], start_date))
            alerts_by_type = {row[0]: row[1] for row in result.fetchall()}
            
            # Alerts by severity
            result = await session.execute("""
                SELECT severity, COUNT(*) FROM alerts
                WHERE user_id = %s AND created_at >= %s
                GROUP BY severity
            """, (user['user_id'], start_date))
            alerts_by_severity = {row[0]: row[1] for row in result.fetchall()}
            
            # Alerts by status
            result = await session.execute("""
                SELECT status, COUNT(*) FROM alerts
                WHERE user_id = %s AND created_at >= %s
                GROUP BY status
            """, (user['user_id'], start_date))
            alerts_by_status = {row[0]: row[1] for row in result.fetchall()}
            
            # Response times
            result = await session.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (read_at - created_at))/60) as avg_response_minutes
                FROM alerts
                WHERE user_id = %s AND created_at >= %s AND read_at IS NOT NULL
            """, (user['user_id'], start_date))
            avg_response = result.fetchone()[0] or 0
            
            # Delivery rates
            result = await session.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) * 100.0 / COUNT(*) as delivery_rate,
                    COUNT(CASE WHEN status = 'read' THEN 1 END) * 100.0 / COUNT(*) as read_rate
                FROM alerts
                WHERE user_id = %s AND created_at >= %s
            """, (user['user_id'], start_date))
            rates = result.fetchone()
            delivery_rate = rates[0] or 0
            read_rate = rates[1] or 0
        
        statistics = AlertStatistics(
            total_alerts=total_alerts,
            alerts_by_type=alerts_by_type,
            alerts_by_severity=alerts_by_severity,
            alerts_by_status=alerts_by_status,
            response_times={"average_minutes": float(avg_response)},
            delivery_rates={
                "delivery_rate": float(delivery_rate),
                "read_rate": float(read_rate)
            },
            period=f"{days}d"
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Get alert statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert statistics"
        )


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete an alert rule"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                DELETE FROM alert_rules
                WHERE rule_id = %s AND user_id = %s
            """, (rule_id, user['user_id']))
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert rule not found or access denied"
                )
            
            await session.commit()
        
        # Unregister rule from monitoring system
        await notification_manager.unregister_alert_rule(rule_id)
        
        logger.info(f"Alert rule deleted: {rule_id}")
        
        return {"message": "Alert rule deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete alert rule failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert rule"
        )


# Helper functions
def _validate_alert_conditions(alert_type: AlertType, conditions: Dict[str, Any]) -> bool:
    """Validate alert rule conditions"""
    required_conditions = {
        AlertType.VIOLATION_DETECTED: ['similarity_threshold', 'platforms'],
        AlertType.COPYRIGHT_CLAIM: ['claim_type'],
        AlertType.REVENUE_MILESTONE: ['milestone_amount', 'currency'],
        AlertType.COLLABORATION_REQUEST: ['request_types'],
        AlertType.SYSTEM_ALERT: ['component'],
        AlertType.SECURITY_ALERT: ['threat_level'],
        AlertType.PROCESSING_COMPLETE: ['processing_types'],
        AlertType.ACCOUNT_UPDATE: ['update_types']
    }
    
    required = required_conditions.get(alert_type, [])
    return all(condition in conditions for condition in required)


def _validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Basic international phone number validation
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))


def _validate_email(email: str) -> bool:
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# Background task functions
async def _send_alert_immediately(alert_id: str, alert: ManualAlert, target_users: List[str]):
    """Send alert immediately to target users"""
    try:
        for user_id in target_users:
            # Get user notification preferences
            preferences = await _get_user_notification_preferences(user_id)
            
            # Send via each requested channel
            for channel in alert.channels:
                if _should_send_via_channel(channel, preferences):
                    await _send_via_channel(
                        channel, user_id, alert, preferences
                    )
        
        # Update alert status
        await _update_alert_status(alert_id, AlertStatus.SENT, target_users)
        
        logger.info(f"Alert sent immediately: {alert_id}")
        
    except Exception as e:
        logger.error(f"Send alert immediately failed: {e}")
        await _update_alert_status(alert_id, AlertStatus.FAILED, target_users, str(e))


async def _schedule_alert_delivery(alert_id: str, alert: ManualAlert, target_users: List[str]):
    """Schedule alert delivery for later"""
    try:
        # Calculate delay
        delay = (alert.schedule_at - datetime.utcnow()).total_seconds()
        
        if delay > 0:
            await asyncio.sleep(delay)
        
        # Send the alert
        await _send_alert_immediately(alert_id, alert, target_users)
        
    except Exception as e:
        logger.error(f"Schedule alert delivery failed: {e}")
        await _update_alert_status(alert_id, AlertStatus.FAILED, target_users, str(e))


async def _get_user_notification_preferences(user_id: str) -> Dict[str, Any]:
    """Get user notification preferences"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT email_enabled, sms_enabled, push_enabled, slack_enabled,
                       webhook_enabled, email_address, phone_number, slack_webhook_url,
                       custom_webhook_url, quiet_hours, alert_frequency
                FROM notification_preferences
                WHERE user_id = %s
            """, (user_id,))
            
            prefs = result.fetchone()
            if prefs:
                return {
                    "email_enabled": prefs[0],
                    "sms_enabled": prefs[1],
                    "push_enabled": prefs[2],
                    "slack_enabled": prefs[3],
                    "webhook_enabled": prefs[4],
                    "email_address": prefs[5],
                    "phone_number": prefs[6],
                    "slack_webhook_url": prefs[7],
                    "custom_webhook_url": prefs[8],
                    "quiet_hours": prefs[9],
                    "alert_frequency": prefs[10]
                }
            else:
                # Default preferences
                return {
                    "email_enabled": True,
                    "sms_enabled": False,
                    "push_enabled": True,
                    "slack_enabled": False,
                    "webhook_enabled": False,
                    "alert_frequency": "immediate"
                }
    except Exception as e:
        logger.error(f"Get notification preferences failed: {e}")
        return {}


def _should_send_via_channel(channel: NotificationChannel, preferences: Dict[str, Any]) -> bool:
    """Check if alert should be sent via specific channel"""
    channel_enabled_map = {
        NotificationChannel.EMAIL: preferences.get("email_enabled", True),
        NotificationChannel.SMS: preferences.get("sms_enabled", False),
        NotificationChannel.PUSH: preferences.get("push_enabled", True),
        NotificationChannel.SLACK: preferences.get("slack_enabled", False),
        NotificationChannel.WEBHOOK: preferences.get("webhook_enabled", False),
        NotificationChannel.IN_APP: True  # Always enabled
    }
    
    return channel_enabled_map.get(channel, False)


async def _send_via_channel(channel: NotificationChannel, user_id: str, 
                           alert: ManualAlert, preferences: Dict[str, Any]):
    """Send alert via specific channel"""
    try:
        if channel == NotificationChannel.EMAIL:
            await sendgrid_integration.send_alert_email(
                user_id, alert.title, alert.message, preferences.get("email_address")
            )
        elif channel == NotificationChannel.SMS:
            await twilio_integration.send_alert_sms(
                user_id, alert.title, alert.message, preferences.get("phone_number")
            )
        elif channel == NotificationChannel.PUSH:
            await notification_manager.send_push_notification(
                user_id, alert.title, alert.message
            )
        elif channel == NotificationChannel.SLACK:
            await notification_manager.send_slack_notification(
                user_id, alert.title, alert.message, preferences.get("slack_webhook_url")
            )
        elif channel == NotificationChannel.WEBHOOK:
            await notification_manager.send_webhook_notification(
                user_id, alert.title, alert.message, preferences.get("custom_webhook_url")
            )
        
        logger.debug(f"Alert sent via {channel.value} to user {user_id}")
        
    except Exception as e:
        logger.error(f"Send via {channel.value} failed: {e}")


async def _update_alert_status(alert_id: str, status: AlertStatus, target_users: List[str], 
                              error_message: Optional[str] = None):
    """Update alert status in database"""
    try:
        async with database_manager.get_postgres_session() as session:
            for user_id in target_users:
                user_alert_id = f"{alert_id}_{user_id}"
                if error_message:
                    await session.execute("""
                        UPDATE alerts 
                        SET status = %s, error_message = %s, updated_at = %s
                        WHERE alert_id = %s
                    """, (status.value, error_message, datetime.utcnow(), user_alert_id))
                else:
                    await session.execute("""
                        UPDATE alerts 
                        SET status = %s, sent_at = %s, updated_at = %s
                        WHERE alert_id = %s
                    """, (status.value, datetime.utcnow(), datetime.utcnow(), user_alert_id))
            await session.commit()
    except Exception as e:
        logger.error(f"Update alert status failed: {e}")