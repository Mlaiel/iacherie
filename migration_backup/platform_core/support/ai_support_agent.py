"""🚀 AI Support Agent - Conversational Intelligence Enterprise
===============================================================
Module: backend/platform_core/support/ai_support_agent.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🤖 AGENT IA CONVERSATIONNEL MULTILINGUE ENTERPRISE
Agent IA GPT-4 avec intelligence contextuelle avancée
- Support conversationnel en 4 langues (EN/FR/DE/AR)
- Intégration knowledge base pour réponses précises
- Escalation intelligente vers agents humains spécialisés
- Learning continu depuis conversations résolues
- Détection sentiment et adaptation tone émotionnel
"""

import asyncio
import logging
import json
import uuid
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms import OpenAI
import nltk
from textblob import TextBlob

logger = logging.getLogger(__name__)


class ConversationLanguage(Enum):
    """Langues supportées par l'agent IA"""
    ENGLISH = "en"
    FRENCH = "fr" 
    GERMAN = "de"
    ARABIC = "ar"


class ConversationTone(Enum):
    """Tons de conversation adaptés au sentiment"""
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    REASSURING = "reassuring"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"


class EscalationTrigger(Enum):
    """Déclencheurs d'escalation automatique"""
    COMPLEX_TECHNICAL = "complex_technical"
    BILLING_DISPUTE = "billing_dispute"
    COPYRIGHT_ISSUE = "copyright_issue"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    MULTIPLE_FAILURES = "multiple_failures"
    VIP_CREATOR = "vip_creator"


@dataclass
class ConversationContext:
    """Contexte conversationnel pour personnalisation"""
    creator_id: str
    creator_type: str  # musician, blogger, photographer
    conversation_id: str
    language: ConversationLanguage
    session_start: datetime
    message_count: int = 0
    sentiment_score: float = 0.0
    escalation_triggers: List[EscalationTrigger] = field(default_factory=list)
    previous_issues: List[str] = field(default_factory=list)
    satisfaction_score: Optional[float] = None


@dataclass
class AIResponse:
    """Réponse structurée de l'agent IA"""
    message: str
    confidence_score: float
    suggested_actions: List[str]
    knowledge_sources: List[str]
    escalation_needed: bool
    escalation_reason: Optional[str] = None
    follow_up_required: bool = False
    estimated_resolution_time: Optional[timedelta] = None


