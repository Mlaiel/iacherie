"""
API Error Translator - IA Chérie Platform
Multi-Platform API Error Translation & Normalization

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class APIErrorFormat(Enum):
    """Formats d'erreur API supportés"""
    JSON = "json"
    XML = "xml"
    PLAIN_TEXT = "plain_text"
    HTML = "html"
    CUSTOM = "custom"


class ErrorStandardization(Enum):
    """Standards de normalisation d'erreur"""
    RFC7807 = "rfc7807"  # Problem Details for HTTP APIs
    OAS3 = "openapi3"    # OpenAPI 3.0
    JSONAPI = "jsonapi"  # JSON:API Error Objects
    IACHERIE = "iacherie"  # IA Chérie Standard
    PLATFORM_NATIVE = "platform_native"


class TranslationStrategy(Enum):
    """Stratégies de traduction"""
    DIRECT_MAPPING = "direct_mapping"
    REGEX_PATTERN = "regex_pattern"
    ML_SEMANTIC = "ml_semantic"
    CONTEXTUAL = "contextual"
    HYBRID = "hybrid"


@dataclass
class APIErrorSource:
    """Source d'erreur API"""
    platform: str
    api_endpoint: str
    http_status_code: int
    response_format: APIErrorFormat
    raw_response: str
    headers: Dict[str, str]
    request_id: Optional[str]
    timestamp: datetime
    context: Dict[str, Any]


@dataclass
class TranslatedError:
    """Erreur traduite et normalisée"""
    translation_id: str
    source_error: APIErrorSource
    normalized_error: Dict[str, Any]
    error_standard: ErrorStandardization
    error_code: str
    error_title: str
    error_detail: str
    error_instance: str
    error_type: str
    translation_confidence: float
    localization: Dict[str, str]  # Multi-language support
    metadata: Dict[str, Any]
    suggested_actions: List[str]
    related_documentation: List[str]


@dataclass
class TranslationRule:
    """Règle de traduction d'erreur"""
    rule_id: str
    platform: str
    pattern: str
    pattern_type: str  # regex, json_path, xml_path
    target_error_code: str
    target_error_type: str
    confidence_score: float
    conditions: Dict[str, Any]
    transformations: List[Dict[str, Any]]
    priority: int
    active: bool


@dataclass
class PlatformAPISpec:
    """Spécification API d'une plateforme"""
    platform_id: str
    api_base_url: str
    api_version: str
    error_format: APIErrorFormat
    error_structure: Dict[str, Any]
    http_status_mapping: Dict[int, str]
    custom_error_codes: Dict[str, Dict[str, Any]]
    authentication_errors: List[str]
    rate_limit_errors: List[str]
    server_errors: List[str]
    localization_support: List[str]


