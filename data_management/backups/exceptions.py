"""
 Exceptions - Backup System Exception Classes
==============================================
Module: backend/data_management/backups/exceptions.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Exception System - Enterprise Production-Ready
Responsibility: Exceptions hiérarchiques pour système de sauvegarde
===================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class BackupException(Exception):
    """
    Exception de base pour le système de sauvegarde
    
    Classe mère pour toutes les exceptions spécifiques au système de backup.
    Fournit des fonctionnalités communes comme les codes d'erreur,
    le contexte et la sérialisation.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialise l'exception
        
        Args:
            message: Message d'erreur principal
            error_code: Code d'erreur spécifique
            context: Contexte additionnel (métadonnées, IDs, etc.)
            original_exception: Exception originale si wrapping
        """
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        
        # Ajout informations de l'exception originale au contexte
        if original_exception:
            self.context["original_error"] = {
                "type": type(original_exception).__name__,
                "message": str(original_exception),
                "args": original_exception.args
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise l'exception en dictionnaire
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire
        """



        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": {
                "type": type(self.original_exception).__name__,
                "message": str(self.original_exception)
            } if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """Représentation string enrichie"""
        base_msg = f"[{self.error_code}] {self.message}"
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        
        if self.original_exception:
            base_msg += f" (Caused by: {self.original_exception})"
        
        return base_msg


# Exceptions de configuration et validation

class ConfigurationException(BackupException):
    """Exception de configuration du système de sauvegarde"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if config_key:
            context["config_key"] = config_key
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ValidationException(BackupException):
    """Exception de validation des données ou paramètres"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["invalid_value"] = str(value)
        kwargs["context"] = context
        super().__init__(message, **kwargs)


# Exceptions de gestion des tâches et jobs