class AISupportAgent:
    """🤖 Agent IA Support Conversationnel Enterprise
    
    Agent intelligent multilingue avec capacités:
    - Traitement NLP avancé multi-langues
    - Recherche sémantique knowledge base
    - Détection sentiment et adaptation émotionnelle
    - Escalation intelligente basée ML
    - Learning continu depuis résolutions
    """
    
    def __init__(self, openai_api_key: str, knowledge_base_path: str):
        self.openai_api_key = openai_api_key
        self.knowledge_base_path = knowledge_base_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vectorstore = None
        self.conversation_memory = {}
        self.escalation_thresholds = {
            "sentiment_negative": -0.3,
            "confidence_low": 0.6,
            "technical_complexity": 0.8,
            "conversation_length": 10
        }
        self.language_models = self._initialize_language_models()
        self.creator_profiles = {}
        
    async def initialize_knowledge_base(self) -> None:
        """🚀 Initialisation base connaissances vectorielle
        
        Charge et indexe la knowledge base avec embeddings
        pour recherche sémantique ultra-rapide
        """
        try:
            if self.knowledge_base_path:
                self.vectorstore = FAISS.load_local(
                    self.knowledge_base_path, 
                    self.embeddings
                )
                logger.info("Knowledge base vectorielle chargée avec succès")
            else:
                logger.warning("Chemin knowledge base non spécifié")
        except Exception as e:
            logger.error(f"Erreur chargement knowledge base: {e}")
            
    def _initialize_language_models(self) -> Dict[str, Any]:
        """🌍 Initialisation modèles linguistiques multilingues"""
        return {
            ConversationLanguage.ENGLISH: {
                "greeting": "Hello! I'm your AI support assistant. How can I help you today?",
                "escalation": "I'm connecting you with a human specialist who can better assist you.",
                "resolution": "I'm glad I could help resolve your issue. Is there anything else?",
                "sentiment_phrases": {
                    "empathy": "I understand this can be frustrating. Let me help you with this.",
                    "reassurance": "Don't worry, we'll get this sorted out for you.",
                    "technical": "Let me walk you through the technical solution step by step."
                }
            },
            ConversationLanguage.FRENCH: {
                "greeting": "Bonjour ! Je suis votre assistant IA de support. Comment puis-je vous aider ?",
                "escalation": "Je vous mets en relation avec un spécialiste humain qui pourra mieux vous aider.",
                "resolution": "Je suis ravi d'avoir pu résoudre votre problème. Autre chose ?",
                "sentiment_phrases": {
                    "empathy": "Je comprends que cela puisse être frustrant. Laissez-moi vous aider.",
                    "reassurance": "Ne vous inquiétez pas, nous allons résoudre cela ensemble.",
                    "technical": "Permettez-moi de vous expliquer la solution technique étape par étape."
                }
            },
            ConversationLanguage.GERMAN: {
                "greeting": "Hallo! Ich bin Ihr KI-Support-Assistent. Wie kann ich Ihnen helfen?",
                "escalation": "Ich verbinde Sie mit einem menschlichen Spezialisten, der Ihnen besser helfen kann.",
                "resolution": "Ich freue mich, dass ich Ihr Problem lösen konnte. Gibt es noch etwas?",
                "sentiment_phrases": {
                    "empathy": "Ich verstehe, dass das frustrierend sein kann. Lassen Sie mich Ihnen helfen.",
                    "reassurance": "Keine Sorge, wir werden das für Sie klären.",
                    "technical": "Lassen Sie mich Ihnen die technische Lösung Schritt für Schritt erklären."
                }
            },
            ConversationLanguage.ARABIC: {
                "greeting": "مرحباً! أنا مساعد الذكي للدعم الفني. كيف يمكنني مساعدتك؟",
                "escalation": "سأقوم بتوصيلك مع أخصائي بشري يمكنه مساعدتك بشكل أفضل.",
                "resolution": "سعيد لأنني تمكنت من حل مشكلتك. هل هناك شيء آخر؟",
                "sentiment_phrases": {
                    "empathy": "أفهم أن هذا قد يكون محبطاً. دعني أساعدك في هذا.",
                    "reassurance": "لا تقلق، سنحل هذا الأمر معاً.",
                    "technical": "دعني أشرح لك الحل التقني خطوة بخطوة."
                }
            }
        }

    async def process_user_message(
        self, 
        message: str, 
        context: ConversationContext
    ) -> AIResponse:
        """🎯 Traitement message utilisateur avec IA contextuelle
        
        Args:
            message: Message utilisateur à traiter
            context: Contexte conversationnel et créateur
            
        Returns:
            AIResponse: Réponse structurée avec actions suggérées
        """
        try:
            # 1. Détection langue et sentiment
            detected_language = await self._detect_language(message)
            sentiment_score = await self._analyze_sentiment(message, detected_language)
            
            # 2. Mise à jour contexte
            context.message_count += 1
            context.sentiment_score = sentiment_score
            context.language = detected_language
            
            # 3. Recherche knowledge base sémantique
            knowledge_results = await self._search_knowledge_base(
                message, context.creator_type
            )
            
            # 4. Génération réponse contextuelle
            ai_response = await self._generate_contextual_response(
                message, context, knowledge_results
            )
            
            # 5. Vérification besoin escalation
            escalation_needed = await self._check_escalation_triggers(
                message, context, ai_response.confidence_score
            )
            
            ai_response.escalation_needed = escalation_needed
            
            # 6. Learning continu
            await self._record_interaction_for_learning(
                message, ai_response, context
            )
            
            logger.info(f"Message traité - Confiance: {ai_response.confidence_score:.2f}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            return await self._generate_fallback_response(context)

    async def _detect_language(self, text: str) -> ConversationLanguage:
        """🌍 Détection automatique langue avec ML"""
        try:
            # Utilisation TextBlob pour détection langue
            blob = TextBlob(text)
            detected_lang = blob.detect_language()
            
            # Mapping vers nos langues supportées
            language_mapping = {
                'en': ConversationLanguage.ENGLISH,
                'fr': ConversationLanguage.FRENCH,
                'de': ConversationLanguage.GERMAN,
                'ar': ConversationLanguage.ARABIC
            }
            
            return language_mapping.get(detected_lang, ConversationLanguage.ENGLISH)
            
        except Exception as e:
            logger.warning(f"Erreur détection langue: {e}")
            return ConversationLanguage.ENGLISH

    async def _analyze_sentiment(self, text: str, language: ConversationLanguage) -> float:
        """🧠 Analyse sentiment avec adaptation culturelle"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Adaptation culturelle du sentiment
            if language == ConversationLanguage.GERMAN:
                # Les Allemands sont plus directs, ajustement
                polarity *= 0.8
            elif language == ConversationLanguage.ARABIC:
                # Culture plus expressive, ajustement
                polarity *= 1.2
            elif language == ConversationLanguage.FRENCH:
                # Nuances subtiles françaises
                polarity *= 1.1
                
            return max(-1.0, min(1.0, polarity))
            
        except Exception as e:
            logger.error(f"Erreur analyse sentiment: {e}")
            return 0.0

    async def _search_knowledge_base(
        self, 
        query: str, 
        creator_type: str
    ) -> List[Dict[str, Any]]:
        """🔍 Recherche sémantique knowledge base optimisée créateur"""
        try:
            if not self.vectorstore:
                return []
                
            # Enrichissement requête avec contexte créateur
            enriched_query = f"{creator_type} {query}"
            
            # Recherche vectorielle similitude sémantique
            results = await asyncio.to_thread(
                self.vectorstore.similarity_search_with_score,
                enriched_query,
                k=5
            )
            
            knowledge_results = []
            for doc, score in results:
                if score < 0.8:  # Seuil pertinence
                    knowledge_results.append({
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "unknown"),
                        "relevance_score": 1.0 - score,
                        "creator_specific": creator_type in doc.page_content.lower()
                    })
                    
            return knowledge_results
            
        except Exception as e:
            logger.error(f"Erreur recherche knowledge base: {e}")
            return []

    async def _generate_contextual_response(
        self,
        message: str,
        context: ConversationContext,
        knowledge_results: List[Dict[str, Any]]
    ) -> AIResponse:
        """🎨 Génération réponse contextuelle avec personnalisation"""
        try:
            # Sélection tone basé sentiment
            tone = self._select_conversation_tone(context.sentiment_score)
            
            # Construction prompt contextualisé
            system_prompt = self._build_system_prompt(context, tone)
            knowledge_context = self._format_knowledge_context(knowledge_results)
            
            # Génération avec OpenAI GPT-4
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {knowledge_context}\n\nUser message: {message}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_message = response.choices[0].message.content
            confidence_score = self._calculate_confidence_score(knowledge_results, ai_message)
            
            # Extraction actions suggérées
            suggested_actions = self._extract_suggested_actions(ai_message, context.creator_type)
            
            return AIResponse(
                message=ai_message,
                confidence_score=confidence_score,
                suggested_actions=suggested_actions,
                knowledge_sources=[kr["source"] for kr in knowledge_results],
                escalation_needed=False,
                follow_up_required=self._needs_follow_up(ai_message),
                estimated_resolution_time=self._estimate_resolution_time(context.creator_type, message)
            )
            
        except Exception as e:
            logger.error(f"Erreur génération réponse: {e}")
            return await self._generate_fallback_response(context)

    def _select_conversation_tone(self, sentiment_score: float) -> ConversationTone:
        """🎭 Sélection tone adapté au sentiment émotionnel"""
        if sentiment_score < -0.3:
            return ConversationTone.EMPATHETIC
        elif sentiment_score < 0:
            return ConversationTone.REASSURING
        elif "technical" in context.previous_issues:
            return ConversationTone.TECHNICAL
        else:
            return ConversationTone.FRIENDLY

    def _build_system_prompt(self, context: ConversationContext, tone: ConversationTone) -> str:
        """🎯 Construction prompt système contextualisé"""
        lang_model = self.language_models[context.language]
        
        base_prompt = f"""You are an expert AI support agent for IA Chéries Creator Economy Platform.

Creator Profile:
- Type: {context.creator_type}
- Language: {context.language.value}
- Conversation tone: {tone.value}
- Previous issues: {', '.join(context.previous_issues)}

Guidelines:
1. Respond in {context.language.value} language only
2. Use {tone.value} tone throughout the conversation
3. Focus on {context.creator_type}-specific solutions
4. Provide actionable steps when possible
5. Reference knowledge base sources when available
6. Keep responses concise but helpful (max 300 words)

Specialized knowledge areas for {context.creator_type}:
"""
        
        # Ajout expertise spécifique créateur
        if context.creator_type == "musician":
            base_prompt += "- Audio processing and formats\n- Copyright protection\n- Music collaboration\n- Streaming monetization"
        elif context.creator_type == "blogger":
            base_prompt += "- Content SEO optimization\n- Plagiarism detection\n- Affiliate marketing\n- Audience growth"
        elif context.creator_type == "photographer":
            base_prompt += "- Image protection and watermarking\n- Portfolio optimization\n- Client licensing\n- Print fulfillment"
            
        return base_prompt

    async def _check_escalation_triggers(
        self,
        message: str,
        context: ConversationContext,
        confidence_score: float
    ) -> bool:
        """⚡ Vérification déclencheurs escalation intelligente"""
        
        escalation_triggers = []
        
        # 1. Sentiment très négatif
        if context.sentiment_score < self.escalation_thresholds["sentiment_negative"]:
            escalation_triggers.append(EscalationTrigger.NEGATIVE_SENTIMENT)
            
        # 2. Faible confiance IA
        if confidence_score < self.escalation_thresholds["confidence_low"]:
            escalation_triggers.append(EscalationTrigger.MULTIPLE_FAILURES)
            
        # 3. Conversation trop longue
        if context.message_count > self.escalation_thresholds["conversation_length"]:
            escalation_triggers.append(EscalationTrigger.MULTIPLE_FAILURES)
            
        # 4. Mots-clés complexité technique
        technical_keywords = ["bug", "error", "crash", "broken", "integration", "API"]
        if any(keyword in message.lower() for keyword in technical_keywords):
            escalation_triggers.append(EscalationTrigger.COMPLEX_TECHNICAL)
            
        # 5. Problèmes facturation/copyright
        if any(keyword in message.lower() for keyword in ["billing", "payment", "copyright", "license"]):
            escalation_triggers.append(EscalationTrigger.BILLING_DISPUTE)
            
        context.escalation_triggers.extend(escalation_triggers)
        
        return len(escalation_triggers) >= 2  # Escalation si 2+ triggers

    async def escalate_to_human_agent(
        self,
        context: ConversationContext,
        escalation_reason: str
    ) -> Dict[str, Any]:
        """🚨 Escalation intelligente vers agent humain spécialisé"""
        try:
            # Détermination spécialiste approprié
            specialist_type = self._determine_specialist_type(context.escalation_triggers)
            
            # Préparation contexte pour agent humain
            escalation_data = {
                "conversation_id": context.conversation_id,
                "creator_id": context.creator_id,
                "creator_type": context.creator_type,
                "escalation_reason": escalation_reason,
                "escalation_triggers": [t.value for t in context.escalation_triggers],
                "conversation_history": self.conversation_memory.get(context.conversation_id, []),
                "sentiment_score": context.sentiment_score,
                "specialist_type": specialist_type,
                "priority": self._calculate_priority(context),
                "estimated_complexity": "high" if len(context.escalation_triggers) > 2 else "medium",
                "language": context.language.value,
                "escalation_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Escalation créée - Spécialiste: {specialist_type}")
            return escalation_data
            
        except Exception as e:
            logger.error(f"Erreur escalation: {e}")
            return {}

    async def learn_from_interactions(
        self,
        conversation_id: str,
        satisfaction_score: float,
        resolution_success: bool
    ) -> None:
        """🧠 Learning continu depuis interactions résolues"""
        try:
            # Récupération données conversation
            conversation_data = self.conversation_memory.get(conversation_id, [])
            
            if not conversation_data:
                return
                
            # Analyse patterns succès/échec
            learning_data = {
                "conversation_id": conversation_id,
                "satisfaction_score": satisfaction_score,
                "resolution_success": resolution_success,
                "interaction_patterns": self._extract_interaction_patterns(conversation_data),
                "escalation_triggers": self._analyze_escalation_patterns(conversation_data),
                "response_effectiveness": self._measure_response_effectiveness(conversation_data),
                "learning_timestamp": datetime.utcnow().isoformat()
            }
            
            # Mise à jour modèles IA
            await self._update_ai_models(learning_data)
            
            logger.info(f"Learning complété - Satisfaction: {satisfaction_score:.2f}")
            
        except Exception as e:
            logger.error(f"Erreur learning: {e}")

    def _determine_specialist_type(self, triggers: List[EscalationTrigger]) -> str:
        """🎯 Détermination type spécialiste optimal"""
        if EscalationTrigger.COMPLEX_TECHNICAL in triggers:
            return "technical_specialist"
        elif EscalationTrigger.BILLING_DISPUTE in triggers:
            return "billing_specialist"
        elif EscalationTrigger.COPYRIGHT_ISSUE in triggers:
            return "legal_specialist"
        elif EscalationTrigger.NEGATIVE_SENTIMENT in triggers:
            return "customer_success_manager"
        else:
            return "general_support"

    def _calculate_confidence_score(self, knowledge_results: List[Dict], response: str) -> float:
        """📊 Calcul score confiance basé sur sources knowledge"""
        if not knowledge_results:
            return 0.3
            
        # Score basé pertinence sources
        relevance_scores = [kr["relevance_score"] for kr in knowledge_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Ajustement selon spécificité créateur
        creator_specific_count = sum(1 for kr in knowledge_results if kr["creator_specific"])
        creator_bonus = creator_specific_count * 0.1
        
        # Score longueur réponse (ni trop courte ni trop longue)
        response_length_score = min(1.0, len(response.split()) / 100)
        
        confidence = (avg_relevance * 0.6) + (creator_bonus * 0.2) + (response_length_score * 0.2)
        return max(0.0, min(1.0, confidence))

    async def _record_interaction_for_learning(
        self,
        message: str,
        response: AIResponse,
        context: ConversationContext
    ) -> None:
        """📝 Enregistrement interaction pour learning ML"""
        if context.conversation_id not in self.conversation_memory:
            self.conversation_memory[context.conversation_id] = []
            
        interaction_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": message,
            "ai_response": response.message,
            "confidence_score": response.confidence_score,
            "sentiment_score": context.sentiment_score,
            "escalation_needed": response.escalation_needed,
            "knowledge_sources": response.knowledge_sources,
            "creator_type": context.creator_type,
            "language": context.language.value
        }
        
        self.conversation_memory[context.conversation_id].append(interaction_record)

    async def _generate_fallback_response(self, context: ConversationContext) -> AIResponse:
        """🆘 Réponse fallback en cas d'erreur"""
        lang_model = self.language_models[context.language]
        
        return AIResponse(
            message=lang_model["escalation"],
            confidence_score=0.2,
            suggested_actions=["Contact human support"],
            knowledge_sources=[],
            escalation_needed=True,
            escalation_reason="Technical error in AI processing"
        )

    def _extract_suggested_actions(self, ai_message: str, creator_type: str) -> List[str]:
        """🎯 Extraction actions suggérées contextuelles"""
        actions = []
        
        # Actions générales
        if "documentation" in ai_message.lower():
            actions.append("Check documentation")
        if "tutorial" in ai_message.lower():
            actions.append("Follow tutorial guide")
        if "settings" in ai_message.lower():
            actions.append("Review account settings")
            
        # Actions spécifiques créateur
        if creator_type == "musician" and "upload" in ai_message.lower():
            actions.append("Upload audio file")
        elif creator_type == "blogger" and "seo" in ai_message.lower():
            actions.append("Optimize SEO settings")
        elif creator_type == "photographer" and "watermark" in ai_message.lower():
            actions.append("Apply watermark protection")
            
        return actions[:3]  # Max 3 actions

    def _needs_follow_up(self, ai_message: str) -> bool:
        """🔄 Détection besoin follow-up"""
        follow_up_indicators = [
            "let me know", "keep me updated", "follow up", 
            "check back", "monitor", "verify"
        ]
        return any(indicator in ai_message.lower() for indicator in follow_up_indicators)

    def _estimate_resolution_time(self, creator_type: str, message: str) -> Optional[timedelta]:
        """⏱️ Estimation temps résolution"""
        # Temps base par type créateur
        base_times = {
            "musician": timedelta(hours=2),
            "blogger": timedelta(hours=1),
            "photographer": timedelta(minutes=30)
        }
        
        base_time = base_times.get(creator_type, timedelta(hours=1))
        
        # Ajustement selon complexité
        if any(keyword in message.lower() for keyword in ["integration", "api", "technical"]):
            base_time *= 2
        elif any(keyword in message.lower() for keyword in ["simple", "quick", "basic"]):
            base_time *= 0.5
            
        return base_time


# Factory function pour initialisation simplifiée
async def create_ai_support_agent(
    openai_api_key: str,
    knowledge_base_path: str = None
) -> AISupportAgent:
    """🏭 Factory création agent IA support configuré"""
    agent = AISupportAgent(openai_api_key, knowledge_base_path)
    if knowledge_base_path:
        await agent.initialize_knowledge_base()
    return agent


# Métriques et analytics pour monitoring
class AISupportMetrics:
    """📊 Métriques performance agent IA"""
    
    def __init__(self):
        self.total_conversations = 0
        self.successful_resolutions = 0
        self.escalations = 0
        self.avg_confidence_score = 0.0
        self.avg_response_time = timedelta()
        self.language_distribution = {}
        self.creator_type_distribution = {}
        
    def record_conversation(self, context: ConversationContext, response: AIResponse):
        """📈 Enregistrement métriques conversation"""
        self.total_conversations += 1
        
        # Distribution langues
        lang = context.language.value
        self.language_distribution[lang] = self.language_distribution.get(lang, 0) + 1
        
        # Distribution types créateur
        creator_type = context.creator_type
        self.creator_type_distribution[creator_type] = self.creator_type_distribution.get(creator_type, 0) + 1
        
        # Mise à jour moyennes
        self.avg_confidence_score = (
            (self.avg_confidence_score * (self.total_conversations - 1) + response.confidence_score) /
            self.total_conversations
        )
        
        if response.escalation_needed:
            self.escalations += 1
            
    def get_performance_report(self) -> Dict[str, Any]:
        """📋 Rapport performance complet"""
        return {
            "total_conversations": self.total_conversations,
            "resolution_rate": (self.successful_resolutions / max(1, self.total_conversations)) * 100,
            "escalation_rate": (self.escalations / max(1, self.total_conversations)) * 100,
            "avg_confidence_score": round(self.avg_confidence_score, 2),
            "language_distribution": self.language_distribution,
            "creator_type_distribution": self.creator_type_distribution,
            "ai_effectiveness": "high" if self.avg_confidence_score > 0.8 else "medium" if self.avg_confidence_score > 0.6 else "low"
        }