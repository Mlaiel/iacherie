"""Content Verification Service for Protection System

This module provides advanced content verification capabilities:
- Automated verification of detected violations
- Human-in-the-loop verification workflows
- Machine learning-based verification scoring
- Content authenticity verification
- Ownership verification through blockchain integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import aiohttp
from PIL import Image
import numpy as np

# Machine learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Blockchain verification (placeholder for future implementation)
import hashlib
import base64

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ViolationAlert
from ...config.settings import get_settings
from .violation_detector import ViolationEvidence, ViolationType, ViolationSeverity

logger = get_logger(__name__)
settings = get_settings()


class VerificationStatus(Enum):
    """Status of verification process"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED_VALID = "verified_valid"
    VERIFIED_INVALID = "verified_invalid"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    DISPUTED = "disputed"
    EXPIRED = "expired"


class VerificationMethod(Enum):
    """Methods used for verification"""    AUTOMATED_ML = "automated_ml"
    CROWDSOURCE = "crowdsource"
    EXPERT_REVIEW = "expert_review"
    BLOCKCHAIN = "blockchain"
    METADATA_ANALYSIS = "metadata_analysis"
    REVERSE_IMAGE_SEARCH = "reverse_image_search"


@dataclass
class VerificationResult:
    """Result of content verification"""    verification_id: str
    violation_evidence: ViolationEvidence
    status: VerificationStatus
    confidence_score: float
    verification_methods: List[VerificationMethod] = field(default_factory=list)
    human_reviewers: List[str] = field(default_factory=list)
    automated_scores: Dict[str, float] = field(default_factory=dict)
    evidence_quality: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    notes: str = ""


@dataclass
class HumanReviewTask:
    """Human review task for content verification"""    task_id: str
    violation_evidence: ViolationEvidence
    priority: int = 5  # 1-10, higher is more urgent
    assigned_reviewer: Optional[str] = None
    deadline: Optional[datetime] = None
    compensation: float = 0.0
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)


