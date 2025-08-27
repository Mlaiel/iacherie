# Module de Configuration de Sécurité - Plateforme IA Influencer Agent

## Vue d'ensemble

Le Module de Configuration de Sécurité fournit des paramètres de sécurité complets de niveau entreprise pour la plateforme IA Influencer Agent. Ce module garantit le plus haut niveau de sécurité pour les créateurs de contenu, les intégrations de plateformes, les opérations de revenus et les systèmes de protection de contenu alimentés par IA dans plusieurs formats (audio, vidéo, image, texte).

## Spécialisations de l'Équipe Projet

**Créateur & Chef de Projet**: Fahed Mlaiel <mlaiel@live.de>

**Spécialisations de l'Équipe d'Experts**:
- Lead Developer IA + Ingénieur Backend Senior
- Ingénieur Machine Learning + Spécialiste Traitement Audio
- Administrateur de Base de Données (DBA) + Expert Sécurité
- Architecte Microservices + Ingénieur DevOps
- Ingénieur IA Prompt + Spécialiste Protection de Contenu
- Ingénieur Sécurité FinTech + Expert Traitement de Paiements
- Spécialiste Intégration Plateformes + Ingénieur Sécurité API

## ⚠️ AVERTISSEMENT DE DROITS D'AUTEUR

**STRICTEMENT CONFIDENTIEL ET PROPRIÉTAIRE**

Ce code, concept et propriété intellectuelle appartiennent exclusivement à **Fahed Mlaiel**.

Toute utilisation non autorisée, copie, distribution, modification ou ingénierie inverse de ce code sans permission écrite explicite de Fahed Mlaiel est **STRICTEMENT INTERDITE** et entraînera des actions juridiques immédiates.

**Avis Juridique**:
- Ce logiciel est protégé par le droit d'auteur international
- L'accès ou l'utilisation non autorisés peuvent entraîner des sanctions civiles et pénales
- Toutes les activités sont surveillées et enregistrées à des fins juridiques
- Contactez mlaiel@live.de pour toute demande de licence

**Pour licence ou collaboration**: mlaiel@live.de

---

## Intégration de la Logique Métier

Le module de sécurité s'intègre parfaitement avec la logique métier principale :

**Parcours Créateur**: Utilisateur (musicien/blogueur/photographe/influenceur/comédien) → Upload multi-format → Protection IA des droits → SEO pro → Collaboration de matching → Distribution multi-plateformes

**Points de Contact Sécurité**:
1. **Authentification** - Accès sécurisé aux comptes créateurs avec authentification multi-facteurs
2. **Upload de Contenu** - Scan malware, validation de format et vérifications de qualité
3. **Traitement IA** - Contenu chiffré pendant les workflows d'empreinte digitale et d'analyse IA
4. **Intégration Plateforme** - Connexions OAuth2 sécurisées vers Spotify, YouTube, Instagram, TikTok
5. **Opérations Revenus** - Protection des données financières, détection de fraude et traitement de paiement sécurisé
6. **Collaboration** - Partage sécurisé, automatisation de licence et distribution des revenus
7. **Protection Contenu** - Surveillance des droits d'auteur alimentée par IA et procédures de retrait automatisées

## Composants du Module

### Modules de Sécurité Principaux

#### 1. Authentification (`authentication.py`)
- **Intégration JWT & OAuth2**: Authentification sécurisée basée sur des tokens
- **Authentification Multi-Facteurs**: TOTP, SMS, email et notifications push
- **Authentification Sociale**: Intégration avec Google, Spotify, Instagram, YouTube
- **Gestion de Session**: Gestion sécurisée des sessions avec backend Redis
- **Sécurité des Mots de Passe**: Politiques avancées et validation de force des mots de passe
- **Gestion des Clés API**: Plusieurs types de clés pour différentes opérations créateurs

#### 2. Autorisation (`authorization.py`)
- **Contrôle d'Accès Basé sur les Rôles (RBAC)**: Rôles créateur, collaborateur, admin
- **Matrice de Permissions**: Permissions granulaires par type de créateur et niveau d'abonnement
- **Contrôle d'Accès aux Ressources**: Restrictions d'accès spécifiques au contenu
- **Gestion des Niveaux d'Abonnement**: Niveaux d'accès gratuit, professionnel, entreprise
- **Permissions Dynamiques**: Évaluation des permissions sensible au contexte

