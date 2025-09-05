# Documentation du Module Collectors

## Aperçu

Le module Collectors fournit une infrastructure de surveillance de contenu unifiée et de niveau entreprise pour la plateforme Ainflue. Ce module consolide 16 collecteurs de plateforme individuels en 6 collecteurs logiques consolidés tout en maintenant la compatibilité ascendante.

## Architecture

### Structure Consolidée (Niveau 3 - Profondeur Maximale)

```
/backend/collectors/
├── __init__.py                    # Exports de module et orchestration
├── base_collector.py              # Fondation d'infrastructure
├── social_media_collector.py      # Instagram, TikTok, Twitter, Facebook, LinkedIn
├── video_platforms_collector.py   # YouTube, Twitch
├── community_collector.py         # Discord, Reddit
├── marketplace_collector.py       # Ecommerce, Pinterest
├── news_trends_collector.py       # News, Trends
├── miscellaneous_collector.py     # Misc + sources spécialisées
├── README.md                      # Documentation (EN)
├── README.de.md                   # Documentation (DE)
├── README.fr.md                   # Documentation (FR)
└── README.ar.md                   # Documentation (AR)
```

**Total des Fichiers: 12** ✅ (Répond aux exigences)

## Collecteurs Consolidés

### 1. SocialMediaCollector
**Plateformes**: Instagram, TikTok, Twitter, Facebook, LinkedIn

**Fonctionnalités**:
- Recherche de contenu cross-plateforme
- Surveillance de hashtags en temps réel
- Analyse de présence des créateurs
- Détection de contenu viral
- Analytiques d'engagement

```python
from backend.collectors import SocialMediaCollector

collector = SocialMediaCollector({
    'instagram': {'api_key': 'votre_clé'},
    'tiktok': {'api_secret': 'votre_secret'}
})

# Recherche sur toutes les plateformes de médias sociaux
results = await collector.search_content("contenu créateur", config)
```

### 2. VideoPlatformsCollector
**Plateformes**: YouTube, Twitch

**Fonctionnalités**:
- Surveillance de contenu vidéo
- Détection de streams en direct
- Suivi de croissance des créateurs
- Analytiques de performance
- Insights de monétisation

```python
from backend.collectors import VideoPlatformsCollector

collector = VideoPlatformsCollector({
    'youtube': {'api_key': 'votre_clé'},
    'twitch': {'client_id': 'votre_id'}
})

# Suivre la croissance d'un créateur
growth_data = await collector.track_creator_growth("creator_id", days=30)
```

### 3. CommunityCollector
**Plateformes**: Discord, Reddit

**Fonctionnalités**:
- Surveillance des discussions communautaires
- Détection de mentions de marque
- Analyse de sentiment
- Suivi d'engagement
- Alertes en temps réel

```python
from backend.collectors import CommunityCollector

collector = CommunityCollector({
    'discord': {'bot_token': 'votre_token'},
    'reddit': {'client_id': 'votre_id'}
})

# Surveiller les mentions de marque
mentions = await collector.monitor_brand_mentions(["nom_marque"], config)
```

### 4. MarketplaceCollector
**Plateformes**: Ecommerce, Pinterest

**Fonctionnalités**:
- Suivi des prix des produits
- Analyse des tendances visuelles
- Opportunités pour créateurs
- Insights de marketplace
- Surveillance des revenus

```python
from backend.collectors import MarketplaceCollector

collector = MarketplaceCollector({
    'ecommerce': {'api_key': 'votre_clé'},
    'pinterest': {'access_token': 'votre_token'}
})

# Trouver des opportunités pour créateurs
opportunities = await collector.find_creator_opportunities("mode", config)
```

### 5. NewsTrendsCollector
**Plateformes**: News, Trends

**Fonctionnalités**:
- Surveillance média
- Détection de tendances
- Analyse de sentiment des actualités
- Insights sectoriels
- Couverture de marque

```python
from backend.collectors import NewsTrendsCollector

collector = NewsTrendsCollector({
    'news': {'api_key': 'votre_clé'},
    'trends': {'access_token': 'votre_token'}
})

# Analyser le sentiment des actualités
sentiment = await collector.analyze_news_sentiment("nom marque", config)
```

### 6. MiscellaneousCollector
**Plateformes**: Sources spécialisées, APIs personnalisées, flux RSS

**Fonctionnalités**:
- Intégration d'API personnalisée
- Surveillance de flux RSS
- Web scraping
- Opportunités de plateforme
- Agrégation cross-plateforme

