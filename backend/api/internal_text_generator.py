"""
Internal Text Generator - Free AI Leader Text Generation
Uses advanced templates and linguistic rules for $0.00 cost generation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import uuid

logger = logging.getLogger(__name__)


class InternalTextGenerator:
    """Professional internal text generation with templates and rules"""
    
    def __init__(self):
        self.available = True
        
        # Guardian humanitarian knowledge base
        self.humanitarian_knowledge = {
            "environment": {
                "beach_cleanup": {
                    "steps": [
                        "Divide the beach into sections (e.g., 10 volunteers = 5 teams of 2)",
                        "Provide each team with gloves, bags, and collection tools",
                        "Set a designated meeting point and time",
                        "Focus on visible trash first (plastic, bottles, cans)",
                        "Use proper disposal: separate recyclables from waste",
                        "Document findings with photos for awareness",
                        "Report hazardous materials to authorities"
                    ],
                    "safety": "Wear gloves, avoid sharp objects, stay hydrated",
                    "duration": "2-3 hours recommended"
                },
                "tree_planting": {
                    "steps": [
                        "Select native tree species suited to local climate",
                        "Prepare planting sites with proper spacing",
                        "Dig holes 2-3 times wider than root ball",
                        "Plant at correct depth (root collar at soil level)",
                        "Water thoroughly after planting",
                        "Mulch around base to retain moisture",
                        "Schedule follow-up care (watering, monitoring)"
                    ],
                    "safety": "Use proper tools, watch for underground utilities",
                    "duration": "1-2 days for group planting"
                },
                "recycling_drive": {
                    "steps": [
                        "Set up collection stations for different materials",
                        "Partner with local recycling centers",
                        "Create awareness materials and signage",
                        "Organize volunteer shifts for sorting",
                        "Track quantities collected for reporting",
                        "Share results with community"
                    ],
                    "safety": "Wear gloves, separate hazardous materials",
                    "duration": "1-day event or ongoing program"
                }
            },
            "animal": {
                "shelter_support": {
                    "steps": [
                        "Contact local animal shelter for needs assessment",
                        "Organize donation drives (food, supplies, blankets)",
                        "Schedule volunteer shifts for animal care",
                        "Help with socialization and exercise",
                        "Assist with adoption events",
                        "Promote adoptable animals on social media",
                        "Fundraise for medical care and facility improvements"
                    ],
                    "safety": "Follow shelter protocols, handle animals gently",
                    "duration": "Ongoing volunteer commitment"
                },
                "wildlife_rescue": {
                    "steps": [
                        "Contact certified wildlife rehabilitators",
                        "Do NOT handle wildlife without training",
                        "Provide temporary shelter if instructed",
                        "Document injuries with photos",
                        "Transport safely to rehabilitation center",
                        "Report illegal wildlife trade or abuse"
                    ],
                    "safety": "Never approach dangerous animals, risk of disease",
                    "duration": "Immediate response"
                }
            },
            "homeless": {
                "meal_distribution": {
                    "steps": [
                        "Partner with local food banks or kitchens",
                        "Prepare nutritious, portable meals",
                        "Set up distribution points in safe locations",
                        "Provide water, utensils, and napkins",
                        "Include hygiene kits (soap, wipes, masks)",
                        "Offer information on shelter and services",
                        "Treat everyone with dignity and respect"
                    ],
                    "safety": "Work in teams, respect personal space, be aware of surroundings",
                    "duration": "2-3 hours per distribution"
                },
                "winter_warmth": {
                    "steps": [
                        "Collect warm clothing (coats, blankets, socks)",
                        "Organize donation drives for winter supplies",
                        "Distribute hand warmers and hot beverages",
                        "Provide information on emergency shelters",
                        "Coordinate with outreach teams",
                        "Check on vulnerable individuals regularly"
                    ],
                    "safety": "Dress warmly, work with experienced outreach teams",
                    "duration": "Urgent during cold weather"
                },
                "housing_assistance": {
                    "steps": [
                        "Connect with housing programs and case managers",
                        "Help complete housing applications",
                        "Assist with documentation and ID retrieval",
                        "Provide temporary shelter information",
                        "Support job search and interview prep",
                        "Offer mentorship and life skills training"
                    ],
                    "safety": "Maintain boundaries, work through established programs",
                    "duration": "Long-term engagement"
                }
            },
            "humanitarian": {
                "disaster_relief": {
                    "steps": [
                        "Assess immediate needs (shelter, food, water, medical)",
                        "Coordinate with emergency response teams",
                        "Set up distribution centers for supplies",
                        "Provide first aid and medical triage",
                        "Assist with temporary shelter setup",
                        "Help reunite families",
                        "Document damage for recovery efforts"
                    ],
                    "safety": "Follow emergency protocols, work with authorities",
                    "duration": "Immediate response, ongoing recovery"
                },
                "refugee_support": {
                    "steps": [
                        "Assist with resettlement and integration",
                        "Provide language and cultural orientation",
                        "Help access healthcare and education",
                        "Support job search and skills training",
                        "Offer mental health and trauma support",
                        "Connect with legal aid for asylum cases"
                    ],
                    "safety": "Cultural sensitivity, trauma-informed care",
                    "duration": "Long-term commitment"
                },
                "community_health": {
                    "steps": [
                        "Organize health screenings and vaccinations",
                        "Provide health education and awareness",
                        "Distribute hygiene and medical supplies",
                        "Support maternal and child health programs",
                        "Address malnutrition and food security",
                        "Partner with local health workers"
                    ],
                    "safety": "Follow medical protocols, infection control",
                    "duration": "Ongoing programs"
                }
            }
        }
        
        # Medical knowledge base
        self.medical_knowledge = {
            "grippe": {
                "symptoms": ["fièvre", "toux", "fatigue", "maux de tête", "douleurs musculaires", "congestion nasale"],
                "causes": ["virus influenza", "transmission par gouttelettes", "contact avec surfaces contaminées"],
                "treatment": ["repos", "hydratation", "antipyrétiques", "antiviraux si nécessaire"],
                "prevention": ["vaccination annuelle", "hygiène des mains", "éviter contact avec malades"],
                "duration": "5-7 jours en moyenne",
                "complications": ["pneumonie", "bronchite", "sinusite"],
                "urgency": "routine"
            },
            "covid": {
                "symptoms": ["fièvre", "toux sèche", "fatigue", "perte goût/odorat", "difficultés respiratoires"],
                "causes": ["virus SARS-CoV-2", "transmission aérienne", "contact rapproché"],
                "treatment": ["isolement", "hydratation", "surveillance oxygénation", "antiviraux si sévère"],
                "prevention": ["vaccination", "masque", "distanciation sociale", "ventilation"],
                "duration": "10-14 jours",
                "complications": ["pneumonie sévère", "détresse respiratoire", "syndrome post-covid"],
                "urgency": "urgent"
            },
            "mal de gorge": {
                "symptoms": ["douleur à la déglutition", "gorge rouge", "amygdales enflées", "fièvre possible"],
                "causes": ["infection virale", "infection bactérienne (streptocoque)", "irritation"],
                "treatment": ["pastilles", "gargarismes eau salée", "analgésiques", "antibiotiques si bactérien"],
                "prevention": ["hygiène des mains", "éviter partage objets", "bonne hydratation"],
                "duration": "3-5 jours",
                "complications": ["abcès", "rhumatisme articulaire aigu si streptocoque"],
                "urgency": "routine"
            },
            "douleur thoracique": {
                "symptoms": ["douleur poitrine", "oppression", "essoufflement", "douleur bras gauche"],
                "causes": ["infarctus possible", "angine", "péricardite", "anxiété", "problèmes digestifs"],
                "treatment": ["URGENCE 911 si infarctus suspecté", "consultation médicale immédiate"],
                "prevention": ["contrôle facteurs risque cardiovasculaire", "exercice régulier", "alimentation saine"],
                "duration": "variable selon cause",
                "complications": ["infarctus du myocarde", "arrêt cardiaque"],
                "urgency": "emergency"
            },
            "diabète": {
                "symptoms": ["soif excessive", "mictions fréquentes", "fatigue", "vision floue", "cicatrisation lente"],
                "causes": ["résistance insuline", "production insuffisante insuline", "facteurs génétiques"],
                "treatment": ["insuline", "antidiabétiques oraux", "régime alimentaire", "exercice"],
                "prevention": ["poids santé", "alimentation équilibrée", "activité physique régulière"],
                "duration": "condition chronique",
                "complications": ["neuropathie", "rétinopathie", "néphropathie", "maladies cardiovasculaires"],
                "urgency": "routine"
            },
            "hypertension": {
                "symptoms": ["souvent asymptomatique", "maux de tête", "vertiges", "vision trouble"],
                "causes": ["facteurs génétiques", "surpoids", "stress", "consommation sel excessive"],
                "treatment": ["antihypertenseurs", "changements mode de vie", "réduction sel", "exercice"],
                "prevention": ["alimentation saine", "exercice régulier", "gestion stress", "limitation alcool"],
                "duration": "condition chronique",
                "complications": ["AVC", "infarctus", "insuffisance rénale", "anévrisme"],
                "urgency": "routine"
            }
        }
        
        # Educational knowledge base
        self.educational_topics = {
            "photosynthèse": {
                "definition": "processus par lequel les plantes convertissent la lumière en énergie chimique",
                "key_points": [
                    "Utilise la lumière du soleil comme source d'énergie",
                    "Convertit le CO2 et l'eau en glucose et oxygène",
                    "Se déroule dans les chloroplastes des cellules végétales",
                    "Équation: 6CO2 + 6H2O + lumière → C6H12O6 + 6O2"
                ],
                "importance": "Production d'oxygène essentiel pour la vie sur Terre"
            },
            "révolution française": {
                "definition": "période de bouleversements politiques et sociaux en France (1789-1799)",
                "key_points": [
                    "Prise de la Bastille le 14 juillet 1789",
                    "Déclaration des Droits de l'Homme et du Citoyen",
                    "Abolition de la monarchie absolue",
                    "Naissance de la République française"
                ],
                "importance": "Événement fondateur de la démocratie moderne"
            },
            "théorème pythagore": {
                "definition": "relation entre les côtés d'un triangle rectangle",
                "key_points": [
                    "Formule: a² + b² = c²",
                    "a et b sont les côtés de l'angle droit",
                    "c est l'hypoténuse (côté le plus long)",
                    "Applicable uniquement aux triangles rectangles"
                ],
                "importance": "Base de la géométrie et de la trigonométrie"
            }
        }
        
        logger.info("🤖 Internal Text Generator initialized")
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        # French indicators
        french_words = ["le", "la", "de", "et", "un", "une", "est", "dans", "pour", "que", "qui", "pas"]
        # English indicators
        english_words = ["the", "is", "and", "of", "to", "a", "in", "that", "it", "for"]
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_words if f" {word} " in f" {text_lower} ")
        english_count = sum(1 for word in english_words if f" {word} " in f" {text_lower} ")
        
        return "fr" if french_count > english_count else "en"
    
    def _find_medical_topic(self, prompt: str) -> Optional[str]:
        """Find medical topic in prompt"""
        prompt_lower = prompt.lower()
        
        # Direct matches
        for topic in self.medical_knowledge.keys():
            if topic in prompt_lower:
                return topic
        
        # Symptom-based detection
        symptom_map = {
            "fièvre": "grippe",
            "toux": "grippe",
            "fatigue": "grippe",
            "gorge": "mal de gorge",
            "douleur": "mal de gorge",
            "poitrine": "douleur thoracique",
            "cœur": "douleur thoracique",
            "thorax": "douleur thoracique",
            "sucre": "diabète",
            "soif": "diabète",
            "mictions": "diabète",
            "tension": "hypertension",
            "pression": "hypertension"
        }
        
        for symptom, topic in symptom_map.items():
            if symptom in prompt_lower:
                return topic
        
        return None
    
    def _find_humanitarian_topic(self, prompt: str, category: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
        """Find humanitarian topic in prompt"""
        prompt_lower = prompt.lower()
        
        # Keywords for each category
        keywords = {
            "environment": {
                "beach_cleanup": ["beach", "cleanup", "clean up", "océan", "mer", "plage", "nettoyage"],
                "tree_planting": ["tree", "planting", "arbre", "plantation", "forest", "forêt"],
                "recycling_drive": ["recycling", "recyclage", "waste", "déchet", "tri"]
            },
            "animal": {
                "shelter_support": ["shelter", "refuge", "animal", "animaux", "adoption", "pet"],
                "wildlife_rescue": ["wildlife", "rescue", "sauvage", "sauvetage", "faune"]
            },
            "homeless": {
                "meal_distribution": ["meal", "food", "repas", "nourriture", "distribution"],
                "winter_warmth": ["winter", "warmth", "hiver", "chaleur", "cold", "froid", "blanket"],
                "housing_assistance": ["housing", "logement", "shelter", "abri", "home"]
            },
            "humanitarian": {
                "disaster_relief": ["disaster", "catastrophe", "urgence", "emergency", "secours"],
                "refugee_support": ["refugee", "réfugié", "asylum", "asile", "migration"],
                "community_health": ["health", "santé", "community", "communauté", "clinic"]
            }
        }
        
        # If category is specified, search within that category
        if category and category in keywords:
            for topic, topic_keywords in keywords[category].items():
                for kw in topic_keywords:
                    if kw in prompt_lower:
                        return category, topic
        
        # Otherwise, search all categories
        for cat, topics in keywords.items():
            for topic, topic_keywords in topics.items():
                for kw in topic_keywords:
                    if kw in prompt_lower:
                        return cat, topic
        
        return None, None
    
    def _find_educational_topic(self, prompt: str) -> Optional[str]:
        """Find educational topic in prompt"""
        prompt_lower = prompt.lower()
        
        for topic in self.educational_topics.keys():
            # Check exact match
            if topic in prompt_lower:
                return topic
            
            # Check partial matches
            topic_words = topic.split()
            if all(word in prompt_lower for word in topic_words):
                return topic
        
        return None
    
    def _generate_medical_explanation(self, topic: str, language: str = "fr") -> str:
        """Generate medical explanation"""
        data = self.medical_knowledge.get(topic)
        if not data:
            return self._generate_generic_response(topic, language)
        
        if language == "fr":
            response = f"# Informations médicales : {topic.title()}\n\n"
            response += f"## Symptômes principaux\n"
            response += "Les symptômes typiques incluent : " + ", ".join(data["symptoms"][:4]) + ".\n\n"
            
            response += f"## Causes\n"
            response += "Cette condition est généralement causée par : " + ", ".join(data["causes"][:2]) + ".\n\n"
            
            response += f"## Traitement recommandé\n"
            response += "Le traitement standard comprend : " + ", ".join(data["treatment"][:3]) + ".\n\n"
            
            response += f"## Prévention\n"
            response += "Pour prévenir cette condition : " + ", ".join(data["prevention"][:3]) + ".\n\n"
            
            response += f"## Durée et complications\n"
            response += f"Durée habituelle : {data['duration']}. "
            response += f"Complications possibles : {', '.join(data['complications'][:2])}.\n\n"
            
            if data["urgency"] == "emergency":
                response += "⚠️ **URGENCE MÉDICALE** - Consultez immédiatement un professionnel de santé ou appelez le 911.\n"
            elif data["urgency"] == "urgent":
                response += "⚠️ Consultation médicale recommandée dans les 24 heures.\n"
            else:
                response += "ℹ️ Consultez un médecin si les symptômes persistent ou s'aggravent.\n"
        
        else:  # English
            response = f"# Medical Information: {topic.title()}\n\n"
            response += f"## Main Symptoms\n"
            response += "Typical symptoms include: " + ", ".join(data["symptoms"][:4]) + ".\n\n"
            
            response += f"## Causes\n"
            response += "This condition is usually caused by: " + ", ".join(data["causes"][:2]) + ".\n\n"
            
            response += f"## Recommended Treatment\n"
            response += "Standard treatment includes: " + ", ".join(data["treatment"][:3]) + ".\n\n"
            
            response += f"## Prevention\n"
            response += "To prevent this condition: " + ", ".join(data["prevention"][:3]) + ".\n\n"
            
            response += f"## Duration and Complications\n"
            response += f"Typical duration: {data['duration']}. "
            response += f"Possible complications: {', '.join(data['complications'][:2])}.\n\n"
            
            if data["urgency"] == "emergency":
                response += "⚠️ **MEDICAL EMERGENCY** - Seek immediate medical attention or call 911.\n"
            elif data["urgency"] == "urgent":
                response += "⚠️ Medical consultation recommended within 24 hours.\n"
            else:
                response += "ℹ️ Consult a doctor if symptoms persist or worsen.\n"
        
        return response
    
    def _generate_educational_content(self, topic: str, language: str = "fr") -> str:
        """Generate educational content"""
        data = self.educational_topics.get(topic)
        if not data:
            return self._generate_generic_response(topic, language)
        
        if language == "fr":
            response = f"# Cours : {topic.title()}\n\n"
            response += f"## Définition\n"
            response += f"{data['definition'].capitalize()}.\n\n"
            
            response += f"## Points clés\n"
            for i, point in enumerate(data['key_points'], 1):
                response += f"{i}. {point}\n"
            response += "\n"
            
            response += f"## Importance\n"
            response += f"{data['importance']}\n\n"
            
            response += "---\n"
            response += "*Contenu généré par AI Leader - Plateforme éducative IA2GOOD*\n"
        
        else:  # English
            response = f"# Lesson: {topic.title()}\n\n"
            response += f"## Definition\n"
            response += f"{data['definition'].capitalize()}.\n\n"
            
            response += f"## Key Points\n"
            for i, point in enumerate(data['key_points'], 1):
                response += f"{i}. {point}\n"
            response += "\n"
            
            response += f"## Importance\n"
            response += f"{data['importance']}\n\n"
            
            response += "---\n"
            response += "*Content generated by AI Leader - IA2GOOD Educational Platform*\n"
        
        return response
    
    def _generate_generic_response(self, topic: str, language: str = "fr") -> str:
        """Generate generic intelligent response"""
        
        # Analyze prompt to detect intent
        prompt_lower = topic.lower()
        
        # Question detection
        is_question = any(q in prompt_lower for q in ["?", "comment", "pourquoi", "quoi", "qui", "où", "quand", "how", "why", "what", "who", "where", "when"])
        
        # Explanation request
        is_explanation = any(exp in prompt_lower for exp in ["explique", "explain", "décris", "describe", "qu'est-ce", "what is"])
        
        if language == "fr":
            if is_question or is_explanation:
                response = f"Pour répondre à votre question sur '{topic}' :\n\n"
                response += f"1. **Contexte** : {topic} est un sujet important qui mérite attention.\n\n"
                response += f"2. **Analyse** : Plusieurs aspects sont à considérer pour bien comprendre {topic}.\n\n"
                response += f"3. **Points clés** :\n"
                response += f"   - Aspect fondamental de {topic}\n"
                response += f"   - Implications pratiques\n"
                response += f"   - Applications concrètes\n\n"
                response += f"4. **Conclusion** : {topic} présente des caractéristiques uniques qu'il convient d'étudier attentivement.\n\n"
            else:
                response = f"# Analyse : {topic}\n\n"
                response += f"Voici une analyse structurée concernant {topic} :\n\n"
                response += f"**Présentation** : Cette thématique nécessite une compréhension approfondie.\n\n"
                response += f"**Développement** : Les éléments principaux à retenir sont multiples et interconnectés.\n\n"
                response += f"**Synthèse** : En conclusion, {topic} représente un domaine d'étude pertinent.\n\n"
        
        else:  # English
            if is_question or is_explanation:
                response = f"To answer your question about '{topic}':\n\n"
                response += f"1. **Context**: {topic} is an important subject that deserves attention.\n\n"
                response += f"2. **Analysis**: Several aspects should be considered to properly understand {topic}.\n\n"
                response += f"3. **Key Points**:\n"
                response += f"   - Fundamental aspect of {topic}\n"
                response += f"   - Practical implications\n"
                response += f"   - Concrete applications\n\n"
                response += f"4. **Conclusion**: {topic} presents unique characteristics worth studying carefully.\n\n"
            else:
                response = f"# Analysis: {topic}\n\n"
                response += f"Here is a structured analysis regarding {topic}:\n\n"
                response += f"**Introduction**: This topic requires deep understanding.\n\n"
                response += f"**Development**: The main elements to remember are multiple and interconnected.\n\n"
                response += f"**Summary**: In conclusion, {topic} represents a relevant field of study.\n\n"
        
        return response
    
    def _generate_quiz(self, topic: str, language: str = "fr", num_questions: int = 3) -> List[Dict]:
        """Generate quiz questions"""
        questions = []
        
        # Try medical topic
        medical_topic = self._find_medical_topic(topic)
        if medical_topic:
            data = self.medical_knowledge[medical_topic]
            
            if language == "fr":
                questions.append({
                    "question": f"Quels sont les symptômes principaux de {medical_topic} ?",
                    "options": [
                        ", ".join(data["symptoms"][:2]),
                        "Aucun symptôme visible",
                        "Seulement des douleurs",
                        "Uniquement de la fièvre"
                    ],
                    "correct_answer": 0,
                    "explanation": f"Les symptômes typiques incluent : {', '.join(data['symptoms'][:3])}"
                })
                
                questions.append({
                    "question": f"Quelle est la durée habituelle de {medical_topic} ?",
                    "options": [
                        data["duration"],
                        "Quelques heures",
                        "Plusieurs mois",
                        "Toute la vie"
                    ],
                    "correct_answer": 0,
                    "explanation": f"La durée habituelle est de {data['duration']}"
                })
                
                questions.append({
                    "question": f"Comment prévenir {medical_topic} ?",
                    "options": [
                        ", ".join(data["prevention"][:2]),
                        "Aucune prévention possible",
                        "Uniquement par médicaments",
                        "En évitant toute activité"
                    ],
                    "correct_answer": 0,
                    "explanation": f"La prévention inclut : {', '.join(data['prevention'][:2])}"
                })
            else:
                questions.append({
                    "question": f"What are the main symptoms of {medical_topic}?",
                    "options": [
                        ", ".join(data["symptoms"][:2]),
                        "No visible symptoms",
                        "Only pain",
                        "Only fever"
                    ],
                    "correct_answer": 0,
                    "explanation": f"Typical symptoms include: {', '.join(data['symptoms'][:3])}"
                })
        
        # Try educational topic
        elif topic_key := self._find_educational_topic(topic):
            data = self.educational_topics[topic_key]
            
            if language == "fr":
                questions.append({
                    "question": f"Qu'est-ce que {topic_key} ?",
                    "options": [
                        data["definition"],
                        "Un phénomène sans importance",
                        "Une théorie non prouvée",
                        "Un concept moderne"
                    ],
                    "correct_answer": 0,
                    "explanation": data["definition"].capitalize()
                })
                
                for i, point in enumerate(data["key_points"][:2], 1):
                    questions.append({
                        "question": f"Quel est un aspect important de {topic_key} ?",
                        "options": [
                            point,
                            "Aucun aspect particulier",
                            "Seulement théorique",
                            "Non applicable"
                        ],
                        "correct_answer": 0,
                        "explanation": point
                    })
        
        else:
            # Generic questions
            if language == "fr":
                questions = [
                    {
                        "question": f"Quel est l'aspect principal de {topic} ?",
                        "options": [
                            f"L'étude approfondie de {topic}",
                            "Aucun aspect spécifique",
                            "Uniquement théorique",
                            "Sans importance"
                        ],
                        "correct_answer": 0,
                        "explanation": f"{topic} nécessite une compréhension approfondie"
                    },
                    {
                        "question": f"Pourquoi {topic} est-il important ?",
                        "options": [
                            f"Pour comprendre les implications de {topic}",
                            "Ce n'est pas important",
                            "Seulement pour les experts",
                            "Pour des raisons historiques"
                        ],
                        "correct_answer": 0,
                        "explanation": f"{topic} a des implications pratiques importantes"
                    },
                    {
                        "question": f"Comment appliquer {topic} ?",
                        "options": [
                            f"En étudiant attentivement {topic}",
                            "Impossible à appliquer",
                            "Seulement en laboratoire",
                            "Sans application pratique"
                        ],
                        "correct_answer": 0,
                        "explanation": f"{topic} s'applique dans divers contextes"
                    }
                ]
        
        return questions[:num_questions]
    
    def _generate_summary(self, text: str, style: str = "concise", language: str = "fr") -> str:
        """Generate text summary"""
        # Extract key sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return text
        
        # Calculate importance scores (simple heuristic)
        scored_sentences = []
        for sentence in sentences:
            score = 0
            # Longer sentences might be more informative
            score += len(sentence.split()) * 0.1
            # Sentences with specific keywords
            keywords = ["important", "essentiel", "crucial", "principal", "key", "essential", "critical", "main"]
            score += sum(2 for kw in keywords if kw in sentence.lower())
            scored_sentences.append((score, sentence))
        
        # Sort by score
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        if style == "concise":
            # Take top 2 sentences
            summary_sentences = [s for _, s in scored_sentences[:2]]
        elif style == "detailed":
            # Take top 5 sentences
            summary_sentences = [s for _, s in scored_sentences[:5]]
        else:  # bullet_points
            summary_sentences = [s for _, s in scored_sentences[:4]]
        
        if style == "bullet_points":
            if language == "fr":
                summary = "**Points clés :**\n"
                for sent in summary_sentences:
                    summary += f"• {sent}\n"
            else:
                summary = "**Key Points:**\n"
                for sent in summary_sentences:
                    summary += f"• {sent}\n"
        else:
            summary = " ".join(summary_sentences)
        
        return summary
    
    def _generate_humanitarian_guidance(self, category: str, topic: str, prompt: str, language: str = "en") -> str:
        """Generate guidance for humanitarian mission"""
        data = self.humanitarian_knowledge.get(category, {}).get(topic, {})
        
        if not data:
            return self._generate_generic_humanitarian(category, prompt, language)
        
        if language == "fr":
            response = f"# Guide de Mission: {topic.replace('_', ' ').title()}\n\n"
            response += f"**Catégorie**: {category.title()}\n\n"
            
            response += "## Étapes à Suivre\n"
            for i, step in enumerate(data.get("steps", []), 1):
                response += f"{i}. {step}\n"
            response += "\n"
            
            if "safety" in data:
                response += "## Sécurité\n"
                response += f"⚠️ {data['safety']}\n\n"
            
            if "duration" in data:
                response += "## Durée Estimée\n"
                response += f"⏱️ {data['duration']}\n\n"
            
            response += "## Conseils Additionnels\n"
            response += "- Travaillez toujours en équipe\n"
            response += "- Documentez vos actions pour rapports\n"
            response += "- Respectez la dignité de toutes les personnes\n"
            response += "- Coordonnez avec les autorités locales\n\n"
            
            response += "---\n"
            response += "*Guide généré par Guardian Volunteer - Plateforme humanitaire IA2GOOD*\n"
        
        else:  # English
            response = f"# Mission Guide: {topic.replace('_', ' ').title()}\n\n"
            response += f"**Category**: {category.title()}\n\n"
            
            response += "## Steps to Follow\n"
            for i, step in enumerate(data.get("steps", []), 1):
                response += f"{i}. {step}\n"
            response += "\n"
            
            if "safety" in data:
                response += "## Safety\n"
                response += f"⚠️ {data['safety']}\n\n"
            
            if "duration" in data:
                response += "## Estimated Duration\n"
                response += f"⏱️ {data['duration']}\n\n"
            
            response += "## Additional Tips\n"
            response += "- Always work in teams\n"
            response += "- Document your actions for reporting\n"
            response += "- Respect the dignity of all individuals\n"
            response += "- Coordinate with local authorities\n\n"
            
            response += "---\n"
            response += "*Guide generated by Guardian Volunteer - IA2GOOD Humanitarian Platform*\n"
        
        return response
    
    def _generate_generic_humanitarian(self, category: str, prompt: str, language: str = "en") -> str:
        """Generate generic humanitarian guidance"""
        if language == "fr":
            response = f"# Assistance Humanitaire: {category.title()}\n\n"
            response += f"Pour répondre à votre demande concernant '{prompt}' :\n\n"
            response += "## Recommandations Générales\n\n"
            response += "1. **Évaluation**: Commencez par évaluer les besoins spécifiques de la mission\n"
            response += "2. **Planification**: Développez un plan d'action détaillé avec objectifs clairs\n"
            response += "3. **Ressources**: Identifiez et mobilisez les ressources nécessaires\n"
            response += "4. **Coordination**: Collaborez avec les organisations locales et autorités\n"
            response += "5. **Exécution**: Mettez en œuvre votre plan avec flexibilité\n"
            response += "6. **Suivi**: Documentez et évaluez l'impact de vos actions\n\n"
            response += "## Principes Humanitaires\n"
            response += "- **Humanité**: Sauver des vies et alléger la souffrance\n"
            response += "- **Impartialité**: Agir uniquement selon les besoins\n"
            response += "- **Neutralité**: Ne prendre parti dans aucun conflit\n"
            response += "- **Indépendance**: Autonomie d'action humanitaire\n\n"
            response += "---\n"
            response += "*Conseils générés par Guardian Volunteer - Plateforme humanitaire IA2GOOD*\n"
        else:
            response = f"# Humanitarian Assistance: {category.title()}\n\n"
            response += f"Regarding your request about '{prompt}':\n\n"
            response += "## General Recommendations\n\n"
            response += "1. **Assessment**: Begin by evaluating the specific needs of the mission\n"
            response += "2. **Planning**: Develop a detailed action plan with clear objectives\n"
            response += "3. **Resources**: Identify and mobilize necessary resources\n"
            response += "4. **Coordination**: Collaborate with local organizations and authorities\n"
            response += "5. **Execution**: Implement your plan with flexibility\n"
            response += "6. **Follow-up**: Document and evaluate the impact of your actions\n\n"
            response += "## Humanitarian Principles\n"
            response += "- **Humanity**: Save lives and alleviate suffering\n"
            response += "- **Impartiality**: Act solely on the basis of need\n"
            response += "- **Neutrality**: Do not take sides in conflicts\n"
            response += "- **Independence**: Autonomy of humanitarian action\n\n"
            response += "---\n"
            response += "*Guidance generated by Guardian Volunteer - IA2GOOD Humanitarian Platform*\n"
        
        return response
    
    async def generate(
        self,
        prompt: str,
        model: str = "internal-gpt-xl",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        task_type: str = "general",
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using internal models
        
        Args:
            prompt: Input prompt
            model: Model to use (internal-gpt-xl, internal-text-pro, etc.)
            max_tokens: Maximum tokens (not strictly enforced)
            temperature: Temperature (affects randomness - not used in current implementation)
            task_type: Type of task (medical, educational, quiz, summary, general)
            language: Target language (auto-detected if not provided)
            **kwargs: Additional parameters
            
        Returns:
            Generated text and metadata
        """
        try:
            # Detect language
            if not language:
                language = self._detect_language(prompt)
            
            # Check for Guardian/humanitarian tasks
            category = kwargs.get("category")
            if category in ["environment", "animal", "homeless", "humanitarian"]:
                cat, topic = self._find_humanitarian_topic(prompt, category)
                if cat and topic:
                    generated_text = self._generate_humanitarian_guidance(cat, topic, prompt, language)
                else:
                    generated_text = self._generate_generic_humanitarian(category, prompt, language)
            
            # Generate based on task type
            elif task_type == "medical":
                topic = self._find_medical_topic(prompt)
                if topic:
                    generated_text = self._generate_medical_explanation(topic, language)
                else:
                    generated_text = self._generate_generic_response(prompt, language)
            
            elif task_type == "educational":
                topic = self._find_educational_topic(prompt)
                if topic:
                    generated_text = self._generate_educational_content(topic, language)
                else:
                    generated_text = self._generate_generic_response(prompt, language)
            
            elif task_type == "quiz":
                num_questions = kwargs.get("num_questions", 3)
                questions = self._generate_quiz(prompt, language, num_questions)
                return {
                    "success": True,
                    "questions": questions,
                    "model": model,
                    "provider": "AI Leader (Internal)",
                    "cost": 0.0,
                    "actual_cost": 0.0,
                    "language": language
                }
            
            elif task_type == "summary":
                style = kwargs.get("style", "concise")
                generated_text = self._generate_summary(prompt, style, language)
            
            else:  # general
                # Try to detect if it's medical, educational, or humanitarian
                medical_topic = self._find_medical_topic(prompt)
                educational_topic = self._find_educational_topic(prompt)
                cat, hum_topic = self._find_humanitarian_topic(prompt, category)
                
                if medical_topic:
                    generated_text = self._generate_medical_explanation(medical_topic, language)
                elif educational_topic:
                    generated_text = self._generate_educational_content(educational_topic, language)
                elif cat and hum_topic:
                    generated_text = self._generate_humanitarian_guidance(cat, hum_topic, prompt, language)
                else:
                    generated_text = self._generate_generic_response(prompt, language)
            
            # Calculate token count (approximate)
            token_count = len(generated_text.split())
            
            logger.info(f"✅ Generated {token_count} tokens for prompt: {prompt[:50]}...")
            
            return {
                "success": True,
                "text": generated_text,
                "model": model,
                "provider": "AI Leader (Internal)",
                "tokens_used": token_count,
                "cost": 0.0,
                "actual_cost": 0.0,
                "language": language,
                "task_type": task_type
            }
            
        except Exception as e:
            logger.error(f"❌ Internal text generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "prompt": prompt
            }


# Global instance
_generator = None

def get_internal_text_generator() -> InternalTextGenerator:
    """Get or create global generator instance"""
    global _generator
    if _generator is None:
        _generator = InternalTextGenerator()
    return _generator
