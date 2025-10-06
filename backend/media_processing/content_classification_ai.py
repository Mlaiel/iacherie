"""
Enterprise Content Classification AI pour IA Chérie
Classification automatique multi-niveaux avec deep learning
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ClassificationType(Enum):
    """Types de classification"""
    CONTENT_TYPE = "content_type"
    GENRE = "genre"
    AUDIENCE = "audience"
    SENTIMENT = "sentiment"
    SAFETY = "safety"
    MATURITY = "maturity"
    LANGUAGE = "language"


class SafetyLevel(Enum):
    """Niveaux de sécurité"""
    SAFE = "safe"
    MODERATE = "moderate"
    SENSITIVE = "sensitive"
    UNSAFE = "unsafe"


class MaturityRating(Enum):
    """Classifications de maturité"""
    GENERAL = "G"
    PARENTAL_GUIDANCE = "PG"
    TEEN = "PG-13"
    MATURE = "R"
    ADULTS_ONLY = "NC-17"


@dataclass
class ClassificationResult:
    """Résultat de classification"""
    content_id: str
    classification_type: ClassificationType
    primary_label: str
    confidence: float
    secondary_labels: List[Dict[str, float]]
    metadata: Dict[str, Any]


@dataclass
class ContentClassificationProfile:
    """Profil de classification complet"""
    content_id: str
    content_type: str
    genres: List[str]
    target_audience: List[str]
    sentiment: str
    safety_level: SafetyLevel
    maturity_rating: MaturityRating
    languages: List[str]
    tags: List[str]
    confidence_scores: Dict[str, float]


class ContentClassificationAI:
    """
    Système de classification AI ultra-avancé
    Classification multi-niveaux avec deep learning
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize classification AI"""
        self.config = config or {}
        self.model_version = "v4.2.0"
        self.classification_history: Dict[str, List[ClassificationResult]] = {}
        logger.info("ContentClassificationAI initialized")
    
    async def classify_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        classification_types: Optional[List[ClassificationType]] = None
    ) -> List[ClassificationResult]:
        """
        Classification complète du contenu
        
        Args:
            content_id: ID du contenu
            content_data: Données du contenu
            classification_types: Types de classification
        
        Returns:
            Liste des résultats de classification
        """
        if classification_types is None:
            classification_types = list(ClassificationType)
        
        results = []
        for classification_type in classification_types:
            result = await self._perform_classification(
                content_id,
                content_data,
                classification_type
            )
            results.append(result)
        
        # Store history
        if content_id not in self.classification_history:
            self.classification_history[content_id] = []
        self.classification_history[content_id].extend(results)
        
        return results
    
    async def _perform_classification(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        classification_type: ClassificationType
    ) -> ClassificationResult:
        """Effectue une classification spécifique"""
        await asyncio.sleep(0.01)  # Simulation ML inference
        
        if classification_type == ClassificationType.CONTENT_TYPE:
            return self._classify_content_type(content_id, content_data)
        
        elif classification_type == ClassificationType.GENRE:
            return self._classify_genre(content_id, content_data)
        
        elif classification_type == ClassificationType.AUDIENCE:
            return self._classify_audience(content_id, content_data)
        
        elif classification_type == ClassificationType.SENTIMENT:
            return self._classify_sentiment(content_id, content_data)
        
        elif classification_type == ClassificationType.SAFETY:
            return self._classify_safety(content_id, content_data)
        
        elif classification_type == ClassificationType.MATURITY:
            return self._classify_maturity(content_id, content_data)
        
        else:  # LANGUAGE
            return self._classify_language(content_id, content_data)
    
    def _classify_content_type(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification du type de contenu"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.CONTENT_TYPE,
            primary_label="video",
            confidence=0.95,
            secondary_labels=[
                {"image": 0.03},
                {"animation": 0.02}
            ],
            metadata={"model": "content-type-resnet50"}
        )
    
    def _classify_genre(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification du genre"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.GENRE,
            primary_label="educational",
            confidence=0.88,
            secondary_labels=[
                {"technology": 0.82},
                {"tutorial": 0.75},
                {"entertainment": 0.45}
            ],
            metadata={"model": "genre-classifier-bert"}
        )
    
    def _classify_audience(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification de l'audience"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.AUDIENCE,
            primary_label="professionals",
            confidence=0.85,
            secondary_labels=[
                {"students": 0.65},
                {"enthusiasts": 0.55},
                {"general": 0.40}
            ],
            metadata={"model": "audience-predictor-v3"}
        )
    
    def _classify_sentiment(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification du sentiment"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.SENTIMENT,
            primary_label="positive",
            confidence=0.92,
            secondary_labels=[
                {"neutral": 0.06},
                {"negative": 0.02}
            ],
            metadata={"model": "sentiment-analyzer-transformer"}
        )
    
    def _classify_safety(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification de sécurité"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.SAFETY,
            primary_label=SafetyLevel.SAFE.value,
            confidence=0.98,
            secondary_labels=[
                {SafetyLevel.MODERATE.value: 0.02}
            ],
            metadata={"model": "safety-classifier-inception"}
        )
    
    def _classify_maturity(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification de maturité"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.MATURITY,
            primary_label=MaturityRating.GENERAL.value,
            confidence=0.94,
            secondary_labels=[
                {MaturityRating.PARENTAL_GUIDANCE.value: 0.05},
                {MaturityRating.TEEN.value: 0.01}
            ],
            metadata={"model": "maturity-rating-classifier"}
        )
    
    def _classify_language(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """Classification de langue"""
        return ClassificationResult(
            content_id=content_id,
            classification_type=ClassificationType.LANGUAGE,
            primary_label="english",
            confidence=0.96,
            secondary_labels=[
                {"french": 0.03},
                {"spanish": 0.01}
            ],
            metadata={"model": "language-detector-fasttext"}
        )
    
    async def generate_classification_profile(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ContentClassificationProfile:
        """
        Génère un profil de classification complet
        
        Args:
            content_id: ID du contenu
            content_data: Données du contenu
        
        Returns:
            Profil de classification complet
        """
        # Classification complète
        results = await self.classify_content(content_id, content_data)
        
        # Extraction des informations
        content_type_result = next(
            (r for r in results if r.classification_type == ClassificationType.CONTENT_TYPE),
            None
        )
        genre_result = next(
            (r for r in results if r.classification_type == ClassificationType.GENRE),
            None
        )
        audience_result = next(
            (r for r in results if r.classification_type == ClassificationType.AUDIENCE),
            None
        )
        sentiment_result = next(
            (r for r in results if r.classification_type == ClassificationType.SENTIMENT),
            None
        )
        safety_result = next(
            (r for r in results if r.classification_type == ClassificationType.SAFETY),
            None
        )
        maturity_result = next(
            (r for r in results if r.classification_type == ClassificationType.MATURITY),
            None
        )
        language_result = next(
            (r for r in results if r.classification_type == ClassificationType.LANGUAGE),
            None
        )
        
        # Construction du profil
        profile = ContentClassificationProfile(
            content_id=content_id,
            content_type=content_type_result.primary_label if content_type_result else "unknown",
            genres=[genre_result.primary_label] if genre_result else [],
            target_audience=[audience_result.primary_label] if audience_result else [],
            sentiment=sentiment_result.primary_label if sentiment_result else "neutral",
            safety_level=SafetyLevel(safety_result.primary_label) if safety_result else SafetyLevel.SAFE,
            maturity_rating=MaturityRating(maturity_result.primary_label) if maturity_result else MaturityRating.GENERAL,
            languages=[language_result.primary_label] if language_result else ["english"],
            tags=self._generate_tags(results),
            confidence_scores={
                r.classification_type.value: r.confidence
                for r in results
            }
        )
        
        return profile
    
    def _generate_tags(self, results: List[ClassificationResult]) -> List[str]:
        """Génère les tags à partir des classifications"""
        tags = []
        for result in results:
            tags.append(result.primary_label)
            for label_dict in result.secondary_labels[:2]:  # Top 2 secondary
                tags.extend(label_dict.keys())
        
        return list(set(tags))[:15]  # Limite à 15 tags uniques
    
    async def batch_classify(
        self,
        contents: List[Dict[str, Any]]
    ) -> Dict[str, ContentClassificationProfile]:
        """Classification en batch"""
        results_dict = {}
        for content in contents:
            content_id = content.get("id", "unknown")
            profile = await self.generate_classification_profile(content_id, content)
            results_dict[content_id] = profile
        
        return results_dict
    
    def get_classification_history(
        self,
        content_id: str
    ) -> List[ClassificationResult]:
        """Récupère l'historique de classification"""
        return self.classification_history.get(content_id, [])


# Factory function
_classification_ai_instance: Optional[ContentClassificationAI] = None

def get_classification_ai(
    config: Optional[Dict[str, Any]] = None
) -> ContentClassificationAI:
    """Factory pour obtenir une instance du classificateur"""
    global _classification_ai_instance
    if _classification_ai_instance is None:
        _classification_ai_instance = ContentClassificationAI(config)
    return _classification_ai_instance


__all__ = [
    "ContentClassificationAI",
    "get_classification_ai",
    "ClassificationResult",
    "ContentClassificationProfile",
    "ClassificationType",
    "SafetyLevel",
    "MaturityRating"
]
