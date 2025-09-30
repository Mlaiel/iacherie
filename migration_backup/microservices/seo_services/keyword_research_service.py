"""
🔍 Keyword Research Service
Advanced SEO keyword research and analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SearchIntent(Enum):
    """Search intent types"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"


class KeywordResearchService:
    """Advanced SEO keyword research and analysis service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keyword_database: Dict[str, Dict[str, Any]] = {}
        self.search_history: List[Dict[str, Any]] = []
        self.trending_keywords: List[Dict[str, Any]] = []
        
        self._initialize_sample_data()
        self.logger.info("✅ KeywordResearchService initialized")
    
    def _initialize_sample_data(self):
        """Initialize sample keyword data"""
        sample_keywords = [
            {
                "keyword": "intelligence artificielle",
                "search_volume": 12000,
                "difficulty": KeywordDifficulty.MEDIUM,
                "cpc": 2.45,
                "competition": 0.7,
                "intent": SearchIntent.INFORMATIONAL,
                "trends": [8900, 9200, 10500, 11800, 12000]
            },
            {
                "keyword": "création de contenu",
                "search_volume": 8500,
                "difficulty": KeywordDifficulty.EASY,
                "cpc": 1.80,
                "competition": 0.5,
                "intent": SearchIntent.COMMERCIAL,
                "trends": [7200, 7800, 8100, 8300, 8500]
            },
            {
                "keyword": "marketing d'influence",
                "search_volume": 15000,
                "difficulty": KeywordDifficulty.HARD,
                "cpc": 3.20,
                "competition": 0.8,
                "intent": SearchIntent.COMMERCIAL,
                "trends": [13000, 13800, 14200, 14600, 15000]
            },
            {
                "keyword": "réseaux sociaux",
                "search_volume": 25000,
                "difficulty": KeywordDifficulty.VERY_HARD,
                "cpc": 2.10,
                "competition": 0.9,
                "intent": SearchIntent.INFORMATIONAL,
                "trends": [22000, 23500, 24200, 24800, 25000]
            }
        ]
        
        for kw in sample_keywords:
            self.keyword_database[kw["keyword"]] = kw
        
        # Initialize trending keywords
        self.trending_keywords = [
            {"keyword": "ChatGPT", "growth": 450, "volume": 35000},
            {"keyword": "TikTok marketing", "growth": 320, "volume": 18000},
            {"keyword": "NFT création", "growth": 280, "volume": 12000},
            {"keyword": "YouTube Shorts", "growth": 250, "volume": 22000}
        ]
    
    async def search_keywords(
        self, 
        query: str, 
        language: str = "fr",
        country: str = "FR",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search for keywords related to query"""
        try:
            search_id = str(uuid.uuid4())
            
            # Simulate keyword research
            keywords = []
            base_keywords = list(self.keyword_database.keys())
            
            # Find related keywords
            query_lower = query.lower()
            for keyword, data in self.keyword_database.items():
                if (query_lower in keyword.lower() or 
                    any(word in keyword.lower() for word in query_lower.split())):
                    keywords.append({
                        "keyword": keyword,
                        "search_volume": data["search_volume"],
                        "difficulty": data["difficulty"].value,
                        "cpc": data["cpc"],
                        "competition": data["competition"],
                        "intent": data["intent"].value,
                        "relevance_score": self._calculate_relevance(query, keyword)
                    })
            
            # Generate additional suggestions
            suggestions = self._generate_keyword_suggestions(query)
            keywords.extend(suggestions)
            
            # Sort by relevance and volume
            keywords.sort(key=lambda x: (x["relevance_score"], x["search_volume"]), reverse=True)
            keywords = keywords[:limit]
            
            # Log search
            search_record = {
                "search_id": search_id,
                "query": query,
                "language": language,
                "country": country,
                "results_count": len(keywords),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.search_history.append(search_record)
            
            return {
                "success": True,
                "search_id": search_id,
                "query": query,
                "keywords": keywords,
                "total_results": len(keywords),
                "language": language,
                "country": country,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Keyword search failed: {str(e)}")
            return {
                "success": False,
                "error": "Recherche de mots-clés échouée",
                "message": str(e)
            }
    
    def _calculate_relevance(self, query: str, keyword: str) -> float:
        """Calculate relevance score between query and keyword"""
        query_words = set(query.lower().split())
        keyword_words = set(keyword.lower().split())
        
        # Jaccard similarity
        intersection = len(query_words.intersection(keyword_words))
        union = len(query_words.union(keyword_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _generate_keyword_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Generate additional keyword suggestions"""
        import random
        
        # Common modifiers for French keywords
        prefixes = ["", "meilleur", "comment", "guide", "tutoriel", "formation"]
        suffixes = ["", "gratuit", "2025", "france", "débutant", "professionnel"]
        
        suggestions = []
        base_volume = random.randint(500, 5000)
        
        for i in range(10):  # Generate 10 suggestions
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            
            # Build suggested keyword
            parts = []
            if prefix:
                parts.append(prefix)
            parts.append(query)
            if suffix:
                parts.append(suffix)
            
            suggested_keyword = " ".join(parts)
            
            suggestions.append({
                "keyword": suggested_keyword,
                "search_volume": random.randint(100, base_volume),
                "difficulty": random.choice(list(KeywordDifficulty)).value,
                "cpc": round(random.uniform(0.50, 4.00), 2),
                "competition": round(random.uniform(0.1, 0.9), 2),
                "intent": random.choice(list(SearchIntent)).value,
                "relevance_score": round(random.uniform(0.5, 1.0), 2)
            })
        
        return suggestions
    
    async def analyze_keyword_difficulty(self, keyword: str) -> Dict[str, Any]:
        """Analyze keyword difficulty and competition"""
        try:
            if keyword in self.keyword_database:
                data = self.keyword_database[keyword]
                difficulty_score = data["competition"]
            else:
                # Simulate difficulty analysis
                difficulty_score = await self._calculate_difficulty_score(keyword)
            
            # Determine difficulty level
            if difficulty_score < 0.2:
                difficulty = KeywordDifficulty.VERY_EASY
            elif difficulty_score < 0.4:
                difficulty = KeywordDifficulty.EASY
            elif difficulty_score < 0.6:
                difficulty = KeywordDifficulty.MEDIUM
            elif difficulty_score < 0.8:
                difficulty = KeywordDifficulty.HARD
            else:
                difficulty = KeywordDifficulty.VERY_HARD
            
            return {
                "success": True,
                "keyword": keyword,
                "difficulty": difficulty.value,
                "difficulty_score": difficulty_score,
                "analysis": {
                    "competition_level": "high" if difficulty_score > 0.7 else "medium" if difficulty_score > 0.4 else "low",
                    "ranking_potential": "low" if difficulty_score > 0.8 else "medium" if difficulty_score > 0.5 else "high",
                    "time_to_rank": "12+ mois" if difficulty_score > 0.8 else "6-12 mois" if difficulty_score > 0.5 else "1-6 mois"
                },
                "recommendations": self._get_difficulty_recommendations(difficulty),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Keyword difficulty analysis failed: {str(e)}")
            return {
                "success": False,
                "error": "Analyse de difficulté échouée",
                "message": str(e)
            }
    
    async def _calculate_difficulty_score(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        import random
        # Simulate complexity based on keyword characteristics
        words = len(keyword.split())
        length = len(keyword)
        
        # More words and longer keywords tend to be easier
        base_score = max(0.1, 1.0 - (words * 0.1) - (length * 0.005))
        
        # Add some randomness
        return min(0.9, base_score + random.uniform(-0.2, 0.3))
    
    def _get_difficulty_recommendations(self, difficulty: KeywordDifficulty) -> List[str]:
        """Get recommendations based on keyword difficulty"""
        recommendations = {
            KeywordDifficulty.VERY_EASY: [
                "Excellent mot-clé pour débuter",
                "Créez du contenu de qualité rapidement",
                "Optimisez votre page pour ce mot-clé"
            ],
            KeywordDifficulty.EASY: [
                "Bon potentiel de classement",
                "Créez du contenu approfondi",
                "Ajoutez des mots-clés longue traîne"
            ],
            KeywordDifficulty.MEDIUM: [
                "Nécessite du contenu de haute qualité",
                "Construisez des liens de qualité",
                "Optimisez l'expérience utilisateur"
            ],
            KeywordDifficulty.HARD: [
                "Stratégie SEO long terme requise",
                "Investissez dans la création de liens",
                "Considérez les mots-clés alternatifs"
            ],
            KeywordDifficulty.VERY_HARD: [
                "Mot-clé très compétitif",
                "Focalisez-vous sur la longue traîne",
                "Développez l'autorité de votre domaine"
            ]
        }
        
        return recommendations.get(difficulty, ["Aucune recommandation disponible"])
    
    async def get_trending_keywords(
        self, 
        category: str = None,
        time_period: str = "week",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get trending keywords"""
        try:
            filtered_keywords = self.trending_keywords.copy()
            
            # Filter by category if specified
            if category:
                # In a real implementation, filter by category
                pass
            
            # Sort by growth rate
            filtered_keywords.sort(key=lambda x: x["growth"], reverse=True)
            filtered_keywords = filtered_keywords[:limit]
            
            return {
                "success": True,
                "trending_keywords": filtered_keywords,
                "category": category,
                "time_period": time_period,
                "total_trends": len(filtered_keywords),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Getting trending keywords failed: {str(e)}")
            return {
                "success": False,
                "error": "Récupération des tendances échouée",
                "message": str(e)
            }
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 10) -> Dict[str, Any]:
        """Get search suggestions for partial query"""
        try:
            suggestions = []
            
            # Find keywords that start with or contain the partial query
            for keyword in self.keyword_database.keys():
                if partial_query.lower() in keyword.lower():
                    suggestions.append({
                        "suggestion": keyword,
                        "search_volume": self.keyword_database[keyword]["search_volume"]
                    })
            
            # Sort by search volume
            suggestions.sort(key=lambda x: x["search_volume"], reverse=True)
            suggestions = suggestions[:limit]
            
            return {
                "success": True,
                "query": partial_query,
                "suggestions": suggestions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Getting search suggestions failed: {str(e)}")
            return {
                "success": False,
                "error": "Récupération des suggestions échouée",
                "message": str(e)
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "KeywordResearchService",
            "status": "healthy",
            "keyword_database_size": len(self.keyword_database),
            "search_history": len(self.search_history),
            "trending_keywords": len(self.trending_keywords),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['KeywordResearchService', 'KeywordDifficulty', 'SearchIntent']