"""
🛡️ Load Testing Automation - Enterprise Creator Economy
========================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

Enterprise load testing automation for Creator Economy
Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import time
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import random
import aiohttp

logger = logging.getLogger(__name__)


class LoadTestType(Enum):
    """Types of load tests"""
    BASELINE = "baseline"              # Normal load testing
    STRESS = "stress"                 # Beyond normal capacity
    SPIKE = "spike"                   # Sudden load increases
    VOLUME = "volume"                 # Large amounts of data
    ENDURANCE = "endurance"           # Extended periods
    SCALABILITY = "scalability"       # Scaling performance
    CAPACITY = "capacity"             # Maximum capacity


class TestStatus(Enum):
    """Load test status"""
    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ANALYZING = "analyzing"


class CreatorWorkload(Enum):
    """Creator Economy specific workload patterns"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESSING = "content_processing"
    CREATOR_DASHBOARD = "creator_dashboard"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    PAYMENT_PROCESSING = "payment_processing"
    ANALYTICS_VIEWING = "analytics_viewing"
    COLLABORATION = "collaboration"
    LIVE_STREAMING = "live_streaming"


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    test_id: str
    name: str
    test_type: LoadTestType
    creator_workload: CreatorWorkload
    
    # Load parameters
    concurrent_users: int = 100
    ramp_up_duration_seconds: int = 300
    test_duration_seconds: int = 1800
    ramp_down_duration_seconds: int = 300
    
    # Target endpoints
    target_endpoints: List[str] = field(default_factory=list)
    base_url: str = "https://api.ainflue.com"
    
    # Performance thresholds
    max_response_time_ms: int = 1000
    max_error_rate_percent: float = 1.0
    min_throughput_rps: int = 10
    
    # Creator Economy specific
    creator_types: List[str] = field(default_factory=lambda: ["musician", "blogger", "photographer"])
    content_sizes_mb: List[float] = field(default_factory=lambda: [1, 5, 10, 25, 50])
    simulate_real_behavior: bool = True
    include_payment_flows: bool = False
    
    # Advanced options
    data_driven: bool = False
    data_file_path: Optional[str] = None
    geo_distribution: Dict[str, float] = field(default_factory=lambda: {"us": 0.5, "eu": 0.3, "asia": 0.2})
    device_distribution: Dict[str, float] = field(default_factory=lambda: {"desktop": 0.6, "mobile": 0.4})


@dataclass
class TestResult:
    """Individual test request result"""
    timestamp: datetime
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    content_size_bytes: int = 0
    user_id: str = ""


