#!/usr/bin/env python3
"""
IA Influencer Agent - Advanced Creator Matching Engine
=====================================================

Professional Multi-Format Creator Matching & Collaboration Engine
Ultra-Advanced Industrial Production-Ready Business Logic

Version: 3.0.0
Created by: Fahed Mlaiel (mlaiel@live.de)
Expert Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)  
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps & Infrastructure Engineer
- AI Prompt Engineering Expert

⚠️ STRICT COPYRIGHT WARNING ⚠️
© 2025 Fahed Mlaiel. ALL RIGHTS RESERVED.

This software, concept and intellectual property are protected by international copyright laws.
Any unauthorized use, reproduction, distribution or appropriation of this code, ideas or 
concepts without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
strictly prohibited and will result in immediate legal action.

CONSEQUENCES OF UNAUTHORIZED USE:
- Immediate legal proceedings under German and international copyright law
- Financial damages and compensation claims  
- Criminal prosecution for intellectual property theft
- Permanent legal documentation and public disclosure of violation

AUTHORIZED USE: Contact mlaiel@live.de for licensing and authorization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from decimal import Decimal
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle

# ML/AI Imports
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import networkx as nx
import faiss
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

# Framework Imports
from fastapi import HTTPException
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import aioredis

# Internal Imports
from ...core.base_engine import BaseBusinessEngine
from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.monitoring import MetricsCollector
from ...core.security import SecurityManager
from .matching_models import (
    CreatorProfile, MatchingCriteria, CreatorCompatibility,
    MatchResult, CollaborationOpportunity, MatchingScore,
    CreatorNetwork, CreatorTier, CollaborationType,
    CompatibilityFactor, MatchingStatus
)


class CreatorMatchingEngine(BaseBusinessEngine):
    """
    Ultra-Advanced Creator Matching Engine
    
    Features:
    - AI-powered semantic matching using transformer models
    - Multi-dimensional compatibility scoring
    - Network analysis and community detection
    - Real-time matching with sub-second response times
    - Scalable vector similarity search using FAISS
    - Advanced business intelligence and revenue optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "CreatorMatchingEngine"
        self.version = "3.0.0"
        
        # Core Components
        self.compatibility_analyzer = None
        self.network_analyzer = None
        self.semantic_matcher = None
        self.business_intelligence = None
        
        # ML Models
        self.embedding_model = None
        self.compatibility_classifier = None
        self.success_predictor = None
        self.revenue_optimizer = None
        
        # Vector Databases
        self.creator_index = None
        self.content_index = None
        self.network_index = None
        
        # Cache & Performance
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.security_manager = SecurityManager()
        
        # Threading
        self.thread_executor = ThreadPoolExecutor(max_workers=16)
        self.process_executor = ProcessPoolExecutor(max_workers=8)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize the matching engine with all components"""
        try:
            self.logger.info("Initializing Creator Matching Engine...")
            
            # Initialize core components
            await self._initialize_ai_models()
            await self._initialize_vector_databases()
            await self._initialize_analyzers()
            await self._initialize_cache_system()
            
            # Validate system readiness
            is_ready = await self._validate_system_readiness()
            
            if is_ready:
                self.logger.info("Creator Matching Engine initialized successfully")
                await self.metrics_collector.record_metric("engine_initialization", 1, {"status": "success"})
            else:
                self.logger.error("Creator Matching Engine initialization failed")
                await self.metrics_collector.record_metric("engine_initialization", 1, {"status": "failure"})
            
            return is_ready
            
        except Exception as e:
            self.logger.error(f"Failed to initialize matching engine: {e}")
            return False
    
    async def _initialize_ai_models(self) -> None:
        """Initialize AI/ML models for semantic matching"""
        try:
            # Semantic embedding model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embedding_model = AutoModel.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Compatibility classifier
            self.compatibility_classifier = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Success predictor
            self.success_predictor = RandomForestClassifier(
                n_estimators=300,
                max_depth=8,
                random_state=42
            )
            
            # Feature scaler
            self.feature_scaler = StandardScaler()
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    async def _initialize_vector_databases(self) -> None:
        """Initialize FAISS vector databases for fast similarity search"""
        try:
            # Creator profile vectors (768-dim)
            self.creator_index = faiss.IndexFlatIP(768)
            self.creator_id_map = {}
            
            # Content embeddings (768-dim) 
            self.content_index = faiss.IndexFlatIP(768)
            self.content_id_map = {}
            
            # Network embeddings (512-dim)
            self.network_index = faiss.IndexFlatIP(512)
            self.network_id_map = {}
            
            self.logger.info("Vector databases initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector databases: {e}")
            raise
    
    async def _initialize_analyzers(self) -> None:
        """Initialize specialized analyzers"""
        try:
            self.compatibility_analyzer = CompatibilityAnalyzer(self.config)
            self.network_analyzer = NetworkAnalyzer(self.config)
            self.business_intelligence = BusinessIntelligenceAnalyzer(self.config)
            self.quality_assessor = QualityAssessor(self.config)
            
            self.logger.info("Analyzers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analyzers: {e}")
            raise
    
    async def _initialize_cache_system(self) -> None:
        """Initialize caching system for performance optimization"""
        try:
            # Redis cache for hot data
            self.redis_client = await aioredis.create_redis_pool(
                self.config.get("redis_url", "redis://localhost:6379"),
                encoding="utf-8"
            )
            
            # In-memory cache for frequently accessed data
            self.memory_cache = {}
            self.cache_ttl = 3600  # 1 hour
            
            self.logger.info("Cache system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache system: {e}")
            raise
    
    async def find_matches(
        self, 
        creator_id: str, 
        criteria: MatchingCriteria,
        limit: int = 50,
        offset: int = 0
    ) -> List[MatchResult]:
        """
        Find optimal collaboration matches for a creator
        
        Args:
            creator_id: ID of the creator seeking matches
            criteria: Matching criteria and preferences
            limit: Maximum number of matches to return
            offset: Pagination offset
            
        Returns:
            List of ranked match results
        """
        try:
            start_time = datetime.utcnow()
            
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                raise HTTPException(status_code=404, detail="Creator profile not found")
            
            # Get candidate creators
            candidates = await self._get_candidate_creators(creator_profile, criteria)
            
            # Filter candidates based on criteria
            filtered_candidates = await self._filter_candidates(
                creator_profile, candidates, criteria
            )
            
            # Calculate compatibility scores
            compatibility_scores = await self._calculate_batch_compatibility(
                creator_profile, filtered_candidates
            )
            
            # Generate match results
            matches = await self._generate_match_results(
                creator_profile, compatibility_scores, criteria
            )
            
            # Rank matches by score and business value
            ranked_matches = await self._rank_matches(matches, criteria)
            
            # Apply pagination
            paginated_matches = ranked_matches[offset:offset + limit]
            
            # Cache results for future requests
            await self._cache_match_results(creator_id, criteria, paginated_matches)
            
            # Record performance metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric(
                "match_finding_duration", 
                processing_time,
                {
                    "creator_id": creator_id,
                    "candidates_processed": len(filtered_candidates),
                    "matches_found": len(paginated_matches)
                }
            )
            
            self.logger.info(
                f"Found {len(paginated_matches)} matches for creator {creator_id} "
                f"in {processing_time:.2f}s"
            )
            
            return paginated_matches
            
        except Exception as e:
            self.logger.error(f"Error finding matches for creator {creator_id}: {e}")
            await self.metrics_collector.record_metric("match_finding_errors", 1, {"error": str(e)})
            raise HTTPException(status_code=500, detail=f"Match finding failed: {str(e)}")
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get creator profile from database or cache"""
        try:
            # Check cache first
            cache_key = f"creator_profile:{creator_id}"
            cached_profile = await self.redis_client.get(cache_key)
            
            if cached_profile:
                profile_data = json.loads(cached_profile)
                return CreatorProfile(**profile_data)
            
            # Query database
            async with get_async_session() as session:
                query = select(CreatorProfileDB).where(
                    CreatorProfileDB.creator_id == creator_id
                )
                result = await session.execute(query)
                profile_db = result.scalar_one_or_none()
                
                if profile_db:
                    profile = CreatorProfile(
                        creator_id=profile_db.creator_id,
                        user_id=profile_db.user_id,
                        username=profile_db.username,
                        display_name=profile_db.display_name,
                        bio=profile_db.bio,
                        creator_type=profile_db.creator_type,
                        tier=profile_db.tier,
                        verification_status=profile_db.verification_status,
                        # ... map other fields
                    )
                    
                    # Cache the profile
                    await self.redis_client.setex(
                        cache_key, 
                        self.cache_ttl, 
                        json.dumps(profile.__dict__)
                    )
                    
                    return profile
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting creator profile {creator_id}: {e}")
            return None
    
    async def _get_candidate_creators(
        self, 
        creator: CreatorProfile, 
        criteria: MatchingCriteria
    ) -> List[CreatorProfile]:
        """Get candidate creators for matching"""
        try:
            # Use vector similarity search for initial candidate retrieval
            if self.creator_index.ntotal > 0:
                candidates = await self._vector_search_candidates(creator, criteria)
            else:
                candidates = await self._database_search_candidates(creator, criteria)
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error getting candidate creators: {e}")
            return []
    
    async def _vector_search_candidates(
        self, 
        creator: CreatorProfile, 
        criteria: MatchingCriteria
    ) -> List[CreatorProfile]:
        """Use vector similarity search for candidate retrieval"""
        try:
            # Generate embedding for creator
            creator_embedding = await self._generate_creator_embedding(creator)
            
            # Search similar creators in vector space
            k = min(1000, self.creator_index.ntotal)  # Top 1000 similar creators
            distances, indices = self.creator_index.search(
                creator_embedding.reshape(1, -1).astype(np.float32), 
                k
            )
            
            # Convert indices to creator IDs and retrieve profiles
            candidate_ids = [self.creator_id_map.get(idx) for idx in indices[0]]
            candidate_ids = [cid for cid in candidate_ids if cid and cid != creator.creator_id]
            
            # Retrieve candidate profiles
            candidates = []
            for creator_id in candidate_ids:
                profile = await self._get_creator_profile(creator_id)
                if profile:
                    candidates.append(profile)
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error in vector search for candidates: {e}")
            return []
    
    async def _database_search_candidates(
        self, 
        creator: CreatorProfile, 
        criteria: MatchingCriteria
    ) -> List[CreatorProfile]:
        """Use database queries for candidate retrieval"""
        try:
            async with get_async_session() as session:
                query = select(CreatorProfileDB).where(
                    CreatorProfileDB.creator_id != creator.creator_id
                )
                
                # Apply basic filters
                if criteria.min_followers:
                    query = query.where(CreatorProfileDB.total_followers >= criteria.min_followers)
                    
                if criteria.max_followers:
                    query = query.where(CreatorProfileDB.total_followers <= criteria.max_followers)
                
                if criteria.min_engagement_rate:
                    query = query.where(
                        CreatorProfileDB.average_engagement_rate >= criteria.min_engagement_rate
                    )
                
                if criteria.min_content_quality:
                    query = query.where(
                        CreatorProfileDB.content_quality_score >= criteria.min_content_quality
                    )
                
                # Limit for performance
                query = query.limit(5000)
                
                result = await session.execute(query)
                profiles_db = result.scalars().all()
                
                # Convert to business models
                candidates = []
                for profile_db in profiles_db:
                    profile = CreatorProfile(
                        creator_id=profile_db.creator_id,
                        user_id=profile_db.user_id,
                        username=profile_db.username,
                        display_name=profile_db.display_name,
                        bio=profile_db.bio,
                        creator_type=profile_db.creator_type,
                        tier=profile_db.tier,
                        verification_status=profile_db.verification_status,
                        total_followers=profile_db.total_followers,
                        average_engagement_rate=profile_db.average_engagement_rate,
                        content_quality_score=profile_db.content_quality_score
                    )
                    candidates.append(profile)
                
                return candidates
                
        except Exception as e:
            self.logger.error(f"Error in database search for candidates: {e}")
            return []
    
    async def _filter_candidates(
        self, 
        creator: CreatorProfile,
        candidates: List[CreatorProfile],
        criteria: MatchingCriteria
    ) -> List[CreatorProfile]:
        """Apply advanced filtering to candidate list"""
        try:
            filtered = []
            
            for candidate in candidates:
                if await self._passes_criteria_filters(creator, candidate, criteria):
                    filtered.append(candidate)
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering candidates: {e}")
            return candidates
    
    async def _passes_criteria_filters(
        self,
        creator: CreatorProfile,
        candidate: CreatorProfile, 
        criteria: MatchingCriteria
    ) -> bool:
        """Check if candidate passes all criteria filters"""
        try:
            # Platform requirements
            if criteria.required_platforms:
                candidate_platforms = set(candidate.platforms.keys())
                required_platforms = set(criteria.required_platforms)
                if not required_platforms.intersection(candidate_platforms):
                    return False
            
            # Content type requirements
            if criteria.required_content_types:
                candidate_content_types = set(candidate.content_types)
                required_content_types = set(criteria.required_content_types)
                if not required_content_types.intersection(candidate_content_types):
                    return False
            
            # Quality thresholds
            if criteria.min_authenticity_score:
                if candidate.authenticity_score < criteria.min_authenticity_score:
                    return False
            
            if criteria.min_brand_safety_score:
                if candidate.brand_safety_score < criteria.min_brand_safety_score:
                    return False
            
            # Geographic filters
            if criteria.excluded_locations:
                candidate_location = candidate.audience_geographic_distribution
                for excluded_location in criteria.excluded_locations:
                    if excluded_location in candidate_location:
                        return False
            
            # Blacklist check
            if criteria.exclude_blacklisted and candidate.creator_id in creator.blacklisted_creators:
                return False
            
            # Past collaboration check
            if criteria.exclude_past_collaborators:
                if candidate.creator_id in creator.past_collaborations:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking criteria filters: {e}")
            return True  # Default to include if error
    
    async def _calculate_batch_compatibility(
        self,
        creator: CreatorProfile,
        candidates: List[CreatorProfile]
    ) -> List[Tuple[CreatorProfile, CreatorCompatibility]]:
        """Calculate compatibility scores for batch of candidates"""
        try:
            compatibility_results = []
            
            # Process in batches for performance
            batch_size = 100
            for i in range(0, len(candidates), batch_size):
                batch = candidates[i:i + batch_size]
                
                # Use thread pool for parallel processing
                tasks = [
                    self.thread_executor.submit(
                        self._calculate_compatibility_sync, 
                        creator, 
                        candidate
                    )
                    for candidate in batch
                ]
                
                # Wait for batch completion
                for task, candidate in zip(tasks, batch):
                    try:
                        compatibility = task.result(timeout=30)  # 30s timeout per compatibility calc
                        if compatibility:
                            compatibility_results.append((candidate, compatibility))
                    except Exception as e:
                        self.logger.warning(f"Compatibility calculation failed for candidate {candidate.creator_id}: {e}")
            
            return compatibility_results
            
        except Exception as e:
            self.logger.error(f"Error in batch compatibility calculation: {e}")
            return []
    
    def _calculate_compatibility_sync(
        self,
        creator: CreatorProfile, 
        candidate: CreatorProfile
    ) -> Optional[CreatorCompatibility]:
        """Synchronous compatibility calculation for threading"""
        try:
            # This would be called from thread pool
            return asyncio.run(self.compatibility_analyzer.analyze_compatibility(creator, candidate))
            
        except Exception as e:
            self.logger.error(f"Sync compatibility calculation error: {e}")
            return None
    
    async def _generate_match_results(
        self,
        creator: CreatorProfile,
        compatibility_scores: List[Tuple[CreatorProfile, CreatorCompatibility]],
        criteria: MatchingCriteria
    ) -> List[MatchResult]:
        """Generate comprehensive match results"""
        try:
            matches = []
            
            for candidate, compatibility in compatibility_scores:
                if compatibility.overall_compatibility_score >= criteria.ai_confidence_threshold:
                    # Generate business intelligence
                    business_insights = await self.business_intelligence.generate_insights(
                        creator, candidate, compatibility
                    )
                    
                    # Create match result
                    match = MatchResult(
                        requester_id=creator.creator_id,
                        matched_creator_id=candidate.creator_id,
                        match_score=compatibility.overall_compatibility_score,
                        match_confidence=compatibility.analysis_confidence,
                        compatibility_analysis=compatibility,
                        match_reasons=business_insights.get("match_reasons", []),
                        compatibility_highlights=business_insights.get("highlights", []),
                        potential_challenges=business_insights.get("challenges", []),
                        success_factors=business_insights.get("success_factors", []),
                        recommended_projects=business_insights.get("recommended_projects", []),
                        suggested_platforms=business_insights.get("suggested_platforms", []),
                        projected_reach=business_insights.get("projected_reach", 0),
                        projected_engagement=business_insights.get("projected_engagement", 0.0),
                        estimated_roi=business_insights.get("estimated_roi")
                    )
                    
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error generating match results: {e}")
            return []
    
    async def _rank_matches(
        self,
        matches: List[MatchResult],
        criteria: MatchingCriteria
    ) -> List[MatchResult]:
        """Rank matches by composite scoring algorithm"""
        try:
            # Calculate composite scores considering multiple factors
            for i, match in enumerate(matches):
                composite_score = await self._calculate_composite_score(match, criteria)
                match.match_score = composite_score
                match.match_rank = i + 1  # Will be reordered
            
            # Sort by composite score (descending)
            ranked_matches = sorted(matches, key=lambda x: x.match_score, reverse=True)
            
            # Update ranks
            for i, match in enumerate(ranked_matches):
                match.match_rank = i + 1
            
            return ranked_matches
            
        except Exception as e:
            self.logger.error(f"Error ranking matches: {e}")
            return matches
    
    async def _calculate_composite_score(
        self,
        match: MatchResult,
        criteria: MatchingCriteria
    ) -> float:
        """Calculate composite match score using weighted factors"""
        try:
            compatibility = match.compatibility_analysis
            weights = criteria.compatibility_weights or {}
            
            # Base compatibility score (50% weight)
            base_score = compatibility.overall_compatibility_score * 0.5
            
            # Business value score (25% weight)
            business_score = (
                (compatibility.revenue_generation_potential * 0.4) +
                (compatibility.audience_growth_potential * 0.3) +
                (compatibility.viral_potential * 0.3)
            ) * 0.25
            
            # Risk-adjusted score (15% weight)  
            risk_score = max(0, 1.0 - compatibility.collaboration_risk_score) * 0.15
            
            # Success probability (10% weight)
            success_score = compatibility.success_probability * 0.1
            
            composite_score = base_score + business_score + risk_score + success_score
            
            return min(1.0, max(0.0, composite_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating composite score: {e}")
            return match.match_score
    
    async def _generate_creator_embedding(self, creator: CreatorProfile) -> np.ndarray:
        """Generate semantic embedding for creator profile"""
        try:
            # Combine textual features
            text_features = f"{creator.bio} {' '.join(creator.content_categories)} {' '.join(creator.content_themes)}"
            
            # Tokenize and encode
            inputs = self.tokenizer(
                text_features,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).numpy().flatten()
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error generating creator embedding: {e}")
            return np.zeros(768)  # Default embedding size
    
    async def _cache_match_results(
        self,
        creator_id: str,
        criteria: MatchingCriteria,
        matches: List[MatchResult]
    ) -> None:
        """Cache match results for performance optimization"""
        try:
            # Create cache key from criteria hash
            criteria_hash = hash(str(criteria.__dict__))
            cache_key = f"matches:{creator_id}:{criteria_hash}"
            
            # Serialize matches
            matches_data = [match.__dict__ for match in matches]
            
            # Cache with TTL
            await self.redis_client.setex(
                cache_key,
                1800,  # 30 minutes
                json.dumps(matches_data, default=str)
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to cache match results: {e}")
    
    async def _validate_system_readiness(self) -> bool:
        """Validate that all systems are ready for operation"""
        try:
            # Test AI models
            if not self.embedding_model:
                return False
            
            # Test vector databases
            if not self.creator_index:
                return False
            
            # Test analyzers
            if not self.compatibility_analyzer:
                return False
            
            # Test cache connection
            await self.redis_client.ping()
            
            return True
            
        except Exception as e:
            self.logger.error(f"System readiness validation failed: {e}")
            return False
    
    async def get_match_by_id(self, match_id: str) -> Optional[MatchResult]:
        """Get specific match result by ID"""
        try:
            cache_key = f"match:{match_id}"
            cached_match = await self.redis_client.get(cache_key)
            
            if cached_match:
                match_data = json.loads(cached_match)
                return MatchResult(**match_data)
            
            # Query from database if not in cache
            async with get_async_session() as session:
                query = select(MatchResultDB).where(MatchResultDB.match_id == match_id)
                result = await session.execute(query)
                match_db = result.scalar_one_or_none()
                
                if match_db:
                    # Convert to business model
                    match = MatchResult(
                        match_id=match_db.match_id,
                        requester_id=match_db.requester_id,
                        matched_creator_id=match_db.matched_creator_id,
                        match_score=match_db.match_score,
                        match_rank=match_db.match_rank,
                        match_confidence=match_db.match_confidence,
                        # ... map other fields
                    )
                    
                    # Cache the result
                    await self.redis_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(match.__dict__, default=str)
                    )
                    
                    return match
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting match by ID {match_id}: {e}")
            return None
    
    async def update_match_status(
        self,
        match_id: str,
        status: MatchingStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update match status"""
        try:
            async with get_async_session() as session:
                query = select(MatchResultDB).where(MatchResultDB.match_id == match_id)
                result = await session.execute(query)
                match_db = result.scalar_one_or_none()
                
                if match_db:
                    match_db.status = status.value
                    match_db.updated_at = datetime.utcnow()
                    
                    if metadata:
                        current_metadata = match_db.metadata or {}
                        current_metadata.update(metadata)
                        match_db.metadata = current_metadata
                    
                    await session.commit()
                    
                    # Invalidate cache
                    cache_key = f"match:{match_id}"
                    await self.redis_client.delete(cache_key)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating match status: {e}")
            return False
    
    async def get_creator_matches_history(
        self,
        creator_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MatchResult]:
        """Get creator's match history"""
        try:
            async with get_async_session() as session:
                query = select(MatchResultDB).where(
                    or_(
                        MatchResultDB.requester_id == creator_id,
                        MatchResultDB.matched_creator_id == creator_id
                    )
                ).order_by(
                    MatchResultDB.created_at.desc()
                ).limit(limit).offset(offset)
                
                result = await session.execute(query)
                matches_db = result.scalars().all()
                
                matches = []
                for match_db in matches_db:
                    match = MatchResult(
                        match_id=match_db.match_id,
                        requester_id=match_db.requester_id,
                        matched_creator_id=match_db.matched_creator_id,
                        match_score=match_db.match_score,
                        match_rank=match_db.match_rank,
                        match_confidence=match_db.match_confidence,
                        status=MatchingStatus(match_db.status)
                    )
                    matches.append(match)
                
                return matches
                
        except Exception as e:
            self.logger.error(f"Error getting creator matches history: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Graceful shutdown of matching engine"""
        try:
            self.logger.info("Shutting down Creator Matching Engine...")
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
                await self.redis_client.wait_closed()
            
            # Shutdown executors
            self.thread_executor.shutdown(wait=True)
            self.process_executor.shutdown(wait=True)
            
            self.logger.info("Creator Matching Engine shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error during engine shutdown: {e}")


class CompatibilityAnalyzer:
    """Advanced compatibility analysis between creators"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def analyze_compatibility(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> CreatorCompatibility:
        """Comprehensive compatibility analysis"""
        try:
            # Calculate individual factor scores
            factor_scores = await self._calculate_factor_scores(creator_a, creator_b)
            
            # Calculate overall compatibility
            overall_score = await self._calculate_overall_score(factor_scores)
            
            # Analyze synergy potential
            synergy_metrics = await self._analyze_synergy_potential(creator_a, creator_b)
            
            # Assess risks
            risk_metrics = await self._assess_collaboration_risks(creator_a, creator_b)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(creator_a, creator_b, factor_scores)
            
            # Predict success metrics
            success_metrics = await self._predict_success_metrics(creator_a, creator_b, overall_score)
            
            compatibility = CreatorCompatibility(
                creator_a_id=creator_a.creator_id,
                creator_b_id=creator_b.creator_id,
                overall_compatibility_score=overall_score,
                factor_scores=factor_scores,
                audience_overlap_percentage=synergy_metrics["audience_overlap"],
                content_style_similarity=synergy_metrics["content_similarity"],
                brand_alignment_score=synergy_metrics["brand_alignment"],
                engagement_compatibility=synergy_metrics["engagement_compatibility"],
                quality_compatibility=synergy_metrics["quality_compatibility"],
                cross_pollination_potential=synergy_metrics["cross_pollination"],
                audience_growth_potential=synergy_metrics["growth_potential"],
                revenue_generation_potential=synergy_metrics["revenue_potential"],
                viral_potential=synergy_metrics["viral_potential"],
                collaboration_risk_score=risk_metrics["overall_risk"],
                brand_safety_risk=risk_metrics["brand_safety_risk"],
                audience_reception_risk=risk_metrics["audience_risk"],
                recommended_collaboration_types=recommendations["collaboration_types"],
                optimal_collaboration_timeline=recommendations["timeline"],
                suggested_content_themes=recommendations["content_themes"],
                success_probability=success_metrics["success_probability"],
                expected_engagement_boost=success_metrics["engagement_boost"],
                expected_follower_growth=success_metrics["follower_growth"],
                expected_revenue_impact=success_metrics["revenue_impact"],
                analysis_confidence=success_metrics["confidence"]
            )
            
            return compatibility
            
        except Exception as e:
            self.logger.error(f"Error in compatibility analysis: {e}")
            raise
    
    async def _calculate_factor_scores(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> Dict[CompatibilityFactor, float]:
        """Calculate individual compatibility factor scores"""
        try:
            scores = {}
            
            # Audience overlap
            scores[CompatibilityFactor.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
                creator_a, creator_b
            )
            
            # Content style similarity
            scores[CompatibilityFactor.CONTENT_STYLE] = await self._calculate_content_style_similarity(
                creator_a, creator_b
            )
            
            # Brand alignment
            scores[CompatibilityFactor.BRAND_ALIGNMENT] = await self._calculate_brand_alignment(
                creator_a, creator_b
            )
            
            # Engagement compatibility
            scores[CompatibilityFactor.ENGAGEMENT_RATE] = await self._calculate_engagement_compatibility(
                creator_a, creator_b
            )
            
            # Quality compatibility
            scores[CompatibilityFactor.CONTENT_QUALITY] = await self._calculate_quality_compatibility(
                creator_a, creator_b
            )
            
            # Platform presence overlap
            scores[CompatibilityFactor.PLATFORM_PRESENCE] = await self._calculate_platform_compatibility(
                creator_a, creator_b
            )
            
            # Geographic compatibility
            scores[CompatibilityFactor.GEOGRAPHIC_LOCATION] = await self._calculate_geographic_compatibility(
                creator_a, creator_b
            )
            
            # Language compatibility
            scores[CompatibilityFactor.LANGUAGE_COMPATIBILITY] = await self._calculate_language_compatibility(
                creator_a, creator_b
            )
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error calculating factor scores: {e}")
            return {}
    
    async def _calculate_audience_overlap(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate audience demographic overlap"""
        try:
            # Age distribution overlap
            age_overlap = self._calculate_distribution_overlap(
                creator_a.audience_age_distribution,
                creator_b.audience_age_distribution
            )
            
            # Geographic overlap
            geo_overlap = self._calculate_distribution_overlap(
                creator_a.audience_geographic_distribution,
                creator_b.audience_geographic_distribution
            )
            
            # Interest overlap (using Jaccard similarity)
            interests_a = set(creator_a.audience_interests)
            interests_b = set(creator_b.audience_interests)
            
            if interests_a or interests_b:
                interest_overlap = len(interests_a & interests_b) / len(interests_a | interests_b)
            else:
                interest_overlap = 0.0
            
            # Weighted combination
            overlap_score = (age_overlap * 0.4) + (geo_overlap * 0.3) + (interest_overlap * 0.3)
            
            return min(1.0, max(0.0, overlap_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating audience overlap: {e}")
            return 0.0
    
    def _calculate_distribution_overlap(
        self,
        dist_a: Dict[str, float],
        dist_b: Dict[str, float]
    ) -> float:
        """Calculate overlap between two probability distributions"""
        try:
            if not dist_a or not dist_b:
                return 0.0
            
            # Get all categories
            all_categories = set(dist_a.keys()) | set(dist_b.keys())
            
            # Calculate overlap using Bhattacharyya coefficient
            overlap = 0.0
            for category in all_categories:
                prob_a = dist_a.get(category, 0.0)
                prob_b = dist_b.get(category, 0.0)
                overlap += np.sqrt(prob_a * prob_b)
            
            return min(1.0, overlap)
            
        except Exception as e:
            self.logger.error(f"Error calculating distribution overlap: {e}")
            return 0.0
    
    async def _calculate_content_style_similarity(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate content style similarity using semantic analysis"""
        try:
            # Content categories overlap
            categories_a = set(creator_a.content_categories)
            categories_b = set(creator_b.content_categories)
            
            category_similarity = 0.0
            if categories_a or categories_b:
                category_similarity = len(categories_a & categories_b) / len(categories_a | categories_b)
            
            # Content themes overlap
            themes_a = set(creator_a.content_themes)
            themes_b = set(creator_b.content_themes)
            
            theme_similarity = 0.0
            if themes_a or themes_b:
                theme_similarity = len(themes_a & themes_b) / len(themes_a | themes_b)
            
            # Style tags overlap
            tags_a = set(creator_a.content_style_tags)
            tags_b = set(creator_b.content_style_tags)
            
            tag_similarity = 0.0
            if tags_a or tags_b:
                tag_similarity = len(tags_a & tags_b) / len(tags_a | tags_b)
            
            # Weighted combination
            style_similarity = (category_similarity * 0.4) + (theme_similarity * 0.4) + (tag_similarity * 0.2)
            
            return min(1.0, max(0.0, style_similarity))
            
        except Exception as e:
            self.logger.error(f"Error calculating content style similarity: {e}")
            return 0.0
    
    async def _calculate_overall_score(self, factor_scores: Dict[CompatibilityFactor, float]) -> float:
        """Calculate weighted overall compatibility score"""
        try:
            # Default weights for factors
            default_weights = {
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.20,
                CompatibilityFactor.CONTENT_STYLE: 0.18,
                CompatibilityFactor.BRAND_ALIGNMENT: 0.15,
                CompatibilityFactor.ENGAGEMENT_RATE: 0.12,
                CompatibilityFactor.CONTENT_QUALITY: 0.10,
                CompatibilityFactor.PLATFORM_PRESENCE: 0.08,
                CompatibilityFactor.GEOGRAPHIC_LOCATION: 0.07,
                CompatibilityFactor.LANGUAGE_COMPATIBILITY: 0.05,
                CompatibilityFactor.POSTING_FREQUENCY: 0.03,
                CompatibilityFactor.AUDIENCE_SIZE: 0.02
            }
            
            overall_score = 0.0
            total_weight = 0.0
            
            for factor, weight in default_weights.items():
                if factor in factor_scores:
                    overall_score += factor_scores[factor] * weight
                    total_weight += weight
            
            if total_weight > 0:
                overall_score = overall_score / total_weight
            
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    # Additional methods for synergy analysis, risk assessment, etc.
    # ... (implementation continues)


class MatchingPreferences:
    """User preferences for matching algorithm configuration"""
    
    def __init__(self):
        self.quality_weight = 0.3
        self.audience_similarity_weight = 0.25
        self.engagement_weight = 0.2
        self.brand_safety_weight = 0.15
        self.growth_potential_weight = 0.1
        
        self.enable_ai_recommendations = True
        self.confidence_threshold = 0.7
        self.max_matches = 50
        self.exclude_past_collaborators = False


# Export main classes
__all__ = [
    "CreatorMatchingEngine",
    "CompatibilityAnalyzer",
    "MatchingPreferences"
]
