"""
Enterprise Proxy Pool Manager

Advanced proxy management and rotation system for distributed
crawling operations with health monitoring and failover.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import asyncio
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    ProxyPool,
    ProxyStatus,
    ProxyType,
    ProxyCountry
)
from ..core.exceptions import (
    ProxyPoolExhaustedError,
    DatabaseError,
    ValidationError
)


class ProxyHealthStatus(Enum):
    """Proxy health status levels."""
    EXCELLENT = 'excellent'     # < 1s response, 99%+ success
    GOOD = 'good'              # < 2s response, 95%+ success
    FAIR = 'fair'              # < 5s response, 85%+ success
    POOR = 'poor'              # < 10s response, 70%+ success
    CRITICAL = 'critical'      # > 10s response, < 70% success


class ProxyPoolManager(DatabaseManager):
    """
    Enterprise-grade proxy pool manager for distributed crawling.
    
    Handles:
    - Proxy pool health monitoring
    - Intelligent proxy rotation
    - Geographic distribution
    - Performance optimization
    - Automatic failover and recovery
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize proxy pool manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        self.table = ProxyPool
    
    async def assign_proxy(
        self,
        platform: str,
        user_id: str,
        preferred_country: Optional[str] = None,
        proxy_type: str = ProxyType.HTTP.value
    ) -> Dict[str, Any]:
        """
        Assign optimal proxy for crawling session.
        
        Args:
            platform: Target platform for crawling
            user_id: User identifier
            preferred_country: Optional preferred proxy country
            proxy_type: Type of proxy required
            
        Returns:
            Dict containing proxy information
            
        Raises:
            ProxyPoolExhaustedError: If no suitable proxies available
        """



        try:
            # Find best available proxy
            proxy = await self._find_optimal_proxy(
                platform, preferred_country, proxy_type
            )
            
            if not proxy:
                raise ProxyPoolExhaustedError(
                    f"No available proxies for platform {platform}"
                )
            
            # Assign proxy to user session
            assignment_id = await self._create_proxy_assignment(
                proxy['proxy_id'], user_id, platform
            )
            
            # Update proxy usage statistics
            await self._update_proxy_usage(proxy['proxy_id'])
            
            return {
                'proxy_id': proxy['proxy_id'],
                'assignment_id': assignment_id,
                'host': proxy['host'],
                'port': proxy['port'],
                'proxy_type': proxy['proxy_type'],
                'country': proxy['country'],
                'performance_score': proxy['performance_score'],
                'assigned_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if isinstance(e, ProxyPoolExhaustedError):
                raise
            raise DatabaseError(f"Failed to assign proxy: {str(e)}")
    
    async def _find_optimal_proxy(
        self,
        platform: str,
        preferred_country: Optional[str],
        proxy_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find the optimal proxy based on performance and availability.
        
        Args:
            platform: Target platform
            preferred_country: Preferred proxy country
            proxy_type: Required proxy type
            
        Returns:
            Dict containing proxy details or None if not found
        """



        try:
            # Build query for available proxies
            query_conditions = [
                "status = :active_status",
                "proxy_type = :proxy_type",
                "current_connections < max_connections",
                "last_health_check > :health_cutoff"
            ]
            
            query_params = {
                'active_status': ProxyStatus.ACTIVE.value,
                'proxy_type': proxy_type,
                'health_cutoff': datetime.utcnow() - timedelta(minutes=30)
            }
            
            # Add country preference if specified
            if preferred_country:
                query_conditions.append("country = :preferred_country")
                query_params['preferred_country'] = preferred_country
            
            # Add platform-specific filters
            if platform in ['youtube', 'google']:
                # Prefer residential proxies for Google services
                query_conditions.append("(proxy_type = 'residential' OR performance_score > 80)")
            elif platform == 'tiktok':
                # Prefer mobile proxies for TikTok
                query_conditions.append("(proxy_type = 'mobile' OR country IN ('US', 'UK', 'CA'))")
            
            query = f"""
            SELECT 
                proxy_id, host, port, proxy_type, country,
                performance_score, current_connections, max_connections,
                success_rate, avg_response_time
            FROM proxy_pools
            WHERE {' AND '.join(query_conditions)}
            ORDER BY 
                performance_score DESC,
                current_connections ASC,
                avg_response_time ASC
            LIMIT 1
            """
            
            result = await self.db.execute(text(query), query_params)
            proxy_data = result.first()
            
            if proxy_data:
                return {
                    'proxy_id': proxy_data.proxy_id,
                    'host': proxy_data.host,
                    'port': proxy_data.port,
                    'proxy_type': proxy_data.proxy_type,
                    'country': proxy_data.country,
                    'performance_score': proxy_data.performance_score,
                    'current_connections': proxy_data.current_connections,
                    'max_connections': proxy_data.max_connections,
                    'success_rate': proxy_data.success_rate,
                    'avg_response_time': proxy_data.avg_response_time
                }
            
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to find optimal proxy: {str(e)}")
    
    async def _create_proxy_assignment(
        self,
        proxy_id: str,
        user_id: str,
        platform: str
    ) -> str:
        """
        Create proxy assignment record.
        
        Args:
            proxy_id: Proxy identifier
            user_id: User identifier
            platform: Target platform
            
        Returns:
            Assignment identifier
        """



        try:
            assignment_id = str(uuid4())
            
            assignment_data = {
                'assignment_id': assignment_id,
                'proxy_id': proxy_id,
                'user_id': user_id,
                'platform': platform,
                'assigned_at': datetime.utcnow(),
                'status': 'active'
            }
            
            # Insert assignment record (assuming we have a proxy_assignments table)
            await self.db.execute(
                text("""
                INSERT INTO proxy_assignments 
                (assignment_id, proxy_id, user_id, platform, assigned_at, status)
                VALUES (:assignment_id, :proxy_id, :user_id, :platform, :assigned_at, :status)
                """),
                assignment_data
            )
            
            await self.db.commit()
            return assignment_id
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create proxy assignment: {str(e)}")
    
    async def _update_proxy_usage(self, proxy_id: str) -> None:
        """
        Update proxy usage statistics.
        
        Args:
            proxy_id: Proxy identifier
        """



        try:
            await self.db.execute(
                text("""
                UPDATE proxy_pools 
                SET current_connections = current_connections + 1,
                    total_requests = total_requests + 1,
                    last_used_at = :now,
                    updated_at = :now
                WHERE proxy_id = :proxy_id
                """),
                {
                    'proxy_id': proxy_id,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update proxy usage: {str(e)}")
    
    async def release_proxy(self, proxy_id: str) -> bool:
        """
        Release proxy from current assignment.
        
        Args:
            proxy_id: Proxy identifier
            
        Returns:
            bool indicating success
        """



        try:
            # Decrement current connections
            result = await self.db.execute(
                text("""
                UPDATE proxy_pools 
                SET current_connections = GREATEST(0, current_connections - 1),
                    updated_at = :now
                WHERE proxy_id = :proxy_id
                """),
                {
                    'proxy_id': proxy_id,
                    'now': datetime.utcnow()
                }
            )
            
            # Update assignment status
            await self.db.execute(
                text("""
                UPDATE proxy_assignments 
                SET status = 'released',
                    released_at = :now
                WHERE proxy_id = :proxy_id 
                  AND status = 'active'
                """),
                {
                    'proxy_id': proxy_id,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to release proxy: {str(e)}")
    
    async def add_proxy_to_pool(
        self,
        host: str,
        port: int,
        proxy_type: str,
        country: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        max_connections: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add new proxy to the pool.
        
        Args:
            host: Proxy host address
            port: Proxy port
            proxy_type: Type of proxy
            country: Proxy country code
            username: Optional authentication username
            password: Optional authentication password
            max_connections: Maximum concurrent connections
            metadata: Optional proxy metadata
            
        Returns:
            Proxy identifier
        """



        try:
            proxy_id = str(uuid4())
            
            proxy_data = {
                'proxy_id': proxy_id,
                'host': host,
                'port': port,
                'proxy_type': proxy_type,
                'country': country,
                'username': username,
                'password': password,  # Should be encrypted in production
                'max_connections': max_connections,
                'current_connections': 0,
                'status': ProxyStatus.PENDING.value,
                'performance_score': 0.0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'metadata': json.dumps(metadata) if metadata else None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_health_check': None,
                'last_used_at': None
            }
            
            proxy = ProxyPool(**proxy_data)
            self.db.add(proxy)
            await self.db.commit()
            
            # Schedule initial health check
            await self.perform_proxy_health_check(proxy_id)
            
            return proxy_id
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to add proxy to pool: {str(e)}")
    
    async def perform_proxy_health_check(self, proxy_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive health check on proxy.
        
        Args:
            proxy_id: Proxy identifier
            
        Returns:
            Dict containing health check results
        """



        try:
            # Get proxy details
            proxy_data = await self.get_proxy_details(proxy_id)
            if not proxy_data:
                raise ValidationError(f"Proxy not found: {proxy_id}")
            
            # Perform actual health check (simplified for demo)
            health_result = await self._execute_proxy_health_check(proxy_data)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(health_result)
            
            # Update proxy with health check results
            await self._update_proxy_health(proxy_id, health_result, performance_score)
            
            return {
                'proxy_id': proxy_id,
                'health_status': health_result['status'],
                'response_time': health_result['response_time'],
                'success_rate': health_result['success_rate'],
                'performance_score': performance_score,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Mark proxy as failed if health check fails
            await self._mark_proxy_failed(proxy_id, str(e))
            raise DatabaseError(f"Health check failed for proxy {proxy_id}: {str(e)}")
    
    async def _execute_proxy_health_check(
        self,
        proxy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute actual proxy health check tests.
        
        Args:
            proxy_data: Proxy configuration data
            
        Returns:
            Dict containing health check results
        """
        # This is a simplified implementation
        # In production, you would actually test the proxy
        import random
        
        # Simulate health check with random results for demo
        response_time = random.uniform(0.5, 10.0)
        success_rate = random.uniform(70.0, 99.5)
        
        if response_time < 1.0 and success_rate > 95:
            status = ProxyHealthStatus.EXCELLENT.value
        elif response_time < 2.0 and success_rate > 90:
            status = ProxyHealthStatus.GOOD.value
        elif response_time < 5.0 and success_rate > 80:
            status = ProxyHealthStatus.FAIR.value
        elif response_time < 10.0 and success_rate > 70:
            status = ProxyHealthStatus.POOR.value
        else:
            status = ProxyHealthStatus.CRITICAL.value
        
        return {
            'status': status,
            'response_time': response_time,
            'success_rate': success_rate,
            'tests_passed': random.randint(8, 10),
            'total_tests': 10
        }
    
    async def _calculate_performance_score(
        self,
        health_result: Dict[str, Any]
    ) -> float:
        """
        Calculate overall performance score for proxy.
        
        Args:
            health_result: Health check results
            
        Returns:
            Performance score (0-100)
        """
        response_time = health_result['response_time']
        success_rate = health_result['success_rate']
        
        # Weight factors
        speed_score = max(0, 100 - (response_time * 10))  # Penalty for slow response
        reliability_score = success_rate  # Direct success rate
        
        # Combined score with weights
        performance_score = (speed_score * 0.4) + (reliability_score * 0.6)
        
        return round(min(100, max(0, performance_score)), 2)
    
    async def _update_proxy_health(
        self,
        proxy_id: str,
        health_result: Dict[str, Any],
        performance_score: float
    ) -> None:
        """
        Update proxy with health check results.
        
        Args:
            proxy_id: Proxy identifier
            health_result: Health check results
            performance_score: Calculated performance score
        """



        try:
            # Determine new status based on health
            if health_result['status'] in [ProxyHealthStatus.EXCELLENT.value, ProxyHealthStatus.GOOD.value]:
                new_status = ProxyStatus.ACTIVE.value
            elif health_result['status'] == ProxyHealthStatus.FAIR.value:
                new_status = ProxyStatus.ACTIVE.value  # Still usable
            else:
                new_status = ProxyStatus.DEGRADED.value
            
            await self.db.execute(
                text("""
                UPDATE proxy_pools 
                SET status = :status,
                    performance_score = :performance_score,
                    success_rate = :success_rate,
                    avg_response_time = :avg_response_time,
                    last_health_check = :now,
                    updated_at = :now
                WHERE proxy_id = :proxy_id
                """),
                {
                    'proxy_id': proxy_id,
                    'status': new_status,
                    'performance_score': performance_score,
                    'success_rate': health_result['success_rate'],
                    'avg_response_time': health_result['response_time'],
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update proxy health: {str(e)}")
    
    async def _mark_proxy_failed(self, proxy_id: str, error_message: str) -> None:
        """
        Mark proxy as failed with error message.
        
        Args:
            proxy_id: Proxy identifier
            error_message: Error description
        """



        try:
            await self.db.execute(
                text("""
                UPDATE proxy_pools 
                SET status = :failed_status,
                    failed_requests = failed_requests + 1,
                    last_error = :error_message,
                    last_health_check = :now,
                    updated_at = :now
                WHERE proxy_id = :proxy_id
                """),
                {
                    'proxy_id': proxy_id,
                    'failed_status': ProxyStatus.FAILED.value,
                    'error_message': error_message,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            # Don't raise exception here to prevent error loops
            print(f"Failed to mark proxy as failed: {str(e)}")
    
    async def get_proxy_details(self, proxy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed proxy information.
        
        Args:
            proxy_id: Proxy identifier
            
        Returns:
            Dict containing proxy details or None if not found
        """



        try:
            result = await self.db.execute(
                text("""
                SELECT * FROM proxy_pools WHERE proxy_id = :proxy_id
                """),
                {'proxy_id': proxy_id}
            )
            
            proxy_data = result.first()
            if not proxy_data:
                return None
            
            return {
                'proxy_id': proxy_data.proxy_id,
                'host': proxy_data.host,
                'port': proxy_data.port,
                'proxy_type': proxy_data.proxy_type,
                'country': proxy_data.country,
                'username': proxy_data.username,
                'status': proxy_data.status,
                'performance_score': proxy_data.performance_score,
                'success_rate': proxy_data.success_rate,
                'avg_response_time': proxy_data.avg_response_time,
                'current_connections': proxy_data.current_connections,
                'max_connections': proxy_data.max_connections,
                'total_requests': proxy_data.total_requests,
                'successful_requests': proxy_data.successful_requests,
                'failed_requests': proxy_data.failed_requests,
                'created_at': proxy_data.created_at,
                'last_health_check': proxy_data.last_health_check,
                'last_used_at': proxy_data.last_used_at
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get proxy details: {str(e)}")
    
    async def get_pool_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive proxy pool statistics.
        
        Returns:
            Dict containing pool statistics
        """



        try:
            # Get status breakdown
            status_stats = await self.db.execute(
                text("""
                SELECT status, COUNT(*) as count
                FROM proxy_pools
                GROUP BY status
                """)
            )
            
            # Get country breakdown
            country_stats = await self.db.execute(
                text("""
                SELECT country, COUNT(*) as count,
                       AVG(performance_score) as avg_performance
                FROM proxy_pools
                WHERE status = :active_status
                GROUP BY country
                ORDER BY count DESC
                """),
                {'active_status': ProxyStatus.ACTIVE.value}
            )
            
            # Get performance metrics
            performance_stats = await self.db.execute(
                text("""
                SELECT 
                    COUNT(*) as total_proxies,
                    COUNT(CASE WHEN status = :active_status THEN 1 END) as active_proxies,
                    AVG(performance_score) as avg_performance_score,
                    AVG(success_rate) as avg_success_rate,
                    AVG(avg_response_time) as avg_response_time,
                    SUM(current_connections) as total_active_connections,
                    SUM(total_requests) as total_requests_all_time
                FROM proxy_pools
                """),
                {'active_status': ProxyStatus.ACTIVE.value}
            )
            
            status_data = {row.status: row.count for row in status_stats}
            country_data = {
                row.country: {
                    'count': row.count,
                    'avg_performance': float(row.avg_performance or 0)
                }
                for row in country_stats
            }
            perf_data = performance_stats.first()
            
            return {
                'status_breakdown': status_data,
                'country_breakdown': country_data,
                'performance_metrics': {
                    'total_proxies': perf_data.total_proxies or 0,
                    'active_proxies': perf_data.active_proxies or 0,
                    'avg_performance_score': float(perf_data.avg_performance_score or 0),
                    'avg_success_rate': float(perf_data.avg_success_rate or 0),
                    'avg_response_time': float(perf_data.avg_response_time or 0),
                    'total_active_connections': perf_data.total_active_connections or 0,
                    'total_requests_all_time': perf_data.total_requests_all_time or 0
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pool statistics: {str(e)}")
    
    async def run_maintenance_cycle(self) -> Dict[str, Any]:
        """
        Run comprehensive maintenance cycle for proxy pool.
        
        Returns:
            Dict containing maintenance results
        """



        try:
            maintenance_results = {
                'health_checks_performed': 0,
                'proxies_activated': 0,
                'proxies_deactivated': 0,
                'failed_proxies_removed': 0,
                'performance_updates': 0
            }
            
            # Get all proxies for health checking
            all_proxies = await self.db.execute(
                text("""
                SELECT proxy_id FROM proxy_pools
                WHERE status != :removed_status
                ORDER BY last_health_check ASC NULLS FIRST
                """),
                {'removed_status': ProxyStatus.REMOVED.value}
            )
            
            for proxy_row in all_proxies:
                try:
                    health_result = await self.perform_proxy_health_check(proxy_row.proxy_id)
                    maintenance_results['health_checks_performed'] += 1
                    
                    if health_result['health_status'] in [ProxyHealthStatus.EXCELLENT.value, ProxyHealthStatus.GOOD.value]:
                        maintenance_results['proxies_activated'] += 1
                    elif health_result['health_status'] == ProxyHealthStatus.CRITICAL.value:
                        maintenance_results['proxies_deactivated'] += 1
                        
                    maintenance_results['performance_updates'] += 1
                    
                except Exception as e:
                    # Count failed health checks but continue
                    maintenance_results['failed_proxies_removed'] += 1
                    continue
            
            # Clean up old assignments
            await self._cleanup_old_assignments()
            
            return maintenance_results
            
        except Exception as e:
            raise DatabaseError(f"Maintenance cycle failed: {str(e)}")
    
    async def _cleanup_old_assignments(self) -> None:
        """Clean up old proxy assignments."""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            await self.db.execute(
                text("""
                DELETE FROM proxy_assignments 
                WHERE status = 'released' 
                  AND released_at < :cutoff_time
                """),
                {'cutoff_time': cutoff_time}
            )
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to cleanup old assignments: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of proxy pool system.
        
        Returns:
            Dict containing health status
        """



        try:
            # Get active proxy count
            active_proxies = await self.db.query(func.count(ProxyPool.proxy_id)).filter(
                ProxyPool.status == ProxyStatus.ACTIVE.value
            ).scalar()
            
            # Get failed proxy count
            failed_proxies = await self.db.query(func.count(ProxyPool.proxy_id)).filter(
                ProxyPool.status == ProxyStatus.FAILED.value
            ).scalar()
            
            # Get proxies needing health check
            stale_proxies = await self.db.query(func.count(ProxyPool.proxy_id)).filter(
                or_(
                    ProxyPool.last_health_check.is_(None),
                    ProxyPool.last_health_check < datetime.utcnow() - timedelta(hours=6)
                )
            ).scalar()
            
            # Determine health status
            total_proxies = active_proxies + failed_proxies
            if total_proxies == 0:
                status = 'unhealthy'  # No proxies available
            elif active_proxies < 5:
                status = 'degraded'   # Too few active proxies
            elif failed_proxies > active_proxies * 0.3:
                status = 'degraded'   # Too many failed proxies
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'active_proxies': active_proxies,
                'failed_proxies': failed_proxies,
                'stale_proxies': stale_proxies,
                'total_proxies': total_proxies,
                'failure_rate_percentage': (failed_proxies / max(total_proxies, 1)) * 100,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['ProxyPoolManager', 'ProxyHealthStatus']
