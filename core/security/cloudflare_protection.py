"""CloudFlare DDoS Protection Integration
=====================================

CloudFlare API integration for DDoS protection, rate limiting, and security controls.
Provides automated threat mitigation and security rule management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from config.security.production_security import CloudFlareConfig, get_security_config


logger = logging.getLogger(__name__)


@dataclass
class CloudFlareResponse:
    """CloudFlare API response"""
    success: bool
    data: Any
    errors: List[str]
    messages: List[str]


class CloudFlareSecurityManager:
    """CloudFlare security and DDoS protection manager"""
    
    def __init__(self, config: Optional[CloudFlareConfig] = None):
        self.config = config or get_security_config().cloudflare
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()
    
    async def _create_session(self):
        """Create HTTP session with proper headers"""
        headers = {
            "Content-Type": "application/json",
        }
        
        # Use API token (preferred) or API key + email
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        elif self.config.api_key and self.config.email:
            headers["X-Auth-Key"] = self.config.api_key
            headers["X-Auth-Email"] = self.config.email
        else:
            raise ValueError("CloudFlare API credentials not configured")
            
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> CloudFlareResponse:
        """Make API request to CloudFlare"""
        if not self.session:
            await self._create_session()
            
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                return CloudFlareResponse(
                    success=response_data.get("success", False),
                    data=response_data.get("result"),
                    errors=response_data.get("errors", []),
                    messages=response_data.get("messages", [])
                )
                
        except Exception as e:
            logger.error(f"CloudFlare API request failed: {e}")
            return CloudFlareResponse(
                success=False,
                data=None,
                errors=[str(e)],
                messages=[]
            )
    
    async def get_zone_info(self) -> CloudFlareResponse:
        """Get zone information"""
        endpoint = f"/zones/{self.config.zone_id}"
        return await self._make_request("GET", endpoint)
    
    async def update_security_level(self, level: str) -> CloudFlareResponse:
        """Update security level (essentially_off, low, medium, high, under_attack)"""
        endpoint = f"/zones/{self.config.zone_id}/settings/security_level"
        data = {"value": level}
        return await self._make_request("PATCH", endpoint, data)
    
    async def enable_ddos_protection(self) -> CloudFlareResponse:
        """Enable DDoS protection"""
        # CloudFlare's DDoS protection is always on, but we can configure security level
        return await self.update_security_level(self.config.ddos_protection_level)
    
    async def create_rate_limiting_rule(
        self,
        description: str,
        threshold: int,
        period: int,
        action: str = "challenge",
        match_criteria: Optional[Dict] = None
    ) -> CloudFlareResponse:
        """Create rate limiting rule"""
        endpoint = f"/zones/{self.config.zone_id}/rate_limits"
        
        # Default match criteria
        if not match_criteria:
            match_criteria = {
                "request": {
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "schemes": ["HTTP", "HTTPS"]
                }
            }
        
        data = {
            "threshold": threshold,
            "period": period,
            "action": {
                "mode": action,
                "timeout": self.config.challenge_ttl if action == "challenge" else None
            },
            "match": match_criteria,
            "description": description,
            "disabled": False
        }
        
        return await self._make_request("POST", endpoint, data)
    
    async def create_firewall_rule(
        self,
        expression: str,
        action: str,
        description: str
    ) -> CloudFlareResponse:
        """Create firewall rule"""
        endpoint = f"/zones/{self.config.zone_id}/firewall/rules"
        
        # First create the filter
        filter_data = {
            "expression": expression,
            "description": f"Filter for {description}"
        }
        
        filter_response = await self._make_request(
            "POST", 
            f"/zones/{self.config.zone_id}/filters", 
            filter_data
        )
        
        if not filter_response.success:
            return filter_response
        
        filter_id = filter_response.data["id"]
        
        # Create the firewall rule
        rule_data = {
            "filter": {"id": filter_id},
            "action": action,
            "description": description,
            "paused": False
        }
        
        return await self._make_request("POST", endpoint, rule_data)
    
    async def block_ip_address(self, ip_address: str, reason: str) -> CloudFlareResponse:
        """Block specific IP address"""
        expression = f'(ip.src eq {ip_address})'
        return await self.create_firewall_rule(
            expression=expression,
            action="block",
            description=f"Block {ip_address} - {reason}"
        )
    
    async def block_country(self, country_code: str, reason: str) -> CloudFlareResponse:
        """Block traffic from specific country"""
        expression = f'(ip.geoip.country eq "{country_code.upper()}")'
        return await self.create_firewall_rule(
            expression=expression,
            action="block", 
            description=f"Block {country_code} - {reason}"
        )
    
    async def setup_production_security(self) -> Dict[str, CloudFlareResponse]:
        """Setup production security configuration"""
        results = {}
        
        # 1. Enable high security level
        results["security_level"] = await self.update_security_level("high")
        
        # 2. Create API rate limiting rule
        results["api_rate_limit"] = await self.create_rate_limiting_rule(
            description="API Rate Limiting",
            threshold=self.config.requests_per_minute,
            period=60,
            action="challenge",
            match_criteria={
                "request": {
                    "methods": ["POST", "PUT", "DELETE"],
                    "url_pattern": "*/api/*"
                }
            }
        )
        
        # 3. Create aggressive rate limiting for login endpoints
        results["login_rate_limit"] = await self.create_rate_limiting_rule(
            description="Login Rate Limiting",
            threshold=5,
            period=300,  # 5 minutes
            action="block",
            match_criteria={
                "request": {
                    "methods": ["POST"],
                    "url_pattern": "*/auth/login*"
                }
            }
        )
        
        # 4. Block known bad bots
        results["block_bad_bots"] = await self.create_firewall_rule(
            expression='(http.user_agent contains "sqlmap") or (http.user_agent contains "nikto") or (http.user_agent contains "nmap")',
            action="block",
            description="Block known security scanners"
        )
        
        # 5. Challenge suspicious requests
        results["challenge_suspicious"] = await self.create_firewall_rule(
            expression='(http.request.uri.path contains "../") or (http.request.uri.query contains "union select") or (http.request.uri.query contains "<script")',
            action="challenge",
            description="Challenge suspicious requests"
        )
        
        return results
    
    async def get_security_analytics(self) -> Dict[str, Any]:
        """Get security analytics and threat data"""
        endpoint = f"/zones/{self.config.zone_id}/analytics/dashboard"
        
        # Get analytics for the last 24 hours
        since = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        until = datetime.utcnow().isoformat() + "Z"
        
        params = {
            "since": since,
            "until": until,
            "continuous": "true"
        }
        
        analytics_response = await self._make_request("GET", f"{endpoint}?{params}")
        
        if analytics_response.success:
            return {
                "threats_mitigated": analytics_response.data.get("totals", {}).get("threats", {}).get("all", 0),
                "requests_total": analytics_response.data.get("totals", {}).get("requests", {}).get("all", 0),
                "bandwidth_total": analytics_response.data.get("totals", {}).get("bytes", {}).get("all", 0),
                "unique_visitors": analytics_response.data.get("totals", {}).get("uniques", {}).get("all", 0)
            }
        
        return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of CloudFlare integration"""
        health_status = {
            "status": "unknown",
            "zone_accessible": False,
            "api_functional": False,
            "security_level": "unknown",
            "errors": []
        }
        
        try:
            # Test zone access
            zone_response = await self.get_zone_info()
            if zone_response.success:
                health_status["zone_accessible"] = True
                health_status["api_functional"] = True
                health_status["zone_name"] = zone_response.data.get("name")
                health_status["zone_status"] = zone_response.data.get("status")
            else:
                health_status["errors"].extend(zone_response.errors)
            
            # Get current security level
            security_response = await self._make_request(
                "GET", 
                f"/zones/{self.config.zone_id}/settings/security_level"
            )
            if security_response.success:
                health_status["security_level"] = security_response.data.get("value")
            
            # Overall status
            if health_status["zone_accessible"] and health_status["api_functional"]:
                health_status["status"] = "healthy"
            else:
                health_status["status"] = "unhealthy"
                
        except Exception as e:
            health_status["status"] = "error"
            health_status["errors"].append(str(e))
        
        return health_status


async def setup_cloudflare_protection() -> Dict[str, Any]:
    """Setup CloudFlare protection (main entry point)"""
    config = get_security_config().cloudflare
    
    if not config.enabled:
        return {"status": "disabled", "message": "CloudFlare protection is disabled"}
    
    async with CloudFlareSecurityManager(config) as cf_manager:
        # Health check first
        health = await cf_manager.health_check()
        if health["status"] != "healthy":
            return {
                "status": "error",
                "message": "CloudFlare health check failed",
                "details": health
            }
        
        # Setup production security
        setup_results = await cf_manager.setup_production_security()
        
        # Count successful setups
        successful_setups = sum(1 for result in setup_results.values() if result.success)
        total_setups = len(setup_results)
        
        return {
            "status": "success" if successful_setups == total_setups else "partial",
            "message": f"CloudFlare security setup completed: {successful_setups}/{total_setups} successful",
            "health": health,
            "setup_results": {
                name: {"success": result.success, "errors": result.errors}
                for name, result in setup_results.items()
            }
        }


if __name__ == "__main__":
    async def main():
        result = await setup_cloudflare_protection()
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())