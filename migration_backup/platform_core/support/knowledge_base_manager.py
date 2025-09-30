"""🚀 Knowledge Base Manager - Semantic Search Enterprise
========================================================
Module: backend/platform_core/support/knowledge_base_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🗄️ KNOWLEDGE BASE MANAGER SÉMANTIQUE ENTERPRISE
Système de gestion connaissances avec recherche vectorielle
- Recherche sémantique ultra-rapide avec embeddings
- Auto-génération articles depuis tickets résolus
- Maintenance automatique contenu obsolète
- Analytics utilisation pour optimisation contenu
- Support multilingue avec traduction automatique
"""

import asyncio
import logging
import json
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import faiss
from core.sentence_transformers_singleton import get_sentence_transformer
import openai
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types de contenu knowledge base"""
    FAQ = "faq"
    TUTORIAL = "tutorial"
    TROUBLESHOOTING = "troubleshooting"
    API_DOCUMENTATION = "api_documentation"
    FEATURE_GUIDE = "feature_guide"
    CREATOR_SPECIFIC = "creator_specific"
    POLICY_LEGAL = "policy_legal"
    INTEGRATION_GUIDE = "integration_guide"


class ContentStatus(Enum):
    """Statuts contenu knowledge base"""
    ACTIVE = "active"
    DRAFT = "draft"
    REVIEW_NEEDED = "review_needed"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class CreatorType(Enum):
    """Types créateurs pour contenu spécialisé"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    GENERAL = "general"


@dataclass
class KnowledgeArticle:
    """Article knowledge base avec métadonnées"""
    article_id: str
    title: str
    content: str
    content_type: ContentType
    creator_types: List[CreatorType]
    languages: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    status: ContentStatus = ContentStatus.ACTIVE
    author: str = ""
    view_count: int = 0
    helpfulness_score: float = 0.0
    search_keywords: List[str] = field(default_factory=list)
    related_tickets: List[str] = field(default_factory=list)
    embedding_vector: Optional[np.ndarray] = None
    last_accessed: Optional[datetime] = None


@dataclass
class SearchQuery:
    """Requête recherche avec contexte"""
    query: str
    creator_type: Optional[CreatorType] = None
    language: str = "en"
    content_types: List[ContentType] = field(default_factory=list)
    max_results: int = 10
    similarity_threshold: float = 0.7
    include_deprecated: bool = False


@dataclass
class SearchResult:
    """Résultat recherche avec scoring"""
    article: KnowledgeArticle
    relevance_score: float
    matched_keywords: List[str]
    content_snippet: str
    reason_for_match: str


