"""Creator Accounts Database Models and Operations

Gestion complète des comptes créateurs avec multi-format support
(musiciens, blogueurs, photographes, influenceurs, comédiens).

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Database Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum as PyEnum
import logging
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()


class CreatorType(PyEnum):
    """Types de créateurs supportés par la plateforme."""
    MUSICIAN = "musician"
    BLOGGER = "blogger" 
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    PRODUCER = "producer"


class CreatorStatus(PyEnum):
    """Statuts possibles des comptes créateurs."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class VerificationLevel(PyEnum):
    """Niveaux de vérification des créateurs."""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    IDENTITY_VERIFIED = "identity_verified"
    PROFESSIONAL_VERIFIED = "professional_verified"


class CreatorAccount(Base):
    """
    Modèle principal pour les comptes créateurs avec support multi-format.
    Intègre la logique métier : Upload → IA Protection → SEO → Collaboration → Distribution.
    """
    __tablename__ = "creator_accounts"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    creator_uuid = Column(String, unique=True, nullable=False)
    
    # Informations de base
    creator_type = Column(Enum(CreatorType), nullable=False)
    stage_name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    bio = Column(Text)
    
    # Statut et vérification
    status = Column(Enum(CreatorStatus), default=CreatorStatus.PENDING)
    verification_level = Column(Enum(VerificationLevel), default=VerificationLevel.UNVERIFIED)
    verified_at = Column(DateTime)
    verification_badge = Column(Boolean, default=False)
    
    # Géolocalisation et marché
    country_code = Column(String(3))
    primary_language = Column(String(10))
    timezone = Column(String(50))
    market_regions = Column(JSON)  # ["US", "EU", "ASIA"]
    
    # Métriques de performance
    total_uploads = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    total_revenue = Column(Decimal(12, 2), default=0.00)
    engagement_score = Column(Decimal(5, 2), default=0.00)
    content_protection_score = Column(Decimal(5, 2), default=0.00)
    
    # Configuration plateforme
    content_formats = Column(JSON)  # ["audio", "video", "image", "text"]
    target_platforms = Column(JSON)  # ["spotify", "youtube", "instagram", "tiktok"]
    ai_protection_enabled = Column(Boolean, default=True)
    auto_distribution_enabled = Column(Boolean, default=False)
    collaboration_enabled = Column(Boolean, default=True)
    
    # SEO et découverte avancée
    seo_keywords = Column(JSON)  # Mots-clés SEO optimisés par IA
    genre_tags = Column(JSON)  # Tags de genre avec scores de pertinence
    collaboration_preferences = Column(JSON)  # Préférences de collaboration détaillées
    discovery_settings = Column(JSON)  # Paramètres de découverte et visibilité
    content_style_embedding = Column(JSON)  # Embedding vectoriel du style de contenu
    
    # Analytics et intelligence créateur
    audience_insights = Column(JSON)  # Insights sur l'audience (âge, localisation, préférences)
    performance_metrics = Column(JSON)  # Métriques de performance cross-platform
    growth_analytics = Column(JSON)  # Analytics de croissance et tendances
    engagement_patterns = Column(JSON)  # Patterns d'engagement identifiés par IA
    
    # Monétisation avancée
    revenue_streams = Column(JSON)  # Sources de revenus activées
    pricing_strategy = Column(JSON)  # Stratégies de pricing pour services
    merchandise_catalog = Column(JSON)  # Catalogue de produits dérivés
    licensing_portfolio = Column(JSON)  # Portfolio de contenus licenciables
    subscription_tiers = Column(JSON)  # Niveaux d'abonnement proposés
    
    # Protection et droits d'auteur
    copyright_registration = Column(JSON)  # Enregistrements de droits d'auteur
    content_fingerprints = Column(JSON)  # Empreintes numériques des contenus
    protection_alerts = Column(JSON)  # Alertes de protection actives
    takedown_history = Column(JSON)  # Historique des demandes de retrait
    legal_representatives = Column(JSON)  # Représentants légaux associés
    
    # Collaboration et réseau
    collaboration_history = Column(JSON)  # Historique des collaborations
    network_connections = Column(JSON)  # Connexions dans le réseau créateur
    mentor_relationships = Column(JSON)  # Relations de mentorat
    brand_partnerships = Column(JSON)  # Partenariats de marque
    cross_promotion_campaigns = Column(JSON)  # Campagnes de promotion croisée
    
    # Professionnalisation
    business_model = Column(String(100))  # "freelance", "agency", "label", "independent"
    team_members = Column(JSON)  # Membres de l'équipe (manager, producteur, etc.)
    professional_services = Column(JSON)  # Services professionnels proposés
    certification_level = Column(String(50))  # Niveau de certification plateforme
    industry_recognition = Column(JSON)  # Reconnaissances et prix industrie
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    onboarding_completed_at = Column(DateTime)
    
    # Relations
    user = relationship("User", back_populates="creator_account")
    platform_integrations = relationship("PlatformIntegration", back_populates="creator")
    collaborations = relationship("Collaboration", secondary="collaboration_participants", back_populates="participants")
    revenue_transactions = relationship("RevenueTransaction", back_populates="creator")

    def __init__(self, **kwargs):
        super().__init__()
        self.creator_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)

    def calculate_profile_completeness(self) -> float:
        """Calculer le score de complétude du profil créateur."""
        score = 0
        total_fields = 15
        
        if self.stage_name: score += 1
        if self.bio: score += 1
        if self.content_formats: score += 1
        if self.target_platforms: score += 1
        if self.genre_tags: score += 1
        if self.seo_keywords: score += 1
        if self.collaboration_preferences: score += 1
        if self.revenue_streams: score += 1
        if self.verification_level != VerificationLevel.UNVERIFIED: score += 1
        if self.total_uploads > 0: score += 1
        if self.total_followers > 0: score += 1
        if self.social_media_links: score += 1
        if self.professional_info: score += 1
        if self.content_protection_score > 0: score += 1
        if self.engagement_score > 0: score += 1
        
        return score / total_fields

    def update_engagement_score(self):
        """Mettre à jour le score d'engagement basé sur les métriques."""
        if self.total_followers > 0 and self.performance_metrics:
            # Calcul simplifié - à enrichir avec algorithme ML
            base_score = min(self.total_followers / 10000, 1.0) * 50
            activity_bonus = min(self.total_uploads / 100, 1.0) * 30
            collaboration_bonus = min(self.total_collaborations / 20, 1.0) * 20
            
            self.engagement_score = base_score + activity_bonus + collaboration_bonus
            self.updated_at = datetime.utcnow()

    def get_monetization_potential(self) -> Dict[str, Any]:
        """Analyser le potentiel de monétisation."""
        potential_score = 0
        recommendations = []
        
        # Analyse basée sur les métriques existantes
        if self.total_followers > 1000:
            potential_score += 20
            recommendations.append("Audience suffisante pour sponsorships")
        
        if self.engagement_score > 50:
            potential_score += 30
            recommendations.append("Engagement élevé - idéal pour collaborations")
        
        if len(self.revenue_streams or []) < 3:
            recommendations.append("Diversifier les sources de revenus")
        
        if self.verification_level == VerificationLevel.PROFESSIONAL_VERIFIED:
            potential_score += 25
            recommendations.append("Statut vérifié - crédibilité élevée")
        
        return {
            "score": min(potential_score, 100),
            "level": "high" if potential_score > 70 else "medium" if potential_score > 40 else "low",
            "recommendations": recommendations
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour API."""
        return {
            'id': self.id,
            'creator_uuid': self.creator_uuid,
            'creator_type': self.creator_type.value if self.creator_type else None,
            'stage_name': self.stage_name,
            'display_name': self.display_name,
            'status': self.status.value if self.status else None,
            'verification_level': self.verification_level.value if self.verification_level else None,
            'total_uploads': self.total_uploads,
            'total_followers': self.total_followers,
            'engagement_score': float(self.engagement_score) if self.engagement_score else 0,
            'content_protection_score': float(self.content_protection_score) if self.content_protection_score else 0,
            'monetization_enabled': self.monetization_enabled,
            'collaboration_enabled': self.collaboration_enabled,
            'target_platforms': self.target_platforms or [],
            'content_formats': self.content_formats or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_completeness': self.calculate_profile_completeness()
        }

    def __repr__(self):
        return f"<CreatorAccount({self.stage_name}, {self.creator_type.value})>"


class CreatorProfile(Base):
    """
    Profil détaillé du créateur avec informations professionnelles complètes.
    """
    __tablename__ = "creator_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_account_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False, unique=True)
    
    # Informations professionnelles
    professional_name = Column(String(200))
    company_name = Column(String(200))
    label_name = Column(String(200))
    manager_contact = Column(JSON)  # {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"}
    agent_contact = Column(JSON)  # Informations de l'agent
    publicist_contact = Column(JSON)  # Informations du publiciste
    
    # Réseaux sociaux et présence en ligne
    social_media_links = Column(JSON)  # Liens vers tous les réseaux sociaux
    website_url = Column(String(500))
    press_kit_url = Column(String(500))
    media_gallery_url = Column(String(500))
    streaming_links = Column(JSON)  # Liens vers plateformes de streaming
    
    # Informations de contact professionnel
    business_email = Column(String(255))
    business_phone = Column(String(50))
    booking_email = Column(String(255))
    
    # Portfolio et médias
    profile_image_url = Column(String(500))
    banner_image_url = Column(String(500))
    portfolio_urls = Column(JSON)
    demo_tracks = Column(JSON)
    
    # Historique professionnel
    career_start_year = Column(Integer)
    achievements = Column(JSON)
    awards = Column(JSON)
    press_coverage = Column(JSON)
    
    # Préférences collaboration
    looking_for_collaborations = Column(Boolean, default=True)
    collaboration_types = Column(JSON)  # ["featuring", "production", "remix"]
    collaboration_budget_range = Column(JSON)  # {"min": 100, "max": 5000}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    creator_account = relationship("CreatorAccount", back_populates="profile")

    def __repr__(self):
        return f"<CreatorProfile({self.professional_name})>"


class CreatorMetrics(Base):
    """
    Métriques détaillées et analytics pour les créateurs.
    """
    __tablename__ = "creator_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_account_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Période de mesure
    metric_date = Column(DateTime, nullable=False)
    metric_period = Column(String(20))  # "daily", "weekly", "monthly"
    
    # Métriques d'audience
    total_followers = Column(Integer, default=0)
    new_followers = Column(Integer, default=0)
    follower_growth_rate = Column(Decimal(5, 2), default=0.00)
    audience_demographics = Column(JSON)
    
    # Métriques de contenu
    content_views = Column(Integer, default=0)
    content_shares = Column(Integer, default=0)
    content_likes = Column(Integer, default=0)
    content_comments = Column(Integer, default=0)
    engagement_rate = Column(Decimal(5, 2), default=0.00)
    
    # Métriques de protection
    protected_content_count = Column(Integer, default=0)
    violations_detected = Column(Integer, default=0)
    violations_resolved = Column(Integer, default=0)
    protection_effectiveness = Column(Decimal(5, 2), default=0.00)
    
    # Métriques de revenus
    revenue_generated = Column(Decimal(12, 2), default=0.00)
    revenue_from_collaborations = Column(Decimal(12, 2), default=0.00)
    revenue_from_licensing = Column(Decimal(12, 2), default=0.00)
    platform_revenue_breakdown = Column(JSON)
    
    # AI et optimisation
    ai_recommendations_applied = Column(Integer, default=0)
    seo_score = Column(Decimal(5, 2), default=0.00)
    content_optimization_score = Column(Decimal(5, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    creator_account = relationship("CreatorAccount", back_populates="metrics")

    def __repr__(self):
        return f"<CreatorMetrics({self.metric_date}, {self.metric_period})>"


class CreatorAccountRepository:
    """
    Repository pattern pour les opérations sur les comptes créateurs.
    Implémentation professionnelle avec gestion d'erreurs avancée.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def create_creator_account(self, user_id: str, creator_data: Dict[str, Any]) -> CreatorAccount:
        """
        Crée un nouveau compte créateur avec validation complète.
        
        Args:
            user_id: ID de l'utilisateur
            creator_data: Données du créateur
            
        Returns:
            CreatorAccount: Compte créateur créé
            
        Raises:
            ValueError: Si les données sont invalides
            Exception: En cas d'erreur de création
        """
        try:
            # Validation des données obligatoires
            required_fields = ['creator_type', 'stage_name', 'display_name']
            for field in required_fields:
                if field not in creator_data:
                    raise ValueError(f"Champ obligatoire manquant: {field}")
            
            # Génération UUID unique
            creator_uuid = str(uuid.uuid4())
            
            # Création du compte
            creator_account = CreatorAccount(
                user_id=user_id,
                creator_uuid=creator_uuid,
                creator_type=CreatorType(creator_data['creator_type']),
                stage_name=creator_data['stage_name'],
                display_name=creator_data['display_name'],
                bio=creator_data.get('bio'),
                country_code=creator_data.get('country_code'),
                primary_language=creator_data.get('primary_language', 'en'),
                content_formats=creator_data.get('content_formats', []),
                target_platforms=creator_data.get('target_platforms', [])
            )
            
            self.session.add(creator_account)
            self.session.commit()
            
            self.logger.info(f"Compte créateur créé: {creator_account.id}")
            return creator_account
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur création compte créateur: {str(e)}")
            raise
    
    def get_creator_by_id(self, creator_id: str) -> Optional[CreatorAccount]:
        """Récupère un créateur par son ID."""
        return self.session.query(CreatorAccount).filter(
            CreatorAccount.id == creator_id
        ).first()
    
    def get_creator_by_user_id(self, user_id: str) -> Optional[CreatorAccount]:
        """Récupère un créateur par l'ID utilisateur."""
        return self.session.query(CreatorAccount).filter(
            CreatorAccount.user_id == user_id
        ).first()
    
    def update_creator_status(self, creator_id: str, status: CreatorStatus) -> bool:
        """
        Met à jour le statut d'un créateur.
        
        Args:
            creator_id: ID du créateur
            status: Nouveau statut
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator:
                return False
            
            creator.status = status
            creator.updated_at = datetime.utcnow()
            
            if status == CreatorStatus.VERIFIED:
                creator.verified_at = datetime.utcnow()
                creator.verification_badge = True
            
            self.session.commit()
            self.logger.info(f"Statut créateur mis à jour: {creator_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour statut: {str(e)}")
            return False
    
    def update_verification_level(self, creator_id: str, level: VerificationLevel) -> bool:
        """Met à jour le niveau de vérification d'un créateur."""
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator:
                return False
            
            creator.verification_level = level
            creator.updated_at = datetime.utcnow()
            
            if level == VerificationLevel.PROFESSIONAL_VERIFIED:
                creator.verification_badge = True
                creator.verified_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour vérification: {str(e)}")
            return False
    
    def update_creator_metrics(self, creator_id: str, metrics_data: Dict[str, Any]) -> bool:
        """Met à jour les métriques d'un créateur."""
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator:
                return False
            
            # Mise à jour des métriques de base
            if 'total_uploads' in metrics_data:
                creator.total_uploads = metrics_data['total_uploads']
            
            if 'total_followers' in metrics_data:
                creator.total_followers = metrics_data['total_followers']
            
            if 'total_revenue' in metrics_data:
                creator.total_revenue = metrics_data['total_revenue']
            
            # Calcul automatique du score d'engagement
            creator.update_engagement_score()
            
            # Mise à jour des analytics avancées
            if 'audience_insights' in metrics_data:
                creator.audience_insights = metrics_data['audience_insights']
            
            if 'performance_metrics' in metrics_data:
                creator.performance_metrics = metrics_data['performance_metrics']
            
            creator.updated_at = datetime.utcnow()
            self.session.commit()
            
            self.logger.info(f"Métriques créateur mises à jour: {creator_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour métriques: {str(e)}")
            return False
    
    def get_creators_by_type(self, creator_type: CreatorType, limit: int = 50) -> List[CreatorAccount]:
        """Récupère les créateurs par type."""
        try:
            return self.session.query(CreatorAccount).filter(
                CreatorAccount.creator_type == creator_type,
                CreatorAccount.status == CreatorStatus.ACTIVE
            ).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"Erreur récupération créateurs: {str(e)}")
            return []
    
    def search_creators(self, search_criteria: Dict[str, Any]) -> List[CreatorAccount]:
        """
        Recherche avancée de créateurs basée sur différents critères.
        
        Args:
            search_criteria: Critères de recherche
                - creator_type: Type de créateur
                - genre_tags: Tags de genre
                - country_code: Code pays
                - verification_level: Niveau de vérification
                - min_followers: Nombre minimum de followers
                - collaboration_enabled: Accepte les collaborations
                
        Returns:
            List[CreatorAccount]: Liste des créateurs trouvés
        """
        try:
            query = self.session.query(CreatorAccount).filter(
                CreatorAccount.status == CreatorStatus.ACTIVE
            )
            
            if 'creator_type' in search_criteria:
                query = query.filter(CreatorAccount.creator_type == search_criteria['creator_type'])
            
            if 'country_code' in search_criteria:
                query = query.filter(CreatorAccount.country_code == search_criteria['country_code'])
            
            if 'verification_level' in search_criteria:
                query = query.filter(CreatorAccount.verification_level == search_criteria['verification_level'])
            
            if 'min_followers' in search_criteria:
                query = query.filter(CreatorAccount.total_followers >= search_criteria['min_followers'])
            
            if 'collaboration_enabled' in search_criteria:
                query = query.filter(CreatorAccount.collaboration_enabled == search_criteria['collaboration_enabled'])
            
            # Recherche par tags de genre (JSON array contains)
            if 'genre_tags' in search_criteria:
                for tag in search_criteria['genre_tags']:
                    query = query.filter(CreatorAccount.genre_tags.contains([tag]))
            
            creators = query.limit(search_criteria.get('limit', 100)).all()
            
            self.logger.info(f"Recherche créateurs: {len(creators)} résultats")
            return creators
            
        except Exception as e:
            self.logger.error(f"Erreur recherche créateurs: {str(e)}")
            return []
    
    def get_creator_analytics(self, creator_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Récupère les analytics détaillées d'un créateur.
        
        Args:
            creator_id: ID du créateur
            timeframe_days: Période d'analyse en jours
            
        Returns:
            Dict[str, Any]: Analytics détaillées
        """
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator:
                return {}
            
            # Calcul des métriques de base
            analytics = {
                "creator_info": {
                    "id": creator.id,
                    "stage_name": creator.stage_name,
                    "creator_type": creator.creator_type.value,
                    "verification_level": creator.verification_level.value,
                    "status": creator.status.value
                },
                "current_metrics": {
                    "total_uploads": creator.total_uploads,
                    "total_followers": creator.total_followers,
                    "total_revenue": float(creator.total_revenue) if creator.total_revenue else 0,
                    "engagement_score": float(creator.engagement_score) if creator.engagement_score else 0,
                    "content_protection_score": float(creator.content_protection_score) if creator.content_protection_score else 0
                },
                "profile_analysis": {
                    "completeness_score": creator.calculate_profile_completeness(),
                    "monetization_potential": creator.get_monetization_potential(),
                    "active_platforms": len(creator.target_platforms or []),
                    "content_formats": len(creator.content_formats or [])
                },
                "growth_metrics": {
                    "account_age_days": (datetime.utcnow() - creator.created_at).days if creator.created_at else 0,
                    "last_activity": creator.last_activity_at.isoformat() if creator.last_activity_at else None,
                    "onboarding_completed": creator.onboarding_completed_at is not None
                }
            }
            
            # Ajout des insights spécifiques si disponibles
            if creator.audience_insights:
                analytics["audience_insights"] = creator.audience_insights
            
            if creator.performance_metrics:
                analytics["performance_metrics"] = creator.performance_metrics
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Erreur analytics créateur: {str(e)}")
            return {}
    
    def get_collaboration_candidates(self, creator_id: str, collaboration_type: str = None) -> List[Dict[str, Any]]:
        """
        Trouve des candidats pour collaboration basé sur l'IA matching.
        
        Args:
            creator_id: ID du créateur cherchant des collaborations
            collaboration_type: Type de collaboration recherché
            
        Returns:
            List[Dict[str, Any]]: Liste des candidats avec scores de compatibilité
        """
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator or not creator.collaboration_enabled:
                return []
            
            # Recherche de créateurs compatibles
            candidates_query = self.session.query(CreatorAccount).filter(
                CreatorAccount.id != creator_id,
                CreatorAccount.collaboration_enabled == True,
                CreatorAccount.status == CreatorStatus.ACTIVE
            )
            
            # Filtrer par préférences de collaboration si spécifiées
            if creator.collaboration_preferences:
                preferred_types = creator.collaboration_preferences.get('preferred_types', [])
                if preferred_types and collaboration_type:
                    if collaboration_type not in preferred_types:
                        return []
            
            potential_candidates = candidates_query.limit(50).all()
            
            # Calcul des scores de compatibilité
            candidates_with_scores = []
            for candidate in potential_candidates:
                compatibility_score = self._calculate_compatibility_score(creator, candidate, collaboration_type)
                
                if compatibility_score > 0.3:  # Seuil minimum de compatibilité
                    candidates_with_scores.append({
                        "creator": {
                            "id": candidate.id,
                            "stage_name": candidate.stage_name,
                            "creator_type": candidate.creator_type.value,
                            "total_followers": candidate.total_followers,
                            "engagement_score": float(candidate.engagement_score) if candidate.engagement_score else 0,
                            "verification_level": candidate.verification_level.value,
                            "target_platforms": candidate.target_platforms or [],
                            "genre_tags": candidate.genre_tags or []
                        },
                        "compatibility_score": round(compatibility_score, 2),
                        "collaboration_factors": self._get_collaboration_factors(creator, candidate),
                        "recommended_collaboration_types": self._get_recommended_collaboration_types(creator, candidate)
                    })
            
            # Trier par score de compatibilité décroissant
            candidates_with_scores.sort(key=lambda x: x["compatibility_score"], reverse=True)
            
            self.logger.info(f"Trouvé {len(candidates_with_scores)} candidats pour {creator_id}")
            return candidates_with_scores[:20]  # Retourner les 20 meilleurs
            
        except Exception as e:
            self.logger.error(f"Erreur recherche candidats: {str(e)}")
            return []
    
    def _calculate_compatibility_score(self, creator1: CreatorAccount, creator2: CreatorAccount, collaboration_type: str = None) -> float:
        """Calcule le score de compatibilité entre deux créateurs."""
        score = 0.0
        
        # Compatibilité des plateformes (30%)
        common_platforms = set(creator1.target_platforms or []) & set(creator2.target_platforms or [])
        if common_platforms:
            platform_score = len(common_platforms) / max(len(creator1.target_platforms or []), len(creator2.target_platforms or []), 1)
            score += platform_score * 0.3
        
        # Compatibilité des genres (25%)
        common_genres = set(creator1.genre_tags or []) & set(creator2.genre_tags or [])
        if common_genres:
            genre_score = len(common_genres) / max(len(creator1.genre_tags or []), len(creator2.genre_tags or []), 1)
            score += genre_score * 0.25
        
        # Compatibilité géographique (15%)
        if creator1.country_code == creator2.country_code:
            score += 0.15
        elif creator1.market_regions and creator2.market_regions:
            common_markets = set(creator1.market_regions or []) & set(creator2.market_regions or [])
            if common_markets:
                score += 0.1
        
        # Équilibre des métriques (20%)
        followers_ratio = min(creator1.total_followers, creator2.total_followers) / max(creator1.total_followers, creator2.total_followers, 1)
        if followers_ratio > 0.3:  # Éviter les déséquilibres trop importants
            score += followers_ratio * 0.2
        
        # Niveau de vérification (10%)
        if creator1.verification_level == creator2.verification_level and creator1.verification_level != VerificationLevel.UNVERIFIED:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_collaboration_factors(self, creator1: CreatorAccount, creator2: CreatorAccount) -> List[str]:
        """Identifie les facteurs de collaboration positifs."""
        factors = []
        
        common_platforms = set(creator1.target_platforms or []) & set(creator2.target_platforms or [])
        if common_platforms:
            factors.append(f"Plateformes communes: {', '.join(common_platforms)}")
        
        common_genres = set(creator1.genre_tags or []) & set(creator2.genre_tags or [])
        if common_genres:
            factors.append(f"Genres compatibles: {', '.join(common_genres)}")
        
        if creator1.country_code == creator2.country_code:
            factors.append("Même région géographique")
        
        if creator1.verification_level == creator2.verification_level and creator1.verification_level != VerificationLevel.UNVERIFIED:
            factors.append("Niveau de vérification similaire")
        
        return factors
    
    def _get_recommended_collaboration_types(self, creator1: CreatorAccount, creator2: CreatorAccount) -> List[str]:
        """Recommande des types de collaboration basés sur les profils."""
        recommendations = []
        
        # Logique basée sur les types de créateurs
        if creator1.creator_type == CreatorType.MUSICIAN and creator2.creator_type == CreatorType.MUSICIAN:
            recommendations.extend(["music_feature", "remix_remix", "joint_project"])
        
        if creator1.creator_type == CreatorType.PODCASTER or creator2.creator_type == CreatorType.PODCASTER:
            recommendations.append("podcast_guest")
        
        if creator1.creator_type == CreatorType.INFLUENCER or creator2.creator_type == CreatorType.INFLUENCER:
            recommendations.extend(["content_cross_promotion", "brand_partnership"])
        
        # Collaborations génériques toujours possibles
        recommendations.extend(["content_cross_promotion", "joint_project"])
        
        return list(set(recommendations))  # Supprimer les doublons
            if not creator:
                return False
            
            creator.status = status
            creator.updated_at = datetime.utcnow()
            
            if status == CreatorStatus.VERIFIED:
                creator.verified_at = datetime.utcnow()
                creator.verification_badge = True
            
            self.session.commit()
            self.logger.info(f"Statut créateur mis à jour: {creator_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour statut: {str(e)}")
            return False
    
    def update_metrics(self, creator_id: str, metrics_data: Dict[str, Any]) -> bool:
        """
        Met à jour les métriques d'un créateur.
        
        Args:
            creator_id: ID du créateur
            metrics_data: Données de métriques
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            creator = self.get_creator_by_id(creator_id)
            if not creator:
                return False
            
            # Mise à jour des métriques principales
            if 'total_uploads' in metrics_data:
                creator.total_uploads = metrics_data['total_uploads']
            if 'total_followers' in metrics_data:
                creator.total_followers = metrics_data['total_followers']
            if 'total_revenue' in metrics_data:
                creator.total_revenue = metrics_data['total_revenue']
            if 'engagement_score' in metrics_data:
                creator.engagement_score = metrics_data['engagement_score']
            
            creator.updated_at = datetime.utcnow()
            creator.last_activity_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour métriques: {str(e)}")
            return False
    
    def search_creators(self, filters: Dict[str, Any], limit: int = 50) -> List[CreatorAccount]:
        """
        Recherche de créateurs avec filtres avancés.
        
        Args:
            filters: Filtres de recherche
            limit: Limite de résultats
            
        Returns:
            List[CreatorAccount]: Liste des créateurs trouvés
        """
        query = self.session.query(CreatorAccount)
        
        # Filtres disponibles
        if 'creator_type' in filters:
            query = query.filter(CreatorAccount.creator_type == filters['creator_type'])
        
        if 'status' in filters:
            query = query.filter(CreatorAccount.status == filters['status'])
        
        if 'verification_level' in filters:
            query = query.filter(CreatorAccount.verification_level == filters['verification_level'])
        
        if 'country_code' in filters:
            query = query.filter(CreatorAccount.country_code == filters['country_code'])
        
        if 'content_formats' in filters:
            query = query.filter(CreatorAccount.content_formats.contains(filters['content_formats']))
        
        if 'min_followers' in filters:
            query = query.filter(CreatorAccount.total_followers >= filters['min_followers'])
        
        return query.limit(limit).all()
    
    def get_creator_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques globales des créateurs.
        
        Returns:
            Dict[str, Any]: Statistiques globales
        """
        total_creators = self.session.query(CreatorAccount).count()
        
        # Répartition par type
        type_stats = {}
        for creator_type in CreatorType:
            count = self.session.query(CreatorAccount).filter(
                CreatorAccount.creator_type == creator_type
            ).count()
            type_stats[creator_type.value] = count
        
        # Répartition par statut
        status_stats = {}
        for status in CreatorStatus:
            count = self.session.query(CreatorAccount).filter(
                CreatorAccount.status == status
            ).count()
            status_stats[status.value] = count
        
        return {
            'total_creators': total_creators,
            'by_type': type_stats,
            'by_status': status_stats,
            'last_updated': datetime.utcnow().isoformat()
        }


# Configuration des relations (à compléter avec les autres modèles)
CreatorAccount.profile = relationship("CreatorProfile", back_populates="creator_account", uselist=False)
CreatorAccount.metrics = relationship("CreatorMetrics", back_populates="creator_account")
