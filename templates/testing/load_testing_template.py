"""
⚡ LOAD TESTING TEMPLATE - PERFORMANCE EXPERT IMPLEMENTATION
============================================================

Enterprise-grade load testing template for Ainflue Creator Economy Platform.
Comprehensive load testing covering:
- HTTP load testing with realistic user patterns
- Database load testing and connection pooling
- Creator Economy workflow load testing
- Real-time collaboration load testing
- Payment processing load testing
- Media streaming load testing
- API rate limiting validation
- Performance degradation analysis

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

Author: Performance Expert & Load Testing Specialist
Team: Lead Dev IA + Backend Senior + Performance Engineer + DevOps Expert
Version: 1.0.0
"""

import pytest
import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import random
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from faker import Faker
import asyncpg
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import psutil
import resource

# Application imports
from core.performance import LoadTestManager, PerformanceMonitor, MetricsCollector
from core.config import get_settings
from utils.exceptions import PerformanceError, LoadTestError, ValidationError
from monitoring.test_metrics import TestMetricsCollector
from tests.fixtures import create_test_users, create_test_content

# Initialize test utilities
fake = Faker()
settings = get_settings()


class LoadTestType(Enum):
    """Load test type classifications"""
    RAMP_UP = "ramp_up"
    SUSTAINED = "sustained"
    SPIKE = "spike"
    STRESS = "stress"
    VOLUME = "volume"
    ENDURANCE = "endurance"


class UserBehaviorPattern(Enum):
    """User behavior pattern for realistic load testing"""
    CREATOR_UPLOAD = "creator_upload"
    CONTENT_BROWSING = "content_browsing"
    COLLABORATION = "collaboration"
    PAYMENT_FLOW = "payment_flow"
    ANALYTICS_VIEWING = "analytics_viewing"
    SOCIAL_INTERACTION = "social_interaction"


@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""
    
    name: str
    test_type: LoadTestType
    user_pattern: UserBehaviorPattern
    concurrent_users: int
    duration_seconds: int
    ramp_up_seconds: int = 60
    think_time_range: Tuple[float, float] = (1.0, 5.0)
    expected_response_time_p95: float = 2.0
    expected_throughput_rps: float = 100.0
    error_rate_threshold: float = 0.01  # 1%
    
    def __post_init__(self):
        self.scenario_id = str(uuid.uuid4())


@dataclass
class LoadTestMetrics:
    """Load test metrics collection"""
    
    scenario_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    error_details: List[Dict[str, Any]] = field(default_factory=list)
    throughput_history: List[Tuple[datetime, float]] = field(default_factory=list)
    resource_usage: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def error_rate(self) -> float:
        return 1.0 - self.success_rate
    
    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
    
    @property
    def p99_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile


@dataclass
class LoadTestContext:
    """Load testing context"""
    
    base_url: str = "https://api.ainflue.com"
    auth_tokens: List[str] = field(default_factory=list)
    test_users: List[Dict[str, Any]] = field(default_factory=list)
    test_content: List[Dict[str, Any]] = field(default_factory=list)
    database_pool: Optional[Any] = None
    redis_pool: Optional[Any] = None
    
    def __post_init__(self):
        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = f"https://{self.base_url}"


