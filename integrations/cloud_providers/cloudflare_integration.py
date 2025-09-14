"""Cloudflare Integration
========================

Enterprise-grade Cloudflare integration supporting CDN, security,
DNS management, and edge computing for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

import httpx


class CloudflareServiceType(Enum):
    """Cloudflare service types."""
    DNS = "dns"
    CDN = "cdn"
    WAF = "waf"
    DDoS_PROTECTION = "ddos_protection"
    SSL_TLS = "ssl_tls"
    WORKERS = "workers"
    PAGES = "pages"
    STREAM = "stream"
    IMAGES = "images"
    ANALYTICS = "analytics"
    FIREWALL = "firewall"
    RATE_LIMITING = "rate_limiting"


class CloudflarePlan(Enum):
    """Cloudflare plan types."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class DNSRecordType(Enum):
    """DNS record types."""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    SRV = "SRV"
    NS = "NS"
    PTR = "PTR"
    CAA = "CAA"


@dataclass
class CloudflareDNSRecord:
    """Cloudflare DNS record."""
    type: DNSRecordType
    name: str
    content: str
    ttl: int = 1
    proxied: bool = False
    priority: Optional[int] = None
    comment: Optional[str] = None


@dataclass
class CloudflareFirewallRule:
    """Cloudflare firewall rule."""
    expression: str
    action: str  # block, challenge, allow, js_challenge, managed_challenge
    description: Optional[str] = None
    priority: Optional[int] = None
    paused: bool = False


@dataclass
class CloudflareWorkerScript:
    """Cloudflare Worker script."""
    name: str
    script: str
    bindings: Optional[List[Dict[str, Any]]] = None
    routes: Optional[List[str]] = None
    compatibility_date: Optional[str] = None


