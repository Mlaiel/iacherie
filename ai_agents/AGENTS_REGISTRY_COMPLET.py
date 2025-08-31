#!/usr/bin/env python3
"""
Agent Registry Update Script
Met à jour le registre des agents selon l'état réel du système

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

# REGISTRE COMPLET DES AGENTS EXISTANTS - État Réel du 13 Août 2025

EXISTING_AGENTS_REGISTRY = {
    # ═══════════════════════════════════════════════════════════════
    # AGENTS CORE BUSINESS (Critiques pour le métier)
    # ═══════════════════════════════════════════════════════════════
    
    # 🎯 Content & Protection (Cœur de métier)
    'content_agent': {
        'path': '/backend/ai_agents/content_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'core_business',
        'description': 'Analyse et traitement contenu multi-format',
        'features': ['content_analysis', 'metadata_extraction', 'format_detection'],
        'dependencies': ['storage_agent', 'vector_agent']
    },
    
    'protection_agent': {
        'path': '/backend/ai_agents/protection_agent/',
        'status': 'active', 
        'priority': 'critical',
        'category': 'core_business',
        'description': 'Protection droits auteur et lutte anti-piratage',
        'features': ['copyright_protection', 'piracy_detection', 'legal_docs'],
        'dependencies': ['fingerprinting_agent', 'dmca_agent', 'legal_agent']
    },
    
    'fingerprinting_agent': {
        'path': '/backend/ai_agents/fingerprinting_agent/',
        'status': 'active',
        'priority': 'critical', 
        'category': 'core_business',
        'description': 'Empreintes digitales multi-format (audio/video/image/text)',
        'features': ['audio_fingerprint', 'video_fingerprint', 'image_fingerprint', 'text_fingerprint'],
        'dependencies': ['audio_agent', 'video_agent', 'image_agent', 'text_agent']
    },
    
    'collaboration_agent': {
        'path': '/backend/ai_agents/collaboration_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'core_business', 
        'description': 'Matching intelligent entre créateurs',
        'features': ['creator_matching', 'compatibility_analysis', 'project_coordination'],
        'dependencies': ['analytics_agent', 'ml_agent', 'vector_agent']
    },
    
    'monetization_agent': {
        'path': '/backend/ai_agents/monetization_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'core_business',
        'description': 'Stratégies monétisation intelligente',
        'features': ['revenue_optimization', 'pricing_engine', 'royalty_calculation'],
        'dependencies': ['payment_processing_agent', 'revenue_agent', 'analytics_agent']
    },
    
    'distribution_agent': {
        'path': '/backend/ai_agents/distribution_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'core_business',
        'description': 'Distribution multi-plateformes automatisée',
        'features': ['multi_platform_upload', 'scheduling', 'optimization'],
        'dependencies': ['social_media_agent', 'platform_agent', 'scheduling_agent']
    },
    
    'seo_agent': {
        'path': '/backend/ai_agents/seo_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'core_business',
        'description': 'Optimisation SEO professionnelle',
        'features': ['keyword_optimization', 'meta_generation', 'ranking_analysis'],
        'dependencies': ['nlp_agent', 'analytics_agent', 'trend_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS TRAITEMENT MÉDIA (Spécialisés par format)
    # ═══════════════════════════════════════════════════════════════
    
    'audio_agent': {
        'path': '/backend/ai_agents/audio_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'media_processing',
        'description': 'Traitement audio avancé et analyse acoustique',
        'features': ['audio_processing', 'noise_reduction', 'format_conversion', 'quality_enhancement'],
        'dependencies': ['music_agent', 'ml_agent']
    },
    
    'music_agent': {
        'path': '/backend/ai_agents/music_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'media_processing',
        'description': 'Analyse musicale et composition IA',
        'features': ['music_analysis', 'genre_classification', 'composition_ai', 'harmony_detection'],
        'dependencies': ['audio_agent', 'ml_agent', 'nlp_agent']
    },
    
    'video_agent': {
        'path': '/backend/ai_agents/video_agent/',
        'status': 'active',
        'priority': 'high', 
        'category': 'media_processing',
        'description': 'Traitement vidéo et analyse visuelle',
        'features': ['video_processing', 'scene_detection', 'object_tracking', 'compression'],
        'dependencies': ['vision_agent', 'image_agent', 'ml_agent']
    },
    
    'image_agent': {
        'path': '/backend/ai_agents/image_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'media_processing', 
        'description': 'Traitement image et reconnaissance visuelle',
        'features': ['image_processing', 'object_detection', 'style_analysis', 'enhancement'],
        'dependencies': ['vision_agent', 'ml_agent']
    },
    
    'text_agent': {
        'path': '/backend/ai_agents/text_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'media_processing',
        'description': 'Traitement texte avancé',
        'features': ['text_processing', 'language_detection', 'translation', 'summarization'],
        'dependencies': ['nlp_agent', 'ml_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS IA AVANCÉS (Machine Learning & Analyse)
    # ═══════════════════════════════════════════════════════════════
    
    'ml_agent': {
        'path': '/backend/ai_agents/ml_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'ai_advanced',
        'description': 'Machine Learning et IA générale',
        'features': ['model_training', 'inference_engine', 'model_registry', 'auto_ml'],
        'dependencies': ['vector_agent', 'analytics_agent']
    },
    
    'nlp_agent': {
        'path': '/backend/ai_agents/nlp_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'ai_advanced',
        'description': 'Traitement langage naturel avancé',
        'features': ['text_analysis', 'sentiment_analysis', 'entity_extraction', 'language_detection'],
        'dependencies': ['ml_agent', 'text_agent']
    },
    
    'vision_agent': {
        'path': '/backend/ai_agents/vision_agent/',
        'status': 'active',
        'priority': 'high', 
        'category': 'ai_advanced',
        'description': 'Vision par ordinateur',
        'features': ['image_recognition', 'object_detection', 'facial_recognition', 'scene_analysis'],
        'dependencies': ['ml_agent', 'image_agent']
    },
    
    'vector_agent': {
        'path': '/backend/ai_agents/vector_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'ai_advanced',
        'description': 'Recherche vectorielle et embeddings IA',
        'features': ['vector_search', 'embeddings_generation', 'similarity_calculation', 'indexing'],
        'dependencies': ['ml_agent']
    },
    
    'intelligence_agent': {
        'path': '/backend/ai_agents/intelligence_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'ai_advanced',
        'description': 'Intelligence artificielle centrale et prise de décision',
        'features': ['decision_engine', 'context_analysis', 'strategy_optimization', 'reasoning'],
        'dependencies': ['ml_agent', 'analytics_agent', 'vector_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS PLATEFORMES & INTÉGRATIONS
    # ═══════════════════════════════════════════════════════════════
    
    'platform_agent': {
        'path': '/backend/ai_agents/platform_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'platform_integration',
        'description': 'Intégrations plateformes génériques',
        'features': ['api_integration', 'platform_management', 'data_sync'],
        'dependencies': ['social_media_agent', 'api_gateway_agent']
    },
    
    'social_media_agent': {
        'path': '/backend/ai_agents/social_media_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'platform_integration',
        'description': 'Intégrations réseaux sociaux multi-plateformes',
        'features': ['multi_platform_posting', 'engagement_tracking', 'social_analytics'],
        'dependencies': ['api_gateway_agent', 'analytics_agent']
    },
    
    'spotify_agent': {
        'path': '/backend/ai_agents/spotify_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'platform_integration',
        'description': 'Intégration Spotify complète',
        'features': ['spotify_upload', 'playlist_management', 'streaming_analytics'],
        'dependencies': ['music_agent', 'audio_agent', 'platform_agent']
    },
    
    'webhook_agent': {
        'path': '/backend/ai_agents/webhook_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'platform_integration', 
        'description': 'Gestion webhooks et intégrations temps réel',
        'features': ['webhook_management', 'event_processing', 'real_time_sync'],
        'dependencies': ['api_gateway_agent', 'notification_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS ANALYTICS & MONITORING
    # ═══════════════════════════════════════════════════════════════
    
    'analytics_agent': {
        'path': '/backend/ai_agents/analytics_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'analytics_monitoring',
        'description': 'Analytics avancés et KPIs business',
        'features': ['metrics_collection', 'report_generation', 'trend_analysis', 'kpi_tracking'],
        'dependencies': ['ml_agent', 'vector_agent']
    },
    
    'predictive_analytics_agent': {
        'path': '/backend/ai_agents/predictive_analytics_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'analytics_monitoring',
        'description': 'Analyses prédictives et forecasting',
        'features': ['predictive_modeling', 'forecast_engine', 'trend_prediction'],
        'dependencies': ['ml_agent', 'analytics_agent']
    },
    
    'market_intelligence_agent': {
        'path': '/backend/ai_agents/market_intelligence_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'analytics_monitoring',
        'description': 'Intelligence marché et veille concurrentielle',
        'features': ['market_analysis', 'competitor_tracking', 'opportunity_detection'],
        'dependencies': ['analytics_agent', 'competitor_monitoring_agent', 'crawling_agent']
    },
    
    'competitor_monitoring_agent': {
        'path': '/backend/ai_agents/competitor_monitoring_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'analytics_monitoring',
        'description': 'Surveillance concurrentielle automatisée',
        'features': ['competitor_tracking', 'market_analysis', 'alert_system'],
        'dependencies': ['crawling_agent', 'analytics_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS SÉCURITÉ & COMPLIANCE
    # ═══════════════════════════════════════════════════════════════
    
    'compliance_agent': {
        'path': '/backend/ai_agents/compliance_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Conformité réglementaire générale',
        'features': ['compliance_checking', 'regulation_monitoring', 'audit_trails'],
        'dependencies': ['legal_agent', 'audit_trail_agent']
    },
    
    'gdpr_compliance_agent': {
        'path': '/backend/ai_agents/gdpr_compliance_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Conformité GDPR et protection données',
        'features': ['gdpr_compliance', 'data_protection', 'consent_management', 'privacy_audit'],
        'dependencies': ['compliance_agent', 'audit_trail_agent']
    },
    
    'dmca_agent': {
        'path': '/backend/ai_agents/dmca_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Gestion DMCA et takedowns automatisés',
        'features': ['dmca_management', 'takedown_processing', 'legal_document_generation'],
        'dependencies': ['legal_agent', 'protection_agent']
    },
    
    'legal_agent': {
        'path': '/backend/ai_agents/legal_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'security_compliance',
        'description': 'Assistance légale et génération contrats',
        'features': ['contract_generation', 'legal_research', 'compliance_checking'],
        'dependencies': ['nlp_agent', 'compliance_agent']
    },
    
    'fraud_detection_agent': {
        'path': '/backend/ai_agents/fraud_detection_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'security_compliance',
        'description': 'Détection fraude et analyse comportementale',
        'features': ['fraud_detection', 'behavioral_analysis', 'risk_assessment'],
        'dependencies': ['ml_agent', 'analytics_agent']
    },
    
    'audit_trail_agent': {
        'path': '/backend/ai_agents/audit_trail_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'security_compliance',
        'description': 'Audit et traçabilité complète',
        'features': ['audit_logging', 'compliance_tracking', 'activity_monitoring'],
        'dependencies': ['compliance_agent']
    },
    
    'content_protection_agent': {
        'path': '/backend/ai_agents/content_protection_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Protection contenu multi-plateforme (35+ plateformes)',
        'features': ['multi_platform_monitoring', 'fingerprint_matching', 'real_time_alerts', 'dmca_automation'],
        'dependencies': ['fingerprinting_agent', 'dmca_agent', 'blockchain_agent']
    },
    
    'piracy_detection_agent': {
        'path': '/backend/ai_agents/piracy_detection_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Détection piratage deep web et monitoring torrent',
        'features': ['deep_web_scanning', 'torrent_monitoring', 'streaming_detection', 'forensic_collection'],
        'dependencies': ['protection_agent', 'fraud_detection_agent', 'legal_agent']
    },
    
    'rights_management_agent': {
        'path': '/backend/ai_agents/rights_management_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'security_compliance',
        'description': 'Gestion droits globale et calcul royalties',
        'features': ['ownership_registry', 'license_management', 'royalty_calculation', 'revenue_optimization'],
        'dependencies': ['legal_agent', 'monetization_agent', 'blockchain_agent']
    },
    
    'violation_scoring_agent': {
        'path': '/backend/ai_agents/violation_scoring_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'security_compliance',
        'description': 'Scoring IA violations et recommandations automatiques',
        'features': ['ai_violation_scoring', 'pattern_analysis', 'risk_assessment', 'action_recommendations'],
        'dependencies': ['ml_agent', 'protection_agent', 'analytics_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS BUSINESS & REVENUE  
    # ═══════════════════════════════════════════════════════════════
    
    'revenue_agent': {
        'path': '/backend/ai_agents/revenue_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'business_revenue',
        'description': 'Optimisation revenus et analytics financiers',
        'features': ['revenue_optimization', 'financial_analysis', 'roi_calculation'],
        'dependencies': ['analytics_agent', 'payment_processing_agent']
    },
    
    'payment_processing_agent': {
        'path': '/backend/ai_agents/payment_processing_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'business_revenue',
        'description': 'Traitement paiements et intégrations financières',
        'features': ['payment_processing', 'transaction_management', 'payout_engine'],
        'dependencies': ['fraud_detection_agent']
    },
    
    'licensing_agent': {
        'path': '/backend/ai_agents/licensing_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'business_revenue',
        'description': 'Gestion licences et droits commerciaux',
        'features': ['license_management', 'rights_tracking', 'royalty_calculation'],
        'dependencies': ['legal_agent', 'revenue_agent']
    },
    
    'brand_agent': {
        'path': '/backend/ai_agents/brand_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'business_revenue',
        'description': 'Gestion marque et cohérence visuelle',
        'features': ['brand_management', 'style_guide_enforcement', 'consistency_checking'],
        'dependencies': ['vision_agent', 'nlp_agent']
    },
    
    'marketplace_agent': {
        'path': '/backend/ai_agents/marketplace_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'business_revenue',
        'description': 'Gestion marketplace et transactions',
        'features': ['marketplace_management', 'transaction_processing', 'vendor_management'],
        'dependencies': ['payment_processing_agent', 'revenue_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS CONTENU & ENGAGEMENT
    # ═══════════════════════════════════════════════════════════════
    
    'moderation_agent': {
        'path': '/backend/ai_agents/moderation_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'content_engagement',
        'description': 'Modération contenu intelligente',
        'features': ['content_moderation', 'toxicity_detection', 'community_guidelines'],
        'dependencies': ['nlp_agent', 'vision_agent', 'ml_agent']
    },
    
    'quality_agent': {
        'path': '/backend/ai_agents/quality_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'content_engagement',
        'description': 'Assurance qualité contenu',
        'features': ['quality_assessment', 'content_validation', 'improvement_suggestions'],
        'dependencies': ['ml_agent', 'vision_agent', 'audio_agent']
    },
    
    'recommendation_agent': {
        'path': '/backend/ai_agents/recommendation_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'content_engagement',
        'description': 'Système recommandations personnalisées',
        'features': ['content_recommendation', 'personalization', 'collaborative_filtering'],
        'dependencies': ['ml_agent', 'vector_agent', 'analytics_agent']
    },
    
    'engagement_agent': {
        'path': '/backend/ai_agents/engagement_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'content_engagement',
        'description': 'Optimisation engagement utilisateurs',
        'features': ['engagement_optimization', 'interaction_analysis', 'growth_strategies'],
        'dependencies': ['analytics_agent', 'social_media_agent']
    },
    
    'trend_agent': {
        'path': '/backend/ai_agents/trend_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'content_engagement',
        'description': 'Analyse tendances et viralité',
        'features': ['trend_analysis', 'virality_prediction', 'hashtag_optimization'],
        'dependencies': ['analytics_agent', 'ml_agent', 'social_media_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS UTILISATEUR & SUPPORT
    # ═══════════════════════════════════════════════════════════════
    
    'creator_onboarding_agent': {
        'path': '/backend/ai_agents/creator_onboarding_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'user_support',
        'description': 'Onboarding automatisé créateurs',
        'features': ['onboarding_orchestration', 'skill_assessment', 'personalization'],
        'dependencies': ['ml_agent', 'recommendation_agent']
    },
    
    'support_agent': {
        'path': '/backend/ai_agents/support_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'user_support',
        'description': 'Support client intelligent automatisé',
        'features': ['chatbot_engine', 'ticket_management', 'knowledge_base'],
        'dependencies': ['nlp_agent', 'ml_agent']
    },
    
    'notification_agent': {
        'path': '/backend/ai_agents/notification_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'user_support',
        'description': 'Notifications intelligentes multi-canal',
        'features': ['notification_engine', 'channel_management', 'personalization'],
        'dependencies': ['ml_agent', 'analytics_agent']
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS INFRASTRUCTURE & TECHNIQUE
    # ═══════════════════════════════════════════════════════════════
    
    'api_gateway_agent': {
        'path': '/backend/ai_agents/api_gateway_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'infrastructure',
        'description': 'Passerelle API et gestion trafic',
        'features': ['request_routing', 'rate_limiting', 'authentication', 'load_balancing'],
        'dependencies': []
    },
    
    'storage_agent': {
        'path': '/backend/ai_agents/storage_agent/',
        'status': 'active',
        'priority': 'critical',
        'category': 'infrastructure',
        'description': 'Gestion stockage distribuée',
        'features': ['storage_management', 'file_system_handler', 'cloud_storage'],
        'dependencies': []
    },
    
    'caching_agent': {
        'path': '/backend/ai_agents/caching_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'infrastructure',
        'description': 'Cache intelligent et optimisation performance',
        'features': ['cache_management', 'cache_strategies', 'memory_optimization'],
        'dependencies': []
    },
    
    'auto_scaling_agent': {
        'path': '/backend/ai_agents/auto_scaling_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'infrastructure',
        'description': 'Mise à l\'échelle automatique',
        'features': ['scaling_management', 'load_monitoring', 'resource_allocation'],
        'dependencies': ['analytics_agent']
    },
    
    'optimization_agent': {
        'path': '/backend/ai_agents/optimization_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'infrastructure',
        'description': 'Optimisation performance globale',
        'features': ['performance_optimization', 'resource_management', 'bottleneck_detection'],
        'dependencies': ['analytics_agent']
    },
    
    'workflow_agent': {
        'path': '/backend/ai_agents/workflow_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'infrastructure',
        'description': 'Orchestration processus métier',
        'features': ['workflow_engine', 'process_management', 'task_scheduling'],
        'dependencies': ['scheduling_agent']
    },
    
    'scheduling_agent': {
        'path': '/backend/ai_agents/scheduling_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'infrastructure',
        'description': 'Planification tâches et ressources',
        'features': ['task_scheduling', 'resource_planning', 'calendar_management'],
        'dependencies': []
    },
    
    'crawling_agent': {
        'path': '/backend/ai_agents/crawling_agent/',
        'status': 'active',
        'priority': 'medium',
        'category': 'infrastructure',
        'description': 'Crawling web et collecte données',
        'features': ['web_crawling', 'data_extraction', 'site_monitoring'],
        'dependencies': []
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGENTS BLOCKCHAIN & CRYPTO (Futur/Experimental)
    # ═══════════════════════════════════════════════════════════════
    
    'blockchain_agent': {
        'path': '/backend/ai_agents/blockchain_agent/',
        'status': 'active',
        'priority': 'high',
        'category': 'blockchain_crypto',
        'description': 'Vérification blockchain NFT et smart contracts',
        'features': ['blockchain_verification', 'nft_validation', 'smart_contracts', 'ownership_proof'],
        'dependencies': ['payment_processing_agent', 'rights_management_agent']
    }
}

# ═══════════════════════════════════════════════════════════════
# STATISTIQUES SYSTÈME
# ═══════════════════════════════════════════════════════════════

def get_agents_statistics():
    """Retourne les statistiques complètes du système d'agents"""
    
    stats = {
        'total_agents': len(EXISTING_AGENTS_REGISTRY),
        'by_category': {},
        'by_priority': {},
        'by_status': {},
        'dependencies_count': {}
    }
    
    for agent_id, config in EXISTING_AGENTS_REGISTRY.items():
        # Par catégorie
        category = config['category']
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Par priorité  
        priority = config['priority']
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Par statut
        status = config['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Dépendances
        deps_count = len(config.get('dependencies', []))
        stats['dependencies_count'][agent_id] = deps_count
    
    return stats

def validate_agent_dependencies():
    """Valide que toutes les dépendances existent"""
    errors = []
    
    for agent_id, config in EXISTING_AGENTS_REGISTRY.items():
        dependencies = config.get('dependencies', [])
        
        for dep in dependencies:
            if dep not in EXISTING_AGENTS_REGISTRY:
                errors.append(f"Agent '{agent_id}' dépend de '{dep}' qui n'existe pas")
    
    return errors

def get_agents_by_category(category: str):
    """Retourne tous les agents d'une catégorie donnée"""
    return {
        agent_id: config 
        for agent_id, config in EXISTING_AGENTS_REGISTRY.items() 
        if config['category'] == category
    }

def get_critical_agents():
    """Retourne tous les agents critiques"""
    return {
        agent_id: config 
        for agent_id, config in EXISTING_AGENTS_REGISTRY.items() 
        if config['priority'] == 'critical'
    }

if __name__ == "__main__":
    # Tests et validation
    print("=== IA INFLUENCER AGENT - REGISTRE COMPLET ===")
    print(f"Auteur: Fahed Mlaiel <mlaiel@live.de>")
    print(f"Date: 13 Août 2025")
    print()
    
    stats = get_agents_statistics()
    print(f"📊 STATISTIQUES SYSTÈME:")
    print(f"  • Total agents: {stats['total_agents']}")
    print(f"  • Par catégorie: {dict(stats['by_category'])}")
    print(f"  • Par priorité: {dict(stats['by_priority'])}")
    print(f"  • Par statut: {dict(stats['by_status'])}")
    print()
    
    # Validation des dépendances
    errors = validate_agent_dependencies()
    if errors:
        print("❌ ERREURS DE DÉPENDANCES:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ Toutes les dépendances sont valides")
    
    print()
    print("🔥 AGENTS CRITIQUES:")
    critical = get_critical_agents()
    for agent_id, config in critical.items():
        print(f"  • {agent_id}: {config['description']}")
    
    print()
    print("⚠️  NOTICE LÉGALE:")
    print("Ce registre et tous les agents listés sont la propriété exclusive de Fahed Mlaiel.")
    print("Toute utilisation non autorisée est strictement interdite.")
    print("Contact: mlaiel@live.de")
