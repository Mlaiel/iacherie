# 🚀 Module de Distribution - Services Docker

**Infrastructure de Distribution de la Plateforme Ainflue**

Système de distribution de contenu multi-plateforme avec planification intelligente, adaptation de format et synchronisation cross-plateforme pour musiciens, blogueurs, photographes, influenceurs et comédiens.

## 🎯 Services Principaux

### **Connecteurs de Plateforme**
- Intégration YouTube, Instagram, TikTok, Spotify, SoundCloud
- Connecteurs Facebook, Twitter, LinkedIn, Pinterest
- Connecteurs API personnalisés pour plateformes de niche
- Synchronisation temps réel et authentification

### **Planificateur de Publication**
- Analyse de timing optimal pour engagement maximum
- Planification multi-fuseaux avec optimisation locale
- File d'attente de contenu et publication par lots
- Tests A/B pour stratégies de publication

### **Adaptateur de Format**
- Conversion automatique de format pour chaque plateforme
- Optimisation du ratio d'aspect (16:9, 9:16, 1:1, 4:5)
- Mise à l'échelle qualité et optimisation compression
- Insertion de métadonnées spécifiques aux plateformes

### **Agrégateur d'Analytics**
- Métriques de performance cross-plateforme
- Analyse et reporting du taux d'engagement
- Suivi ROI et attribution des revenus
- Agrégation démographiques d'audience

## 🛠️ Architecture des Services

```yaml
# Services de Distribution Docker Compose
version: '3.8'
services:
  platform-connectors:
    build: ./platform_connectors.dockerfile
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - INSTAGRAM_ACCESS_TOKEN=${INSTAGRAM_ACCESS_TOKEN}
      - TIKTOK_CLIENT_KEY=${TIKTOK_CLIENT_KEY}
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
    
  publication-scheduler:
    build: ./publication_scheduler.dockerfile
    depends_on:
      - redis
      - postgres
    
  format-adapter:
    build: ./format_adapter.dockerfile
    volumes:
      - media_processing:/app/media
      - format_cache:/app/cache
    
  analytics-aggregator:
    build: ./analytics_aggregator.dockerfile
    environment:
      - ANALYTICS_DB_URL=${ANALYTICS_DB_URL}
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# Clés API de Plateforme
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
TIKTOK_CLIENT_KEY=your_tiktok_key
SPOTIFY_CLIENT_ID=your_spotify_id

# URLs de Base de Données
ANALYTICS_DB_URL=postgresql://user:pass@analytics-db:5432/analytics
REDIS_URL=redis://redis:6379/0

# Paramètres de Traitement
MAX_CONCURRENT_UPLOADS=10
FORMAT_QUALITY_PRESET=high
ENABLE_AB_TESTING=true
```

## 📊 Surveillance & Vérifications de Santé

Tous les services incluent des vérifications de santé et métriques complètes:
- Taux de réussite des uploads et suivi d'erreurs
- Surveillance des limites de taux API de plateforme
- Profondeur de file d'attente de traitement de contenu
- Analytics d'engagement cross-plateforme

## 🚀 Démarrage

```bash
# Déployer les services de distribution
docker-compose -f docker-compose.distribution.yml up -d

# Surveiller la santé des services
docker-compose ps

# Voir les logs agrégés
docker-compose logs -f analytics-aggregator
```

---

**Auteur:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** © 2025 Fahed Mlaiel. Tous droits réservés.