#### 3. Protection de Contenu (`content_protection.py`) 🆕
- **Moteur d'Empreinte Digitale IA**: Empreinte digitale de contenu multi-format
  - Audio: Algorithmes Chromaprint, Essentia, Hash Spectral
  - Vidéo: OpenCV pHash, YOLO Features, Frame Hash
  - Image: CLIP Embedding, Image Hash, Perceptual Hash
  - Texte: BERT Embedding, RoBERTa Similarity, Semantic Hash
- **Surveillance Temps Réel**: Crawling web automatisé et surveillance de contenu
- **Détection de Menaces**: Détection de violation de droits d'auteur alimentée par ML
- **Collection de Preuves**: Capture d'écran et chaîne de custody
- **Tatouage**: Tatouage de contenu invisible et visible

#### 4. Sécurité des Revenus (`revenue_security.py`) 🆕
- **Sécurité Traitement Paiements**: Conformité PCI DSS Level 1
- **Détection de Fraude**: Analyse de transaction alimentée par IA et scoring de risque
- **Suivi des Revenus**: Agrégation et validation des revenus multi-plateformes
- **Paiements Automatisés**: Distribution sécurisée des paiements avec double approbation
- **Conformité Fiscale**: Calcul fiscal automatisé et reporting
- **Résolution de Litiges**: Gestion automatisée des rétrofacturations et soumission de preuves

#### 5. Intégration Plateforme (`platform_integration.py`) 🆕
- **Sécurité OAuth2**: Flux d'authentification plateforme sécurisés
- **Limitation de Taux**: Limitation de taux API intelligente par plateforme
- **Sécurité Webhook**: Vérification de signature et validation d'événements
- **Passerelle API**: Filtrage requête/réponse et patterns circuit-breaker
- **Surveillance & Alertes**: Surveillance santé intégration temps réel
- **Protection des Données**: Chiffrement et conformité confidentialité pour données plateforme

#### 6. Chiffrement (`encryption.py`)
- **Chiffrement AES-256-GCM**: Chiffrement standard industrie pour toutes données sensibles
- **Gestion des Clés**: Intégration Hardware Security Module (HSM)
- **Rotation des Clés**: Procédures automatisées de rotation et dépôt des clés
- **Chiffrement Bout-en-Bout**: Transmission et stockage sécurisés des données

#### 7. Détection de Menaces (`threat_detection.py`)
- **Surveillance Temps Réel**: Surveillance continue des événements de sécurité
- **Analyse Comportementale**: Détection d'anomalies comportementales utilisateur alimentée par ML
- **Réponse Automatisée**: Actions de réponse configurables par niveau de menace
- **Intelligence Sécuritaire**: Intégration avec flux de renseignements sur les menaces

#### 8. Conformité (`compliance.py`)
- **Conformité RGPD**: Conformité règlement européen protection des données
- **Conformité CCPA**: Conformité California Consumer Privacy Act
- **PCI DSS**: Standards sécurité données industrie cartes de paiement
- **Conformité SOX**: Contrôles reporting financier et audit
- **Conformité DMCA**: Procédures Digital Millennium Copyright Act

#### 9. Journalisation d'Audit (`audit_logging.py`)
- **Journalisation Complète**: Pistes d'audit immuables pour toutes activités système
- **Journalisation Structurée**: Logs formatés JSON pour analytics avancées
- **Rétention des Logs**: Politiques de rétention configurables par type de données
- **Reporting Conformité**: Génération automatisée de rapports de conformité

#### 10. Limitation de Taux (`rate_limiting.py`)
- **Limitation de Taux Adaptative**: Limites de taux dynamiques basées sur comportement utilisateur
- **Limites Niveaux Créateur**: Limites différenciées par niveau d'abonnement
- **Limites Spécifiques Plateforme**: Limites personnalisées pour chaque intégration plateforme
- **Protection Burst**: Détection et atténuation burst avancées

#### 11. Validation de Contenu (`content_validation.py`)
- **Scan Malware**: Détection malware multi-moteur
- **Validation Format**: Vérification format et qualité fichier
- **Analyse Contenu**: Détection contenu explicite et droits d'auteur
- **Seuils Qualité**: Exigences qualité minimum par type de contenu

