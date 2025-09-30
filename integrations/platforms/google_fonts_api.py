#!/usr/bin/env python3
"""
🔤 GOOGLE FONTS API INTEGRATION
Service gratuit pour accéder aux polices Google Fonts
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib.parse
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FontFamily:
    """Informations sur une famille de polices"""
    family: str
    category: str
    variants: List[str]
    subsets: List[str]
    version: str
    last_modified: str
    popularity: Optional[int] = None
    files: Optional[Dict[str, str]] = None

@dataclass
class FontFile:
    """Fichier de police téléchargé"""
    family: str
    variant: str
    format: str
    url: str
    local_path: Optional[str] = None
    size_bytes: Optional[int] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class GoogleFontsAPI:
    """Client pour Google Fonts API - Service 100% gratuit"""
    
    def __init__(self, api_key: Optional[str] = None):
        # L'API Google Fonts est gratuite mais avec clé optionnelle pour plus de données
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/webfonts/v1/webfonts"
        self.fonts_css_url = "https://fonts.googleapis.com/css2"
        self.session = None
        
        # Cache des polices
        self._fonts_cache = None
        self._popular_fonts = [
            "Open Sans", "Roboto", "Lato", "Montserrat", "Source Sans Pro",
            "Oswald", "Raleway", "PT Sans", "Lora", "Ubuntu", "Playfair Display",
            "Merriweather", "Nunito", "Roboto Condensed", "Poppins"
        ]
        
        logger.info("🔤 GoogleFontsAPI initialisé - Service gratuit")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def get_all_fonts(self, sort: str = "popularity") -> Optional[List[FontFamily]]:
        """Obtenir toutes les polices disponibles"""
        
        if self._fonts_cache:
            logger.info("📦 Utilisation du cache des polices")
            return self._fonts_cache
            
        logger.info("🔤 Récupération de toutes les polices Google Fonts...")
        
        try:
            params = {"sort": sort}
            if self.api_key:
                params["key"] = self.api_key
                
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    fonts = []
                    for font_data in data.get("items", []):
                        font = FontFamily(
                            family=font_data.get("family", ""),
                            category=font_data.get("category", ""),
                            variants=font_data.get("variants", []),
                            subsets=font_data.get("subsets", []),
                            version=font_data.get("version", ""),
                            last_modified=font_data.get("lastModified", ""),
                            files=font_data.get("files", {})
                        )
                        fonts.append(font)
                    
                    # Ajouter la popularité basée sur l'ordre
                    for i, font in enumerate(fonts):
                        font.popularity = i + 1
                    
                    self._fonts_cache = fonts
                    logger.info(f"✅ {len(fonts)} polices récupérées")
                    return fonts
                    
                elif response.status == 403:
                    logger.warning("⚠️ Accès sans clé API - fonctionnalités limitées")
                    return await self._get_popular_fonts_fallback()
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return await self._get_popular_fonts_fallback()
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return await self._get_popular_fonts_fallback()

    async def _get_popular_fonts_fallback(self) -> List[FontFamily]:
        """Fallback avec les polices populaires (sans API)"""
        
        logger.info("🔤 Mode fallback - polices populaires")
        
        popular_fonts = []
        for i, family_name in enumerate(self._popular_fonts):
            # Créer des données basiques pour les polices populaires
            font = FontFamily(
                family=family_name,
                category="sans-serif",
                variants=["regular", "700"],
                subsets=["latin"],
                version="v1",
                last_modified=datetime.now().isoformat(),
                popularity=i + 1
            )
            popular_fonts.append(font)
        
        self._fonts_cache = popular_fonts
        return popular_fonts

    async def search_fonts(self, 
                         query: str,
                         category: Optional[str] = None,
                         limit: int = 20) -> List[FontFamily]:
        """Rechercher des polices par nom"""
        
        all_fonts = await self.get_all_fonts()
        if not all_fonts:
            return []
            
        query_lower = query.lower()
        results = []
        
        for font in all_fonts:
            # Recherche dans le nom de famille
            if query_lower in font.family.lower():
                # Filtrer par catégorie si spécifiée
                if category and font.category != category:
                    continue
                    
                results.append(font)
                
                # Limiter les résultats
                if len(results) >= limit:
                    break
        
        logger.info(f"🔍 Recherche '{query}': {len(results)} résultats")
        return results

    async def get_font_by_family(self, family_name: str) -> Optional[FontFamily]:
        """Obtenir une police spécifique par nom de famille"""
        
        all_fonts = await self.get_all_fonts()
        if not all_fonts:
            return None
            
        for font in all_fonts:
            if font.family.lower() == family_name.lower():
                return font
        
        logger.warning(f"⚠️ Police '{family_name}' non trouvée")
        return None

    async def get_popular_fonts(self, limit: int = 50) -> List[FontFamily]:
        """Obtenir les polices les plus populaires"""
        
        all_fonts = await self.get_all_fonts()
        if not all_fonts:
            return []
            
        # Prendre les premières (les plus populaires)
        popular = all_fonts[:limit]
        
        logger.info(f"🔥 {len(popular)} polices populaires récupérées")
        return popular

    async def get_fonts_by_category(self, category: str) -> List[FontFamily]:
        """Obtenir les polices par catégorie"""
        
        all_fonts = await self.get_all_fonts()
        if not all_fonts:
            return []
            
        filtered = [font for font in all_fonts if font.category == category]
        
        logger.info(f"📂 Catégorie '{category}': {len(filtered)} polices")
        return filtered

    def generate_css_url(self, 
                        families: Union[str, List[str]],
                        variants: Optional[List[str]] = None,
                        display: str = "swap") -> str:
        """Générer l'URL CSS pour charger des polices"""
        
        if isinstance(families, str):
            families = [families]
            
        family_params = []
        
        for family in families:
            family_encoded = urllib.parse.quote_plus(family)
            
            if variants:
                # Ajouter les variantes spécifiées
                variants_str = ";".join(variants)
                family_params.append(f"{family_encoded}:{variants_str}")
            else:
                # Variantes par défaut
                family_params.append(f"{family_encoded}:wght@400;700")
        
        families_param = "|".join(family_params)
        
        css_url = f"{self.fonts_css_url}?family={families_param}&display={display}"
        
        logger.info(f"🔗 URL CSS générée pour {len(families)} polices")
        return css_url

    async def download_font_css(self, 
                              families: Union[str, List[str]],
                              variants: Optional[List[str]] = None) -> Optional[str]:
        """Télécharger le CSS des polices"""
        
        css_url = self.generate_css_url(families, variants)
        
        try:
            async with self.session.get(css_url) as response:
                if response.status == 200:
                    css_content = await response.text()
                    logger.info(f"✅ CSS téléchargé: {len(css_content)} caractères")
                    return css_content
                else:
                    logger.error(f"❌ Erreur téléchargement CSS: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement CSS: {e}")
            return None

    async def download_font_files(self, 
                                font_family: FontFamily,
                                output_dir: str,
                                variants: Optional[List[str]] = None) -> List[FontFile]:
        """Télécharger les fichiers de police"""
        
        if not font_family.files:
            logger.warning(f"⚠️ Pas de fichiers disponibles pour {font_family.family}")
            return []
            
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_files = []
        variants_to_download = variants or list(font_family.files.keys())
        
        for variant in variants_to_download:
            if variant not in font_family.files:
                logger.warning(f"⚠️ Variante '{variant}' non disponible")
                continue
                
            file_url = font_family.files[variant]
            
            try:
                async with self.session.get(file_url) as response:
                    if response.status == 200:
                        # Déterminer l'extension du fichier
                        content_type = response.headers.get('content-type', '')
                        if 'truetype' in content_type:
                            ext = '.ttf'
                        elif 'opentype' in content_type:
                            ext = '.otf'
                        elif 'woff2' in content_type:
                            ext = '.woff2'
                        elif 'woff' in content_type:
                            ext = '.woff'
                        else:
                            ext = '.ttf'  # Par défaut
                        
                        # Nom du fichier local
                        safe_family = re.sub(r'[^\w\-_]', '_', font_family.family)
                        filename = f"{safe_family}_{variant}{ext}"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Télécharger et sauvegarder
                        content = await response.read()
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        font_file = FontFile(
                            family=font_family.family,
                            variant=variant,
                            format=ext[1:],  # Sans le point
                            url=file_url,
                            local_path=filepath,
                            size_bytes=len(content)
                        )
                        
                        downloaded_files.append(font_file)
                        logger.info(f"💾 Police téléchargée: {filename} ({len(content)} bytes)")
                        
                    else:
                        logger.error(f"❌ Erreur téléchargement {variant}: {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Erreur téléchargement {variant}: {e}")
        
        logger.info(f"✅ {len(downloaded_files)} fichiers de polices téléchargés")
        return downloaded_files

    def get_categories(self) -> List[str]:
        """Obtenir les catégories de polices disponibles"""
        return [
            "serif",
            "sans-serif", 
            "display",
            "handwriting",
            "monospace"
        ]

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur le service Google Fonts"""
        return {
            'service': 'Google Fonts API',
            'base_url': self.base_url,
            'features': [
                'Free font library access',
                'Font search and filtering',
                'CSS generation for web fonts',
                'Font file downloads',
                'Category browsing',
                'Popularity rankings'
            ],
            'categories': self.get_categories(),
            'has_api_key': self.api_key is not None,
            'popular_fonts_count': len(self._popular_fonts),
            'rate_limit': 'None (free tier with limits)',
            'output_formats': ['CSS', 'TTF', 'OTF', 'WOFF', 'WOFF2']
        }

# Fonctions utilitaires
async def test_fonts_integration():
    """Tester l'intégration Google Fonts"""
    try:
        async with GoogleFontsAPI() as fonts_api:
            # Test 1: Polices populaires
            print("🔤 Test polices populaires...")
            popular = await fonts_api.get_popular_fonts(10)
            
            if popular:
                print(f"✅ {len(popular)} polices populaires récupérées")
                for font in popular[:3]:
                    print(f"   {font.family} ({font.category}) - {len(font.variants)} variantes")
            
            # Test 2: Recherche de police
            print("\n🔍 Test recherche de police...")
            search_results = await fonts_api.search_fonts("roboto", limit=5)
            
            if search_results:
                print(f"✅ Recherche 'roboto': {len(search_results)} résultats")
                for font in search_results:
                    print(f"   {font.family} - {font.variants}")
            
            # Test 3: Police spécifique
            print("\n🔤 Test police spécifique...")
            specific_font = await fonts_api.get_font_by_family("Open Sans")
            
            if specific_font:
                print(f"✅ Police trouvée: {specific_font.family}")
                print(f"   Catégorie: {specific_font.category}")
                print(f"   Variantes: {specific_font.variants}")
                print(f"   Sous-ensembles: {specific_font.subsets}")
            
            # Test 4: Génération CSS
            print("\n🔗 Test génération CSS...")
            css_url = fonts_api.generate_css_url(
                families=["Open Sans", "Roboto"],
                variants=["400", "700"]
            )
            print(f"✅ URL CSS générée: {css_url[:80]}...")
            
            # Test 5: Téléchargement CSS
            print("\n💾 Test téléchargement CSS...")
            css_content = await fonts_api.download_font_css(["Open Sans"])
            
            if css_content:
                print(f"✅ CSS téléchargé: {len(css_content)} caractères")
                print(f"   Aperçu: {css_content[:100]}...")
            
            # Test 6: Catégories
            print("\n📂 Test catégories...")
            categories = fonts_api.get_categories()
            print(f"✅ Catégories disponibles: {categories}")
            
            category_fonts = await fonts_api.get_fonts_by_category("serif")
            if category_fonts:
                print(f"✅ Polices serif: {len(category_fonts)}")
            
            # Test 7: Informations service
            print("\n📊 Informations service...")
            service_info = fonts_api.get_service_info()
            print(f"✅ Service: {service_info['service']}")
            print(f"🔤 Catégories: {len(service_info['categories'])}")
            print(f"📦 Formats: {service_info['output_formats']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test Google Fonts: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration Google Fonts
    result = asyncio.run(test_fonts_integration())
    sys.exit(0 if result else 1)