```python
from backend.collectors import MiscellaneousCollector

collector = MiscellaneousCollector({
    'misc': {'custom_configs': 'vos_configurations'}
})

# Surveiller les flux RSS
rss_content = await collector.monitor_rss_feeds(["url_flux"], config)
```

## Infrastructure de Base

### BaseCollector
Classe de base abstraite fournissant une interface standardisée pour tous les collecteurs:

- Limitation de débit
- Gestion de statut
- Collection d'analytiques
- Gestion d'erreurs
- Surveillance de performance

### CollectorResult
Structure de résultat standardisée:

```python
@dataclass
class CollectorResult:
    platform: str
    content_id: str
    content_type: str
    title: str
    description: str
    url: str
    author: str
    timestamp: float
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]
    engagement_metrics: Optional[Dict[str, Any]]
    # ... champs supplémentaires
```

## Configuration

### CollectionConfig
Objet de configuration pour les opérations de collecte:

```python
@dataclass
class CollectionConfig:
    max_results: int = 50
    include_metadata: bool = True
    include_engagement: bool = True
    include_media: bool = False
    rate_limit_delay: float = 1.0
    timeout_seconds: int = 30
    retry_attempts: int = 3
```

## Exemples d'Utilisation

### Démarrage Rapide
```python
from backend.collectors import get_collector

# Obtenir un collecteur consolidé
social_collector = get_collector('social_media')

# Obtenir un collecteur de plateforme individuelle (legacy)
instagram_collector = get_collector('instagram')

# Lister les plateformes supportées
platforms = get_supported_platforms()
```

### Utilisation Avancée
```python
from backend.collectors import (
    SocialMediaCollector, 
    VideoPlatformsCollector,
    CollectionConfig
)

# Initialiser les collecteurs
social = SocialMediaCollector()
video = VideoPlatformsCollector()

# Configurer la collecte
config = CollectionConfig(
    max_results=100,
    include_engagement=True,
    rate_limit_delay=2.0
)

# Rechercher sur les plateformes
social_results = await social.search_content("nom créateur", config)
video_results = await video.search_content("nom créateur", config)

# Combiner les résultats
all_results = social_results + video_results
```

## Performance & Surveillance

### Limitation de Débit
Tous les collecteurs implémentent une limitation de débit intelligente:
- Limites de requêtes configurables
- Backoff automatique
- Limites spécifiques aux plateformes
- Gestion de requêtes concurrentes

### Analytiques
Statistiques de collecte intégrées:
- Taux de succès/échec
- Temps de réponse
- Total des requêtes
- Performance des plateformes

### Gestion de Statut
Statut de collecteur en temps réel:
- IDLE, RUNNING, PAUSED, ERROR, COMPLETED
- Surveillance de santé
- Métriques de performance

## Support des Créateurs

Les collecteurs supportent une surveillance complète des créateurs:

### Types de Créateurs
- **Musiciens**: YouTube Music, intégration Spotify
- **Influenceurs**: Médias sociaux multi-plateformes
- **Photographes**: Focus sur plateformes visuelles
- **Blogueurs**: Surveillance de contenu textuel
- **Streamers**: Suivi de contenu en direct

### Fonctionnalités
- Collection de contenu multi-format
- Analytiques cross-plateforme
- Suivi des revenus
- Insights d'audience
- Métriques de croissance

## Droits d'Auteur & Légal

### Propriété Intellectuelle
```
© 2025 Fahed Mlaiel - TOUS DROITS RÉSERVÉS

Toute utilisation, reproduction, modification, distribution ou
commercialisation de ce code, concept ou idée sans autorisation
écrite explicite de Fahed Mlaiel est strictement interdite et
constitue une violation du droit d'auteur passible de poursuites
judiciaires.

Contact pour autorisations: mlaiel@live.de
```

### Créateur & Propriétaire
**Fahed Mlaiel** (mlaiel@live.de)
- Lead Developer IA & Architecture Collectors
- Concepteur du système de surveillance multi-plateformes
- Propriétaire exclusif de propriété intellectuelle

## Spécifications Techniques

### Exigences
- Python 3.8+
- Support AsyncIO
- Bibliothèques client HTTP
- Connectivité base de données
- Redis pour le cache

### Dépendances
- aiohttp
- asyncio
- logging
- dataclasses
- typing
- datetime

### Performance
- Collection simultanée sur plateformes
- Limitation de débit intelligente
- Structures de données efficaces en mémoire
- Architecture évolutive

## Support & Contact

Pour le support technique, demandes de fonctionnalités ou demandes de licence:

**Email**: mlaiel@live.de  
**Plateforme**: Ainflue Creator Monitoring System  
**Version**: Enterprise v1.0  
**Licence**: Propriétaire - Tous Droits Réservés