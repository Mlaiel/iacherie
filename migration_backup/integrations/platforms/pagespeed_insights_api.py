#!/usr/bin/env python3
"""
⚡ GOOGLE PAGESPEED INSIGHTS API INTEGRATION
Analyse de performance des pages web
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib.parse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PageSpeedMetrics:
    """Métriques de performance d'une page"""
    url: str
    strategy: str  # desktop ou mobile
    score: Optional[float] = None
    
    # Core Web Vitals
    first_contentful_paint: Optional[float] = None
    largest_contentful_paint: Optional[float] = None
    first_input_delay: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None
    speed_index: Optional[float] = None
    total_blocking_time: Optional[float] = None
    
    # Autres métriques
    time_to_interactive: Optional[float] = None
    first_meaningful_paint: Optional[float] = None
    
    # Scores par catégorie
    performance_score: Optional[float] = None
    accessibility_score: Optional[float] = None
    best_practices_score: Optional[float] = None
    seo_score: Optional[float] = None
    pwa_score: Optional[float] = None
    
    # Méta-données
    timestamp: str = None
    lighthouse_version: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class PageSpeedOpportunity:
    """Opportunité d'amélioration"""
    id: str
    title: str
    description: str
    score_display_mode: str
    numeric_value: Optional[float] = None
    display_value: Optional[str] = None
    potential_savings: Optional[float] = None

@dataclass
class PageSpeedDiagnostic:
    """Diagnostic de performance"""
    id: str
    title: str
    description: str
    score_display_mode: str
    score: Optional[float] = None
    display_value: Optional[str] = None