#### 12. Sécurité API (`api_security.py`)
- **Validation Requête**: Assainissement et validation des entrées
- **Filtrage Réponse**: Filtrage sortie et masquage données
- **Configuration CORS**: Sécurité Cross-Origin Resource Sharing
- **En-têtes Sécurité**: Implémentation en-têtes sécurité HTTP

### Fonctionnalités Avancées

#### Gestionnaire Configuration Sécurité (`index.py`) 🆕
- **Configuration Centralisée**: Point unique pour tous paramètres sécurité
- **Profils Sécurité**: Profils préconfigurés pour différents environnements
- **Configuration Niveaux Créateur**: Configuration automatique basée sur niveau abonnement
- **Framework Validation**: Validation configuration complète
- **Reconfiguration Dynamique**: Mises à jour configuration runtime

#### Profils de Sécurité
- **Développement**: Paramètres assouplis pour environnement développement
- **Staging**: Paramètres similaires production pour tests
- **Production**: Contrôles sécurité complets pour environnement live
- **Haute Sécurité**: Sécurité renforcée pour opérations sensibles
- **Entreprise**: Sécurité maximale pour clients entreprise

#### Sécurité Niveaux Créateur
- **Niveau Gratuit**: Sécurité de base avec fonctionnalités limitées
- **Niveau Professionnel**: Sécurité renforcée avec fonctionnalités avancées
- **Niveau Entreprise**: Sécurité maximale avec fonctionnalités premium

## Exemples de Configuration

### Configuration de Base
```python
from backend.config.security import initialize_security_config, SecurityProfile

# Initialisation avec profil sécurité production
security_config = initialize_security_config(
    profile=SecurityProfile.PRODUCTION,
    creator_tier=CreatorTier.PROFESSIONAL
)
```

### Configuration Protection Contenu
```python
from backend.config.security.content_protection import ContentProtectionConfig, ProtectionLevel

# Configuration protection contenu haut niveau
protection_config = ContentProtectionConfig()
protection_config.protection_level = ProtectionLevel.ENTERPRISE
protection_config.fingerprint.similarity_thresholds = {
    ContentType.AUDIO: 0.90,
    ContentType.VIDEO: 0.85,
    ContentType.IMAGE: 0.95
}
```

### Configuration Sécurité Revenus
```python
from backend.config.security.revenue_security import RevenueSecurityConfig

# Configuration sécurité revenus entreprise
revenue_config = RevenueSecurityConfig()
revenue_config.fraud_detection.ml_fraud_detection = True
revenue_config.payment_security.pci_compliance_level = "Level 1"
revenue_config.audit.third_party_audits = True
```

## Conformité Standards Sécurité

### Standards Industrie
- **PCI DSS Level 1**: Conformité industrie cartes de paiement
- **SOC 2 Type II**: Contrôles sécurité et disponibilité
- **ISO 27001**: Gestion sécurité information
- **NIST Cybersecurity Framework**: Contrôles sécurité complets

### Réglementations Confidentialité
- **RGPD**: Règlement Général sur la Protection des Données européen
- **CCPA**: California Consumer Privacy Act
- **PIPEDA**: Canadian Personal Information Protection Act

### Réglementations Financières
- **SOX**: Exigences reporting financier Sarbanes-Oxley
- **AML**: Procédures Anti-Blanchiment d'Argent
- **KYC**: Vérification Know Your Customer

## Performance & Évolutivité

### Fonctionnalités Haute Performance
- **Traitement Parallèle**: Opérations sécurité multi-thread
- **Mise en Cache**: Mise en cache tokens sécurité et permissions basée Redis
- **Opérations Async**: Validations sécurité non-bloquantes
- **Équilibrage Charge**: Architecture service sécurité distribuée

### Métriques Évolutivité
- **10 000+ utilisateurs simultanés**: Support scaling horizontal
- **1M+ événements sécurité quotidiens**: Capacité traitement événements
- **99,99% disponibilité**: Services sécurité haute disponibilité
- **<100ms temps réponse**: Performance validation sécurité

## Surveillance & Alertes

### Surveillance Temps Réel
- **Tableau de Bord Événements Sécurité**: Visualisation événements sécurité live
- **Intelligence Menaces**: Détection et analyse menaces temps réel
- **Métriques Performance**: Surveillance performance services sécurité
- **Statut Conformité**: Surveillance conformité continue