class KnowledgeBaseManager:
    """🧠 Knowledge Base Manager Enterprise
    
    Gestionnaire intelligent de base de connaissances:
    - Indexation vectorielle pour recherche sémantique
    - Auto-génération contenu depuis résolutions tickets
    - Maintenance prédictive contenu obsolète
    - Analytics utilisation et optimisation
    - Support multilingue avec embeddings cross-language
    """
    
    def __init__(self, openai_api_key: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.openai_api_key = openai_api_key
        self.embedding_model = get_sentence_transformer(embedding_model)
        self.articles: Dict[str, KnowledgeArticle] = {}
        self.vector_index = None
        self.article_vectors = []
        self.article_ids = []
        self.search_analytics = SearchAnalytics()
        self.content_optimizer = ContentOptimizer()
        
        # Configuration multilingue
        self.supported_languages = ["en", "fr", "de", "ar"]
        self.language_models = {
            "en": "all-MiniLM-L6-v2",
            "fr": "distiluse-base-multilingual-cased",
            "de": "distiluse-base-multilingual-cased", 
            "ar": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        }
        
    async def initialize_knowledge_base(self, initial_articles: List[KnowledgeArticle] = None) -> None:
        """🚀 Initialisation knowledge base avec indexation vectorielle"""
        try:
            if initial_articles:
                for article in initial_articles:
                    await self.add_article(article)
                    
            # Construction index FAISS
            await self._build_vector_index()
            
            logger.info(f"Knowledge base initialisée avec {len(self.articles)} articles")
            
        except Exception as e:
            logger.error(f"Erreur initialisation knowledge base: {e}")

    async def add_article(self, article: KnowledgeArticle) -> bool:
        """📝 Ajout article avec génération embedding"""
        try:
            # Validation article
            if not article.article_id or not article.content:
                raise ValueError("ID et contenu article requis")
                
            # Génération embedding pour recherche sémantique
            article.embedding_vector = await self._generate_embedding(
                article.title + " " + article.content[:500]
            )
            
            # Extraction keywords automatique
            article.search_keywords = await self._extract_keywords(article.content)
            
            # Ajout à la collection
            self.articles[article.article_id] = article
            
            # Mise à jour index vectoriel
            await self._update_vector_index(article)
            
            logger.info(f"Article ajouté: {article.title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout article: {e}")
            return False

    async def search_semantic_content(self, query: SearchQuery) -> List[SearchResult]:
        """🔍 Recherche sémantique ultra-rapide avec scoring avancé
        
        Args:
            query: Requête recherche avec contexte
            
        Returns:
            List[SearchResult]: Résultats ordonnés par pertinence
        """
        try:
            # Génération embedding requête
            query_embedding = await self._generate_embedding(query.query)
            
            # Recherche vectorielle FAISS
            vector_results = await self._search_vector_index(
                query_embedding, query.max_results * 2
            )
            
            # Filtrage et scoring contextuels
            filtered_results = []
            
            for article_id, similarity_score in vector_results:
                article = self.articles.get(article_id)
                if not article:
                    continue
                    
                # Filtres contextuels
                if not await self._passes_context_filters(article, query):
                    continue
                    
                # Calcul score final multi-critères
                final_score = await self._calculate_final_relevance_score(
                    article, query, similarity_score
                )
                
                if final_score >= query.similarity_threshold:
                    # Génération snippet et explication
                    snippet = self._generate_content_snippet(article.content, query.query)
                    match_reason = self._explain_match_reason(article, query, similarity_score)
                    matched_keywords = self._find_matched_keywords(article, query.query)
                    
                    result = SearchResult(
                        article=article,
                        relevance_score=final_score,
                        matched_keywords=matched_keywords,
                        content_snippet=snippet,
                        reason_for_match=match_reason
                    )
                    
                    filtered_results.append(result)
                    
            # Tri par pertinence décroissante
            filtered_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Mise à jour analytics
            await self.search_analytics.record_search(query, filtered_results[:query.max_results])
            
            # Mise à jour compteurs accès articles
            for result in filtered_results[:query.max_results]:
                await self._update_article_access_stats(result.article.article_id)
                
            logger.info(f"Recherche '{query.query[:30]}...' - {len(filtered_results)} résultats")
            return filtered_results[:query.max_results]
            
        except Exception as e:
            logger.error(f"Erreur recherche sémantique: {e}")
            return []

    async def generate_articles_from_tickets(
        self, 
        resolved_tickets: List[Dict[str, Any]]
    ) -> List[KnowledgeArticle]:
        """🤖 Auto-génération articles depuis tickets résolus avec IA
        
        Args:
            resolved_tickets: Liste tickets résolus avec conversations
            
        Returns:
            List[KnowledgeArticle]: Articles générés automatiquement
        """
        try:
            generated_articles = []
            
            for ticket in resolved_tickets:
                # Filtrage tickets candidats
                if not await self._is_good_candidate_for_article(ticket):
                    continue
                    
                # Extraction information ticket
                problem_summary = await self._extract_problem_summary(ticket)
                solution_steps = await self._extract_solution_steps(ticket)
                creator_type = CreatorType(ticket.get("creator_type", "general"))
                
                # Génération contenu article avec GPT-4
                article_content = await self._generate_article_content(
                    problem_summary, solution_steps, creator_type
                )
                
                if not article_content:
                    continue
                    
                # Création article
                article = KnowledgeArticle(
                    article_id=f"auto_{uuid.uuid4().hex[:8]}",
                    title=article_content["title"],
                    content=article_content["content"],
                    content_type=ContentType.TROUBLESHOOTING,
                    creator_types=[creator_type],
                    languages=["en"],  # Base en anglais, traduction après
                    tags=article_content["tags"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    status=ContentStatus.REVIEW_NEEDED,  # Nécessite review humaine
                    author="AI_Generator",
                    related_tickets=[ticket["ticket_id"]]
                )
                
                # Ajout à la base
                if await self.add_article(article):
                    generated_articles.append(article)
                    
                    # Génération versions multilingues
                    await self._generate_multilingual_versions(article)
                    
            logger.info(f"{len(generated_articles)} articles générés depuis tickets")
            return generated_articles
            
        except Exception as e:
            logger.error(f"Erreur génération articles: {e}")
            return []

    async def maintain_content_freshness(self) -> Dict[str, Any]:
        """🔄 Maintenance automatique contenu avec détection obsolescence
        
        Returns:
            Dict[str, Any]: Rapport maintenance avec actions prises
        """
        try:
            maintenance_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "articles_reviewed": 0,
                "articles_updated": 0,
                "articles_deprecated": 0,
                "articles_archived": 0,
                "duplicate_removal": 0,
                "freshness_analysis": {}
            }
            
            current_time = datetime.utcnow()
            
            for article in self.articles.values():
                maintenance_report["articles_reviewed"] += 1
                
                # 1. Détection contenu obsolète
                age_days = (current_time - article.updated_at).days
                
                if age_days > 365:  # Plus d'un an
                    if article.view_count < 10:  # Peu consulté
                        article.status = ContentStatus.ARCHIVED
                        maintenance_report["articles_archived"] += 1
                    else:
                        article.status = ContentStatus.REVIEW_NEEDED
                        
                elif age_days > 180:  # Plus de 6 mois
                    if article.helpfulness_score < 3.0:  # Peu utile
                        article.status = ContentStatus.REVIEW_NEEDED
                        
                # 2. Vérification liens morts (simulation)
                if await self._check_broken_links(article.content):
                    article.status = ContentStatus.REVIEW_NEEDED
                    
                # 3. Mise à jour scores pertinence
                relevance_score = await self._calculate_content_relevance_score(article)
                
                if relevance_score < 0.3:
                    article.status = ContentStatus.DEPRECATED
                    maintenance_report["articles_deprecated"] += 1
                elif relevance_score > 0.8 and article.status == ContentStatus.REVIEW_NEEDED:
                    article.status = ContentStatus.ACTIVE
                    maintenance_report["articles_updated"] += 1
                    
            # 4. Détection et suppression doublons
            duplicate_pairs = await self._detect_duplicate_articles()
            for article_id1, article_id2 in duplicate_pairs:
                # Conserver le plus récent et mieux noté
                article1 = self.articles[article_id1]
                article2 = self.articles[article_id2]
                
                if (article1.updated_at > article2.updated_at and 
                    article1.helpfulness_score >= article2.helpfulness_score):
                    await self._merge_articles(article1, article2)
                    del self.articles[article_id2]
                else:
                    await self._merge_articles(article2, article1)
                    del self.articles[article_id1]
                    
                maintenance_report["duplicate_removal"] += 1
                
            # 5. Analyse fraîcheur globale
            maintenance_report["freshness_analysis"] = await self._analyze_content_freshness()
            
            # 6. Reconstruction index si nécessaire
            if maintenance_report["articles_archived"] > 10:
                await self._build_vector_index()
                
            logger.info(f"Maintenance terminée - {maintenance_report['articles_reviewed']} articles traités")
            return maintenance_report
            
        except Exception as e:
            logger.error(f"Erreur maintenance contenu: {e}")
            return {}

    async def analyze_search_patterns(self) -> Dict[str, Any]:
        """📊 Analyse patterns recherche pour optimisation contenu
        
        Returns:
            Dict[str, Any]: Analytics détaillées recherches et recommandations
        """
        try:
            analytics_data = await self.search_analytics.get_comprehensive_analytics()
            
            # Identification gaps contenu
            content_gaps = await self._identify_content_gaps(analytics_data)
            
            # Recommandations optimisation
            optimization_recommendations = await self._generate_optimization_recommendations(
                analytics_data, content_gaps
            )
            
            # Analyse tendances temporelles
            search_trends = await self._analyze_search_trends()
            
            # Performance articles
            article_performance = await self._analyze_article_performance()
            
            comprehensive_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "search_analytics": analytics_data,
                "content_gaps": content_gaps,
                "optimization_recommendations": optimization_recommendations,
                "search_trends": search_trends,
                "article_performance": article_performance,
                "knowledge_base_health": await self._assess_knowledge_base_health()
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns: {e}")
            return {}

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """🔢 Génération embedding pour texte"""
        try:
            # Nettoyage texte
            cleaned_text = text.strip()[:512]  # Limitation longueur
            
            # Génération embedding
            embedding = await asyncio.to_thread(
                self.embedding_model.encode,
                [cleaned_text]
            )
            
            return embedding[0]
            
        except Exception as e:
            logger.error(f"Erreur génération embedding: {e}")
            return np.zeros(384)  # Embedding par défaut

    async def _build_vector_index(self) -> None:
        """🏗️ Construction index vectoriel FAISS"""
        try:
            if not self.articles:
                return
                
            # Collection embeddings et IDs
            vectors = []
            article_ids = []
            
            for article_id, article in self.articles.items():
                if article.embedding_vector is not None and article.status == ContentStatus.ACTIVE:
                    vectors.append(article.embedding_vector)
                    article_ids.append(article_id)
                    
            if not vectors:
                return
                
            # Construction index FAISS
            vectors_array = np.array(vectors).astype('float32')
            dimension = vectors_array.shape[1]
            
            # Index avec recherche par similarité cosinus
            self.vector_index = faiss.IndexFlatIP(dimension)
            
            # Normalisation pour similarité cosinus
            faiss.normalize_L2(vectors_array)
            self.vector_index.add(vectors_array)
            
            self.article_vectors = vectors_array
            self.article_ids = article_ids
            
            logger.info(f"Index vectoriel construit - {len(vectors)} articles indexés")
            
        except Exception as e:
            logger.error(f"Erreur construction index: {e}")

    async def _search_vector_index(
        self, 
        query_embedding: np.ndarray, 
        k: int = 10
    ) -> List[Tuple[str, float]]:
        """🔍 Recherche dans index vectoriel"""
        try:
            if not self.vector_index or not self.article_ids:
                return []
                
            # Normalisation query pour similarité cosinus
            query_vector = query_embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(query_vector)
            
            # Recherche k plus proches voisins
            similarities, indices = self.vector_index.search(query_vector, min(k, len(self.article_ids)))
            
            results = []
            for i, similarity in enumerate(similarities[0]):
                if indices[0][i] < len(self.article_ids):
                    article_id = self.article_ids[indices[0][i]]
                    results.append((article_id, float(similarity)))
                    
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche vectorielle: {e}")
            return []

    async def _passes_context_filters(self, article: KnowledgeArticle, query: SearchQuery) -> bool:
        """🎯 Vérification filtres contextuels"""
        # Filtre type créateur
        if query.creator_type and query.creator_type not in article.creator_types:
            if CreatorType.GENERAL not in article.creator_types:
                return False
                
        # Filtre langue
        if query.language not in article.languages:
            return False
            
        # Filtre types contenu
        if query.content_types and article.content_type not in query.content_types:
            return False
            
        # Filtre statut (exclure dépréciés par défaut)
        if not query.include_deprecated and article.status in [ContentStatus.DEPRECATED, ContentStatus.ARCHIVED]:
            return False
            
        return True

    async def _calculate_final_relevance_score(
        self,
        article: KnowledgeArticle,
        query: SearchQuery,
        semantic_similarity: float
    ) -> float:
        """📊 Calcul score pertinence final multi-critères"""
        
        score = semantic_similarity * 0.4  # 40% similarité sémantique
        
        # Boost spécificité créateur (20%)
        if query.creator_type and query.creator_type in article.creator_types:
            score += 0.2
        elif CreatorType.GENERAL in article.creator_types:
            score += 0.1
            
        # Boost popularité/utilité (15%)
        popularity_score = min(1.0, article.view_count / 100) * 0.1
        helpfulness_score = (article.helpfulness_score / 5.0) * 0.05
        score += popularity_score + helpfulness_score
        
        # Boost fraîcheur contenu (15%)
        age_days = (datetime.utcnow() - article.updated_at).days
        freshness_score = max(0, (365 - age_days) / 365) * 0.15
        score += freshness_score
        
        # Boost correspondance mots-clés (10%)
        keyword_matches = len(self._find_matched_keywords(article, query.query))
        keyword_score = min(1.0, keyword_matches / 5) * 0.1
        score += keyword_score
        
        return min(1.0, score)

    def _generate_content_snippet(self, content: str, query: str) -> str:
        """✂️ Génération snippet pertinent"""
        sentences = content.split('. ')
        query_words = set(query.lower().split())
        
        # Recherche phrase la plus pertinente
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words.intersection(sentence_words))
            
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence
                
        # Snippet avec contexte
        if best_sentence:
            snippet = best_sentence[:200] + "..." if len(best_sentence) > 200 else best_sentence
        else:
            snippet = content[:200] + "..." if len(content) > 200 else content
            
        return snippet

    def _explain_match_reason(
        self, 
        article: KnowledgeArticle, 
        query: SearchQuery, 
        similarity: float
    ) -> str:
        """💡 Explication raison correspondance"""
        reasons = []
        
        if similarity > 0.8:
            reasons.append("High semantic similarity")
        elif similarity > 0.6:
            reasons.append("Good semantic match")
        else:
            reasons.append("Partial semantic match")
            
        if query.creator_type and query.creator_type in article.creator_types:
            reasons.append(f"Specialized for {query.creator_type.value}")
            
        keyword_matches = self._find_matched_keywords(article, query.query)
        if keyword_matches:
            reasons.append(f"Keywords: {', '.join(keyword_matches[:3])}")
            
        if article.helpfulness_score > 4.0:
            reasons.append("Highly rated content")
            
        return " | ".join(reasons)

    def _find_matched_keywords(self, article: KnowledgeArticle, query: str) -> List[str]:
        """🔍 Recherche mots-clés correspondants"""
        query_words = set(word.lower() for word in query.split())
        article_keywords = set(keyword.lower() for keyword in article.search_keywords)
        
        matches = query_words.intersection(article_keywords)
        return list(matches)

    async def _extract_keywords(self, content: str) -> List[str]:
        """🏷️ Extraction automatique mots-clés"""
        try:
            # Extraction mots-clés simple (à améliorer avec NLP avancé)
            words = content.lower().split()
            
            # Filtrage mots vides
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Comptage fréquence
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Top mots-clés par fréquence
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            return [word for word, freq in sorted_keywords[:20]]
            
        except Exception as e:
            logger.error(f"Erreur extraction keywords: {e}")
            return []

    async def _update_article_access_stats(self, article_id: str) -> None:
        """📈 Mise à jour statistiques accès article"""
        if article_id in self.articles:
            self.articles[article_id].view_count += 1
            self.articles[article_id].last_accessed = datetime.utcnow()

    async def _is_good_candidate_for_article(self, ticket: Dict[str, Any]) -> bool:
        """✅ Vérification candidat article depuis ticket"""
        # Critères qualité pour génération article
        return (
            ticket.get("resolution_quality_score", 0) > 4.0 and
            ticket.get("customer_satisfaction", 0) > 4.0 and
            len(ticket.get("solution_steps", [])) > 2 and
            ticket.get("issue_complexity") in ["medium", "high"]
        )

    async def _generate_article_content(
        self,
        problem_summary: str,
        solution_steps: List[str],
        creator_type: CreatorType
    ) -> Dict[str, Any]:
        """🤖 Génération contenu article avec GPT-4"""
        try:
            prompt = f"""Create a comprehensive knowledge base article for {creator_type.value} creators.

Problem: {problem_summary}

Solution steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(solution_steps))}

Generate a professional article with:
1. Clear, concise title
2. Well-structured content with sections
3. Step-by-step instructions
4. Relevant tags for searchability
5. Creator-specific context and terminology

Format as JSON with fields: title, content, tags"""

            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback si JSON invalide
                return {
                    "title": problem_summary[:100],
                    "content": content,
                    "tags": ["auto-generated", creator_type.value]
                }
                
        except Exception as e:
            logger.error(f"Erreur génération contenu IA: {e}")
            return None