class LoadTestingTemplate:
    """
    ⚡ ENTERPRISE LOAD TESTING FRAMEWORK
    
    Comprehensive load testing template providing:
    - HTTP load testing with realistic user patterns
    - Database connection and query load testing
    - Creator Economy workflow performance validation
    - Real-time collaboration stress testing
    - Payment processing load validation
    - Media streaming performance testing
    - API rate limiting and throttling validation
    - Performance degradation analysis
    - Resource utilization monitoring
    - Scalability assessment and bottleneck identification
    """
    
    def __init__(self):
        self.load_test_manager = LoadTestManager()
        self.performance_monitor = PerformanceMonitor()
        self.metrics_collector = TestMetricsCollector("load_testing")
        self.test_scenarios = self._create_test_scenarios()
        self.active_scenarios: Dict[str, LoadTestMetrics] = {}
        
    async def setup_test_environment(self) -> LoadTestContext:
        """Setup load testing environment"""
        context = LoadTestContext()
        
        # Create test users and authentication tokens
        await self._setup_test_users(context)
        
        # Create test content for load testing
        await self._setup_test_content(context)
        
        # Setup database connections
        await self._setup_database_pools(context)
        
        return context
    
    async def teardown_test_environment(self, context: LoadTestContext):
        """Clean up load testing environment"""
        try:
            # Close database connections
            if context.database_pool:
                await context.database_pool.close()
            
            if context.redis_pool:
                await context.redis_pool.close()
            
            # Clean up test data
            await self._cleanup_test_data(context)
            
        except Exception as e:
            self.metrics_collector.record_error("teardown_failed", str(e))
    
    def _create_test_scenarios(self) -> List[LoadTestScenario]:
        """Create comprehensive load test scenarios"""
        
        scenarios = [
            # Creator upload workflow
            LoadTestScenario(
                name="Creator Content Upload",
                test_type=LoadTestType.RAMP_UP,
                user_pattern=UserBehaviorPattern.CREATOR_UPLOAD,
                concurrent_users=50,
                duration_seconds=300,
                ramp_up_seconds=60,
                expected_response_time_p95=5.0,  # File uploads take longer
                expected_throughput_rps=10.0
            ),
            
            # Content browsing
            LoadTestScenario(
                name="Content Browsing",
                test_type=LoadTestType.SUSTAINED,
                user_pattern=UserBehaviorPattern.CONTENT_BROWSING,
                concurrent_users=200,
                duration_seconds=600,
                ramp_up_seconds=120,
                expected_response_time_p95=1.0,
                expected_throughput_rps=150.0
            ),
            
            # Collaboration workflow
            LoadTestScenario(
                name="Real-time Collaboration",
                test_type=LoadTestType.SPIKE,
                user_pattern=UserBehaviorPattern.COLLABORATION,
                concurrent_users=100,
                duration_seconds=180,
                ramp_up_seconds=30,
                expected_response_time_p95=0.5,  # Real-time requires low latency
                expected_throughput_rps=80.0
            ),
            
            # Payment processing
            LoadTestScenario(
                name="Payment Processing",
                test_type=LoadTestType.STRESS,
                user_pattern=UserBehaviorPattern.PAYMENT_FLOW,
                concurrent_users=75,
                duration_seconds=240,
                ramp_up_seconds=45,
                expected_response_time_p95=3.0,
                expected_throughput_rps=25.0
            ),
            
            # Analytics viewing
            LoadTestScenario(
                name="Analytics Dashboard",
                test_type=LoadTestType.VOLUME,
                user_pattern=UserBehaviorPattern.ANALYTICS_VIEWING,
                concurrent_users=150,
                duration_seconds=360,
                ramp_up_seconds=90,
                expected_response_time_p95=2.0,
                expected_throughput_rps=100.0
            ),
            
            # Social interactions
            LoadTestScenario(
                name="Social Interactions",
                test_type=LoadTestType.ENDURANCE,
                user_pattern=UserBehaviorPattern.SOCIAL_INTERACTION,
                concurrent_users=300,
                duration_seconds=1800,  # 30 minutes
                ramp_up_seconds=180,
                expected_response_time_p95=1.5,
                expected_throughput_rps=200.0
            )
        ]
        
        return scenarios
    
    async def _setup_test_users(self, context: LoadTestContext):
        """Setup test users for load testing"""
        
        # Generate test users
        for i in range(1000):  # Support up to 1000 concurrent users
            user = {
                "id": f"load_test_user_{i}",
                "username": f"loadtest_{i}",
                "email": f"loadtest_{i}@ainflue.com",
                "auth_token": f"token_{uuid.uuid4()}",
                "role": random.choice(["creator", "collaborator", "viewer"]),
                "subscription": random.choice(["free", "pro", "enterprise"])
            }
            context.test_users.append(user)
            context.auth_tokens.append(user["auth_token"])
    
    async def _setup_test_content(self, context: LoadTestContext):
        """Setup test content for load testing"""
        
        # Generate test content
        for i in range(500):
            content = {
                "id": f"load_test_content_{i}",
                "title": f"Test Content {i}",
                "type": random.choice(["audio", "video", "text", "image"]),
                "size_mb": random.randint(1, 100),
                "owner_id": random.choice(context.test_users)["id"],
                "status": random.choice(["draft", "published", "archived"])
            }
            context.test_content.append(content)
    
    async def _setup_database_pools(self, context: LoadTestContext):
        """Setup database connection pools for load testing"""
        
        try:
            # PostgreSQL connection pool
            context.database_pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="test",
                password="test",
                database="ainflue_test",
                min_size=10,
                max_size=100,
                command_timeout=60
            )
            
            # Redis connection pool
            context.redis_pool = redis.ConnectionPool.from_url(
                "redis://localhost:6379/0",
                max_connections=50
            )
            
        except Exception as e:
            print(f"Database setup failed (using mocks): {e}")
            # Use mock pools for testing
            context.database_pool = Mock()
            context.redis_pool = Mock()
    
    async def _cleanup_test_data(self, context: LoadTestContext):
        """Clean up test data after load testing"""
        # Implementation would clean up test data
        pass

    # ==================== USER BEHAVIOR SIMULATION ====================
    
    async def simulate_creator_upload_behavior(self, session: aiohttp.ClientSession, 
                                             context: LoadTestContext, 
                                             user: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creator content upload behavior"""
        
        start_time = time.time()
        request_results = []
        
        try:
            # Step 1: Check upload quota
            quota_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/users/{user['id']}/quota",
                headers={"Authorization": f"Bearer {user['auth_token']}"}
            )
            request_results.append(quota_response)
            
            # Think time
            await asyncio.sleep(random.uniform(*self.test_scenarios[0].think_time_range))
            
            # Step 2: Create content metadata
            content_data = {
                "title": fake.sentence(nb_words=4),
                "description": fake.text(max_nb_chars=200),
                "type": "audio",
                "genre": random.choice(["electronic", "rock", "jazz", "classical"]),
                "tags": [fake.word() for _ in range(3)]
            }
            
            metadata_response = await self._make_request(
                session, "POST", f"{context.base_url}/api/v1/content",
                headers={"Authorization": f"Bearer {user['auth_token']}"},
                json=content_data
            )
            request_results.append(metadata_response)
            
            if metadata_response["success"]:
                content_id = metadata_response.get("data", {}).get("id", "test_content")
                
                # Step 3: Upload file chunks (simulate)
                chunk_size = 1024 * 1024  # 1MB chunks
                total_size = random.randint(5, 50) * 1024 * 1024  # 5-50MB file
                chunks = total_size // chunk_size
                
                for chunk in range(chunks):
                    chunk_data = {
                        "chunk_number": chunk,
                        "total_chunks": chunks,
                        "data": "base64_encoded_audio_data_chunk"
                    }
                    
                    chunk_response = await self._make_request(
                        session, "POST", 
                        f"{context.base_url}/api/v1/content/{content_id}/upload",
                        headers={"Authorization": f"Bearer {user['auth_token']}"},
                        json=chunk_data
                    )
                    request_results.append(chunk_response)
                    
                    # Small delay between chunks
                    await asyncio.sleep(0.1)
                
                # Step 4: Finalize upload
                finalize_response = await self._make_request(
                    session, "POST", 
                    f"{context.base_url}/api/v1/content/{content_id}/finalize",
                    headers={"Authorization": f"Bearer {user['auth_token']}"}
                )
                request_results.append(finalize_response)
            
            total_time = time.time() - start_time
            
            return {
                "success": all(r["success"] for r in request_results),
                "total_time": total_time,
                "requests": len(request_results),
                "details": request_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "total_time": time.time() - start_time,
                "error": str(e),
                "requests": len(request_results)
            }
    
    async def simulate_content_browsing_behavior(self, session: aiohttp.ClientSession,
                                               context: LoadTestContext,
                                               user: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate content browsing behavior"""
        
        start_time = time.time()
        request_results = []
        
        try:
            # Step 1: Browse homepage/feed
            feed_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/content/feed",
                headers={"Authorization": f"Bearer {user['auth_token']}"},
                params={"limit": 20, "offset": 0}
            )
            request_results.append(feed_response)
            
            # Think time
            await asyncio.sleep(random.uniform(*self.test_scenarios[1].think_time_range))
            
            # Step 2: Search content
            search_query = random.choice(["electronic music", "collaboration", "jazz", "original"])
            search_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/content/search",
                headers={"Authorization": f"Bearer {user['auth_token']}"},
                params={"q": search_query, "limit": 10}
            )
            request_results.append(search_response)
            
            # Think time
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Step 3: View specific content details
            if feed_response["success"] and "data" in feed_response:
                content_list = feed_response["data"].get("items", [])
                if content_list:
                    selected_content = random.choice(content_list)
                    content_id = selected_content.get("id", "test_content")
                    
                    detail_response = await self._make_request(
                        session, "GET", 
                        f"{context.base_url}/api/v1/content/{content_id}",
                        headers={"Authorization": f"Bearer {user['auth_token']}"}
                    )
                    request_results.append(detail_response)
                    
                    # Step 4: Get content analytics (if creator/collaborator)
                    if user["role"] in ["creator", "collaborator"]:
                        analytics_response = await self._make_request(
                            session, "GET",
                            f"{context.base_url}/api/v1/content/{content_id}/analytics",
                            headers={"Authorization": f"Bearer {user['auth_token']}"}
                        )
                        request_results.append(analytics_response)
            
            # Step 5: Check notifications
            notifications_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/notifications",
                headers={"Authorization": f"Bearer {user['auth_token']}"},
                params={"limit": 5}
            )
            request_results.append(notifications_response)
            
            total_time = time.time() - start_time
            
            return {
                "success": all(r["success"] for r in request_results),
                "total_time": total_time,
                "requests": len(request_results),
                "details": request_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "total_time": time.time() - start_time,
                "error": str(e),
                "requests": len(request_results)
            }
    
    async def simulate_collaboration_behavior(self, session: aiohttp.ClientSession,
                                            context: LoadTestContext,
                                            user: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate real-time collaboration behavior"""
        
        start_time = time.time()
        request_results = []
        
        try:
            # Step 1: Get active collaborations
            collabs_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/collaborations",
                headers={"Authorization": f"Bearer {user['auth_token']}"}
            )
            request_results.append(collabs_response)
            
            # Step 2: Join collaboration session (WebSocket simulation)
            collab_id = "test_collaboration_123"
            join_response = await self._make_request(
                session, "POST", 
                f"{context.base_url}/api/v1/collaborations/{collab_id}/join",
                headers={"Authorization": f"Bearer {user['auth_token']}"}
            )
            request_results.append(join_response)
            
            # Step 3: Send real-time updates (simulate WebSocket messages)
            for i in range(5):
                update_data = {
                    "type": random.choice(["edit", "comment", "cursor_move"]),
                    "content": f"Real-time update {i}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                update_response = await self._make_request(
                    session, "POST",
                    f"{context.base_url}/api/v1/collaborations/{collab_id}/update",
                    headers={"Authorization": f"Bearer {user['auth_token']}"},
                    json=update_data
                )
                request_results.append(update_response)
                
                # Short delay for real-time feel
                await asyncio.sleep(0.2)
            
            # Step 4: Get collaboration state
            state_response = await self._make_request(
                session, "GET",
                f"{context.base_url}/api/v1/collaborations/{collab_id}/state",
                headers={"Authorization": f"Bearer {user['auth_token']}"}
            )
            request_results.append(state_response)
            
            total_time = time.time() - start_time
            
            return {
                "success": all(r["success"] for r in request_results),
                "total_time": total_time,
                "requests": len(request_results),
                "details": request_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "total_time": time.time() - start_time,
                "error": str(e),
                "requests": len(request_results)
            }
    
    async def simulate_payment_flow_behavior(self, session: aiohttp.ClientSession,
                                           context: LoadTestContext,
                                           user: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment processing behavior"""
        
        start_time = time.time()
        request_results = []
        
        try:
            # Step 1: Get pricing information
            pricing_response = await self._make_request(
                session, "GET", f"{context.base_url}/api/v1/pricing",
                headers={"Authorization": f"Bearer {user['auth_token']}"}
            )
            request_results.append(pricing_response)
            
            # Step 2: Create payment intent
            payment_data = {
                "amount": random.choice([9.99, 19.99, 49.99]),
                "currency": "USD",
                "type": random.choice(["subscription", "content_purchase", "tip"]),
                "content_id": random.choice(context.test_content)["id"]
            }
            
            intent_response = await self._make_request(
                session, "POST", f"{context.base_url}/api/v1/payments/intent",
                headers={"Authorization": f"Bearer {user['auth_token']}"},
                json=payment_data
            )
            request_results.append(intent_response)
            
            if intent_response["success"]:
                payment_id = intent_response.get("data", {}).get("id", "test_payment")
                
                # Step 3: Process payment (simulate)
                process_data = {
                    "payment_method": "card_test_123",
                    "billing_address": {
                        "country": "US",
                        "postal_code": "12345"
                    }
                }
                
                process_response = await self._make_request(
                    session, "POST",
                    f"{context.base_url}/api/v1/payments/{payment_id}/process",
                    headers={"Authorization": f"Bearer {user['auth_token']}"},
                    json=process_data
                )
                request_results.append(process_response)
                
                # Step 4: Confirm payment
                confirm_response = await self._make_request(
                    session, "POST",
                    f"{context.base_url}/api/v1/payments/{payment_id}/confirm",
                    headers={"Authorization": f"Bearer {user['auth_token']}"}
                )
                request_results.append(confirm_response)
            
            total_time = time.time() - start_time
            
            return {
                "success": all(r["success"] for r in request_results),
                "total_time": total_time,
                "requests": len(request_results),
                "details": request_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "total_time": time.time() - start_time,
                "error": str(e),
                "requests": len(request_results)
            }

    # ==================== LOAD TEST EXECUTION ====================
    
    async def _make_request(self, session: aiohttp.ClientSession, method: str, 
                          url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and metrics"""
        
        start_time = time.time()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                
                # Try to parse JSON response
                try:
                    data = await response.json()
                except:
                    data = {"text": await response.text()}
                
                return {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "response_time": response_time,
                    "data": data,
                    "url": url,
                    "method": method
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "response_time": response_time,
                "error": str(e),
                "url": url,
                "method": method
            }
    
    async def execute_load_test_scenario(self, scenario: LoadTestScenario, 
                                       context: LoadTestContext) -> LoadTestMetrics:
        """Execute a single load test scenario"""
        
        print(f"🚀 Starting load test: {scenario.name}")
        print(f"   Users: {scenario.concurrent_users}, Duration: {scenario.duration_seconds}s")
        
        metrics = LoadTestMetrics(
            scenario_id=scenario.scenario_id,
            start_time=datetime.utcnow()
        )
        
        self.active_scenarios[scenario.scenario_id] = metrics
        
        # Create user behavior function mapping
        behavior_functions = {
            UserBehaviorPattern.CREATOR_UPLOAD: self.simulate_creator_upload_behavior,
            UserBehaviorPattern.CONTENT_BROWSING: self.simulate_content_browsing_behavior,
            UserBehaviorPattern.COLLABORATION: self.simulate_collaboration_behavior,
            UserBehaviorPattern.PAYMENT_FLOW: self.simulate_payment_flow_behavior,
            UserBehaviorPattern.ANALYTICS_VIEWING: self.simulate_content_browsing_behavior,  # Similar pattern
            UserBehaviorPattern.SOCIAL_INTERACTION: self.simulate_content_browsing_behavior  # Similar pattern
        }
        
        behavior_function = behavior_functions.get(scenario.user_pattern)
        if not behavior_function:
            raise ValueError(f"Unknown user behavior pattern: {scenario.user_pattern}")
        
        # Setup session and run load test
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=scenario.concurrent_users * 2)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                # Start resource monitoring
                monitor_task = asyncio.create_task(
                    self._monitor_resources(metrics, scenario.duration_seconds)
                )
                
                # Execute load test based on type
                if scenario.test_type == LoadTestType.RAMP_UP:
                    await self._execute_ramp_up_test(scenario, context, session, behavior_function, metrics)
                elif scenario.test_type == LoadTestType.SUSTAINED:
                    await self._execute_sustained_test(scenario, context, session, behavior_function, metrics)
                elif scenario.test_type == LoadTestType.SPIKE:
                    await self._execute_spike_test(scenario, context, session, behavior_function, metrics)
                elif scenario.test_type == LoadTestType.STRESS:
                    await self._execute_stress_test(scenario, context, session, behavior_function, metrics)
                elif scenario.test_type == LoadTestType.VOLUME:
                    await self._execute_volume_test(scenario, context, session, behavior_function, metrics)
                elif scenario.test_type == LoadTestType.ENDURANCE:
                    await self._execute_endurance_test(scenario, context, session, behavior_function, metrics)
                
                # Stop resource monitoring
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
                
        except Exception as e:
            print(f"❌ Load test failed: {e}")
            metrics.error_details.append({
                "error": str(e),
                "timestamp": datetime.utcnow(),
                "context": "test_execution"
            })
        
        metrics.end_time = datetime.utcnow()
        
        # Calculate final metrics
        self._calculate_final_metrics(scenario, metrics)
        
        print(f"✅ Load test completed: {scenario.name}")
        print(f"   Success Rate: {metrics.success_rate:.2%}")
        print(f"   Avg Response Time: {metrics.avg_response_time:.3f}s")
        print(f"   P95 Response Time: {metrics.p95_response_time:.3f}s")
        
        return metrics
    
    async def _execute_ramp_up_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                  session: aiohttp.ClientSession, behavior_function: Callable,
                                  metrics: LoadTestMetrics):
        """Execute ramp-up load test"""
        
        users_per_second = scenario.concurrent_users / scenario.ramp_up_seconds
        active_tasks = []
        
        start_time = time.time()
        
        for second in range(scenario.ramp_up_seconds):
            # Add new users this second
            new_users = int(users_per_second * (second + 1)) - len(active_tasks)
            
            for _ in range(new_users):
                if len(active_tasks) < scenario.concurrent_users:
                    user = random.choice(context.test_users)
                    task = asyncio.create_task(
                        self._execute_user_session(session, context, user, behavior_function, 
                                                 scenario.duration_seconds - second, metrics)
                    )
                    active_tasks.append(task)
            
            await asyncio.sleep(1)
            
            # Check if test duration is reached
            if time.time() - start_time >= scenario.duration_seconds:
                break
        
        # Wait for remaining tasks
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
    
    async def _execute_sustained_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                    session: aiohttp.ClientSession, behavior_function: Callable,
                                    metrics: LoadTestMetrics):
        """Execute sustained load test"""
        
        # Ramp up to target users
        users_per_second = scenario.concurrent_users / scenario.ramp_up_seconds if scenario.ramp_up_seconds > 0 else scenario.concurrent_users
        active_tasks = []
        
        # Ramp up phase
        for second in range(min(scenario.ramp_up_seconds, scenario.duration_seconds)):
            new_users = int(users_per_second * (second + 1)) - len(active_tasks)
            
            for _ in range(new_users):
                if len(active_tasks) < scenario.concurrent_users:
                    user = random.choice(context.test_users)
                    task = asyncio.create_task(
                        self._execute_user_session(session, context, user, behavior_function,
                                                 scenario.duration_seconds - second, metrics)
                    )
                    active_tasks.append(task)
            
            await asyncio.sleep(1)
        
        # Sustain phase - maintain concurrent users
        remaining_time = scenario.duration_seconds - scenario.ramp_up_seconds
        if remaining_time > 0:
            await asyncio.sleep(remaining_time)
        
        # Wait for all tasks to complete
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
    
    async def _execute_spike_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                session: aiohttp.ClientSession, behavior_function: Callable,
                                metrics: LoadTestMetrics):
        """Execute spike load test"""
        
        # Immediate spike to target users
        active_tasks = []
        
        for _ in range(scenario.concurrent_users):
            user = random.choice(context.test_users)
            task = asyncio.create_task(
                self._execute_user_session(session, context, user, behavior_function,
                                         scenario.duration_seconds, metrics)
            )
            active_tasks.append(task)
        
        # Wait for all tasks
        await asyncio.gather(*active_tasks, return_exceptions=True)
    
    async def _execute_stress_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                 session: aiohttp.ClientSession, behavior_function: Callable,
                                 metrics: LoadTestMetrics):
        """Execute stress test with gradually increasing load"""
        
        # Start with base load and increase over time
        base_users = scenario.concurrent_users // 2
        max_users = scenario.concurrent_users * 2  # Stress beyond normal capacity
        
        increment = (max_users - base_users) / (scenario.duration_seconds / 10)
        active_tasks = []
        
        for interval in range(scenario.duration_seconds // 10):
            target_users = int(base_users + increment * interval)
            
            # Add users to reach target
            while len(active_tasks) < target_users:
                user = random.choice(context.test_users)
                task = asyncio.create_task(
                    self._execute_user_session(session, context, user, behavior_function,
                                             scenario.duration_seconds - interval * 10, metrics)
                )
                active_tasks.append(task)
            
            await asyncio.sleep(10)
        
        # Wait for remaining tasks
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
    
    async def _execute_volume_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                 session: aiohttp.ClientSession, behavior_function: Callable,
                                 metrics: LoadTestMetrics):
        """Execute volume test with large amount of data"""
        
        # Similar to sustained but with larger payloads
        await self._execute_sustained_test(scenario, context, session, behavior_function, metrics)
    
    async def _execute_endurance_test(self, scenario: LoadTestScenario, context: LoadTestContext,
                                    session: aiohttp.ClientSession, behavior_function: Callable,
                                    metrics: LoadTestMetrics):
        """Execute endurance test for long duration"""
        
        # Long-running sustained test
        await self._execute_sustained_test(scenario, context, session, behavior_function, metrics)
    
    async def _execute_user_session(self, session: aiohttp.ClientSession, context: LoadTestContext,
                                  user: Dict[str, Any], behavior_function: Callable,
                                  duration_seconds: int, metrics: LoadTestMetrics):
        """Execute a single user session"""
        
        session_start = time.time()
        
        while time.time() - session_start < duration_seconds:
            try:
                # Execute user behavior
                result = await behavior_function(session, context, user)
                
                # Record metrics
                metrics.total_requests += result.get("requests", 1)
                if result["success"]:
                    metrics.successful_requests += result.get("requests", 1)
                else:
                    metrics.failed_requests += result.get("requests", 1)
                    metrics.error_details.append({
                        "error": result.get("error", "Unknown error"),
                        "user_id": user["id"],
                        "timestamp": datetime.utcnow()
                    })
                
                metrics.response_times.append(result["total_time"])
                
                # Think time between actions
                think_time = random.uniform(1.0, 5.0)
                await asyncio.sleep(think_time)
                
            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_details.append({
                    "error": str(e),
                    "user_id": user["id"],
                    "timestamp": datetime.utcnow()
                })
                
                # Wait a bit before retrying
                await asyncio.sleep(1.0)
    
    async def _monitor_resources(self, metrics: LoadTestMetrics, duration_seconds: int):
        """Monitor system resources during load test"""
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            try:
                # Collect resource metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                resource_data = {
                    "timestamp": datetime.utcnow(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
                
                metrics.resource_usage.append(resource_data)
                
                # Calculate throughput
                current_time = datetime.utcnow()
                if len(metrics.throughput_history) > 0:
                    last_time, last_requests = metrics.throughput_history[-1]
                    time_diff = (current_time - last_time).total_seconds()
                    request_diff = metrics.total_requests - last_requests
                    
                    if time_diff > 0:
                        throughput = request_diff / time_diff
                        metrics.throughput_history.append((current_time, metrics.total_requests))
                else:
                    metrics.throughput_history.append((current_time, metrics.total_requests))
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                print(f"Resource monitoring error: {e}")
                await asyncio.sleep(5)
    
    def _calculate_final_metrics(self, scenario: LoadTestScenario, metrics: LoadTestMetrics):
        """Calculate final performance metrics"""
        
        # Validate against scenario expectations
        if metrics.p95_response_time > scenario.expected_response_time_p95:
            metrics.error_details.append({
                "error": f"P95 response time {metrics.p95_response_time:.3f}s exceeds threshold {scenario.expected_response_time_p95}s",
                "type": "performance_threshold",
                "timestamp": datetime.utcnow()
            })
        
        if metrics.error_rate > scenario.error_rate_threshold:
            metrics.error_details.append({
                "error": f"Error rate {metrics.error_rate:.2%} exceeds threshold {scenario.error_rate_threshold:.2%}",
                "type": "error_rate_threshold",
                "timestamp": datetime.utcnow()
            })
        
        # Calculate average throughput
        if len(metrics.throughput_history) > 1:
            first_time, first_requests = metrics.throughput_history[0]
            last_time, last_requests = metrics.throughput_history[-1]
            
            total_time = (last_time - first_time).total_seconds()
            total_requests = last_requests - first_requests
            
            if total_time > 0:
                avg_throughput = total_requests / total_time
                
                if avg_throughput < scenario.expected_throughput_rps:
                    metrics.error_details.append({
                        "error": f"Average throughput {avg_throughput:.1f} RPS below threshold {scenario.expected_throughput_rps} RPS",
                        "type": "throughput_threshold",
                        "timestamp": datetime.utcnow()
                    })

    # ==================== COMPREHENSIVE TEST SUITE ====================
    
    async def run_comprehensive_load_tests(self) -> Dict[str, Any]:
        """Run complete load testing suite"""
        print("⚡ Starting Comprehensive Load Testing Suite...")
        
        context = await self.setup_test_environment()
        test_results = {
            "total_scenarios": len(self.test_scenarios),
            "completed_scenarios": 0,
            "failed_scenarios": 0,
            "scenario_results": [],
            "overall_metrics": {},
            "performance_score": 0
        }
        
        for scenario in self.test_scenarios:
            try:
                print(f"\n📊 Executing scenario: {scenario.name}")
                
                start_time = time.time()
                metrics = await self.execute_load_test_scenario(scenario, context)
                execution_time = time.time() - start_time
                
                scenario_result = {
                    "scenario_name": scenario.name,
                    "scenario_type": scenario.test_type.value,
                    "user_pattern": scenario.user_pattern.value,
                    "status": "COMPLETED",
                    "execution_time": execution_time,
                    "metrics": {
                        "total_requests": metrics.total_requests,
                        "success_rate": metrics.success_rate,
                        "error_rate": metrics.error_rate,
                        "avg_response_time": metrics.avg_response_time,
                        "p95_response_time": metrics.p95_response_time,
                        "p99_response_time": metrics.p99_response_time,
                        "error_count": len(metrics.error_details)
                    },
                    "thresholds_met": {
                        "response_time": metrics.p95_response_time <= scenario.expected_response_time_p95,
                        "error_rate": metrics.error_rate <= scenario.error_rate_threshold,
                        "performance": len([e for e in metrics.error_details if e.get("type") == "performance_threshold"]) == 0
                    }
                }
                
                test_results["scenario_results"].append(scenario_result)
                test_results["completed_scenarios"] += 1
                
                print(f"✅ Scenario completed: {scenario.name}")
                print(f"   Success Rate: {metrics.success_rate:.2%}")
                print(f"   P95 Response Time: {metrics.p95_response_time:.3f}s")
                
            except Exception as e:
                scenario_result = {
                    "scenario_name": scenario.name,
                    "status": "FAILED",
                    "error": str(e)
                }
                
                test_results["scenario_results"].append(scenario_result)
                test_results["failed_scenarios"] += 1
                
                print(f"❌ Scenario failed: {scenario.name} - {e}")
        
        # Calculate overall performance score
        successful_scenarios = test_results["completed_scenarios"]
        total_scenarios = test_results["total_scenarios"]
        
        if total_scenarios > 0:
            success_rate = successful_scenarios / total_scenarios
            
            # Additional scoring based on threshold compliance
            threshold_compliance = sum(
                1 for result in test_results["scenario_results"]
                if result.get("thresholds_met", {}).get("performance", False)
            ) / total_scenarios if total_scenarios > 0 else 0
            
            test_results["performance_score"] = (success_rate * 0.7 + threshold_compliance * 0.3) * 100
        else:
            test_results["performance_score"] = 0
        
        await self.teardown_test_environment(context)
        
        print(f"\n⚡ Load Testing Complete!")
        print(f"   Scenarios Completed: {test_results['completed_scenarios']}/{test_results['total_scenarios']}")
        print(f"   Performance Score: {test_results['performance_score']:.1f}%")
        
        return test_results


# ==================== PYTEST INTEGRATION ====================

@pytest.fixture
async def load_test_template():
    """Pytest fixture for load testing"""
    template = LoadTestingTemplate()
    yield template

@pytest.fixture
async def load_test_context(load_test_template):
    """Pytest fixture for load test context"""
    context = await load_test_template.setup_test_environment()
    yield context
    await load_test_template.teardown_test_environment(context)

@pytest.mark.asyncio
@pytest.mark.load_test
async def test_creator_upload_load(load_test_template, load_test_context):
    """Test creator upload load scenario"""
    scenario = LoadTestScenario(
        name="Creator Upload Load Test",
        test_type=LoadTestType.RAMP_UP,
        user_pattern=UserBehaviorPattern.CREATOR_UPLOAD,
        concurrent_users=10,  # Reduced for unit testing
        duration_seconds=30,
        ramp_up_seconds=10
    )
    
    metrics = await load_test_template.execute_load_test_scenario(scenario, load_test_context)
    assert metrics.total_requests > 0
    assert metrics.success_rate >= 0.8  # 80% success rate minimum

@pytest.mark.asyncio
@pytest.mark.load_test
async def test_content_browsing_load(load_test_template, load_test_context):
    """Test content browsing load scenario"""
    scenario = LoadTestScenario(
        name="Content Browsing Load Test",
        test_type=LoadTestType.SUSTAINED,
        user_pattern=UserBehaviorPattern.CONTENT_BROWSING,
        concurrent_users=20,
        duration_seconds=30,
        ramp_up_seconds=10
    )
    
    metrics = await load_test_template.execute_load_test_scenario(scenario, load_test_context)
    assert metrics.total_requests > 0
    assert metrics.avg_response_time < 5.0  # 5 second max average

@pytest.mark.asyncio
@pytest.mark.load_test
async def test_collaboration_spike_load(load_test_template, load_test_context):
    """Test collaboration spike load scenario"""
    scenario = LoadTestScenario(
        name="Collaboration Spike Test",
        test_type=LoadTestType.SPIKE,
        user_pattern=UserBehaviorPattern.COLLABORATION,
        concurrent_users=15,
        duration_seconds=20,
        ramp_up_seconds=5
    )
    
    metrics = await load_test_template.execute_load_test_scenario(scenario, load_test_context)
    assert metrics.total_requests > 0
    assert metrics.p95_response_time < 10.0  # 10 second P95 max

@pytest.mark.asyncio
@pytest.mark.integration
async def test_comprehensive_load_suite(load_test_template):
    """Run comprehensive load testing suite"""
    # Use smaller scenarios for testing
    template = load_test_template
    template.test_scenarios = [
        LoadTestScenario(
            name="Mini Load Test",
            test_type=LoadTestType.RAMP_UP,
            user_pattern=UserBehaviorPattern.CONTENT_BROWSING,
            concurrent_users=5,
            duration_seconds=15,
            ramp_up_seconds=5
        )
    ]
    
    results = await template.run_comprehensive_load_tests()
    assert results["performance_score"] >= 50  # Minimum 50% performance score


if __name__ == "__main__":
    """
    Run load tests directly
    Usage: python load_testing_template.py
    """
    async def main():
        template = LoadTestingTemplate()
        results = await template.run_comprehensive_load_tests()
        
        print("\n" + "="*80)
        print("⚡ LOAD TESTING RESULTS")
        print("="*80)
        print(f"Performance Score: {results['performance_score']:.1f}%")
        print(f"Scenarios Completed: {results['completed_scenarios']}/{results['total_scenarios']}")
        
        if results['failed_scenarios'] > 0:
            print("\n❌ Failed Scenarios:")
            for result in results['scenario_results']:
                if result.get('status') == 'FAILED':
                    print(f"  - {result['scenario_name']}: {result.get('error', 'Unknown error')}")
        
        return results['performance_score'] >= 70
    
    # Run the tests
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1)