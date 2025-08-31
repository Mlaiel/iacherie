"""Content Fingerprint Repository Module

Enterprise-grade repository for content fingerprinting operations
supporting audio, video, image, and text fingerprint management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from datetime import datetime, timedelta
import uuid
import hashlib
import numpy as np
from ..models.content_fingerprints import (
    ContentFingerprint, 
    ContentType, 
    FingerprintAlgorithm,
    FingerprintStatus,
    QualityLevel,
    ContentCategory
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class ContentFingerprintRepository(BaseRepository[ContentFingerprint]):
    """    Repository for content fingerprint operations with advanced similarity search,
    vector matching, and multi-format content protection capabilities.
    """    
    def __init__(self, db_session: Session):
        """Initialize content fingerprint repository"""        super().__init__(db_session, ContentFingerprint)
        
    def create_fingerprint(self,
                          user_id: int,
                          content_type: ContentType,
                          original_filename: str,
                          fingerprint_hash: str,
                          vector_embedding: Optional[bytes] = None,
                          algorithm: FingerprintAlgorithm = FingerprintAlgorithm.CHROMAPRINT,
                          quality_level: QualityLevel = QualityLevel.HIGH,
                          content_category: ContentCategory = ContentCategory.ORIGINAL,
                          metadata: Optional[Dict[str, Any]] = None) -> ContentFingerprint:
        """        Create content fingerprint with validation and deduplication
        
        Args:
            user_id: Owner user ID
            content_type: Type of content (audio, video, image, text)
            original_filename: Original file name
            fingerprint_hash: Generated fingerprint hash
            vector_embedding: Vector representation for similarity search
            algorithm: Fingerprinting algorithm used
            quality_level: Quality level of the fingerprint
            content_category: Category of content
            metadata: Additional metadata
            
        Returns:
            Created ContentFingerprint instance
        """        try:
            # Check for duplicate fingerprints
            existing = self.get_by_fingerprint_hash(fingerprint_hash)
            if existing:
                raise RepositoryException(
                    f"Fingerprint already exists for hash: {fingerprint_hash[:16]}..."
                )
            
            # Generate content ID if not provided
            content_id = str(uuid.uuid4())
            
            fingerprint_data = {
                'user_id': user_id,
                'content_type': content_type,
                'original_filename': original_filename,
                'fingerprint_hash': fingerprint_hash,
                'vector_embedding': vector_embedding,
                'algorithm': algorithm,
                'quality_level': quality_level,
                'content_category': content_category,
                'metadata': metadata or {},
                'content_id': content_id,
                'status': FingerprintStatus.ACTIVE,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            fingerprint = self.create(**fingerprint_data)
            
            self.logger.info(
                f"Created fingerprint for {content_type.value} content: {original_filename}"
            )
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Failed to create fingerprint: {str(e)}")
            raise RepositoryException(f"Fingerprint creation failed: {str(e)}")
            
    def get_by_fingerprint_hash(self, fingerprint_hash: str) -> Optional[ContentFingerprint]:
        """        Get fingerprint by hash value
        
        Args:
            fingerprint_hash: Fingerprint hash to search for
            
        Returns:
            ContentFingerprint instance or None
        """        try:
            return self.db_session.query(ContentFingerprint).filter(
                ContentFingerprint.fingerprint_hash == fingerprint_hash
            ).first()
            
        except Exception as e:
            self.logger.error(f"Failed to get fingerprint by hash: {str(e)}")
            return None
            
    def get_by_user_id(self, 
                      user_id: int,
                      content_type: Optional[ContentType] = None,
                      status: Optional[FingerprintStatus] = None,
                      limit: Optional[int] = None,
                      offset: Optional[int] = None) -> List[ContentFingerprint]:
        """        Get fingerprints by user ID with optional filtering
        
        Args:
            user_id: User ID to filter by
            content_type: Optional content type filter
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ContentFingerprint instances
        """        try:
            query = self.db_session.query(ContentFingerprint).filter(
                ContentFingerprint.user_id == user_id
            )
            
            if content_type:
                query = query.filter(ContentFingerprint.content_type == content_type)
                
            if status:
                query = query.filter(ContentFingerprint.status == status)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            query = query.order_by(ContentFingerprint.created_at.desc())
            
            fingerprints = query.all()
            
            self.logger.debug(
                f"Retrieved {len(fingerprints)} fingerprints for user {user_id}"
            )
            
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Failed to get fingerprints by user: {str(e)}")
            return []
            
    def find_similar_fingerprints(self,
                                 fingerprint_hash: str,
                                 content_type: ContentType,
                                 similarity_threshold: float = 0.8,
                                 exclude_user_id: Optional[int] = None,
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """        Find similar fingerprints using hash comparison and vector similarity
        
        Args:
            fingerprint_hash: Hash to compare against
            content_type: Content type to filter by
            similarity_threshold: Minimum similarity score
            exclude_user_id: User ID to exclude from results
            limit: Maximum number of results
            
        Returns:
            List of similar fingerprints with similarity scores
        """        try:
            # Find exact hash matches first
            exact_matches = self.db_session.query(ContentFingerprint).filter(
                and_(
                    ContentFingerprint.fingerprint_hash == fingerprint_hash,
                    ContentFingerprint.content_type == content_type,
                    ContentFingerprint.status == FingerprintStatus.ACTIVE
                )
            )
            
            if exclude_user_id:
                exact_matches = exact_matches.filter(
                    ContentFingerprint.user_id != exclude_user_id
                )
                
            exact_results = []
            for match in exact_matches.limit(limit).all():
                exact_results.append({
                    'fingerprint': match,
                    'similarity_score': 1.0,
                    'match_type': 'exact'
                })
            
            # If we have exact matches, return them
            if exact_results:
                return exact_results
            
            # For fuzzy matching, we would implement vector similarity search
            # This would typically use FAISS or similar vector database
            similar_results = self._find_fuzzy_matches(
                fingerprint_hash,
                content_type,
                similarity_threshold,
                exclude_user_id,
                limit
            )
            
            return similar_results
            
        except Exception as e:
            self.logger.error(f"Failed to find similar fingerprints: {str(e)}")
            return []
            
    def _find_fuzzy_matches(self,
                           fingerprint_hash: str,
                           content_type: ContentType,
                           similarity_threshold: float,
                           exclude_user_id: Optional[int],
                           limit: int) -> List[Dict[str, Any]]:
        """        Find fuzzy matches using advanced similarity algorithms
        
        Args:
            fingerprint_hash: Hash to compare against
            content_type: Content type to filter by
            similarity_threshold: Minimum similarity score
            exclude_user_id: User ID to exclude from results
            limit: Maximum number of results
            
        Returns:
            List of similar fingerprints with similarity scores
        """        try:
            # Get all fingerprints of the same content type
            query = self.db_session.query(ContentFingerprint).filter(
                and_(
                    ContentFingerprint.content_type == content_type,
                    ContentFingerprint.status == FingerprintStatus.ACTIVE,
                    ContentFingerprint.fingerprint_hash != fingerprint_hash
                )
            )
            
            if exclude_user_id:
                query = query.filter(ContentFingerprint.user_id != exclude_user_id)
            
            candidates = query.all()
            
            similar_fingerprints = []
            
            for candidate in candidates:
                # Calculate similarity score using various methods
                similarity_score = self._calculate_similarity(
                    fingerprint_hash, 
                    candidate.fingerprint_hash,
                    content_type
                )
                
                if similarity_score >= similarity_threshold:
                    similar_fingerprints.append({
                        'fingerprint': candidate,
                        'similarity_score': similarity_score,
                        'match_type': 'fuzzy'
                    })
            
            # Sort by similarity score (highest first)
            similar_fingerprints.sort(
                key=lambda x: x['similarity_score'], 
                reverse=True
            )
            
            return similar_fingerprints[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to find fuzzy matches: {str(e)}")
            return []
            
    def _calculate_similarity(self,
                            hash1: str,
                            hash2: str,
                            content_type: ContentType) -> float:
        """        Calculate similarity score between two fingerprint hashes
        
        Args:
            hash1: First fingerprint hash
            hash2: Second fingerprint hash
            content_type: Type of content for algorithm selection
            
        Returns:
            Similarity score between 0.0 and 1.0
        """        try:
            # Hamming distance for binary hashes
            if len(hash1) == len(hash2):
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                max_distance = len(hash1)
                similarity = 1.0 - (hamming_distance / max_distance)
                return max(0.0, similarity)
            
            # Jaccard similarity for set-based hashes
            set1 = set(hash1[i:i+4] for i in range(0, len(hash1), 4))
            set2 = set(hash2[i:i+4] for i in range(0, len(hash2), 4))
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            if union == 0:
                return 0.0
                
            jaccard_similarity = intersection / union
            return jaccard_similarity
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {str(e)}")
            return 0.0
            
    def get_content_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """        Get comprehensive content fingerprint statistics
        
        Args:
            user_id: Optional user ID to filter statistics
            
        Returns:
            Dictionary containing various statistics
        """        try:
            base_query = self.db_session.query(ContentFingerprint)
            
            if user_id:
                base_query = base_query.filter(ContentFingerprint.user_id == user_id)
            
            # Total counts
            total_fingerprints = base_query.count()
            active_fingerprints = base_query.filter(
                ContentFingerprint.status == FingerprintStatus.ACTIVE
            ).count()
            
            # Counts by content type
            content_type_stats = {}
            for content_type in ContentType:
                count = base_query.filter(
                    ContentFingerprint.content_type == content_type
                ).count()
                content_type_stats[content_type.value] = count
            
            # Counts by algorithm
            algorithm_stats = {}
            for algorithm in FingerprintAlgorithm:
                count = base_query.filter(
                    ContentFingerprint.algorithm == algorithm
                ).count()
                algorithm_stats[algorithm.value] = count
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_fingerprints = base_query.filter(
                ContentFingerprint.created_at >= thirty_days_ago
            ).count()
            
            statistics = {
                'total_fingerprints': total_fingerprints,
                'active_fingerprints': active_fingerprints,
                'inactive_fingerprints': total_fingerprints - active_fingerprints,
                'content_type_distribution': content_type_stats,
                'algorithm_distribution': algorithm_stats,
                'recent_activity_30_days': recent_fingerprints,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get content statistics: {str(e)}")
            return {'error': str(e)}
            
    def bulk_update_status(self,
                          fingerprint_ids: List[int],
                          new_status: FingerprintStatus) -> int:
        """        Bulk update fingerprint status for multiple fingerprints
        
        Args:
            fingerprint_ids: List of fingerprint IDs to update
            new_status: New status to set
            
        Returns:
            Number of updated fingerprints
        """        try:
            updated_count = self.db_session.query(ContentFingerprint).filter(
                ContentFingerprint.id.in_(fingerprint_ids)
            ).update(
                {
                    'status': new_status,
                    'updated_at': datetime.utcnow()
                },
                synchronize_session=False
            )
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(
                f"Bulk updated {updated_count} fingerprints to status {new_status.value}"
            )
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Failed to bulk update status: {str(e)}")
            raise RepositoryException(f"Bulk status update failed: {str(e)}")
            
    def delete_expired_fingerprints(self, retention_days: int = 365) -> int:
        """        Delete or archive fingerprints older than retention period
        
        Args:
            retention_days: Number of days to retain fingerprints
            
        Returns:
            Number of deleted fingerprints
        """        try:
            expiry_date = datetime.utcnow() - timedelta(days=retention_days)
            
            expired_fingerprints = self.db_session.query(ContentFingerprint).filter(
                and_(
                    ContentFingerprint.created_at < expiry_date,
                    ContentFingerprint.status != FingerprintStatus.ARCHIVED
                )
            )
            
            # Archive instead of hard delete
            deleted_count = expired_fingerprints.update(
                {
                    'status': FingerprintStatus.ARCHIVED,
                    'updated_at': datetime.utcnow()
                },
                synchronize_session=False
            )
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(
                f"Archived {deleted_count} expired fingerprints older than {retention_days} days"
            )
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to delete expired fingerprints: {str(e)}")
            raise RepositoryException(f"Expired fingerprint cleanup failed: {str(e)}")
            
    def get_user_content_summary(self, user_id: int) -> Dict[str, Any]:
        """        Get comprehensive content summary for a user
        
        Args:
            user_id: User ID to get summary for
            
        Returns:
            Dictionary containing user content summary
        """        try:
            user_fingerprints = self.get_by_user_id(user_id)
            
            if not user_fingerprints:
                return {
                    'user_id': user_id,
                    'total_content': 0,
                    'content_types': {},
                    'protection_coverage': 0.0,
                    'recent_uploads': 0,
                    'status_distribution': {}
                }
            
            # Content type distribution
            content_types = {}
            for fingerprint in user_fingerprints:
                content_type = fingerprint.content_type.value
                content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Status distribution
            status_distribution = {}
            for fingerprint in user_fingerprints:
                status = fingerprint.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Recent uploads (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_uploads = sum(
                1 for fp in user_fingerprints 
                if fp.created_at >= seven_days_ago
            )
            
            # Protection coverage
            active_fingerprints = sum(
                1 for fp in user_fingerprints 
                if fp.status == FingerprintStatus.ACTIVE
            )
            protection_coverage = active_fingerprints / len(user_fingerprints) * 100
            
            summary = {
                'user_id': user_id,
                'total_content': len(user_fingerprints),
                'content_types': content_types,
                'protection_coverage': round(protection_coverage, 2),
                'recent_uploads': recent_uploads,
                'status_distribution': status_distribution,
                'last_upload': max(fp.created_at for fp in user_fingerprints).isoformat(),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get user content summary: {str(e)}")
            return {'error': str(e), 'user_id': user_id}

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
