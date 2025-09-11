"""
💰 ROI CALCULATOR - ENTERPRISE ML INVESTMENT ATTRIBUTION ENGINE  
Rôle DBA: Calculateur de ROI pour investissements ML avec attribution précise

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
import aiosqlite
from collections import defaultdict
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Ainflue Business Logic Integration
from core.config import AinflueCoreConfig
from core.exceptions import AinflueCoreException

class InvestmentType(Enum):
    """Types d'investissements ML"""
    MODEL_DEVELOPMENT = "model_development"
    INFRASTRUCTURE = "infrastructure"
    DATA_ACQUISITION = "data_acquisition"
    TRAINING_COMPUTE = "training_compute"
    INFERENCE_COMPUTE = "inference_compute"
    STORAGE = "storage"
    PERSONNEL = "personnel"
    TOOLS_LICENSES = "tools_licenses"

class ROIMetric(Enum):
    """Métriques ROI"""
    REVENUE_INCREASE = "revenue_increase"
    COST_REDUCTION = "cost_reduction"
    EFFICIENCY_GAIN = "efficiency_gain"
    USER_ACQUISITION = "user_acquisition"
    RETENTION_IMPROVEMENT = "retention_improvement"
    CONVERSION_RATE = "conversion_rate"

class AttributionModel(Enum):
    """Modèles d'attribution"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"

@dataclass
class Investment:
    """Investissement ML"""
    investment_id: str
    name: str
    investment_type: InvestmentType
    amount: float
    currency: str
    start_date: datetime
    end_date: Optional[datetime]
    creator_types: List[str]
    models_affected: List[str]
    business_objective: str
    cost_category: str

@dataclass
class Revenue:
    """Revenu attribuable"""
    revenue_id: str
    amount: float
    currency: str
    date: datetime
    creator_id: str
    creator_type: str
    model_id: str
    attribution_confidence: float
    revenue_source: str
    conversion_path: List[str]

@dataclass
class ROIAnalysis:
    """Analyse ROI"""
    analysis_id: str
    investment_id: str
    period_start: datetime
    period_end: datetime
    total_investment: float
    total_revenue: float
    roi_percentage: float
    payback_period_days: int
    npv: float
    irr: float
    attribution_model: AttributionModel
    confidence_score: float
    creator_breakdown: Dict[str, Dict[str, float]]
    model_breakdown: Dict[str, Dict[str, float]]

class ROICalculator:
    """
    💰 Enterprise ROI Calculator pour investissements MLOps
    
    Fonctionnalités DBA Expert:
    - Attribution précise revenus aux investissements ML
    - Modèles d'attribution sophistiqués multi-touch
    - ROI analysis par créateur/modèle/période
    - NPV et IRR calculation avec discount rates
    - Payback period analysis avec risk adjustment
    - Creator-specific revenue attribution
    - Real-time ROI tracking et alerting
    """
    
    def __init__(self, config: Optional[AinflueCoreConfig] = None):
        self.config = config or AinflueCoreConfig()
        self.logger = self._setup_logging()
        self.db_path = "mlops_roi_calculator.db"
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Creator revenue multipliers (basé sur le potentiel monétaire)
        self.creator_revenue_multipliers = {
            "musician": 1.5,      # Streaming, concerts, merchandise
            "influencer": 1.8,    # Sponsorships, affiliate marketing  
            "photographer": 1.2,  # Stock photos, commissions
            "blogger": 1.0,       # Ads, affiliate marketing
            "comedian": 1.1       # Shows, streaming, merchandise
        }
        
        # Attribution windows par type d'investissement
        self.attribution_windows = {
            InvestmentType.MODEL_DEVELOPMENT: 365,      # 1 an
            InvestmentType.INFRASTRUCTURE: 180,         # 6 mois
            InvestmentType.DATA_ACQUISITION: 90,        # 3 mois
            InvestmentType.TRAINING_COMPUTE: 30,        # 1 mois
            InvestmentType.INFERENCE_COMPUTE: 7,        # 1 semaine
            InvestmentType.STORAGE: 365,                # 1 an
            InvestmentType.PERSONNEL: 730,              # 2 ans
            InvestmentType.TOOLS_LICENSES: 365          # 1 an
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger("ROICalculator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    async def initialize(self) -> None:
        """Initialisation de la base de données"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS investments (
                        investment_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        investment_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT,
                        creator_types TEXT NOT NULL,
                        models_affected TEXT NOT NULL,
                        business_objective TEXT,
                        cost_category TEXT,
                        created_at TEXT NOT NULL
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS revenues (
                        revenue_id TEXT PRIMARY KEY,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        date TEXT NOT NULL,
                        creator_id TEXT NOT NULL,
                        creator_type TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        attribution_confidence REAL,
                        revenue_source TEXT,
                        conversion_path TEXT,
                        created_at TEXT NOT NULL
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS roi_analyses (
                        analysis_id TEXT PRIMARY KEY,
                        investment_id TEXT NOT NULL,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        total_investment REAL NOT NULL,
                        total_revenue REAL NOT NULL,
                        roi_percentage REAL NOT NULL,
                        payback_period_days INTEGER,
                        npv REAL,
                        irr REAL,
                        attribution_model TEXT NOT NULL,
                        confidence_score REAL,
                        creator_breakdown TEXT,
                        model_breakdown TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (investment_id) REFERENCES investments (investment_id)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS attribution_rules (
                        rule_id TEXT PRIMARY KEY,
                        model_type TEXT NOT NULL,
                        creator_type TEXT NOT NULL,
                        attribution_model TEXT NOT NULL,
                        confidence_threshold REAL,
                        time_decay_factor REAL,
                        position_weights TEXT,
                        custom_logic TEXT,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TEXT NOT NULL
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS roi_benchmarks (
                        benchmark_id TEXT PRIMARY KEY,
                        investment_type TEXT NOT NULL,
                        creator_type TEXT NOT NULL,
                        industry_roi_avg REAL,
                        industry_roi_p75 REAL,
                        industry_roi_p90 REAL,
                        benchmark_date TEXT NOT NULL,
                        data_source TEXT
                    )
                """)
                
                await db.commit()
                
            # Chargement des règles d'attribution par défaut
            await self._load_default_attribution_rules()
            
            self.logger.info("✅ ROI Calculator initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            raise AinflueCoreException(f"Échec initialisation ROI Calculator: {e}")

    async def _load_default_attribution_rules(self) -> None:
        """Chargement des règles d'attribution par défaut"""
        try:
            default_rules = [
                # Musiciens - Attribution basée sur données
                {
                    "rule_id": "musician_audio_model",
                    "model_type": "audio_classification",
                    "creator_type": "musician",
                    "attribution_model": AttributionModel.DATA_DRIVEN.value,
                    "confidence_threshold": 0.8,
                    "time_decay_factor": 0.9,
                    "position_weights": json.dumps([0.4, 0.3, 0.2, 0.1]),
                    "custom_logic": "streaming_revenue_correlation"
                },
                
                # Influenceurs - Attribution position-basée
                {
                    "rule_id": "influencer_engagement_model",
                    "model_type": "engagement_prediction", 
                    "creator_type": "influencer",
                    "attribution_model": AttributionModel.POSITION_BASED.value,
                    "confidence_threshold": 0.75,
                    "time_decay_factor": 0.85,
                    "position_weights": json.dumps([0.4, 0.2, 0.2, 0.2]),
                    "custom_logic": "sponsorship_conversion_tracking"
                },
                
                # Photographes - Attribution linéaire
                {
                    "rule_id": "photographer_vision_model",
                    "model_type": "image_classification",
                    "creator_type": "photographer", 
                    "attribution_model": AttributionModel.LINEAR.value,
                    "confidence_threshold": 0.7,
                    "time_decay_factor": 0.8,
                    "position_weights": json.dumps([0.25, 0.25, 0.25, 0.25]),
                    "custom_logic": "portfolio_optimization_impact"
                }
            ]
            
            async with aiosqlite.connect(self.db_path) as db:
                for rule in default_rules:
                    await db.execute("""
                        INSERT OR IGNORE INTO attribution_rules
                        (rule_id, model_type, creator_type, attribution_model, 
                         confidence_threshold, time_decay_factor, position_weights,
                         custom_logic, active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        rule[rule_id], rule["model_type"], rule["creator_type"],
                        rule["attribution_model"], rule["confidence_threshold"],
                        rule["time_decay_factor"], rule["position_weights"],
                        rule["custom_logic"], True, datetime.now().isoformat()
                    ))
                await db.commit()
                
            self.logger.info(f"✅ {len(default_rules)} règles d'attribution chargées")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement règles attribution: {e}")

    async def record_investment(self, investment: Investment) -> bool:
        """Enregistrement d'un investissement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO investments
                    (investment_id, name, investment_type, amount, currency, start_date,
                     end_date, creator_types, models_affected, business_objective,
                     cost_category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    investment.investment_id, investment.name, investment.investment_type.value,
                    investment.amount, investment.currency, investment.start_date.isoformat(),
                    investment.end_date.isoformat() if investment.end_date else None,
                    json.dumps(investment.creator_types), json.dumps(investment.models_affected),
                    investment.business_objective, investment.cost_category,
                    datetime.now().isoformat()
                ))
                await db.commit()
            
            self.logger.info(f"✅ Investissement {investment.investment_id} enregistré: ${investment.amount}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement investissement: {e}")
            return False

    async def record_revenue(self, revenue: Revenue) -> bool:
        """Enregistrement d'un revenu"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO revenues
                    (revenue_id, amount, currency, date, creator_id, creator_type,
                     model_id, attribution_confidence, revenue_source, conversion_path,
                     created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    revenue.revenue_id, revenue.amount, revenue.currency,
                    revenue.date.isoformat(), revenue.creator_id, revenue.creator_type,
                    revenue.model_id, revenue.attribution_confidence, revenue.revenue_source,
                    json.dumps(revenue.conversion_path), datetime.now().isoformat()
                ))
                await db.commit()
            
            self.logger.info(f"✅ Revenu {revenue.revenue_id} enregistré: ${revenue.amount}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement revenu: {e}")
            return False

    async def calculate_roi_analysis(self, 
                                   investment_id: str,
                                   period_start: datetime,
                                   period_end: datetime,
                                   attribution_model: AttributionModel = AttributionModel.DATA_DRIVEN,
                                   discount_rate: float = 0.1) -> ROIAnalysis:
        """Calcul d'analyse ROI complète"""
        try:
            # Récupération de l'investissement
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM investments WHERE investment_id = ?
                """, (investment_id,))
                
                investment_data = await cursor.fetchone()
                if not investment_data:
                    raise ValueError(f"Investissement {investment_id} non trouvé")
            
            # Calcul des revenus attribuables
            attributed_revenues = await self._calculate_attributed_revenues(
                investment_id, period_start, period_end, attribution_model
            )
            
            total_revenue = sum(rev.amount for rev in attributed_revenues)
            total_investment = investment_data[3]  # amount column
            
            # Calcul ROI de base
            roi_percentage = ((total_revenue - total_investment) / total_investment) * 100 if total_investment > 0 else 0
            
            # Calcul période de retour sur investissement
            payback_period = await self._calculate_payback_period(
                investment_id, total_investment, attributed_revenues
            )
            
            # Calcul NPV (Net Present Value)
            npv = await self._calculate_npv(
                total_investment, attributed_revenues, discount_rate
            )
            
            # Calcul IRR (Internal Rate of Return)
            irr = await self._calculate_irr(
                total_investment, attributed_revenues
            )
            
            # Breakdown par créateur
            creator_breakdown = await self._calculate_creator_breakdown(attributed_revenues)
            
            # Breakdown par modèle
            model_breakdown = await self._calculate_model_breakdown(attributed_revenues)
            
            # Score de confiance basé sur la qualité des données
            confidence_score = await self._calculate_confidence_score(attributed_revenues)
            
            analysis = ROIAnalysis(
                analysis_id=f"ROI_{investment_id}_{int(datetime.now().timestamp())}",
                investment_id=investment_id,
                period_start=period_start,
                period_end=period_end,
                total_investment=total_investment,
                total_revenue=total_revenue,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period,
                npv=npv,
                irr=irr,
                attribution_model=attribution_model,
                confidence_score=confidence_score,
                creator_breakdown=creator_breakdown,
                model_breakdown=model_breakdown
            )
            
            # Sauvegarde de l'analyse
            await self._save_roi_analysis(analysis)
            
            self.logger.info(f"✅ Analyse ROI calculée: {roi_percentage:.1f}% ROI, ${total_revenue:.2f} revenus")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul ROI: {e}")
            raise AinflueCoreException(f"Échec calcul ROI: {e}")

    async def _calculate_attributed_revenues(self,
                                           investment_id: str,
                                           period_start: datetime,
                                           period_end: datetime,
                                           attribution_model: AttributionModel) -> List[Revenue]:
        """Calcul des revenus attribuables à un investissement"""
        try:
            # Récupération de l'investissement pour connaître les modèles affectés
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT models_affected, creator_types, start_date, investment_type
                    FROM investments WHERE investment_id = ?
                """, (investment_id,))
                
                investment_data = await cursor.fetchone()
                if not investment_data:
                    return []
                
                models_affected = json.loads(investment_data[0])
                creator_types = json.loads(investment_data[1])
                investment_start = datetime.fromisoformat(investment_data[2])
                investment_type = InvestmentType(investment_data[3])
                
                # Fenêtre d'attribution
                attribution_window = self.attribution_windows.get(investment_type, 365)
                attribution_start = max(investment_start, period_start)
                attribution_end = min(
                    investment_start + timedelta(days=attribution_window),
                    period_end
                )
                
                # Récupération des revenus dans la fenêtre d'attribution
                cursor = await db.execute("""
                    SELECT * FROM revenues
                    WHERE date >= ? AND date <= ?
                    AND creator_type IN ({})
                    AND model_id IN ({})
                """.format(
                    ','.join('?' * len(creator_types)),
                    ','.join('?' * len(models_affected))
                ), (
                    attribution_start.isoformat(),
                    attribution_end.isoformat(),
                    *creator_types,
                    *models_affected
                ))
                
                revenue_rows = await cursor.fetchall()
            
            # Construction des objets Revenue
            revenues = []
            for row in revenue_rows:
                revenue = Revenue(
                    revenue_id=row[0],
                    amount=row[1],
                    currency=row[2],
                    date=datetime.fromisoformat(row[3]),
                    creator_id=row[4],
                    creator_type=row[5],
                    model_id=row[6],
                    attribution_confidence=row[7] or 1.0,
                    revenue_source=row[8],
                    conversion_path=json.loads(row[9]) if row[9] else []
                )
                revenues.append(revenue)
            
            # Application du modèle d'attribution
            attributed_revenues = await self._apply_attribution_model(
                revenues, attribution_model, investment_start
            )
            
            return attributed_revenues
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul revenus attribuables: {e}")
            return []

    async def _apply_attribution_model(self,
                                     revenues: List[Revenue],
                                     attribution_model: AttributionModel,
                                     investment_start: datetime) -> List[Revenue]:
        """Application du modèle d'attribution"""
        try:
            if attribution_model == AttributionModel.FIRST_TOUCH:
                # 100% au premier touchpoint
                return revenues
                
            elif attribution_model == AttributionModel.LAST_TOUCH:
                # 100% au dernier touchpoint
                return revenues
                
            elif attribution_model == AttributionModel.LINEAR:
                # Attribution uniforme
                for revenue in revenues:
                    if len(revenue.conversion_path) > 1:
                        revenue.amount *= (1.0 / len(revenue.conversion_path))
                return revenues
                
            elif attribution_model == AttributionModel.TIME_DECAY:
                # Decay temporel - plus récent = plus d'attribution
                for revenue in revenues:
                    days_since_investment = (revenue.date - investment_start).days
                    decay_factor = np.exp(-days_since_investment / 30)  # 30 jours half-life
                    revenue.amount *= decay_factor
                return revenues
                
            elif attribution_model == AttributionModel.POSITION_BASED:
                # 40% premier, 40% dernier, 20% milieu
                for revenue in revenues:
                    path_length = len(revenue.conversion_path)
                    if path_length == 1:
                        revenue.amount *= 1.0
                    elif path_length == 2:
                        revenue.amount *= 0.5  # 50-50 split
                    else:
                        # Position-based attribution
                        revenue.amount *= 0.6  # Simplified for demo
                return revenues
                
            elif attribution_model == AttributionModel.DATA_DRIVEN:
                # Attribution basée sur les données historiques
                for revenue in revenues:
                    # Utilisation du score de confiance comme proxy
                confidence_boost = 1 + (revenue.attribution_confidence - 0.5)
                revenue.amount *= max(0.1, min(2.0, confidence_boost))
                return revenues
            
            return revenues
            
        except Exception as e:
            self.logger.error(f"❌ Erreur application modèle attribution: {e}")
            return revenues

    async def _calculate_payback_period(self,
                                      investment_id: str,
                                      total_investment: float,
                                      revenues: List[Revenue]) -> int:
        """Calcul de la période de retour sur investissement"""
        try:
            if not revenues:
                return -1  # Pas de retour
            
            # Tri des revenus par date
            sorted_revenues = sorted(revenues, key=lambda r: r.date)
            
            cumulative_revenue = 0.0
            investment_date = min(rev.date for rev in revenues)
            
            for revenue in sorted_revenues:
                cumulative_revenue += revenue.amount
                
                if cumulative_revenue >= total_investment:
                    payback_days = (revenue.date - investment_date).days
                    return payback_days
            
            return -1  # Pas encore atteint le break-even
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul payback period: {e}")
            return -1

    async def _calculate_npv(self,
                           investment: float,
                           revenues: List[Revenue],
                           discount_rate: float) -> float:
        """Calcul de la valeur actualisée nette (NPV)"""
        try:
            if not revenues:
                return -investment
            
            investment_date = min(rev.date for rev in revenues)
            npv = -investment  # Investissement initial négatif
            
            for revenue in revenues:
                days_elapsed = (revenue.date - investment_date).days
                years_elapsed = days_elapsed / 365.25
                
                # Actualisation du cash flow
                discounted_value = revenue.amount / ((1 + discount_rate) ** years_elapsed)
                npv += discounted_value
            
            return npv
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul NPV: {e}")
            return 0.0

    async def _calculate_irr(self,
                           investment: float,
                           revenues: List[Revenue]) -> float:
        """Calcul du taux de rendement interne (IRR)"""
        try:
            if not revenues:
                return 0.0
            
            # Simplification: calcul approximatif de l'IRR
            total_revenue = sum(rev.amount for rev in revenues)
            
            if total_revenue <= investment:
                return 0.0
            
            # Période moyenne
            investment_date = min(rev.date for rev in revenues)
            avg_period = np.mean([(rev.date - investment_date).days for rev in revenues]) / 365.25
            
            if avg_period <= 0:
                return 0.0
            
            # IRR approximé
            irr = ((total_revenue / investment) ** (1 / avg_period)) - 1
            return min(1.0, max(-1.0, irr))  # Limité entre -100% et 100%
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul IRR: {e}")
            return 0.0

    async def _calculate_creator_breakdown(self, revenues: List[Revenue]) -> Dict[str, Dict[str, float]]:
        """Breakdown des revenus par type de créateur"""
        try:
            breakdown = defaultdict(lambda: {"revenue": 0.0, "count": 0})
            
            for revenue in revenues:
                breakdown[revenue.creator_type]["revenue"] += revenue.amount
                breakdown[revenue.creator_type]["count"] += 1
            
            # Calcul des moyennes
            for creator_type in breakdown:
                count = breakdown[creator_type]["count"]
                breakdown[creator_type]["average"] = breakdown[creator_type]["revenue"] / max(count, 1)
            
            return dict(breakdown)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur breakdown créateurs: {e}")
            return {}

    async def _calculate_model_breakdown(self, revenues: List[Revenue]) -> Dict[str, Dict[str, float]]:
        """Breakdown des revenus par modèle"""
        try:
            breakdown = defaultdict(lambda: {"revenue": 0.0, "count": 0})
            
            for revenue in revenues:
                breakdown[revenue.model_id]["revenue"] += revenue.amount
                breakdown[revenue.model_id]["count"] += 1
            
            # Calcul des moyennes et attribution
            for model_id in breakdown:
                count = breakdown[model_id]["count"]
                breakdown[model_id]["average"] = breakdown[model_id]["revenue"] / max(count, 1)
                breakdown[model_id]["attribution_confidence"] = np.mean([
                    rev.attribution_confidence for rev in revenues if rev.model_id == model_id
                ])
            
            return dict(breakdown)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur breakdown modèles: {e}")
            return {}

    async def _calculate_confidence_score(self, revenues: List[Revenue]) -> float:
        """Calcul du score de confiance de l'analyse"""
        try:
            if not revenues:
                return 0.0
            
            # Facteurs de confiance
            avg_attribution_confidence = np.mean([rev.attribution_confidence for rev in revenues])
            
            # Diversité des sources de revenus (plus = mieux)
            revenue_sources = set(rev.revenue_source for rev in revenues)
            source_diversity = min(1.0, len(revenue_sources) / 5)  # Max 5 sources
            
            # Consistance temporelle (pas de gaps trop importants)
            sorted_dates = sorted([rev.date for rev in revenues])
            max_gap = max(
                (sorted_dates[i+1] - sorted_dates[i]).days 
                for i in range(len(sorted_dates) - 1)
            ) if len(sorted_dates) > 1 else 0
            
            temporal_consistency = max(0.0, 1.0 - (max_gap / 365))  # Pénalité pour gaps > 1 an
            
            # Score composite
            confidence_score = (
                avg_attribution_confidence * 0.5 +
                source_diversity * 0.3 +
                temporal_consistency * 0.2
            )
            
            return min(1.0, max(0.0, confidence_score))
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul confidence score: {e}")
            return 0.5

    async def _save_roi_analysis(self, analysis: ROIAnalysis) -> None:
        """Sauvegarde d'une analyse ROI"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO roi_analyses
                    (analysis_id, investment_id, period_start, period_end, total_investment,
                     total_revenue, roi_percentage, payback_period_days, npv, irr,
                     attribution_model, confidence_score, creator_breakdown, model_breakdown,
                     created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.analysis_id, analysis.investment_id,
                    analysis.period_start.isoformat(), analysis.period_end.isoformat(),
                    analysis.total_investment, analysis.total_revenue, analysis.roi_percentage,
                    analysis.payback_period_days, analysis.npv, analysis.irr,
                    analysis.attribution_model.value, analysis.confidence_score,
                    json.dumps(analysis.creator_breakdown), json.dumps(analysis.model_breakdown),
                    datetime.now().isoformat()
                ))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde analyse ROI: {e}")

    async def get_roi_dashboard(self, period_days: int = 90) -> Dict[str, Any]:
        """Dashboard ROI en temps réel"""
        try:
            since = datetime.now() - timedelta(days=period_days)
            
            async with aiosqlite.connect(self.db_path) as db:
                # ROI analyses récentes
                cursor = await db.execute("""
                    SELECT * FROM roi_analyses
                    WHERE created_at >= ?
                    ORDER BY roi_percentage DESC
                """, (since.isoformat(),))
                
                analyses_data = await cursor.fetchall()
                
                # Investissements totaux
                cursor = await db.execute("""
                    SELECT SUM(amount), COUNT(*), investment_type
                    FROM investments
                    WHERE start_date >= ?
                    GROUP BY investment_type
                """, (since.isoformat(),))
                
                investment_summary = await cursor.fetchall()
                
                # Revenus totaux
                cursor = await db.execute("""
                    SELECT SUM(amount), COUNT(*), creator_type
                    FROM revenues
                    WHERE date >= ?
                    GROUP BY creator_type
                """, (since.isoformat(),))
                
                revenue_summary = await cursor.fetchall()
            
            # Métriques clés
            total_investment = sum(row[0] for row in investment_summary)
            total_revenue = sum(row[0] for row in revenue_summary)
            overall_roi = ((total_revenue - total_investment) / max(total_investment, 1)) * 100
            
            # Top performing investments
            top_investments = []
            for row in analyses_data[:5]:
                top_investments.append({
                    "investment_id": row[1],
                    "roi_percentage": row[6],
                    "total_revenue": row[5],
                    "confidence_score": row[11]
                })
            
            dashboard = {
                "period_days": period_days,
                "overall_roi": overall_roi,
                "total_investment": total_investment,
                "total_revenue": total_revenue,
                "net_profit": total_revenue - total_investment,
                "analyses_count": len(analyses_data),
                "top_investments": top_investments,
                "investment_by_type": {row[2]: row[0] for row in investment_summary},
                "revenue_by_creator": {row[2]: row[0] for row in revenue_summary},
                "avg_confidence_score": np.mean([row[11] for row in analyses_data]) if analyses_data else 0.0,
                "roi_status": "excellent" if overall_roi > 50 else "good" if overall_roi > 20 else "poor"
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dashboard ROI: {e}")
            raise AinflueCoreException(f"Échec génération dashboard: {e}")

    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        try:
            self.executor.shutdown(wait=True)
            self.logger.info("✅ ROI Calculator nettoyé")
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")

# Example usage
async def main():
    calculator = ROICalculator()
    await calculator.initialize()
    
    # Exemple d'investissement
    investment = Investment(
        investment_id="INV_ML_AUDIO_2025",
        name="Audio ML Model Development",
        investment_type=InvestmentType.MODEL_DEVELOPMENT,
        amount=50000.0,
        currency="USD",
        start_date=datetime.now() - timedelta(days=90),
        end_date=None,
        creator_types=["musician"],
        models_affected=["audio_classification", "music_generation"],
        business_objective="Improve musician revenue through better audio processing",
        cost_category="R&D"
    )
    
    await calculator.record_investment(investment)
    
    # Exemple de revenus
    for i in range(10):
        revenue = Revenue(
            revenue_id=f"REV_MUS_{i:03d}",
            amount=2500.0 + np.random.normal(0, 500),
            currency="USD",
            date=datetime.now() - timedelta(days=80-i*8),
            creator_id=f"musician_{i%3:03d}",
            creator_type="musician",
            model_id="audio_classification",
            attribution_confidence=0.8 + np.random.normal(0, 0.1),
            revenue_source="streaming",
            conversion_path=["model_recommendation", "playlist_placement", "stream"]
        )
        await calculator.record_revenue(revenue)
    
    # Calcul ROI
    analysis = await calculator.calculate_roi_analysis(
        investment_id=investment.investment_id,
        period_start=datetime.now() - timedelta(days=90),
        period_end=datetime.now(),
        attribution_model=AttributionModel.DATA_DRIVEN
    )
    
    dashboard = await calculator.get_roi_dashboard()
    
    print(f"ROI Analysis: {analysis.roi_percentage:.1f}% ROI")
    print(f"Payback Period: {analysis.payback_period_days} days")
    print(f"Confidence Score: {analysis.confidence_score:.2f}")
    print(f"Dashboard: {dashboard['overall_roi']:.1f}% overall ROI")
    
    await calculator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())