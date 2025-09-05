"""Index Module - Matching System Entry Point
==========================================

Centralized entry point for the advanced matching system providing
quick access to all matching algorithms and utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import (
    AdvancedMLMatcher,
    NeuralCompatibilityEngine, 
    AudienceAnalyzer,
    ContentSimilarityEngine,
    CollaborationPredictor,
    NicheCompatibilityMatcher,
    PerformanceAnalyzer,
    SuccessPredictor,
    SkillMatcher,
    GeographicMatcher,
    TemporalAnalyzer
)

def get_matching_engine(config=None):
    """Get unified matching engine with all components"""
    return {
        'ml_matcher': AdvancedMLMatcher(config),
        'neural_compatibility': NeuralCompatibilityEngine(config),
        'audience_analyzer': AudienceAnalyzer(config),
        'content_similarity': ContentSimilarityEngine(config),
        'collaboration_predictor': CollaborationPredictor(config),
        'niche_matcher': NicheCompatibilityMatcher(config),
        'performance_analyzer': PerformanceAnalyzer(config),
        'success_predictor': SuccessPredictor(config),
        'skill_matcher': SkillMatcher(config),
        'geographic_matcher': GeographicMatcher(config),
        'temporal_analyzer': TemporalAnalyzer(config)
    }

async def find_optimal_matches(creator_profile, criteria, creator_pool=None):
    """Find optimal matches using all available algorithms"""
    engine = get_matching_engine()
    
    # Run parallel matching algorithms
    results = {}
    
    # ML-based matching
    ml_matches = await engine['ml_matcher'].find_matches(creator_profile, creator_pool)
    results['ml_matches'] = ml_matches
    
    # Neural compatibility
    neural_scores = await engine['neural_compatibility'].predict_compatibility(creator_profile, creator_pool)
    results['neural_scores'] = neural_scores
    
    # Audience analysis
    audience_overlap = await engine['audience_analyzer'].analyze_overlap(creator_profile, creator_pool)
    results['audience_overlap'] = audience_overlap
    
    # Content similarity
    content_similarity = await engine['content_similarity'].calculate_similarity(creator_profile, creator_pool)
    results['content_similarity'] = content_similarity
    
    # Success prediction
    success_predictions = await engine['success_predictor'].predict_success(creator_profile, creator_pool)
    results['success_predictions'] = success_predictions
    
    return results