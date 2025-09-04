# Module d'Affiliation - API Documentation

## Vue d'ensemble

Le Module d'Affiliation (`backend/services/affiliate.py`) fournit une solution complète pour la gestion des programmes partenaires, le tracking des commissions et les paiements automatiques sur la plateforme Ainflue.

## Fonctionnalités Principales

### 🤝 Programme Partenaires (Partner Programs)
- Gestion de multiples types de programmes
- Configuration dynamique des taux de commission
- Gestion des exigences et avantages
- Statistiques et analytics des programmes

### 📈 Tracking Commissions
- Calcul et suivi des commissions en temps réel
- Support de multiples types de commissions
- Analytics et rapports complets
- Gestion des statuts de commission

### 💸 Paiements Automatiques (Automatic Payments)
- Planification configurable des paiements
- Multiples méthodes de paiement
- Traitement automatique par lot
- Historique et suivi des paiements

## Utilisation de l'API

### Initialisation du Service

```python
from backend.services.affiliate import AffiliateService

# Créer une instance du service
service = AffiliateService()

# Initialiser le service
await service.initialize()
```

### Gestion des Programmes Partenaires

```python
from backend.services.affiliate import ProgramType
from decimal import Decimal

# Créer un nouveau programme
program = await service.create_partner_program(
    program_type=ProgramType.PREMIUM_PARTNER,
    name="Programme Premium",
    description="Programme avancé pour partenaires expérimentés",
    commission_rate=Decimal("5.0"),
    minimum_payout=Decimal("100.00")
)

# Obtenir la liste des programmes
programs = await service.get_partner_programs()

# Obtenir les statistiques d'un programme
stats = await service.get_program_stats(program.program_id)
```

### Inscription et Gestion des Affiliés

```python
# Inscrire un affilié à un programme
affiliate = await service.register_affiliate_to_program(
    user_id="user_123",
    name="Sophie Martin",
    email="sophie.martin@example.com",
    program_id=program.program_id
)

# Approuver un affilié
await service.approve_affiliate(affiliate.affiliate_id)

# Obtenir un affilié par ID
affiliate = await service.get_affiliate(affiliate_id)

# Obtenir un affilié par code de parrainage
affiliate = await service.get_affiliate_by_referral_code("SOPHIE2155")

# Lister les affiliés avec filtres
affiliates = await service.list_affiliates(
    status=AffiliateStatus.ACTIVE,
    program_id=program.program_id
)
```

### Tracking des Commissions

```python
from decimal import Decimal

# Tracker un événement de commission
commission = await service.track_commission_event(
    affiliate_id=affiliate.affiliate_id,
    transaction_id="tx_12345",
    amount=Decimal("150.00"),
    reference_type="sale",
    metadata={"product_id": "prod_123"}
)

# Approuver une commission
await service.approve_commission(commission.commission_id)

# Obtenir les commissions d'un affilié
commissions = await service.get_affiliate_commissions(
    affiliate_id=affiliate.affiliate_id,
    status=CommissionStatus.APPROVED
)

# Obtenir les analytics des commissions
analytics = await service.get_commission_analytics(
    affiliate_id=affiliate.affiliate_id,
    period_days=30
)
```

### Paiements Automatiques

```python
from backend.services.affiliate import PayoutMethod

# Configurer les paiements automatiques
schedule = await service.setup_automatic_payments(
    affiliate_id=affiliate.affiliate_id,
    payment_method=PayoutMethod.PAYPAL,
    frequency="monthly",
    minimum_amount=Decimal("50.00")
)

# Traiter les paiements automatiques programmés
results = await service.process_automatic_payments()

# Mettre à jour le planning de paiement
await service.update_payment_schedule(
    affiliate_id=affiliate.affiliate_id,
    payment_method=PayoutMethod.STRIPE,
    frequency="bi-weekly"
)

# Obtenir l'historique des paiements
payout_batches = await service.get_payout_batches(affiliate_id)
```

### Dashboard et Analytics

