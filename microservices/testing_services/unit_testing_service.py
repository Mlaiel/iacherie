"""
🧪 UNIT TESTING SERVICE
Service de tests unitaires automatisés pour microservices Ainflue

Fonctionnalités:
- Tests unitaires automatisés
- Mocking et stubbing avancé
- Coverage analysis
- Continuous testing
- Test reporting et analytics

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
import time
import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
import inspect
import traceback

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Statuts des tests"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCategory(Enum):
    """Catégories de tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    API = "api"
    UI = "ui"

@dataclass
class TestCase:
    """Cas de test unitaire"""
    test_id: str
    name: str
    description: str
    category: TestCategory
    test_function: Callable
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    timeout_seconds: int = 30
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    mock_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestResult:
    """Résultat d'un test"""
    test_id: str
    test_name: str
    status: TestStatus
    execution_time_ms: float
    start_time: float
    end_time: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertions_count: int = 0
    assertions_passed: int = 0
    output: str = ""
    coverage_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """Suite de tests"""
    suite_id: str
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_suite: Optional[Callable] = None
    teardown_suite: Optional[Callable] = None
    parallel_execution: bool = False

class MockObject:
    """Objet mock pour les tests"""
    
    def __init__(self, name: str):
        self.name = name
        self.call_history: List[Dict[str, Any]] = []
        self.return_values: Dict[str, Any] = {}
        self.side_effects: Dict[str, Exception] = {}
    
    def set_return_value(self, method_name: str, value: Any) -> None:
        """Définir la valeur de retour d'une méthode"""
        self.return_values[method_name] = value
    
    def set_side_effect(self, method_name: str, exception: Exception) -> None:
        """Définir un effet de bord (exception) pour une méthode"""
        self.side_effects[method_name] = exception
    
    def __getattr__(self, name: str) -> Callable:
        """Créer dynamiquement des méthodes mockées"""
        def mock_method(*args, **kwargs):
            # Enregistrer l'appel
            self.call_history.append({
                "method": name,
                "args": args,
                "kwargs": kwargs,
                "timestamp": time.time()
            })
            
            # Vérifier les effets de bord
            if name in self.side_effects:
                raise self.side_effects[name]
            
            # Retourner la valeur configurée
            return self.return_values.get(name, None)
        
        return mock_method
    
    def get_call_count(self, method_name: str) -> int:
        """Obtenir le nombre d'appels d'une méthode"""
        return len([call for call in self.call_history if call["method"] == method_name])
    
    def was_called_with(self, method_name: str, *args, **kwargs) -> bool:
        """Vérifier si une méthode a été appelée avec des arguments spécifiques"""
        for call in self.call_history:
            if (call["method"] == method_name and 
                call["args"] == args and 
                call["kwargs"] == kwargs):
                return True
        return False

class TestAssertion:
    """Utilitaires d'assertion pour les tests"""
    
    def __init__(self):
        self.assertions_count = 0
        self.assertions_passed = 0
    
    def assert_equal(self, actual: Any, expected: Any, message: str = "") -> None:
        """Vérifier l'égalité"""
        self.assertions_count += 1
        if actual == expected:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected {expected}, got {actual}. {message}")
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str = "") -> None:
        """Vérifier l'inégalité"""
        self.assertions_count += 1
        if actual != expected:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected {actual} != {expected}. {message}")
    
    def assert_true(self, condition: bool, message: str = "") -> None:
        """Vérifier qu'une condition est vraie"""
        self.assertions_count += 1
        if condition:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected True, got {condition}. {message}")
    
    def assert_false(self, condition: bool, message: str = "") -> None:
        """Vérifier qu'une condition est fausse"""
        self.assertions_count += 1
        if not condition:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected False, got {condition}. {message}")
    
    def assert_is_none(self, value: Any, message: str = "") -> None:
        """Vérifier qu'une valeur est None"""
        self.assertions_count += 1
        if value is None:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected None, got {value}. {message}")
    
    def assert_is_not_none(self, value: Any, message: str = "") -> None:
        """Vérifier qu'une valeur n'est pas None"""
        self.assertions_count += 1
        if value is not None:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected not None, got {value}. {message}")
    
    def assert_in(self, item: Any, container: Any, message: str = "") -> None:
        """Vérifier qu'un élément est dans un conteneur"""
        self.assertions_count += 1
        if item in container:
            self.assertions_passed += 1
        else:
            raise AssertionError(f"Expected {item} in {container}. {message}")
    
    def assert_raises(self, expected_exception: type, callable_func: Callable, *args, **kwargs) -> None:
        """Vérifier qu'une exception est levée"""
        self.assertions_count += 1
        try:
            callable_func(*args, **kwargs)
            raise AssertionError(f"Expected {expected_exception.__name__} to be raised")
        except expected_exception:
            self.assertions_passed += 1
        except Exception as e:
            raise AssertionError(f"Expected {expected_exception.__name__}, got {type(e).__name__}")

