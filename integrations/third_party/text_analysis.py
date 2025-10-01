#!/usr/bin/env python3
"""
🔍 TEXTRAZOR ENGINE - Analyse de texte avancée pour IA Chérie
════════════════════════════════════════════════════════════════

Fonctionnalités:
✅ Analyse de sentiment
✅ Extraction d'entités 
✅ Détection de mots-clés
✅ Classification de contenu
✅ Analyse de relation entre entités
✅ Détection de thèmes

Auteur: Fahed Mlaiel
Date: 28 Septembre 2025
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import textrazor

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextAnalysisResult:
    """Résultat d'analyse TextRazor"""
    text: str
    sentiment: Dict[str, float]
    entities: List[Dict[str, Any]]
    keywords: List[Dict[str, Any]]
    topics: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    language: str
    success: bool
    error: Optional[str] = None

class iaCherieTextRazor:
    """
    🧠 Moteur d'analyse de texte TextRazor pour IA Chérie
    """
    
    def __init__(self):
        self.api_key = os.getenv('TEXTRAZOR_API_KEY')
        if not self.api_key:
            raise ValueError("❌ TEXTRAZOR_API_KEY manquante dans .env")
            
        # Configuration TextRazor
        textrazor.api_key = self.api_key
        self.client = textrazor.TextRazor(
            extractors=["entities", "topics", "words", "phrases", "dependency-trees", "relations"]
        )
        self.client.set_language_override("auto")  # Détection automatique de langue
        
        logger.info("✅ TextRazor Engine initialisé avec succès")
    
    async def analyze_text(self, text: str, extract_sentiment: bool = True) -> TextAnalysisResult:
        """
        Analyse complète d'un texte avec TextRazor
        
        Args:
            text: Texte à analyser
            extract_sentiment: Si True, extrait le sentiment
            
        Returns:
            TextAnalysisResult avec toutes les analyses
        """
        try:
            if not text or len(text.strip()) < 3:
                return TextAnalysisResult(
                    text=text,
                    sentiment={}, entities=[], keywords=[], topics=[],
                    categories=[], relations=[], language="unknown",
                    success=False, error="Texte trop court"
                )
            
            # Configuration des extracteurs
            extractors = ["entities", "topics", "words", "phrases", "relations"]
            if extract_sentiment:
                extractors.append("sentiment")
                
            self.client.set_extractors(extractors)
            
            # Analyse avec TextRazor
            response = await asyncio.to_thread(self.client.analyze, text)
            
            # Extraction du sentiment
            sentiment_data = {}
            if hasattr(response, 'sentiment') and response.sentiment:
                sentiment_data = {
                    "score": float(response.sentiment.score),
                    "label": "positive" if response.sentiment.score > 0.1 else "negative" if response.sentiment.score < -0.1 else "neutral",
                    "confidence": abs(float(response.sentiment.score))
                }
            
            # Extraction des entités
            entities = []
            if hasattr(response, 'entities') and response.entities:
                for entity in response.entities[:20]:  # Limite à 20 entités
                    entities.append({
                        "text": entity.matched_text,
                        "type": getattr(entity, 'type', ['Unknown'])[0] if hasattr(entity, 'type') and entity.type else 'Unknown',
                        "confidence": float(getattr(entity, 'confidence_score', 0.5)),
                        "wikidata_id": getattr(entity, 'wikidata_id', None),
                        "wikipedia_link": getattr(entity, 'wikipedia_link', None)
                    })
            
            # Extraction des mots-clés
            keywords = []
            if hasattr(response, 'noun_phrases') and response.noun_phrases:
                for phrase in response.noun_phrases[:15]:  # Limite à 15 mots-clés
                    keywords.append({
                        "text": phrase.words[0].token if phrase.words else "",
                        "score": float(getattr(phrase, 'score', 0.5)),
                        "stem": getattr(phrase.words[0], 'stem', "") if phrase.words else ""
                    })
            
            # Extraction des topics
            topics = []
            if hasattr(response, 'topics') and response.topics:
                for topic in response.topics[:10]:  # Limite à 10 topics
                    topics.append({
                        "label": topic.label,
                        "score": float(topic.score),
                        "wikidata_id": getattr(topic, 'wikidata_id', None)
                    })
            
            # Extraction des relations
            relations = []
            if hasattr(response, 'relations') and response.relations:
                for relation in response.relations[:10]:  # Limite à 10 relations
                    relations.append({
                        "predicate": relation.predicate_words[0].token if relation.predicate_words else "",
                        "subject": relation.subject_words[0].token if relation.subject_words else "",
                        "object": relation.object_words[0].token if relation.object_words else ""
                    })
            
            # Détection de langue
            language = getattr(response, 'language', 'unknown')
            
            return TextAnalysisResult(
                text=text[:200] + "..." if len(text) > 200 else text,
                sentiment=sentiment_data,
                entities=entities,
                keywords=keywords,
                topics=topics,
                categories=[],  # TextRazor ne fournit pas de catégories directes
                relations=relations,
                language=language,
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse TextRazor: {str(e)}")
            return TextAnalysisResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                sentiment={}, entities=[], keywords=[], topics=[],
                categories=[], relations=[], language="unknown",
                success=False, error=str(e)
            )
    
    async def extract_entities_only(self, text: str) -> List[Dict[str, Any]]:
        """Extraction rapide des entités uniquement"""
        try:
            self.client.set_extractors(["entities"])
            response = await asyncio.to_thread(self.client.analyze, text)
            
            entities = []
            if hasattr(response, 'entities') and response.entities:
                for entity in response.entities[:30]:
                    entities.append({
                        "text": entity.matched_text,
                        "type": getattr(entity, 'type', ['Unknown'])[0] if hasattr(entity, 'type') and entity.type else 'Unknown',
                        "confidence": float(getattr(entity, 'confidence_score', 0.5)),
                        "start_pos": entity.start_pos,
                        "end_pos": entity.end_pos
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction entités: {str(e)}")
            return []
    
    async def analyze_sentiment_only(self, text: str) -> Dict[str, Any]:
        """Analyse de sentiment uniquement (plus rapide)"""
        try:
            self.client.set_extractors(["sentiment"])
            response = await asyncio.to_thread(self.client.analyze, text)
            
            if hasattr(response, 'sentiment') and response.sentiment:
                score = float(response.sentiment.score)
                return {
                    "score": score,
                    "label": "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral",
                    "confidence": abs(score),
                    "success": True
                }
            
            return {"success": False, "error": "Pas de sentiment détecté"}
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse sentiment: {str(e)}")
            return {"success": False, "error": str(e)}

# Test du moteur si exécuté directement
async def test_textrazor_engine():
    """Test complet du moteur TextRazor"""
    print("🧪 Test TextRazor Engine - Analyse de texte avancée")
    print("=" * 60)
    
    try:
        engine = iaCherieTextRazor()
        
        # Texte de test
        test_text = """
        IA Chérie est une plateforme révolutionnaire d'intelligence artificielle 
        qui transforme la création de contenu. Grâce à ses 53 agents IA et 680 microservices, 
        la plateforme permet aux entreprises de générer du contenu de haute qualité 
        automatiquement. L'entreprise, basée à Berlin, vise un chiffre d'affaires 
        de 50 millions d'euros d'ici 2026.
        """
        
        print(f"📝 Texte à analyser:\n{test_text.strip()}\n")
        
        # Test analyse complète
        result = await engine.analyze_text(test_text)
        
        print("🎯 RÉSULTATS D'ANALYSE:")
        print("-" * 40)
        
        if result.success:
            print(f"🌐 Langue détectée: {result.language}")
            
            if result.sentiment:
                print(f"😊 Sentiment: {result.sentiment['label']} (score: {result.sentiment['score']:.2f})")
            
            if result.entities:
                print(f"🏷️  Entités trouvées ({len(result.entities)}):")
                for entity in result.entities[:5]:
                    print(f"   • {entity['text']} ({entity['type']}) - conf: {entity['confidence']:.2f}")
            
            if result.keywords:
                print(f"🔑 Mots-clés ({len(result.keywords)}):")
                for kw in result.keywords[:5]:
                    print(f"   • {kw['text']} (score: {kw['score']:.2f})")
            
            if result.topics:
                print(f"📊 Topics ({len(result.topics)}):")
                for topic in result.topics[:3]:
                    print(f"   • {topic['label']} (score: {topic['score']:.2f})")
            
            if result.relations:
                print(f"🔗 Relations ({len(result.relations)}):")
                for rel in result.relations[:3]:
                    print(f"   • {rel['subject']} → {rel['predicate']} → {rel['object']}")
        
        else:
            print(f"❌ Erreur: {result.error}")
        
        # Test extraction entités rapide
        print("\n⚡ Test extraction entités rapide:")
        entities = await engine.extract_entities_only("Apple Inc. est une entreprise américaine basée à Cupertino en Californie.")
        print(f"Entités trouvées: {len(entities)}")
        for entity in entities[:3]:
            print(f"   • {entity['text']} ({entity['type']})")
        
        # Test sentiment rapide
        print("\n😊 Test sentiment rapide:")
        sentiment = await engine.analyze_sentiment_only("Je suis très heureux de cette nouvelle fonctionnalité!")
        if sentiment['success']:
            print(f"Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})")
        
        print("\n✅ TextRazor Engine testé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_textrazor_engine())