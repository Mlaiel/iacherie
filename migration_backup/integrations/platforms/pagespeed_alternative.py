#!/usr/bin/env python3
"""
⚡ PAGESPEED INSIGHTS ALTERNATIVE
Version simplifiée utilisant des outils alternatifs de performance web
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import urllib.parse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AlternativePageSpeedResult:
    """Résultat d'analyse de performance alternative"""
    url: str
    test_method: str
    
    # Métriques basiques
    load_time: Optional[float] = None
    page_size: Optional[int] = None
    requests_count: Optional[int] = None
    
    # Status
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    
    # Conseils basiques
    recommendations: List[str] = None
    
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.recommendations is None:
            self.recommendations = []

class AlternativePageSpeedAPI:
    """Alternative à PageSpeed Insights utilisant des méthodes simples"""
    
    def __init__(self):
        self.session = None
        
        # Services alternatifs gratuits (APIs publiques limitées)
        self.alternative_services = {
            "gtmetrix": "https://gtmetrix.com/api/2.0/test",  # Nécessite inscription
            "webpagetest": "https://www.webpagetest.org/runtest.php",  # API publique
            "pingdom": "https://tools.pingdom.com/"  # Interface web seulement
        }
        
        logger.info("⚡ Alternative PageSpeed API initialisée")
        logger.info("🔧 Utilise des méthodes alternatives pour l'analyse de performance")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; IA Chéries Performance Analyzer)'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def analyze_basic_performance(self, url: str) -> Optional[AlternativePageSpeedResult]:
        """Analyse basique de performance (temps de réponse, taille, etc.)"""
        
        if not url.strip():
            logger.warning("⚠️ URL vide fournie")
            return None
            
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.warning("⚠️ URL doit commencer par http:// ou https://")
            return None
            
        logger.info(f"⚡ Analyse basique: {url}")
        
        try:
            start_time = time.time()
            
            async with self.session.get(url) as response:
                end_time = time.time()
                
                # Calculer le temps de réponse
                response_time = end_time - start_time
                
                # Récupérer le contenu pour calculer la taille
                content = await response.read()
                page_size = len(content)
                
                # Analyser les headers
                content_type = response.headers.get('content-type', '')
                server = response.headers.get('server', '')
                
                # Créer le résultat
                result = AlternativePageSpeedResult(
                    url=url,
                    test_method="Basic HTTP Analysis",
                    load_time=response_time,
                    page_size=page_size,
                    status_code=response.status,
                    response_time=response_time,
                    requests_count=1  # Requête principale seulement
                )
                
                # Générer des recommandations basiques
                recommendations = []
                
                if response_time > 3.0:
                    recommendations.append("🐌 Temps de réponse lent (>3s) - Optimiser le serveur")
                elif response_time > 1.0:
                    recommendations.append("⚠️ Temps de réponse moyen (>1s) - Optimisation recommandée")
                else:
                    recommendations.append("✅ Temps de réponse rapide (<1s)")
                
                if page_size > 5 * 1024 * 1024:  # 5MB
                    recommendations.append("📦 Page très lourde (>5MB) - Optimiser les ressources")
                elif page_size > 1 * 1024 * 1024:  # 1MB
                    recommendations.append("📦 Page lourde (>1MB) - Compression recommandée")
                else:
                    recommendations.append("✅ Taille de page acceptable")
                
                if 'gzip' not in response.headers.get('content-encoding', ''):
                    recommendations.append("🗜️ Compression GZIP non détectée - Activer la compression")
                else:
                    recommendations.append("✅ Compression GZIP activée")
                
                if not response.headers.get('cache-control'):
                    recommendations.append("🔄 Cache-Control manquant - Configurer le cache")
                else:
                    recommendations.append("✅ Headers de cache présents")
                
                result.recommendations = recommendations
                
                logger.info(f"✅ Analyse terminée: {response_time:.2f}s, {page_size} bytes")
                return result
                
        except Exception as e:
            logger.error(f"❌ Erreur d'analyse: {e}")
            return None

    async def analyze_multiple_pages(self, urls: List[str]) -> Dict[str, AlternativePageSpeedResult]:
        """Analyser plusieurs pages"""
        
        logger.info(f"⚡ Analyse de {len(urls)} pages")
        
        results = {}
        
        for url in urls:
            try:
                result = await self.analyze_basic_performance(url)
                if result:
                    results[url] = result
                
                # Pause pour éviter de surcharger les serveurs
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erreur analyse {url}: {e}")
                results[url] = None
        
        successful = sum(1 for r in results.values() if r is not None)
        logger.info(f"✅ Analyse terminée: {successful}/{len(urls)} pages analysées")
        
        return results

    def generate_performance_report(self, result: AlternativePageSpeedResult) -> str:
        """Générer un rapport de performance lisible"""
        
        if not result:
            return "❌ Aucun résultat disponible"
        
        report = f"""
⚡ RAPPORT DE PERFORMANCE - {result.url}
{'='*60}
📅 Analysé le: {result.timestamp}
🔧 Méthode: {result.test_method}

📊 MÉTRIQUES:
  • Temps de réponse: {result.response_time:.2f}s
  • Taille de la page: {result.page_size:,} bytes ({result.page_size/1024:.1f} KB)
  • Code de statut: {result.status_code}
  
🎯 ÉVALUATION:
"""
        
        if result.response_time:
            if result.response_time < 1.0:
                report += "  • ✅ Performance: EXCELLENTE (< 1s)\n"
            elif result.response_time < 3.0:
                report += "  • 🟡 Performance: BONNE (< 3s)\n"
            else:
                report += "  • 🔴 Performance: À AMÉLIORER (> 3s)\n"
        
        if result.page_size:
            if result.page_size < 500 * 1024:  # 500KB
                report += "  • ✅ Taille: OPTIMALE (< 500KB)\n"
            elif result.page_size < 2 * 1024 * 1024:  # 2MB
                report += "  • 🟡 Taille: ACCEPTABLE (< 2MB)\n"
            else:
                report += "  • 🔴 Taille: LOURDE (> 2MB)\n"
        
        report += "\n💡 RECOMMANDATIONS:\n"
        for i, rec in enumerate(result.recommendations, 1):
            report += f"  {i}. {rec}\n"
        
        return report

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur le service alternatif"""
        return {
            'service': 'Alternative PageSpeed Analysis',
            'method': 'Basic HTTP performance analysis',
            'features': [
                'Response time measurement',
                'Page size analysis',
                'Basic optimization recommendations',
                'Multiple page comparison',
                'No API key required',
                'Unlimited usage'
            ],
            'limitations': [
                'No detailed Core Web Vitals',
                'No Lighthouse integration',
                'Basic analysis only',
                'No browser rendering metrics'
            ],
            'alternatives': list(self.alternative_services.keys())
        }

# Fonctions utilitaires
async def test_alternative_pagespeed():
    """Tester l'alternative PageSpeed"""
    try:
        async with AlternativePageSpeedAPI() as alt_api:
            print("⚡ === TEST ALTERNATIVE PAGESPEED ===\n")
            
            # Test 1: Analyse simple
            print("⚡ Test analyse basique...")
            result = await alt_api.analyze_basic_performance("https://www.example.com")
            
            if result:
                print("✅ Analyse réussie!")
                print(f"   ⏱️ Temps de réponse: {result.response_time:.3f}s")
                print(f"   📦 Taille: {result.page_size:,} bytes ({result.page_size/1024:.1f} KB)")
                print(f"   📊 Status: {result.status_code}")
                print(f"   💡 Recommandations: {len(result.recommendations)}")
                
                # Afficher le rapport complet
                report = alt_api.generate_performance_report(result)
                print(f"\n{report}")
            
            # Test 2: Comparaison de sites
            print("\n⚡ Test comparaison de sites...")
            test_urls = [
                "https://www.google.com",
                "https://www.github.com"
            ]
            
            comparison = await alt_api.analyze_multiple_pages(test_urls)
            
            if comparison:
                print("✅ Comparaison terminée:")
                for url, result in comparison.items():
                    if result:
                        print(f"   {url}: {result.response_time:.3f}s ({result.page_size/1024:.1f}KB)")
            
            # Test 3: Informations service
            print("\n📊 Informations service...")
            service_info = alt_api.get_service_info()
            print(f"✅ Service: {service_info['service']}")
            print(f"🔧 Méthode: {service_info['method']}")
            print(f"⚡ Fonctionnalités: {len(service_info['features'])}")
            print(f"⚠️ Limitations: {len(service_info['limitations'])}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur test alternative: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_alternative_pagespeed())
    sys.exit(0 if result else 1)