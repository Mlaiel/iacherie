"""Request Router - Intelligent Request Routing System

Advanced request routing with pattern matching, service discovery integration,
and dynamic routing rules for the API Gateway.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

from .config import APIGatewayConfig

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """
Request routing strategies"""

    PREFIX_MATCH = "prefix_match"
    EXACT_MATCH = "exact_match"
    REGEX_MATCH = "regex_match"
    WILDCARD_MATCH = "wildcard_match"


@dataclass
class RoutingRule:
    """Individual routing rule configuration"""
    pattern: str
    service: str
    strategy: RoutingStrategy
    priority: int = 0
    conditions: Optional[Dict[str, Any]] = None
    transformations: Optional[Dict[str, Any]] = None
    compiled_regex: Optional[re.Pattern] = None


class RequestRouter:
    """
    Enterprise Request Router
    
    Provides intelligent request routing based on:
    - URL path patterns
    - HTTP methods and headers
    - Service availability and health
    - Dynamic routing rules
    - Load balancing integration
    """
    
    def __init__(self, config: APIGatewayConfig):
        """
Initialize request router"""
        self.config = config
        self.routing_rules: List[RoutingRule] = []
        
        # Initialize routing rules from configuration
        self._initialize_routing_rules()
        
        # Service discovery integration
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Request router initialized with {len(self.routing_rules)} rules")
    
    def _initialize_routing_rules(self):
        """Initialize routing rules from configuration"""
        try:
            # Create routing rules from service configuration
            for service_name, service_config in self.config.service_routes.items():
                rule = RoutingRule(
                    pattern=service_config["path_prefix"],
                    service=service_name,
                    strategy=RoutingStrategy.PREFIX_MATCH,
                    priority=service_config.get("priority", 0)
                )
                self.routing_rules.append(rule)
            
            # Sort rules by priority (higher priority first)
            self.routing_rules.sort(key=lambda x: x.priority, reverse=True)
            
            # Compile regex patterns
            self._compile_regex_patterns()
            
            logger.info(f"Initialized {len(self.routing_rules)} routing rules")
            
        except Exception as e:
            logger.error(f"Failed to initialize routing rules: {e}")
            raise
    
    def _compile_regex_patterns(self):
        """Compile regex patterns for regex-based rules"""
        for rule in self.routing_rules:
            if rule.strategy == RoutingStrategy.REGEX_MATCH:
                try:
                    rule.compiled_regex = re.compile(rule.pattern)
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{rule.pattern}': {e}")
                    # Fallback to prefix matching
                    rule.strategy = RoutingStrategy.PREFIX_MATCH
    
    def route_request(self, path: str, method: str = "GET", headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Route request to appropriate service
        
        Args:
            path: Request path
            method: HTTP method
            headers: Request headers
            
        Returns:
            Service name or None if no match found
        """
        try:
            headers = headers or {}
            
            # Normalize path
            normalized_path = self._normalize_path(path)
            
            # Try each routing rule in priority order
            for rule in self.routing_rules:
                if self._match_rule(rule, normalized_path, method, headers):
                    # Check service health before routing
                    if self._is_service_healthy(rule.service):
                        logger.debug(f"Routed {method} {path} to service: {rule.service}")
                        return rule.service
                    else:
                        logger.warning(f"Service {rule.service} is unhealthy, trying next rule")
                        continue
            
            logger.warning(f"No routing rule matched for {method} {path}")
            return None
            
        except Exception as e:
            logger.error(f"Error routing request {method} {path}: {e}")
            return None
    
    def _normalize_path(self, path: str) -> str:
        """Normalize request path"""
        # Remove query parameters
        if "?" in path:
            path = path.split("?")[0]
        
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        
        # Remove trailing slash (except for root)
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        
        return path
    
    def _match_rule(
        self, 
        rule: RoutingRule, 
        path: str, 
        method: str, 
        headers: Dict[str, str]
    ) -> bool:
        """Check if routing rule matches the request"""
        try:
            # Match based on strategy
            path_match = False
            
            if rule.strategy == RoutingStrategy.PREFIX_MATCH:
                path_match = path.startswith(rule.pattern)
            elif rule.strategy == RoutingStrategy.EXACT_MATCH:
                path_match = path == rule.pattern
            elif rule.strategy == RoutingStrategy.REGEX_MATCH and rule.compiled_regex:
                path_match = bool(rule.compiled_regex.match(path))
            elif rule.strategy == RoutingStrategy.WILDCARD_MATCH:
                path_match = self._wildcard_match(rule.pattern, path)
            
            if not path_match:
                return False
            
            # Check additional conditions
            if rule.conditions:
                return self._check_conditions(rule.conditions, method, headers)
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching rule {rule.pattern}: {e}")
            return False
    
    def _wildcard_match(self, pattern: str, path: str) -> bool:
        """Perform wildcard matching (* and ? supported)"""
        try:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            regex = re.compile(f"^{regex_pattern}$")
            return bool(regex.match(path))
        except Exception as e:
            logger.error(f"Wildcard matching error: {e}")
            return False
    
    def _check_conditions(
        self, 
        conditions: Dict[str, Any], 
        method: str, 
        headers: Dict[str, str]
    ) -> bool:
        """Check additional routing conditions"""
        try:
            # Method conditions
            if "methods" in conditions:
                allowed_methods = conditions["methods"]
                if isinstance(allowed_methods, str):
                    allowed_methods = [allowed_methods]
                if method not in allowed_methods:
                    return False
            
            # Header conditions
            if "headers" in conditions:
                header_conditions = conditions["headers"]
                for header_name, expected_value in header_conditions.items():
                    actual_value = headers.get(header_name)
                    if actual_value != expected_value:
                        return False
            
            # Header existence conditions
            if "required_headers" in conditions:
                required_headers = conditions["required_headers"]
                for header_name in required_headers:
                    if header_name not in headers:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {e}")
            return False
    
    def _is_service_healthy(self, service_name: str) -> bool:
        """Check if service is healthy and available"""
        # This would integrate with service discovery and health checking
        # For now, assume all configured services are healthy
        return service_name in self.config.service_routes
    
    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """
Add new routing rule dynamically"""
        try:
            # Compile regex if needed
            if rule.strategy == RoutingStrategy.REGEX_MATCH:
                try:
                    rule.compiled_regex = re.compile(rule.pattern)
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{rule.pattern}': {e}")
                    return False
            
            # Add rule and resort by priority
            self.routing_rules.append(rule)
            self.routing_rules.sort(key=lambda x: x.priority, reverse=True)
            
            logger.info(f"Added routing rule: {rule.pattern} -> {rule.service}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding routing rule: {e}")
            return False
    
    def remove_routing_rule(self, pattern: str, service: str) -> bool:
        """Remove routing rule"""
        try:
            initial_count = len(self.routing_rules)
            
            self.routing_rules = [
                rule for rule in self.routing_rules 
                if not (rule.pattern == pattern and rule.service == service)
            ]
            
            removed_count = initial_count - len(self.routing_rules)
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} routing rule(s) for {pattern} -> {service}")
                return True
            else:
                logger.warning(f"No routing rule found for {pattern} -> {service}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing routing rule: {e}")
            return False
    
    def update_service_registry(self, services: Dict[str, Dict[str, Any]]):
        """Update service registry from service discovery"""
        try:
            self.service_registry = services.copy()
            
            # Update routing rules based on discovered services
            self._update_rules_from_registry()
            
            logger.info(f"Updated service registry with {len(services)} services")
            
        except Exception as e:
            logger.error(f"Error updating service registry: {e}")
    
    def _update_rules_from_registry(self):
        """Update routing rules based on service registry"""
        try:
            # Add rules for newly discovered services
            for service_name, service_info in self.service_registry.items():
                # Check if we already have a rule for this service
                existing_rule = next(
                    (rule for rule in self.routing_rules if rule.service == service_name), 
                    None
                )
                
                if not existing_rule and "path_prefix" in service_info:
                    # Create new rule for discovered service
                    rule = RoutingRule(
                        pattern=service_info["path_prefix"],
                        service=service_name,
                        strategy=RoutingStrategy.PREFIX_MATCH,
                        priority=service_info.get("priority", 0)
                    )
                    self.routing_rules.append(rule)
            
            # Resort by priority
            self.routing_rules.sort(key=lambda x: x.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"Error updating rules from registry: {e}")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        try:
            service_counts = {}
            strategy_counts = {}
            
            for rule in self.routing_rules:
                # Count by service
                service_counts[rule.service] = service_counts.get(rule.service, 0) + 1
                
                # Count by strategy
                strategy_counts[rule.strategy.value] = strategy_counts.get(rule.strategy.value, 0) + 1
            
            return {
                "total_rules": len(self.routing_rules),
                "services": service_counts,
                "strategies": strategy_counts,
                "service_registry_size": len(self.service_registry)
            }
            
        except Exception as e:
            logger.error(f"Error getting routing stats: {e}")
            return {}
    
    def list_routing_rules(self) -> List[Dict[str, Any]]:
        """List all routing rules"""
        try:
            rules_list = []
            
            for rule in self.routing_rules:
                rule_dict = {
                    "pattern": rule.pattern,
                    "service": rule.service,
                    "strategy": rule.strategy.value,
                    "priority": rule.priority
                }
                
                if rule.conditions:
                    rule_dict["conditions"] = rule.conditions
                
                if rule.transformations:
                    rule_dict["transformations"] = rule.transformations
                
                rules_list.append(rule_dict)
            
            return rules_list
            
        except Exception as e:
            logger.error(f"Error listing routing rules: {e}")
            return []