@dataclass
class LoadTestMetrics:
    """Load test execution metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Response time metrics
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    peak_rps: float = 0.0
    data_transferred_mb: float = 0.0
    
    # Error metrics
    error_rate_percent: float = 0.0
    timeout_count: int = 0
    connection_errors: int = 0
    
    # Status code distribution
    status_codes: Dict[int, int] = field(default_factory=dict)
    
    # Creator Economy specific metrics
    creator_workflows_completed: int = 0
    content_uploads_successful: int = 0
    payment_transactions_successful: int = 0
    average_creator_session_duration: float = 0.0


@dataclass
class LoadTestExecution:
    """Load test execution tracking"""
    test_id: str
    config: LoadTestConfig
    status: TestStatus = TestStatus.SCHEDULED
    
    # Timing
    scheduled_time: datetime = field(default_factory=datetime.utcnow)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Execution state
    current_users: int = 0
    target_users: int = 0
    phase: str = "idle"  # "ramp_up", "steady", "ramp_down"
    
    # Results
    metrics: LoadTestMetrics = field(default_factory=LoadTestMetrics)
    results: List[TestResult] = field(default_factory=list)
    
    # Analysis
    performance_grade: str = "unknown"  # A, B, C, D, F
    bottlenecks_identified: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Error tracking
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class VirtualUser:
    """Virtual user for load testing"""
    
    def __init__(self, user_id: str, workload: CreatorWorkload, config: LoadTestConfig):
        self.user_id = user_id
        self.workload = workload
        self.config = config
        self.session = None
        self.creator_type = random.choice(config.creator_types)
        self.active = False
        
        # User behavior simulation
        self.session_start_time = None
        self.actions_completed = 0
        self.content_uploaded_mb = 0.0
        self.current_workflow_step = 0
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_response_time = 0.0
    
    async def initialize(self):
        """Initialize virtual user session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": f"LoadTest-VirtualUser-{self.user_id}",
                "X-Creator-Type": self.creator_type
            }
        )
        self.session_start_time = datetime.utcnow()
        self.active = True
    
    async def execute_workload(self) -> List[TestResult]:
        """Execute the workload pattern for this user"""
        results = []
        
        try:
            if self.workload == CreatorWorkload.CONTENT_UPLOAD:
                results = await self._content_upload_workflow()
            elif self.workload == CreatorWorkload.CREATOR_DASHBOARD:
                results = await self._creator_dashboard_workflow()
            elif self.workload == CreatorWorkload.PAYMENT_PROCESSING:
                results = await self._payment_processing_workflow()
            elif self.workload == CreatorWorkload.ANALYTICS_VIEWING:
                results = await self._analytics_viewing_workflow()
            else:
                results = await self._generic_workflow()
                
        except Exception as e:
            logger.error(f"Virtual user {self.user_id} workload execution failed: {str(e)}")
            
        return results
    
    async def _content_upload_workflow(self) -> List[TestResult]:
        """Simulate content upload workflow"""
        results = []
        
        # Step 1: Login
        login_result = await self._make_request("POST", "/auth/login", {
            "username": f"creator_{self.user_id}",
            "password": "test_password"
        })
        results.append(login_result)
        
        if login_result.success:
            # Step 2: Get upload URL
            upload_url_result = await self._make_request("GET", "/content/upload-url")
            results.append(upload_url_result)
            
            # Step 3: Upload content
            content_size = random.choice(self.config.content_sizes_mb)
            upload_result = await self._simulate_content_upload(content_size)
            results.append(upload_result)
            
            if upload_result.success:
                self.content_uploaded_mb += content_size
                
                # Step 4: Process content
                process_result = await self._make_request("POST", "/content/process", {
                    "content_id": f"content_{uuid.uuid4()}",
                    "processing_options": {"quality": "high", "format": "auto"}
                })
                results.append(process_result)
        
        return results
    
    async def _creator_dashboard_workflow(self) -> List[TestResult]:
        """Simulate creator dashboard workflow"""
        results = []
        
        # Dashboard views
        dashboard_endpoints = [
            "/dashboard/overview",
            "/dashboard/analytics",
            "/dashboard/content",
            "/dashboard/earnings",
            "/dashboard/audience"
        ]
        
        for endpoint in dashboard_endpoints:
            result = await self._make_request("GET", endpoint)
            results.append(result)
            
            # Simulate user reading time
            await asyncio.sleep(random.uniform(1, 3))
        
        return results
    
    async def _payment_processing_workflow(self) -> List[TestResult]:
        """Simulate payment processing workflow"""
        results = []
        
        # Payment flow
        payment_result = await self._make_request("POST", "/payments/process", {
            "amount": random.uniform(10, 500),
            "currency": "USD",
            "creator_id": f"creator_{self.user_id}",
            "payment_method": "card"
        })
        results.append(payment_result)
        
        if payment_result.success:
            # Verify payment
            verify_result = await self._make_request("GET", f"/payments/verify/{uuid.uuid4()}")
            results.append(verify_result)
        
        return results
    
    async def _analytics_viewing_workflow(self) -> List[TestResult]:
        """Simulate analytics viewing workflow"""
        results = []
        
        analytics_endpoints = [
            "/analytics/performance",
            "/analytics/audience",
            "/analytics/revenue",
            "/analytics/content-stats"
        ]
        
        for endpoint in analytics_endpoints:
            result = await self._make_request("GET", endpoint, params={
                "period": "7d",
                "metrics": "views,engagement,revenue"
            })
            results.append(result)
        
        return results
    
    async def _generic_workflow(self) -> List[TestResult]:
        """Generic workflow for other workload types"""
        results = []
        
        for endpoint in self.config.target_endpoints:
            result = await self._make_request("GET", endpoint)
            results.append(result)
            
            # Random delay between requests
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return results
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> TestResult:
        """Make HTTP request and return result"""
        start_time = time.time()
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            self.total_requests += 1
            
            async with self.session.request(method, url, json=data, params=params) as response:
                response_time_ms = (time.time() - start_time) * 1000
                content = await response.read()
                
                success = 200 <= response.status < 400
                if success:
                    self.successful_requests += 1
                
                self.total_response_time += response_time_ms
                
                return TestResult(
                    timestamp=datetime.utcnow(),
                    endpoint=endpoint,
                    method=method,
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    success=success,
                    content_size_bytes=len(content),
                    user_id=self.user_id,
                    error_message=None if success else f"HTTP {response.status}"
                )
                
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                user_id=self.user_id,
                error_message="Timeout"
            )
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                user_id=self.user_id,
                error_message=str(e)
            )
    
    async def _simulate_content_upload(self, size_mb: float) -> TestResult:
        """Simulate content upload with size"""
        start_time = time.time()
        
        # Simulate upload time based on size
        upload_time = size_mb * 0.1  # 0.1 seconds per MB
        await asyncio.sleep(upload_time)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Simulate occasional upload failures
        success = random.random() > 0.02  # 2% failure rate
        
        return TestResult(
            timestamp=datetime.utcnow(),
            endpoint="/content/upload",
            method="POST",
            response_time_ms=response_time_ms,
            status_code=200 if success else 500,
            success=success,
            content_size_bytes=int(size_mb * 1024 * 1024),
            user_id=self.user_id,
            error_message=None if success else "Upload failed"
        )
    
    async def shutdown(self):
        """Shutdown virtual user session"""
        if self.session:
            await self.session.close()
        self.active = False


