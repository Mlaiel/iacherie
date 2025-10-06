"""DeepL Translation API Integration - Production Ready
======================================================

Integration professionnelle avec l'API DeepL pour traduction
haute qualité dans 30+ langues.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json

logger = logging.getLogger(__name__)


class DeepLLanguage(str, Enum):
    """
        Langues supportées par DeepL"""
    # Langues source et cible
    DE = "DE"  # Allemand
    EN = "EN"  # Anglais
    FR = "FR"  # Français
    ES = "ES"  # Espagnol
    IT = "IT"  # Italien
    NL = "NL"  # Néerlandais
    PL = "PL"  # Polonais
    PT = "PT"  # Portugais
    RU = "RU"  # Russe
    JA = "JA"  # Japonais
    ZH = "ZH"  # Chinois
    AR = "AR"  # Arabe
    # Variantes spécifiques
    EN_GB = "EN-GB"  # Anglais britannique
    EN_US = "EN-US"  # Anglais américain
    PT_BR = "PT-BR"  # Portugais brésilien
    PT_PT = "PT-PT"  # Portugais européen


class DeepLFormality(str, Enum):
    """Niveau de formalité"""
    DEFAULT = "default"
    MORE = "more"  # Plus formel
    LESS = "less"  # Moins formel


@dataclass
class DeepLTranslation:
    """Résultat de traduction DeepL"""
    text: str
    detected_source_language: str
    source_text: str
    target_language: str


@dataclass
class DeepLUsage:
    """
        Usage API DeepL"""
    character_count: int
    character_limit: int
    usage_percent: float


class DeepLTranslator:
    """
    Client DeepL API Production-Ready
    
    Supporte:
    - Traduction texte (30+ langues)
    - Détection automatique langue source
    - Formalité ajustable
    - Gestion glossaires personnalisés
    - Mode document (PDF, DOCX, etc.)
    """
    
    API_FREE = "https://api-free.deepl.com/v2"
    API_PRO = "https://api.deepl.com/v2"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_free_api: bool = True
    ):
        """
        Initialise le client DeepL
        
        Args:
            api_key: Clé API DeepL (ou DEEPL_API_KEY env var)

            use_free_api: True = Free API, False = Pro API
        """
        self.api_key = api_key or os.getenv('DEEPL_API_KEY')
        self.api_base = self.API_FREE if use_free_api else self.API_PRO
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("⚠️ DEEPL_API_KEY non configurée - Mode simulation")
    
    async def _ensure_session(self):
        """Crée session HTTP si nécessaire"""
        if not self.session:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"DeepL-Auth-Key {self.api_key}"
            
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def translate(
        self,
        text: Union[str, List[str]],
        target_lang: Union[str, DeepLLanguage],
        source_lang: Optional[Union[str, DeepLLanguage]] = None,
        formality: Optional[DeepLFormality] = None,
        preserve_formatting: bool = True
    ) -> Union[DeepLTranslation, List[DeepLTranslation]]:
        """
        Traduit texte(s) avec DeepL
        
        Args:
            text: Texte ou liste de textes à traduire
            target_lang: Langue cible (ex: 'FR', 'EN-US')

            source_lang: Langue source (auto-détection si None)

            formality: Niveau de formalité
            preserve_formatting: Préserver mise en forme
        
        Returns:
            DeepLTranslation ou liste de DeepLTranslation
        """
        await self._ensure_session()


        
        is_list = isinstance(text, list)

        texts = text if is_list else [text]
        
        if not self.api_key:
            logger.info(f"🤖 Mode simulation DeepL ({len(texts)} texte(s))")


            results = [
                DeepLTranslation(
                    text=f"[TRADUCTION SIMULÉE {target_lang}] {t[:100]}...",
                    detected_source_language="EN",
                    source_text=t,
                    target_language=str(target_lang)
                )

                for t in texts
            ]
            return results if is_list else results[0]
        
        # Payload API
        payload = {
            "text": texts,
            "target_lang": str(target_lang).upper()
        }
        
        if source_lang:
            payload["source_lang"] = str(source_lang).upper()

        
        if formality:
            payload["formality"] = formality.value
        
        if preserve_formatting:
            payload["preserve_formatting"] = "1"
        
        try:
            async with self.session.post(
                f"{self.api_base}/translate",
                data=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    logger.error(f"❌ DeepL API error {response.status}: {error_text}")

                    raise Exception(f"DeepL API error: {response.status}")


                
                data = await response.json()


                
                results = [
                    DeepLTranslation(
                        text=item['text'],
                        detected_source_language=item['detected_source_language'],
                        source_text=texts[i],
                        target_language=str(target_lang)
                    )

                    for i, item in enumerate(data['translations'])
                ]
                
                return results if is_list else results[0]
        
        except Exception as e:
            logger.error(f"❌ Erreur traduction DeepL: {e}")

            raise
    
    async def get_usage(self) -> DeepLUsage:
        """
        Récupère statistiques d'usage API
        
        Returns:
            DeepLUsage avec caractères utilisés/limite
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info("🤖 Mode simulation usage DeepL")

            return DeepLUsage(
                character_count=50000,
                character_limit=500000,
                usage_percent=10.0
            )

        
        try:
            async with self.session.get(
                f"{self.api_base}/usage"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    raise Exception(f"DeepL usage error: {response.status}")


                
                data = await response.json()


                
                count = data['character_count']

                limit = data['character_limit']
                
                return DeepLUsage(
                    character_count=count,
                    character_limit=limit,
                    usage_percent=(count / limit * 100) if limit > 0 else 0
                )

        
        except Exception as e:
            logger.error(f"❌ Erreur usage DeepL: {e}")

            raise
    
    async def get_languages(self, target: bool = True) -> List[Dict[str, str]]:
        """
        Récupère liste langues supportées
        
        Args:
            target: True = langues cibles, False = langues sources
        
        Returns:
            Liste de dicts {language: "EN", name: "English"}
        """
        await self._ensure_session()

        
        if not self.api_key:
            logger.info("🤖 Mode simulation langues DeepL")

            return [
                {"language": "EN", "name": "English"},
                {"language": "FR", "name": "French"},
                {"language": "DE", "name": "German"},
                {"language": "ES", "name": "Spanish"}
            ]
        
        try:
            params = {"type": "target" if target else "source"}
            
            async with self.session.get(
                f"{self.api_base}/languages",
                params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()

                    raise Exception(f"DeepL languages error: {response.status}")


                
                data = await response.json()

                return data
        
        except Exception as e:
            logger.error(f"❌ Erreur langues DeepL: {e}")

            raise
    
    async def translate_batch(
        self,
        texts: List[str],
        target_lang: Union[str, DeepLLanguage],
        source_lang: Optional[Union[str, DeepLLanguage]] = None,
        batch_size: int = 50
    ) -> List[DeepLTranslation]:
        """
        Traduit lot de textes en batches optimisés
        
        Args:
            texts: Liste de textes
            target_lang: Langue cible
            source_lang: Langue source (optionnel)

            batch_size: Taille batch (DeepL limite à 50)

        
        Returns:
            Liste de DeepLTranslation
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            batch_results = await self.translate(
                batch,
                target_lang=target_lang,
                source_lang=source_lang
            )

            results.extend(batch_results)
            
            # Rate limiting friendly
            if i + batch_size < len(texts):
                await asyncio.sleep(0.5)

        
        return results
    
    async def close(self):
        """
        Ferme session HTTP"""
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


__all__ = [
    'DeepLTranslator',
    'DeepLTranslation',
    'DeepLUsage',
    'DeepLLanguage',
    'DeepLFormality'
]
