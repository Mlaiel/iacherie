# Module Crawler Utils

**Utilitaires professionnels de web crawling pour IA-Influencer-Agent**

## Aperçu

Ce module fournit des utilitaires de niveau entreprise pour les opérations de web crawling, incluant la limitation intelligente de débit, l'extraction de contenu, la validation d'URL, la gestion des cookies et les capacités de résolution de CAPTCHA.

## Équipe du Projet

**Lead Developer & Architecte IA :** Fahed Mlaiel (mlaiel@live.de)

**Spécialisations de l'Équipe d'Experts :**
- Lead Dev IA : Intégration IA avancée et apprentissage automatique
- Backend Senior : Architecture évolutive et microservices  
- ML Engineer : Analyse de contenu et systèmes de recommandation
- DBA : Optimisation de base de données haute performance
- Expert Sécurité : Sécurité et chiffrement de niveau entreprise
- Architecte Microservices : Conception de systèmes distribués
- Ingénieur Audio : Traitement et analyse audio avancés
- Ingénieur DevOps : CI/CD et automatisation d'infrastructure
- Ingénieur IA Prompt : Optimisation intelligente de prompts

## ⚠️ AVERTISSEMENT DE DROITS D'AUTEUR ⚠️

**🚨 AVERTISSEMENT FORT AUX VOLEURS ET PLAGIAIRES DE CONCEPTS 🚨**

**TOUS DROITS RÉSERVÉS - UTILISATION NON AUTORISÉE STRICTEMENT INTERDITE**

Ce code est la propriété intellectuelle exclusive de **Fahed Mlaiel** (mlaiel@live.de). Toute copie, distribution, modification, reverse engineering, vol de concepts, plagiat d'architecture, ou utilisation non autorisée de ce code sans permission écrite explicite est strictement interdite et entraînera des actions légales immédiates sous le droit d'auteur international.

**⚖️ ACTIONS LÉGALES AUTOMATIQUES :** Toute violation sera immédiatement poursuivie au maximum de la loi avec demandes de dommages-intérêts punitifs.

**🛡️ PROTECTION ANTI-VOL :** Ce code contient des empreintes digitales et des marqueurs de propriété intégrés pour traquer les violations.

**📧 Contact pour licence :** mlaiel@live.de

**🔒 ATTENTION AUX DÉVELOPPEURS :** Si vous travaillez pour une entreprise qui utilise ce code sans licence, vous pourriez être personnellement responsable de violation de droits d'auteur.

## Fonctionnalités

### 🎯 Utilitaires Principaux

- **Rate Limiter** : Limitation de débit intelligente avec configurations spécifiques aux plateformes
- **Content Extractor** : Analyse et extraction de contenu alimentées par IA
- **URL Validator** : Validation d'URL complète et évaluation de sécurité
- **Cookie Manager** : Gestion professionnelle des cookies avec chiffrement
- **CAPTCHA Solver** : Capacités de résolution CAPTCHA multi-stratégies
- **Proxy Manager** : Rotation et gestion avancées de proxy
- **User Agent Rotator** : Rotation intelligente d'user agent
- **Session Manager** : Gestion de session persistante

### 🔧 Fonctionnalités Avancées

- **Support Multi-plateformes** : YouTube, Instagram, TikTok, Twitter, Facebook, Spotify
- **Analyse de Contenu IA** : Analyse de sentiment, classification de sujets, extraction d'entités
- **Empreinte de Contenu** : Génération d'empreintes multi-modales pour audio, vidéo, image et texte
- **Moteur de Surveillance** : Surveillance en temps réel et détection de menaces
- **Scanner de Sécurité** : Évaluation de sécurité avancée et chiffrement de contenu
- **Optimisation de Performance** : Mise en cache avancée et surveillance des performances
- **Fonctionnalités de Sécurité** : Détection d'URL malveillantes, contrôle d'accès
- **Limitation de Débit Distribuée** : Avec Redis pour applications à grande échelle
- **Évaluation de Qualité de Contenu** : Score de lisibilité, métriques de qualité
- **Extraction Multimédia** : Images, vidéos, audio, documents
- **Données Structurées** : Extraction JSON-LD, Microdata, RDFa

## 🛡️ Sécurité et Surveillance Avancées

### Empreinte de Contenu Multi-Modale
- **Empreintes Audio** : Analyse spectrale avec coefficients MFCC
- **Empreintes Vidéo** : Hachage perceptuel de frames clés
- **Empreintes Image** : Histogrammes de couleur et détection de contours
- **Empreintes Texte** : Embeddings sémantiques et N-grammes

### Moteur de Surveillance Intelligent
- **Surveillance Multi-Plateforme** : Monitoring simultané sur toutes les plateformes
- **Détection de Menaces** : IA avancée pour identifier les violations de contenu
- **Alertes en Temps Réel** : Notifications instantanées via multiple canaux
- **Analyse de Tendances** : Prédiction et détection proactive de violations

