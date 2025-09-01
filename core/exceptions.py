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