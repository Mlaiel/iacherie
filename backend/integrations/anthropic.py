"""Anthropic Claude Integration - Production Ready
================================================

Integration professionnelle avec l'API Claude d'Anthropic pour génération
de contenu IA avancée.

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

logger = logging.getLogger(__name__)


@dataclass
class ClaudeMessage:
    """
        Message pour Claude"""
    role: str  # 'user' ou 'assistant'
    content: str


@dataclass
class ClaudeResponse:
    """
        Réponse de Claude"""
    content: str
    model: str
    stop_reason: str
    usage: Dict[str, int]
    raw_response: Dict[str, Any]


class AnthropicAI:
    """
    Client Anthropic Claude Production-Ready
    
    Supporte:
    - Claude 3 Opus (intelligence maximale)
    - Claude 3 Sonnet (équilibré)
    - Claude 3 Haiku (rapide)
    - Streaming responses
    - Gestion erreurs robuste
    """
    
    API_BASE = "https://api.anthropic.com/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialise le client Anthropic
        
        Args:
            api_key: Clé API Anthropic (ou ANTHROPIC_API_KEY env var)

            model: Modèle Claude à utiliser
            max_tokens: Tokens maximum par réponse
            temperature: Température génération (0-1)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY non configurée - Mode simulation")
    
    async def _ensure_session(self):
        """Crée session HTTP si nécessaire"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "x-api-key": self.api_key or "demo-key",
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        messages: Optional[List[ClaudeMessage]] = None
    ) -> ClaudeResponse:
        """
        Génère réponse avec Claude
        
        Args:
            prompt: Prompt utilisateur
            system: Message système (instructions)

            max_tokens: Override max_tokens
            temperature: Override temperature
            messages: Historique conversation (optionnel)

        
        Returns:
            ClaudeResponse avec contenu généré
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info("🤖 Mode simulation Anthropic")

            return ClaudeResponse(
                content=f"[SIMULATION] Réponse Claude à: {prompt[:100]}...",
                model=self.model,
                stop_reason="end_turn",
                usage={"input_tokens": 50, "output_tokens": 100},
                raw_response={}
            )
        
        # Construction messages

        msg_list = []
        if messages:
            msg_list = [{"role": m.role, "content": m.content} for m in messages]
        msg_list.append({"role": "user", "content": prompt})
        
        # Payload API
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "messages": msg_list
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/messages",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    logger.error(f"❌ Anthropic API error {response.status}: {error_text}")

                    raise Exception(f"Anthropic API error: {response.status}")


                
                data = await response.json()

                
                return ClaudeResponse(
                    content=data["content"][0]["text"],
                    model=data["model"],
                    stop_reason=data["stop_reason"],
                    usage=data["usage"],
                    raw_response=data
                )

        
        except Exception as e:
            logger.error(f"❌ Erreur génération Claude: {e}")

            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Génère réponse en streaming
        
        Yields:
            Chunks de texte au fur et à mesure
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info("🤖 Mode simulation streaming Anthropic")

            for word in prompt.split()[:10]:
                yield word + " "
                await asyncio.sleep(0.1)

            return

        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with self.session.post(
                f"{self.API_BASE}/messages",
                json=payload
            ) as response:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()

                    if line_text.startswith('data: '):
                        data = json.loads(line_text[6:])

                        if data.get('type') == 'content_block_delta':
                            yield data['delta'].get('text', '')

        
        except Exception as e:
            logger.error(f"❌ Erreur streaming Claude: {e}")

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


__all__ = ['AnthropicAI', 'ClaudeMessage', 'ClaudeResponse']