```python
# Obtenir le tableau de bord complet d'un affilié
dashboard = await service.get_affiliate_dashboard(affiliate.affiliate_id)

# Le dashboard contient:
# - Informations de l'affilié
# - Analytics des commissions
# - Planning des paiements
# - Commissions récentes
```

## Types de Données

### Types de Programmes
- `BASIC_AFFILIATE`: Programme de base pour nouveaux affiliés
- `PREMIUM_PARTNER`: Programme avancé pour partenaires expérimentés
- `BRAND_AMBASSADOR`: Programme exclusif pour ambassadeurs
- `INFLUENCER_NETWORK`: Réseau d'influenceurs spécialisé
- `ENTERPRISE_PARTNER`: Partenariat entreprise

### Statuts des Affiliés
- `ACTIVE`: Affilié actif
- `INACTIVE`: Affilié inactif
- `SUSPENDED`: Affilié suspendu
- `PENDING_APPROVAL`: En attente d'approbation
- `BANNED`: Affilié banni

### Statuts des Commissions
- `PENDING`: Commission en attente
- `APPROVED`: Commission approuvée
- `PAID`: Commission payée
- `CANCELLED`: Commission annulée
- `DISPUTED`: Commission disputée
- `HOLD`: Commission en attente

### Méthodes de Paiement
- `PAYPAL`: Paiement via PayPal
- `STRIPE`: Paiement via Stripe
- `BANK_TRANSFER`: Virement bancaire
- `WISE`: Paiement via Wise
- `CRYPTOCURRENCY`: Cryptomonnaie

## Événements de Tracking
- `REGISTRATION`: Inscription d'un affilié
- `FIRST_PURCHASE`: Premier achat
- `SUBSCRIPTION`: Abonnement
- `REFERRAL_CLICK`: Clic sur lien de parrainage
- `COMMISSION_EARNED`: Commission gagnée
- `PAYOUT_PROCESSED`: Paiement traité

## Exemples d'Intégration

### Workflow Complet

```python
async def complete_affiliate_workflow():
    # 1. Initialisation
    service = AffiliateService()
    await service.initialize()
    
    # 2. Inscription d'un affilié
    affiliate = await service.register_affiliate_to_program(
        user_id="user_456",
        name="Jean Dupont",
        email="jean.dupont@example.com",
        program_id="basic_program_id"
    )
    
    # 3. Approbation
    await service.approve_affiliate(affiliate.affiliate_id)
    
    # 4. Configuration des paiements
    await service.setup_automatic_payments(
        affiliate_id=affiliate.affiliate_id,
        payment_method=PayoutMethod.PAYPAL,
        frequency="monthly"
    )
    
    # 5. Tracking d'une vente
    commission = await service.track_commission_event(
        affiliate_id=affiliate.affiliate_id,
        transaction_id="tx_789",
        amount=Decimal("200.00"),
        reference_type="sale"
    )
    
    # 6. Approbation de la commission
    await service.approve_commission(commission.commission_id)
    
    # 7. Traitement des paiements
    await service.process_automatic_payments()
    
    # 8. Consultation du dashboard
    dashboard = await service.get_affiliate_dashboard(affiliate.affiliate_id)
    
    return dashboard
```

## Sécurité et Conformité

- Tous les montants sont traités avec `Decimal` pour la précision financière
- Validation complète des entrées utilisateur
- Logging détaillé pour audit et compliance
- Gestion d'erreurs robuste
- Protection contre les fraudes

## Performance

- Opérations asynchrones pour optimiser les performances
- Cache intelligent pour les données fréquemment accédées
- Traitement par lot pour les paiements
- Indexation optimale des données

## Support et Maintenance

Pour toute question ou support technique concernant le Module d'Affiliation:
- **Auteur**: Fahed Mlaiel
- **Email**: mlaiel@live.de
- **Copyright**: (c) 2025 Fahed Mlaiel. Tous droits réservés.

---

*Ce module fait partie de la plateforme Ainflue et est protégé par les droits d'auteur. Utilisation non autorisée strictement interdite.*