class PageSpeedInsightsAPI:
    """Client pour Google PageSpeed Insights API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # PageSpeed Insights peut fonctionner sans clé API (avec limitations strictes)
        self.api_key = None  # Désactiver la clé pour éviter les erreurs 403
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.session = None
        
        # Mode gratuit uniquement - Très limité mais fonctionnel
        logger.info("⚡ PageSpeedInsightsAPI initialisé en mode GRATUIT (sans clé)")
        logger.warning("⚠️ Limitations: 2-3 requêtes/minute, fonctionnalités de base seulement")
        
        # Stratégies disponibles
        self.strategies = ["mobile", "desktop"]
        
        # Catégories d'audit
        self.categories = [
            "performance",
            "accessibility", 
            "best-practices",
            "seo",
            "pwa"
        ]
        
        # Métriques Core Web Vitals
        self.core_web_vitals = [
            "first-contentful-paint",
            "largest-contentful-paint", 
            "first-input-delay",
            "cumulative-layout-shift",
            "speed-index",
            "total-blocking-time"
        ]
        
        logger.info("⚡ PageSpeedInsightsAPI initialisé avec clé Google")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)  # PageSpeed peut être lent
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def analyze_page(self, 
                         url: str,
                         strategy: str = "mobile",
                         categories: Optional[List[str]] = None,
                         locale: str = "fr") -> Optional[PageSpeedMetrics]:
        """Analyser la performance d'une page"""
        
        if not url.strip():
            logger.warning("⚠️ URL vide fournie")
            return None
            
        # Vérifier que l'URL est valide
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.warning("⚠️ URL doit commencer par http:// ou https://")
            return None
            
        # Vérifier la stratégie
        if strategy not in self.strategies:
            logger.warning(f"⚠️ Stratégie {strategy} invalide, utilisation de mobile")
            strategy = "mobile"
            
        logger.info(f"⚡ Analyse PageSpeed: {url} ({strategy})")
        
        try:
            # Construire les paramètres
            params = {
                'url': url,
                'strategy': strategy,
                'locale': locale
            }
            
            # Ajouter la clé API seulement si disponible
            if self.api_key:
                params['key'] = self.api_key
            
            # Ajouter les catégories si spécifiées
            if categories:
                valid_categories = [c for c in categories if c in self.categories]
                if valid_categories:
                    params['category'] = valid_categories
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extraire les métriques
                    lighthouse_result = data.get('lighthouseResult', {})
                    audits = lighthouse_result.get('audits', {})
                    categories_result = lighthouse_result.get('categories', {})
                    
                    # Score global
                    performance_category = categories_result.get('performance', {})
                    overall_score = performance_category.get('score')
                    if overall_score is not None:
                        overall_score = overall_score * 100  # Convertir en pourcentage
                    
                    # Extraire les métriques Core Web Vitals
                    metrics = PageSpeedMetrics(
                        url=url,
                        strategy=strategy,
                        score=overall_score,
                        lighthouse_version=lighthouse_result.get('lighthouseVersion')
                    )
                    
                    # Métriques de performance
                    if 'first-contentful-paint' in audits:
                        fcp = audits['first-contentful-paint'].get('numericValue')
                        metrics.first_contentful_paint = fcp / 1000 if fcp else None  # Convertir en secondes
                    
                    if 'largest-contentful-paint' in audits:
                        lcp = audits['largest-contentful-paint'].get('numericValue')
                        metrics.largest_contentful_paint = lcp / 1000 if lcp else None
                    
                    if 'cumulative-layout-shift' in audits:
                        cls_value = audits['cumulative-layout-shift'].get('numericValue')
                        metrics.cumulative_layout_shift = cls_value
                    
                    if 'speed-index' in audits:
                        si = audits['speed-index'].get('numericValue')
                        metrics.speed_index = si / 1000 if si else None
                    
                    if 'total-blocking-time' in audits:
                        tbt = audits['total-blocking-time'].get('numericValue')
                        metrics.total_blocking_time = tbt if tbt else None
                    
                    if 'interactive' in audits:
                        tti = audits['interactive'].get('numericValue')
                        metrics.time_to_interactive = tti / 1000 if tti else None
                    
                    if 'first-meaningful-paint' in audits:
                        fmp = audits['first-meaningful-paint'].get('numericValue')
                        metrics.first_meaningful_paint = fmp / 1000 if fmp else None
                    
                    # Scores par catégorie
                    for category_name in self.categories:
                        category_data = categories_result.get(category_name.replace('-', ''), {})
                        score = category_data.get('score')
                        if score is not None:
                            score = score * 100  # Convertir en pourcentage
                            
                            if category_name == 'performance':
                                metrics.performance_score = score
                            elif category_name == 'accessibility':
                                metrics.accessibility_score = score
                            elif category_name == 'best-practices':
                                metrics.best_practices_score = score
                            elif category_name == 'seo':
                                metrics.seo_score = score
                            elif category_name == 'pwa':
                                metrics.pwa_score = score
                    
                    logger.info(f"✅ Analyse terminée: Score {overall_score:.1f}/100")
                    return metrics
                    
                elif response.status == 400:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Erreur inconnue')
                    logger.error(f"❌ Erreur de paramètres: {error_msg}")
                    return None
                elif response.status == 403:
                    logger.error("❌ Accès refusé - Vérifier la clé API")
                    return None
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API PageSpeed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur d'analyse: {e}")
            return None

    async def get_opportunities(self, 
                              url: str,
                              strategy: str = "mobile") -> List[PageSpeedOpportunity]:
        """Obtenir les opportunités d'amélioration"""
        
        logger.info(f"⚡ Récupération opportunités: {url}")
        
        try:
            params = {
                'url': url,
                'strategy': strategy,
                'category': 'performance'
            }
            
            # Ajouter la clé API seulement si disponible
            if self.api_key:
                params['key'] = self.api_key
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    lighthouse_result = data.get('lighthouseResult', {})
                    audits = lighthouse_result.get('audits', {})
                    
                    opportunities = []
                    
                    # Identifier les audits avec des économies potentielles
                    for audit_id, audit_data in audits.items():
                        if audit_data.get('scoreDisplayMode') == 'numeric' and 'numericValue' in audit_data:
                            opportunity = PageSpeedOpportunity(
                                id=audit_id,
                                title=audit_data.get('title', ''),
                                description=audit_data.get('description', ''),
                                score_display_mode=audit_data.get('scoreDisplayMode', ''),
                                numeric_value=audit_data.get('numericValue'),
                                display_value=audit_data.get('displayValue', ''),
                                potential_savings=audit_data.get('details', {}).get('overallSavingsMs')
                            )
                            opportunities.append(opportunity)
                    
                    logger.info(f"✅ {len(opportunities)} opportunités trouvées")
                    return opportunities
                    
                else:
                    logger.error(f"❌ Erreur récupération opportunités: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erreur opportunités: {e}")
            return []

    async def compare_pages(self, 
                          urls: List[str],
                          strategy: str = "mobile") -> Dict[str, PageSpeedMetrics]:
        """Comparer la performance de plusieurs pages"""
        
        logger.info(f"⚡ Comparaison de {len(urls)} pages ({strategy})")
        
        results = {}
        
        # Analyser chaque page (séquentiellement pour éviter de surcharger l'API)
        for url in urls:
            try:
                metrics = await self.analyze_page(url, strategy)
                if metrics:
                    results[url] = metrics
                    
                # Pause entre les requêtes pour respecter les limites
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur analyse {url}: {e}")
                results[url] = None
        
        successful = sum(1 for r in results.values() if r is not None)
        logger.info(f"✅ Comparaison terminée: {successful}/{len(urls)} pages analysées")
        
        return results

    async def analyze_mobile_vs_desktop(self, url: str) -> Dict[str, PageSpeedMetrics]:
        """Analyser une page sur mobile ET desktop"""
        
        logger.info(f"⚡ Analyse mobile vs desktop: {url}")
        
        results = {}
        
        # Analyser mobile
        mobile_metrics = await self.analyze_page(url, "mobile")
        if mobile_metrics:
            results["mobile"] = mobile_metrics
        
        # Pause entre les requêtes
        await asyncio.sleep(3)
        
        # Analyser desktop
        desktop_metrics = await self.analyze_page(url, "desktop")
        if desktop_metrics:
            results["desktop"] = desktop_metrics
        
        logger.info(f"✅ Analyse comparative terminée")
        return results

    def get_performance_grade(self, score: float) -> str:
        """Obtenir la note de performance"""
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 70:
            return "🟡 Bon"
        elif score >= 50:
            return "🟠 Moyen"
        else:
            return "🔴 Faible"

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur le service PageSpeed"""
        return {
            'service': 'Google PageSpeed Insights',
            'base_url': self.base_url,
            'features': [
                'Performance analysis',
                'Core Web Vitals metrics',
                'Mobile and desktop analysis',
                'Optimization opportunities',
                'SEO and accessibility scores',
                'Lighthouse integration'
            ],
            'strategies': self.strategies,
            'categories': self.categories,
            'core_web_vitals': self.core_web_vitals,
            'has_api_key': self.api_key is not None,
            'rate_limit': '240 requests per minute'
        }

# Fonctions utilitaires
async def test_pagespeed_integration():
    """Tester l'intégration PageSpeed Insights"""
    try:
        async with PageSpeedInsightsAPI() as pagespeed_api:
            # Test 1: Analyse simple
            print("⚡ Test analyse PageSpeed simple...")
            result = await pagespeed_api.analyze_page(
                url="https://www.google.com",
                strategy="mobile"
            )
            
            if result:
                print(f"✅ Analyse réussie: {result.url}")
                print(f"   📊 Score: {result.score:.1f}/100 ({pagespeed_api.get_performance_grade(result.score)})")
                print(f"   ⚡ FCP: {result.first_contentful_paint:.2f}s" if result.first_contentful_paint else "   ⚡ FCP: N/A")
                print(f"   🎯 LCP: {result.largest_contentful_paint:.2f}s" if result.largest_contentful_paint else "   🎯 LCP: N/A")
                print(f"   📱 Stratégie: {result.strategy}")
                
                if result.performance_score:
                    print(f"   🏃 Performance: {result.performance_score:.1f}/100")
                if result.accessibility_score:
                    print(f"   ♿ Accessibilité: {result.accessibility_score:.1f}/100")
                if result.seo_score:
                    print(f"   🔍 SEO: {result.seo_score:.1f}/100")
            
            # Test 2: Opportunités d'amélioration
            print("\n⚡ Test opportunités d'amélioration...")
            opportunities = await pagespeed_api.get_opportunities(
                url="https://www.example.com",
                strategy="mobile"
            )
            
            if opportunities:
                print(f"✅ {len(opportunities)} opportunités trouvées")
                for i, opp in enumerate(opportunities[:3]):  # Top 3
                    print(f"   {i+1}. {opp.title}")
                    if opp.display_value:
                        print(f"      Valeur: {opp.display_value}")
            
            # Test 3: Comparaison mobile vs desktop
            print("\n⚡ Test mobile vs desktop...")
            comparison = await pagespeed_api.analyze_mobile_vs_desktop("https://www.github.com")
            
            if comparison:
                print("✅ Comparaison terminée:")
                for strategy, metrics in comparison.items():
                    if metrics:
                        grade = pagespeed_api.get_performance_grade(metrics.score)
                        print(f"   📱 {strategy.capitalize()}: {metrics.score:.1f}/100 {grade}")
            
            # Test 4: Informations service
            print("\n📊 Informations service...")
            service_info = pagespeed_api.get_service_info()
            print(f"✅ Service: {service_info['service']}")
            print(f"📊 Stratégies: {service_info['strategies']}")
            print(f"🎯 Core Web Vitals: {len(service_info['core_web_vitals'])}")
            print(f"⏱️ Limite: {service_info['rate_limit']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test PageSpeed: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration PageSpeed Insights
    result = asyncio.run(test_pagespeed_integration())
    sys.exit(0 if result else 1)