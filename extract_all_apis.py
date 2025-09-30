#!/usr/bin/env python3
"""
🕵️ EXTRACTEUR COMPLET DES APIs
==============================

Identification de TOUTES les APIs configurées dans .env
Aucune API ne sera oubliée cette fois !
"""

import os
import re
from typing import Dict, List, Set
from dotenv import load_dotenv

load_dotenv()

def extract_all_apis_from_env() -> Dict[str, List[str]]:
    """Extraire TOUTES les APIs du fichier .env"""
    
    # Lire le fichier .env directement
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Patterns pour identifier les APIs
    api_patterns = [
        r'(\w+)_API_KEY=(.+)',
        r'(\w+)_TOKEN=(.+)',
        r'(\w+)_SECRET=(.+)',
        r'(\w+)_CLIENT_ID=(.+)',
        r'(\w+)_CLIENT_SECRET=(.+)',
        r'(\w+)_ACCESS_TOKEN=(.+)',
        r'(\w+)_BEARER_TOKEN=(.+)',
        r'(\w+)_APP_ID=(.+)',
        r'(\w+)_APP_SECRET=(.+)',
        r'(\w+)_PUBLIC_KEY=(.+)',
        r'(\w+)_PRIVATE_KEY=(.+)',
        r'(\w+)_APPLICATION_ID=(.+)',
        r'(\w+)_WEBHOOK_SECRET=(.+)',
        r'(\w+)_SIGNING_SECRET=(.+)',
        r'(\w+)_KEY=(.+)',
        r'(\w+)_AUTH_TOKEN=(.+)',
        r'(\w+)_ACCOUNT_SID=(.+)',
        r'(\w+)_PHONE_NUMBER=(.+)',
        r'(\w+)_ANON_KEY=(.+)',
        r'(\w+)_SERVICE_KEY=(.+)',
        r'(\w+)_MEASUREMENT_ID=(.+)',
        r'(\w+)_DSN=(.+)',
        r'(\w+)_ENVIRONMENT=(.+)',
        r'(\w+)_URL=(.+)',
        r'(\w+)_DOMAIN=(.+)',
        r'(\w+)_SCOPE=(.+)',
        r'(\w+)_TENANT_ID=(.+)',
        r'(\w+)_SECRET_ID=(.+)',
    ]
    
    apis_found = {}
    lines = env_content.split('\n')
    
    print("🔍 EXTRACTION DE TOUTES LES APIs DU FICHIER .ENV")
    print("=" * 60)
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        for pattern in api_patterns:
            match = re.match(pattern, line)
            if match:
                service_name = match.group(1).lower()
                full_key = match.group(0).split('=')[0]
                value = match.group(2) if len(match.groups()) > 1 else ""
                
                if service_name not in apis_found:
                    apis_found[service_name] = []
                
                apis_found[service_name].append({
                    'key_name': full_key,
                    'value_preview': value[:20] + "..." if len(value) > 20 else value,
                    'line_number': line_num,
                    'has_value': len(value.strip()) > 0 and value != "VOTRE_TOKEN_ACCES"
                })
                break
    
    return apis_found

def categorize_apis(apis_found: Dict) -> Dict[str, List]:
    """Catégoriser les APIs par type de service"""
    
    categories = {
        'AI/ML': ['openai', 'huggingface', 'google_gemini', 'cohere', 'stability', 'elevenlabs', 'runwayml', 'textrazor'],
        'Social Media': ['twitter', 'instagram', 'facebook', 'youtube', 'tiktok', 'linkedin', 'pinterest', 'snapchat'],
        'Communication': ['discord', 'telegram', 'whatsapp', 'twilio', 'resend', 'sendgrid', 'mailchimp'],
        'Cloud/Database': ['supabase', 'firebase', 'mongodb', 'redis', 'azure', 'aws', 'gcp', 'algolia', 'pinecone'],
        'Media/Content': ['unsplash', 'freepik', 'freesound', 'pixabay', 'giphy', 'pexels'],
        'Analytics': ['google_analytics', 'mixpanel', 'amplitude', 'hotjar', 'sentry'],
        'Payment': ['stripe', 'paypal', 'square', 'braintree'],
        'Utility': ['tinyurl', 'bitly', 'ipgeolocation', 'pagespeed', 'typeform', 'reddit'],
        'Other': []
    }
    
    categorized = {cat: [] for cat in categories.keys()}
    uncategorized = []
    
    for service_name in apis_found.keys():
        found_category = False
        for category, services in categories.items():
            if any(service in service_name for service in services):
                categorized[category].append(service_name)
                found_category = True
                break
        
        if not found_category:
            uncategorized.append(service_name)
    
    if uncategorized:
        categorized['Other'] = uncategorized
    
    return categorized

