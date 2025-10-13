"""
Quiz Generator Service
Génération automatique de quiz avec IA (GPT-4, Claude, Gemini)
"""
import logging
import json
import os
from typing import List, Dict
from uuid import UUID
import openai
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """Service de génération de quiz automatique"""
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("✅ OpenAI client initialized")
        else:
            logger.warning("⚠️ No OpenAI API key found - quiz generation will use fallback")
        
    async def generate_quiz(
        self,
        content_text: str,
        num_questions: int = 10,
        difficulty: str = "medium",
        language: str = "fr",
        question_types: List[str] = None
    ) -> Dict:
        """
        Générer un quiz à partir de contenu
        
        Utilise LLM (GPT-4, Claude, Gemini) pour générer:
        - Questions pertinentes
        - Choix de réponses (QCM avec distracteurs intelligents)
        - Questions vrai/faux
        - Questions ouvertes
        - Explications détaillées
        - Références au contenu source
        
        Args:
            content_text: Texte du contenu source
            num_questions: Nombre de questions (5-50)
            difficulty: Difficulté (easy, medium, hard)
            language: Langue du quiz
            question_types: Types de questions (mcq, true_false, open)
            
        Returns:
            Dict avec quiz généré (questions, réponses, explications)
        """
        logger.info(f"Generating quiz: {num_questions} questions, difficulty: {difficulty}")
        
        if question_types is None:
            question_types = ["mcq", "true_false"]
        
        # Generate questions using LLM or fallback
        questions = await self._generate_questions_with_ai(
            content_text,
            num_questions,
            difficulty,
            question_types,
            language
        )
        
        quiz = {
            "title": "Quiz généré automatiquement",
            "difficulty": difficulty,
            "language": language,
            "total_questions": len(questions),
            "questions": questions
        }
        
        logger.info(f"✅ Quiz generated with {len(quiz['questions'])} questions")
        return quiz
    
    async def _generate_questions_with_ai(
        self,
        content: str,
        num_questions: int,
        difficulty: str,
        question_types: List[str],
        language: str
    ) -> List[Dict]:
        """Générer les questions du quiz avec AI"""
        
        # Use OpenAI if available
        if self.client:
            try:
                return await self._generate_with_openai(
                    content, num_questions, difficulty, question_types, language
                )
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Quiz generation failed. OpenAI API key required. Error: {str(e)}"
                )
        
        # No fallback - require real AI generation
        raise HTTPException(
            status_code=503,
            detail="Quiz generation requires OpenAI API key to be configured"
        )
    
    async def _generate_with_openai(
        self,
        content: str,
        num_questions: int,
        difficulty: str,
        question_types: List[str],
        language: str
    ) -> List[Dict]:
        """Generate questions using OpenAI GPT-4"""
        
        difficulty_map = {
            "easy": "facile (niveau débutant)",
            "medium": "moyen (niveau intermédiaire)",
            "hard": "difficile (niveau avancé)"
        }
        
        types_description = {
            "mcq": "questions à choix multiple (4 options)",
            "true_false": "questions vrai/faux",
            "open_ended": "questions ouvertes"
        }
        
        prompt = f"""Tu es un expert en pédagogie. Génère {num_questions} questions de quiz basées sur le contenu suivant.

CONTENU:
{content[:3000]}  

CONSIGNES:
- Difficulté: {difficulty_map.get(difficulty, 'moyen')}
- Types de questions: {', '.join([types_description.get(t, t) for t in question_types])}
- Langue: {language}
- Chaque question doit avoir:
  * Une question claire et précise
  * Des options de réponse (pour QCM)
  * La réponse correcte
  * Une explication détaillée
  * Une référence au contenu source

Format de réponse (JSON strict):
{{
  "questions": [
    {{
      "id": "q1",
      "type": "mcq",
      "question": "Quelle est...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option B",
      "explanation": "La réponse correcte est B parce que...",
      "reference": "Référence au texte source",
      "points": 1,
      "difficulty": "{difficulty}"
    }}
  ]
}}

Génère UNIQUEMENT le JSON, sans texte avant ou après."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[
                {"role": "system", "content": "Tu es un générateur de quiz éducatif expert. Réponds uniquement en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in code blocks
        if "```json" in ai_response:
            ai_response = ai_response.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_response:
            ai_response = ai_response.split("```")[1].split("```")[0].strip()
        
        try:
            quiz_data = json.loads(ai_response)
            questions = quiz_data.get("questions", [])
            
            # Ensure proper format
            formatted_questions = []
            for i, q in enumerate(questions[:num_questions]):
                formatted_questions.append({
                    "id": q.get("id", f"q{i+1}"),
                    "type": q.get("type", "mcq"),
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct_answer": q.get("correct_answer", ""),
                    "explanation": q.get("explanation", ""),
                    "reference": q.get("reference", ""),
                    "points": q.get("points", 1),
                    "difficulty": q.get("difficulty", difficulty)
                })
            
            logger.info(f"✅ Generated {len(formatted_questions)} questions with OpenAI")
            return formatted_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            logger.debug(f"Response was: {ai_response[:500]}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse AI response. OpenAI returned invalid JSON."
            )
    
    async def validate_quiz_quality(self, quiz: Dict) -> float:
        """
        Valider la qualité du quiz
        
        Critères:
        - Questions pertinentes au contenu
        - Distracteurs plausibles (pas évidents)
        - Explications claires et complètes
        - Couverture équilibrée du contenu
        - Pas de questions ambiguës
        
        Returns:
            Score de qualité (0-1, cible >0.85)
        """
        # TODO: Implement quality validation
        # TODO: Use review model or heuristics
        
        quality_score = 0.90  # Placeholder
        logger.info(f"Quiz quality score: {quality_score}")
        
        return quality_score
    
    async def adapt_difficulty(
        self,
        user_id: UUID,
        current_difficulty: str
    ) -> str:
        """
        Adapter la difficulté selon l'historique de l'utilisateur
        
        Apprentissage adaptatif:
        - Analyser performances passées
        - Ajuster difficulté progressivement
        - Identifier lacunes et renforcer
        
        Returns:
            Difficulté recommandée (easy, medium, hard)
        """
        # TODO: Query user's past quiz results
        # TODO: Calculate average score and adapt
        
        return "medium"  # Placeholder
