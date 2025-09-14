"""
Enterprise SEO Revenue Intelligence System
========================================

Module consolidé pour l'intelligence et monétisation SEO.
Combine: seo_revenue_optimizer.py + keyword_monetization_engine.py + content_seo_revenue_tracker.py + organic_traffic_monetizer.py + seo_performance_revenue_analyzer.py

Architecture FinTech Enterprise pour:
- Optimisation revenus via SEO intelligent
- Monétisation des mots-clés premium
- Tracking revenus du trafic organique
- Analyse performance SEO-revenue corrélation
- Intelligence artificielle pour stratégies SEO
- Automatisation des optimisations revenue-focused
- Prédictions de performance SEO-monétisation

Expert Roles Intégrés:
- Lead Dev IA: Algorithmes ML pour prédictions SEO et revenus
- Backend Senior: Architecture scalable pour big data SEO
- ML Engineer: Modèles d'optimisation et prédiction performances
- DBA: Optimisation requêtes pour analytics SEO massives
- Security: Protection données SEO sensibles et stratégies
- Microservices: APIs découplées pour intégrations SEO
- FinTech: Monétisation et tracking revenus SEO
- DevOps: Monitoring performances et scaling automatique
- AI Prompt Engineer: Prompts pour optimisation contenu SEO
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import re
from collections import defaultdict, Counter
import statistics

# ML Libraries
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# NLP Libraries
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
from collections import defaultdict

# FastAPI & Database
from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, DateTime, Decimal as SQLDecimal, Boolean, JSON, Text, Float
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

# Cache & Queue
import redis
from celery import Celery

# Web Scraping & SEO
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Configuration
logger = logging.getLogger(__name__)
Base = declarative_base()

class SEOMetricType(Enum):
    """Types de métriques SEO"""
    KEYWORD_RANKING = "keyword_ranking"
    ORGANIC_TRAFFIC = "organic_traffic"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    BOUNCE_RATE = "bounce_rate"
    PAGE_SPEED = "page_speed"
    BACKLINK_QUALITY = "backlink_quality"
    CONTENT_QUALITY = "content_quality"

class KeywordDifficulty(Enum):
    """Difficulté des mots-clés"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class ContentType(Enum):
    """Types de contenu SEO"""
    BLOG_POST = "blog_post"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    VIDEO_CONTENT = "video_content"
    INFOGRAPHIC = "infographic"
    PODCAST = "podcast"
    SOCIAL_POST = "social_post"

class RevenueOptimizationStrategy(Enum):
    """Stratégies d'optimisation revenus"""
    KEYWORD_TARGETING = "keyword_targeting"
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    LINK_BUILDING = "link_building"
    USER_EXPERIENCE = "user_experience"
    CONVERSION_OPTIMIZATION = "conversion_optimization"

@dataclass
class SEOPerformanceMetrics:
    """Métriques de performance SEO"""
    organic_traffic: int = 0
    keyword_rankings: Dict[str, int] = field(default_factory=dict)
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    pages_per_session: float = 0.0
    revenue_per_visitor: Decimal = Decimal('0')
    total_revenue: Decimal = Decimal('0')

@dataclass
class KeywordOpportunity:
    """Opportunité de mot-clé"""
    keyword: str
    search_volume: int
    difficulty: KeywordDifficulty
    current_ranking: int
    potential_ranking: int
    revenue_potential: Decimal
    competition_level: float
    cpc: Decimal
    conversion_likelihood: float

