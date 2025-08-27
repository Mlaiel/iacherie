# IA Influencer Agent - Module d'Infrastructure Core

## 🏗️ Systèmes Core de Niveau Entreprise

Ce module fournit l'infrastructure fondamentale pour la plateforme IA Influencer Agent, implémentant des systèmes professionnels pour la protection de contenu, le traitement IA, et la collaboration d'influenceurs.

### 🎯 Aperçu de la Logique Métier

**Workflow Multi-Créateur:** Musiciens, blogueurs, photographes, influenceurs, comédiens → Upload contenu multi-format → Protection IA & gestion des droits → SEO professionnel → Matching collaboration → Distribution multi-plateforme

### 👥 Équipe d'Experts

**Chef de Projet & Architecte:** Fahed Mlaiel <mlaiel@live.de>
- **Spécialités:** Lead Développeur IA, Ingénieur Backend Senior, Ingénieur ML, Administrateur de Base de Données, Expert Sécurité, Architecte Microservices, Spécialiste Traitement Audio, Ingénieur DevOps, Ingénieur Prompt IA

---

## ⚠️ AVERTISSEMENT PROPRIÉTÉ INTELLECTUELLE

**AVIS STRICT DE DROITS D'AUTEUR - UTILISATION NON AUTORISÉE INTERDITE**

Ce logiciel, concept et implémentation sont la propriété intellectuelle exclusive de **Fahed Mlaiel** (mlaiel@live.de).

**AVERTISSEMENT À TOUTES PERSONNES ET ENTITÉS:**
- **AUCUNE PERMISSION** n'est accordée pour copier, modifier, distribuer ou utiliser ce code sans autorisation écrite explicite de Fahed Mlaiel
- **DES ACTIONS LÉGALES** seront poursuivies contre toute utilisation non autorisée, copie ou vol de cette propriété intellectuelle
- **DES DOMMAGES MONÉTAIRES** et une réparation injonctive seront réclamés pour toute violation
- Ce code est protégé par les lois et traités internationaux sur les droits d'auteur

**Contact pour les licences:** mlaiel@live.de

---

## 🏭 Composants d'Infrastructure Core

### 🔧 Gestion de Configuration (`config.py`)
- Configuration basée sur l'environnement avec des défauts sécurisés
- Support multi-environnement (développement, test, production)
- Paramètres centralisés avec validation de type utilisant Pydantic

### 🗄️ Intégration Base de Données (`db.py`)
- Base de données PostgreSQL principale avec pool de connexions
- Couche de cache Redis avec stratégies intelligentes
- Gestion de session de base de données avec cycle de vie approprié

### 📊 Journalisation d'Entreprise (`logging.py`)
- Journalisation JSON structurée avec IDs de corrélation
- Formats de sortie multiples (console, fichier, distant)
- Surveillance des performances et suivi des erreurs

### 🔐 Framework de Sécurité (`security.py`)
- Authentification JWT avec jetons de rafraîchissement
- Gestion de clés API avec limitation de taux
- Isolation de sécurité multi-locataire

### ⚡ Gestion des Exceptions (`exceptions.py`)
- Hiérarchie d'erreurs complète pour la logique métier
- Codes d'erreur professionnels et messages conviviaux
- Mappage de codes de statut HTTP avec contexte détaillé

### 🏗️ Injection de Dépendance (`container.py`)
- Conteneur IoC professionnel avec gestion du cycle de vie
- Enregistrement de service avec durées de vie singleton, transient et scoped
- Résolution automatique des dépendances avec les indices de type

### 🚀 Système d'Événements (`events.py`)
- Event Sourcing de domaine avec métadonnées complètes
- Bus d'événements asynchrone avec gestion des priorités
- Événements métier pour le workflow de protection de contenu

### 💾 Cache Multi-Niveau (`cache.py`)
- Hiérarchie de cache L1 (Mémoire) + L2 (Redis) + L3 (Base de données)
- Stratégies d'invalidation de cache intelligentes (LRU, LFU, TTL)
- Promotion de cache et générateurs de clés spécifiques au métier

### 🌐 Contexte de Requête (`context.py`)
- Traçage distribué avec IDs de corrélation
- Session utilisateur et isolation locataire
- Suivi du contexte d'opération métier

### 📈 Métriques et Surveillance (`metrics.py`)
- Métriques métier pour le workflow de protection de contenu
- Surveillance des performances système avec timing et compteurs
- Observabilité professionnelle avec format compatible Prometheus

### 🩺 Surveillance de Santé (`health.py`)
- Vérifications de santé complètes pour toutes les dépendances
- Surveillance base de données, Redis, APIs externes et stockage
- Dégradation gracieuse avec rapport de statut détaillé

### 🛡️ Limitation de Taux (`rate_limit.py`)
- Algorithmes multiples: Token Bucket, Sliding Window, Fixed Window
- Portées configurables: Utilisateur, IP, Clé API, Endpoint, Locataire
- Limitation de taux professionnelle avec en-têtes appropriés

---

## 🚀 Démarrage Rapide

```python
from app.core import (
    settings,
    get_db,
    get_cache_manager,
    get_event_bus,
    get_metrics_registry,
    check_system_health
)

# Initialiser les systèmes core
cache = get_cache_manager()
metrics = get_metrics_registry()
event_bus = await get_event_bus()

# Vérifier la santé du système
health_status = await check_system_health()
print(f"Statut Système: {health_status.overall_status.value}")
```

## 🎯 Intégration Métriques Métier

```python
from app.core import get_business_metrics

business_metrics = get_business_metrics()

# Enregistrer upload de contenu
business_metrics.record_content_upload(
    content_type="audio",
    file_size_mb=25.5,
    user_id="user123"
)

# Enregistrer génération d'empreinte
business_metrics.record_fingerprint_generation(
    content_type="audio",
    duration_ms=1250.0,
    accuracy_score=0.95
)
```

## 🔄 Architecture Événementielle

```python
from app.core import publish_event, ContentUploadedEvent

# Publier événement métier
await publish_event(ContentUploadedEvent(
    content_id="content123",
    user_id="user123",
    content_type="audio",
    file_path="/uploads/audio/song.mp3",
    file_size=26214400
))
```

---

## 📋 Dépendances du Module

- **FastAPI**: Framework web moderne avec documentation automatique
- **Pydantic**: Validation de données et gestion des paramètres
- **SQLAlchemy**: ORM de base de données avec support async
- **Redis**: Cache haute performance et stockage de session
- **Prometheus Client**: Collection de métriques et surveillance

## 🔗 Points d'Intégration

Ce module core s'intègre avec:
- **Système de Protection de Contenu** (`app.content_protection`)
- **Pipeline de Traitement IA** (`app.ai`)
- **Couche Logique Métier** (`app.business`)
- **Gateway API** (`app.api`)
- **Framework de Sécurité** (`app.security`)

---

## 📝 Licence et Contact

**Copyright © 2025 IA Influencer Agent - Fahed Mlaiel**
**Tous Droits Réservés**

**Pour les demandes de licence:** mlaiel@live.de
**Utilisation non autorisée strictement interdite**