class JobException(BackupException):
    """Exception de base pour les tâches de sauvegarde"""
    
    def __init__(self, message: str, job_id: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if job_id:
            context["job_id"] = job_id
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class JobCreationException(JobException):
    """Exception lors de la création d'une tâche de sauvegarde"""
    pass


class JobExecutionException(JobException):
    """Exception lors de l'exécution d'une tâche de sauvegarde"""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        phase: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if phase:
            context["execution_phase"] = phase
        kwargs["context"] = context
        super().__init__(message, job_id=job_id, **kwargs)


class JobTimeoutException(JobException):
    """Exception de timeout lors de l'exécution d'une tâche"""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        kwargs["context"] = context
        super().__init__(message, job_id=job_id, **kwargs)


# Exceptions de stockage et I/O

class StorageException(BackupException):
    """Exception de base pour les opérations de stockage"""
    
    def __init__(
        self,
        message: str,
        storage_provider: Optional[str] = None,
        storage_path: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if storage_provider:
            context["storage_provider"] = storage_provider
        if storage_path:
            context["storage_path"] = storage_path
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class StorageConnectionException(StorageException):
    """Exception de connexion au stockage"""
    pass


class StorageAuthenticationException(StorageException):
    """Exception d'authentification avec le stockage"""
    pass


class StorageCapacityException(StorageException):
    """Exception de capacité de stockage insuffisante"""
    
    def __init__(
        self,
        message: str,
        required_space: Optional[int] = None,
        available_space: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if required_space:
            context["required_space_bytes"] = required_space
        if available_space:
            context["available_space_bytes"] = available_space
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class StoragePermissionException(StorageException):
    """Exception de permissions de stockage"""
    pass


class FileNotFoundException(StorageException):
    """Exception de fichier non trouvé"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if file_path:
            context["file_path"] = file_path
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class FileAccessException(StorageException):
    """Exception d'accès aux fichiers"""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if file_path:
            context["file_path"] = file_path
        if operation:
            context["operation"] = operation
        kwargs["context"] = context
        super().__init__(message, **kwargs)


# Exceptions de compression

class CompressionException(BackupException):
    """Exception de base pour les opérations de compression"""
    
    def __init__(
        self,
        message: str,
        algorithm: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if algorithm:
            context["compression_algorithm"] = algorithm
        if file_path:
            context["file_path"] = file_path
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CompressionAlgorithmException(CompressionException):
    """Exception d'algorithme de compression non supporté"""
    pass


class CompressionRatioException(CompressionException):
    """Exception de ratio de compression anormal"""
    
    def __init__(
        self,
        message: str,
        expected_ratio: Optional[float] = None,
        actual_ratio: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if expected_ratio:
            context["expected_ratio"] = expected_ratio
        if actual_ratio:
            context["actual_ratio"] = actual_ratio
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class DecompressionException(CompressionException):
    """Exception lors de la décompression"""
    pass


# Exceptions de chiffrement et sécurité

class EncryptionException(BackupException):
    """Exception de base pour les opérations de chiffrement"""
    
    def __init__(
        self,
        message: str,
        algorithm: Optional[str] = None,
        key_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if algorithm:
            context["encryption_algorithm"] = algorithm
        if key_id:
            context["key_id"] = key_id
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class KeyManagementException(EncryptionException):
    """Exception de gestion des clés de chiffrement"""
    pass


class KeyNotFoundException(KeyManagementException):
    """Exception de clé de chiffrement non trouvée"""
    
    def __init__(self, message: str, key_id: Optional[str] = None, **kwargs):
        super().__init__(message, key_id=key_id, **kwargs)


class KeyExpiredException(KeyManagementException):
    """Exception de clé de chiffrement expirée"""
    
    def __init__(
        self,
        message: str,
        key_id: Optional[str] = None,
        expired_at: Optional[datetime] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if expired_at:
            context["expired_at"] = expired_at.isoformat()
        kwargs["context"] = context
        super().__init__(message, key_id=key_id, **kwargs)


class DecryptionException(EncryptionException):
    """Exception lors du déchiffrement"""
    pass


# Exceptions de vérification et intégrité

class VerificationException(BackupException):
    """Exception de base pour les opérations de vérification"""
    
    def __init__(
        self,
        message: str,
        backup_id: Optional[str] = None,
        verification_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if backup_id:
            context["backup_id"] = backup_id
        if verification_type:
            context["verification_type"] = verification_type
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class IntegrityException(VerificationException):
    """Exception d'intégrité des données"""
    
    def __init__(
        self,
        message: str,
        expected_checksum: Optional[str] = None,
        actual_checksum: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if expected_checksum:
            context["expected_checksum"] = expected_checksum
        if actual_checksum:
            context["actual_checksum"] = actual_checksum
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CorruptionException(IntegrityException):
    """Exception de corruption de données détectée"""
    pass


class ChecksumMismatchException(IntegrityException):
    """Exception de différence de checksum"""
    pass


# Exceptions de récupération

class RecoveryException(BackupException):
    """Exception de base pour les opérations de récupération"""
    
    def __init__(
        self,
        message: str,
        recovery_id: Optional[str] = None,
        backup_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if recovery_id:
            context["recovery_id"] = recovery_id
        if backup_id:
            context["backup_id"] = backup_id
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class RecoveryPlanException(RecoveryException):
    """Exception de planification de récupération"""
    pass


class RecoveryExecutionException(RecoveryException):
    """Exception d'exécution de récupération"""
    
    def __init__(
        self,
        message: str,
        recovery_id: Optional[str] = None,
        phase: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if phase:
            context["recovery_phase"] = phase
        kwargs["context"] = context
        super().__init__(message, recovery_id=recovery_id, **kwargs)


class RecoveryTimeoutException(RecoveryException):
    """Exception de timeout lors de la récupération"""
    pass


# Exceptions de monitoring et alertes

class MonitoringException(BackupException):
    """Exception de base pour le système de monitoring"""
    
    def __init__(
        self,
        message: str,
        metric_name: Optional[str] = None,
        component: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if metric_name:
            context["metric_name"] = metric_name
        if component:
            context["monitoring_component"] = component
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class MetricCollectionException(MonitoringException):
    """Exception de collection de métriques"""
    pass


class AlertException(MonitoringException):
    """Exception du système d'alertes"""
    
    def __init__(
        self,
        message: str,
        alert_id: Optional[str] = None,
        alert_level: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if alert_id:
            context["alert_id"] = alert_id
        if alert_level:
            context["alert_level"] = alert_level
        kwargs["context"] = context
        super().__init__(message, **kwargs)


# Exceptions de rétention

class RetentionException(BackupException):
    """Exception de base pour les opérations de rétention"""
    
    def __init__(
        self,
        message: str,
        rule_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if rule_id:
            context["retention_rule_id"] = rule_id
        if plan_id:
            context["retention_plan_id"] = plan_id
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class RetentionPolicyException(RetentionException):
    """Exception de politique de rétention"""
    pass


class RetentionExecutionException(RetentionException):
    """Exception d'exécution de rétention"""
    pass


# Exceptions de planification

class SchedulingException(BackupException):
    """Exception de base pour la planification"""
    
    def __init__(
        self,
        message: str,
        schedule_id: Optional[str] = None,
        cron_expression: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if schedule_id:
            context["schedule_id"] = schedule_id
        if cron_expression:
            context["cron_expression"] = cron_expression
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CronExpressionException(SchedulingException):
    """Exception d'expression cron invalide"""
    pass


class ScheduleConflictException(SchedulingException):
    """Exception de conflit de planification"""
    pass


# Exceptions de quotas et limites

class QuotaException(BackupException):
    """Exception de dépassement de quota"""
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        quota_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if user_id:
            context["user_id"] = user_id
        if quota_type:
            context["quota_type"] = quota_type
        if current_usage is not None:
            context["current_usage"] = current_usage
        if quota_limit is not None:
            context["quota_limit"] = quota_limit
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class StorageQuotaException(QuotaException):
    """Exception de dépassement de quota de stockage"""
    pass


class BackupCountQuotaException(QuotaException):
    """Exception de dépassement de quota de nombre de sauvegardes"""
    pass


class BandwidthQuotaException(QuotaException):
    """Exception de dépassement de quota de bande passante"""
    pass


# Exceptions de réseau et connectivité

class NetworkException(BackupException):
    """Exception de base pour les problèmes réseau"""
    
    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if host:
            context["host"] = host
        if port:
            context["port"] = port
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ConnectionException(NetworkException):
    """Exception de connexion réseau"""
    pass


class TimeoutException(NetworkException):
    """Exception de timeout réseau"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        kwargs["context"] = context
        super().__init__(message, **kwargs)


# Fonctions utilitaires pour les exceptions

def wrap_exception(
    original_exception: Exception,
    new_exception_class: type = BackupException,
    message: Optional[str] = None,
    **kwargs
) -> BackupException:
    """
    Encapsule une exception générique dans une exception de backup
    
    Args:
        original_exception: Exception originale
        new_exception_class: Classe de la nouvelle exception
        message: Message personnalisé (optionnel)
        **kwargs: Arguments supplémentaires
        
    Returns:
        BackupException: Nouvelle exception encapsulée
    """
    if message is None:
        message = f"Backup operation failed: {str(original_exception)}"
    
    return new_exception_class(
        message=message,
        original_exception=original_exception,
        **kwargs
    )


def format_exception_for_logging(exception: BackupException) -> str:
    """
    Formate une exception pour le logging
    
    Args:
        exception: Exception à formater
        
    Returns:
        str: Format pour logging
    """
    lines = [
        f"Exception: {exception.__class__.__name__}",
        f"Message: {exception.message}",
        f"Error Code: {exception.error_code}",
        f"Timestamp: {exception.timestamp.isoformat()}"
    ]
    
    if exception.context:
        lines.append("Context:")
        for key, value in exception.context.items():
            lines.append(f"  {key}: {value}")
    
    if exception.original_exception:
        lines.append(f"Original Exception: {exception.original_exception}")
    
    return "\n".join(lines)


def create_error_response(
    exception: BackupException,
    include_stack_trace: bool = False
) -> Dict[str, Any]:
    """
    Crée une réponse d'erreur standardisée
    
    Args:
        exception: Exception à convertir
        include_stack_trace: Inclure la stack trace
        
    Returns:
        Dict[str, Any]: Réponse d'erreur
    """
    response = {
        "error": True,
        "error_code": exception.error_code,
        "message": exception.message,
        "timestamp": exception.timestamp.isoformat(),
        "context": exception.context
    }
    
    if include_stack_trace:
        import traceback
        response["stack_trace"] = traceback.format_exc()
    
    return response


# Export de toutes les exceptions
__all__ = [
    # Exception de base
    'BackupException',
    
    # Configuration et validation
    'ConfigurationException',
    'ValidationException',
    
    # Jobs et tâches
    'JobException',
    'JobCreationException',
    'JobExecutionException',
    'JobTimeoutException',
    
    # Stockage et I/O
    'StorageException',
    'StorageConnectionException',
    'StorageAuthenticationException',
    'StorageCapacityException',
    'StoragePermissionException',
    'FileNotFoundException',
    'FileAccessException',
    
    # Compression
    'CompressionException',
    'CompressionAlgorithmException',
    'CompressionRatioException',
    'DecompressionException',
    
    # Chiffrement et sécurité
    'EncryptionException',
    'KeyManagementException',
    'KeyNotFoundException',
    'KeyExpiredException',
    'DecryptionException',
    
    # Vérification et intégrité
    'VerificationException',
    'IntegrityException',
    'CorruptionException',
    'ChecksumMismatchException',
    
    # Récupération
    'RecoveryException',
    'RecoveryPlanException',
    'RecoveryExecutionException',
    'RecoveryTimeoutException',
    
    # Monitoring
    'MonitoringException',
    'MetricCollectionException',
    'AlertException',
    
    # Rétention
    'RetentionException',
    'RetentionPolicyException',
    'RetentionExecutionException',
    
    # Planification
    'SchedulingException',
    'CronExpressionException',
    'ScheduleConflictException',
    
    # Quotas
    'QuotaException',
    'StorageQuotaException',
    'BackupCountQuotaException',
    'BandwidthQuotaException',
    
    # Réseau
    'NetworkException',
    'ConnectionException',
    'TimeoutException',
    
    # Fonctions utilitaires
    'wrap_exception',
    'format_exception_for_logging',
    'create_error_response'
]
