#!/usr/bin/env python3
"""
🎨 POLLINATIONS AI API INTEGRATION
API gratuite illimitée pour génération d'images IA
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import urllib.parse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GeneratedImage:
    """Classe pour représenter une image générée"""
    prompt: str
    url: str
    seed: Optional[int] = None
    model: str = "flux"
    width: int = 1024
    height: int = 1024
    enhance: bool = True
    safe: bool = True
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class PollinationsAPI:
    """Client API pour Pollinations.ai - 100% gratuit et illimité"""
    
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        self.session = None
        
        # Modèles disponibles
        self.available_models = [
            "flux",           # Par défaut - haute qualité
            "flux-realism",   # Style réaliste
            "flux-cablyai",   # Style artistique
            "flux-anime",     # Style anime
            "any-dark",       # Style sombre
            "flux-3d",        # Style 3D
        ]
        
        logger.info("🎨 PollinationsAPI initialisé - 100% gratuit et illimité!")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)  # Plus long pour génération d'images
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    def _build_url(self, 
                   prompt: str, 
                   model: str = "flux",
                   width: int = 1024, 
                   height: int = 1024,
                   seed: Optional[int] = None,
                   enhance: bool = True,
                   safe: bool = True) -> str:
        """Construire l'URL de génération d'image"""
        
        # Encoder le prompt pour URL
        encoded_prompt = urllib.parse.quote(prompt)
        
        # URL de base
        url = f"{self.base_url}/{encoded_prompt}"
        
        # Paramètres
        params = []
        
        if model != "flux":
            params.append(f"model={model}")
        if width != 1024:
            params.append(f"width={width}")
        if height != 1024:
            params.append(f"height={height}")
        if seed is not None:
            params.append(f"seed={seed}")
        if not enhance:
            params.append("enhance=false")
        if not safe:
            params.append("safe=false")
        
        # Ajouter les paramètres à l'URL
        if params:
            url += "?" + "&".join(params)
            
        return url

    async def generate_image(self, 
                           prompt: str,
                           model: str = "flux",
                           width: int = 1024,
                           height: int = 1024, 
                           seed: Optional[int] = None,
                           enhance: bool = True,
                           safe: bool = True) -> Optional[GeneratedImage]:
        """Générer une image avec Pollinations AI"""
        
        if model not in self.available_models:
            logger.warning(f"⚠️ Modèle {model} non reconnu, utilisation de 'flux'")
            model = "flux"
            
        logger.info(f"🎨 Génération d'image: '{prompt}' avec modèle {model}")
        
        try:
            url = self._build_url(prompt, model, width, height, seed, enhance, safe)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    # L'URL est directement l'image générée
                    logger.info(f"✅ Image générée avec succès: {len(await response.read())} bytes")
                    
                    return GeneratedImage(
                        prompt=prompt,
                        url=url,
                        seed=seed,
                        model=model,
                        width=width,
                        height=height,
                        enhance=enhance,
                        safe=safe
                    )
                else:
                    logger.error(f"❌ Erreur de génération: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de génération: {e}")
            return None

    async def generate_multiple_images(self, 
                                     prompt: str,
                                     count: int = 4,
                                     model: str = "flux",
                                     width: int = 1024,
                                     height: int = 1024,
                                     different_seeds: bool = True) -> List[GeneratedImage]:
        """Générer plusieurs images avec des graines différentes"""
        
        tasks = []
        
        for i in range(count):
            seed = i + 1000 if different_seeds else None
            task = self.generate_image(
                prompt=prompt,
                model=model,
                width=width,
                height=height,
                seed=seed,
                enhance=True,
                safe=True
            )
            tasks.append(task)
        
        logger.info(f"🎨 Génération de {count} images en parallèle...")
        
        results = await asyncio.gather(*tasks)
        successful_results = [img for img in results if img is not None]
        
        logger.info(f"✅ {len(successful_results)}/{count} images générées avec succès")
        return successful_results

    async def generate_style_variations(self, 
                                      prompt: str,
                                      width: int = 1024,
                                      height: int = 1024) -> Dict[str, GeneratedImage]:
        """Générer le même prompt avec différents styles"""
        
        styles_to_test = ["flux", "flux-realism", "flux-anime", "flux-3d"]
        results = {}
        
        logger.info(f"🎨 Génération avec {len(styles_to_test)} styles différents...")
        
        for style in styles_to_test:
            image = await self.generate_image(
                prompt=prompt,
                model=style,
                width=width,
                height=height,
                enhance=True,
                safe=True
            )
            
            if image:
                results[style] = image
                logger.info(f"✅ Style {style}: succès")
            else:
                logger.warning(f"⚠️ Style {style}: échec")
        
        return results

    def get_optimized_prompt(self, basic_prompt: str, style: str = "professional") -> str:
        """Optimiser un prompt pour de meilleurs résultats"""
        
        style_modifiers = {
            "professional": "professional, high quality, detailed, 8k resolution",
            "artistic": "artistic, creative, masterpiece, detailed artwork",
            "realistic": "photorealistic, highly detailed, professional photography",
            "anime": "anime style, manga, detailed illustration, vibrant colors",
            "3d": "3d rendered, blender, octane render, high quality 3d",
            "vintage": "vintage style, retro, classic, film photography",
            "modern": "modern, contemporary, sleek, minimalist design"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["professional"])
        optimized = f"{basic_prompt}, {modifier}"
        
        return optimized

    async def download_image(self, image: GeneratedImage, filepath: str) -> bool:
        """Télécharger une image générée vers un fichier"""
        try:
            async with self.session.get(image.url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Créer le dossier si nécessaire
                    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Écrire le fichier
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"💾 Image sauvegardée: {filepath}")
                    return True
                else:
                    logger.error(f"❌ Erreur de téléchargement: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur de sauvegarde: {e}")
            return False

    def get_models_info(self) -> Dict:
        """Obtenir les informations sur les modèles disponibles"""
        return {
            "flux": {
                "description": "Modèle par défaut, haute qualité, polyvalent",
                "best_for": "Usage général, qualité élevée"
            },
            "flux-realism": {
                "description": "Optimisé pour le photoréalisme",
                "best_for": "Photos réalistes, portraits, paysages"
            },
            "flux-cablyai": {
                "description": "Style artistique créatif",
                "best_for": "Art conceptuel, créations artistiques"
            },
            "flux-anime": {
                "description": "Style anime et manga",
                "best_for": "Personnages anime, illustrations manga"
            },
            "any-dark": {
                "description": "Style sombre et dramatique",
                "best_for": "Ambiances sombres, gothic, horror"
            },
            "flux-3d": {
                "description": "Rendu 3D professionnel",
                "best_for": "Objets 3D, architecture, produits"
            }
        }

# Fonctions utilitaires
async def test_integration():
    """Tester l'intégration Pollinations AI"""
    try:
        async with PollinationsAPI() as api:
            # Test de génération simple
            print("🎨 Test génération d'image simple...")
            image = await api.generate_image(
                prompt="A beautiful sunset over mountains",
                model="flux",
                width=512,
                height=512
            )
            
            if image:
                print(f"✅ Image générée: {image.url}")
                print(f"📝 Prompt: {image.prompt}")
                print(f"🎨 Modèle: {image.model}")
                
                # Test de variations de style
                print("\n🎨 Test variations de style...")
                variations = await api.generate_style_variations(
                    prompt="A robot in a futuristic city",
                    width=512,
                    height=512
                )
                
                print(f"✅ {len(variations)} variations générées:")
                for style, img in variations.items():
                    print(f"   🎭 {style}: {img.url[:50]}...")
                
                # Test d'optimisation de prompt
                print("\n✨ Test optimisation de prompt...")
                basic_prompt = "cat sitting on table"
                optimized = api.get_optimized_prompt(basic_prompt, "professional")
                print(f"📝 Original: {basic_prompt}")
                print(f"⚡ Optimisé: {optimized}")
                
                # Informations sur les modèles
                print("\n📊 Modèles disponibles:")
                models_info = api.get_models_info()
                for model, info in models_info.items():
                    print(f"   🎨 {model}: {info['description']}")
                
                return True
            else:
                print("❌ Échec de génération d'image")
                return False
                
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)