def generate_complete_api_list():
    """Générer la liste complète de toutes vos APIs"""
    
    apis_found = extract_all_apis_from_env()
    categorized = categorize_apis(apis_found)
    
    total_services = len(apis_found)
    total_keys = sum(len(keys) for keys in apis_found.values())
    configured_services = sum(1 for service_keys in apis_found.values() 
                            if any(key['has_value'] for key in service_keys))
    
    print(f"\n📊 STATISTIQUES DÉCOUVERTE:")
    print(f"   🔢 Total services détectés: {total_services}")
    print(f"   🔑 Total clés API: {total_keys}")
    print(f"   ✅ Services configurés: {configured_services}")
    print(f"   ⚠️  Services non configurés: {total_services - configured_services}")
    
    print(f"\n📋 INVENTAIRE COMPLET PAR CATÉGORIE:")
    print("=" * 60)
    
    all_services = []
    
    for category, services in categorized.items():
        if services:
            print(f"\n🏷️  {category.upper()} ({len(services)} services):")
            for service in services:
                service_keys = apis_found[service]
                configured = any(key['has_value'] for key in service_keys)
                status = "✅" if configured else "⚠️"
                
                print(f"   {status} {service.upper()}")
                for key_info in service_keys:
                    config_status = "✓" if key_info['has_value'] else "✗"
                    print(f"      {config_status} {key_info['key_name']}")
                
                all_services.append({
                    'name': service,
                    'category': category,
                    'configured': configured,
                    'keys': service_keys
                })
    
    # APIs manquantes détectées
    missing_apis = [
        'tiktok', 'linkedin', 'pinterest', 'snapchat', 'telegram', 'whatsapp',
        'sendgrid', 'mailchimp', 'firebase', 'mongodb', 'aws', 'gcp',
        'stripe', 'paypal', 'mixpanel', 'amplitude', 'hotjar', 'bitly',
        'giphy', 'pexels', 'pixabay'
    ]
    
    found_service_names = set(apis_found.keys())
    actually_missing = [api for api in missing_apis 
                       if not any(api in found_name for found_name in found_service_names)]
    
    if actually_missing:
        print(f"\n❌ APIS POTENTIELLEMENT MANQUANTES ({len(actually_missing)}):")
        for api in actually_missing:
            print(f"   ⭕ {api.upper()}")
    
    print(f"\n🎯 RECOMMANDATION:")
    print(f"   Nous avons trouvé {total_services} services avec {total_keys} clés API")
    print(f"   Il faut tester TOUTES ces APIs, pas seulement 26!")
    
    return all_services, apis_found

def main():
    """Exécution principale"""
    print("🚀 DÉCOUVERTE COMPLÈTE DE TOUTES VOS APIs")
    print("Nous allons identifier CHAQUE API dans votre .env")
    print()
    
    all_services, apis_found = generate_complete_api_list()
    
    print(f"\n💡 CONCLUSION:")
    print(f"   Vous avez {len(apis_found)} services API différents")
    print(f"   L'audit précédent n'en a testé que 26")
    print(f"   Il manque {len(apis_found) - 26} services à tester!")
    
    # Sauvegarder la liste complète
    import json
    with open("complete_api_inventory.json", "w") as f:
        json.dump({
            'total_services': len(apis_found),
            'services': all_services,
            'raw_apis': apis_found
        }, f, indent=2)
    
    print(f"\n💾 Inventaire complet sauvegardé: complete_api_inventory.json")

if __name__ == "__main__":
    main()