class LoadTestingAutomation:
    """
    ⚡ Enterprise Load Testing Automation for Creator Economy
    
    Tests charge automatisés Creator Economy avec:
    - Creator usage pattern simulation
    - Peak traffic load testing
    - Performance regression detection
    - Capacity threshold validation
    - Creator experience impact testing
    
    Features:
    - Intelligent workload simulation based on Creator behaviors
    - Multi-region load testing with geo-distribution
    - Real-time performance monitoring during tests
    - Automated bottleneck detection and recommendations
    - Creator journey impact analysis
    """
    
    def __init__(self):
        self.automation_id = str(uuid.uuid4())
        self.active_tests: Dict[str, LoadTestExecution] = {}
        self.test_history: List[LoadTestExecution] = []
        self.test_queue: List[LoadTestConfig] = []
        
        # Test execution management
        self.executor_running = False
        self.max_concurrent_tests = 3
        self.virtual_users: Dict[str, List[VirtualUser]] = {}
        
        # Monitoring and metrics
        self.real_time_metrics: Dict[str, Any] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Creator Economy specific
        self.creator_behavior_patterns: Dict[CreatorWorkload, Dict[str, Any]] = {}
        self.peak_traffic_patterns: Dict[str, List[int]] = {}  # Hour -> user count
        
        logger.info(f"Load Testing Automation initialized: {self.automation_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize load testing automation
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Load Testing Automation...")
            
            # Setup Creator behavior patterns
            await self._setup_creator_behavior_patterns()
            
            # Initialize performance baselines
            await self._initialize_performance_baselines()
            
            # Setup peak traffic patterns
            await self._setup_peak_traffic_patterns()
            
            # Start test executor
            await self._start_test_executor()
            
            # Start monitoring
            await self._start_monitoring()
            
            logger.info("Load Testing Automation successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize load testing automation: {str(e)}")
            return False
    
    async def _setup_creator_behavior_patterns(self):
        """Setup Creator Economy behavior patterns"""
        
        self.creator_behavior_patterns = {
            CreatorWorkload.CONTENT_UPLOAD: {
                "avg_session_duration_minutes": 30,
                "requests_per_session": 15,
                "peak_hours": [9, 10, 14, 15, 19, 20],  # UTC hours
                "content_size_distribution": {"small": 0.6, "medium": 0.3, "large": 0.1},
                "success_rate_threshold": 98.0
            },
            CreatorWorkload.CREATOR_DASHBOARD: {
                "avg_session_duration_minutes": 20,
                "requests_per_session": 25,
                "peak_hours": [8, 9, 12, 13, 17, 18],
                "page_views_per_session": 8,
                "success_rate_threshold": 99.5
            },
            CreatorWorkload.PAYMENT_PROCESSING: {
                "avg_session_duration_minutes": 5,
                "requests_per_session": 8,
                "peak_hours": [10, 11, 15, 16, 20, 21],
                "transaction_amount_range": [10, 500],
                "success_rate_threshold": 99.9
            },
            CreatorWorkload.AUDIENCE_ENGAGEMENT: {
                "avg_session_duration_minutes": 45,
                "requests_per_session": 50,
                "peak_hours": [18, 19, 20, 21, 22],
                "engagement_actions_per_session": 12,
                "success_rate_threshold": 99.0
            }
        }
        
        logger.info("Creator behavior patterns configured")
    
    async def _initialize_performance_baselines(self):
        """Initialize performance baselines for different workloads"""
        
        self.performance_baselines = {
            "content_upload": {
                "avg_response_time_ms": 2000,
                "p95_response_time_ms": 5000,
                "throughput_rps": 50,
                "error_rate_percent": 1.0
            },
            "creator_dashboard": {
                "avg_response_time_ms": 300,
                "p95_response_time_ms": 800,
                "throughput_rps": 200,
                "error_rate_percent": 0.5
            },
            "payment_processing": {
                "avg_response_time_ms": 150,
                "p95_response_time_ms": 400,
                "throughput_rps": 100,
                "error_rate_percent": 0.1
            },
            "analytics_viewing": {
                "avg_response_time_ms": 500,
                "p95_response_time_ms": 1200,
                "throughput_rps": 150,
                "error_rate_percent": 0.5
            }
        }
        
        logger.info("Performance baselines initialized")
    
    async def _setup_peak_traffic_patterns(self):
        """Setup peak traffic patterns for different times"""
        
        # Typical Creator Economy traffic patterns (users per hour)
        self.peak_traffic_patterns = {
            "weekday": [
                50,   # 00:00
                30,   # 01:00
                20,   # 02:00
                15,   # 03:00
                20,   # 04:00
                40,   # 05:00
                80,   # 06:00
                150,  # 07:00
                250,  # 08:00 - Creator morning peak
                300,  # 09:00
                280,  # 10:00
                220,  # 11:00
                300,  # 12:00 - Lunch break content creation
                350,  # 13:00
                320,  # 14:00
                400,  # 15:00 - Afternoon peak
                450,  # 16:00
                500,  # 17:00
                600,  # 18:00 - Evening peak
                700,  # 19:00 - Prime content creation time
                800,  # 20:00 - Peak
                650,  # 21:00
                400,  # 22:00
                200   # 23:00
            ],
            "weekend": [
                100,  # 00:00
                60,   # 01:00
                40,   # 02:00
                30,   # 03:00
                40,   # 04:00
                60,   # 05:00
                100,  # 06:00
                180,  # 07:00
                300,  # 08:00
                450,  # 09:00 - Weekend content creation
                600,  # 10:00
                700,  # 11:00
                750,  # 12:00 - Weekend peak
                800,  # 13:00
                750,  # 14:00
                700,  # 15:00
                650,  # 16:00
                600,  # 17:00
                550,  # 18:00
                500,  # 19:00
                450,  # 20:00
                350,  # 21:00
                250,  # 22:00
                150   # 23:00
            ]
        }
        
        logger.info("Peak traffic patterns configured")
    
    async def _start_test_executor(self):
        """Start test execution engine"""
        if not self.executor_running:
            self.executor_running = True
            asyncio.create_task(self._test_executor_loop())
            logger.info("Test executor started")
    
    async def _start_monitoring(self):
        """Start real-time monitoring"""
        asyncio.create_task(self._monitoring_loop())
        logger.info("Load testing monitoring started")
    
    async def _test_executor_loop(self):
        """Main test executor loop"""
        while self.executor_running:
            try:
                # Process test queue
                if self.test_queue and len(self.active_tests) < self.max_concurrent_tests:
                    config = self.test_queue.pop(0)
                    await self._start_load_test(config)
                
                # Check for completed tests
                completed_tests = []
                for test_id, execution in self.active_tests.items():
                    if execution.status in [TestStatus.COMPLETED, TestStatus.FAILED, TestStatus.CANCELLED]:
                        completed_tests.append(test_id)
                
                # Move completed tests to history
                for test_id in completed_tests:
                    execution = self.active_tests.pop(test_id)
                    self.test_history.append(execution)
                    await self._cleanup_test_resources(execution)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Test executor loop error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _monitoring_loop(self):
        """Real-time monitoring loop"""
        while self.executor_running:
            try:
                for test_id, execution in self.active_tests.items():
                    if execution.status == TestStatus.RUNNING:
                        await self._update_real_time_metrics(execution)
                        await self._check_performance_thresholds(execution)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(30)
    
    async def schedule_load_test(self, config: LoadTestConfig) -> str:
        """
        Schedule a load test
        
        Args:
            config: Load test configuration
            
        Returns:
            str: Test ID
        """
        try:
            config.test_id = str(uuid.uuid4())
            self.test_queue.append(config)
            
            logger.info(f"Scheduled load test: {config.name} ({config.test_id})")
            return config.test_id
            
        except Exception as e:
            logger.error(f"Failed to schedule load test: {str(e)}")
            raise
    
    async def _start_load_test(self, config: LoadTestConfig):
        """Start executing a load test"""
        try:
            execution = LoadTestExecution(
                test_id=config.test_id,
                config=config,
                status=TestStatus.PREPARING,
                start_time=datetime.utcnow()
            )
            
            self.active_tests[config.test_id] = execution
            
            logger.info(f"Starting load test: {config.name}")
            
            # Execute the test
            asyncio.create_task(self._execute_load_test(execution))
            
        except Exception as e:
            logger.error(f"Failed to start load test {config.test_id}: {str(e)}")
    
    async def _execute_load_test(self, execution: LoadTestExecution):
        """Execute a load test"""
        try:
            config = execution.config
            execution.status = TestStatus.RUNNING
            
            # Create virtual users
            virtual_users = []
            for i in range(config.concurrent_users):
                user = VirtualUser(
                    user_id=f"user_{i}",
                    workload=config.creator_workload,
                    config=config
                )
                await user.initialize()
                virtual_users.append(user)
            
            self.virtual_users[execution.test_id] = virtual_users
            
            # Phase 1: Ramp up
            execution.phase = "ramp_up"
            await self._ramp_up_phase(execution, virtual_users)
            
            # Phase 2: Steady state
            execution.phase = "steady"
            await self._steady_state_phase(execution, virtual_users)
            
            # Phase 3: Ramp down
            execution.phase = "ramp_down"
            await self._ramp_down_phase(execution, virtual_users)
            
            # Complete test
            execution.status = TestStatus.ANALYZING
            await self._analyze_test_results(execution)
            
            execution.status = TestStatus.COMPLETED
            execution.end_time = datetime.utcnow()
            
            logger.info(f"Load test completed: {config.name}")
            
        except Exception as e:
            execution.status = TestStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
            logger.error(f"Load test failed {execution.test_id}: {str(e)}")
    
    async def _ramp_up_phase(self, execution: LoadTestExecution, virtual_users: List[VirtualUser]):
        """Execute ramp-up phase"""
        config = execution.config
        ramp_up_duration = config.ramp_up_duration_seconds
        user_batch_size = max(1, len(virtual_users) // 10)  # Add users in 10 batches
        
        logger.info(f"Starting ramp-up phase: {ramp_up_duration}s")
        
        active_users = []
        start_time = time.time()
        
        while len(active_users) < len(virtual_users) and (time.time() - start_time) < ramp_up_duration:
            # Add next batch of users
            batch_end = min(len(active_users) + user_batch_size, len(virtual_users))
            new_users = virtual_users[len(active_users):batch_end]
            
            # Start workloads for new users
            for user in new_users:
                asyncio.create_task(self._run_user_workload(user, execution))
            
            active_users.extend(new_users)
            execution.current_users = len(active_users)
            
            # Wait before adding next batch
            batch_interval = ramp_up_duration / 10
            await asyncio.sleep(batch_interval)
        
        # Ensure all users are active
        for user in virtual_users:
            if user not in active_users:
                asyncio.create_task(self._run_user_workload(user, execution))
        
        execution.current_users = len(virtual_users)
        logger.info(f"Ramp-up completed: {execution.current_users} users active")
    
    async def _steady_state_phase(self, execution: LoadTestExecution, virtual_users: List[VirtualUser]):
        """Execute steady state phase"""
        config = execution.config
        test_duration = config.test_duration_seconds
        
        logger.info(f"Starting steady state phase: {test_duration}s")
        
        # All users continue their workloads
        execution.target_users = len(virtual_users)
        
        # Wait for test duration
        await asyncio.sleep(test_duration)
        
        logger.info("Steady state phase completed")
    
    async def _ramp_down_phase(self, execution: LoadTestExecution, virtual_users: List[VirtualUser]):
        """Execute ramp-down phase"""
        config = execution.config
        ramp_down_duration = config.ramp_down_duration_seconds
        
        logger.info(f"Starting ramp-down phase: {ramp_down_duration}s")
        
        # Gradually stop users
        user_batch_size = max(1, len(virtual_users) // 5)  # Remove in 5 batches
        active_users = virtual_users.copy()
        
        start_time = time.time()
        
        while active_users and (time.time() - start_time) < ramp_down_duration:
            # Stop next batch of users
            batch_end = min(user_batch_size, len(active_users))
            users_to_stop = active_users[:batch_end]
            
            for user in users_to_stop:
                await user.shutdown()
                active_users.remove(user)
            
            execution.current_users = len(active_users)
            
            # Wait before stopping next batch
            batch_interval = ramp_down_duration / 5
            await asyncio.sleep(batch_interval)
        
        # Ensure all users are stopped
        for user in active_users:
            await user.shutdown()
        
        execution.current_users = 0
        logger.info("Ramp-down completed")
    
    async def _run_user_workload(self, user: VirtualUser, execution: LoadTestExecution):
        """Run workload for a virtual user"""
        try:
            while user.active and execution.status == TestStatus.RUNNING:
                # Execute workload
                results = await user.execute_workload()
                execution.results.extend(results)
                
                # Wait between workflow executions
                pattern = self.creator_behavior_patterns.get(user.workload, {})
                session_duration = pattern.get("avg_session_duration_minutes", 15)
                wait_time = random.uniform(session_duration * 30, session_duration * 90)  # 30s to 90s per minute
                
                await asyncio.sleep(wait_time)
                
        except Exception as e:
            logger.error(f"User workload error for {user.user_id}: {str(e)}")
    
    async def _update_real_time_metrics(self, execution: LoadTestExecution):
        """Update real-time metrics during test execution"""
        try:
            results = execution.results
            if not results:
                return
            
            # Calculate metrics from recent results (last 60 seconds)
            recent_cutoff = datetime.utcnow() - timedelta(seconds=60)
            recent_results = [r for r in results if r.timestamp > recent_cutoff]
            
            if recent_results:
                # Response time metrics
                response_times = [r.response_time_ms for r in recent_results]
                execution.metrics.min_response_time_ms = min(response_times)
                execution.metrics.max_response_time_ms = max(response_times)
                execution.metrics.avg_response_time_ms = statistics.mean(response_times)
                
                if len(response_times) > 1:
                    sorted_times = sorted(response_times)
                    execution.metrics.p50_response_time_ms = sorted_times[len(sorted_times) // 2]
                    execution.metrics.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
                    execution.metrics.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
                
                # Success/failure metrics
                successful = [r for r in recent_results if r.success]
                execution.metrics.successful_requests = len(successful)
                execution.metrics.failed_requests = len(recent_results) - len(successful)
                execution.metrics.total_requests = len(recent_results)
                
                if len(recent_results) > 0:
                    execution.metrics.error_rate_percent = (execution.metrics.failed_requests / len(recent_results)) * 100
                
                # Throughput
                execution.metrics.requests_per_second = len(recent_results) / 60  # Per minute to per second
                
                # Update peak RPS
                if execution.metrics.requests_per_second > execution.metrics.peak_rps:
                    execution.metrics.peak_rps = execution.metrics.requests_per_second
                
                # Status code distribution
                status_codes = defaultdict(int)
                for result in recent_results:
                    status_codes[result.status_code] += 1
                execution.metrics.status_codes = dict(status_codes)
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {str(e)}")
    
    async def _check_performance_thresholds(self, execution: LoadTestExecution):
        """Check if performance thresholds are exceeded"""
        try:
            config = execution.config
            metrics = execution.metrics
            
            warnings = []
            
            # Check response time threshold
            if metrics.avg_response_time_ms > config.max_response_time_ms:
                warning = f"Average response time {metrics.avg_response_time_ms:.2f}ms exceeds threshold {config.max_response_time_ms}ms"
                warnings.append(warning)
            
            # Check error rate threshold
            if metrics.error_rate_percent > config.max_error_rate_percent:
                warning = f"Error rate {metrics.error_rate_percent:.2f}% exceeds threshold {config.max_error_rate_percent}%"
                warnings.append(warning)
            
            # Check throughput threshold
            if metrics.requests_per_second < config.min_throughput_rps:
                warning = f"Throughput {metrics.requests_per_second:.2f} RPS below threshold {config.min_throughput_rps} RPS"
                warnings.append(warning)
            
            # Add new warnings
            for warning in warnings:
                if warning not in execution.warnings:
                    execution.warnings.append(warning)
                    logger.warning(f"Performance threshold exceeded in test {execution.test_id}: {warning}")
            
        except Exception as e:
            logger.error(f"Failed to check performance thresholds: {str(e)}")
    
    async def _analyze_test_results(self, execution: LoadTestExecution):
        """Analyze test results and generate recommendations"""
        try:
            results = execution.results
            if not results:
                return
            
            metrics = execution.metrics
            config = execution.config
            
            # Final metrics calculation
            response_times = [r.response_time_ms for r in results]
            successful_results = [r for r in results if r.success]
            
            metrics.total_requests = len(results)
            metrics.successful_requests = len(successful_results)
            metrics.failed_requests = len(results) - len(successful_results)
            
            if response_times:
                metrics.min_response_time_ms = min(response_times)
                metrics.max_response_time_ms = max(response_times)
                metrics.avg_response_time_ms = statistics.mean(response_times)
                
                sorted_times = sorted(response_times)
                metrics.p50_response_time_ms = sorted_times[len(sorted_times) // 2]
                metrics.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
                metrics.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
            
            if metrics.total_requests > 0:
                metrics.error_rate_percent = (metrics.failed_requests / metrics.total_requests) * 100
            
            # Calculate test duration
            if execution.start_time and execution.end_time:
                test_duration_seconds = (execution.end_time - execution.start_time).total_seconds()
                metrics.requests_per_second = metrics.total_requests / test_duration_seconds
            
            # Performance grading
            execution.performance_grade = self._calculate_performance_grade(metrics, config)
            
            # Identify bottlenecks
            execution.bottlenecks_identified = self._identify_bottlenecks(metrics, config)
            
            # Generate recommendations
            execution.recommendations = self._generate_recommendations(metrics, config, execution.bottlenecks_identified)
            
            # Creator Economy specific analysis
            await self._analyze_creator_impact(execution)
            
            logger.info(f"Test analysis completed for {execution.test_id}: Grade {execution.performance_grade}")
            
        except Exception as e:
            logger.error(f"Failed to analyze test results: {str(e)}")
    
    def _calculate_performance_grade(self, metrics: LoadTestMetrics, config: LoadTestConfig) -> str:
        """Calculate performance grade A-F"""
        score = 100
        
        # Response time penalty
        if metrics.avg_response_time_ms > config.max_response_time_ms:
            penalty = min(30, (metrics.avg_response_time_ms - config.max_response_time_ms) / config.max_response_time_ms * 30)
            score -= penalty
        
        # Error rate penalty
        if metrics.error_rate_percent > config.max_error_rate_percent:
            penalty = min(40, metrics.error_rate_percent * 10)
            score -= penalty
        
        # Throughput penalty
        if metrics.requests_per_second < config.min_throughput_rps:
            penalty = min(20, (config.min_throughput_rps - metrics.requests_per_second) / config.min_throughput_rps * 20)
            score -= penalty
        
        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_bottlenecks(self, metrics: LoadTestMetrics, config: LoadTestConfig) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if metrics.p95_response_time_ms > config.max_response_time_ms * 2:
            bottlenecks.append("High response time variance - possible backend bottleneck")
        
        if metrics.error_rate_percent > 5:
            bottlenecks.append("High error rate - service stability issues")
        
        if metrics.requests_per_second < config.min_throughput_rps * 0.5:
            bottlenecks.append("Low throughput - capacity limitations")
        
        # Check status code patterns
        if 500 in metrics.status_codes and metrics.status_codes[500] > metrics.total_requests * 0.01:
            bottlenecks.append("Server errors detected - backend instability")
        
        if 429 in metrics.status_codes:
            bottlenecks.append("Rate limiting triggered - need capacity scaling")
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: LoadTestMetrics, config: LoadTestConfig, bottlenecks: List[str]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if metrics.avg_response_time_ms > config.max_response_time_ms:
            recommendations.append("Consider optimizing backend queries and caching strategies")
            recommendations.append("Review database indexing and connection pooling")
        
        if metrics.error_rate_percent > config.max_error_rate_percent:
            recommendations.append("Implement circuit breakers and retry mechanisms")
            recommendations.append("Review error handling and graceful degradation")
        
        if metrics.requests_per_second < config.min_throughput_rps:
            recommendations.append("Scale horizontally by adding more instances")
            recommendations.append("Optimize resource allocation and auto-scaling policies")
        
        if "Rate limiting triggered" in bottlenecks:
            recommendations.append("Increase rate limiting thresholds or implement adaptive rate limiting")
        
        if config.creator_workload == CreatorWorkload.CONTENT_UPLOAD:
            recommendations.append("Consider implementing multipart uploads for large content")
            recommendations.append("Optimize content processing pipeline for better throughput")
        
        return recommendations
    
    async def _analyze_creator_impact(self, execution: LoadTestExecution):
        """Analyze Creator Economy specific impact"""
        try:
            virtual_users = self.virtual_users.get(execution.test_id, [])
            
            # Creator workflow completion metrics
            total_workflows = 0
            completed_workflows = 0
            content_uploads = 0
            successful_uploads = 0
            total_content_mb = 0.0
            
            for user in virtual_users:
                total_workflows += 1
                if user.successful_requests > 0:
                    completed_workflows += 1
                
                if user.workload == CreatorWorkload.CONTENT_UPLOAD:
                    content_uploads += 1
                    if user.content_uploaded_mb > 0:
                        successful_uploads += 1
                        total_content_mb += user.content_uploaded_mb
            
            # Update Creator specific metrics
            execution.metrics.creator_workflows_completed = completed_workflows
            execution.metrics.content_uploads_successful = successful_uploads
            execution.metrics.data_transferred_mb = total_content_mb
            
            if virtual_users:
                avg_session_duration = statistics.mean([
                    (datetime.utcnow() - user.session_start_time).total_seconds() / 60
                    for user in virtual_users if user.session_start_time
                ])
                execution.metrics.average_creator_session_duration = avg_session_duration
            
        except Exception as e:
            logger.error(f"Failed to analyze creator impact: {str(e)}")
    
    async def _cleanup_test_resources(self, execution: LoadTestExecution):
        """Clean up test resources"""
        try:
            # Clean up virtual users
            if execution.test_id in self.virtual_users:
                virtual_users = self.virtual_users[execution.test_id]
                for user in virtual_users:
                    await user.shutdown()
                del self.virtual_users[execution.test_id]
            
            logger.info(f"Cleaned up resources for test {execution.test_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup test resources: {str(e)}")
    
    async def get_load_testing_status(self) -> Dict[str, Any]:
        """Get comprehensive load testing status"""
        return {
            "automation_id": self.automation_id,
            "executor_running": self.executor_running,
            "active_tests": len(self.active_tests),
            "queued_tests": len(self.test_queue),
            "total_tests_completed": len(self.test_history),
            "active_test_details": {
                test_id: {
                    "name": execution.config.name,
                    "type": execution.config.test_type.value,
                    "workload": execution.config.creator_workload.value,
                    "status": execution.status.value,
                    "current_users": execution.current_users,
                    "target_users": execution.target_users,
                    "phase": execution.phase,
                    "start_time": execution.start_time.isoformat() if execution.start_time else None,
                    "requests_per_second": execution.metrics.requests_per_second,
                    "avg_response_time_ms": execution.metrics.avg_response_time_ms,
                    "error_rate_percent": execution.metrics.error_rate_percent
                }
                for test_id, execution in self.active_tests.items()
            },
            "recent_test_results": [
                {
                    "test_id": execution.test_id,
                    "name": execution.config.name,
                    "status": execution.status.value,
                    "performance_grade": execution.performance_grade,
                    "total_requests": execution.metrics.total_requests,
                    "success_rate": (execution.metrics.successful_requests / execution.metrics.total_requests * 100) if execution.metrics.total_requests > 0 else 0,
                    "avg_response_time_ms": execution.metrics.avg_response_time_ms,
                    "creator_workflows_completed": execution.metrics.creator_workflows_completed,
                    "start_time": execution.start_time.isoformat() if execution.start_time else None,
                    "end_time": execution.end_time.isoformat() if execution.end_time else None
                }
                for execution in self.test_history[-10:]  # Last 10 tests
            ],
            "performance_baselines": self.performance_baselines,
            "creator_behavior_patterns": {
                workload.value: pattern for workload, pattern in self.creator_behavior_patterns.items()
            }
        }
    
    async def health_check(self) -> bool:
        """Health check for load testing automation"""
        try:
            # Check if executor is running
            if not self.executor_running:
                return False
            
            # Check if there are too many failed tests recently
            recent_tests = [
                execution for execution in self.test_history
                if execution.end_time and (datetime.utcnow() - execution.end_time).total_seconds() < 3600  # Last hour
            ]
            
            if recent_tests:
                failed_tests = [execution for execution in recent_tests if execution.status == TestStatus.FAILED]
                failure_rate = len(failed_tests) / len(recent_tests)
                
                if failure_rate > 0.5:  # More than 50% failure rate
                    return False
            
            # Check if any tests are stuck
            stuck_tests = [
                execution for execution in self.active_tests.values()
                if execution.start_time and (datetime.utcnow() - execution.start_time).total_seconds() > 7200  # 2 hours
            ]
            
            if stuck_tests:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Load testing automation health check failed: {str(e)}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of load testing automation"""
        try:
            logger.info("Shutting down Load Testing Automation...")
            
            # Stop executor
            self.executor_running = False
            
            # Stop all active tests
            for test_id, execution in self.active_tests.items():
                execution.status = TestStatus.CANCELLED
                await self._cleanup_test_resources(execution)
            
            # Clear queued tests
            self.test_queue.clear()
            
            logger.info("Load Testing Automation shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during load testing automation shutdown: {str(e)}")


# Factory function
def create_load_testing_automation() -> LoadTestingAutomation:
    """Factory function to create load testing automation"""
    return LoadTestingAutomation()


# Example usage
async def main():
    """Example usage of load testing automation"""
    logging.basicConfig(level=logging.INFO)
    
    automation = create_load_testing_automation()
    
    try:
        # Initialize
        await automation.initialize()
        
        # Create a test configuration
        test_config = LoadTestConfig(
            test_id="",
            name="Creator Dashboard Load Test",
            test_type=LoadTestType.BASELINE,
            creator_workload=CreatorWorkload.CREATOR_DASHBOARD,
            concurrent_users=50,
            test_duration_seconds=120,  # 2 minutes for demo
            target_endpoints=["/dashboard/overview", "/dashboard/analytics"],
            max_response_time_ms=500,
            max_error_rate_percent=1.0,
            min_throughput_rps=20
        )
        
        # Schedule test
        test_id = await automation.schedule_load_test(test_config)
        print(f"Scheduled load test: {test_id}")
        
        # Monitor for a while
        for i in range(30):  # Monitor for 5 minutes
            status = await automation.get_load_testing_status()
            print(f"Active tests: {status['active_tests']}, Completed: {status['total_tests_completed']}")
            
            if status['active_test_details']:
                for test_id, details in status['active_test_details'].items():
                    print(f"  Test {test_id}: {details['status']} - {details['current_users']} users - {details['requests_per_second']:.1f} RPS")
            
            await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await automation.shutdown()


if __name__ == "__main__":
    asyncio.run(main())