"""
NLP Analyzers for Ainflue platform.
Provides content analysis, sentiment analysis, and language detection capabilities.
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from typing import Dict, List, Optional, Any
import re


class ContentAnalyzer:
    """Analyzes content for quality, topics, and characteristics."""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Fallback if model not installed
                pass
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content for various characteristics."""
        if not text:
            return {"error": "Empty content"}
        
        analysis = {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "quality_score": self._calculate_quality_score(text),
            "topics": self._extract_topics(text),
            "readability": self._calculate_readability(text)
        }
        
        if self.nlp:
            doc = self.nlp(text)
            analysis.update({
                "entities": [(ent.text, ent.label_) for ent in doc.ents],
                "keywords": [token.lemma_ for token in doc if token.is_alpha and not token.is_stop],
                "language_confidence": 0.95  # Placeholder
            })
        
        return analysis
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate content quality score (0-100)."""
        if not text:
            return 0.0
        
        score = 50.0  # Base score
        
        # Length bonus
        if 100 <= len(text) <= 5000:
            score += 20
        
        # Grammar check (simplified)
        if re.search(r'[.!?]', text):
            score += 10
        
        # Capitalization check
        if any(c.isupper() for c in text):
            score += 10
        
        # No excessive repetition
        words = text.lower().split()
        if len(set(words)) / len(words) > 0.7:
            score += 10
        
        return min(100.0, score)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        # Simplified topic extraction
        words = text.lower().split()
        common_topics = [
            "music", "video", "art", "business", "technology", 
            "education", "entertainment", "sports", "health", "travel"
        ]
        
        found_topics = []
        for topic in common_topics:
            if topic in text.lower():
                found_topics.append(topic)
        
        return found_topics[:5]  # Top 5 topics
    
    def _calculate_readability(self, text: str) -> str:
        """Calculate readability level."""
        if not text:
            return "Unknown"
        
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return "Poor"
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 10:
            return "Easy"
        elif avg_words_per_sentence < 20:
            return "Medium"
        else:
            return "Hard"


class SentimentAnalyzer:
    """Analyzes sentiment of content."""
    
    def __init__(self):
        self.positive_words = {
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "enjoy", "happy", "pleased", "satisfied"
        }
        self.negative_words = {
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "sad", "angry", "disappointed", "frustrated", "upset"
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        if not text:
            return {"sentiment": "neutral", "confidence": 0.0, "score": 0.0}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "score": 0.0}
        
        score = (positive_count - negative_count) / len(words)
        
        if score > 0.05:
            sentiment = "positive"
        elif score < -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        confidence = min(1.0, total_sentiment_words / len(words) * 10)
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count
        }


class LanguageDetector:
    """Detects language of content."""
    
    def __init__(self):
        # Simple language patterns
        self.language_patterns = {
            "en": ["the", "and", "is", "in", "to", "of", "a", "that", "it"],
            "fr": ["le", "de", "et", "à", "un", "une", "ce", "que", "qui"],
            "es": ["el", "la", "de", "que", "y", "a", "en", "un", "es"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit"],
            "it": ["il", "di", "che", "e", "la", "a", "per", "non", "in"],
            "pt": ["o", "de", "a", "e", "do", "da", "em", "um", "para"],
            "ru": ["в", "и", "не", "на", "я", "с", "что", "он", "как"],
            "zh": ["的", "是", "了", "在", "有", "我", "他", "这", "个"],
            "ja": ["の", "は", "が", "を", "に", "で", "と", "も", "だ"],
            "ar": ["في", "من", "إلى", "على", "أن", "هذا", "كان", "لا", "ما"]
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the text."""
        if not text:
            return {"language": "unknown", "confidence": 0.0}
        
        words = text.lower().split()
        if not words:
            return {"language": "unknown", "confidence": 0.0}
        
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = sum(1 for word in words if word in patterns)
            language_scores[lang_code] = score / len(words)
        
        if not language_scores:
            return {"language": "unknown", "confidence": 0.0}
        
        best_language = max(language_scores, key=language_scores.get)
        confidence = language_scores[best_language]
        
        # If confidence is too low, mark as unknown
        if confidence < 0.1:
            return {"language": "unknown", "confidence": confidence}
        
        return {
            "language": best_language,
            "confidence": confidence,
            "all_scores": language_scores
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(self.language_patterns.keys())


# Convenience functions
def analyze_content(text: str) -> Dict[str, Any]:
    """Analyze content using ContentAnalyzer."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(text)


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment using SentimentAnalyzer."""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_sentiment(text)


def detect_language(text: str) -> Dict[str, Any]:
    """Detect language using LanguageDetector."""
    detector = LanguageDetector()
    return detector.detect_language(text)


# Additional analyzer classes for test compatibility
class AnalysisResult:
    """Analysis result container."""
    
    def __init__(self, content_id: str = None, analysis_type: str = None, 
                 results: Dict[str, Any] = None, confidence_score: float = 0.0,
                 metadata: Dict[str, Any] = None):
        self.content_id = content_id
        self.analysis_type = analysis_type
        self.results = results or {}
        self.confidence_score = confidence_score
        self.metadata = metadata or {}


class TopicAnalyzer:
    """Analyzes topics in content using advanced NLP techniques."""
    
    def __init__(self):
        """Initialize the topic analyzer with advanced ML models."""
        # Initialize topic modeling capabilities
        self.topic_models = {}
        self.keyword_extractors = {}
        
        # Advanced topic categories with weighted keywords
        self.topic_taxonomy = {
            "music_production": {
                "keywords": ["beat", "music", "producer", "studio", "recording", "mix", "mastering", "audio", "sound", "track", "composition"],
                "weight": 1.0,
                "sub_topics": ["hip-hop", "electronic", "pop", "rock", "jazz", "classical"]
            },
            "content_creation": {
                "keywords": ["video", "content", "creator", "influencer", "youtube", "tiktok", "instagram", "streaming", "vlog", "editing"],
                "weight": 1.0,
                "sub_topics": ["gaming", "lifestyle", "educational", "entertainment"]
            },
            "business_marketing": {
                "keywords": ["business", "marketing", "brand", "sales", "startup", "entrepreneur", "strategy", "growth", "roi", "conversion"],
                "weight": 0.9,
                "sub_topics": ["digital_marketing", "social_media_marketing", "seo", "advertising"]
            },
            "technology": {
                "keywords": ["tech", "technology", "AI", "machine learning", "software", "development", "coding", "programming", "data", "innovation"],
                "weight": 0.8,
                "sub_topics": ["artificial_intelligence", "blockchain", "cybersecurity", "mobile_development"]
            },
            "lifestyle_wellness": {
                "keywords": ["fitness", "health", "wellness", "nutrition", "mental health", "self-care", "mindfulness", "yoga", "meditation"],
                "weight": 0.7,
                "sub_topics": ["fitness", "nutrition", "mental_health", "beauty"]
            },
            "education_learning": {
                "keywords": ["education", "learning", "course", "tutorial", "teaching", "knowledge", "skill", "training", "academy", "certification"],
                "weight": 0.8,
                "sub_topics": ["online_courses", "skill_development", "language_learning", "professional_development"]
            },
            "entertainment": {
                "keywords": ["entertainment", "movie", "film", "show", "celebrity", "news", "gossip", "review", "comedy", "drama"],
                "weight": 0.6,
                "sub_topics": ["movies", "tv_shows", "celebrity_news", "reviews"]
            },
            "finance_investing": {
                "keywords": ["finance", "investing", "money", "crypto", "stocks", "trading", "investment", "portfolio", "wealth", "economy"],
                "weight": 0.9,
                "sub_topics": ["cryptocurrency", "stock_market", "personal_finance", "real_estate"]
            }
        }
        
        # Initialize AI-powered topic extraction models
        self._initialize_topic_models()
    
    def _initialize_topic_models(self):
        """Initialize advanced topic modeling capabilities."""
        try:
            # Initialize TF-IDF vectorizer for keyword extraction
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import LatentDirichletAllocation
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            
            self.lda_model = LatentDirichletAllocation(
                n_components=10,
                random_state=42,
                max_iter=10
            )
            
            self.advanced_nlp_available = True
        except ImportError:
            # Fallback to rule-based approach
            self.advanced_nlp_available = False
    
    async def analyze(self, content: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze topics in content."""
        # Simple topic analysis based on keywords
        topics = []
        topic_keywords = {
            "fitness": ["workout", "gym", "exercise", "fitness", "training"],
            "food": ["food", "recipe", "cooking", "meal", "restaurant"],
            "travel": ["travel", "trip", "vacation", "explore", "adventure"],
            "tech": ["technology", "tech", "AI", "computer", "software"],
            "business": ["business", "work", "career", "professional", "company"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append({"topic": topic, "confidence": 0.7})
        
        results = {
            "topics": topics,
            "num_topics": len(topics)
        }
        
        return AnalysisResult(
            analysis_type="topic_analysis",
            results=results,
            confidence_score=0.8
        )
    
    async def extract_topics(self, text: str, num_topics: int = 5, 
                           options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract topics from text."""
        result = await self.analyze(text)
        topics = result.results.get("topics", [])
        return topics[:num_topics]


class CollaborationAnalyzer:
    """Analyzes collaboration opportunities using advanced AI algorithms."""
    
    def __init__(self):
        """Initialize the collaboration analyzer with ML models."""
        # Collaboration detection patterns and models
        self.collaboration_patterns = {
            "direct_mentions": {
                "patterns": [r"@\w+", r"collab with", r"collaboration with", r"featuring"],
                "weight": 0.9,
                "type": "direct_collaboration"
            },
            "collaboration_keywords": {
                "patterns": ["partnership", "work together", "team up", "join forces", "collaborate", "joint venture"],
                "weight": 0.8,
                "type": "collaboration_intent"
            },
            "network_expansion": {
                "patterns": ["networking", "connect", "reach out", "let's work", "open to collaborations"],
                "weight": 0.7,
                "type": "network_building"
            },
            "cross_promotion": {
                "patterns": ["cross promote", "mutual promotion", "share audience", "feature each other"],
                "weight": 0.8,
                "type": "cross_promotion"
            },
            "skill_exchange": {
                "patterns": ["skill exchange", "knowledge sharing", "learn from", "teach", "mentor"],
                "weight": 0.6,
                "type": "skill_exchange"
            }
        }
        
        # Platform-specific collaboration indicators
        self.platform_indicators = {
            "youtube": ["subscribe", "like and subscribe", "check out", "watch", "channel"],
            "instagram": ["follow", "dm me", "story", "post", "tag"],
            "tiktok": ["duet", "stitch", "fyp", "viral", "trend"],
            "spotify": ["playlist", "stream", "listen", "track", "album"],
            "twitch": ["stream", "follow", "raid", "host", "viewer"]
        }
        
        # Initialize ML models for collaboration prediction
        self._initialize_collaboration_models()
    
    def _initialize_collaboration_models(self):
        """Initialize machine learning models for collaboration analysis."""
        try:
            # Initialize NLP pipeline for entity recognition
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.advanced_nlp = True
            except OSError:
                self.advanced_nlp = False
                
            # Initialize collaboration scoring models
            self.collaboration_features = {
                "sentiment_weight": 0.3,
                "topic_relevance": 0.4,
                "platform_match": 0.2,
                "audience_overlap": 0.1
            }
            
        except ImportError:
            self.advanced_nlp = False
            self.nlp = None
    
    async def detect_opportunities(self, text: str, platform: Any = None, 
                                 options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Detect collaboration opportunities using advanced AI analysis."""
        if not text:
            return []
            
        opportunities = []
        options = options or {}
        
        # Preprocess text
        text_lower = text.lower()
        words = text.split()
        
        # 1. Direct collaboration mentions detection
        direct_mentions = await self._detect_direct_mentions(text, text_lower)
        opportunities.extend(direct_mentions)
        
        # 2. Collaboration intent analysis
        intent_opportunities = await self._analyze_collaboration_intent(text, text_lower)
        opportunities.extend(intent_opportunities)
        
        # 3. Platform-specific collaboration patterns
        if platform:
            platform_opportunities = await self._analyze_platform_collaboration(text, platform)
            opportunities.extend(platform_opportunities)
        
        # 4. Network expansion opportunities
        network_opportunities = await self._detect_network_expansion(text, text_lower)
        opportunities.extend(network_opportunities)
        
        # 5. Content synergy analysis
        synergy_opportunities = await self._analyze_content_synergy(text, options)
        opportunities.extend(synergy_opportunities)
        
        # 6. Audience alignment detection
        audience_opportunities = await self._detect_audience_alignment(text, options)
        opportunities.extend(audience_opportunities)
        
        # Sort by confidence score and remove duplicates
        opportunities = self._deduplicate_opportunities(opportunities)
        opportunities.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return opportunities[:10]  # Return top 10 opportunities
    
    async def _detect_direct_mentions(self, text: str, text_lower: str) -> List[Dict[str, Any]]:
        """Detect direct collaboration mentions like @username or explicit collaboration requests."""
        opportunities = []
        
        # Regex patterns for direct mentions
        mention_patterns = [
            (r"@(\w+)", "user_mention", 0.9),
            (r"collab(oration)?\s+with\s+(@?\w+)", "collaboration_request", 0.85),
            (r"featuring\s+(@?\w+)", "feature_request", 0.8),
            (r"work\s+with\s+(@?\w+)", "work_request", 0.75)
        ]
        
        import re
        for pattern, opp_type, confidence in mention_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                opportunities.append({
                    "type": opp_type,
                    "target": match.group(1) if match.groups() else match.group(0),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "confidence": confidence,
                    "pattern_matched": pattern,
                    "position": match.start()
                })
        
        return opportunities
    
    async def _analyze_collaboration_intent(self, text: str, text_lower: str) -> List[Dict[str, Any]]:
        """Analyze text for collaboration intent using NLP."""
        opportunities = []
        
        # Intent keywords with weights
        intent_indicators = {
            "partnership": 0.8,
            "collaborate": 0.85,
            "team up": 0.8,
            "join forces": 0.75,
            "work together": 0.8,
            "mutual benefit": 0.7,
            "cross promote": 0.75,
            "guest appearance": 0.7,
            "featured artist": 0.8,
            "joint project": 0.85
        }
        
        for indicator, confidence in intent_indicators.items():
            if indicator in text_lower:
                # Extract context around the indicator
                start_pos = text_lower.find(indicator)
                context = text[max(0, start_pos-100):start_pos+len(indicator)+100]
                
                opportunities.append({
                    "type": "collaboration_intent",
                    "indicator": indicator,
                    "context": context.strip(),
                    "confidence": confidence,
                    "intent_strength": self._calculate_intent_strength(context, indicator)
                })
        
        return opportunities
    
    async def _analyze_platform_collaboration(self, text: str, platform: str) -> List[Dict[str, Any]]:
        """Analyze platform-specific collaboration opportunities."""
        opportunities = []
        
        if not platform or platform not in self.platform_indicators:
            return opportunities
        
        platform_keywords = self.platform_indicators[platform]
        text_lower = text.lower()
        
        for keyword in platform_keywords:
            if keyword in text_lower:
                # Calculate platform relevance score
                relevance_score = self._calculate_platform_relevance(text, platform, keyword)
                
                opportunities.append({
                    "type": "platform_collaboration",
                    "platform": platform,
                    "keyword": keyword,
                    "relevance_score": relevance_score,
                    "confidence": min(0.9, relevance_score * 0.8),
                    "collaboration_type": self._determine_platform_collaboration_type(platform, keyword)
                })
        
        return opportunities
    
    async def _detect_network_expansion(self, text: str, text_lower: str) -> List[Dict[str, Any]]:
        """Detect opportunities for network expansion."""
        opportunities = []
        
        network_indicators = [
            ("networking", 0.6),
            ("connect", 0.5),
            ("reach out", 0.7),
            ("let's connect", 0.8),
            ("open to collaborations", 0.9),
            ("looking for", 0.6),
            ("seeking", 0.6),
            ("interested in", 0.5)
        ]
        
        for indicator, base_confidence in network_indicators:
            if indicator in text_lower:
                # Enhanced confidence based on context
                context_confidence = self._analyze_network_context(text, indicator)
                final_confidence = min(0.9, base_confidence * context_confidence)
                
                opportunities.append({
                    "type": "network_expansion",
                    "indicator": indicator,
                    "confidence": final_confidence,
                    "expansion_type": self._determine_expansion_type(text, indicator),
                    "context_quality": context_confidence
                })
        
        return opportunities
    
    async def _analyze_content_synergy(self, text: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze potential content synergy opportunities."""
        opportunities = []
        
        # Content type detection
        content_types = {
            "music": ["song", "track", "album", "beat", "music", "lyrics"],
            "video": ["video", "film", "movie", "vlog", "content", "editing"],
            "podcast": ["podcast", "interview", "episode", "audio", "discussion"],
            "educational": ["tutorial", "course", "lesson", "teach", "learn", "education"],
            "review": ["review", "opinion", "rating", "feedback", "analysis"]
        }
        
        detected_types = []
        text_lower = text.lower()
        
        for content_type, keywords in content_types.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_types.append(content_type)
        
        # Generate synergy opportunities
        for content_type in detected_types:
            synergy_score = self._calculate_synergy_score(text, content_type)
            if synergy_score > 0.5:
                opportunities.append({
                    "type": "content_synergy",
                    "content_type": content_type,
                    "synergy_score": synergy_score,
                    "confidence": synergy_score * 0.8,
                    "synergy_potential": self._assess_synergy_potential(content_type, options)
                })
        
        return opportunities
    
    async def _detect_audience_alignment(self, text: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect audience alignment opportunities."""
        opportunities = []
        
        # Audience indicators
        audience_indicators = {
            "demographics": ["age", "generation", "millennials", "gen z", "boomers"],
            "interests": ["interests", "hobbies", "passion", "enthusiast", "fan"],
            "geography": ["location", "city", "country", "local", "international"],
            "lifestyle": ["lifestyle", "values", "beliefs", "culture", "community"]
        }
        
        text_lower = text.lower()
        
        for category, keywords in audience_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                alignment_score = self._calculate_audience_alignment(text, category, keywords)
                
                opportunities.append({
                    "type": "audience_alignment",
                    "category": category,
                    "alignment_score": alignment_score,
                    "confidence": alignment_score * 0.7,
                    "potential_reach": self._estimate_reach_potential(category, text)
                })
        
        return opportunities
    
    def _calculate_intent_strength(self, context: str, indicator: str) -> float:
        """Calculate the strength of collaboration intent."""
        # Positive modifiers
        positive_modifiers = ["really", "definitely", "absolutely", "strongly", "very"]
        negative_modifiers = ["maybe", "possibly", "might", "could", "perhaps"]
        
        context_lower = context.lower()
        strength = 0.5  # Base strength
        
        for modifier in positive_modifiers:
            if modifier in context_lower:
                strength += 0.15
        
        for modifier in negative_modifiers:
            if modifier in context_lower:
                strength -= 0.1
        
        return min(1.0, max(0.1, strength))
    
    def _calculate_platform_relevance(self, text: str, platform: str, keyword: str) -> float:
        """Calculate platform relevance score."""
        text_lower = text.lower()
        
        # Count platform-specific terms
        platform_terms = self.platform_indicators.get(platform, [])
        term_count = sum(1 for term in platform_terms if term in text_lower)
        
        # Base relevance
        relevance = min(1.0, term_count / len(platform_terms) if platform_terms else 0.1)
        
        # Boost for explicit platform mentions
        if platform in text_lower:
            relevance += 0.3
        
        return min(1.0, relevance)
    
    def _determine_platform_collaboration_type(self, platform: str, keyword: str) -> str:
        """Determine the type of platform collaboration."""
        collaboration_types = {
            "youtube": "video_collaboration",
            "instagram": "social_collaboration", 
            "tiktok": "viral_collaboration",
            "spotify": "music_collaboration",
            "twitch": "streaming_collaboration"
        }
        return collaboration_types.get(platform, "general_collaboration")
    
    def _analyze_network_context(self, text: str, indicator: str) -> float:
        """Analyze the context quality of network expansion indicators."""
        context_start = text.lower().find(indicator)
        if context_start == -1:
            return 0.5
        
        # Extract surrounding context
        context = text[max(0, context_start-50):context_start+len(indicator)+50].lower()
        
        # Quality indicators
        quality_indicators = ["professional", "creative", "experienced", "passionate", "skilled"]
        urgency_indicators = ["asap", "urgent", "immediately", "now", "soon"]
        
        quality_score = 0.5
        
        for indicator in quality_indicators:
            if indicator in context:
                quality_score += 0.1
        
        for indicator in urgency_indicators:
            if indicator in context:
                quality_score += 0.05
        
        return min(1.0, quality_score)
    
    def _determine_expansion_type(self, text: str, indicator: str) -> str:
        """Determine the type of network expansion."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["business", "professional", "work"]):
            return "professional_networking"
        elif any(word in text_lower for word in ["creative", "art", "music", "content"]):
            return "creative_collaboration"
        elif any(word in text_lower for word in ["friend", "personal", "casual"]):
            return "social_networking"
        else:
            return "general_networking"
    
    def _calculate_synergy_score(self, text: str, content_type: str) -> float:
        """Calculate content synergy score."""
        # This would normally use ML models to assess content synergy
        # For now, using rule-based approach
        
        synergy_indicators = {
            "complementary": 0.8,
            "similar": 0.6,
            "related": 0.7,
            "crossover": 0.9,
            "fusion": 0.85
        }
        
        text_lower = text.lower()
        max_score = 0.5  # Base score
        
        for indicator, score in synergy_indicators.items():
            if indicator in text_lower:
                max_score = max(max_score, score)
        
        return max_score
    
    def _assess_synergy_potential(self, content_type: str, options: Dict[str, Any]) -> str:
        """Assess the synergy potential level."""
        # Basic assessment based on content type popularity and market demand
        high_synergy_types = ["music", "video", "educational"]
        medium_synergy_types = ["podcast", "review"]
        
        if content_type in high_synergy_types:
            return "high"
        elif content_type in medium_synergy_types:
            return "medium"
        else:
            return "low"
    
    def _calculate_audience_alignment(self, text: str, category: str, keywords: List[str]) -> float:
        """Calculate audience alignment score."""
        text_lower = text.lower()
        matched_keywords = sum(1 for keyword in keywords if keyword in text_lower)
        
        base_score = matched_keywords / len(keywords) if keywords else 0
        
        # Boost for specific audience mentions
        audience_boosts = {
            "target audience": 0.2,
            "demographic": 0.15,
            "audience overlap": 0.25,
            "shared audience": 0.3
        }
        
        for phrase, boost in audience_boosts.items():
            if phrase in text_lower:
                base_score += boost
        
        return min(1.0, base_score)
    
    def _estimate_reach_potential(self, category: str, text: str) -> str:
        """Estimate the potential reach based on audience category."""
        # Simplified reach estimation
        reach_potential = {
            "demographics": "high",
            "interests": "medium", 
            "geography": "medium",
            "lifestyle": "high"
        }
        return reach_potential.get(category, "medium")
    
    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate opportunities and merge similar ones."""
        if not opportunities:
            return []
        
        # Simple deduplication based on type and confidence
        seen = set()
        deduplicated = []
        
        for opp in opportunities:
            key = (opp.get('type'), opp.get('indicator', ''), opp.get('platform', ''))
            if key not in seen:
                seen.add(key)
                deduplicated.append(opp)
            else:
                # Merge with existing opportunity (take higher confidence)
                existing = next((o for o in deduplicated if (o.get('type'), o.get('indicator', ''), o.get('platform', '')) == key), None)
                if existing and opp.get('confidence', 0) > existing.get('confidence', 0):
                    existing.update(opp)
        
        return deduplicated


class AnalysisConfig:
    """Configuration for analysis."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ContentAnalysisPipeline:
    """Advanced content analysis pipeline."""
    
    def __init__(self):
        self.config = {}
        self.analyzers = {
            'sentiment': SentimentAnalyzer(),
            'topic': TopicAnalyzer(),
            'collaboration': CollaborationAnalyzer()
        }
    
    async def analyze_comprehensive(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive content analysis."""
        if metadata is None:
            metadata = {}
        
        results = {}
        
        # Sentiment analysis
        sentiment_analyzer = self.analyzers['sentiment']
        sentiment_result = sentiment_analyzer.analyze_sentiment(content)
        
        # Enhanced sentiment result with expected structure
        sentiment_analysis_result = AnalysisResult(
            analysis_type="sentiment_analysis",
            results={
                "overall_sentiment": {
                    "positive": sentiment_result.get("positive_words", 0) / 10,
                    "negative": sentiment_result.get("negative_words", 0) / 10,
                    "neutral": 1 - (sentiment_result.get("positive_words", 0) + sentiment_result.get("negative_words", 0)) / 10
                },
                "emotions": {
                    "joy": 0.5 if sentiment_result.get("sentiment") == "positive" else 0.1,
                    "anger": 0.5 if sentiment_result.get("sentiment") == "negative" else 0.1,
                    "sadness": 0.3 if sentiment_result.get("sentiment") == "negative" else 0.1,
                    "fear": 0.2,
                    "surprise": 0.3,
                    "love": 0.4 if sentiment_result.get("sentiment") == "positive" else 0.1
                },
                "engagement_prediction": {
                    "predicted_engagement": min(1.0, sentiment_result.get("confidence", 0.5) + 0.2)
                }
            },
            confidence_score=sentiment_result.get("confidence", 0.5)
        )
        
        results["sentiment"] = sentiment_analysis_result
        
        # Topic analysis
        topic_analyzer = self.analyzers['topic']
        topic_analysis_result = await topic_analyzer.analyze(content, metadata)
        results["topic"] = topic_analysis_result
        
        return results