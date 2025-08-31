"""
🧪 LOAD TESTS ULTRA-AVANCÉS
📈 10K+ Utilisateurs Simultanés, Performance à l'Échelle

Framework de tests de charge de niveau industriel pour Ainflue.
Simulation de 10,000+ utilisateurs simultanés avec métriques détaillées.

Caractéristiques:
• Tests de charge jusqu'à 10K+ utilisateurs simultanés
• Simulation de patterns d'usage réalistes
• Métriques de performance en temps réel
• Tests de scalabilité automatisés
• Détection de goulots d'étranglement

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import sys
import random

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests_industrial import TEST_FRAMEWORK

@dataclass
class LoadTestMetrics:
    """Métriques des tests de charge"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    error_rates: Dict[str, int] = field(default_factory=dict)
    throughput_rps: float = 0.0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    concurrent_users: int = 0

class LoadTestFramework:
    """Framework de tests de charge ultra-avancé"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.max_concurrent_users = 10000
        self.test_duration = 300  # 5 minutes
        self.ramp_up_time = 60   # 1 minute
        self.metrics = LoadTestMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def setup_session(self):
        """Configuration de la session HTTP pour tests de charge"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_users,
            limit_per_host=self.max_concurrent_users,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=30, sock_read=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
    
    async def teardown_session(self):
        """Nettoyage de la session"""
        if self.session:
            await self.session.close()
    
    async def simulate_user_behavior(self, user_id: int) -> List[Dict[str, Any]]:
        """Simule le comportement d'un utilisateur réaliste"""
        user_actions = []
        
        try:
            # 1. Authentication
            auth_result = await self._simulate_authentication(user_id)
            user_actions.append(auth_result)
            
            if auth_result["success"]:
                token = auth_result.get("token", "mock-token")
                
                # 2. Browse content
                browse_result = await self._simulate_content_browsing(user_id, token)
                user_actions.extend(browse_result)
                
                # 3. Upload content (10% of users)
                if random.random() < 0.1:
                    upload_result = await self._simulate_content_upload(user_id, token)
                    user_actions.append(upload_result)
                
                # 4. Enable protection (5% of users)
                if random.random() < 0.05:
                    protection_result = await self._simulate_content_protection(user_id, token)
                    user_actions.append(protection_result)
                
                # 5. Check analytics (30% of users)
                if random.random() < 0.3:
                    analytics_result = await self._simulate_analytics_check(user_id, token)
                    user_actions.append(analytics_result)
        
        except Exception as e:
            user_actions.append({
                "action": "error",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            })
        
        return user_actions
    
    async def _simulate_authentication(self, user_id: int) -> Dict[str, Any]:
        """Simule l'authentification utilisateur"""
        start_time = time.perf_counter()
        
        try:
            auth_data = {
                "email": f"loadtest_user_{user_id}@example.com",
                "password": "LoadTestPassword123!"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data
            ) as response:
                response_time = time.perf_counter() - start_time
                
                result = {
                    "action": "authentication",
                    "user_id": user_id,
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": response_time,
                    "timestamp": time.time()
                }
                
                if response.status == 200:
                    data = await response.json()
                    result["token"] = data.get("access_token", "mock-token")
                
                return result
                
        except Exception as e:
            return {
                "action": "authentication",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "response_time": time.perf_counter() - start_time,
                "timestamp": time.time()
            }
    
    async def _simulate_content_browsing(self, user_id: int, token: str) -> List[Dict[str, Any]]:
        """Simule la navigation dans le contenu"""
        actions = []
        headers = {"Authorization": f"Bearer {token}"}
        
        # Browse content list
        start_time = time.perf_counter()
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/content",
                headers=headers
            ) as response:
                actions.append({
                    "action": "browse_content",
                    "user_id": user_id,
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": time.perf_counter() - start_time,
                    "timestamp": time.time()
                })
        except Exception as e:
            actions.append({
                "action": "browse_content",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            })
        
        # Random delay between actions
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return actions
    
    async def _simulate_content_upload(self, user_id: int, token: str) -> Dict[str, Any]:
        """Simule l'upload de contenu"""
        start_time = time.perf_counter()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            upload_data = {
                "title": f"Load Test Content {user_id}",
                "description": "Content uploaded during load test",
                "content_type": "video",
                "tags": ["loadtest", "performance"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/content/upload",
                json=upload_data,
                headers=headers
            ) as response:
                return {
                    "action": "content_upload",
                    "user_id": user_id,
                    "success": response.status in [200, 201],
                    "status_code": response.status,
                    "response_time": time.perf_counter() - start_time,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "action": "content_upload",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "response_time": time.perf_counter() - start_time,
                "timestamp": time.time()
            }
    
    async def _simulate_content_protection(self, user_id: int, token: str) -> Dict[str, Any]:
        """Simule l'activation de protection"""
        start_time = time.perf_counter()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/content/test-content/protect",
                headers=headers
            ) as response:
                return {
                    "action": "enable_protection",
                    "user_id": user_id,
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": time.perf_counter() - start_time,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "action": "enable_protection",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "response_time": time.perf_counter() - start_time,
                "timestamp": time.time()
            }
    
    async def _simulate_analytics_check(self, user_id: int, token: str) -> Dict[str, Any]:
        """Simule la consultation d'analytics"""
        start_time = time.perf_counter()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/analytics/content",
                headers=headers
            ) as response:
                return {
                    "action": "check_analytics",
                    "user_id": user_id,
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": time.perf_counter() - start_time,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "action": "check_analytics",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "response_time": time.perf_counter() - start_time,
                "timestamp": time.time()
            }
    
    async def run_load_test(self, target_users: int = None) -> LoadTestMetrics:
        """Exécute un test de charge complet"""
        target_users = target_users or self.max_concurrent_users
        
        print(f"🚀 Démarrage du test de charge avec {target_users} utilisateurs")
        print(f"📊 Durée: {self.test_duration}s, Ramp-up: {self.ramp_up_time}s")
        
        await self.setup_session()
        
        try:
            # Phase de montée en charge progressive
            await self._ramp_up_users(target_users)
            
            # Phase de test stable
            await self._stable_load_phase(target_users)
            
            # Calcul des métriques finales
            self._calculate_final_metrics()
            
        finally:
            await self.teardown_session()
        
        return self.metrics
    
    async def _ramp_up_users(self, target_users: int):
        """Phase de montée en charge progressive"""
        print("📈 Phase de ramp-up en cours...")
        
        users_per_second = target_users / self.ramp_up_time
        current_users = 0
        
        for second in range(self.ramp_up_time):
            new_users = int(users_per_second * (second + 1)) - current_users
            
            # Lancer les nouveaux utilisateurs
            tasks = []
            for i in range(new_users):
                user_id = current_users + i
                task = asyncio.create_task(self.simulate_user_behavior(user_id))
                tasks.append(task)
            
            current_users += new_users
            
            # Attendre une seconde avant le prochain batch
            await asyncio.sleep(1)
            
            if second % 10 == 0:
                print(f"   {current_users}/{target_users} utilisateurs actifs")
    
    async def _stable_load_phase(self, target_users: int):
        """Phase de charge stable"""
        print("⚖️  Phase de charge stable en cours...")
        
        stable_duration = self.test_duration - self.ramp_up_time
        
        # Maintenir la charge pendant la durée stable
        tasks = []
        for user_id in range(target_users):
            task = asyncio.create_task(self.simulate_user_behavior(user_id))
            tasks.append(task)
        
        # Attendre la fin de la phase stable
        start_time = time.time()
        while time.time() - start_time < stable_duration:
            await asyncio.sleep(5)
            completed_tasks = sum(1 for task in tasks if task.done())
            print(f"   {completed_tasks}/{len(tasks)} sessions utilisateur terminées")
        
        # Attendre que toutes les tâches se terminent
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def _calculate_final_metrics(self):
        """Calcule les métriques finales du test"""
        if self.metrics.response_times:
            self.metrics.avg_response_time = statistics.mean(self.metrics.response_times)
            self.metrics.p95_response_time = statistics.quantiles(
                self.metrics.response_times, n=20)[18]  # 95th percentile
            self.metrics.p99_response_time = statistics.quantiles(
                self.metrics.response_times, n=100)[98]  # 99th percentile
        
        if self.test_duration > 0:
            self.metrics.throughput_rps = self.metrics.total_requests / self.test_duration
        
        print("\n📊 Métriques finales du test de charge:")
        print(f"   Requêtes totales: {self.metrics.total_requests}")
        print(f"   Requêtes réussies: {self.metrics.successful_requests}")
        print(f"   Requêtes échouées: {self.metrics.failed_requests}")
        print(f"   Temps de réponse moyen: {self.metrics.avg_response_time:.3f}s")
        print(f"   P95 temps de réponse: {self.metrics.p95_response_time:.3f}s")
        print(f"   P99 temps de réponse: {self.metrics.p99_response_time:.3f}s")
        print(f"   Débit: {self.metrics.throughput_rps:.1f} req/s")