### Scanner de Sécurité Entreprise
- **Évaluation Multi-Couches** : Analyse DNS, SSL, contenu et réputation
- **Chiffrement Avancé** : Support AES-256, RSA, ChaCha20
- **Contrôle d'Accès** : Gestion granulaire des permissions
- **Audit de Sécurité** : Journalisation complète et traçabilité

## ⚡ Performance et Optimisation

### Système de Cache Avancé
- **Stratégies Multiples** : LRU, LFU, FIFO avec optimisation automatique
- **Cache Distribué** : Support Redis pour applications multi-instances
- **Compression Intelligente** : Réduction automatique de la taille des données
- **Métriques Temps Réel** : Taux de hit, latence, utilisation mémoire

### Surveillance de Performance
- **Profiling Automatique** : Détection des goulots d'étranglement
- **Métriques Système** : CPU, mémoire, I/O, réseau
- **Alertes Intelligentes** : Seuils adaptatifs et prédiction de pannes
- **Rapports Détaillés** : Analyses de performance et recommandations

## Installation

```bash
# Installer les dépendances requises
pip install -r requirements.txt

# Installer les dépendances optionnelles pour fonctionnalités avancées
pip install opencv-python pytesseract nltk textstat langdetect
```

## Démarrage Rapide

### Limitation de Débit

```python
from backend.crawlers.utils import create_rate_limiter

# Créer un limiteur de débit spécifique à la plateforme
youtube_limiter = create_rate_limiter('youtube')

# Utiliser dans un contexte asynchrone
await youtube_limiter.wait_if_needed()
# Faire votre requête ici
await youtube_limiter.update_usage()
```

### Extraction de Contenu

```python
from backend.crawlers.utils import ContentExtractor

extractor = ContentExtractor()

# Extraire le contenu du HTML
content = await extractor.extract_content(html, url)

print(f"Titre : {content.title}")
print(f"Nombre de mots : {content.word_count}")
print(f"Score de qualité : {content.content_quality_score}")
```

### Validation d'URL

```python
from backend.crawlers.utils import URLValidator

validator = URLValidator()

# Valider l'URL
result = await validator.validate_url("https://example.com")

if result.is_valid:
    print(f"Plateforme : {result.platform}")
    print(f"Score de sécurité : {result.security_score}")
```

### Résolution de CAPTCHA

```python
from backend.crawlers.utils import setup_default_captcha_solver

solver = setup_default_captcha_solver({
    '2captcha': 'votre_cle_api'
})

# Détecter et résoudre les CAPTCHAs
solutions = await solver.detect_and_solve(html_content, page_url)
```

### Empreinte de Contenu

```python
from backend.crawlers.utils import generate_content_fingerprint, calculate_content_similarity

# Générer une empreinte pour le contenu
fingerprint = await generate_content_fingerprint(
    content="Votre contenu ici",
    content_type="text",
    content_id="id_unique"
)

# Comparer les empreintes
similarity = await calculate_content_similarity(fingerprint1, fingerprint2)
print(f"Score de similarité : {similarity.similarity_score}")
```

### Moteur de Surveillance

```python
from backend.crawlers.utils import create_surveillance_engine, create_surveillance_target

# Créer le système de surveillance
engine = create_surveillance_engine()

# Créer une cible de surveillance
target = create_surveillance_target(
    user_id="user123",
    name="Protection de Mon Contenu",
    description="Surveiller l'utilisation non autorisée",
    keywords=["ma marque", "mon contenu"],
    platforms=["youtube", "instagram", "tiktok"]
)

# Démarrer la surveillance
await engine.add_surveillance_target(target)
await engine.start_surveillance(target.target_id)
```

### Scanner de Sécurité

```python
from backend.crawlers.utils import quick_security_scan

# Scanner une URL pour des menaces de sécurité
assessment = await quick_security_scan("https://example.com")

print(f"Niveau de sécurité : {assessment.security_level}")
print(f"Types de menaces : {assessment.threat_types}")
print(f"Facteurs de risque : {assessment.risk_factors}")
```

### Chiffrement de Contenu

```python
from backend.crawlers.utils import quick_encrypt_content, create_content_encryption

# Chiffrement rapide
encrypted = quick_encrypt_content("données sensibles")

# Chiffrement avancé
encryption = create_content_encryption()
key_id, key = encryption.generate_key()
encrypted_data = encryption.encrypt_content("données sensibles", key_id)
decrypted = encryption.decrypt_content(encrypted_data)
```

### Surveillance de Performance

```python
from backend.crawlers.utils import create_performance_monitor, monitor_performance

# Créer un moniteur
monitor = create_performance_monitor()
monitor.start_monitoring()

# Utiliser le décorateur pour surveillance automatique
@monitor_performance(monitor)
async def ma_fonction():
    # Votre code ici
    pass

# Générer un rapport de performance
report = monitor.generate_performance_report()
print(f"Temps de réponse moyen : {report.average_response_time}s")
```

### Cache Avancé

