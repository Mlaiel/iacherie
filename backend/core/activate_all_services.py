"""
🚀 ACTIVATION COMPLÈTE DE TOUS LES SERVICES
============================================

Ce script active TOUS les services dormants (lazy loading)
pour que le backend soit 100% opérationnel.
"""

import asyncio
from typing import Dict, Any

async def activate_all_services(gateway) -> Dict[str, Any]:
    """
    Active tous les services dormants en appelant ensure_initialized()
    
    Returns:
        Statistiques d'activation
    """
    stats = {
        'total': len(gateway.services),
        'activated': 0,
        'already_active': 0,
        'failed': [],
        'services_with_ensure': []
    }
    
    print(f"\n🚀 ACTIVATION DE {stats['total']} SERVICES...")
    print("━" * 50)
    
    for name, service in gateway.services.items():
        # Vérifier si le service a une méthode ensure_initialized
        if hasattr(service, 'ensure_initialized'):
            stats['services_with_ensure'].append(name)

            try:
                await service.ensure_initialized()

                stats['activated'] += 1
                print(f"✅ {name}: activé")

            except Exception as e:
                stats['failed'].append((name, str(e)))

                print(f"❌ {name}: erreur - {str(e)[:80]}")
        else:
            stats['already_active'] += 1
    
    return stats


async def main():
    """Point d'entrée principal"""
    # Importer le gateway
    from backend.core.microservices_gateway import MicroservicesGateway
    
    # Initialiser le gateway
    print("\n🔄 Initialisation du gateway...")
    gateway = MicroservicesGateway()
    await gateway.initialize()
    
    print(f"\n✅ Gateway initialisé : {len(gateway.services)} services chargés")
    
    # Activer tous les services
    stats = await activate_all_services(gateway)
    
    # Afficher le rapport
    print("\n" + "━" * 50)
    print("\n📊 RAPPORT D'ACTIVATION:")
    print(f"   Total services: {stats['total']}")
    print(f"   ✅ Déjà actifs: {stats['already_active']}")
    print(f"   🔄 Services activés: {stats['activated']}")
    print(f"   ❌ Échecs: {len(stats['failed'])}")
    
    if stats['failed']:
        print(f"\n❌ ÉCHECS D'ACTIVATION ({len(stats['failed'])}):")
        for name, error in stats['failed']:
            print(f"   • {name}: {error[:100]}")
    
    # Verdict final
    print("\n" + "━" * 50)
    taux_activation = (stats['already_active'] + stats['activated']) / stats['total'] * 100
    print(f"\n🎯 TAUX D'ACTIVATION FINAL: {taux_activation:.1f}%")
    
    if taux_activation == 100.0:
        print("🎉 TOUS LES SERVICES SONT ACTIFS !")
    else:
        print(f"⚠️  {stats['total'] - stats['already_active'] - stats['activated']} services restent dormants")


if __name__ == "__main__":
    asyncio.run(main())