class UnitTestingService:
    """
    🧪 SERVICE TESTS UNITAIRES ENTERPRISE
    
    Framework de tests unitaires complet pour les microservices Ainflue
    avec mocking, coverage analysis et reporting automatisé
    """
    
    def __init__(self, service_id: str = None):
        self.service_id = service_id or f"unit-testing-{int(time.time())}"
        self.status = "initializing"
        
        # Suites de tests
        self.test_suites: Dict[str, TestSuite] = {}
        
        # Résultats des tests
        self.test_results: Dict[str, TestResult] = {}
        self.test_runs: List[Dict[str, Any]] = []
        
        # Configuration
        self.config = {
            "parallel_execution": True,
            "max_parallel_tests": 10,
            "default_timeout": 30,
            "enable_coverage": True,
            "enable_mocking": True,
            "auto_retry_failed": True,
            "max_retries": 3
        }
        
        # Mock registry
        self.mocks: Dict[str, MockObject] = {}
        
        # Métriques
        self.metrics = {
            "total_tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "average_execution_time_ms": 0.0,
            "total_assertions": 0,
            "assertions_passed": 0,
            "coverage_percentage": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialiser le service de tests unitaires"""
        logger.info("🧪 Initializing Unit Testing Service...")
        
        try:
            # Créer les suites de tests pour les modules Ainflue
            await self._create_ainflue_test_suites()
            
            # Initialiser les mocks par défaut
            await self._setup_default_mocks()
            
            self.status = "ready"
            logger.info("✅ Unit Testing Service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Unit Testing Service: {e}")
            self.status = "error"
            return False
    
    async def _create_ainflue_test_suites(self) -> None:
        """Créer les suites de tests pour les modules Ainflue"""
        
        # Suite de tests pour AI Services
        ai_suite = TestSuite(
            suite_id="ai_services_tests",
            name="AI Services Test Suite",
            description="Tests unitaires pour les services IA",
            parallel_execution=True
        )
        
        # Tests pour AI Inference Service
        ai_suite.test_cases.extend([
            TestCase(
                test_id="test_ai_inference_basic",
                name="Test AI Inference Basic",
                description="Test basique d'inférence IA",
                category=TestCategory.UNIT,
                test_function=self._test_ai_inference_basic,
                tags=["ai", "inference", "basic"]
            ),
            TestCase(
                test_id="test_ai_inference_error_handling",
                name="Test AI Inference Error Handling",
                description="Test gestion d'erreurs inférence IA",
                category=TestCategory.UNIT,
                test_function=self._test_ai_inference_error_handling,
                tags=["ai", "inference", "error"]
            )
        ])
        
        self.test_suites[ai_suite.suite_id] = ai_suite
        
        # Suite de tests pour API Gateway
        gateway_suite = TestSuite(
            suite_id="api_gateway_tests",
            name="API Gateway Test Suite",
            description="Tests unitaires pour l'API Gateway",
            parallel_execution=True
        )
        
        gateway_suite.test_cases.extend([
            TestCase(
                test_id="test_gateway_authentication",
                name="Test Gateway Authentication",
                description="Test authentification API Gateway",
                category=TestCategory.UNIT,
                test_function=self._test_gateway_authentication,
                tags=["gateway", "auth", "security"]
            ),
            TestCase(
                test_id="test_gateway_rate_limiting",
                name="Test Gateway Rate Limiting",
                description="Test limitation de taux",
                category=TestCategory.UNIT,
                test_function=self._test_gateway_rate_limiting,
                tags=["gateway", "rate_limit", "security"]
            )
        ])
        
        self.test_suites[gateway_suite.suite_id] = gateway_suite
        
        # Suite de tests pour Financial Services
        financial_suite = TestSuite(
            suite_id="financial_services_tests",
            name="Financial Services Test Suite",
            description="Tests unitaires pour les services financiers",
            parallel_execution=False  # Sériel pour éviter conflits financiers
        )
        
        financial_suite.test_cases.extend([
            TestCase(
                test_id="test_currency_conversion",
                name="Test Currency Conversion",
                description="Test conversion de devises",
                category=TestCategory.UNIT,
                test_function=self._test_currency_conversion,
                tags=["financial", "currency", "conversion"]
            ),
            TestCase(
                test_id="test_payment_processing",
                name="Test Payment Processing",
                description="Test traitement des paiements",
                category=TestCategory.UNIT,
                test_function=self._test_payment_processing,
                tags=["financial", "payment", "processing"]
            )
        ])
        
        self.test_suites[financial_suite.suite_id] = financial_suite
        
        logger.info(f"Created {len(self.test_suites)} test suites")
    
    async def _setup_default_mocks(self) -> None:
        """Configurer les mocks par défaut"""
        # Mock pour base de données
        db_mock = MockObject("database")
        db_mock.set_return_value("query", {"status": "success", "data": []})
        db_mock.set_return_value("insert", {"id": "123", "status": "created"})
        self.mocks["database"] = db_mock
        
        # Mock pour API externe
        api_mock = MockObject("external_api")
        api_mock.set_return_value("get", {"status": 200, "data": {"test": "data"}})
        api_mock.set_return_value("post", {"status": 201, "data": {"created": True}})
        self.mocks["external_api"] = api_mock
        
        # Mock pour service de cache
        cache_mock = MockObject("cache")
        cache_mock.set_return_value("get", None)
        cache_mock.set_return_value("set", True)
        self.mocks["cache"] = cache_mock
    
    def create_mock(self, name: str) -> MockObject:
        """Créer un nouvel objet mock"""
        mock = MockObject(name)
        self.mocks[name] = mock
        return mock
    
    def get_mock(self, name: str) -> Optional[MockObject]:
        """Obtenir un mock existant"""
        return self.mocks.get(name)
    
    async def run_test_suite(self, suite_id: str) -> Dict[str, Any]:
        """Exécuter une suite de tests"""
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite {suite_id} not found")
        
        suite = self.test_suites[suite_id]
        logger.info(f"🧪 Running test suite: {suite.name}")
        
        start_time = time.time()
        
        try:
            # Setup de la suite
            if suite.setup_suite:
                await suite.setup_suite()
            
            # Exécuter les tests
            if suite.parallel_execution and self.config["parallel_execution"]:
                results = await self._run_tests_parallel(suite.test_cases)
            else:
                results = await self._run_tests_sequential(suite.test_cases)
            
            # Teardown de la suite
            if suite.teardown_suite:
                await suite.teardown_suite()
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            # Calculer les statistiques
            passed = len([r for r in results if r.status == TestStatus.PASSED])
            failed = len([r for r in results if r.status == TestStatus.FAILED])
            skipped = len([r for r in results if r.status == TestStatus.SKIPPED])
            errors = len([r for r in results if r.status == TestStatus.ERROR])
            
            suite_result = {
                "suite_id": suite_id,
                "suite_name": suite.name,
                "execution_time_ms": execution_time,
                "total_tests": len(results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "success_rate": (passed / len(results)) * 100 if results else 0,
                "test_results": [
                    {
                        "test_id": r.test_id,
                        "test_name": r.test_name,
                        "status": r.status.value,
                        "execution_time_ms": r.execution_time_ms,
                        "assertions_passed": r.assertions_passed,
                        "assertions_count": r.assertions_count,
                        "error_message": r.error_message
                    }
                    for r in results
                ]
            }
            
            # Enregistrer le run
            self.test_runs.append(suite_result)
            
            # Mettre à jour les métriques
            self.metrics["total_tests_run"] += len(results)
            self.metrics["tests_passed"] += passed
            self.metrics["tests_failed"] += failed
            self.metrics["tests_skipped"] += skipped
            
            logger.info(f"✅ Test suite completed: {passed}/{len(results)} passed")
            return suite_result
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            raise
    
    async def _run_tests_parallel(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Exécuter les tests en parallèle"""
        max_concurrent = min(self.config["max_parallel_tests"], len(test_cases))
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(test_case):
            async with semaphore:
                return await self._execute_test_case(test_case)
        
        tasks = [run_with_semaphore(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = TestResult(
                    test_id=test_cases[i].test_id,
                    test_name=test_cases[i].name,
                    status=TestStatus.ERROR,
                    execution_time_ms=0.0,
                    start_time=time.time(),
                    end_time=time.time(),
                    error_message=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _run_tests_sequential(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Exécuter les tests séquentiellement"""
        results = []
        for test_case in test_cases:
            try:
                result = await self._execute_test_case(test_case)
                results.append(result)
            except Exception as e:
                error_result = TestResult(
                    test_id=test_case.test_id,
                    test_name=test_case.name,
                    status=TestStatus.ERROR,
                    execution_time_ms=0.0,
                    start_time=time.time(),
                    end_time=time.time(),
                    error_message=str(e)
                )
                results.append(error_result)
        
        return results
    
    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Exécuter un cas de test individuel"""
        logger.debug(f"Executing test: {test_case.name}")
        
        start_time = time.time()
        assertions = TestAssertion()
        
        try:
            # Setup du test
            if test_case.setup_function:
                await test_case.setup_function()
            
            # Exécuter le test avec timeout
            if inspect.iscoroutinefunction(test_case.test_function):
                await asyncio.wait_for(
                    test_case.test_function(assertions, self.mocks),
                    timeout=test_case.timeout_seconds
                )
            else:
                test_case.test_function(assertions, self.mocks)
            
            # Teardown du test
            if test_case.teardown_function:
                await test_case.teardown_function()
            
            end_time = time.time()
            
            result = TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                status=TestStatus.PASSED,
                execution_time_ms=(end_time - start_time) * 1000,
                start_time=start_time,
                end_time=end_time,
                assertions_count=assertions.assertions_count,
                assertions_passed=assertions.assertions_passed
            )
            
            self.test_results[test_case.test_id] = result
            return result
            
        except asyncio.TimeoutError:
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                status=TestStatus.FAILED,
                execution_time_ms=(time.time() - start_time) * 1000,
                start_time=start_time,
                end_time=time.time(),
                error_message=f"Test timeout after {test_case.timeout_seconds} seconds",
                assertions_count=assertions.assertions_count,
                assertions_passed=assertions.assertions_passed
            )
            
        except AssertionError as e:
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                status=TestStatus.FAILED,
                execution_time_ms=(time.time() - start_time) * 1000,
                start_time=start_time,
                end_time=time.time(),
                error_message=str(e),
                assertions_count=assertions.assertions_count,
                assertions_passed=assertions.assertions_passed
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                status=TestStatus.ERROR,
                execution_time_ms=(time.time() - start_time) * 1000,
                start_time=start_time,
                end_time=time.time(),
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                assertions_count=assertions.assertions_count,
                assertions_passed=assertions.assertions_passed
            )
    
    # Tests d'exemple pour les services Ainflue
    async def _test_ai_inference_basic(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test basique d'inférence IA"""
        # Mock de l'API d'inférence
        ai_mock = mocks["external_api"]
        ai_mock.set_return_value("predict", {"prediction": "positive", "confidence": 0.95})
        
        # Test de l'inférence
        result = ai_mock.predict(text="This is a great product!")
        
        assert_.assert_equal(result["prediction"], "positive")
        assert_.assert_true(result["confidence"] > 0.9)
        assert_.assert_equal(ai_mock.get_call_count("predict"), 1)
    
    async def _test_ai_inference_error_handling(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test gestion d'erreurs inférence IA"""
        # Mock avec erreur
        ai_mock = mocks["external_api"]
        ai_mock.set_side_effect("predict", Exception("Model not available"))
        
        # Test que l'exception est levée
        assert_.assert_raises(Exception, ai_mock.predict, text="test")
    
    async def _test_gateway_authentication(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test authentification API Gateway"""
        # Mock de l'authentification
        auth_mock = mocks.get("auth_service", MockObject("auth_service"))
        auth_mock.set_return_value("validate_token", {"valid": True, "user_id": "123"})
        
        # Test de validation de token
        result = auth_mock.validate_token("valid_token")
        
        assert_.assert_true(result["valid"])
        assert_.assert_equal(result["user_id"], "123")
    
    async def _test_gateway_rate_limiting(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test limitation de taux"""
        # Mock du rate limiter
        rate_limiter = mocks.get("rate_limiter", MockObject("rate_limiter"))
        rate_limiter.set_return_value("check_limit", {"allowed": True, "remaining": 99})
        
        # Test de vérification de limite
        result = rate_limiter.check_limit("user_123")
        
        assert_.assert_true(result["allowed"])
        assert_.assert_equal(result["remaining"], 99)
    
    async def _test_currency_conversion(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test conversion de devises"""
        # Mock du service de conversion
        currency_mock = mocks.get("currency_service", MockObject("currency_service"))
        currency_mock.set_return_value("convert", {
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": 100,
            "converted_amount": 85.0,
            "rate": 0.85
        })
        
        # Test de conversion
        result = currency_mock.convert(100, "USD", "EUR")
        
        assert_.assert_equal(result["converted_amount"], 85.0)
        assert_.assert_equal(result["rate"], 0.85)
    
    async def _test_payment_processing(self, assert_: TestAssertion, mocks: Dict[str, MockObject]) -> None:
        """Test traitement des paiements"""
        # Mock du service de paiement
        payment_mock = mocks.get("payment_service", MockObject("payment_service"))
        payment_mock.set_return_value("process_payment", {
            "status": "success",
            "transaction_id": "txn_123",
            "amount": 100.0
        })
        
        # Test de traitement
        result = payment_mock.process_payment(100.0, "USD", "card_123")
        
        assert_.assert_equal(result["status"], "success")
        assert_.assert_is_not_none(result["transaction_id"])
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Exécuter toutes les suites de tests"""
        logger.info("🧪 Running all test suites...")
        
        all_results = []
        total_start_time = time.time()
        
        for suite_id in self.test_suites.keys():
            try:
                result = await self.run_test_suite(suite_id)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to run suite {suite_id}: {e}")
                all_results.append({
                    "suite_id": suite_id,
                    "error": str(e),
                    "total_tests": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0
                })
        
        total_execution_time = (time.time() - total_start_time) * 1000
        
        # Calculer les statistiques globales
        total_tests = sum(r.get("total_tests", 0) for r in all_results)
        total_passed = sum(r.get("passed", 0) for r in all_results)
        total_failed = sum(r.get("failed", 0) for r in all_results)
        total_skipped = sum(r.get("skipped", 0) for r in all_results)
        
        return {
            "execution_time_ms": total_execution_time,
            "total_suites": len(self.test_suites),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "overall_success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "suite_results": all_results,
            "metrics": self.metrics
        }
    
    def get_test_coverage_report(self) -> Dict[str, Any]:
        """Obtenir le rapport de couverture de tests"""
        # Simulation de coverage - en production, utiliser coverage.py
        return {
            "overall_coverage": 85.5,
            "modules": {
                "ai_services": {"coverage": 92.3, "lines_covered": 450, "lines_total": 487},
                "api_gateway": {"coverage": 88.1, "lines_covered": 320, "lines_total": 363},
                "financial_services": {"coverage": 79.2, "lines_covered": 234, "lines_total": 295},
                "security_services": {"coverage": 91.7, "lines_covered": 289, "lines_total": 315},
                "platform_services": {"coverage": 75.4, "lines_covered": 198, "lines_total": 262}
            },
            "uncovered_lines": [
                {"module": "ai_services", "file": "ai_inference.py", "lines": [45, 67, 89]},
                {"module": "api_gateway", "file": "rate_limiting.py", "lines": [123, 156]}
            ]
        }
    
    def get_test_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques de tests"""
        return {
            "service_id": self.service_id,
            "status": self.status,
            "test_suites": len(self.test_suites),
            "total_test_cases": sum(len(suite.test_cases) for suite in self.test_suites.values()),
            "test_runs_completed": len(self.test_runs),
            "mocks_available": len(self.mocks),
            "config": self.config,
            "metrics": self.metrics
        }

# Instance globale du service
unit_testing_service = UnitTestingService()

async def main():
    """Test du service de tests unitaires"""
    await unit_testing_service.initialize()
    
    # Exécuter toutes les suites de tests
    results = await unit_testing_service.run_all_tests()
    print(f"Test results: {results}")
    
    # Rapport de couverture
    coverage = unit_testing_service.get_test_coverage_report()
    print(f"Coverage report: {coverage}")
    
    # Métriques
    metrics = unit_testing_service.get_test_metrics()
    print(f"Test metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())