class MLVerificationModel:
    """Machine learning model for automated verification"""    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.is_trained = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize ML model for verification"""        try:
            # Try to load pre-trained model
            model_path = Path("models/verification_model.joblib")
            scaler_path = Path("models/verification_scaler.joblib")
            
            if model_path.exists() and scaler_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                logger.info("Loaded pre-trained verification model")
            else:
                # Initialize new model
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
                self.scaler = StandardScaler()
                logger.info("Initialized new verification model")
                
        except Exception as e:
            logger.error(f"Error initializing ML model: {e}")
            # Fallback to simple model
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.scaler = StandardScaler()
    
    def extract_features(self, evidence: ViolationEvidence) -> np.ndarray:
        """Extract features from violation evidence for ML prediction"""        features = []
        
        # Similarity score features
        if evidence.similarity_scores:
            similarities = [s.similarity_score for s in evidence.similarity_scores]
            features.extend([
                max(similarities),
                np.mean(similarities),
                np.std(similarities),
                len(similarities)
            ])
            
            # Hash match indicators
            hash_matches = sum(1 for s in evidence.similarity_scores if s.hash_match)
            features.append(hash_matches / len(similarities))
            
            # Vector similarity features
            vector_sims = [s.vector_similarity for s in evidence.similarity_scores if s.vector_similarity is not None]
            if vector_sims:
                features.extend([max(vector_sims), np.mean(vector_sims)])
            else:
                features.extend([0.0, 0.0])
        else:
            features.extend([0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0])
        
        # Violation type and severity
        violation_type_scores = {
            ViolationType.EXACT_DUPLICATE: 1.0,
            ViolationType.MODIFIED_CONTENT: 0.8,
            ViolationType.DERIVATIVE_WORK: 0.6,
            ViolationType.PARTIAL_USAGE: 0.4,
            ViolationType.UNAUTHORIZED_REMIX: 0.3,
            ViolationType.THUMBNAIL_THEFT: 0.2,
            ViolationType.METADATA_COPYING: 0.1
        }
        features.append(violation_type_scores.get(evidence.violation_type, 0.0))
        
        severity_scores = {
            ViolationSeverity.CRITICAL: 1.0,
            ViolationSeverity.HIGH: 0.8,
            ViolationSeverity.MEDIUM: 0.6,
            ViolationSeverity.LOW: 0.4,
            ViolationSeverity.SUSPICIOUS: 0.2
        }
        features.append(severity_scores.get(evidence.severity, 0.0))
        
        # URL and domain features
        url_features = self._extract_url_features(evidence.detected_url)
        features.extend(url_features)
        
        # Temporal features
        age_hours = (datetime.utcnow() - evidence.timestamp).total_seconds() / 3600
        features.extend([
            age_hours,
            1.0 if age_hours < 24 else 0.0,  # Recent detection
            1.0 if age_hours < 1 else 0.0    # Very recent detection
        ])
        
        # False positive score
        features.append(evidence.false_positive_score)
        
        # Evidence quality indicators
        features.extend([
            len(evidence.screenshots) / 5.0,  # Normalized screenshot count
            1.0 if evidence.metadata else 0.0,
            len(str(evidence.metadata)) / 1000.0  # Normalized metadata length
        ])
        
        return np.array(features)
    
    def _extract_url_features(self, url: str) -> List[float]:
        """Extract features from URL"""        from urllib.parse import urlparse
        
        features = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Platform indicators
            platform_scores = {
                'youtube.com': 0.9,
                'instagram.com': 0.8,
                'tiktok.com': 0.7,
                'twitter.com': 0.6,
                'facebook.com': 0.8,
                'soundcloud.com': 0.7
            }
            
            platform_score = max([score for pattern, score in platform_scores.items() 
                                if pattern in domain] + [0.0])
            features.append(platform_score)
            
            # Domain characteristics
            features.extend([
                len(domain) / 50.0,  # Normalized domain length
                domain.count('.') / 5.0,  # Subdomain count
                1.0 if domain.endswith('.com') else 0.0,
                1.0 if any(keyword in domain for keyword in ['media', 'content', 'share']) else 0.0
            ])
            
            # Path characteristics
            path = parsed.path.lower()
            features.extend([
                len(path) / 100.0,  # Normalized path length
                path.count('/') / 10.0,  # Path depth
                1.0 if 'download' in path else 0.0,
                1.0 if any(ext in path for ext in ['.mp3', '.mp4', '.jpg', '.png']) else 0.0
            ])
            
        except Exception:
            # Fallback features
            features = [0.0] * 9
        
        return features
    
    async def predict_verification(self, evidence: ViolationEvidence) -> Tuple[float, Dict[str, float]]:
        """Predict verification result using ML model"""        try:
            if not self.is_trained:
                # Return conservative estimate if model not trained
                return 0.5, {'ml_confidence': 0.3}
            
            # Extract features
            features = self.extract_features(evidence)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            
            # Assuming binary classification (valid/invalid)
            confidence = max(prediction_proba)
            validity_score = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
            
            scores = {
                'ml_confidence': float(confidence),
                'validity_score': float(validity_score),
                'feature_count': len(features)
            }
            
            return float(validity_score), scores
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return 0.5, {'error': str(e)}
    
    def update_model(self, training_data: List[Tuple[ViolationEvidence, bool]]):
        """Update model with new training data"""        try:
            if len(training_data) < 10:
                logger.warning("Insufficient training data for model update")
                return
            
            # Extract features and labels
            X = []
            y = []
            
            for evidence, is_valid in training_data:
                features = self.extract_features(evidence)
                X.append(features)
                y.append(1 if is_valid else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model
            model_path = Path("models")
            model_path.mkdir(exist_ok=True)
            
            joblib.dump(self.model, model_path / "verification_model.joblib")
            joblib.dump(self.scaler, model_path / "verification_scaler.joblib")
            
            logger.info(f"Updated verification model with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Error updating ML model: {e}")


class MetadataAnalyzer:
    """Analyzer for content metadata verification"""    
    async def analyze_metadata(self, evidence: ViolationEvidence) -> Dict[str, float]:
        """Analyze metadata for verification clues"""        scores = {}
        
        try:
            metadata = evidence.metadata
            
            # Copyright indicators
            copyright_indicators = [
                'copyright', '©', '(c)', 'all rights reserved',
                'unauthorized use', 'permission required'
            ]
            
            copyright_score = 0.0
            metadata_text = str(metadata).lower()
            
            for indicator in copyright_indicators:
                if indicator in metadata_text:
                    copyright_score += 0.2
            
            scores['copyright_indicators'] = min(1.0, copyright_score)
            
            # Attribution indicators
            attribution_indicators = [
                'creative commons', 'cc by', 'public domain',
                'fair use', 'attribution', 'source:'
            ]
            
            attribution_score = 0.0
            for indicator in attribution_indicators:
                if indicator in metadata_text:
                    attribution_score += 0.3
            
            scores['attribution_indicators'] = min(1.0, attribution_score)
            
            # Quality indicators
            if 'title' in metadata:
                scores['has_title'] = 1.0
            if 'description' in metadata:
                scores['has_description'] = 1.0
            if 'tags' in metadata or 'keywords' in metadata:
                scores['has_tags'] = 1.0
            
            # Timestamp analysis
            if 'upload_date' in metadata or 'created_at' in metadata:
                scores['has_timestamp'] = 1.0
                
                # Check if content is very recent (might indicate violation)
                try:
                    upload_date = metadata.get('upload_date') or metadata.get('created_at')
                    if isinstance(upload_date, str):
                        upload_time = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        age_hours = (datetime.utcnow() - upload_time).total_seconds() / 3600
                        scores['content_age_hours'] = age_hours
                        scores['very_recent'] = 1.0 if age_hours < 24 else 0.0
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error analyzing metadata: {e}")
        
        return scores


class ReverseSearchAnalyzer:
    """Analyzer using reverse image/content search"""    
    async def perform_reverse_search(self, evidence: ViolationEvidence) -> Dict[str, Any]:
        """Perform reverse search analysis"""        results = {}
        
        try:
            # For images, we could use Google Images API or TinEye
            # For now, implement a simplified version
            
            if evidence.screenshots:
                results['reverse_search_results'] = await self._reverse_image_search(evidence.screenshots[0])
            
            # For other content types, analyze URL patterns
            results['url_analysis'] = self._analyze_url_patterns(evidence.detected_url)
            
        except Exception as e:
            logger.error(f"Error in reverse search: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _reverse_image_search(self, image_path: str) -> Dict[str, Any]:
        """Perform reverse image search (simplified implementation)"""        try:
            # This would integrate with actual reverse image search APIs
            # For now, return placeholder results
            
            return {
                'similar_images_found': 5,
                'oldest_match_date': '2023-01-15',
                'most_popular_source': 'stock_photo_site.com',
                'confidence': 0.7
            }
            
        except Exception as e:
            logger.error(f"Error in reverse image search: {e}")
            return {}
    
    def _analyze_url_patterns(self, url: str) -> Dict[str, Any]:
        """Analyze URL for suspicious patterns"""        analysis = {}
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Check for suspicious URL patterns
            suspicious_patterns = [
                'download', 'mirror', 'copy', 'backup',
                'leaked', 'free', 'crack', 'pirate'
            ]
            
            url_lower = url.lower()
            suspicious_score = sum(1 for pattern in suspicious_patterns if pattern in url_lower)
            
            analysis.update({
                'suspicious_keywords': suspicious_score,
                'domain_reputation': self._check_domain_reputation(parsed.netloc),
                'url_length': len(url),
                'has_tracking_params': '?utm_' in url or '&utm_' in url
            })
            
        except Exception as e:
            logger.error(f"Error analyzing URL patterns: {e}")
        
        return analysis
    
    def _check_domain_reputation(self, domain: str) -> float:
        """Check domain reputation (simplified implementation)"""        # In production, this would check against reputation databases
        
        known_good_domains = [
            'youtube.com', 'instagram.com', 'twitter.com',
            'spotify.com', 'soundcloud.com', 'vimeo.com'
        ]
        
        known_bad_patterns = [
            'download', 'pirate', 'leak', 'free',
            'crack', 'warez', 'torrent'
        ]
        
        domain_lower = domain.lower()
        
        if any(good_domain in domain_lower for good_domain in known_good_domains):
            return 0.9
        
        if any(bad_pattern in domain_lower for bad_pattern in known_bad_patterns):
            return 0.1
        
        return 0.5  # Neutral reputation


class BlockchainVerifier:
    """Blockchain-based content verification (future implementation)"""    
    async def verify_ownership(self, evidence: ViolationEvidence) -> Dict[str, Any]:
        """Verify content ownership using blockchain records"""        # Placeholder for future blockchain integration
        return {
            'blockchain_verified': False,
            'ownership_record_found': False,
            'verification_method': 'placeholder'
        }
    
    def create_content_hash(self, content_data: bytes) -> str:
        """Create blockchain-compatible content hash"""        sha256_hash = hashlib.sha256(content_data).hexdigest()
        return base64.b64encode(sha256_hash.encode()).decode()


class VerificationService:
    """Main verification service coordinating all verification methods"""    
    def __init__(self):
        self.ml_model = MLVerificationModel()
        self.metadata_analyzer = MetadataAnalyzer()
        self.reverse_search_analyzer = ReverseSearchAnalyzer()
        self.blockchain_verifier = BlockchainVerifier()
        
        # Human review management
        self.human_review_tasks: Dict[str, HumanReviewTask] = {}
        self.verification_results: Dict[str, VerificationResult] = {}
        
        # Configuration
        self.auto_verification_threshold = 0.85
        self.human_review_threshold = 0.60
    
    async def verify_violation(self, evidence: ViolationEvidence) -> VerificationResult:
        """Perform comprehensive verification of violation evidence"""        verification_id = f"verify_{evidence.violation_id}_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Initialize result
            result = VerificationResult(
                verification_id=verification_id,
                violation_evidence=evidence,
                status=VerificationStatus.IN_PROGRESS
            )
            
            # Step 1: Automated ML verification
            ml_score, ml_details = await self.ml_model.predict_verification(evidence)
            result.automated_scores['ml_verification'] = ml_score
            result.automated_scores.update(ml_details)
            result.verification_methods.append(VerificationMethod.AUTOMATED_ML)
            
            # Step 2: Metadata analysis
            metadata_scores = await self.metadata_analyzer.analyze_metadata(evidence)
            result.automated_scores.update(metadata_scores)
            result.verification_methods.append(VerificationMethod.METADATA_ANALYSIS)
            
            # Step 3: Reverse search analysis
            reverse_search_results = await self.reverse_search_analyzer.perform_reverse_search(evidence)
            result.automated_scores.update(reverse_search_results)
            result.verification_methods.append(VerificationMethod.REVERSE_IMAGE_SEARCH)
            
            # Step 4: Blockchain verification (if available)
            blockchain_results = await self.blockchain_verifier.verify_ownership(evidence)
            result.automated_scores.update(blockchain_results)
            if blockchain_results.get('blockchain_verified'):
                result.verification_methods.append(VerificationMethod.BLOCKCHAIN)
            
            # Calculate overall confidence
            result.confidence_score = self._calculate_overall_confidence(result.automated_scores)
            
            # Determine verification status
            if result.confidence_score >= self.auto_verification_threshold:
                result.status = VerificationStatus.VERIFIED_VALID
            elif result.confidence_score <= (1.0 - self.auto_verification_threshold):
                result.status = VerificationStatus.VERIFIED_INVALID
            elif result.confidence_score >= self.human_review_threshold:
                result.status = VerificationStatus.NEEDS_HUMAN_REVIEW
                await self._create_human_review_task(evidence, result)
            else:
                result.status = VerificationStatus.VERIFIED_INVALID
                result.notes = "Low confidence, marked as invalid"
            
            # Store result
            self.verification_results[verification_id] = result
            
            logger.info(f"Verification completed: {verification_id}, confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in verification: {e}")
            result.status = VerificationStatus.PENDING
            result.notes = f"Verification error: {str(e)}"
            return result
    
    def _calculate_overall_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate overall confidence from individual scores"""        try:
            # Weight different verification methods
            weights = {
                'ml_verification': 0.4,
                'validity_score': 0.3,
                'copyright_indicators': 0.1,
                'attribution_indicators': -0.1,  # Negative weight (indicates legitimate use)
                'suspicious_keywords': -0.1,
                'domain_reputation': 0.2
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for score_name, weight in weights.items():
                if score_name in scores:
                    weighted_score += scores[score_name] * weight
                    total_weight += abs(weight)
            
            if total_weight > 0:
                confidence = weighted_score / total_weight
                return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            else:
                return 0.5  # Default confidence
                
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    async def _create_human_review_task(self, evidence: ViolationEvidence, verification_result: VerificationResult):
        """Create human review task for manual verification"""        try:
            task_id = f"review_{evidence.violation_id}_{int(datetime.utcnow().timestamp())}"
            
            # Determine priority based on severity and confidence
            priority = 5  # Default
            if evidence.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]:
                priority = 8
            elif verification_result.confidence_score > 0.8:
                priority = 7
            elif verification_result.confidence_score < 0.4:
                priority = 3
            
            task = HumanReviewTask(
                task_id=task_id,
                violation_evidence=evidence,
                priority=priority,
                deadline=datetime.utcnow() + timedelta(hours=48),  # 48 hour deadline
                compensation=5.0 if priority >= 7 else 3.0  # Higher pay for urgent tasks
            )
            
            self.human_review_tasks[task_id] = task
            
            # In production, this would notify human reviewers
            logger.info(f"Created human review task: {task_id}, priority: {priority}")
            
        except Exception as e:
            logger.error(f"Error creating human review task: {e}")
    
    async def submit_human_review(self, task_id: str, reviewer_id: str, is_valid: bool, notes: str = "") -> bool:
        """Submit human review result"""        try:
            if task_id not in self.human_review_tasks:
                return False
            
            task = self.human_review_tasks[task_id]
            task.status = "completed"
            task.assigned_reviewer = reviewer_id
            
            # Update verification result
            verification_id = None
            for vid, result in self.verification_results.items():
                if result.violation_evidence.violation_id == task.violation_evidence.violation_id:
                    verification_id = vid
                    break
            
            if verification_id:
                result = self.verification_results[verification_id]
                result.status = VerificationStatus.VERIFIED_VALID if is_valid else VerificationStatus.VERIFIED_INVALID
                result.human_reviewers.append(reviewer_id)
                result.verification_methods.append(VerificationMethod.EXPERT_REVIEW)
                result.notes = notes
                
                # Update confidence based on human review
                if is_valid:
                    result.confidence_score = max(result.confidence_score, 0.9)
                else:
                    result.confidence_score = min(result.confidence_score, 0.1)
                
                # Use this data to improve ML model
                training_data = [(task.violation_evidence, is_valid)]
                self.ml_model.update_model(training_data)
            
            logger.info(f"Human review submitted for task {task_id}: {'valid' if is_valid else 'invalid'}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting human review: {e}")
            return False
    
    def get_pending_human_reviews(self, reviewer_id: Optional[str] = None) -> List[HumanReviewTask]:
        """Get pending human review tasks"""        pending_tasks = [
            task for task in self.human_review_tasks.values()
            if task.status == "open" and (reviewer_id is None or task.assigned_reviewer == reviewer_id)
        ]
        
        # Sort by priority and deadline
        pending_tasks.sort(key=lambda t: (-t.priority, t.deadline or datetime.max))
        
        return pending_tasks
    
    def get_verification_result(self, verification_id: str) -> Optional[VerificationResult]:
        """Get verification result by ID"""        return self.verification_results.get(verification_id)
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification system statistics"""        total_verifications = len(self.verification_results)
        
        if total_verifications == 0:
            return {'total_verifications': 0}
        
        status_counts = {}
        for result in self.verification_results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_confidence = np.mean([r.confidence_score for r in self.verification_results.values()])
        
        human_reviews_total = len(self.human_review_tasks)
        human_reviews_completed = sum(1 for task in self.human_review_tasks.values() if task.status == "completed")
        
        return {
            'total_verifications': total_verifications,
            'status_distribution': status_counts,
            'average_confidence': float(avg_confidence),
            'human_reviews_total': human_reviews_total,
            'human_reviews_completed': human_reviews_completed,
            'human_review_completion_rate': human_reviews_completed / human_reviews_total if human_reviews_total > 0 else 0,
            'ml_model_trained': self.ml_model.is_trained,
            'verification_methods_used': list(set(
                method.value for result in self.verification_results.values()
                for method in result.verification_methods
            ))
        }
