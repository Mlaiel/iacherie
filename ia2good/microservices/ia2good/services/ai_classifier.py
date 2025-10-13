"""AI classification service for cases"""
import re
from typing import Dict, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from models.case import Case


class AIClassifierService:
    """Service for AI-powered case classification"""
    
    URGENCY_KEYWORDS = {
        'critical': 5,
        'urgent': 4,
        'emergency': 5,
        'immediate': 4,
        'danger': 4,
        'risk': 3,
        'cold': 3,
        'injured': 4,
        'bleeding': 5,
        'unconscious': 5,
        'dying': 5,
        'fire': 5,
        'flood': 5,
        'accident': 4,
        'help': 2,
        'need': 2,
        'alone': 2,
        'lost': 3,
        'scared': 2,
        'sick': 3,
        'hungry': 2,
        'homeless': 2,
    }
    
    SKILL_KEYWORDS = {
        'medical': ['injured', 'bleeding', 'sick', 'health', 'wound', 'hospital', 'doctor', 'medicine'],
        'shelter': ['homeless', 'cold', 'housing', 'accommodation', 'sleep', 'bed', 'roof'],
        'food': ['hungry', 'food', 'meal', 'eat', 'starving', 'nutrition'],
        'transport': ['car', 'transport', 'move', 'travel', 'location', 'distance'],
        'legal': ['papers', 'documents', 'rights', 'law', 'legal', 'police'],
        'psychological': ['scared', 'alone', 'depressed', 'mental', 'traumatized', 'anxiety'],
        'animal': ['dog', 'cat', 'animal', 'pet', 'stray', 'veterinary'],
    }
    
    def __init__(self, db: Session = None):
        self.db = db
    
    def classify_case(self, case: Case) -> Dict:
        """
        Classify case using AI/NLP
        
        This is a simplified version. In production, this would:
        - Call OpenAI/Claude API
        - Use fine-tuned models
        - Perform entity extraction
        - Detect sentiment
        
        Args:
            case: Case object to classify
            
        Returns:
            Classification results
        """
        text = f"{case.title} {case.description}".lower()
        
        # Detect case type
        case_type = self._detect_type(text)
        
        # Detect urgency
        urgency = self.detect_urgency(text)
        
        # Detect required skills
        required_skills = self._detect_skills(text)
        
        # Extract entities (simplified)
        entities = self._extract_entities(text)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Confidence score (simplified)
        confidence = 0.85
        
        classification = {
            'type': case_type,
            'confidence': confidence,
            'urgency_detected': urgency,
            'skills_needed': required_skills,
            'entities': entities,
            'keywords': keywords,
            'language': 'fr',
            'sentiment': 'concerned',
            'recommended_actions': self._get_recommended_actions(case_type, urgency)
        }
        
        return classification
    
    def _detect_type(self, text: str) -> str:
        """
        Detect case type from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected type
        """
        # Simple keyword matching
        if any(word in text for word in ['homeless', 'sdf', 'sans-abri', 'rue']):
            return 'homeless'
        elif any(word in text for word in ['animal', 'dog', 'cat', 'chien', 'chat', 'pet']):
            return 'animal'
        elif any(word in text for word in ['emergency', 'urgent', 'danger', 'accident', 'fire']):
            return 'emergency'
        else:
            return 'other'
    
    def detect_urgency(self, text: str) -> int:
        """
        Detect urgency level from text
        
        Uses keyword matching with weighted scores
        
        Args:
            text: Text to analyze
            
        Returns:
            Urgency score (1-10)
        """
        base_score = 5  # Default medium urgency
        keyword_boost = 0
        
        # Check for urgency keywords
        for keyword, boost in self.URGENCY_KEYWORDS.items():
            if keyword in text:
                keyword_boost = max(keyword_boost, boost)
        
        # Adjust for multiple exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count >= 3:
            keyword_boost += 2
        elif exclamation_count >= 1:
            keyword_boost += 1
        
        # Check for time-sensitive words
        time_sensitive = ['now', 'immediately', 'today', 'maintenant', "aujourd'hui"]
        if any(word in text for word in time_sensitive):
            keyword_boost += 2
        
        final_score = min(base_score + keyword_boost, 10)
        return max(final_score, 1)
    
    def _detect_skills(self, text: str) -> List[str]:
        """
        Detect required skills from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of required skills
        """
        detected_skills = []
        
        for skill, keywords in self.SKILL_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                detected_skills.append(skill)
        
        return detected_skills or ['general']
    
    def _extract_entities(self, text: str) -> Dict:
        """
        Extract named entities (simplified)
        
        In production, use spaCy or similar NER
        
        Args:
            text: Text to analyze
            
        Returns:
            Extracted entities
        """
        entities = {
            'persons': [],
            'locations': [],
            'organizations': []
        }
        
        # Simple pattern matching for common entities
        # In production, use proper NER
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords
        
        Args:
            text: Text to analyze
            
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'a', 'à', 'the', 'a', 'an', 'and', 'or', 'but'}
        
        # Split and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get unique keywords (first 10)
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
            if len(unique_keywords) >= 10:
                break
        
        return unique_keywords
    
    def _get_recommended_actions(self, case_type: str, urgency: int) -> List[str]:
        """
        Get recommended actions based on case type and urgency
        
        Args:
            case_type: Type of case
            urgency: Urgency level
            
        Returns:
            List of recommended actions
        """
        actions = []
        
        if urgency >= 8:
            actions.append("Contact emergency services immediately")
            actions.append("Notify all available volunteers in 2km radius")
        elif urgency >= 6:
            actions.append("Assign high-priority volunteer")
            actions.append("Send immediate notifications")
        
        if case_type == 'homeless':
            actions.append("Contact local shelters")
            actions.append("Assign volunteers with shelter/food skills")
        elif case_type == 'animal':
            actions.append("Contact veterinary services")
            actions.append("Assign volunteers with animal care skills")
        elif case_type == 'emergency':
            actions.append("Verify emergency services contacted")
            actions.append("Assign multiple volunteers if needed")
        
        return actions
    
    def detect_duplicates(
        self,
        case: Case,
        radius_meters: float = 100.0,
        time_window_hours: int = 48
    ) -> List[Tuple[Case, float]]:
        """
        Detect similar/duplicate cases
        
        Logic:
        1. Geographic proximity (< 100m)
        2. Textual similarity (TF-IDF)
        3. Temporal proximity (< 48h)
        4. Return cases with similarity > 80%
        
        Args:
            case: Case to check
            radius_meters: Geographic radius
            time_window_hours: Time window
            
        Returns:
            List of (similar_case, similarity_score) tuples
        """
        if not self.db:
            return []
        
        # TODO: Implement with PostGIS geographic queries
        # TODO: Implement text similarity with TF-IDF
        # TODO: Filter by time window
        
        similar_cases = []
        
        return similar_cases
    
    def analyze_trends(self, cases: List[Case]) -> Dict:
        """
        Analyze trends across multiple cases
        
        Args:
            cases: List of cases to analyze
            
        Returns:
            Trend analysis
        """
        if not cases:
            return {}
        
        # Type distribution
        type_counts = {}
        urgency_avg = 0
        common_skills = {}
        
        for case in cases:
            # Count types
            case_type = case.type
            type_counts[case_type] = type_counts.get(case_type, 0) + 1
            
            # Average urgency
            urgency_avg += case.urgency_level or 5
            
            # Common skills
            if case.ai_classification:
                skills = case.ai_classification.get('skills_needed', [])
                for skill in skills:
                    common_skills[skill] = common_skills.get(skill, 0) + 1
        
        urgency_avg = urgency_avg / len(cases)
        
        # Top skills needed
        top_skills = sorted(common_skills.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_cases': len(cases),
            'type_distribution': type_counts,
            'average_urgency': round(urgency_avg, 2),
            'top_skills_needed': [skill for skill, count in top_skills],
            'skill_demand': dict(top_skills)
        }
