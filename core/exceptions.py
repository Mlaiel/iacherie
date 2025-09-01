"""Core Exceptions for AI Agents Business Logic
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
class AgentError(Exception):
    """
Base exception for agent operations"""
    pass


class ValidationError(AgentError):
    """
Exception for validation failures"""
    pass


class ProcessingError(AgentError):
    """
Exception for processing failures"""
    pass


class ResourceLimitError(AgentError):
    """
Exception for resource limit violations"""
    pass


class SecurityError(AgentError):
    """
Exception for security violations"""
    pass


class CrawlerError(AgentError):
    """
Exception for crawler operations"""
    pass


class RateLimitError(CrawlerError):
    """
Exception for rate limit violations"""
    pass


class ContentMatchError(AgentError):
    """
Exception for content matching operations"""
    pass


class WorkflowError(AgentError):
    """
Exception for workflow failures"""
    pass


class BusinessLogicError(AgentError):
    """
Exception for business logic failures"""
    pass


class DistributionError(AgentError):
    """
Exception for distribution operations"""
    pass


class PlatformError(AgentError):
    """
Exception for platform integration failures"""
    pass


class ProtectionError(AgentError):
    """
Exception for content protection failures"""
    pass


class MonetizationError(AgentError):
    """
Exception for monetization operations"""
    pass


class AuthenticationError(AgentError):
    """
Exception for authentication failures"""
    pass


class AuthorizationError(AgentError):
    """
Exception for authorization failures"""
    pass


class StorageError(AgentError):
    """
Exception for storage operations"""
    pass


class NetworkError(AgentError):
    """
Exception for network operations"""
    pass


class ConfigurationError(AgentError):
    """
Exception for configuration errors"""
    pass


class DatabaseError(AgentError):
    """
Exception for database operations"""
    pass


class LicensingError(AgentError):
    """
Exception for licensing operations"""
    pass


class ComplianceError(AgentError):
    """
Exception for compliance failures"""
    pass