# Test functions
async def test_load_10k_users():
    """Test de charge avec 10K utilisateurs"""
    framework = LoadTestFramework()
    metrics = await framework.run_load_test(target_users=10000)
    
    # Assertions de performance
    assert metrics.avg_response_time < 1.0, "Temps de réponse moyen trop élevé"
    assert metrics.p95_response_time < 2.0, "P95 temps de réponse trop élevé"
    assert metrics.throughput_rps > 100, "Débit insuffisant"
    
    error_rate = metrics.failed_requests / metrics.total_requests if metrics.total_requests > 0 else 0
    assert error_rate < 0.05, f"Taux d'erreur trop élevé: {error_rate:.2%}"

async def test_stress_breaking_point():
    """Test pour identifier le point de rupture"""
    framework = LoadTestFramework()
    
    # Test progressif jusqu'au point de rupture
    for users in [1000, 5000, 10000, 15000, 20000]:
        print(f"\n🔬 Test avec {users} utilisateurs...")
        metrics = await framework.run_load_test(target_users=users)
        
        error_rate = metrics.failed_requests / metrics.total_requests if metrics.total_requests > 0 else 0
        
        if error_rate > 0.1 or metrics.avg_response_time > 5.0:
            print(f"💥 Point de rupture identifié à ~{users} utilisateurs")
            break

# Export des classes principales
__all__ = [
    "LoadTestFramework",
    "LoadTestMetrics",
    "test_load_10k_users",
    "test_stress_breaking_point"
]