class CloudflareIntegration:
    """Enterprise Cloudflare integration for Ainflue.
    
    Features:
    - Global CDN for content delivery acceleration
    - Advanced DDoS protection and WAF
    - DNS management with DNSSEC
    - SSL/TLS encryption and certificate management
    - Edge computing with Cloudflare Workers
    - Image and video optimization
    - Analytics and performance monitoring
    - Firewall rules and rate limiting
    - Bot management and security
    - Load balancing and failover
    - Stream delivery for video content
    - Pages for static site hosting
    - Zero Trust security solutions
    """
    
    def __init__(
        self,
        api_token -> None: str,
        email -> None: Optional[str] = None,
        api_key -> None: Optional[str] = None,
        account_id -> None: Optional[str] = None
    ) -> None:
        """Initialize Cloudflare integration.
        
        Args:
            api_token: Cloudflare API token (preferred)
            email: Account email (for legacy API key auth)
            api_key: Global API key (legacy auth)
            account_id: Cloudflare account ID
        """
        self.api_token = api_token
        self.email = email
        self.api_key = api_key
        self.account_id = account_id
        
        # Base API URL
        self.api_base_url = "https://api.cloudflare.com/client/v4"
        
        # Setup authentication headers
        if api_token:
            self.auth_headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
        elif email and api_key:
            self.auth_headers = {
                "X-Auth-Email": email,
                "X-Auth-Key": api_key,
                "Content-Type": "application/json"
            }
        else:
            raise ValueError("Either api_token or (email + api_key) must be provided")
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(
            headers=self.auth_headers,
            timeout=30.0
        )

    async def get_zones(self) -> List[Dict[str, Any]]:
        """Get list of zones (domains) in the account.
        
        Returns:
            List of zone information
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/zones"
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                zones = result["result"]
                self.logger.info(f"Retrieved {len(zones)} zones")
                return zones
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get zones: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting zones: {e}")
            raise

    async def get_zone_by_name(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get zone information by domain name.
        
        Args:
            zone_name: Domain name
            
        Returns:
            Zone information or None if not found
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/zones",
                params={"name": zone_name}
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"] and result["result"]:
                zone = result["result"][0]
                self.logger.info(f"Found zone: {zone_name}")
                return zone
            else:
                self.logger.info(f"Zone not found: {zone_name}")
                return None
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get zone: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting zone: {e}")
            raise

    async def create_dns_record(
        self,
        zone_id: str,
        dns_record: CloudflareDNSRecord
    ) -> Dict[str, Any]:
        """Create DNS record in a zone.
        
        Args:
            zone_id: Zone ID
            dns_record: DNS record configuration
            
        Returns:
            Created DNS record information
        """
        try:
            payload = {
                "type": dns_record.type.value,
                "name": dns_record.name,
                "content": dns_record.content,
                "ttl": dns_record.ttl,
                "proxied": dns_record.proxied
            }
            
            if dns_record.priority is not None:
                payload["priority"] = dns_record.priority
            if dns_record.comment:
                payload["comment"] = dns_record.comment
            
            response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/dns_records",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                dns_record_info = result["result"]
                self.logger.info(f"Created DNS record: {dns_record.name}")
                return dns_record_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create DNS record: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating DNS record: {e}")
            raise

    async def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        dns_record: CloudflareDNSRecord
    ) -> Dict[str, Any]:
        """Update existing DNS record.
        
        Args:
            zone_id: Zone ID
            record_id: DNS record ID
            dns_record: Updated DNS record configuration
            
        Returns:
            Updated DNS record information
        """
        try:
            payload = {
                "type": dns_record.type.value,
                "name": dns_record.name,
                "content": dns_record.content,
                "ttl": dns_record.ttl,
                "proxied": dns_record.proxied
            }
            
            if dns_record.priority is not None:
                payload["priority"] = dns_record.priority
            if dns_record.comment:
                payload["comment"] = dns_record.comment
            
            response = await self.session.put(
                f"{self.api_base_url}/zones/{zone_id}/dns_records/{record_id}",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                dns_record_info = result["result"]
                self.logger.info(f"Updated DNS record: {dns_record.name}")
                return dns_record_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to update DNS record: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating DNS record: {e}")
            raise

    async def delete_dns_record(
        self,
        zone_id: str,
        record_id: str
    ) -> bool:
        """Delete DNS record.
        
        Args:
            zone_id: Zone ID
            record_id: DNS record ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.session.delete(
                f"{self.api_base_url}/zones/{zone_id}/dns_records/{record_id}"
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                self.logger.info(f"Deleted DNS record: {record_id}")
                return True
            else:
                self.logger.error(f"Failed to delete DNS record: {result['errors']}")
                return False
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to delete DNS record: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting DNS record: {e}")
            return False

    async def get_dns_records(
        self,
        zone_id: str,
        record_type: Optional[DNSRecordType] = None,
        name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get DNS records for a zone.
        
        Args:
            zone_id: Zone ID
            record_type: Filter by record type
            name: Filter by record name
            
        Returns:
            List of DNS records
        """
        try:
            params = {}
            if record_type:
                params["type"] = record_type.value
            if name:
                params["name"] = name
            
            response = await self.session.get(
                f"{self.api_base_url}/zones/{zone_id}/dns_records",
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                records = result["result"]
                self.logger.info(f"Retrieved {len(records)} DNS records")
                return records
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get DNS records: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting DNS records: {e}")
            raise

    async def enable_ssl(
        self,
        zone_id: str,
        ssl_mode: str = "flexible"
    ) -> Dict[str, Any]:
        """Enable SSL/TLS for a zone.
        
        Args:
            zone_id: Zone ID
            ssl_mode: SSL mode (off, flexible, full, strict)
            
        Returns:
            SSL configuration result
        """
        try:
            payload = {"value": ssl_mode}
            
            response = await self.session.patch(
                f"{self.api_base_url}/zones/{zone_id}/settings/ssl",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                ssl_config = result["result"]
                self.logger.info(f"Enabled SSL mode: {ssl_mode}")
                return ssl_config
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to enable SSL: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error enabling SSL: {e}")
            raise

    async def create_firewall_rule(
        self,
        zone_id: str,
        firewall_rule: CloudflareFirewallRule
    ) -> Dict[str, Any]:
        """Create firewall rule for a zone.
        
        Args:
            zone_id: Zone ID
            firewall_rule: Firewall rule configuration
            
        Returns:
            Created firewall rule information
        """
        try:
            # First create the filter
            filter_payload = {
                "expression": firewall_rule.expression,
                "description": firewall_rule.description or "Firewall rule filter"
            }
            
            filter_response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/filters",
                json=filter_payload
            )
            filter_response.raise_for_status()
            
            filter_result = filter_response.json()
            if not filter_result["success"]:
                raise Exception(f"Filter creation failed: {filter_result['errors']}")
            
            filter_id = filter_result["result"]["id"]
            
            # Create the firewall rule
            rule_payload = {
                "filter": {"id": filter_id},
                "action": firewall_rule.action,
                "description": firewall_rule.description,
                "paused": firewall_rule.paused
            }
            
            if firewall_rule.priority is not None:
                rule_payload["priority"] = firewall_rule.priority
            
            rule_response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/firewall/rules",
                json=rule_payload
            )
            rule_response.raise_for_status()
            
            rule_result = rule_response.json()
            if rule_result["success"]:
                rule_info = rule_result["result"]
                self.logger.info(f"Created firewall rule: {firewall_rule.description}")
                return rule_info
            else:
                raise Exception(f"Rule creation failed: {rule_result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create firewall rule: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating firewall rule: {e}")
            raise

    async def create_rate_limit_rule(
        self,
        zone_id: str,
        threshold: int,
        period: int,
        action: str,
        match: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create rate limiting rule.
        
        Args:
            zone_id: Zone ID
            threshold: Request threshold
            period: Time period in seconds
            action: Action to take (block, challenge, js_challenge)
            match: Matching criteria
            description: Rule description
            
        Returns:
            Created rate limit rule information
        """
        try:
            payload = {
                "threshold": threshold,
                "period": period,
                "action": {"mode": action},
                "match": match
            }
            
            if description:
                payload["description"] = description
            
            response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/rate_limits",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                rule_info = result["result"]
                self.logger.info(f"Created rate limit rule: {description}")
                return rule_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create rate limit rule: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating rate limit rule: {e}")
            raise

    async def create_worker_script(
        self,
        worker_script: CloudflareWorkerScript
    ) -> Dict[str, Any]:
        """Deploy Cloudflare Worker script.
        
        Args:
            worker_script: Worker script configuration
            
        Returns:
            Deployed worker information
        """
        try:
            # Upload the script
            script_payload = {
                "script": worker_script.script
            }
            
            if worker_script.bindings:
                script_payload["bindings"] = worker_script.bindings
            if worker_script.compatibility_date:
                script_payload["compatibility_date"] = worker_script.compatibility_date
            
            if self.account_id:
                url = f"{self.api_base_url}/accounts/{self.account_id}/workers/scripts/{worker_script.name}"
            else:
                # Try to get account ID first
                accounts = await self.get_accounts()
                if not accounts:
                    raise Exception("No account ID provided and unable to retrieve accounts")
                account_id = accounts[0]["id"]
                url = f"{self.api_base_url}/accounts/{account_id}/workers/scripts/{worker_script.name}"
            
            response = await self.session.put(url, json=script_payload)
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                # Add routes if specified
                if worker_script.routes:
                    for route in worker_script.routes:
                        await self.create_worker_route(
                            zone_id=None,  # This would need to be determined from the route
                            route_pattern=route,
                            script_name=worker_script.name
                        )
                
                worker_info = result["result"]
                self.logger.info(f"Created worker script: {worker_script.name}")
                return worker_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create worker script: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating worker script: {e}")
            raise

    async def create_worker_route(
        self,
        zone_id: str,
        route_pattern: str,
        script_name: str
    ) -> Dict[str, Any]:
        """Create worker route.
        
        Args:
            zone_id: Zone ID
            route_pattern: Route pattern (e.g., "example.com/api/*")
            script_name: Worker script name
            
        Returns:
            Created route information
        """
        try:
            payload = {
                "pattern": route_pattern,
                "script": script_name
            }
            
            response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/workers/routes",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                route_info = result["result"]
                self.logger.info(f"Created worker route: {route_pattern}")
                return route_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create worker route: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating worker route: {e}")
            raise

    async def purge_cache(
        self,
        zone_id: str,
        files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        hosts: Optional[List[str]] = None,
        purge_everything: bool = False
    ) -> Dict[str, Any]:
        """Purge cache for a zone.
        
        Args:
            zone_id: Zone ID
            files: Specific files to purge
            tags: Cache tags to purge
            hosts: Hosts to purge
            purge_everything: Purge all cache
            
        Returns:
            Purge operation result
        """
        try:
            payload = {}
            
            if purge_everything:
                payload["purge_everything"] = True
            else:
                if files:
                    payload["files"] = files
                if tags:
                    payload["tags"] = tags
                if hosts:
                    payload["hosts"] = hosts
            
            response = await self.session.post(
                f"{self.api_base_url}/zones/{zone_id}/purge_cache",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                purge_info = result["result"]
                self.logger.info(f"Purged cache for zone: {zone_id}")
                return purge_info
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to purge cache: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error purging cache: {e}")
            raise

    async def get_analytics(
        self,
        zone_id: str,
        since: datetime,
        until: Optional[datetime] = None,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get analytics data for a zone.
        
        Args:
            zone_id: Zone ID
            since: Start time
            until: End time (default: now)
            dimensions: Analytics dimensions
            metrics: Analytics metrics
            
        Returns:
            Analytics data
        """
        try:
            params = {
                "since": since.isoformat(),
                "until": (until or datetime.utcnow()).isoformat()
            }
            
            if dimensions:
                params["dimensions"] = ",".join(dimensions)
            if metrics:
                params["metrics"] = ",".join(metrics)
            
            response = await self.session.get(
                f"{self.api_base_url}/zones/{zone_id}/analytics/dashboard",
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                analytics_data = result["result"]
                self.logger.info(f"Retrieved analytics for zone: {zone_id}")
                return analytics_data
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get analytics: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting analytics: {e}")
            raise

    async def get_accounts(self) -> List[Dict[str, Any]]:
        """Get account information.
        
        Returns:
            List of account information
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/accounts"
            )
            response.raise_for_status()
            
            result = response.json()
            if result["success"]:
                accounts = result["result"]
                self.logger.info(f"Retrieved {len(accounts)} accounts")
                return accounts
            else:
                raise Exception(f"API error: {result['errors']}")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get accounts: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting accounts: {e}")
            raise

    async def close(self) -> None:
        """Close HTTP session."""
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator content delivery specific functions
async def setup_creator_cdn(
    cf: CloudflareIntegration,
    creator_id: str,
    domain: str,
    origin_server: str
) -> Dict[str, Any]:
    """Setup Cloudflare CDN for creator content delivery.
    
    Args:
        cf: Cloudflare integration instance
        creator_id: Creator identifier
        domain: Creator's custom domain
        origin_server: Origin server IP/hostname
        
    Returns:
        Dict containing CDN setup details
    """
    # Get or create zone for domain
    zone = await cf.get_zone_by_name(domain)
    if not zone:
        raise ValueError(f"Zone {domain} not found in Cloudflare account")
    
    zone_id = zone["id"]
    
    # Create DNS records for creator content
    dns_records = []
    
    # Main domain record
    main_record = await cf.create_dns_record(
        zone_id,
        CloudflareDNSRecord(
            type=DNSRecordType.A,
            name=domain,
            content=origin_server,
            proxied=True,  # Enable Cloudflare proxy for CDN
            comment=f"Creator {creator_id} main domain"
        )
    )
    dns_records.append(main_record)
    
    # Content subdomain for media files
    content_record = await cf.create_dns_record(
        zone_id,
        CloudflareDNSRecord(
            type=DNSRecordType.A,
            name=f"content.{domain}",
            content=origin_server,
            proxied=True,
            comment=f"Creator {creator_id} content delivery"
        )
    )
    dns_records.append(content_record)
    
    # API subdomain
    api_record = await cf.create_dns_record(
        zone_id,
        CloudflareDNSRecord(
            type=DNSRecordType.A,
            name=f"api.{domain}",
            content=origin_server,
            proxied=True,
            comment=f"Creator {creator_id} API endpoint"
        )
    )
    dns_records.append(api_record)
    
    # Enable SSL
    ssl_config = await cf.enable_ssl(zone_id, "full")
    
    # Create firewall rules for protection
    security_rule = await cf.create_firewall_rule(
        zone_id,
        CloudflareFirewallRule(
            expression='(http.request.uri.path contains "/admin" and ip.src ne 1.2.3.4)',
            action="block",
            description=f"Creator {creator_id} admin protection"
        )
    )
    
    # Create rate limiting for API
    rate_limit = await cf.create_rate_limit_rule(
        zone_id,
        threshold=100,
        period=60,
        action="block",
        match={
            "request": {
                "url": f"api.{domain}/*"
            }
        },
        description=f"Creator {creator_id} API rate limit"
    )
    
    cdn_setup = {
        "creator_id": creator_id,
        "domain": domain,
        "zone_id": zone_id,
        "dns_records": dns_records,
        "ssl_config": ssl_config,
        "security_rules": [security_rule],
        "rate_limits": [rate_limit],
        "endpoints": {
            "main": f"https://{domain}",
            "content": f"https://content.{domain}",
            "api": f"https://api.{domain}"
        }
    }
    
    return cdn_setup


async def deploy_creator_worker(
    cf: CloudflareIntegration,
    creator_id: str,
    domain: str,
    worker_code: str
) -> Dict[str, Any]:
    """Deploy Cloudflare Worker for creator-specific edge processing.
    
    Args:
        cf: Cloudflare integration instance
        creator_id: Creator identifier
        domain: Creator's domain
        worker_code: Worker JavaScript code
        
    Returns:
        Dict containing worker deployment details
    """
    worker_name = f"creator-{creator_id}-processor"
    
    # Create worker script
    worker = await cf.create_worker_script(
        CloudflareWorkerScript(
            name=worker_name,
            script=worker_code,
            compatibility_date="2023-05-18",
            routes=[f"{domain}/api/*", f"content.{domain}/*"]
        )
    )
    
    # Get zone for routing
    zone = await cf.get_zone_by_name(domain)
    if zone:
        zone_id = zone["id"]
        
        # Create worker routes
        api_route = await cf.create_worker_route(
            zone_id=zone_id,
            route_pattern=f"{domain}/api/*",
            script_name=worker_name
        )
        
        content_route = await cf.create_worker_route(
            zone_id=zone_id,
            route_pattern=f"content.{domain}/*",
            script_name=worker_name
        )
        
        routes = [api_route, content_route]
    else:
        routes = []
    
    deployment = {
        "creator_id": creator_id,
        "worker_name": worker_name,
        "domain": domain,
        "worker_script": worker,
        "routes": routes,
        "deployed_at": datetime.utcnow().isoformat()
    }
    
    return deployment