class SEOKeywordTracking(Base):
    """Modèle pour tracking des mots-clés SEO"""
    __tablename__ = 'seo_keyword_tracking'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, nullable=False, index=True)
    content_id = Column(String, index=True)
    keyword = Column(String, nullable=False, index=True)
    search_volume = Column(Integer, default=0)
    difficulty_score = Column(Float, default=0.0)
    current_ranking = Column(Integer)
    target_ranking = Column(Integer)
    cpc = Column(SQLDecimal(10, 2))
    competition_level = Column(Float)
    revenue_potential = Column(SQLDecimal(15, 2))
    conversion_rate = Column(Float)
    tracking_frequency = Column(String, default="daily")
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class SEOContentPerformance(Base):
    """Modèle pour performance SEO du contenu"""
    __tablename__ = 'seo_content_performance'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, nullable=False, index=True)
    creator_id = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String)
    target_keywords = Column(JSON)
    organic_traffic = Column(Integer, default=0)
    click_through_rate = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    revenue_generated = Column(SQLDecimal(15, 2), default=0)
    seo_score = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)
    word_count = Column(Integer, default=0)
    backlinks_count = Column(Integer, default=0)
    social_shares = Column(Integer, default=0)
    last_optimized = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SEORevenueAttribution(Base):
    """Modèle pour attribution des revenus SEO"""
    __tablename__ = 'seo_revenue_attribution'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, nullable=False, index=True)
    content_id = Column(String, index=True)
    keyword_id = Column(String, index=True)
    traffic_source = Column(String, nullable=False)
    session_id = Column(String)
    visitor_id = Column(String)
    landing_page = Column(String)
    conversion_page = Column(String)
    revenue_amount = Column(SQLDecimal(15, 2), nullable=False)
    conversion_type = Column(String)
    attribution_model = Column(String, default="last_click")
    traffic_quality_score = Column(Float)
    seo_contribution_weight = Column(Float)
    session_data = Column(JSON)
    converted_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SEOOptimizationRecommendation(Base):
    """Modèle pour recommandations d'optimisation SEO"""
    __tablename__ = 'seo_optimization_recommendations'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, nullable=False, index=True)
    creator_id = Column(String, nullable=False, index=True)
    recommendation_type = Column(String, nullable=False)
    priority_level = Column(String, nullable=False)  # high, medium, low
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    implementation_steps = Column(JSON)
    estimated_impact = Column(JSON)  # traffic, ranking, revenue impact
    effort_required = Column(String)  # low, medium, high
    confidence_score = Column(Float)
    status = Column(String, default="pending")  # pending, in_progress, completed, rejected
    implemented_at = Column(DateTime)
    impact_measured = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SEOCompetitorAnalysis(Base):
    """Modèle pour analyse concurrentielle SEO"""
    __tablename__ = 'seo_competitor_analysis'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, nullable=False, index=True)
    competitor_domain = Column(String, nullable=False)
    competitor_name = Column(String)
    analysis_type = Column(String, nullable=False)
    keyword_overlap = Column(JSON)
    content_gaps = Column(JSON)
    backlink_comparison = Column(JSON)
    technical_comparison = Column(JSON)
    revenue_estimation = Column(SQLDecimal(15, 2))
    traffic_estimation = Column(Integer)
    competitive_advantage_score = Column(Float)
    opportunities_identified = Column(JSON)
    threats_identified = Column(JSON)
    analyzed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SEORevenueIntelligenceSystem:
    """
    Système principal d'intelligence SEO pour la monétisation
    Architecture enterprise pour optimisation revenus via SEO
    """
    
    def __init__(self, db_session -> None: Session, redis_client -> None: redis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'ranking_check_frequency': 'daily',
            'min_search_volume': 100,
            'max_keyword_difficulty': 80,
            'target_page_speed': 3.0,  # seconds
            'min_content_length': 1000,  # words
            'revenue_attribution_window': 30  # days
        }
        
        # ML Models
        self.ranking_predictor = None
        self.revenue_predictor = None
        self.keyword_opportunity_scorer = None
        self._initialize_ml_models()
        
        # Composants spécialisés
        self.keyword_monetizer = KeywordMonetizationEngine(db_session, redis_client)
        self.content_tracker = ContentSEORevenueTracker(db_session, redis_client)
        self.traffic_monetizer = OrganicTrafficMonetizer(db_session, redis_client)
        self.performance_analyzer = SEOPerformanceRevenueAnalyzer(db_session, redis_client)
    
    def _initialize_ml_models(self) -> None:
        """Initialiser les modèles ML pour SEO"""
        try:
            # Modèle de prédiction de ranking
            self.ranking_predictor = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            )
            
            # Modèle de prédiction de revenus
            self.revenue_predictor = RandomForestRegressor(
                n_estimators=300,
                max_depth=12,
                random_state=42
            )
            
            # Scorer d'opportunités mots-clés
            self.keyword_opportunity_scorer = GradientBoostingRegressor(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.scaler = StandardScaler()
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation modèles ML SEO: {e}")
    
    async def optimize_content_for_revenue(
        self,
        content_id: str,
        target_keywords: List[str],
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimiser le contenu pour maximiser les revenus via SEO"""
        try:
            # Analyse actuelle du contenu
            current_performance = await self._analyze_content_seo_performance(content_id)
            
            # Analyse des opportunités de mots-clés
            keyword_opportunities = await self._analyze_keyword_opportunities(
                target_keywords, content_id
            )
            
            # Génération des recommandations d'optimisation
            optimization_recommendations = await self._generate_optimization_recommendations(
                content_id, current_performance, keyword_opportunities, optimization_goals
            )
            
            # Prédiction de l'impact revenue
            predicted_impact = await self._predict_optimization_impact(
                content_id, optimization_recommendations
            )
            
            # Priorisation des recommandations par ROI
            prioritized_recommendations = await self._prioritize_recommendations_by_roi(
                optimization_recommendations, predicted_impact
            )
            
            # Enregistrement des recommandations
            for recommendation in prioritized_recommendations:
                await self._save_optimization_recommendation(content_id, recommendation)
            
            return {
                'content_id': content_id,
                'current_performance': current_performance,
                'keyword_opportunities': keyword_opportunities,
                'optimization_recommendations': prioritized_recommendations,
                'predicted_impact': predicted_impact,
                'implementation_priority': await self._calculate_implementation_priority(
                    prioritized_recommendations
                )
            }
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation contenu revenue: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _analyze_content_seo_performance(self, content_id: str) -> Dict[str, Any]:
        """Analyser les performances SEO actuelles du contenu"""
        try:
            # Récupération des données de performance
            performance = self.db.query(SEOContentPerformance).filter(
                SEOContentPerformance.content_id == content_id
            ).first()
            
            if not performance:
                return {
                    'organic_traffic': 0,
                    'click_through_rate': 0.0,
                    'conversion_rate': 0.0,
                    'revenue_generated': 0.0,
                    'seo_score': 0.0
                }
            
            # Analyse des tendances
            performance_history = await self._get_performance_history(content_id)
            trends = await self._calculate_performance_trends(performance_history)
            
            # Analyse des mots-clés actuels
            keyword_performance = await self._analyze_keyword_performance(content_id)
            
            # Score de qualité du contenu
            content_quality_score = await self._calculate_content_quality_score(content_id)
            
            return {
                'organic_traffic': performance.organic_traffic,
                'click_through_rate': performance.click_through_rate,
                'conversion_rate': performance.conversion_rate,
                'revenue_generated': float(performance.revenue_generated),
                'seo_score': performance.seo_score,
                'content_quality_score': content_quality_score,
                'keyword_performance': keyword_performance,
                'trends': trends,
                'backlinks_count': performance.backlinks_count,
                'social_shares': performance.social_shares
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse performance SEO: {e}")
            return {}
    
    async def _analyze_keyword_opportunities(
        self,
        target_keywords: List[str],
        content_id: str
    ) -> List[KeywordOpportunity]:
        """Analyser les opportunités de mots-clés"""
        try:
            opportunities = []
            
            for keyword in target_keywords:
                # Données de base du mot-clé
                keyword_data = await self._get_keyword_data(keyword)
                
                # Analyse de la compétition
                competition_analysis = await self._analyze_keyword_competition(keyword)
                
                # Prédiction du ranking potentiel
                potential_ranking = await self._predict_keyword_ranking_potential(
                    keyword, content_id
                )
                
                # Calcul du potentiel de revenus
                revenue_potential = await self._calculate_keyword_revenue_potential(
                    keyword, potential_ranking, keyword_data
                )
                
                opportunity = KeywordOpportunity(
                    keyword=keyword,
                    search_volume=keyword_data.get('search_volume', 0),
                    difficulty=KeywordDifficulty(keyword_data.get('difficulty', 'medium')),
                    current_ranking=keyword_data.get('current_ranking', 100),
                    potential_ranking=potential_ranking,
                    revenue_potential=revenue_potential,
                    competition_level=competition_analysis.get('level', 0.5),
                    cpc=Decimal(str(keyword_data.get('cpc', 0))),
                    conversion_likelihood=keyword_data.get('conversion_likelihood', 0.02)
                )
                
                opportunities.append(opportunity)
            
            # Tri par potentiel de revenus
            opportunities.sort(key=lambda x: x.revenue_potential, reverse=True)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Erreur analyse opportunités mots-clés: {e}")
            return []
    
    async def _generate_optimization_recommendations(
        self,
        content_id: str,
        current_performance: Dict[str, Any],
        keyword_opportunities: List[KeywordOpportunity],
        optimization_goals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Générer des recommandations d'optimisation personnalisées"""
        try:
            recommendations = []
            
            # Recommandations basées sur les mots-clés
            for opportunity in keyword_opportunities[:10]:  # Top 10
                if opportunity.revenue_potential > Decimal('100'):
                    keyword_rec = await self._generate_keyword_recommendation(
                        content_id, opportunity
                    )
                    recommendations.append(keyword_rec)
            
            # Recommandations techniques SEO
            technical_recs = await self._generate_technical_seo_recommendations(
                content_id, current_performance
            )
            recommendations.extend(technical_recs)
            
            # Recommandations de contenu
            content_recs = await self._generate_content_recommendations(
                content_id, current_performance, keyword_opportunities
            )
            recommendations.extend(content_recs)
            
            # Recommandations de conversion
            conversion_recs = await self._generate_conversion_recommendations(
                content_id, current_performance, optimization_goals
            )
            recommendations.extend(conversion_recs)
            
            # Recommandations de link building
            linkbuilding_recs = await self._generate_linkbuilding_recommendations(
                content_id, current_performance
            )
            recommendations.extend(linkbuilding_recs)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erreur génération recommandations: {e}")
            return []
    
    async def _generate_keyword_recommendation(
        self,
        content_id: str,
        opportunity: KeywordOpportunity
    ) -> Dict[str, Any]:
        """Générer une recommandation spécifique pour un mot-clé"""
        try:
            # Analyse de l'optimisation actuelle pour ce mot-clé
            current_optimization = await self._analyze_keyword_optimization(
                content_id, opportunity.keyword
            )
            
            implementation_steps = []
            
            # Optimisation title tag
            if current_optimization['title_optimization'] < 0.8:
                implementation_steps.append({
                    'action': 'optimize_title',
                    'description': f'Optimiser le title tag pour "{opportunity.keyword}"',
                    'priority': 'high',
                    'estimated_effort': 'low'
                })
            
            # Optimisation meta description
            if current_optimization['meta_description_optimization'] < 0.8:
                implementation_steps.append({
                    'action': 'optimize_meta_description',
                    'description': f'Améliorer la meta description avec "{opportunity.keyword}"',
                    'priority': 'medium',
                    'estimated_effort': 'low'
                })
            
            # Optimisation contenu
            if current_optimization['content_optimization'] < 0.7:
                implementation_steps.append({
                    'action': 'optimize_content',
                    'description': f'Améliorer l\'intégration naturelle de "{opportunity.keyword}" dans le contenu',
                    'priority': 'high',
                    'estimated_effort': 'medium'
                })
            
            # Calcul de l'impact estimé
            estimated_impact = {
                'ranking_improvement': max(0, opportunity.current_ranking - opportunity.potential_ranking),
                'traffic_increase': int(opportunity.search_volume * 0.1 * (1/opportunity.potential_ranking)),
                'revenue_increase': float(opportunity.revenue_potential),
                'confidence': 0.8 if opportunity.difficulty == KeywordDifficulty.EASY else 0.6
            }
            
            return {
                'type': 'keyword_optimization',
                'keyword': opportunity.keyword,
                'priority_level': 'high' if opportunity.revenue_potential > Decimal('500') else 'medium',
                'title': f'Optimiser pour "{opportunity.keyword}"',
                'description': f'Optimisation complète pour le mot-clé "{opportunity.keyword}" avec un potentiel de revenus de ${opportunity.revenue_potential}',
                'implementation_steps': implementation_steps,
                'estimated_impact': estimated_impact,
                'effort_required': 'medium',
                'confidence_score': estimated_impact['confidence']
            }
            
        except Exception as e:
            self.logger.error(f"Erreur génération recommandation mot-clé: {e}")
            return {}
    
    async def track_seo_revenue_attribution(
        self,
        session_data: Dict[str, Any],
        conversion_data: Dict[str, Any]
    ) -> str:
        """Tracker l'attribution des revenus SEO"""
        try:
            # Analyse de la source de trafic
            traffic_source = await self._analyze_traffic_source(session_data)
            
            if traffic_source['type'] != 'organic':
                return None
            
            # Identification du contenu de landing
            content_id = await self._identify_landing_content(
                session_data.get('landing_page')
            )
            
            # Identification du mot-clé source
            keyword_id = await self._identify_source_keyword(
                session_data, traffic_source
            )
            
            # Calcul du score de contribution SEO
            seo_contribution_weight = await self._calculate_seo_contribution_weight(
                session_data, conversion_data
            )
            
            # Enregistrement de l'attribution
            attribution = SEORevenueAttribution(
                creator_id=conversion_data['creator_id'],
                content_id=content_id,
                keyword_id=keyword_id,
                traffic_source='organic_search',
                session_id=session_data.get('session_id'),
                visitor_id=session_data.get('visitor_id'),
                landing_page=session_data.get('landing_page'),
                conversion_page=conversion_data.get('conversion_page'),
                revenue_amount=Decimal(str(conversion_data['revenue_amount'])),
                conversion_type=conversion_data.get('conversion_type'),
                traffic_quality_score=session_data.get('quality_score', 0.8),
                seo_contribution_weight=seo_contribution_weight,
                session_data=session_data,
                converted_at=datetime.fromisoformat(conversion_data['converted_at'])
            )
            
            self.db.add(attribution)
            self.db.commit()
            
            # Mise à jour des métriques en temps réel
            await self._update_realtime_seo_metrics(
                content_id, keyword_id, conversion_data['revenue_amount']
            )
            
            return attribution.id
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur tracking attribution SEO: {e}")
            raise
    
    async def generate_seo_revenue_forecast(
        self,
        creator_id: str,
        forecast_period_days: int = 90
    ) -> Dict[str, Any]:
        """Générer des prévisions de revenus SEO"""
        try:
            # Récupération des données historiques
            historical_data = await self._get_historical_seo_revenue_data(
                creator_id, days=365
            )
            
            # Préparation des features pour le modèle
            features = await self._prepare_forecast_features(historical_data)
            
            # Prédiction avec modèle ML
            revenue_forecast = await self._predict_revenue_with_ml(
                features, forecast_period_days
            )
            
            # Analyse des facteurs d'influence
            influence_factors = await self._analyze_forecast_influence_factors(
                creator_id, historical_data
            )
            
            # Recommandations pour améliorer les prévisions
            improvement_recommendations = await self._generate_forecast_improvement_recommendations(
                creator_id, revenue_forecast, influence_factors
            )
            
            # Scénarios optimiste/pessimiste
            scenarios = await self._generate_revenue_scenarios(
                revenue_forecast, influence_factors
            )
            
            return {
                'creator_id': creator_id,
                'forecast_period_days': forecast_period_days,
                'base_forecast': {
                    'total_revenue': float(revenue_forecast['total']),
                    'daily_average': float(revenue_forecast['daily_average']),
                    'monthly_projection': float(revenue_forecast['monthly']),
                    'confidence_interval': revenue_forecast['confidence_interval']
                },
                'scenarios': scenarios,
                'influence_factors': influence_factors,
                'improvement_recommendations': improvement_recommendations,
                'key_opportunities': await self._identify_key_opportunities(creator_id),
                'risk_factors': await self._identify_risk_factors(creator_id, historical_data)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur génération prévisions SEO: {e}")
            return {}
    
    async def get_seo_revenue_analytics(
        self,
        creator_id: str = None,
        period_days: int = 30,
        granularity: str = 'daily'
    ) -> Dict[str, Any]:
        """Obtenir les analytics détaillées SEO-revenue"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Requête de base pour attributions
            attribution_query = self.db.query(SEORevenueAttribution).filter(
                SEORevenueAttribution.converted_at >= start_date,
                SEORevenueAttribution.converted_at <= end_date
            )
            
            if creator_id:
                attribution_query = attribution_query.filter(
                    SEORevenueAttribution.creator_id == creator_id
                )
            
            attributions = attribution_query.all()
            
            # Requête pour performances de contenu
            content_query = self.db.query(SEOContentPerformance).filter(
                SEOContentPerformance.updated_at >= start_date,
                SEOContentPerformance.updated_at <= end_date
            )
            
            if creator_id:
                content_query = content_query.filter(
                    SEOContentPerformance.creator_id == creator_id
                )
            
            content_performances = content_query.all()
            
            # Métriques globales
            total_seo_revenue = sum(attr.revenue_amount for attr in attributions)
            total_organic_traffic = sum(perf.organic_traffic for perf in content_performances)
            avg_conversion_rate = statistics.mean([perf.conversion_rate for perf in content_performances if perf.conversion_rate > 0]) if content_performances else 0
            
            # Analyse par mot-clé
            keyword_performance = await self._analyze_keyword_revenue_performance(attributions)
            
            # Analyse par contenu
            content_performance = await self._analyze_content_revenue_performance(
                content_performances, attributions
            )
            
            # Tendances temporelles
            temporal_trends = await self._calculate_temporal_seo_trends(
                attributions, granularity
            )
            
            # ROI SEO
            seo_investment = await self._calculate_seo_investment(creator_id, period_days)
            seo_roi = float(total_seo_revenue / seo_investment) if seo_investment > 0 else 0
            
            # Comparaison avec autres canaux
            channel_comparison = await self._compare_seo_with_other_channels(
                creator_id, period_days
            )
            
            # Top performers
            top_keywords = sorted(
                keyword_performance.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:10]
            
            top_content = sorted(
                content_performance.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:10]
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'summary': {
                    'total_seo_revenue': float(total_seo_revenue),
                    'total_organic_traffic': total_organic_traffic,
                    'average_conversion_rate': avg_conversion_rate,
                    'revenue_per_visitor': float(total_seo_revenue / total_organic_traffic) if total_organic_traffic > 0 else 0,
                    'seo_roi': seo_roi,
                    'total_conversions': len(attributions)
                },
                'keyword_performance': {
                    'top_keywords': [
                        {
                            'keyword': kw,
                            'revenue': float(data['revenue']),
                            'traffic': data['traffic'],
                            'conversions': data['conversions'],
                            'conversion_rate': data['conversion_rate']
                        }
                        for kw, data in top_keywords
                    ],
                    'total_keywords_tracked': len(keyword_performance)
                },
                'content_performance': {
                    'top_content': [
                        {
                            'content_id': content_id,
                            'revenue': float(data['revenue']),
                            'traffic': data['traffic'],
                            'conversions': data['conversions'],
                            'seo_score': data.get('seo_score', 0)
                        }
                        for content_id, data in top_content
                    ],
                    'total_content_pieces': len(content_performance)
                },
                'trends': temporal_trends,
                'channel_comparison': channel_comparison,
                'opportunities': await self._identify_seo_revenue_opportunities(creator_id),
                'recommendations': await self._generate_seo_revenue_recommendations(creator_id)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analytics SEO revenue: {e}")
            return {}

class KeywordMonetizationEngine:
    """Moteur de monétisation des mots-clés"""
    
    def __init__(self, db_session -> None: Session, redis_client -> None: redis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
    
    async def monetize_keyword_opportunity(
        self,
        keyword: str,
        creator_id: str,
        monetization_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monétiser une opportunité de mot-clé"""
        try:
            # Analyse de la valeur du mot-clé
            keyword_value = await self._calculate_keyword_value(keyword)
            
            # Création du tracking
            keyword_tracking = SEOKeywordTracking(
                creator_id=creator_id,
                keyword=keyword,
                search_volume=keyword_value['search_volume'],
                difficulty_score=keyword_value['difficulty_score'],
                cpc=Decimal(str(keyword_value['cpc'])),
                revenue_potential=Decimal(str(keyword_value['revenue_potential'])),
                conversion_rate=keyword_value['conversion_rate']
            )
            
            self.db.add(keyword_tracking)
            self.db.commit()
            
            return {
                'keyword': keyword,
                'tracking_id': keyword_tracking.id,
                'monetization_activated': True,
                'revenue_potential': float(keyword_value['revenue_potential'])
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur monétisation mot-clé: {e}")
            raise

class ContentSEORevenueTracker:
    """Tracker spécialisé pour revenus SEO du contenu"""
    
    def __init__(self, db_session -> None: Session, redis_client -> None: redis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
    
    async def track_content_seo_performance(
        self,
        content_id: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Tracker les performances SEO du contenu"""
        try:
            # Mise à jour ou création de l'enregistrement
            performance = self.db.query(SEOContentPerformance).filter(
                SEOContentPerformance.content_id == content_id
            ).first()
            
            if not performance:
                performance = SEOContentPerformance(
                    content_id=content_id,
                    creator_id=performance_data['creator_id'],
                    content_type=performance_data['content_type'],
                    title=performance_data['title']
                )
                self.db.add(performance)
            
            # Mise à jour des métriques
            performance.organic_traffic = performance_data.get('organic_traffic', 0)
            performance.click_through_rate = performance_data.get('click_through_rate', 0.0)
            performance.conversion_rate = performance_data.get('conversion_rate', 0.0)
            performance.revenue_generated = Decimal(str(performance_data.get('revenue_generated', 0)))
            performance.seo_score = performance_data.get('seo_score', 0.0)
            performance.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur tracking performance contenu SEO: {e}")
            return False

class OrganicTrafficMonetizer:
    """Monétiseur de trafic organique"""
    
    def __init__(self, db_session -> None: Session, redis_client -> None: redis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
    
    async def optimize_traffic_monetization(
        self,
        traffic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimiser la monétisation du trafic organique"""
        try:
            # Segmentation du trafic par qualité
            traffic_segments = await self._segment_traffic_by_quality(traffic_data)
            
            # Stratégies de monétisation par segment
            monetization_strategies = {}
            
            for segment, data in traffic_segments.items():
                strategy = await self._determine_monetization_strategy(segment, data)
                monetization_strategies[segment] = strategy
            
            return {
                'traffic_segments': traffic_segments,
                'monetization_strategies': monetization_strategies,
                'total_revenue_potential': sum(
                    strategy['revenue_potential'] 
                    for strategy in monetization_strategies.values()
                )
            }
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation monétisation trafic: {e}")
            return {}

class SEOPerformanceRevenueAnalyzer:
    """Analyseur de performance SEO-revenue"""
    
    def __init__(self, db_session -> None: Session, redis_client -> None: redis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
    
    async def analyze_seo_revenue_correlation(
        self,
        creator_id: str,
        analysis_period_days: int = 90
    ) -> Dict[str, Any]:
        """Analyser la corrélation entre performance SEO et revenus"""
        try:
            # Récupération des données
            seo_data = await self._get_seo_performance_data(creator_id, analysis_period_days)
            revenue_data = await self._get_revenue_data(creator_id, analysis_period_days)
            
            # Calcul des corrélations
            correlations = {}
            
            # Corrélation trafic organique - revenus
            correlations['organic_traffic_revenue'] = await self._calculate_correlation(
                [d['organic_traffic'] for d in seo_data],
                [d['revenue'] for d in revenue_data]
            )
            
            # Corrélation ranking - revenus
            correlations['ranking_revenue'] = await self._calculate_ranking_revenue_correlation(
                seo_data, revenue_data
            )
            
            # Analyse des facteurs clés
            key_factors = await self._identify_key_performance_factors(
                seo_data, revenue_data
            )
            
            return {
                'correlations': correlations,
                'key_factors': key_factors,
                'recommendations': await self._generate_correlation_based_recommendations(
                    correlations, key_factors
                )
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse corrélation SEO-revenue: {e}")
            return {}

# Factory function
def create_seo_revenue_intelligence_system(db_session: Session, redis_client: redis.Redis) -> SEORevenueIntelligenceSystem:
    """Factory pour créer le système d'intelligence SEO revenue"""
    return SEORevenueIntelligenceSystem(db_session, redis_client)

# Export des classes principales
__all__ = [
    'SEORevenueIntelligenceSystem',
    'KeywordMonetizationEngine',
    'ContentSEORevenueTracker',
    'OrganicTrafficMonetizer',
    'SEOPerformanceRevenueAnalyzer',
    'SEOMetricType',
    'KeywordDifficulty',
    'ContentType',
    'RevenueOptimizationStrategy',
    'SEOPerformanceMetrics',
    'KeywordOpportunity',
    'create_seo_revenue_intelligence_system'
]