### Catégories d'Alertes
- **Critique**: Menaces sécurité immédiates nécessitant réponse instantanée
- **Élevé**: Événements sécurité significatifs nécessitant attention prompte
- **Moyen**: Événements sécurité importants pour investigation
- **Faible**: Événements sécurité informatifs pour journalisation

## Points d'Intégration

### Intégrations Plateformes
- **API Spotify**: Intégration plateforme musicale sécurisée
- **API YouTube**: Sécurité plateforme vidéo et protection contenu
- **API Instagram**: Connexions sécurisées plateforme médias sociaux
- **API TikTok**: Intégration plateforme vidéo courte

### Intégrations Paiement
- **Stripe**: Traitement paiement primaire avec détection fraude avancée
- **PayPal**: Méthode paiement alternative avec protection acheteur
- **Wise**: Transferts argent internationaux pour créateurs globaux
- **Virements Bancaires**: Intégration bancaire directe pour clients entreprise

### Outils Sécurité
- **OWASP ZAP**: Tests sécurité automatisés
- **Snyk**: Scan vulnérabilités dépendances
- **Semgrep**: Analyse sécurité code statique
- **ClamAV**: Moteur détection malware

## Déploiement & Configuration

### Variables d'Environnement
```bash
# Authentification
JWT_SECRET_KEY=votre_cle_secrete_jwt
OAUTH2_CLIENT_ID=votre_oauth2_client_id
OAUTH2_CLIENT_SECRET=votre_oauth2_client_secret

# Intégration Plateforme
SPOTIFY_CLIENT_ID=votre_spotify_client_id
SPOTIFY_CLIENT_SECRET=votre_spotify_client_secret
YOUTUBE_API_KEY=votre_cle_api_youtube
INSTAGRAM_CLIENT_ID=votre_instagram_client_id

# Traitement Paiement
STRIPE_SECRET_KEY=votre_cle_secrete_stripe
STRIPE_WEBHOOK_SECRET=votre_stripe_webhook_secret
PAYPAL_CLIENT_ID=votre_paypal_client_id
PAYPAL_CLIENT_SECRET=votre_paypal_client_secret

# Infrastructure
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://utilisateur:motdepasse@localhost/db
```

## Tests & Assurance Qualité

### Tests Sécurité
- **Tests Pénétration**: Évaluations sécurité tierces régulières
- **Scan Vulnérabilités**: Scans sécurité automatisés quotidiens
- **Analyse Sécurité Code**: Analyse code statique et dynamique
- **Audit Conformité**: Vérification conformité régulière

### Couverture Tests
- **Tests Unitaires**: 95%+ couverture code pour tous modules sécurité
- **Tests Intégration**: Tests workflow sécurité bout-en-bout
- **Tests Performance**: Tests charge et stress services sécurité
- **Tests Conformité**: Vérification automatisée exigences conformité

## Support & Documentation

### Ressources Développeur
- **Documentation API**: Référence API sécurité complète
- **Guide Configuration**: Instructions configuration détaillées
- **Meilleures Pratiques**: Directives implémentation sécurité
- **Dépannage**: Problèmes courants et solutions

### Canaux Support
- **Support Technique**: mlaiel@live.de
- **Problèmes Sécurité**: security@ia-influencer-agent.com
- **Documentation**: docs.ia-influencer-agent.com/security

## Feuille de Route & Améliorations Futures

### Fonctionnalités Prévues
- **Architecture Zero-Knowledge**: Protection confidentialité renforcée
- **Vérification Blockchain**: Vérification piste audit immuable
- **Chiffrement Résistant Quantique**: Algorithmes cryptographiques futurs
- **Sécurité Alimentée IA**: Fonctionnalités sécurité machine learning avancées

### Historique Versions
- **v2.0.0**: Version actuelle avec protection contenu et sécurité revenus
- **v1.5.0**: Améliorations sécurité intégration plateforme
- **v1.0.0**: Framework authentification et autorisation principal

---

**© 2025 Fahed Mlaiel. Tous droits réservés.**
**Contact**: mlaiel@live.de | **Sécurité**: security@ia-influencer-agent.com

---

## Intégration de la Logique Métier

Le module de sécurité s'intègre parfaitement avec la logique métier centrale :

