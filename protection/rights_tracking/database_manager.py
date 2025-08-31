"""Database Manager - Enterprise Database Management System
Gestionnaire de base de données avancé pour le suivi des droits
Système professionnel avec haute disponibilité et performance optimisée

Auteur: Fahed Mlaiel - Lead Developer & AI Architect
Email: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  AVERTISSEMENT LÉGAL - PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel et est protégé par les lois
sur la propriété intellectuelle. Toute reproduction, distribution, ou utilisation
non autorisée est strictement interdite et passible de poursuites judiciaires.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json
from decimal import Decimal

from sqlalchemy import create_engine, and_, or_, func, text
from sqlalchemy.orm import sessionmaker, Session, selectinload, joinedload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from alembic import command
from alembic.config import Config

from .data_models import (
    Base, ContentMetadata, RightsHolder, RightsRecord, CoHolderAssociation,
    LicenseAgreement, UsageEvent, UsageReport, RoyaltyCalculation,
    PaymentInstruction, TerritorialRights
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire de base de données enterprise pour le rights tracking"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = None
        self.async_session_factory = None
        self.redis_client = None
        
        # Configuration
        self.database_url = config.get('database_url')
        self.redis_url = config.get('redis_url', 'redis://localhost:6379/0')
        self.connection_pool_size = config.get('pool_size', 20)
        self.max_overflow = config.get('max_overflow', 30)
        self.pool_timeout = config.get('pool_timeout', 30)
        self.pool_recycle = config.get('pool_recycle', 3600)
        
        # Cache settings
        self.cache_enabled = config.get('cache_enabled', True)
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour
        
        # Performance settings
        self.query_timeout = config.get('query_timeout', 30)
        self.batch_size = config.get('batch_size', 1000)
        
    async def initialize(self) -> bool:
        """Initialise le gestionnaire de base de données"""        try:
            # Configuration de l'engine async
            self.engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.connection_pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=self.config.get('sql_debug', False)
            )
            
            # Session factory
            self.async_session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Cache Redis
            if self.cache_enabled:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    encoding='utf-8',
                    decode_responses=True,
                    socket_timeout=5.0,
                    socket_connect_timeout=5.0,
                    retry_on_timeout=True
                )
                
                # Test de connexion Redis
                await self.redis_client.ping()
                logger.info("Connexion Redis établie")
            
            # Création des tables si nécessaire
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Gestionnaire de base de données initialisé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation base de données: {e}")
            return False
    
    @asynccontextmanager
    async def get_session(self):
        """Context manager pour les sessions de base de données"""        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Erreur session database: {e}")
                raise
            finally:
                await session.close()
    
    # =================================================================
    # CONTENT METADATA OPERATIONS
    # =================================================================
    
    async def create_content_metadata(
        self, 
        content_data: Dict[str, Any]
    ) -> Optional[ContentMetadata]:
        """Crée une nouvelle entrée de métadonnées de contenu"""        try:
            async with self.get_session() as session:
                content_metadata = ContentMetadata(**content_data)
                session.add(content_metadata)
                await session.flush()
                await session.refresh(content_metadata)
                
                # Cache
                if self.cache_enabled:
                    await self._cache_content_metadata(content_metadata)
                
                logger.info(f"Métadonnées contenu créées: {content_metadata.content_id}")
                return content_metadata
                
        except Exception as e:
            logger.error(f"Erreur création métadonnées contenu: {e}")
            return None
    
    async def get_content_metadata(
        self, 
        content_id: str,
        include_relations: bool = False
    ) -> Optional[ContentMetadata]:
        """Récupère les métadonnées d'un contenu"""        try:
            # Vérification cache
            if self.cache_enabled:
                cached = await self._get_cached_content_metadata(content_id)
                if cached:
                    return cached
            
            async with self.get_session() as session:
                query = session.query(ContentMetadata).filter(
                    ContentMetadata.content_id == content_id
                )
                
                if include_relations:
                    query = query.options(
                        selectinload(ContentMetadata.rights_records),
                        selectinload(ContentMetadata.usage_events)
                    )
                
                content_metadata = await query.first()
                
                if content_metadata and self.cache_enabled:
                    await self._cache_content_metadata(content_metadata)
                
                return content_metadata
                
        except Exception as e:
            logger.error(f"Erreur récupération métadonnées contenu {content_id}: {e}")
            return None
    
    async def search_content_by_fingerprint(
        self, 
        fingerprint_data: Dict[str, Any],
        similarity_threshold: float = 0.85
    ) -> List[ContentMetadata]:
        """Recherche de contenu par empreinte digitale"""        try:
            async with self.get_session() as session:
                # Recherche par hash exact d'abord
                if 'md5_hash' in fingerprint_data:
                    query = session.query(ContentMetadata).filter(
                        ContentMetadata.md5_hash == fingerprint_data['md5_hash']
                    )
                    exact_matches = await query.all()
                    if exact_matches:
                        return exact_matches
                
                # Recherche par similarité d'empreinte (placeholder)
                # En production, utiliser une base vectorielle comme FAISS
                query = session.query(ContentMetadata).filter(
                    ContentMetadata.content_fingerprint.isnot(None)
                ).limit(100)
                
                all_content = await query.all()
                similar_content = []
                
                for content in all_content:
                    if content.content_fingerprint:
                        # Calcul de similarité simplifié
                        # En production, utiliser des algorithmes de similarité avancés
                        similarity = await self._calculate_fingerprint_similarity(
                            fingerprint_data,
                            json.loads(content.content_fingerprint)
                        )
                        
                        if similarity >= similarity_threshold:
                            similar_content.append((content, similarity))
                
                # Tri par similarité décroissante
                similar_content.sort(key=lambda x: x[1], reverse=True)
                return [content for content, _ in similar_content[:20]]
                
        except Exception as e:
            logger.error(f"Erreur recherche par empreinte: {e}")
            return []
    
    # =================================================================
    # RIGHTS HOLDER OPERATIONS
    # =================================================================
    
    async def create_rights_holder(
        self, 
        holder_data: Dict[str, Any]
    ) -> Optional[RightsHolder]:
        """Crée un nouveau détenteur de droits"""        try:
            async with self.get_session() as session:
                rights_holder = RightsHolder(**holder_data)
                session.add(rights_holder)
                await session.flush()
                await session.refresh(rights_holder)
                
                # Cache
                if self.cache_enabled:
                    await self._cache_rights_holder(rights_holder)
                
                logger.info(f"Détenteur de droits créé: {rights_holder.holder_id}")
                return rights_holder
                
        except Exception as e:
            logger.error(f"Erreur création détenteur de droits: {e}")
            return None
    
    async def get_rights_holder(
        self, 
        holder_id: str,
        include_relations: bool = False
    ) -> Optional[RightsHolder]:
        """Récupère un détenteur de droits"""        try:
            # Vérification cache
            if self.cache_enabled:
                cached = await self._get_cached_rights_holder(holder_id)
                if cached:
                    return cached
            
            async with self.get_session() as session:
                query = session.query(RightsHolder).filter(
                    RightsHolder.holder_id == holder_id
                )
                
                if include_relations:
                    query = query.options(
                        selectinload(RightsHolder.rights_records),
                        selectinload(RightsHolder.license_agreements)
                    )
                
                rights_holder = await query.first()
                
                if rights_holder and self.cache_enabled:
                    await self._cache_rights_holder(rights_holder)
                
                return rights_holder
                
        except Exception as e:
            logger.error(f"Erreur récupération détenteur {holder_id}: {e}")
            return None
    
    async def search_rights_holders(
        self,
        search_params: Dict[str, Any],
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[RightsHolder], int]:
        """Recherche de détenteurs de droits avec pagination"""        try:
            async with self.get_session() as session:
                query = session.query(RightsHolder)
                count_query = session.query(func.count(RightsHolder.id))
                
                # Filtres de recherche
                if 'name' in search_params:
                    name_filter = or_(
                        RightsHolder.legal_name.ilike(f"%{search_params['name']}%"),
                        RightsHolder.display_name.ilike(f"%{search_params['name']}%"),
                        RightsHolder.artist_name.ilike(f"%{search_params['name']}%")
                    )
                    query = query.filter(name_filter)
                    count_query = count_query.filter(name_filter)
                
                if 'email' in search_params:
                    email_filter = RightsHolder.email == search_params['email']
                    query = query.filter(email_filter)
                    count_query = count_query.filter(email_filter)
                
                if 'country' in search_params:
                    country_filter = RightsHolder.country == search_params['country']
                    query = query.filter(country_filter)
                    count_query = count_query.filter(country_filter)
                
                if 'holder_type' in search_params:
                    type_filter = RightsHolder.holder_type == search_params['holder_type']
                    query = query.filter(type_filter)
                    count_query = count_query.filter(type_filter)
                
                if 'account_status' in search_params:
                    status_filter = RightsHolder.account_status == search_params['account_status']
                    query = query.filter(status_filter)
                    count_query = count_query.filter(status_filter)
                
                # Tri
                query = query.order_by(RightsHolder.created_at.desc())
                
                # Pagination
                query = query.offset(offset).limit(limit)
                
                # Exécution
                holders = await query.all()
                total_count = await count_query.scalar()
                
                return holders, total_count
                
        except Exception as e:
            logger.error(f"Erreur recherche détenteurs: {e}")
            return [], 0
    
    # =================================================================
    # RIGHTS RECORD OPERATIONS
    # =================================================================
    
    async def create_rights_record(
        self,
        record_data: Dict[str, Any],
        co_holders: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[RightsRecord]:
        """Crée un enregistrement de droits avec co-détenteurs"""        try:
            async with self.get_session() as session:
                # Création de l'enregistrement principal
                rights_record = RightsRecord(**record_data)
                session.add(rights_record)
                await session.flush()
                
                # Ajout des co-détenteurs
                if co_holders:
                    for co_holder_data in co_holders:
                        co_holder_assoc = CoHolderAssociation(
                            rights_record_id=rights_record.record_id,
                            **co_holder_data
                        )
                        session.add(co_holder_assoc)
                
                await session.flush()
                await session.refresh(rights_record)
                
                # Cache
                if self.cache_enabled:
                    await self._cache_rights_record(rights_record)
                
                logger.info(f"Enregistrement de droits créé: {rights_record.record_id}")
                return rights_record
                
        except Exception as e:
            logger.error(f"Erreur création enregistrement droits: {e}")
            return None
    
    async def get_rights_record(
        self,
        record_id: str,
        include_relations: bool = False
    ) -> Optional[RightsRecord]:
        """Récupère un enregistrement de droits"""        try:
            # Vérification cache
            if self.cache_enabled:
                cached = await self._get_cached_rights_record(record_id)
                if cached:
                    return cached
            
            async with self.get_session() as session:
                query = session.query(RightsRecord).filter(
                    RightsRecord.record_id == record_id
                )
                
                if include_relations:
                    query = query.options(
                        selectinload(RightsRecord.content_metadata),
                        selectinload(RightsRecord.primary_holder_rel),
                        selectinload(RightsRecord.co_holders),
                        selectinload(RightsRecord.license_agreements)
                    )
                
                rights_record = await query.first()
                
                if rights_record and self.cache_enabled:
                    await self._cache_rights_record(rights_record)
                
                return rights_record
                
        except Exception as e:
            logger.error(f"Erreur récupération enregistrement {record_id}: {e}")
            return None
    
    async def get_rights_by_content(
        self,
        content_id: str,
        include_relations: bool = False
    ) -> List[RightsRecord]:
        """Récupère tous les enregistrements de droits pour un contenu"""        try:
            async with self.get_session() as session:
                query = session.query(RightsRecord).filter(
                    RightsRecord.content_id == content_id
                )
                
                if include_relations:
                    query = query.options(
                        selectinload(RightsRecord.primary_holder_rel),
                        selectinload(RightsRecord.co_holders)
                    )
                
                rights_records = await query.all()
                return rights_records
                
        except Exception as e:
            logger.error(f"Erreur récupération droits par contenu {content_id}: {e}")
            return []
    
    async def get_rights_by_holder(
        self,
        holder_id: str,
        include_co_holdings: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[RightsRecord], int]:
        """Récupère tous les droits d'un détenteur"""        try:
            async with self.get_session() as session:
                query = session.query(RightsRecord)
                count_query = session.query(func.count(RightsRecord.id))
                
                if include_co_holdings:
                    # Inclut les droits où l'utilisateur est détenteur principal ou co-détenteur
                    holder_filter = or_(
                        RightsRecord.primary_holder_id == holder_id,
                        RightsRecord.co_holders.any(CoHolderAssociation.holder_id == holder_id)
                    )
                else:
                    # Seulement les droits où l'utilisateur est détenteur principal
                    holder_filter = RightsRecord.primary_holder_id == holder_id
                
                query = query.filter(holder_filter)
                count_query = count_query.filter(holder_filter)
                
                # Tri par date de création décroissante
                query = query.order_by(RightsRecord.created_at.desc())
                
                # Pagination
                query = query.offset(offset).limit(limit)
                
                rights_records = await query.all()
                total_count = await count_query.scalar()
                
                return rights_records, total_count
                
        except Exception as e:
            logger.error(f"Erreur récupération droits détenteur {holder_id}: {e}")
            return [], 0
    
    # =================================================================
    # LICENSE AGREEMENT OPERATIONS
    # =================================================================
    
    async def create_license_agreement(
        self,
        license_data: Dict[str, Any]
    ) -> Optional[LicenseAgreement]:
        """Crée un accord de licence"""        try:
            async with self.get_session() as session:
                license_agreement = LicenseAgreement(**license_data)
                session.add(license_agreement)
                await session.flush()
                await session.refresh(license_agreement)
                
                # Cache
                if self.cache_enabled:
                    await self._cache_license_agreement(license_agreement)
                
                logger.info(f"Accord de licence créé: {license_agreement.license_id}")
                return license_agreement
                
        except Exception as e:
            logger.error(f"Erreur création accord licence: {e}")
            return None
    
    async def get_license_agreement(
        self,
        license_id: str,
        include_relations: bool = False
    ) -> Optional[LicenseAgreement]:
        """Récupère un accord de licence"""        try:
            # Vérification cache
            if self.cache_enabled:
                cached = await self._get_cached_license_agreement(license_id)
                if cached:
                    return cached
            
            async with self.get_session() as session:
                query = session.query(LicenseAgreement).filter(
                    LicenseAgreement.license_id == license_id
                )
                
                if include_relations:
                    query = query.options(
                        selectinload(LicenseAgreement.rights_record),
                        selectinload(LicenseAgreement.licensor_rel),
                        selectinload(LicenseAgreement.usage_reports)
                    )
                
                license_agreement = await query.first()
                
                if license_agreement and self.cache_enabled:
                    await self._cache_license_agreement(license_agreement)
                
                return license_agreement
                
        except Exception as e:
            logger.error(f"Erreur récupération licence {license_id}: {e}")
            return None
    
    async def get_active_licenses_by_content(
        self,
        content_id: str
    ) -> List[LicenseAgreement]:
        """Récupère les licences actives pour un contenu"""        try:
            async with self.get_session() as session:
                current_time = datetime.utcnow()
                
                query = session.query(LicenseAgreement).join(
                    RightsRecord,
                    LicenseAgreement.rights_record_id == RightsRecord.record_id
                ).filter(
                    and_(
                        RightsRecord.content_id == content_id,
                        LicenseAgreement.status == 'active',
                        LicenseAgreement.start_date <= current_time,
                        or_(
                            LicenseAgreement.end_date.is_(None),
                            LicenseAgreement.end_date > current_time
                        )
                    )
                )
                
                licenses = await query.all()
                return licenses
                
        except Exception as e:
            logger.error(f"Erreur récupération licences actives {content_id}: {e}")
            return []
    
    # =================================================================
    # USAGE EVENT OPERATIONS
    # =================================================================
    
    async def create_usage_event(
        self,
        event_data: Dict[str, Any]
    ) -> Optional[UsageEvent]:
        """Crée un événement d'utilisation"""        try:
            async with self.get_session() as session:
                usage_event = UsageEvent(**event_data)
                session.add(usage_event)
                await session.flush()
                await session.refresh(usage_event)
                
                logger.info(f"Événement d'utilisation créé: {usage_event.event_id}")
                return usage_event
                
        except Exception as e:
            logger.error(f"Erreur création événement utilisation: {e}")
            return None
    
    async def bulk_create_usage_events(
        self,
        events_data: List[Dict[str, Any]]
    ) -> int:
        """Création en lot d'événements d'utilisation"""        try:
            created_count = 0
            batch_size = self.batch_size
            
            async with self.get_session() as session:
                for i in range(0, len(events_data), batch_size):
                    batch = events_data[i:i + batch_size]
                    
                    usage_events = [UsageEvent(**event_data) for event_data in batch]
                    session.add_all(usage_events)
                    
                    await session.flush()
                    created_count += len(usage_events)
                
                logger.info(f"Événements d'utilisation créés en lot: {created_count}")
                return created_count
                
        except Exception as e:
            logger.error(f"Erreur création lot événements: {e}")
            return 0
    
    async def get_usage_events_by_content(
        self,
        content_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        platform_id: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Tuple[List[UsageEvent], int]:
        """Récupère les événements d'utilisation pour un contenu"""        try:
            async with self.get_session() as session:
                query = session.query(UsageEvent).filter(
                    UsageEvent.content_id == content_id
                )
                count_query = session.query(func.count(UsageEvent.id)).filter(
                    UsageEvent.content_id == content_id
                )
                
                # Filtres temporels
                if start_date:
                    date_filter = UsageEvent.detected_at >= start_date
                    query = query.filter(date_filter)
                    count_query = count_query.filter(date_filter)
                
                if end_date:
                    date_filter = UsageEvent.detected_at <= end_date
                    query = query.filter(date_filter)
                    count_query = count_query.filter(date_filter)
                
                # Filtre plateforme
                if platform_id:
                    platform_filter = UsageEvent.platform_id == platform_id
                    query = query.filter(platform_filter)
                    count_query = count_query.filter(platform_filter)
                
                # Tri par date de détection décroissante
                query = query.order_by(UsageEvent.detected_at.desc())
                
                # Pagination
                query = query.offset(offset).limit(limit)
                
                events = await query.all()
                total_count = await count_query.scalar()
                
                return events, total_count
                
        except Exception as e:
            logger.error(f"Erreur récupération événements {content_id}: {e}")
            return [], 0
    
    # =================================================================
    # ANALYTICS AND REPORTING
    # =================================================================
    
    async def get_content_usage_analytics(
        self,
        content_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Génère des analytics d'utilisation pour un contenu"""        try:
            async with self.get_session() as session:
                # Métriques de base
                base_query = session.query(UsageEvent).filter(
                    and_(
                        UsageEvent.content_id == content_id,
                        UsageEvent.detected_at >= period_start,
                        UsageEvent.detected_at <= period_end
                    )
                )
                
                # Comptages totaux
                total_events = await base_query.count()
                total_views = await base_query.with_entities(
                    func.sum(UsageEvent.view_count)
                ).scalar() or 0
                total_revenue = await base_query.with_entities(
                    func.sum(UsageEvent.revenue_generated)
                ).scalar() or 0
                
                # Répartition par plateforme
                platform_stats = await base_query.with_entities(
                    UsageEvent.platform_id,
                    func.count(UsageEvent.id).label('event_count'),
                    func.sum(UsageEvent.view_count).label('total_views'),
                    func.sum(UsageEvent.revenue_generated).label('total_revenue')
                ).group_by(UsageEvent.platform_id).all()
                
                # Répartition géographique
                geo_stats = await base_query.filter(
                    UsageEvent.geographic_location.isnot(None)
                ).with_entities(
                    UsageEvent.geographic_location,
                    func.count(UsageEvent.id).label('event_count'),
                    func.sum(UsageEvent.view_count).label('total_views')
                ).group_by(UsageEvent.geographic_location).all()
                
                # Tendances temporelles (par jour)
                daily_stats = await base_query.with_entities(
                    func.date(UsageEvent.detected_at).label('date'),
                    func.count(UsageEvent.id).label('event_count'),
                    func.sum(UsageEvent.view_count).label('total_views'),
                    func.sum(UsageEvent.revenue_generated).label('total_revenue')
                ).group_by(func.date(UsageEvent.detected_at)).all()
                
                analytics = {
                    'content_id': content_id,
                    'period': {
                        'start': period_start.isoformat(),
                        'end': period_end.isoformat()
                    },
                    'summary': {
                        'total_events': total_events,
                        'total_views': int(total_views),
                        'total_revenue': float(total_revenue),
                        'unique_platforms': len(platform_stats),
                        'unique_locations': len(geo_stats)
                    },
                    'platform_breakdown': [
                        {
                            'platform_id': stat.platform_id,
                            'event_count': stat.event_count,
                            'total_views': int(stat.total_views or 0),
                            'total_revenue': float(stat.total_revenue or 0)
                        }
                        for stat in platform_stats
                    ],
                    'geographic_breakdown': [
                        {
                            'location': stat.geographic_location,
                            'event_count': stat.event_count,
                            'total_views': int(stat.total_views or 0)
                        }
                        for stat in geo_stats
                    ],
                    'daily_trends': [
                        {
                            'date': stat.date.isoformat(),
                            'event_count': stat.event_count,
                            'total_views': int(stat.total_views or 0),
                            'total_revenue': float(stat.total_revenue or 0)
                        }
                        for stat in daily_stats
                    ]
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Erreur analytics contenu {content_id}: {e}")
            return {}
    
    async def get_holder_revenue_summary(
        self,
        holder_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Génère un résumé des revenus pour un détenteur"""        try:
            async with self.get_session() as session:
                # Jointure complexe pour récupérer les revenus
                revenue_query = session.query(
                    func.sum(RoyaltyCalculation.net_royalty).label('total_revenue'),
                    func.count(RoyaltyCalculation.id).label('calculation_count'),
                    func.avg(RoyaltyCalculation.net_royalty).label('avg_revenue')
                ).join(
                    UsageReport,
                    RoyaltyCalculation.usage_report_id == UsageReport.report_id
                ).join(
                    LicenseAgreement,
                    UsageReport.license_agreement_id == LicenseAgreement.license_id
                ).filter(
                    and_(
                        LicenseAgreement.licensor_id == holder_id,
                        RoyaltyCalculation.calculated_at >= period_start,
                        RoyaltyCalculation.calculated_at <= period_end
                    )
                )
                
                revenue_stats = await revenue_query.first()
                
                # Revenus par contenu
                content_revenue = await session.query(
                    RoyaltyCalculation.content_id,
                    func.sum(RoyaltyCalculation.net_royalty).label('content_revenue'),
                    func.count(RoyaltyCalculation.id).label('calculation_count')
                ).join(
                    UsageReport,
                    RoyaltyCalculation.usage_report_id == UsageReport.report_id
                ).join(
                    LicenseAgreement,
                    UsageReport.license_agreement_id == LicenseAgreement.license_id
                ).filter(
                    and_(
                        LicenseAgreement.licensor_id == holder_id,
                        RoyaltyCalculation.calculated_at >= period_start,
                        RoyaltyCalculation.calculated_at <= period_end
                    )
                ).group_by(RoyaltyCalculation.content_id).all()
                
                summary = {
                    'holder_id': holder_id,
                    'period': {
                        'start': period_start.isoformat(),
                        'end': period_end.isoformat()
                    },
                    'revenue_summary': {
                        'total_revenue': float(revenue_stats.total_revenue or 0),
                        'calculation_count': revenue_stats.calculation_count or 0,
                        'average_revenue': float(revenue_stats.avg_revenue or 0)
                    },
                    'content_breakdown': [
                        {
                            'content_id': stat.content_id,
                            'total_revenue': float(stat.content_revenue),
                            'calculation_count': stat.calculation_count
                        }
                        for stat in content_revenue
                    ]
                }
                
                return summary
                
        except Exception as e:
            logger.error(f"Erreur résumé revenus détenteur {holder_id}: {e}")
            return {}
    
    # =================================================================
    # CACHE OPERATIONS
    # =================================================================
    
    async def _cache_content_metadata(self, content_metadata: ContentMetadata):
        """Met en cache les métadonnées de contenu"""        if not self.redis_client:
            return
        
        try:
            cache_key = f"content_metadata:{content_metadata.content_id}"
            cache_data = {
                'content_id': content_metadata.content_id,
                'title': content_metadata.title,
                'content_type': content_metadata.content_type,
                'created_at': content_metadata.created_at.isoformat(),
                'updated_at': content_metadata.updated_at.isoformat()
            }
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur cache métadonnées contenu: {e}")
    
    async def _get_cached_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les métadonnées de contenu du cache"""        if not self.redis_client:
            return None
        
        try:
            cache_key = f"content_metadata:{content_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
        except Exception as e:
            logger.error(f"Erreur récupération cache métadonnées: {e}")
        
        return None
    
    async def _cache_rights_holder(self, rights_holder: RightsHolder):
        """Met en cache un détenteur de droits"""        if not self.redis_client:
            return
        
        try:
            cache_key = f"rights_holder:{rights_holder.holder_id}"
            cache_data = {
                'holder_id': rights_holder.holder_id,
                'legal_name': rights_holder.legal_name,
                'email': rights_holder.email,
                'account_status': rights_holder.account_status,
                'created_at': rights_holder.created_at.isoformat()
            }
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur cache détenteur droits: {e}")
    
    async def _get_cached_rights_holder(self, holder_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un détenteur de droits du cache"""        if not self.redis_client:
            return None
        
        try:
            cache_key = f"rights_holder:{holder_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
        except Exception as e:
            logger.error(f"Erreur récupération cache détenteur: {e}")
        
        return None
    
    async def invalidate_cache(self, pattern: str):
        """Invalide les entrées de cache selon un pattern"""        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Cache invalidé: {len(keys)} entrées supprimées")
            
        except Exception as e:
            logger.error(f"Erreur invalidation cache: {e}")
    
    # =================================================================
    # UTILITY METHODS
    # =================================================================
    
    async def _calculate_fingerprint_similarity(
        self,
        fingerprint1: Dict[str, Any],
        fingerprint2: Dict[str, Any]
    ) -> float:
        """Calcule la similarité entre deux empreintes"""        # Implémentation simplifiée
        # En production, utiliser des algorithmes spécialisés
        
        if not fingerprint1 or not fingerprint2:
            return 0.0
        
        # Comparaison des hashes si disponibles
        if 'audio_hash' in fingerprint1 and 'audio_hash' in fingerprint2:
            if fingerprint1['audio_hash'] == fingerprint2['audio_hash']:
                return 1.0
        
        # Similarité basique basée sur les métadonnées communes
        common_fields = set(fingerprint1.keys()) & set(fingerprint2.keys())
        if not common_fields:
            return 0.0
        
        matches = sum(
            1 for field in common_fields
            if fingerprint1[field] == fingerprint2[field]
        )
        
        return matches / len(common_fields)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de la base de données"""        try:
            health_status = {
                'database': 'unknown',
                'cache': 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Test base de données
            try:
                async with self.get_session() as session:
                    await session.execute(text("SELECT 1"))
                health_status['database'] = 'healthy'
            except Exception as e:
                health_status['database'] = f'error: {str(e)}'
            
            # Test cache Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    health_status['cache'] = 'healthy'
                except Exception as e:
                    health_status['cache'] = f'error: {str(e)}'
            else:
                health_status['cache'] = 'disabled'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'database': f'error: {str(e)}',
                'cache': 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la base de données"""        try:
            async with self.get_session() as session:
                stats = {}
                
                # Comptages par table
                tables = [
                    ('content_metadata', ContentMetadata),
                    ('rights_holders', RightsHolder),
                    ('rights_records', RightsRecord),
                    ('license_agreements', LicenseAgreement),
                    ('usage_events', UsageEvent),
                    ('usage_reports', UsageReport),
                    ('royalty_calculations', RoyaltyCalculation),
                    ('payment_instructions', PaymentInstruction)
                ]
                
                for table_name, model_class in tables:
                    count = await session.query(func.count(model_class.id)).scalar()
                    stats[f'{table_name}_count'] = count
                
                # Statistiques temporelles
                now = datetime.utcnow()
                last_24h = now - timedelta(hours=24)
                last_7d = now - timedelta(days=7)
                
                # Nouveaux contenus
                new_content_24h = await session.query(func.count(ContentMetadata.id)).filter(
                    ContentMetadata.created_at >= last_24h
                ).scalar()
                
                new_content_7d = await session.query(func.count(ContentMetadata.id)).filter(
                    ContentMetadata.created_at >= last_7d
                ).scalar()
                
                # Nouveaux événements d'utilisation
                new_events_24h = await session.query(func.count(UsageEvent.id)).filter(
                    UsageEvent.detected_at >= last_24h
                ).scalar()
                
                new_events_7d = await session.query(func.count(UsageEvent.id)).filter(
                    UsageEvent.detected_at >= last_7d
                ).scalar()
                
                stats.update({
                    'new_content_24h': new_content_24h,
                    'new_content_7d': new_content_7d,
                    'new_events_24h': new_events_24h,
                    'new_events_7d': new_events_7d,
                    'generated_at': now.isoformat()
                })
                
                return stats
                
        except Exception as e:
            logger.error(f"Erreur statistiques base de données: {e}")
            return {'error': str(e)}
    
    async def cleanup_old_data(self, retention_days: int = 365):
        """Nettoie les anciennes données selon la politique de rétention"""        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            deleted_counts = {}
            
            async with self.get_session() as session:
                # Suppression des anciens événements d'utilisation
                old_events = await session.query(UsageEvent).filter(
                    UsageEvent.detected_at < cutoff_date
                ).count()
                
                if old_events > 0:
                    await session.query(UsageEvent).filter(
                        UsageEvent.detected_at < cutoff_date
                    ).delete()
                    deleted_counts['usage_events'] = old_events
                
                # Suppression des anciens rapports d'utilisation
                old_reports = await session.query(UsageReport).filter(
                    UsageReport.created_at < cutoff_date
                ).count()
                
                if old_reports > 0:
                    await session.query(UsageReport).filter(
                        UsageReport.created_at < cutoff_date
                    ).delete()
                    deleted_counts['usage_reports'] = old_reports
                
                logger.info(f"Nettoyage données anciennes: {deleted_counts}")
                return deleted_counts
                
        except Exception as e:
            logger.error(f"Erreur nettoyage données anciennes: {e}")
            return {}
    
    async def shutdown(self):
        """Arrêt propre du gestionnaire de base de données"""        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.engine:
                await self.engine.dispose()
            
            logger.info("Gestionnaire de base de données arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt gestionnaire base de données: {e}")


# Instance globale (singleton pattern)
database_manager: Optional[DatabaseManager] = None


async def get_database_manager(config: Optional[Dict[str, Any]] = None) -> DatabaseManager:
    """Récupère l'instance du gestionnaire de base de données"""    global database_manager
    
    if database_manager is None:
        if config is None:
            raise ValueError("Configuration requise pour initialiser le gestionnaire de base de données")
        
        database_manager = DatabaseManager(config)
        await database_manager.initialize()
    
    return database_manager


__all__ = [
    'DatabaseManager',
    'get_database_manager'
]