class APIErrorTranslator:
    """
    🔄 Lead Dev IA + Backend Senior: Traducteur d'erreurs API multi-plateforme
    
    Système de traduction centralisé pour:
    - Normalisation cross-platform d'erreurs API
    - Support multi-format (JSON, XML, HTML, etc.)
    - Standardisation selon RFC7807, OpenAPI, JSON:API
    - Localisation multi-langue
    - ML-powered semantic translation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation du traducteur d'erreurs API"""
        self.config = config or {}
        
        # Translation components
        self.translation_rules: Dict[str, List[TranslationRule]] = defaultdict(list)
        self.platform_specs: Dict[str, PlatformAPISpec] = {}
        self.custom_translators: Dict[str, callable] = {}
        
        # Caching and history
        self.translation_cache: Dict[str, TranslatedError] = {}
        self.translation_history: deque = deque(maxlen=10000)
        
        # ML components
        self.semantic_analyzer = None
        self.pattern_detector = None
        
        # Localization support
        self.supported_languages = ['en', 'fr', 'de', 'es', 'ar']
        self.error_messages: Dict[str, Dict[str, str]] = {}
        
        # Metrics
        self.metrics = {
            'translations_performed': 0,
            'direct_mappings': 0,
            'regex_matches': 0,
            'ml_translations': 0,
            'cache_hits': 0,
            'translation_failures': 0,
            'average_confidence': 0.0
        }
        
        # Initialize components
        self._initialize_platform_specs()
        self._initialize_translation_rules()
        self._initialize_error_messages()
        
        logger.info("APIErrorTranslator initialized with multi-platform support")
    
    def _initialize_platform_specs(self):
        """🔧 Backend Senior: Initialisation des spécifications de plateformes"""
        
        # Spotify API specification
        self.platform_specs['spotify'] = PlatformAPISpec(
            platform_id='spotify',
            api_base_url='https://api.spotify.com/v1',
            api_version='v1',
            error_format=APIErrorFormat.JSON,
            error_structure={
                'error': {
                    'status': 'int',
                    'message': 'string'
                }
            },
            http_status_mapping={
                400: 'BAD_REQUEST',
                401: 'UNAUTHORIZED',
                403: 'FORBIDDEN', 
                404: 'NOT_FOUND',
                429: 'RATE_LIMITED',
                500: 'INTERNAL_ERROR',
                502: 'BAD_GATEWAY',
                503: 'SERVICE_UNAVAILABLE'
            },
            custom_error_codes={
                'NO_SUCH_USER': {'type': 'USER_ERROR', 'severity': 'medium'},
                'TRACK_NOT_PLAYABLE': {'type': 'CONTENT_ERROR', 'severity': 'low'},
                'PREMIUM_REQUIRED': {'type': 'SUBSCRIPTION_ERROR', 'severity': 'high'}
            },
            authentication_errors=['UNAUTHORIZED', 'TOKEN_EXPIRED', 'INVALID_CLIENT'],
            rate_limit_errors=['RATE_LIMITED', 'QUOTA_EXCEEDED'],
            server_errors=['INTERNAL_ERROR', 'SERVICE_UNAVAILABLE', 'BAD_GATEWAY'],
            localization_support=['en', 'fr', 'de', 'es']
        )
        
        # YouTube API specification
        self.platform_specs['youtube'] = PlatformAPISpec(
            platform_id='youtube',
            api_base_url='https://www.googleapis.com/youtube/v3',
            api_version='v3',
            error_format=APIErrorFormat.JSON,
            error_structure={
                'error': {
                    'code': 'int',
                    'message': 'string',
                    'errors': 'array',
                    'status': 'string'
                }
            },
            http_status_mapping={
                400: 'BAD_REQUEST',
                401: 'UNAUTHORIZED',
                403: 'FORBIDDEN',
                404: 'NOT_FOUND',
                409: 'CONFLICT',
                429: 'QUOTA_EXCEEDED',
                500: 'BACKEND_ERROR',
                503: 'SERVICE_UNAVAILABLE'
            },
            custom_error_codes={
                'videoNotFound': {'type': 'CONTENT_ERROR', 'severity': 'medium'},
                'quotaExceeded': {'type': 'QUOTA_ERROR', 'severity': 'high'},
                'uploadLimitExceeded': {'type': 'LIMIT_ERROR', 'severity': 'high'},
                'processingFailure': {'type': 'PROCESSING_ERROR', 'severity': 'high'}
            },
            authentication_errors=['UNAUTHORIZED', 'INVALID_CREDENTIALS', 'TOKEN_EXPIRED'],
            rate_limit_errors=['QUOTA_EXCEEDED', 'RATE_LIMIT_EXCEEDED'],
            server_errors=['BACKEND_ERROR', 'SERVICE_UNAVAILABLE', 'INTERNAL_ERROR'],
            localization_support=['en', 'fr', 'de', 'es', 'ar']
        )
        
        # Instagram API specification
        self.platform_specs['instagram'] = PlatformAPISpec(
            platform_id='instagram',
            api_base_url='https://graph.instagram.com',
            api_version='v12.0',
            error_format=APIErrorFormat.JSON,
            error_structure={
                'error': {
                    'message': 'string',
                    'type': 'string',
                    'code': 'int',
                    'error_subcode': 'int',
                    'fbtrace_id': 'string'
                }
            },
            http_status_mapping={
                400: 'BAD_REQUEST',
                401: 'UNAUTHORIZED',
                403: 'PERMISSION_DENIED',
                404: 'NOT_FOUND',
                429: 'RATE_LIMITED',
                500: 'INTERNAL_ERROR',
                503: 'SERVICE_UNAVAILABLE'
            },
            custom_error_codes={
                'OAuthException': {'type': 'AUTH_ERROR', 'severity': 'high'},
                'InvalidParameterException': {'type': 'PARAMETER_ERROR', 'severity': 'medium'},
                'MediaUploadException': {'type': 'UPLOAD_ERROR', 'severity': 'high'},
                'HashtagSpamException': {'type': 'POLICY_ERROR', 'severity': 'high'}
            },
            authentication_errors=['OAuthException', 'UNAUTHORIZED', 'INVALID_TOKEN'],
            rate_limit_errors=['RATE_LIMITED', 'API_LIMIT_REACHED'],
            server_errors=['INTERNAL_ERROR', 'SERVICE_UNAVAILABLE', 'FACEBOOK_API_ERROR'],
            localization_support=['en', 'fr', 'de', 'es']
        )
        
        # Patreon API specification
        self.platform_specs['patreon'] = PlatformAPISpec(
            platform_id='patreon',
            api_base_url='https://www.patreon.com/api/oauth2/v2',
            api_version='v2',
            error_format=APIErrorFormat.JSON,
            error_structure={
                'errors': [{
                    'code': 'string',
                    'code_name': 'string',
                    'detail': 'string',
                    'id': 'string',
                    'status': 'string',
                    'title': 'string'
                }]
            },
            http_status_mapping={
                400: 'BAD_REQUEST',
                401: 'UNAUTHORIZED',
                403: 'FORBIDDEN',
                404: 'NOT_FOUND',
                422: 'UNPROCESSABLE_ENTITY',
                429: 'TOO_MANY_REQUESTS',
                500: 'INTERNAL_SERVER_ERROR',
                503: 'SERVICE_UNAVAILABLE'
            },
            custom_error_codes={
                'invalid_grant': {'type': 'AUTH_ERROR', 'severity': 'high'},
                'payment_declined': {'type': 'PAYMENT_ERROR', 'severity': 'critical'},
                'tier_not_found': {'type': 'TIER_ERROR', 'severity': 'medium'},
                'pledge_limit_reached': {'type': 'LIMIT_ERROR', 'severity': 'high'}
            },
            authentication_errors=['UNAUTHORIZED', 'invalid_grant', 'TOKEN_EXPIRED'],
            rate_limit_errors=['TOO_MANY_REQUESTS', 'RATE_LIMIT'],
            server_errors=['INTERNAL_SERVER_ERROR', 'SERVICE_UNAVAILABLE', 'GATEWAY_ERROR'],
            localization_support=['en', 'fr', 'de']
        )
    
    def _initialize_translation_rules(self):
        """📋 Rules: Initialisation des règles de traduction"""
        
        # Spotify translation rules
        spotify_rules = [
            TranslationRule(
                rule_id='spotify_rate_limit',
                platform='spotify',
                pattern=r'"status":\s*429',
                pattern_type='regex',
                target_error_code='RATE_LIMIT_EXCEEDED',
                target_error_type='rate_limiting',
                confidence_score=0.95,
                conditions={'http_status': 429},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'Rate limit exceeded'}
                ],
                priority=1,
                active=True
            ),
            TranslationRule(
                rule_id='spotify_auth_error',
                platform='spotify',
                pattern=r'"status":\s*401',
                pattern_type='regex',
                target_error_code='AUTHENTICATION_FAILED',
                target_error_type='authentication',
                confidence_score=0.9,
                conditions={'http_status': 401},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'Authentication failed'}
                ],
                priority=1,
                active=True
            )
        ]
        self.translation_rules['spotify'] = spotify_rules
        
        # YouTube translation rules
        youtube_rules = [
            TranslationRule(
                rule_id='youtube_quota_exceeded',
                platform='youtube',
                pattern=r'"quotaExceeded"',
                pattern_type='regex',
                target_error_code='QUOTA_EXCEEDED',
                target_error_type='quota_limitation',
                confidence_score=0.95,
                conditions={'error_reason': 'quotaExceeded'},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'API quota exceeded'}
                ],
                priority=1,
                active=True
            ),
            TranslationRule(
                rule_id='youtube_video_not_found',
                platform='youtube',
                pattern=r'"videoNotFound"',
                pattern_type='regex',
                target_error_code='CONTENT_NOT_FOUND',
                target_error_type='content_error',
                confidence_score=0.9,
                conditions={'http_status': 404},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'Video not found'}
                ],
                priority=1,
                active=True
            )
        ]
        self.translation_rules['youtube'] = youtube_rules
        
        # Instagram translation rules
        instagram_rules = [
            TranslationRule(
                rule_id='instagram_oauth_exception',
                platform='instagram',
                pattern=r'"type":\s*"OAuthException"',
                pattern_type='regex',
                target_error_code='OAUTH_ERROR',
                target_error_type='authentication',
                confidence_score=0.95,
                conditions={'error_type': 'OAuthException'},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'OAuth authentication error'}
                ],
                priority=1,
                active=True
            ),
            TranslationRule(
                rule_id='instagram_media_upload_error',
                platform='instagram',
                pattern=r'"MediaUploadException"',
                pattern_type='regex',
                target_error_code='MEDIA_UPLOAD_FAILED',
                target_error_type='upload_error',
                confidence_score=0.9,
                conditions={'error_subcode': [1363030, 1363031, 1363032]},
                transformations=[
                    {'extract': 'error.message', 'target': 'detail'},
                    {'set': 'title', 'value': 'Media upload failed'}
                ],
                priority=1,
                active=True
            )
        ]
        self.translation_rules['instagram'] = instagram_rules
        
        # Patreon translation rules
        patreon_rules = [
            TranslationRule(
                rule_id='patreon_payment_declined',
                platform='patreon',
                pattern=r'"code_name":\s*"payment_declined"',
                pattern_type='regex',
                target_error_code='PAYMENT_DECLINED',
                target_error_type='payment_error',
                confidence_score=0.95,
                conditions={'code_name': 'payment_declined'},
                transformations=[
                    {'extract': 'errors[0].detail', 'target': 'detail'},
                    {'set': 'title', 'value': 'Payment declined'}
                ],
                priority=1,
                active=True
            ),
            TranslationRule(
                rule_id='patreon_invalid_grant',
                platform='patreon',
                pattern=r'"code_name":\s*"invalid_grant"',
                pattern_type='regex',
                target_error_code='INVALID_GRANT',
                target_error_type='authentication',
                confidence_score=0.9,
                conditions={'code_name': 'invalid_grant'},
                transformations=[
                    {'extract': 'errors[0].detail', 'target': 'detail'},
                    {'set': 'title', 'value': 'Invalid authorization grant'}
                ],
                priority=1,
                active=True
            )
        ]
        self.translation_rules['patreon'] = patreon_rules
    
    def _initialize_error_messages(self):
        """🌐 Localization: Initialisation des messages d'erreur multilingues"""
        
        self.error_messages = {
            'RATE_LIMIT_EXCEEDED': {
                'en': 'Rate limit exceeded. Please wait before making more requests.',
                'fr': 'Limite de taux dépassée. Veuillez attendre avant de faire plus de requêtes.',
                'de': 'Ratenlimit überschritten. Bitte warten Sie, bevor Sie weitere Anfragen stellen.',
                'es': 'Límite de velocidad excedido. Espere antes de hacer más solicitudes.',
                'ar': 'تم تجاوز حد المعدل. يرجى الانتظار قبل تقديم المزيد من الطلبات.'
            },
            'AUTHENTICATION_FAILED': {
                'en': 'Authentication failed. Please check your credentials.',
                'fr': 'Échec de l\'authentification. Veuillez vérifier vos identifiants.',
                'de': 'Authentifizierung fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldedaten.',
                'es': 'La autenticación falló. Verifique sus credenciales.',
                'ar': 'فشل في التحقق من الهوية. يرجى التحقق من بيانات الاعتماد الخاصة بك.'
            },
            'QUOTA_EXCEEDED': {
                'en': 'API quota exceeded. Please try again later or upgrade your plan.',
                'fr': 'Quota API dépassé. Veuillez réessayer plus tard ou mettre à niveau votre plan.',
                'de': 'API-Kontingent überschritten. Versuchen Sie es später erneut oder upgraden Sie Ihren Plan.',
                'es': 'Cuota de API excedida. Inténtelo de nuevo más tarde o actualice su plan.',
                'ar': 'تم تجاوز حصة واجهة برمجة التطبيقات. يرجى المحاولة مرة أخرى لاحقاً أو ترقية خطتك.'
            },
            'CONTENT_NOT_FOUND': {
                'en': 'The requested content was not found.',
                'fr': 'Le contenu demandé n\'a pas été trouvé.',
                'de': 'Der angeforderte Inhalt wurde nicht gefunden.',
                'es': 'El contenido solicitado no fue encontrado.',
                'ar': 'لم يتم العثور على المحتوى المطلوب.'
            },
            'PAYMENT_DECLINED': {
                'en': 'Payment was declined. Please check your payment method.',
                'fr': 'Le paiement a été refusé. Veuillez vérifier votre mode de paiement.',
                'de': 'Die Zahlung wurde abgelehnt. Bitte überprüfen Sie Ihre Zahlungsmethode.',
                'es': 'El pago fue rechazado. Verifique su método de pago.',
                'ar': 'تم رفض الدفع. يرجى التحقق من طريقة الدفع الخاصة بك.'
            },
            'MEDIA_UPLOAD_FAILED': {
                'en': 'Media upload failed. Please check file format and size.',
                'fr': 'Échec du téléchargement de média. Veuillez vérifier le format et la taille du fichier.',
                'de': 'Medien-Upload fehlgeschlagen. Bitte überprüfen Sie Dateiformat und -größe.',
                'es': 'Falló la carga de medios. Verifique el formato y tamaño del archivo.',
                'ar': 'فشل في تحميل الوسائط. يرجى التحقق من تنسيق الملف وحجمه.'
            }
        }
    
    async def translate_api_error(
        self,
        platform: str,
        raw_response: str,
        http_status_code: int,
        response_headers: Optional[Dict[str, str]] = None,
        api_endpoint: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None,
        target_language: str = 'en',
        target_standard: ErrorStandardization = ErrorStandardization.IACHERIE
    ) -> TranslatedError:
        """
        🔄 Lead Dev IA: Traduction principale d'erreur API
        
        Args:
            platform: Plateforme source
            raw_response: Réponse brute de l'API
            http_status_code: Code de statut HTTP
            response_headers: Headers de réponse
            api_endpoint: Endpoint API appelé
            request_context: Contexte de la requête
            target_language: Langue cible pour localisation
            target_standard: Standard de normalisation cible
            
        Returns:
            Erreur traduite et normalisée
        """
        try:
            # Création de la source d'erreur
            error_source = APIErrorSource(
                platform=platform,
                api_endpoint=api_endpoint or 'unknown',
                http_status_code=http_status_code,
                response_format=await self._detect_response_format(raw_response),
                raw_response=raw_response,
                headers=response_headers or {},
                request_id=response_headers.get('x-request-id') if response_headers else None,
                timestamp=datetime.now(),
                context=request_context or {}
            )
            
            # Vérification du cache
            cache_key = self._generate_cache_key(error_source)
            if cache_key in self.translation_cache:
                self.metrics['cache_hits'] += 1
                cached_translation = self.translation_cache[cache_key]
                # Update localization if different language requested
                if target_language != 'en':
                    cached_translation.localization = await self._localize_error(
                        cached_translation.error_code, target_language
                    )
                return cached_translation
            
            # Traduction de l'erreur
            translated_error = await self._perform_translation(
                error_source, target_language, target_standard
            )
            
            # Mise en cache
            self.translation_cache[cache_key] = translated_error
            self.translation_history.append(translated_error)
            
            # Mise à jour des métriques
            self.metrics['translations_performed'] += 1
            
            logger.info(f"Successfully translated {platform} API error: {translated_error.error_code}")
            return translated_error
            
        except Exception as e:
            logger.error(f"Error translating API error: {e}")
            
            # Fallback translation
            return await self._create_fallback_translation(
                platform, raw_response, http_status_code, target_language
            )
    
    async def _detect_response_format(self, raw_response: str) -> APIErrorFormat:
        """🔍 Detection: Détection du format de réponse"""
        
        stripped_response = raw_response.strip()
        
        # JSON detection
        if stripped_response.startswith(('{', '[')):
            try:
                json.loads(stripped_response)
                return APIErrorFormat.JSON
            except json.JSONDecodeError:
                pass
        
        # XML detection
        if stripped_response.startswith('<'):
            try:
                ET.fromstring(stripped_response)
                return APIErrorFormat.XML
            except ET.ParseError:
                pass
        
        # HTML detection
        if '<html' in stripped_response.lower() or '<!doctype html' in stripped_response.lower():
            return APIErrorFormat.HTML
        
        # Default to plain text
        return APIErrorFormat.PLAIN_TEXT
    
    async def _perform_translation(
        self,
        error_source: APIErrorSource,
        target_language: str,
        target_standard: ErrorStandardization
    ) -> TranslatedError:
        """🔄 Translation: Exécution de la traduction d'erreur"""
        
        # 1. Essayer la traduction par règles directes
        rule_translation = await self._translate_by_rules(error_source)
        if rule_translation and rule_translation.translation_confidence > 0.8:
            self.metrics['direct_mappings'] += 1
            return await self._finalize_translation(
                rule_translation, target_language, target_standard
            )
        
        # 2. Essayer la traduction par patterns regex
        regex_translation = await self._translate_by_regex(error_source)
        if regex_translation and regex_translation.translation_confidence > 0.7:
            self.metrics['regex_matches'] += 1
            return await self._finalize_translation(
                regex_translation, target_language, target_standard
            )
        
        # 3. Essayer la traduction ML sémantique
        if self.semantic_analyzer:
            ml_translation = await self._translate_by_ml(error_source)
            if ml_translation and ml_translation.translation_confidence > 0.6:
                self.metrics['ml_translations'] += 1
                return await self._finalize_translation(
                    ml_translation, target_language, target_standard
                )
        
        # 4. Traduction contextuelle basique
        contextual_translation = await self._translate_contextual(error_source)
        return await self._finalize_translation(
            contextual_translation, target_language, target_standard
        )
    
    async def _translate_by_rules(self, error_source: APIErrorSource) -> Optional[TranslatedError]:
        """📋 Rules: Traduction par règles directes"""
        
        platform_rules = self.translation_rules.get(error_source.platform, [])
        
        for rule in sorted(platform_rules, key=lambda r: r.priority):
            if not rule.active:
                continue
            
            # Vérification des conditions
            if not await self._check_rule_conditions(rule, error_source):
                continue
            
            # Application de la règle
            try:
                translated_error = await self._apply_translation_rule(rule, error_source)
                if translated_error:
                    return translated_error
            except Exception as e:
                logger.warning(f"Error applying rule {rule.rule_id}: {e}")
        
        return None
    
    async def _check_rule_conditions(self, rule: TranslationRule, error_source: APIErrorSource) -> bool:
        """✅ Validation: Vérification des conditions de règle"""
        
        conditions = rule.conditions
        
        # HTTP status condition
        if 'http_status' in conditions:
            if error_source.http_status_code != conditions['http_status']:
                return False
        
        # Pattern matching condition
        if rule.pattern_type == 'regex':
            if not re.search(rule.pattern, error_source.raw_response, re.IGNORECASE):
                return False
        elif rule.pattern_type == 'json_path':
            try:
                error_data = json.loads(error_source.raw_response)
                if not self._check_json_path(error_data, rule.pattern):
                    return False
            except json.JSONDecodeError:
                return False
        
        # Additional custom conditions
        for condition_key, condition_value in conditions.items():
            if condition_key in ['http_status']:
                continue  # Already checked
            
            # Context-based conditions
            if condition_key in error_source.context:
                context_value = error_source.context[condition_key]
                if isinstance(condition_value, list):
                    if context_value not in condition_value:
                        return False
                elif context_value != condition_value:
                    return False
        
        return True
    
    async def _apply_translation_rule(self, rule: TranslationRule, error_source: APIErrorSource) -> TranslatedError:
        """🔧 Application: Application d'une règle de traduction"""
        
        # Parse source error
        parsed_error = await self._parse_error_response(error_source)
        
        # Apply transformations
        normalized_error = {}
        for transformation in rule.transformations:
            await self._apply_transformation(transformation, parsed_error, normalized_error)
        
        # Set required fields
        normalized_error.setdefault('type', rule.target_error_type)
        normalized_error.setdefault('code', rule.target_error_code)
        normalized_error.setdefault('status', str(error_source.http_status_code))
        
        # Generate translation ID
        translation_id = f"rule_{rule.rule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TranslatedError(
            translation_id=translation_id,
            source_error=error_source,
            normalized_error=normalized_error,
            error_standard=ErrorStandardization.IACHERIE,
            error_code=rule.target_error_code,
            error_title=normalized_error.get('title', rule.target_error_code),
            error_detail=normalized_error.get('detail', 'Error occurred'),
            error_instance=f"/errors/{translation_id}",
            error_type=rule.target_error_type,
            translation_confidence=rule.confidence_score,
            localization={},  # Will be filled later
            metadata={
                'rule_id': rule.rule_id,
                'platform': error_source.platform,
                'translation_method': 'rule_based'
            },
            suggested_actions=await self._generate_suggested_actions(rule.target_error_code),
            related_documentation=await self._get_documentation_links(rule.target_error_code)
        )
    
    async def _parse_error_response(self, error_source: APIErrorSource) -> Dict[str, Any]:
        """📖 Parsing: Analyse de la réponse d'erreur"""
        
        if error_source.response_format == APIErrorFormat.JSON:
            try:
                return json.loads(error_source.raw_response)
            except json.JSONDecodeError:
                return {'raw_message': error_source.raw_response}
        
        elif error_source.response_format == APIErrorFormat.XML:
            try:
                root = ET.fromstring(error_source.raw_response)
                return self._xml_to_dict(root)
            except ET.ParseError:
                return {'raw_message': error_source.raw_response}
        
        elif error_source.response_format == APIErrorFormat.HTML:
            # Extract error information from HTML
            error_patterns = [
                r'<title>(.*?)</title>',
                r'<h1>(.*?)</h1>',
                r'<p[^>]*error[^>]*>(.*?)</p>',
                r'<div[^>]*error[^>]*>(.*?)</div>'
            ]
            
            extracted_info = {}
            for pattern in error_patterns:
                matches = re.findall(pattern, error_source.raw_response, re.IGNORECASE | re.DOTALL)
                if matches:
                    extracted_info['error_message'] = matches[0].strip()
                    break
            
            return extracted_info or {'raw_message': error_source.raw_response}
        
        else:
            # Plain text
            return {'raw_message': error_source.raw_response}
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """🔄 XML: Conversion XML vers dictionnaire"""
        
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    async def _apply_transformation(
        self, 
        transformation: Dict[str, Any], 
        source_data: Dict[str, Any], 
        target_data: Dict[str, Any]
    ):
        """🔧 Transform: Application d'une transformation"""
        
        if 'extract' in transformation:
            # Extract value from source using JSON path
            source_path = transformation['extract']
            target_field = transformation['target']
            
            extracted_value = self._get_nested_value(source_data, source_path)
            if extracted_value:
                target_data[target_field] = extracted_value
        
        elif 'set' in transformation:
            # Set static value
            target_field = transformation['set']
            value = transformation['value']
            target_data[target_field] = value
        
        elif 'map' in transformation:
            # Map value using mapping table
            source_field = transformation['map']['source']
            mapping_table = transformation['map']['mapping']
            target_field = transformation['map']['target']
            
            source_value = self._get_nested_value(source_data, source_field)
            if source_value in mapping_table:
                target_data[target_field] = mapping_table[source_value]
        
        elif 'format' in transformation:
            # Format string template
            template = transformation['format']['template']
            fields = transformation['format']['fields']
            target_field = transformation['format']['target']
            
            format_values = {}
            for field in fields:
                format_values[field] = self._get_nested_value(source_data, field) or ''
            
            try:
                formatted_value = template.format(**format_values)
                target_data[target_field] = formatted_value
            except KeyError:
                pass  # Skip if formatting fails
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """🔍 Path: Récupération de valeur par chemin JSON"""
        
        try:
            keys = path.split('.')
            current = data
            
            for key in keys:
                if '[' in key and ']' in key:
                    # Array access: key[index]
                    array_key, index_part = key.split('[', 1)
                    index = int(index_part.rstrip(']'))
                    current = current[array_key][index]
                else:
                    current = current[key]
            
            return current
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    async def _translate_by_regex(self, error_source: APIErrorSource) -> Optional[TranslatedError]:
        """🔍 Regex: Traduction par patterns regex"""
        
        # Get platform spec
        platform_spec = self.platform_specs.get(error_source.platform)
        if not platform_spec:
            return None
        
        # Common error patterns
        error_patterns = {
            'rate_limit': [
                r'rate.*limit.*exceeded',
                r'too.*many.*requests',
                r'quota.*exceeded',
                r'429',
                r'throttle'
            ],
            'authentication': [
                r'unauthorized',
                r'authentication.*failed',
                r'invalid.*token',
                r'access.*denied',
                r'401'
            ],
            'not_found': [
                r'not.*found',
                r'does.*not.*exist',
                r'404',
                r'resource.*unavailable'
            ],
            'server_error': [
                r'internal.*server.*error',
                r'service.*unavailable',
                r'server.*error',
                r'5\d{2}'
            ],
            'bad_request': [
                r'bad.*request',
                r'invalid.*parameter',
                r'malformed.*request',
                r'400'
            ]
        }
        
        response_lower = error_source.raw_response.lower()
        
        for error_type, patterns in error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response_lower):
                    return await self._create_regex_translation(
                        error_source, error_type, pattern, 0.7
                    )
        
        return None
    
    async def _create_regex_translation(
        self,
        error_source: APIErrorSource,
        error_type: str,
        matched_pattern: str,
        confidence: float
    ) -> TranslatedError:
        """🔧 Regex Creation: Création de traduction basée sur regex"""
        
        # Map error types to codes
        error_code_mapping = {
            'rate_limit': 'RATE_LIMIT_EXCEEDED',
            'authentication': 'AUTHENTICATION_FAILED',
            'not_found': 'RESOURCE_NOT_FOUND',
            'server_error': 'SERVER_ERROR',
            'bad_request': 'BAD_REQUEST'
        }
        
        error_code = error_code_mapping.get(error_type, 'UNKNOWN_ERROR')
        
        # Generate basic normalized error
        normalized_error = {
            'type': error_type,
            'code': error_code,
            'status': str(error_source.http_status_code),
            'title': error_code.replace('_', ' ').title(),
            'detail': f"Pattern '{matched_pattern}' matched in response"
        }
        
        translation_id = f"regex_{error_source.platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TranslatedError(
            translation_id=translation_id,
            source_error=error_source,
            normalized_error=normalized_error,
            error_standard=ErrorStandardization.IACHERIE,
            error_code=error_code,
            error_title=normalized_error['title'],
            error_detail=normalized_error['detail'],
            error_instance=f"/errors/{translation_id}",
            error_type=error_type,
            translation_confidence=confidence,
            localization={},
            metadata={
                'matched_pattern': matched_pattern,
                'platform': error_source.platform,
                'translation_method': 'regex_pattern'
            },
            suggested_actions=await self._generate_suggested_actions(error_code),
            related_documentation=await self._get_documentation_links(error_code)
        )
    
    async def _translate_by_ml(self, error_source: APIErrorSource) -> Optional[TranslatedError]:
        """🤖 ML: Traduction par machine learning sémantique"""
        
        # This would integrate with ML models for semantic error classification
        # For now, return None to indicate ML translation is not available
        return None
    
    async def _translate_contextual(self, error_source: APIErrorSource) -> TranslatedError:
        """🎯 Contextual: Traduction contextuelle basique"""
        
        # Basic contextual translation based on HTTP status and platform
        error_code = f"HTTP_{error_source.http_status_code}"
        error_type = "http_error"
        
        # Improve classification based on HTTP status
        if error_source.http_status_code == 401:
            error_code = "AUTHENTICATION_REQUIRED"
            error_type = "authentication"
        elif error_source.http_status_code == 403:
            error_code = "ACCESS_FORBIDDEN"
            error_type = "authorization"
        elif error_source.http_status_code == 404:
            error_code = "RESOURCE_NOT_FOUND"
            error_type = "not_found"
        elif error_source.http_status_code == 429:
            error_code = "RATE_LIMIT_EXCEEDED"
            error_type = "rate_limiting"
        elif 500 <= error_source.http_status_code < 600:
            error_code = "SERVER_ERROR"
            error_type = "server_error"
        
        normalized_error = {
            'type': error_type,
            'code': error_code,
            'status': str(error_source.http_status_code),
            'title': error_code.replace('_', ' ').title(),
            'detail': f"HTTP {error_source.http_status_code} error from {error_source.platform}"
        }
        
        translation_id = f"contextual_{error_source.platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TranslatedError(
            translation_id=translation_id,
            source_error=error_source,
            normalized_error=normalized_error,
            error_standard=ErrorStandardization.IACHERIE,
            error_code=error_code,
            error_title=normalized_error['title'],
            error_detail=normalized_error['detail'],
            error_instance=f"/errors/{translation_id}",
            error_type=error_type,
            translation_confidence=0.5,  # Lower confidence for contextual
            localization={},
            metadata={
                'platform': error_source.platform,
                'translation_method': 'contextual'
            },
            suggested_actions=await self._generate_suggested_actions(error_code),
            related_documentation=await self._get_documentation_links(error_code)
        )
    
    async def _finalize_translation(
        self,
        translated_error: TranslatedError,
        target_language: str,
        target_standard: ErrorStandardization
    ) -> TranslatedError:
        """✨ Finalization: Finalisation de la traduction"""
        
        # Apply localization
        translated_error.localization = await self._localize_error(
            translated_error.error_code, target_language
        )
        
        # Apply target standard formatting
        if target_standard != ErrorStandardization.IACHERIE:
            translated_error.normalized_error = await self._apply_error_standard(
                translated_error.normalized_error, target_standard
            )
            translated_error.error_standard = target_standard
        
        return translated_error
    
    async def _localize_error(self, error_code: str, target_language: str) -> Dict[str, str]:
        """🌐 Localization: Localisation de l'erreur"""
        
        localization = {}
        
        if error_code in self.error_messages:
            messages = self.error_messages[error_code]
            localization['message'] = messages.get(target_language, messages.get('en', ''))
        
        # Add language-specific formatting
        localization['language'] = target_language
        localization['locale'] = f"{target_language}_US"  # Default locale
        
        return localization
    
    async def _apply_error_standard(
        self, 
        normalized_error: Dict[str, Any], 
        target_standard: ErrorStandardization
    ) -> Dict[str, Any]:
        """📝 Standards: Application du standard d'erreur cible"""
        
        if target_standard == ErrorStandardization.RFC7807:
            # RFC 7807 Problem Details format
            return {
                'type': f"https://api.iacherie.com/errors/{normalized_error.get('type', 'unknown')}",
                'title': normalized_error.get('title', 'Error'),
                'status': int(normalized_error.get('status', 500)),
                'detail': normalized_error.get('detail', ''),
                'instance': normalized_error.get('instance', '')
            }
        
        elif target_standard == ErrorStandardization.JSONAPI:
            # JSON:API Error Objects format
            return {
                'errors': [{
                    'id': normalized_error.get('id', ''),
                    'status': normalized_error.get('status', '500'),
                    'code': normalized_error.get('code', 'UNKNOWN'),
                    'title': normalized_error.get('title', 'Error'),
                    'detail': normalized_error.get('detail', ''),
                    'source': {
                        'pointer': '/data'
                    }
                }]
            }
        
        elif target_standard == ErrorStandardization.OAS3:
            # OpenAPI 3.0 Error format
            return {
                'error': {
                    'code': normalized_error.get('code', 'UNKNOWN'),
                    'message': normalized_error.get('detail', 'Error occurred'),
                    'details': normalized_error.get('details', {})
                }
            }
        
        # Default: return as-is for IACHERIE or PLATFORM_NATIVE
        return normalized_error
    
    async def _generate_suggested_actions(self, error_code: str) -> List[str]:
        """💡 Actions: Génération d'actions suggérées"""
        
        action_mapping = {
            'RATE_LIMIT_EXCEEDED': [
                'Wait before making additional requests',
                'Implement exponential backoff',
                'Consider upgrading API plan for higher limits',
                'Optimize request frequency'
            ],
            'AUTHENTICATION_FAILED': [
                'Check API credentials',
                'Refresh authentication token',
                'Verify API key permissions',
                'Review authentication documentation'
            ],
            'QUOTA_EXCEEDED': [
                'Wait for quota reset',
                'Upgrade to higher quota plan',
                'Optimize API usage',
                'Implement request batching'
            ],
            'PAYMENT_DECLINED': [
                'Verify payment method',
                'Check account balance',
                'Contact payment provider',
                'Update billing information'
            ],
            'RESOURCE_NOT_FOUND': [
                'Check resource ID',
                'Verify resource exists',
                'Review API endpoint',
                'Check access permissions'
            ]
        }
        
        return action_mapping.get(error_code, [
            'Check API documentation',
            'Verify request parameters',
            'Contact support if issue persists'
        ])
    
    async def _get_documentation_links(self, error_code: str) -> List[str]:
        """📚 Documentation: Liens vers documentation"""
        
        base_url = "https://docs.iacherie.com/errors"
        
        return [
            f"{base_url}/{error_code.lower()}",
            f"{base_url}/troubleshooting",
            f"{base_url}/best-practices"
        ]
    
    async def _create_fallback_translation(
        self,
        platform: str,
        raw_response: str,
        http_status_code: int,
        target_language: str
    ) -> TranslatedError:
        """🔄 Fallback: Traduction de secours"""
        
        error_source = APIErrorSource(
            platform=platform,
            api_endpoint='unknown',
            http_status_code=http_status_code,
            response_format=APIErrorFormat.PLAIN_TEXT,
            raw_response=raw_response,
            headers={},
            request_id=None,
            timestamp=datetime.now(),
            context={}
        )
        
        normalized_error = {
            'type': 'translation_error',
            'code': 'TRANSLATION_FAILED',
            'status': str(http_status_code),
            'title': 'Error Translation Failed',
            'detail': f'Failed to translate error from {platform}'
        }
        
        translation_id = f"fallback_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TranslatedError(
            translation_id=translation_id,
            source_error=error_source,
            normalized_error=normalized_error,
            error_standard=ErrorStandardization.IACHERIE,
            error_code='TRANSLATION_FAILED',
            error_title='Error Translation Failed',
            error_detail=f'Failed to translate error from {platform}',
            error_instance=f"/errors/{translation_id}",
            error_type='translation_error',
            translation_confidence=0.1,
            localization=await self._localize_error('TRANSLATION_FAILED', target_language),
            metadata={
                'platform': platform,
                'translation_method': 'fallback',
                'original_status': http_status_code
            },
            suggested_actions=['Contact support', 'Check platform documentation'],
            related_documentation=[f"https://docs.iacherie.com/platforms/{platform}"]
        )
    
    def _generate_cache_key(self, error_source: APIErrorSource) -> str:
        """🔑 Cache: Génération de clé de cache"""
        
        cache_data = {
            'platform': error_source.platform,
            'http_status': error_source.http_status_code,
            'response_hash': hashlib.md5(error_source.raw_response.encode()).hexdigest()[:16]
        }
        
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _check_json_path(self, data: Dict[str, Any], path: str) -> bool:
        """✅ JSON Path: Vérification d'existence d'un chemin JSON"""
        
        try:
            self._get_nested_value(data, path)
            return True
        except:
            return False
    
    async def get_translation_analytics(self) -> Dict[str, Any]:
        """
        📊 Analytics: Analytics complets du traducteur
        
        Returns:
            Analytics détaillés avec métriques
        """
        try:
            # Platform distribution
            platform_distribution = {}
            for translation in self.translation_history:
                platform = translation.source_error.platform
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            # Translation method distribution
            method_distribution = {}
            for translation in self.translation_history:
                method = translation.metadata.get('translation_method', 'unknown')
                method_distribution[method] = method_distribution.get(method, 0) + 1
            
            # Error code distribution
            error_code_distribution = {}
            for translation in self.translation_history:
                code = translation.error_code
                error_code_distribution[code] = error_code_distribution.get(code, 0) + 1
            
            # Average confidence calculation
            confidences = [t.translation_confidence for t in self.translation_history]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            self.metrics['average_confidence'] = avg_confidence
            
            return {
                'timestamp': datetime.now().isoformat(),
                'translator_status': {
                    'platforms_configured': len(self.platform_specs),
                    'translation_rules': sum(len(rules) for rules in self.translation_rules.values()),
                    'supported_languages': len(self.supported_languages),
                    'cache_size': len(self.translation_cache),
                    'history_size': len(self.translation_history)
                },
                'metrics': self.metrics,
                'distributions': {
                    'by_platform': platform_distribution,
                    'by_method': method_distribution,
                    'by_error_code': error_code_distribution
                },
                'supported_platforms': list(self.platform_specs.keys()),
                'supported_formats': [format.value for format in APIErrorFormat],
                'supported_standards': [standard.value for standard in ErrorStandardization],
                'supported_languages': self.supported_languages,
                'capabilities': {
                    'rule_based_translation': True,
                    'regex_pattern_matching': True,
                    'contextual_translation': True,
                    'multi_language_support': True,
                    'error_standardization': True,
                    'caching': True,
                    'fallback_translation': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating translation analytics: {e}")
            return {'error': 'Failed to generate analytics', 'timestamp': datetime.now().isoformat()}


# Instance globale pour utilisation
api_error_translator = APIErrorTranslator()

# Export des classes principales
__all__ = [
    'APIErrorTranslator',
    'APIErrorSource',
    'TranslatedError',
    'TranslationRule',
    'PlatformAPISpec',
    'APIErrorFormat',
    'ErrorStandardization',
    'TranslationStrategy',
    'api_error_translator'
]