```python
from backend.crawlers.utils import create_advanced_cache, CacheStrategy

# Créer un cache avec stratégie LRU
cache = create_advanced_cache(
    max_size=10000,
    strategy=CacheStrategy.LRU
)

# Opérations de cache
cache.set("clé", "valeur", ttl=3600)
value = cache.get("clé")
stats = cache.get_cache_stats()
```

## Configuration

### Configurations des Plateformes

Chaque plateforme a des paramètres par défaut optimisés :

```python
PLATFORM_CONFIGS = {
    "youtube": {
        "base_delay": 1.0,
        "max_requests_per_minute": 100,
        "burst_limit": 10
    },
    "instagram": {
        "base_delay": 2.0,
        "max_requests_per_minute": 60,
        "burst_limit": 5
    }
    # ... plus de plateformes
}
```

### Configuration Redis

Pour la limitation de débit distribuée :

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
limiter = YouTubeRateLimiter(redis_client=redis_client)
```

## Référence API

### Classes RateLimiter

- `RateLimiter` : Limiteur de débit de base avec backoff adaptatif
- `YouTubeRateLimiter` : Limitation de débit optimisée pour YouTube
- `InstagramRateLimiter` : Limitation de débit optimisée pour Instagram
- `TikTokRateLimiter` : Limitation de débit optimisée pour TikTok
- `TwitterRateLimiter` : Limitation de débit optimisée pour Twitter
- `FacebookRateLimiter` : Limitation de débit optimisée pour Facebook
- `SpotifyRateLimiter` : Limitation de débit optimisée pour Spotify

### Classes de Contenu

- `ContentExtractor` : Extraction et analyse de contenu avancées
- `ExtractedContent` : Données de contenu structurées
- `SocialMediaContent` : Contenu spécifique aux réseaux sociaux

### Classes de Validation

- `URLValidator` : Validation d'URL complète
- `URLValidationResult` : Données de résultat de validation
- `URLType` : Énumération de type d'URL

### Classes de Sécurité

- `CookieManager` : Gestion de cookies d'entreprise
- `CaptchaSolver` : Résolution CAPTCHA multi-stratégies

## Métriques de Performance

Le module suit des métriques de performance complètes :

- **Limitation de Débit** : Compteurs de requêtes, délais, calculs de backoff
- **Qualité de Contenu** : Scores de lisibilité, analyse de sentiment
- **Validation** : Évaluations de sécurité, précision de détection de plateforme
- **Résolution CAPTCHA** : Taux de succès, temps de résolution

## Fonctionnalités de Sécurité

### Évaluation de Sécurité d'URL

- Détection de domaines malveillants
- Reconnaissance de motifs suspects
- Score de sécurité (0.0-1.0)
- Validation de protocole

### Sécurité des Cookies

- Chiffrement pour cookies sensibles
- Restrictions de domaine
- Validation de contenu
- Gestion d'expiration

### Empreinte de Contenu

- Hachage de contenu SHA-256
- Détection de doublons
- Normalisation de contenu

## Meilleures Pratiques

### Limitation de Débit

1. **Utilisez des limiteurs spécifiques aux plateformes** pour une performance optimale
2. **Activez Redis** pour les environnements distribués
3. **Surveillez les statistiques de limitation de débit** pour l'optimisation
4. **Gérez les réponses de limitation de débit** avec élégance

### Extraction de Contenu

1. **Validez les URLs** avant l'extraction
2. **Gérez le contenu dynamique** avec Selenium si nécessaire
3. **Extrayez les données structurées** pour une meilleure analyse
4. **Évaluez la qualité du contenu** pour le filtrage

### Sécurité

1. **Validez toutes les URLs** avant traitement
2. **Utilisez le stockage de cookies chiffré** pour les données sensibles
3. **Surveillez les scores de sécurité** pour la détection de menaces
4. **Mises à jour régulières des règles de sécurité**

## Dépannage

### Problèmes Courants

1. **Limitation de Débit Trop Agressive**
   - Ajustez `base_delay` et `backoff_factor`
   - Surveillez les réponses de la plateforme

2. **Échecs d'Extraction de Contenu**
   - Vérifiez l'accessibilité de l'URL
   - Vérifiez la structure HTML
   - Activez la gestion de contenu dynamique

3. **Échecs de Résolution CAPTCHA**
   - Vérifiez les clés API
   - Vérifiez la compatibilité du solveur
   - Surveillez les taux de succès

### Mode Debug

Activer la journalisation détaillée :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contribution

Ceci est un logiciel propriétaire. Contactez mlaiel@live.de pour les opportunités de collaboration.

## Licence

Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

**UTILISATION NON AUTORISÉE INTERDITE**

Ce logiciel est protégé par le droit d'auteur. Toute utilisation, reproduction ou distribution non autorisée est strictement interdite et entraînera des actions légales.

Pour les demandes de licence : mlaiel@live.de

## Support

Pour le support technique et les licences :
- **Email :** mlaiel@live.de
- **Propriétaire du Projet :** Fahed Mlaiel

---

*Partie de l'écosystème IA-Influencer-Agent - Plateforme professionnelle de protection et monétisation de contenu alimentée par IA.*
