"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

DNS Discovery Template for iacherie Platform
==========================================

Production-ready DNS-based service discovery with:
- SRV record service discovery
- A/AAAA record resolution
- TXT record metadata support
- DNS caching and optimization
- Health checking via DNS
- Multi-resolver support

Author: Fahed Mlaiel (mlaiel@live.de)
DNS & Network Engineering Expert
"""

import asyncio
import json
import logging
import time
import socket
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

import dns.resolver
import dns.asyncresolver
import dns.exception
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
dns_queries_counter = Counter('dns_queries_total', 'Total DNS queries', ['query_type', 'status'])
dns_latency_histogram = Histogram('dns_query_duration_seconds', 'DNS query latency', ['query_type'])
dns_cache_hits_counter = Counter('dns_cache_hits_total', 'DNS cache hits', ['query_type'])
dns_services_gauge = Gauge('dns_discovered_services', 'Number of services discovered via DNS')

class DNSRecordType(str, Enum):
    """DNS record types for service discovery"""
    A = "A"
    AAAA = "AAAA"
    SRV = "SRV"
    TXT = "TXT"
    CNAME = "CNAME"
    PTR = "PTR"

@dataclass
class DNSServiceRecord:
    """DNS service record information"""
    name: str
    type: DNSRecordType
    target: str
    port: Optional[int] = None
    priority: Optional[int] = None
    weight: Optional[int] = None
    ttl: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class DiscoveredService:
    """Discovered service via DNS"""
    service_name: str
    protocol: str
    domain: str
    instances: List[DNSServiceRecord]
    metadata: Dict[str, str] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

class DNSCache:
    """DNS resolution cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached DNS result"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() < entry["expires"]:
                dns_cache_hits_counter.labels(query_type="cached").inc()
                return entry["data"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Cache DNS result"""
        ttl = ttl or self.default_ttl
        expires = datetime.utcnow() + timedelta(seconds=ttl)
        self.cache[key] = {
            "data": data,
            "expires": expires
        }
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now >= entry["expires"]
        ]
        for key in expired_keys:
            del self.cache[key]

class DNSDiscoveryClient:
    """
    DNS-based service discovery client
    
    Features:
    - SRV record service discovery
    - A/AAAA record resolution for endpoints
    - TXT record metadata parsing
    - DNS caching with TTL support
    - Multiple DNS resolver support
    - Health checking integration
    """
    
    def __init__(self, nameservers: Optional[List[str]] = None, search_domains: Optional[List[str]] = None):
        self.nameservers = nameservers or []
        self.search_domains = search_domains or []
        
        # Configure DNS resolver
        self.resolver = dns.resolver.Resolver()
        self.async_resolver = dns.asyncresolver.Resolver()
        
        if self.nameservers:
            self.resolver.nameservers = self.nameservers
            self.async_resolver.nameservers = self.nameservers
        
        if self.search_domains:
            self.resolver.search = [dns.name.from_text(domain) for domain in self.search_domains]
            self.async_resolver.search = [dns.name.from_text(domain) for domain in self.search_domains]
        
        # DNS cache
        self.cache = DNSCache()
        
        # Service discovery patterns
        self.service_patterns = {
            "consul": "_consul._tcp.{domain}",
            "etcd": "_etcd._tcp.{domain}",
            "kafka": "_kafka._tcp.{domain}",
            "redis": "_redis._tcp.{domain}",
            "postgresql": "_postgresql._tcp.{domain}",
            "mongodb": "_mongodb._tcp.{domain}",
            "elasticsearch": "_elasticsearch._tcp.{domain}",
            "custom": "_{service}._tcp.{domain}"
        }
    
    async def discover_service(self, service_name: str, protocol: str = "tcp", domain: str = "local") -> Optional[DiscoveredService]:
        """Discover service instances via DNS SRV records"""
        try:
            with dns_latency_histogram.labels(query_type="srv").time():
                # Build SRV query
                srv_query = f"_{service_name}._{protocol}.{domain}"
                cache_key = f"srv:{srv_query}"
                
                # Check cache first
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    return cached_result
                
                # Query SRV records
                try:
                    srv_records = await self.async_resolver.resolve(srv_query, 'SRV')
                except dns.exception.DNSException as e:
                    dns_queries_counter.labels(query_type="srv", status="not_found").inc()
                    logger.debug(f"No SRV records found for {srv_query}: {e}")
                    return None
                
                instances = []
                
                for srv_record in srv_records:
                    # Resolve A/AAAA records for target
                    target_ips = await self._resolve_hostname(str(srv_record.target).rstrip('.'))
                    
                    for ip in target_ips:
                        dns_service_record = DNSServiceRecord(
                            name=str(srv_record.target).rstrip('.'),
                            type=DNSRecordType.SRV,
                            target=ip,
                            port=srv_record.port,
                            priority=srv_record.priority,
                            weight=srv_record.weight,
                            ttl=srv_records.rrset.ttl
                        )
                        instances.append(dns_service_record)
                
                # Get TXT records for metadata
                metadata = await self._get_txt_metadata(srv_query)
                
                discovered_service = DiscoveredService(
                    service_name=service_name,
                    protocol=protocol,
                    domain=domain,
                    instances=instances,
                    metadata=metadata
                )
                
                # Cache result
                self.cache.set(cache_key, discovered_service, srv_records.rrset.ttl)
                
                dns_queries_counter.labels(query_type="srv", status="success").inc()
                dns_services_gauge.set(len(instances))
                
                logger.info(f"Discovered {len(instances)} instances for service {service_name}")
                return discovered_service
                
        except Exception as e:
            dns_queries_counter.labels(query_type="srv", status="error").inc()
            logger.error(f"Failed to discover service {service_name}: {e}")
            return None
    
    async def discover_services_by_pattern(self, pattern: str, domain: str = "local") -> List[DiscoveredService]:
        """Discover multiple services using a naming pattern"""
        try:
            discovered_services = []
            
            # Common service types to check
            common_services = [
                "api", "web", "database", "cache", "queue", "auth", "storage",
                "monitoring", "logging", "metrics", "backup", "search"
            ]
            
            for service in common_services:
                if pattern == "consul":
                    query_pattern = self.service_patterns["consul"].format(domain=domain)
                elif pattern == "custom":
                    query_pattern = self.service_patterns["custom"].format(service=service, domain=domain)
                else:
                    continue
                
                discovered = await self.discover_service(service, "tcp", domain)
                if discovered and discovered.instances:
                    discovered_services.append(discovered)
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"Failed to discover services by pattern {pattern}: {e}")
            return []
    
    async def resolve_service_endpoint(self, service_name: str, protocol: str = "tcp", domain: str = "local") -> List[Tuple[str, int]]:
        """Resolve service to list of (host, port) endpoints"""
        try:
            discovered = await self.discover_service(service_name, protocol, domain)
            
            if not discovered:
                return []
            
            endpoints = []
            for instance in discovered.instances:
                if instance.target and instance.port:
                    endpoints.append((instance.target, instance.port))
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to resolve service endpoint {service_name}: {e}")
            return []
    
    async def _resolve_hostname(self, hostname: str) -> List[str]:
        """Resolve hostname to IP addresses"""
        try:
            cache_key = f"a:{hostname}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            ips = []
            
            # Try A records (IPv4)
            try:
                a_records = await self.async_resolver.resolve(hostname, 'A')
                ips.extend([str(record) for record in a_records])
                dns_queries_counter.labels(query_type="a", status="success").inc()
            except dns.exception.DNSException:
                dns_queries_counter.labels(query_type="a", status="not_found").inc()
            
            # Try AAAA records (IPv6)
            try:
                aaaa_records = await self.async_resolver.resolve(hostname, 'AAAA')
                ips.extend([str(record) for record in aaaa_records])
                dns_queries_counter.labels(query_type="aaaa", status="success").inc()
            except dns.exception.DNSException:
                dns_queries_counter.labels(query_type="aaaa", status="not_found").inc()
            
            # Cache result
            if ips:
                self.cache.set(cache_key, ips, 300)  # 5 minute TTL for A/AAAA records
            
            return ips
            
        except Exception as e:
            logger.error(f"Failed to resolve hostname {hostname}: {e}")
            return []
    
    async def _get_txt_metadata(self, query: str) -> Dict[str, str]:
        """Get TXT record metadata for service"""
        try:
            cache_key = f"txt:{query}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            metadata = {}
            
            try:
                txt_records = await self.async_resolver.resolve(query, 'TXT')
                
                for txt_record in txt_records:
                    # Parse key=value pairs from TXT record
                    for string in txt_record.strings:
                        text = string.decode('utf-8')
                        if '=' in text:
                            key, value = text.split('=', 1)
                            metadata[key.strip()] = value.strip()
                        else:
                            metadata[text] = ""
                
                dns_queries_counter.labels(query_type="txt", status="success").inc()
                
            except dns.exception.DNSException:
                dns_queries_counter.labels(query_type="txt", status="not_found").inc()
            
            # Cache metadata
            self.cache.set(cache_key, metadata, 300)
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get TXT metadata for {query}: {e}")
            return {}
    
    async def health_check_service(self, service_name: str, protocol: str = "tcp", domain: str = "local") -> Dict[str, Any]:
        """Perform health check on discovered service instances"""
        try:
            discovered = await self.discover_service(service_name, protocol, domain)
            
            if not discovered:
                return {"status": "not_found", "instances": []}
            
            health_results = {
                "service_name": service_name,
                "status": "unknown",
                "total_instances": len(discovered.instances),
                "healthy_instances": 0,
                "unhealthy_instances": 0,
                "instances": []
            }
            
            for instance in discovered.instances:
                instance_health = await self._check_instance_health(instance.target, instance.port)
                
                instance_result = {
                    "target": instance.target,
                    "port": instance.port,
                    "status": instance_health["status"],
                    "response_time_ms": instance_health["response_time_ms"],
                    "error": instance_health.get("error")
                }
                
                health_results["instances"].append(instance_result)
                
                if instance_health["status"] == "healthy":
                    health_results["healthy_instances"] += 1
                else:
                    health_results["unhealthy_instances"] += 1
            
            # Determine overall status
            if health_results["healthy_instances"] == health_results["total_instances"]:
                health_results["status"] = "healthy"
            elif health_results["healthy_instances"] > 0:
                health_results["status"] = "degraded"
            else:
                health_results["status"] = "unhealthy"
            
            return health_results
            
        except Exception as e:
            logger.error(f"Failed to health check service {service_name}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _check_instance_health(self, host: str, port: int) -> Dict[str, Any]:
        """Check health of individual service instance"""
        start_time = time.time()
        
        try:
            # Simple TCP connection check
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=5.0)
            
            writer.close()
            await writer.wait_closed()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time_ms
            }
            
        except asyncio.TimeoutError:
            return {
                "status": "unhealthy",
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": "Connection timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": str(e)
            }
    
    async def watch_service_changes(self, service_name: str, callback, protocol: str = "tcp", domain: str = "local", interval: int = 30):
        """Watch for changes in service discovery (polling-based)"""
        try:
            last_instances = set()
            
            while True:
                discovered = await self.discover_service(service_name, protocol, domain)
                
                current_instances = set()
                if discovered:
                    current_instances = {
                        (instance.target, instance.port)
                        for instance in discovered.instances
                    }
                
                # Check for changes
                if current_instances != last_instances:
                    added = current_instances - last_instances
                    removed = last_instances - current_instances
                    
                    change_event = {
                        "service_name": service_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "added": list(added),
                        "removed": list(removed),
                        "current": list(current_instances)
                    }
                    
                    try:
                        await callback(change_event)
                    except Exception as e:
                        logger.error(f"Service watch callback error: {e}")
                    
                    last_instances = current_instances
                
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            logger.info(f"Stopped watching service {service_name}")
        except Exception as e:
            logger.error(f"Service watch error for {service_name}: {e}")
    
    def clear_cache(self):
        """Clear DNS cache"""
        self.cache.clear()
        logger.info("DNS cache cleared")
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        self.cache.cleanup_expired()

class DnsDiscoveryTemplate:
    """
    DNS Discovery Template for iacherie Platform
    
    A comprehensive DNS-based service discovery that provides:
    - SRV record service discovery
    - A/AAAA record endpoint resolution
    - TXT record metadata support
    - DNS caching and optimization
    """
    
    def __init__(self):
        self.service_name = "dns-discovery"
        self.service_version = "1.0.0"
        self.description = "Production-ready DNS-based service discovery"
    
    def create_client(self, config: Dict[str, Any]) -> DNSDiscoveryClient:
        """Create a DNS discovery client"""
        return DNSDiscoveryClient(
            nameservers=config.get("nameservers"),
            search_domains=config.get("search_domains")
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get DNS discovery template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "SRV record service discovery",
                "A/AAAA record endpoint resolution",
                "TXT record metadata parsing",
                "DNS caching with TTL support",
                "Health checking integration",
                "Service change monitoring",
                "Multiple nameserver support",
                "Search domain configuration"
            ],
            "dns_features": [
                "SRV record queries for service discovery",
                "A/AAAA record resolution for endpoints",
                "TXT record metadata extraction",
                "Recursive DNS resolution",
                "DNS cache with TTL respect",
                "Multiple resolver support",
                "IPv4 and IPv6 support",
                "Timeout and retry handling"
            ],
            "dependencies": ["dnspython", "prometheus"],
            "endpoints": [
                "/dns/discover/{service_name}",
                "/dns/resolve/{hostname}",
                "/dns/health/{service_name}",
                "/dns/services",
                "/dns/cache/clear"
            ]
        }