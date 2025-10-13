"""HuggingFace Hub Integration - Production Ready
===============================================

Integration professionnelle avec HuggingFace Hub pour modèles IA,
embeddings, et inférence.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import aiohttp
import json
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HFInferenceResult:
    """
        Résultat d'inférence HuggingFace"""
    output: Any
    model: str
    task: str
    raw_response: Dict[str, Any]


class HuggingFaceAPI:
    """
    Client HuggingFace Hub Production-Ready
    
    Supporte:
    - Text generation (GPT, LLaMA, Mistral)
    - Embeddings (sentence-transformers)
    - Classification
    - Translation
    - Summarization
    - Question Answering
    """
    
    API_BASE = "https://api-inference.huggingface.co/models"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    ):
        """
        Initialise le client HuggingFace
        
        Args:
            api_key: Token HuggingFace (ou HF_TOKEN env var)

            default_model: Modèle par défaut
        """
        self.api_key = api_key or os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
        self.default_model = default_model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("⚠️ HF_TOKEN non configuré - Mode simulation")
    
    async def _ensure_session(self):
        """Crée session HTTP si nécessaire"""
        if not self.session:
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> HFInferenceResult:
        """
        Génère texte avec un modèle HuggingFace
        
        Args:
            prompt: Texte d'entrée
            model: Modèle à utiliser (default: self.default_model)

            max_length: Longueur max génération
            temperature: Température (0-2)

            top_p: Nucleus sampling
        
        Returns:
            HFInferenceResult avec texte généré
        """
        await self._ensure_session()


        
        model = model or self.default_model
        
        if not self.api_key:
            logger.info(f"🤖 Mode simulation HuggingFace ({model})")

            return HFInferenceResult(
                output=f"[SIMULATION] Réponse {model}: {prompt[:80]}...",
                model=model,
                task="text-generation",
                raw_response={}
            )


        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False
            }
        }
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/{model}",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    logger.error(f"❌ HuggingFace API error {response.status}: {error_text}")

                    raise Exception(f"HuggingFace API error: {response.status}")


                
                data = await response.json()
                
                # Extraction texte selon format API
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get('generated_text', '')

                else:
                    generated_text = data.get('generated_text', str(data))

                
                return HFInferenceResult(
                    output=generated_text,
                    model=model,
                    task="text-generation",
                    raw_response=data
                )

        
        except Exception as e:
            logger.error(f"❌ Erreur génération HuggingFace: {e}")

            raise
    
    async def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> np.ndarray:
        """
        Génère embeddings pour texte(s)

        
        Args:
            texts: Texte ou liste de textes
            model: Modèle d'embedding
        
        Returns:
            Array numpy d'embeddings (shape: [n_texts, embedding_dim])
        """
        await self._ensure_session()

        
        if isinstance(texts, str):
            texts = [texts]
        
        if not self.api_key:
            logger.info(f"🤖 Mode simulation embeddings ({model})")

            return np.random.randn(len(texts), 384).astype(np.float32)


        
        payload = {
            "inputs": texts
        }
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/{model}",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    logger.error(f"❌ HuggingFace embeddings error {response.status}: {error_text}")

                    raise Exception(f"HuggingFace embeddings error: {response.status}")


                
                data = await response.json()
                
                # Conversion en numpy array
                if isinstance(data, list):
                    embeddings = np.array(data, dtype=np.float32)

                else:
                    embeddings = np.array([data], dtype=np.float32)

                
                return embeddings
        
        except Exception as e:
            logger.error(f"❌ Erreur embeddings HuggingFace: {e}")

            raise
    
    async def classify(
        self,
        text: str,
        model: str = "facebook/bart-large-mnli"
    ) -> HFInferenceResult:
        """
        Classification de texte
        
        Args:
            text: Texte à classifier
            model: Modèle de classification
        
        Returns:
            HFInferenceResult avec labels et scores
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info(f"🤖 Mode simulation classification ({model})")

            return HFInferenceResult(
                output=[
                    {"label": "POSITIVE", "score": 0.85},
                    {"label": "NEGATIVE", "score": 0.15}
                ],
                model=model,
                task="classification",
                raw_response={}
            )


        
        payload = {"inputs": text}
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/{model}",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    raise Exception(f"HuggingFace classification error: {response.status}")


                
                data = await response.json()

                
                return HFInferenceResult(
                    output=data,
                    model=model,
                    task="classification",
                    raw_response=data
                )

        
        except Exception as e:
            logger.error(f"❌ Erreur classification HuggingFace: {e}")

            raise
    
    async def summarize(
        self,
        text: str,
        model: str = "facebook/bart-large-cnn",
        max_length: int = 150
    ) -> HFInferenceResult:
        """
        Résumé de texte
        
        Args:
            text: Texte à résumer
            model: Modèle de summarization
            max_length: Longueur max résumé
        
        Returns:
            HFInferenceResult avec résumé
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info(f"🤖 Mode simulation summarization ({model})")

            return HFInferenceResult(
                output=f"[RÉSUMÉ SIMULÉ] {text[:100]}...",
                model=model,
                task="summarization",
                raw_response={}
            )


        
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length
            }
        }
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/{model}",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    raise Exception(f"HuggingFace summarization error: {response.status}")


                
                data = await response.json()


                
                summary = data[0]['summary_text'] if isinstance(data, list) else data.get('summary_text', '')

                
                return HFInferenceResult(
                    output=summary,
                    model=model,
                    task="summarization",
                    raw_response=data
                )

        
        except Exception as e:
            logger.error(f"❌ Erreur summarization HuggingFace: {e}")

            raise
    
    async def close(self):
        """Ferme session HTTP"""
        if self.session:
            await self.session.close()

            self.session = None
    
    async def __aenter__(self):
        """
        Context manager async"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, *args):
        """
        Context manager exit"""
        await self.close()


__all__ = ['HuggingFaceAPI', 'HFInferenceResult']
