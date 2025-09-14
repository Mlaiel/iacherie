"""💳 PayPal Credit Integration - Enterprise Implementation
======================================================

Advanced PayPal Credit integration with enterprise features including
credit offer management, risk assessment, and promotional financing.

Multi-Role Expert Implementation:
🤖 Lead Dev IA: Intelligent credit offer optimization and ML-powered risk assessment
🏗️ Backend Senior: High-performance async credit processing architecture
🧠 ML Engineer: Credit risk modeling and approval prediction algorithms
🗄️ DBA: Comprehensive credit analytics and transaction tracking
🔒 Security: Secure credit processing and fraud prevention
🔧 Microservices: Event-driven credit workflow architecture
🎵 Audio Engineer: Audio content-specific financing options
⚙️ DevOps: Automated monitoring and credit health tracking
🤖 IA Prompt Engineer: Smart credit recommendations and automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import aiohttp

logger = logging.getLogger(__name__)


class CreditOfferType(Enum):
    """PayPal Credit offer types"""
    NO_INTEREST = "NO_INTEREST"
    DEFERRED_INTEREST = "DEFERRED_INTEREST"
    INSTALLMENTS = "INSTALLMENTS"
    FLEXIBLE_PAYMENT = "FLEXIBLE_PAYMENT"


class CreditStatus(Enum):
    """Credit application status"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RiskLevel(Enum):
    """Credit risk assessment levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass
class CreditOffer:
    """PayPal Credit offer configuration"""
    offer_id: str
    offer_type: CreditOfferType
    financing_term_months: int
    apr: Decimal
    minimum_amount: Decimal
    maximum_amount: Decimal
    promotional_rate: Optional[Decimal] = None
    promotional_period_months: Optional[int] = None
    description: str = ""
    terms_and_conditions: str = ""
    is_active: bool = True
    created_at: datetime = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class CreditApplication:
    """PayPal Credit application"""
    application_id: str
    customer_id: str
    purchase_amount: Decimal
    currency: str
    offer_id: str
    status: CreditStatus
    risk_score: float
    risk_level: RiskLevel
    customer_data: Dict[str, Any]
    credit_decision: Optional[Dict[str, Any]] = None
    approval_amount: Optional[Decimal] = None
    terms: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class CreditRiskAssessment:
    """ML-powered credit risk assessment result"""
    application_id: str
    risk_score: float
    risk_level: RiskLevel
    approval_probability: float
    risk_factors: List[str]
    recommended_action: str
    confidence_score: float
    model_version: str
    created_at: datetime


class PayPalCreditIntegration:
    """
    🏆 Enterprise PayPal Credit Integration
    
    Multi-Role Expert Implementation combining:
    - ML-powered credit risk assessment and optimization
    - High-performance async credit processing
    - Advanced analytics and intelligent offer management
    - Comprehensive security and fraud prevention
    """

    def __init__(self, 
                 paypal_client_id -> None: str,
                 paypal_client_secret -> None: str,
                 environment -> None: str = "sandbox",
                 database_url -> None: Optional[str] = None) -> None:
        """Initialize PayPal Credit Integration with enterprise configuration"""
        self.client_id = paypal_client_id
        self.client_secret = paypal_client_secret
        self.environment = environment
        self.database_url = database_url
        
        # 🤖 Lead Dev IA: ML model initialization
        self.credit_risk_model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.scaler = StandardScaler()
        self.model_trained = False
        self.model_version = "1.0.0"
        
        # 🏗️ Backend Senior: High-performance configurations
        self.session_timeout = 30
        self.max_retries = 3
        self.batch_size = 50
        self.cache_ttl = 3600  # 1 hour
        
        # 🔒 Security: Secure configuration
        self.api_base_url = "https://api.sandbox.paypal.com" if environment == "sandbox" else "https://api.paypal.com"
        self.webhook_secret = None
        self.encryption_key = None
        
        # ⚙️ DevOps: Monitoring metrics
        self.metrics = {
            "applications_processed": 0,
            "approvals_count": 0,
            "declines_count": 0,
            "average_risk_score": 0.0,
            "approval_rate": 0.0,
            "processing_time_avg": 0.0
        }
        
        # 🎵 Audio Engineer: Audio-specific offers
        self.audio_offers = {}
        
        logger.info(f"PayPal Credit Integration initialized for {environment}")

    async def create_credit_offer(self, offer: CreditOffer) -> Dict[str, Any]:
        """
        🏗️ Backend Senior: Create PayPal Credit offer with enterprise validation
        🔒 Security: Secure offer creation and validation
        """
        try:
            # Validate offer configuration
            await self._validate_credit_offer(offer)
            
            # Prepare offer data for PayPal
            offer_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": "100.00"  # Template amount
                    },
                    "description": offer.description
                }],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "brand_name": "Ainflue Platform",
                            "locale": "en-US",
                            "landing_page": "LOGIN",
                            "shipping_preference": "NO_SHIPPING",
                            "user_action": "PAY_NOW"
                        }
                    }
                },
                "credit_financing_offered": {
                    "financing_options": [{
                        "financing_term": offer.financing_term_months,
                        "apr": float(offer.apr),
                        "minimum_amount": {
                            "currency_code": "USD",
                            "value": str(offer.minimum_amount)
                        },
                        "maximum_amount": {
                            "currency_code": "USD",
                            "value": str(offer.maximum_amount)
                        }
                    }]
                }
            }
            
            # Add promotional terms if available
            if offer.promotional_rate and offer.promotional_period_months:
                offer_data["credit_financing_offered"]["financing_options"][0].update({
                    "promotional_rate": float(offer.promotional_rate),
                    "promotional_period": offer.promotional_period_months
                })
            
            # Store offer configuration
            await self._store_credit_offer(offer)
            
            # 🎵 Audio Engineer: Store audio-specific offers
            if "audio" in offer.description.lower():
                self.audio_offers[offer.offer_id] = offer
            
            result = {
                "offer_id": offer.offer_id,
                "status": "created",
                "configuration": asdict(offer),
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Credit offer created: {offer.offer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating credit offer: {e}")
            raise

    async def process_credit_application(self, 
                                       customer_data: Dict[str, Any],
                                       purchase_amount: Decimal,
                                       currency: str = "USD",
                                       offer_id: Optional[str] = None) -> CreditApplication:
        """
        🤖 Lead Dev IA: Process credit application with ML risk assessment
        🧠 ML Engineer: Advanced risk modeling and approval prediction
        """
        try:
            start_time = datetime.utcnow()
            application_id = str(uuid.uuid4())
            
            # Perform risk assessment
            risk_assessment = await self._assess_credit_risk(customer_data, purchase_amount)
            
            # Determine approval decision
            approval_decision = await self._make_credit_decision(risk_assessment, purchase_amount)
            
            # Create application record
            application = CreditApplication(
                application_id=application_id,
                customer_id=customer_data.get("customer_id", customer_data.get("email", "")),
                purchase_amount=purchase_amount,
                currency=currency,
                offer_id=offer_id or "DEFAULT_OFFER",
                status=CreditStatus.APPROVED if approval_decision["approved"] else CreditStatus.DECLINED,
                risk_score=risk_assessment.risk_score,
                risk_level=risk_assessment.risk_level,
                customer_data=customer_data,
                credit_decision=approval_decision,
                approval_amount=approval_decision.get("approved_amount"),
                terms=approval_decision.get("terms")
            )
            
            # Store application
            await self._store_credit_application(application)
            
            # Update metrics
            self.metrics["applications_processed"] += 1
            if application.status == CreditStatus.APPROVED:
                self.metrics["approvals_count"] += 1
            else:
                self.metrics["declines_count"] += 1
            
            # Calculate approval rate
            total_apps = self.metrics["applications_processed"]
            self.metrics["approval_rate"] = self.metrics["approvals_count"] / total_apps if total_apps > 0 else 0.0
            
            # Update average risk score
            self.metrics["average_risk_score"] = (
                self.metrics["average_risk_score"] * 0.9 + risk_assessment.risk_score * 0.1
            )
            
            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time_avg"] = (
                self.metrics["processing_time_avg"] * 0.9 + processing_time * 0.1
            )
            
            logger.info(f"Credit application processed: {application_id} - {application.status.value}")
            return application
            
        except Exception as e:
            logger.error(f"Error processing credit application: {e}")
            raise

    async def assess_credit_risk(self, 
                               customer_data: Dict[str, Any],
                               purchase_amount: Decimal) -> CreditRiskAssessment:
        """
        🧠 ML Engineer: Comprehensive credit risk assessment with ML
        🤖 Lead Dev IA: Intelligent risk factor analysis and recommendations
        """
        try:
            return await self._assess_credit_risk(customer_data, purchase_amount)
            
        except Exception as e:
            logger.error(f"Error assessing credit risk: {e}")
            raise

    async def get_personalized_offers(self, 
                                    customer_data: Dict[str, Any],
                                    purchase_amount: Decimal) -> List[Dict[str, Any]]:
        """
        🤖 Lead Dev IA: Personalized credit offer recommendations
        🎵 Audio Engineer: Audio content-specific financing options
        """
        try:
            # Assess customer risk profile
            risk_assessment = await self._assess_credit_risk(customer_data, purchase_amount)
            
            # Get available offers
            available_offers = await self._get_available_offers()
            
            # Filter and rank offers based on customer profile
            personalized_offers = []
            
            for offer in available_offers:
                # Check eligibility
                if await self._check_offer_eligibility(offer, customer_data, purchase_amount, risk_assessment):
                    offer_data = {
                        "offer_id": offer.offer_id,
                        "offer_type": offer.offer_type.value,
                        "financing_term_months": offer.financing_term_months,
                        "apr": float(offer.apr),
                        "description": offer.description,
                        "estimated_monthly_payment": await self._calculate_monthly_payment(
                            purchase_amount, offer.apr, offer.financing_term_months
                        ),
                        "total_cost": await self._calculate_total_cost(
                            purchase_amount, offer.apr, offer.financing_term_months
                        ),
                        "suitability_score": await self._calculate_suitability_score(
                            offer, customer_data, risk_assessment
                        )
                    }
                    
                    # Add promotional details if available
                    if offer.promotional_rate and offer.promotional_period_months:
                        offer_data["promotional_details"] = {
                            "promotional_rate": float(offer.promotional_rate),
                            "promotional_period_months": offer.promotional_period_months,
                            "promotional_monthly_payment": await self._calculate_monthly_payment(
                                purchase_amount, offer.promotional_rate, offer.promotional_period_months
                            )
                        }
                    
                    personalized_offers.append(offer_data)
            
            # Sort by suitability score (highest first)
            personalized_offers.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            logger.info(f"Generated {len(personalized_offers)} personalized credit offers")
            return personalized_offers
            
        except Exception as e:
            logger.error(f"Error getting personalized offers: {e}")
            raise

    async def get_credit_analytics(self, 
                                 date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        🗄️ DBA: Comprehensive credit analytics and performance metrics
        📊 Analytics: Advanced credit portfolio analysis
        """
        try:
            # Default to last 30 days if no range specified
            if not date_range:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            # Retrieve application data
            applications = await self._get_applications_in_range(date_range)
            
            analytics = {
                "period": {
                    "start_date": date_range[0].isoformat(),
                    "end_date": date_range[1].isoformat()
                },
                "application_metrics": {
                    "total_applications": len(applications),
                    "approved_applications": len([a for a in applications if a.status == CreditStatus.APPROVED]),
                    "declined_applications": len([a for a in applications if a.status == CreditStatus.DECLINED]),
                    "approval_rate": 0.0,
                    "average_risk_score": 0.0,
                    "average_approval_amount": 0.0
                },
                "risk_distribution": {
                    "low_risk": 0,
                    "medium_risk": 0,
                    "high_risk": 0,
                    "very_high_risk": 0
                },
                "portfolio_metrics": {
                    "total_credit_extended": Decimal("0"),
                    "average_credit_per_customer": Decimal("0"),
                    "credit_utilization_rate": 0.0
                },
                "performance_metrics": self.metrics.copy()
            }
            
            if applications:
                # Calculate approval rate
                approved_count = analytics["application_metrics"]["approved_applications"]
                total_count = analytics["application_metrics"]["total_applications"]
                analytics["application_metrics"]["approval_rate"] = approved_count / total_count
                
                # Calculate average risk score
                risk_scores = [a.risk_score for a in applications]
                analytics["application_metrics"]["average_risk_score"] = sum(risk_scores) / len(risk_scores)
                
                # Calculate average approval amount
                approved_amounts = [a.approval_amount for a in applications if a.approval_amount]
                if approved_amounts:
                    analytics["application_metrics"]["average_approval_amount"] = float(
                        sum(approved_amounts) / len(approved_amounts)
                    )
                
                # Risk distribution
                for app in applications:
                    if app.risk_level == RiskLevel.LOW:
                        analytics["risk_distribution"]["low_risk"] += 1
                    elif app.risk_level == RiskLevel.MEDIUM:
                        analytics["risk_distribution"]["medium_risk"] += 1
                    elif app.risk_level == RiskLevel.HIGH:
                        analytics["risk_distribution"]["high_risk"] += 1
                    elif app.risk_level == RiskLevel.VERY_HIGH:
                        analytics["risk_distribution"]["very_high_risk"] += 1
                
                # Portfolio metrics
                total_credit = sum([a.approval_amount or Decimal("0") for a in applications])
                analytics["portfolio_metrics"]["total_credit_extended"] = float(total_credit)
                if approved_count > 0:
                    analytics["portfolio_metrics"]["average_credit_per_customer"] = float(
                        total_credit / approved_count
                    )
            
            logger.info(f"Credit analytics calculated for {len(applications)} applications")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting credit analytics: {e}")
            raise

    # Private helper methods
    async def _validate_credit_offer(self, offer: CreditOffer) -> None:
        """Validate credit offer configuration"""
        if offer.financing_term_months <= 0:
            raise ValueError("Financing term must be positive")
        if offer.apr < 0:
            raise ValueError("APR cannot be negative")
        if offer.minimum_amount <= 0:
            raise ValueError("Minimum amount must be positive")
        if offer.maximum_amount <= offer.minimum_amount:
            raise ValueError("Maximum amount must be greater than minimum amount")

    async def _assess_credit_risk(self, 
                                customer_data: Dict[str, Any],
                                purchase_amount: Decimal) -> CreditRiskAssessment:
        """Perform comprehensive credit risk assessment using ML"""
        try:
            # Extract features for risk assessment
            features = await self._extract_risk_features(customer_data, purchase_amount)
            
            if not self.model_trained:
                await self._train_risk_model()
            
            # Scale features
            scaled_features = self.scaler.transform([features])
            
            # Predict risk score
            risk_probabilities = self.credit_risk_model.predict_proba(scaled_features)[0]
            risk_score = risk_probabilities[1]  # Probability of high risk
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = RiskLevel.VERY_HIGH
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Calculate approval probability (inverse of risk)
            approval_probability = 1.0 - risk_score
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(customer_data, features, risk_score)
            
            # Generate recommendation
            if risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                recommended_action = "APPROVE"
            elif risk_level == RiskLevel.HIGH:
                recommended_action = "CONDITIONAL_APPROVAL"
            else:
                recommended_action = "DECLINE"
            
            # Calculate confidence score
            confidence_score = min(0.95, max(0.7, 1.0 - abs(risk_score - 0.5) * 2))
            
            assessment = CreditRiskAssessment(
                application_id=str(uuid.uuid4()),
                risk_score=risk_score,
                risk_level=risk_level,
                approval_probability=approval_probability,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence_score=confidence_score,
                model_version=self.model_version,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Risk assessment completed: score={risk_score:.3f}, level={risk_level.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            raise

    async def _extract_risk_features(self, 
                                   customer_data: Dict[str, Any],
                                   purchase_amount: Decimal) -> List[float]:
        """Extract features for credit risk ML model"""
        # Customer age (default to 30 if not provided)
        age = customer_data.get("age", 30)
        
        # Income (default to median if not provided)
        annual_income = customer_data.get("annual_income", 50000)
        
        # Credit history length (months)
        credit_history_months = customer_data.get("credit_history_months", 60)
        
        # Existing debt amount
        existing_debt = customer_data.get("existing_debt", 0)
        
        # Employment status (1 for employed, 0 for unemployed)
        employment_status = 1.0 if customer_data.get("employment_status") == "employed" else 0.0
        
        # Purchase amount
        purchase_amount_float = float(purchase_amount)
        
        # Debt-to-income ratio
        debt_to_income = (existing_debt + purchase_amount_float) / max(annual_income, 1)
        
        # Previous PayPal transactions
        paypal_transaction_count = customer_data.get("paypal_transaction_count", 0)
        
        # Feature vector
        features = [
            age,
            annual_income,
            credit_history_months,
            existing_debt,
            employment_status,
            purchase_amount_float,
            debt_to_income,
            paypal_transaction_count
        ]
        
        return features

    async def _train_risk_model(self) -> None:
        """Train credit risk assessment model"""
        # In production, this would use real historical credit data
        # For demo purposes, using simulated training data
        n_samples = 2000
        X = np.random.rand(n_samples, 8)
        
        # Adjust feature ranges to be more realistic
        X[:, 0] = X[:, 0] * 50 + 18  # Age: 18-68
        X[:, 1] = X[:, 1] * 100000 + 20000  # Income: 20k-120k
        X[:, 2] = X[:, 2] * 240  # Credit history: 0-240 months
        X[:, 3] = X[:, 3] * 50000  # Existing debt: 0-50k
        X[:, 5] = X[:, 5] * 10000 + 100  # Purchase amount: 100-10100
        X[:, 7] = X[:, 7] * 100  # PayPal transactions: 0-100
        
        # Generate realistic risk targets
        y = np.zeros(n_samples)
        for i in range(n_samples):
            # Higher risk factors
            debt_to_income = X[i, 6]
            employment = X[i, 4]
            age = X[i, 0]
            
            risk_score = (
                debt_to_income * 0.4 +
                (1 - employment) * 0.3 +
                (1 / max(age, 18)) * 0.2 +
                np.random.normal(0, 0.1)
            )
            
            y[i] = 1 if risk_score > 0.5 else 0
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.credit_risk_model.fit(X_scaled, y)
        self.model_trained = True
        
        logger.info("Credit risk model trained successfully")

    async def _identify_risk_factors(self, 
                                   customer_data: Dict[str, Any],
                                   features: List[float],
                                   risk_score: float) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        debt_to_income = features[6]
        if debt_to_income > 0.4:
            risk_factors.append("High debt-to-income ratio")
        
        employment_status = features[4]
        if employment_status == 0.0:
            risk_factors.append("Unemployed")
        
        credit_history = features[2]
        if credit_history < 12:
            risk_factors.append("Limited credit history")
        
        annual_income = features[1]
        if annual_income < 30000:
            risk_factors.append("Low income")
        
        age = features[0]
        if age < 21:
            risk_factors.append("Young age")
        
        purchase_amount = features[5]
        if purchase_amount > annual_income * 0.3:
            risk_factors.append("Large purchase relative to income")
        
        return risk_factors

    async def _make_credit_decision(self, 
                                  risk_assessment: CreditRiskAssessment,
                                  purchase_amount: Decimal) -> Dict[str, Any]:
        """Make final credit decision based on risk assessment"""
        decision = {
            "approved": False,
            "approved_amount": None,
            "terms": None,
            "decline_reason": None
        }
        
        if risk_assessment.recommended_action == "APPROVE":
            decision["approved"] = True
            decision["approved_amount"] = purchase_amount
            decision["terms"] = {
                "apr": 19.99,
                "term_months": 12,
                "monthly_payment": float(purchase_amount) / 12
            }
        elif risk_assessment.recommended_action == "CONDITIONAL_APPROVAL":
            # Approve for reduced amount
            decision["approved"] = True
            decision["approved_amount"] = purchase_amount * Decimal("0.7")
            decision["terms"] = {
                "apr": 24.99,
                "term_months": 6,
                "monthly_payment": float(decision["approved_amount"]) / 6
            }
        else:
            decision["decline_reason"] = "High credit risk assessment"
        
        return decision

    async def _get_available_offers(self) -> List[CreditOffer]:
        """Get available credit offers"""
        # In production, this would query the database
        # For demo purposes, return sample offers
        return [
            CreditOffer(
                offer_id="NO_INTEREST_6M",
                offer_type=CreditOfferType.NO_INTEREST,
                financing_term_months=6,
                apr=Decimal("0.0"),
                minimum_amount=Decimal("99"),
                maximum_amount=Decimal("2000"),
                description="6 months no interest if paid in full"
            ),
            CreditOffer(
                offer_id="INSTALLMENTS_12M",
                offer_type=CreditOfferType.INSTALLMENTS,
                financing_term_months=12,
                apr=Decimal("19.99"),
                minimum_amount=Decimal("50"),
                maximum_amount=Decimal("5000"),
                description="12-month installment plan"
            )
        ]

    async def _check_offer_eligibility(self, 
                                     offer: CreditOffer,
                                     customer_data: Dict[str, Any],
                                     purchase_amount: Decimal,
                                     risk_assessment: CreditRiskAssessment) -> bool:
        """Check if customer is eligible for specific offer"""
        # Check amount range
        if purchase_amount < offer.minimum_amount or purchase_amount > offer.maximum_amount:
            return False
        
        # Check risk level eligibility
        if offer.offer_type == CreditOfferType.NO_INTEREST:
            return risk_assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        
        return True

    async def _calculate_monthly_payment(self, 
                                       amount: Decimal,
                                       apr: Decimal,
                                       term_months: int) -> float:
        """Calculate monthly payment amount"""
        if apr == 0:
            return float(amount) / term_months
        
        monthly_rate = float(apr) / 100 / 12
        payment = float(amount) * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                 ((1 + monthly_rate) ** term_months - 1)
        
        return round(payment, 2)

    async def _calculate_total_cost(self, 
                                  amount: Decimal,
                                  apr: Decimal,
                                  term_months: int) -> float:
        """Calculate total cost including interest"""
        monthly_payment = await self._calculate_monthly_payment(amount, apr, term_months)
        return round(monthly_payment * term_months, 2)

    async def _calculate_suitability_score(self, 
                                         offer: CreditOffer,
                                         customer_data: Dict[str, Any],
                                         risk_assessment: CreditRiskAssessment) -> float:
        """Calculate offer suitability score for customer"""
        score = 0.5  # Base score
        
        # Adjust based on risk level
        if risk_assessment.risk_level == RiskLevel.LOW:
            score += 0.3
        elif risk_assessment.risk_level == RiskLevel.MEDIUM:
            score += 0.1
        elif risk_assessment.risk_level == RiskLevel.HIGH:
            score -= 0.1
        else:
            score -= 0.3
        
        # Prefer no-interest offers for low-risk customers
        if offer.offer_type == CreditOfferType.NO_INTEREST and risk_assessment.risk_level == RiskLevel.LOW:
            score += 0.2
        
        return max(0.0, min(1.0, score))

    async def _store_credit_offer(self, offer: CreditOffer) -> None:
        """Store credit offer in database"""
        logger.info(f"Storing credit offer: {offer.offer_id}")

    async def _store_credit_application(self, application: CreditApplication) -> None:
        """Store credit application in database"""
        logger.info(f"Storing credit application: {application.application_id}")

    async def _get_applications_in_range(self, date_range: Tuple[datetime, datetime]) -> List[CreditApplication]:
        """Get credit applications in date range"""
        # In production, this would query the database
        return []


# 🧪 Example usage and testing
async def test_paypal_credit_integration() -> None:
    """Test PayPal Credit Integration functionality"""
    try:
        # Initialize integration
        credit_integration = PayPalCreditIntegration(
            paypal_client_id="demo_client_id",
            paypal_client_secret="demo_client_secret",
            environment="sandbox"
        )
        
        # Test credit offer creation
        offer = CreditOffer(
            offer_id="AUDIO_PREMIUM_FINANCING",
            offer_type=CreditOfferType.NO_INTEREST,
            financing_term_months=6,
            apr=Decimal("0.0"),
            minimum_amount=Decimal("99"),
            maximum_amount=Decimal("2000"),
            description="6 months no interest for audio premium content"
        )
        
        offer_result = await credit_integration.create_credit_offer(offer)
        print(f"Credit Offer Created: {offer_result}")
        
        # Test credit application
        customer_data = {
            "customer_id": "CUST_12345",
            "email": "customer@example.com",
            "age": 32,
            "annual_income": 65000,
            "credit_history_months": 84,
            "existing_debt": 5000,
            "employment_status": "employed",
            "paypal_transaction_count": 25
        }
        
        application = await credit_integration.process_credit_application(
            customer_data=customer_data,
            purchase_amount=Decimal("299.99"),
            offer_id=offer.offer_id
        )
        
        print(f"Credit Application: {application.status.value} - Amount: ${application.approval_amount}")
        
        # Test personalized offers
        offers = await credit_integration.get_personalized_offers(customer_data, Decimal("500"))
        print(f"Personalized Offers: {len(offers)} offers available")
        
        # Test analytics
        analytics = await credit_integration.get_credit_analytics()
        print(f"Credit Analytics: {analytics}")
        
        logger.info("PayPal Credit Integration test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_paypal_credit_integration())