**Parcours Créateur**: Utilisateur (musicien/blogueur/photographe/influenceur/comédien) → Upload multi-format → Protection IA des droits → SEO pro → Matching collaboration → Distribution multi-plateformes

**Points de Contact Sécurité**:
1. **Authentification** - Accès sécurisé aux comptes créateurs
2. **Upload de Contenu** - Scanning malware et validation
3. **Traitement IA** - Contenu chiffré pendant les workflows IA
4. **Intégration Plateforme** - Connexions API sécurisées vers Spotify, YouTube, Instagram, TikTok
5. **Opérations Revenus** - Protection des données financières et détection de fraude
6. **Collaboration** - Partage sécurisé et distribution des revenus

## Composants du Module

### 1. Authentification (`authentication.py`)
- **JWT & OAuth2** - Flux d'authentification entreprise
- **Authentification Multi-Facteurs** - Vérification TOTP, SMS, email
- **Intégration Social Login** - Spotify, Google, Instagram, YouTube
- **Authentification Spécifique Créateurs** - Contrôles d'accès par niveau

### 2. Autorisation (`authorization.py`)
- **Contrôle d'Accès Basé sur les Rôles (RBAC)** - Permissions granulaires
- **Permissions par Type de Créateur** - Musicien, blogueur, photographe, influenceur, comédien
- **Gestion des Niveaux d'Abonnement** - Gratuit, Basic, Professionnel, Entreprise
- **Contrôle d'Accès Plateforme** - Permissions d'intégration Spotify, YouTube, Instagram, TikTok

### 3. Chiffrement (`encryption.py`)
- **Chiffrement AES-256-GCM** - Chiffrement de fichiers et données
- **Système de Gestion de Clés** - Intégration HSM/Vault
- **Chiffrement Spécifique au Contenu** - Protection audio, vidéo, image, texte
- **Algorithmes Résistants Quantiques** - Cryptographie future-proof

### 4. Validation de Contenu (`content_validation.py`)
- **Scanning Multi-Format** - Validation audio, vidéo, image, texte
- **Détection de Malware** - ClamAV, YARA, modèles ML personnalisés
- **Conformité Copyright** - DMCA, empreintage, détection usage équitable
- **Modération de Contenu** - Application de politiques alimentée par IA

### 5. Limitation de Débit (`rate_limiting.py`)
- **Limitation de Débit API** - Throttling spécifique par endpoint
- **Limites de Traitement de Contenu** - Quotas d'upload et de traitement
- **Limites d'Intégration Plateforme** - Respect des limites d'API externes
- **Limitation Adaptive** - Ajustement dynamique basé ML

### 6. Journalisation d'Audit (`audit_logging.py`)
- **Suivi d'Événements Complet** - Authentification, contenu, opérations revenus
- **Journalisation Conformité** - Pistes d'audit GDPR, CCPA, SOX
- **Surveillance d'Événements Sécurité** - Détection de menaces et réponse incident
- **Suivi d'Activité Créateur** - Audit des opérations métier

### 7. Conformité (`compliance.py`)
- **Conformité GDPR** - Exigences de protection des données UE
- **Conformité CCPA** - Réglementations de confidentialité Californie
- **Conformité Copyright** - DMCA, protection de contenu
- **Conformité Financière** - PCI-DSS, AML, réglementations fiscales

### 8. Détection de Menaces (`threat_detection.py`)
- **Détection d'Anomalies Alimentée par IA** - Analyse comportementale
- **Protection Malware** - Scanning en temps réel
- **Détection de Fraude** - Prévention de fraude revenus et paiements
- **Réponse aux Incidents** - Réponse automatisée aux menaces

### 9. Sécurité API (`api_security.py`)
- **Protection API Complète** - En-têtes de sécurité, validation d'entrée
- **Configuration CORS** - Partage de ressources cross-origin
- **Sécurité Gateway API** - WAF, protection DDoS
- **Protection Endpoint** - Niveaux de sécurité et surveillance

## Utilisation de la Configuration

### Configuration de Base

```python
from backend.config.security import (
    get_authentication_config,
    get_authorization_config,
    get_encryption_config
)

# Obtenir les paramètres d'authentification
auth_config = get_authentication_config()

# Obtenir les permissions créateur
creator_permissions = get_creator_permissions(
    creator_type=CreatorType.MUSICIAN,
    tier=SubscriptionTier.PROFESSIONAL
)

# Obtenir les paramètres de chiffrement pour le contenu
encryption_settings = get_content_encryption_config(
    content_type="audio",
    tier="professional"
)
```

