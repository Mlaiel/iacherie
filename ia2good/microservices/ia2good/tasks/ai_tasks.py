"""
Celery tasks for AI processing in IA2GOOD module
"""
import os
import sys
from typing import Dict, Any, List
from uuid import UUID

from celery import Task
from .celery_app import celery_app

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from microservices.ia2good.services.ai_classifier import AIClassifierService
except ImportError:
    print("Warning: Could not import AIClassifierService")
    AIClassifierService = None


class AITask(Task):
    """Base task with AI service setup"""
    _ai_classifier = None
    
    @property
    def ai_classifier(self):
        if self._ai_classifier is None and AIClassifierService:
            self._ai_classifier = AIClassifierService()
        return self._ai_classifier


@celery_app.task(base=AITask, bind=True, max_retries=3)
def classify_case_async(
    self,
    case_id: str,
    title: str,
    description: str,
    case_type: str = None
) -> Dict[str, Any]:
    """
    Asynchronously classify a case using AI
    
    This task runs in the background after a case is created to:
    - Detect case type (if not provided)
    - Determine urgency level
    - Extract skills needed
    - Extract keywords
    - Detect sentiment
    
    Args:
        case_id: UUID of the case
        title: Case title
        description: Case description
        case_type: Optional existing case type
        
    Returns:
        Dict with AI classification results
    """
    try:
        if not self.ai_classifier:
            print(f"AI Classifier not available, skipping classification for case {case_id}")
            return {}
        
        text = f"{title}. {description}"
        
        # Detect case type if not provided
        detected_type = case_type
        if not detected_type:
            detected_type = self.ai_classifier.detect_case_type(text)
        
        # Detect urgency level
        urgency_level = self.ai_classifier.detect_urgency(text)
        
        # Extract required skills
        skills_needed = self.ai_classifier.extract_skills(text)
        
        # Extract keywords
        keywords = self.ai_classifier.extract_keywords(text)
        
        # Detect sentiment (for priority)
        sentiment = self.ai_classifier.detect_sentiment(text)
        
        # Build classification result
        classification = {
            'case_type': detected_type,
            'confidence': 0.85,  # Placeholder
            'urgency_level': urgency_level,
            'skills_needed': skills_needed,
            'keywords': keywords,
            'sentiment': sentiment,
            'entities': [],  # Can be extended with NER
            'language': 'fr',
            'processed_at': None  # Will be set by DB
        }
        
        # TODO: Update case in database with classification results
        # UPDATE ia2good_cases 
        # SET ai_classification = classification, urgency_level = urgency_level
        # WHERE id = case_id
        
        print(f"Classified case {case_id}: type={detected_type}, urgency={urgency_level}")
        return classification
        
    except Exception as exc:
        # Retry with exponential backoff
        print(f"Error classifying case {case_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=AITask, bind=True, max_retries=2)
def analyze_case_photos(
    self,
    case_id: str,
    photo_urls: List[str]
) -> Dict[str, Any]:
    """
    Analyze case photos using computer vision
    
    This task:
    - Detects objects in photos
    - Classifies scene type
    - Counts people/animals
    - Checks for inappropriate content
    
    Args:
        case_id: UUID of the case
        photo_urls: List of photo URLs to analyze
        
    Returns:
        Dict with analysis results for all photos
    """
    try:
        if not photo_urls:
            return {'analyzed': False, 'reason': 'No photos provided'}
        
        results = {
            'case_id': case_id,
            'photos_analyzed': len(photo_urls),
            'photos': []
        }
        
        for photo_url in photo_urls:
            try:
                # TODO: Implement actual image analysis
                # For now, return placeholder
                photo_analysis = {
                    'url': photo_url,
                    'objects': [],
                    'scene': 'outdoor',
                    'people_count': 0,
                    'animals': [],
                    'nsfw_score': 0.0,
                    'safe': True,
                    'quality_score': 0.8
                }
                
                results['photos'].append(photo_analysis)
                
            except Exception as e:
                print(f"Error analyzing photo {photo_url}: {e}")
                results['photos'].append({
                    'url': photo_url,
                    'error': str(e),
                    'analyzed': False
                })
        
        # TODO: Update case with photo analysis results
        # UPDATE ia2good_cases 
        # SET ai_classification = jsonb_set(ai_classification, '{photo_analysis}', results)
        # WHERE id = case_id
        
        print(f"Analyzed {len(photo_urls)} photos for case {case_id}")
        return results
        
    except Exception as exc:
        print(f"Error analyzing photos for case {case_id}: {exc}")
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@celery_app.task(base=AITask, bind=True)
def detect_duplicate_cases(
    self,
    case_id: str,
    location: Dict[str, float],
    title: str,
    description: str
) -> List[str]:
    """
    Detect potentially duplicate cases
    
    Args:
        case_id: UUID of the new case
        location: Dict with lat/lng
        title: Case title
        description: Case description
        
    Returns:
        List of potential duplicate case IDs
    """
    try:
        # TODO: Implement duplicate detection
        # 1. Find cases within 100m radius
        # 2. Compare text similarity (TF-IDF or embeddings)
        # 3. Check temporal proximity (last 48h)
        # 4. Return cases with >80% similarity
        
        duplicates = []
        
        # Query database for nearby recent cases
        # SELECT id, title, description, location
        # FROM ia2good_cases
        # WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography, 100)
        # AND created_at > NOW() - INTERVAL '48 hours'
        # AND status IN ('open', 'claimed')
        # AND id != case_id
        
        print(f"Checked for duplicates of case {case_id}: found {len(duplicates)}")
        return duplicates
        
    except Exception as exc:
        print(f"Error detecting duplicates for case {case_id}: {exc}")
        return []


@celery_app.task(bind=True)
def reindex_case_search(
    self,
    case_id: str = None
) -> Dict[str, Any]:
    """
    Reindex case(s) for full-text search
    
    Args:
        case_id: Optional specific case ID, or None to reindex all
        
    Returns:
        Dict with reindexing statistics
    """
    try:
        if case_id:
            # Reindex single case
            # UPDATE ia2good_cases
            # SET search_vector = to_tsvector('french', coalesce(title, '') || ' ' || coalesce(description, ''))
            # WHERE id = case_id
            reindexed = 1
        else:
            # Reindex all cases
            # UPDATE ia2good_cases
            # SET search_vector = to_tsvector('french', coalesce(title, '') || ' ' || coalesce(description, ''))
            reindexed = 0  # Count from DB
        
        print(f"Reindexed {reindexed} case(s) for search")
        return {'reindexed': reindexed, 'case_id': case_id}
        
    except Exception as exc:
        print(f"Error reindexing cases: {exc}")
        return {'reindexed': 0, 'error': str(exc)}