class SearchAnalytics:
    """📊 Analytics recherche knowledge base"""
    
    def __init__(self):
        self.search_history = []
        self.failed_searches = []
        self.popular_queries = {}
        
    async def record_search(self, query: SearchQuery, results: List[SearchResult]) -> None:
        """📝 Enregistrement recherche pour analytics"""
        search_record = {
            "timestamp": datetime.utcnow(),
            "query": query.query,
            "creator_type": query.creator_type.value if query.creator_type else None,
            "language": query.language,
            "results_count": len(results),
            "avg_relevance": np.mean([r.relevance_score for r in results]) if results else 0.0,
            "search_successful": len(results) > 0
        }
        
        self.search_history.append(search_record)
        
        # Suivi popularité requêtes
        query_key = query.query.lower()
        self.popular_queries[query_key] = self.popular_queries.get(query_key, 0) + 1
        
        # Détection échec recherche
        if len(results) == 0:
            self.failed_searches.append({
                "query": query.query,
                "timestamp": datetime.utcnow(),
                "creator_type": query.creator_type.value if query.creator_type else None
            })

    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """📋 Analytics complètes recherche"""
        if not self.search_history:
            return {"status": "no_data"}
            
        total_searches = len(self.search_history)
        successful_searches = len([s for s in self.search_history if s["search_successful"]])
        
        return {
            "total_searches": total_searches,
            "success_rate": (successful_searches / total_searches) * 100,
            "avg_results_per_search": np.mean([s["results_count"] for s in self.search_history]),
            "avg_relevance_score": np.mean([s["avg_relevance"] for s in self.search_history if s["avg_relevance"] > 0]),
            "popular_queries": dict(sorted(self.popular_queries.items(), key=lambda x: x[1], reverse=True)[:10]),
            "failed_searches_count": len(self.failed_searches),
            "language_distribution": self._calculate_language_distribution(),
            "creator_type_distribution": self._calculate_creator_distribution(),
            "search_trends": self._calculate_search_trends()
        }

    def _calculate_language_distribution(self) -> Dict[str, int]:
        """🌍 Distribution langues recherches"""
        lang_dist = {}
        for search in self.search_history:
            lang = search["language"]
            lang_dist[lang] = lang_dist.get(lang, 0) + 1
        return lang_dist

    def _calculate_creator_distribution(self) -> Dict[str, int]:
        """👥 Distribution types créateurs"""
        creator_dist = {}
        for search in self.search_history:
            creator_type = search["creator_type"] or "general"
            creator_dist[creator_type] = creator_dist.get(creator_type, 0) + 1
        return creator_dist

    def _calculate_search_trends(self) -> Dict[str, Any]:
        """📈 Tendances recherche temporelles"""
        if len(self.search_history) < 10:
            return {"status": "insufficient_data"}
            
        recent = self.search_history[-50:]
        older = self.search_history[-100:-50] if len(self.search_history) >= 100 else []
        
        trends = {
            "recent_success_rate": (len([s for s in recent if s["search_successful"]]) / len(recent)) * 100,
            "trend": "stable"
        }
        
        if older:
            older_success_rate = (len([s for s in older if s["search_successful"]]) / len(older)) * 100
            if trends["recent_success_rate"] > older_success_rate + 5:
                trends["trend"] = "improving"
            elif trends["recent_success_rate"] < older_success_rate - 5:
                trends["trend"] = "declining"
                
        return trends


class ContentOptimizer:
    """🎯 Optimiseur contenu knowledge base"""
    
    def __init__(self):
        self.optimization_history = []
        
    async def suggest_content_improvements(
        self, 
        article: KnowledgeArticle,
        search_patterns: Dict[str, Any]
    ) -> List[str]:
        """💡 Suggestions amélioration contenu"""
        suggestions = []
        
        # Analyse performance article
        if article.view_count < 10 and (datetime.utcnow() - article.created_at).days > 30:
            suggestions.append("Low visibility - consider improving title and tags")
            
        if article.helpfulness_score < 3.0:
            suggestions.append("Low helpfulness score - review content quality and clarity")
            
        # Analyse gaps mots-clés
        popular_queries = search_patterns.get("popular_queries", {})
        article_keywords = set(article.search_keywords)
        
        missing_keywords = []
        for query, frequency in popular_queries.items():
            query_words = set(query.split())
            if not query_words.intersection(article_keywords) and frequency > 5:
                missing_keywords.extend(query_words)
                
        if missing_keywords:
            unique_missing = list(set(missing_keywords))[:5]
            suggestions.append(f"Consider adding keywords: {', '.join(unique_missing)}")
            
        return suggestions