### Configuration Spécifique Créateur

```python
# Configurer l'authentification pour les créateurs de contenu
auth_config.creator_verification_required = True
auth_config.mfa.required_for_creators = True

# Configurer les permissions spécifiques plateforme
platform_access = get_platform_access_control()
spotify_access = platform_access.check_access("spotify", "professional")
```

### Application des Politiques de Sécurité

```python
# Valider les uploads de contenu
validation_config = get_content_validation_config()
audio_rules = validation_config.audio
video_rules = validation_config.video

# Appliquer la limitation de débit
rate_limits = get_tier_rate_limits("professional")
upload_limits = get_content_type_limits("audio")
```

## Points d'Intégration

### 1. Pipeline d'Upload de Contenu
```python
# Vérifications de sécurité lors de l'upload de contenu
- Vérification d'authentification
- Validation et scanning de contenu
- Détection de malware
- Vérification de conformité copyright
- Chiffrement avant stockage
```

### 2. Sécurité d'Intégration Plateforme
```python
# Connexions plateformes sécurisées
- Gestion des tokens OAuth2
- Limitation de débit API
- Chiffrement requête/réponse
- Journalisation d'audit
```

### 3. Sécurité des Opérations Revenus
```python
# Protection des données financières
- Conformité PCI-DSS
- Détection de fraude
- Données financières chiffrées
- Pistes d'audit
```

## Fonctionnalités de Sécurité

### Protection Avancée
- **Architecture Zero Trust** - Ne jamais faire confiance, toujours vérifier
- **Défense en Profondeur** - Multiples couches de sécurité
- **Chiffrement Partout** - Données au repos et en transit
- **Surveillance Temps Réel** - Détection de menaces 24/7

### Prêt pour la Conformité
- **Conforme GDPR** - Protection des données UE
- **Conforme CCPA** - Confidentialité Californie
- **Prêt PCI-DSS** - Sécurité des paiements
- **Conforme SOX** - Contrôles financiers

### Sécurité Axée Créateur
- **Protection de Contenu** - Protection copyright et PI
- **Sécurité Plateforme** - Distribution multi-plateforme sécurisée
- **Sécurité Revenus** - Prévention de fraude financière
- **Sécurité Collaboration** - Partage sécurisé et partenariats

## Configuration d'Environnement

### Paramètres de Production
```python
# Configuration production haute sécurité
encryption_config.compliance.fips_140_2_level = 2
threat_detection_config.real_time_detection = True
audit_logging_config.tamper_detection = True
```

### Paramètres de Développement
```python
# Paramètres conviviaux développement (jamais utiliser en production)
api_security_config.debug_mode = False  # Toujours False
encryption_config.test_key_generation = False
```

## Surveillance et Alertes

### Tableaux de Bord Sécurité
- Statut de détection de menaces en temps réel
- Taux de succès/échec d'authentification
- Métriques de sécurité d'upload de contenu
- Statut de sécurité d'intégration plateforme

### Alertes Automatisées
- Notifications d'incidents de sécurité
- Alertes de violation de conformité
- Avertissements de détection de menaces
- Dépassements de seuils de performance

## Support et Maintenance

### Mises à Jour Régulières
- Gestion des patches de sécurité
- Mises à jour des signatures de menaces
- Mises à jour des exigences de conformité
- Optimisations de performance

### Révisions de Sécurité
- Évaluations de sécurité trimestrielles
- Tests de pénétration annuels
- Audits de conformité
- Évaluations de vulnérabilités

## Informations de Contact

**Propriétaire du Projet**: Fahed Mlaiel  
**Email**: mlaiel@live.de  
**Contact Sécurité**: Pour les problèmes de sécurité ou demandes de licence

**Avis Légal**: Ce logiciel est propriétaire et confidentiel. L'utilisation non autorisée est interdite et sera poursuivie dans toute la mesure permise par la loi.

---

*Module de Configuration de Sécurité - Partie de la Plateforme IA Influencer Agent*  
*Copyright © 2025 Fahed Mlaiel. Tous droits réservés.*
