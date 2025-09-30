#!/usr/bin/env python3
"""
Affiliate Service Demo - Demonstration of Module d'Affiliation functionality
===========================================================================

This script demonstrates the key features of the affiliate service:
- Programme partenaires (Partner programs)
- Tracking commissions 
- Paiements automatiques (Automatic payments)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.affiliate import (
    AffiliateService, 
    ProgramType, 
    PayoutMethod,
    TrackingEventType,
    AffiliateStatus
)


async def demonstrate_affiliate_service():
    """Démonstration complète du service d'affiliation"""
    
    print("=" * 60)
    print("🤝 DÉMONSTRATION MODULE AFFILIATION - AINFLUE PLATFORM")
    print("=" * 60)
    
    # Initialize the service
    print("\n1️⃣ INITIALISATION DU SERVICE")
    print("-" * 30)
    
    service = AffiliateService()
    success = await service.initialize()
    
    if success:
        print("✅ Service d'affiliation initialisé avec succès")
        print(f"📊 Programmes par défaut créés: {len(service.partner_programs)}")
    else:
        print("❌ Échec de l'initialisation")
        return False
    
    # Display default programs
    print("\n📋 Programmes partenaires disponibles:")
    programs = await service.get_partner_programs()
    for program in programs:
        print(f"  • {program.name}: {program.commission_rate}% commission")
    
    # Register affiliates to different programs
    print("\n2️⃣ INSCRIPTION D'AFFILIÉS")
    print("-" * 30)
    
    affiliates_data = [
        {
            "user_id": "user_001",
            "name": "Sophie Martin",
            "email": "sophie.martin@example.com",
            "program_type": ProgramType.BASIC_AFFILIATE
        },
        {
            "user_id": "user_002", 
            "name": "Thomas Dubois",
            "email": "thomas.dubois@example.com",
            "program_type": ProgramType.PREMIUM_PARTNER
        },
        {
            "user_id": "user_003",
            "name": "Emma Wilson",
            "email": "emma.wilson@example.com", 
            "program_type": ProgramType.BRAND_AMBASSADOR
        }
    ]
    
    registered_affiliates = []
    
    for affiliate_data in affiliates_data:
        # Find program by type
        program = next((p for p in programs if p.program_type == affiliate_data["program_type"]), None)
        
        if program:
            affiliate = await service.register_affiliate_to_program(
                user_id=affiliate_data["user_id"],
                name=affiliate_data["name"],
                email=affiliate_data["email"],
                program_id=program.program_id
            )
            
            if affiliate:
                registered_affiliates.append(affiliate)
                print(f"✅ Affilié inscrit: {affiliate.name} -> {program.name}")
                print(f"   Code de parrainage: {affiliate.referral_code}")
                
                # Approve the affiliate
                await service.approve_affiliate(affiliate.affiliate_id)
                print(f"   Statut: Approuvé")
            else:
                print(f"❌ Échec inscription: {affiliate_data['name']}")
    
    # Simulate commission tracking
    print("\n3️⃣ TRACKING DES COMMISSIONS")
    print("-" * 30)
    
    transactions = [
        {"amount": Decimal("150.00"), "type": "sale", "description": "Vente produit digital"},
        {"amount": Decimal("89.99"), "type": "subscription", "description": "Abonnement mensuel"},
        {"amount": Decimal("299.50"), "type": "sale", "description": "Pack premium"},
        {"amount": Decimal("45.00"), "type": "referral", "description": "Parrainage nouveau client"}
    ]
    
    total_tracked = Decimal("0")
    
    for i, affiliate in enumerate(registered_affiliates):
        print(f"\n📈 Tracking pour {affiliate.name}:")
        
        for j, transaction in enumerate(transactions):
            commission = await service.track_commission_event(
                affiliate_id=affiliate.affiliate_id,
                transaction_id=f"tx_{i}_{j}_{int(datetime.now().timestamp())}",
                amount=transaction["amount"],
                reference_type=transaction["type"],
                metadata={"description": transaction["description"]}
            )
            
            if commission:
                total_tracked += commission.commission_amount
                print(f"  ✅ {transaction['description']}: {transaction['amount']}€ → {commission.commission_amount}€ commission")
                
                # Approve commission automatically for demo
                await service.approve_commission(commission.commission_id)
    
    print(f"\n💰 Total commissions trackées: {total_tracked}€")
    
    # Setup automatic payments
    print("\n4️⃣ CONFIGURATION PAIEMENTS AUTOMATIQUES")
    print("-" * 30)
    
    payment_methods = [PayoutMethod.PAYPAL, PayoutMethod.STRIPE, PayoutMethod.BANK_TRANSFER]
    
    for i, affiliate in enumerate(registered_affiliates):
        payment_method = payment_methods[i % len(payment_methods)]
        
        schedule = await service.setup_automatic_payments(
            affiliate_id=affiliate.affiliate_id,
            payment_method=payment_method,
            frequency="monthly",
            minimum_amount=Decimal("25.00")
        )
        
        if schedule:
            print(f"✅ Paiements automatiques configurés pour {affiliate.name}")
            print(f"   Méthode: {payment_method.value}")
            print(f"   Fréquence: {schedule.frequency}")
            print(f"   Prochain paiement: {schedule.next_payment_date.strftime('%d/%m/%Y')}")
    
    # Process automatic payments
    print("\n5️⃣ TRAITEMENT PAIEMENTS AUTOMATIQUES")
    print("-" * 30)
    
    # Force payment dates to now for demo
    for schedule in service.payment_schedules.values():
        schedule.next_payment_date = datetime.utcnow() - timedelta(minutes=1)
    
    payment_results = await service.process_automatic_payments()
    print(f"✅ Paiements traités: {payment_results['processed']}")
    print(f"❌ Paiements échoués: {payment_results['failed']}")
    print(f"📊 Total programmés: {payment_results['total_schedules']}")
    
    # Show analytics and dashboard
    print("\n6️⃣ ANALYTICS ET TABLEAU DE BORD")
    print("-" * 30)
    
    for affiliate in registered_affiliates:
        print(f"\n📊 Dashboard - {affiliate.name}:")
        
        dashboard = await service.get_affiliate_dashboard(affiliate.affiliate_id)
        
        if dashboard:
            analytics = dashboard.get("analytics", {})
            print(f"  💰 Commissions totales: {analytics.get('total_commissions', 0)}€")
            print(f"  📈 Transactions: {analytics.get('total_transactions', 0)}")
            print(f"  📊 Commission moyenne: {analytics.get('average_commission', 0):.2f}€")
            print(f"  🔄 Commissions récentes: {dashboard.get('total_recent_commissions', 0)}")
    
    # Show program statistics
    print("\n7️⃣ STATISTIQUES DES PROGRAMMES")
    print("-" * 30)
    
    for program in programs:
        stats = await service.get_program_stats(program.program_id)
        if stats:
            print(f"\n📋 {stats['program_name']}:")
            print(f"  👥 Affiliés: {stats['affiliate_count']}")
            print(f"  💰 Total commissions: {stats['total_commissions']}€")
            print(f"  📊 Taux commission: {stats['commission_rate']}%")
    
    # Show payout batches
    print("\n8️⃣ HISTORIQUE DES PAIEMENTS")
    print("-" * 30)
    
    payout_batches = await service.get_payout_batches()
    print(f"📦 Lots de paiement créés: {len(payout_batches)}")
    
    for batch in payout_batches:
        print(f"  • Lot {batch.batch_id[:8]}...")
        print(f"    Montant: {batch.total_amount}€")
        print(f"    Commissions: {batch.commission_count}")
        print(f"    Méthode: {batch.payout_method.value}")
        print(f"    Statut: {batch.status}")
    
    print("\n" + "=" * 60)
    print("✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
    print("🤝 Module d'Affiliation - Ainflue Platform")
    print("=" * 60)
    
    return True


async def main():
    """Point d'entrée principal"""
    try:
        success = await demonstrate_affiliate_service()
        
        if success:
            print("\n🎉 Toutes les fonctionnalités ont été démontrées avec succès!")
        else:
            print("\n❌ Erreur pendant la démonstration")
            
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Démarrage de la démonstration...")
    asyncio.run(main())