"""
Audit Log Repository Module

Enterprise-grade repository for comprehensive audit logging with security
compliance, forensic analysis, and automated threat detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime, timedelta
import uuid
import json
import hashlib
from ..models.audit_logs import (
    AuditLog,
    ActionType,
    EntityType,
    SecurityClassification,
    LogLevel,
    ComplianceCategory,
    AccessType
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class AuditLogRepository(BaseRepository[AuditLog]):
    """
    Repository for audit log operations with enterprise-grade security compliance,
    forensic capabilities, threat detection, and comprehensive audit trails.
    """
    
    def __init__(self, db_session: Session):
        """Initialize audit log repository"""
        super().__init__(db_session, AuditLog)
        
    def log_action(self,
                  user_id: Optional[int],
                  action_type: ActionType,
                  entity_type: EntityType,
                  entity_id: Optional[int] = None,
                  details: Optional[Dict[str, Any]] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  session_id: Optional[str] = None,
                  security_classification: SecurityClassification = SecurityClassification.INTERNAL,
                  log_level: LogLevel = LogLevel.INFO,
                  compliance_category: ComplianceCategory = ComplianceCategory.OPERATIONAL,
                  access_type: AccessType = AccessType.WEB) -> AuditLog:
        """
        Create comprehensive audit log entry with security context
        
        Args:
            user_id: User performing the action (None for system actions)
            action_type: Type of action performed
            entity_type: Type of entity affected
            entity_id: ID of affected entity
            details: Additional action details
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: Session identifier
            security_classification: Security classification level
            log_level: Log severity level
            compliance_category: Compliance category
            access_type: Access method type
            
        Returns:
            Created AuditLog instance
        """



        try:
            # Generate log entry ID and hash
            log_id = str(uuid.uuid4())
            
            # Create details hash for integrity verification
            details_json = json.dumps(details or {}, sort_keys=True)
            details_hash = hashlib.sha256(details_json.encode()).hexdigest()
            
            # Determine risk score based on action and classification
            risk_score = self._calculate_risk_score(action_type, security_classification, user_id)
            
            log_data = {
                'user_id': user_id,
                'action_type': action_type,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'details': details or {},
                'details_hash': details_hash,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
                'security_classification': security_classification,
                'log_level': log_level,
                'compliance_category': compliance_category,
                'access_type': access_type,
                'risk_score': risk_score,
                'log_id': log_id,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            audit_log = self.create(**log_data)
            
            # Trigger security alerts for high-risk actions
            if risk_score >= 80:
                self._trigger_security_alert(audit_log)
            
            self.logger.debug(
                f"Logged {action_type.value} action on {entity_type.value} by user {user_id}"
            )
            
            return audit_log
            
        except Exception as e:
            # Critical: Log to system logger if audit logging fails
            logger.critical(f"AUDIT LOG FAILURE: {str(e)} - Action: {action_type.value}")
            raise RepositoryException(f"Audit log creation failed: {str(e)}")
            
    def _calculate_risk_score(self,
                            action_type: ActionType,
                            security_classification: SecurityClassification,
                            user_id: Optional[int]) -> int:
        """
        Calculate risk score for the action
        
        Args:
            action_type: Type of action
            security_classification: Security classification
            user_id: User ID (None for system actions)
            
        Returns:
            Risk score (0-100)
        """
        base_scores = {
            ActionType.CREATE: 20,
            ActionType.READ: 10,
            ActionType.UPDATE: 30,
            ActionType.DELETE: 60,
            ActionType.LOGIN: 15,
            ActionType.LOGOUT: 5,
            ActionType.FAILED_LOGIN: 40,
            ActionType.PERMISSION_CHANGE: 70,
            ActionType.SECURITY_EVENT: 80,
            ActionType.DATA_EXPORT: 50,
            ActionType.DATA_IMPORT: 45,
            ActionType.SYSTEM_CONFIG: 75,
            ActionType.ADMIN_ACTION: 65
        }
        
        classification_multipliers = {
            SecurityClassification.PUBLIC: 1.0,
            SecurityClassification.INTERNAL: 1.2,
            SecurityClassification.CONFIDENTIAL: 1.5,
            SecurityClassification.RESTRICTED: 2.0
        }
        
        base_score = base_scores.get(action_type, 25)
        multiplier = classification_multipliers.get(security_classification, 1.0)
        
        # System actions get lower scores
        if user_id is None:
            multiplier *= 0.7
            
        final_score = min(100, int(base_score * multiplier))
        return final_score
        
    def _trigger_security_alert(self, audit_log: AuditLog) -> None:
        """
        Trigger security alert for high-risk actions
        
        Args:
            audit_log: High-risk audit log entry
        """



        try:
            # In production, this would integrate with security monitoring systems
            alert_data = {
                'alert_type': 'HIGH_RISK_ACTION',
                'log_id': audit_log.log_id,
                'user_id': audit_log.user_id,
                'action_type': audit_log.action_type.value,
                'risk_score': audit_log.risk_score,
                'ip_address': audit_log.ip_address,
                'timestamp': audit_log.timestamp.isoformat()
            }
            
            self.logger.warning(f"HIGH RISK ACTION DETECTED: {json.dumps(alert_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger security alert: {str(e)}")
            
    def get_user_activity(self,
                         user_id: int,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         action_types: Optional[List[ActionType]] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None) -> List[AuditLog]:
        """
        Get user activity logs with comprehensive filtering
        
        Args:
            user_id: User ID to get activity for
            start_date: Optional start date filter
            end_date: Optional end date filter
            action_types: Optional action type filters
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of AuditLog instances
        """



        try:
            query = self.db_session.query(AuditLog).filter(
                AuditLog.user_id == user_id
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Apply action type filter
            if action_types:
                query = query.filter(AuditLog.action_type.in_(action_types))
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            # Order by timestamp (most recent first)
            query = query.order_by(AuditLog.timestamp.desc())
            
            activity_logs = query.all()
            
            self.logger.debug(
                f"Retrieved {len(activity_logs)} activity logs for user {user_id}"
            )
            
            return activity_logs
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity: {str(e)}")
            return []
            
    def get_security_events(self,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          min_risk_score: int = 50,
                          security_classification: Optional[SecurityClassification] = None,
                          limit: Optional[int] = None) -> List[AuditLog]:
        """
        Get security-relevant events for monitoring and analysis
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            min_risk_score: Minimum risk score threshold
            security_classification: Optional security classification filter
            limit: Maximum number of results
            
        Returns:
            List of security-relevant AuditLog instances
        """



        try:
            query = self.db_session.query(AuditLog).filter(
                AuditLog.risk_score >= min_risk_score
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Apply security classification filter
            if security_classification:
                query = query.filter(AuditLog.security_classification == security_classification)
            
            # Order by risk score (highest first) then by timestamp
            query = query.order_by(
                AuditLog.risk_score.desc(),
                AuditLog.timestamp.desc()
            )
            
            if limit:
                query = query.limit(limit)
            
            security_events = query.all()
            
            self.logger.debug(f"Retrieved {len(security_events)} security events")
            
            return security_events
            
        except Exception as e:
            self.logger.error(f"Failed to get security events: {str(e)}")
            return []
            
    def search_logs(self,
                   search_criteria: Dict[str, Any],
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[AuditLog]:
        """
        Advanced search through audit logs with flexible criteria
        
        Args:
            search_criteria: Dictionary of search criteria
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results
            
        Returns:
            List of matching AuditLog instances
        """



        try:
            query = self.db_session.query(AuditLog)
            
            # Apply date filters
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Apply search criteria
            for field, value in search_criteria.items():
                if hasattr(AuditLog, field):
                    column = getattr(AuditLog, field)
                    
                    if isinstance(value, dict):
                        # Advanced search operations
                        for operation, operand in value.items():
                            if operation == 'contains' and field in ['details', 'user_agent']:
                                if field == 'details':
                                    # Search in JSON field
                                    query = query.filter(
                                        func.jsonb_path_exists(
                                            column,
                                            f'$.** ? (@ like_regex "{operand}" flag "i")'
                                        )
                                    )
                                else:
                                    query = query.filter(column.ilike(f"%{operand}%"))
                            elif operation == 'in':
                                query = query.filter(column.in_(operand))
                            elif operation == 'gte':
                                query = query.filter(column >= operand)
                            elif operation == 'lte':
                                query = query.filter(column <= operand)
                    else:
                        query = query.filter(column == value)
            
            # Order by timestamp (most recent first)
            query = query.order_by(AuditLog.timestamp.desc()).limit(limit)
            
            search_results = query.all()
            
            self.logger.debug(f"Found {len(search_results)} logs matching search criteria")
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Failed to search logs: {str(e)}")
            return []
            
    def get_compliance_report(self,
                            start_date: datetime,
                            end_date: datetime,
                            compliance_category: Optional[ComplianceCategory] = None) -> Dict[str, Any]:
        """
        Generate compliance audit report for regulatory requirements
        
        Args:
            start_date: Report start date
            end_date: Report end date
            compliance_category: Optional compliance category filter
            
        Returns:
            Comprehensive compliance report
        """



        try:
            query = self.db_session.query(AuditLog).filter(
                and_(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date
                )
            )
            
            if compliance_category:
                query = query.filter(AuditLog.compliance_category == compliance_category)
            
            audit_logs = query.all()
            
            # Generate statistics
            total_events = len(audit_logs)
            
            # Action type distribution
            action_stats = {}
            for action_type in ActionType:
                count = sum(1 for log in audit_logs if log.action_type == action_type)
                action_stats[action_type.value] = count
            
            # User activity statistics
            user_activity = {}
            for log in audit_logs:
                if log.user_id:
                    user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
            
            # Security events
            high_risk_events = [log for log in audit_logs if log.risk_score >= 70]
            
            # Compliance category distribution
            compliance_stats = {}
            for category in ComplianceCategory:
                count = sum(1 for log in audit_logs if log.compliance_category == category)
                compliance_stats[category.value] = count
            
            # Access pattern analysis
            access_patterns = {}
            for access_type in AccessType:
                count = sum(1 for log in audit_logs if log.access_type == access_type)
                access_patterns[access_type.value] = count
            
            # Failed access attempts
            failed_logins = [
                log for log in audit_logs 
                if log.action_type == ActionType.FAILED_LOGIN
            ]
            
            # Data access events
            data_access_events = [
                log for log in audit_logs 
                if log.action_type in [ActionType.DATA_EXPORT, ActionType.DATA_IMPORT]
            ]
            
            # Generate compliance summary
            compliance_issues = []
            
            # Check for excessive failed logins
            if len(failed_logins) > 100:
                compliance_issues.append({
                    'type': 'EXCESSIVE_FAILED_LOGINS',
                    'count': len(failed_logins),
                    'severity': 'HIGH'
                })
            
            # Check for unauthorized data access
            unauthorized_access = [
                log for log in audit_logs 
                if log.security_classification == SecurityClassification.RESTRICTED
                and log.risk_score >= 80
            ]
            
            if unauthorized_access:
                compliance_issues.append({
                    'type': 'UNAUTHORIZED_RESTRICTED_ACCESS',
                    'count': len(unauthorized_access),
                    'severity': 'CRITICAL'
                })
            
            report = {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days
                },
                'summary': {
                    'total_events': total_events,
                    'unique_users': len(user_activity),
                    'high_risk_events': len(high_risk_events),
                    'failed_login_attempts': len(failed_logins),
                    'data_access_events': len(data_access_events)
                },
                'distributions': {
                    'action_types': action_stats,
                    'compliance_categories': compliance_stats,
                    'access_patterns': access_patterns
                },
                'security_analysis': {
                    'high_risk_events_count': len(high_risk_events),
                    'failed_login_count': len(failed_logins),
                    'unauthorized_access_attempts': len(unauthorized_access)
                },
                'compliance_issues': compliance_issues,
                'top_users_by_activity': sorted(
                    user_activity.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                'generated_at': datetime.utcnow().isoformat(),
                'report_integrity_hash': self._generate_report_hash(audit_logs)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            return {'error': str(e)}
            
    def _generate_report_hash(self, audit_logs: List[AuditLog]) -> str:
        """
        Generate integrity hash for compliance report
        
        Args:
            audit_logs: List of audit logs in the report
            
        Returns:
            SHA-256 hash of report data
        """



        try:
            # Create concatenated string of all log IDs and hashes
            log_data = ''.join(
                f"{log.log_id}{log.details_hash}" 
                for log in sorted(audit_logs, key=lambda x: x.log_id)
            )
            
            return hashlib.sha256(log_data.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to generate report hash: {str(e)}")
            return 'hash_generation_failed'
            
    def verify_log_integrity(self, log_id: str) -> bool:
        """
        Verify integrity of an audit log entry
        
        Args:
            log_id: Log ID to verify
            
        Returns:
            True if integrity is verified, False otherwise
        """



        try:
            audit_log = self.db_session.query(AuditLog).filter(
                AuditLog.log_id == log_id
            ).first()
            
            if not audit_log:
                return False
            
            # Recalculate details hash
            details_json = json.dumps(audit_log.details, sort_keys=True)
            calculated_hash = hashlib.sha256(details_json.encode()).hexdigest()
            
            return calculated_hash == audit_log.details_hash
            
        except Exception as e:
            self.logger.error(f"Failed to verify log integrity: {str(e)}")
            return False
            
    def cleanup_old_logs(self, retention_days: int = 2555) -> int:  # 7 years default
        """
        Clean up old audit logs beyond retention period
        
        Args:
            retention_days: Number of days to retain logs
            
        Returns:
            Number of archived/deleted logs
        """



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # For compliance, we archive rather than delete
            old_logs = self.db_session.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date
            )
            
            # Update metadata to mark as archived
            archived_count = old_logs.update(
                {
                    'archived_at': datetime.utcnow(),
                    'details': func.jsonb_set(
                        AuditLog.details,
                        '{archived}',
                        'true'
                    )
                },
                synchronize_session=False
            )
            
            with self.transaction():
                pass  # Commit changes
                
            self.logger.info(
                f"Archived {archived_count} audit logs older than {retention_days} days"
            )
            
            return archived_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {str(e)}")
            raise RepositoryException(f"Log cleanup failed: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
