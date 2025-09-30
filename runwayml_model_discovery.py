#!/usr/bin/env python3
"""
Découverte des modèles RunwayML disponibles
Test exhaustif de tous les noms de modèles possibles
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class RunwayMLModelDiscovery:
    def __init__(self):
        self.api_key = os.getenv('RUNWAYML_API_KEY')
        self.base_url = 'https://api.dev.runwayml.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-Runway-Version': '2024-09-13',
            'Content-Type': 'application/json'
        }
        
        # Liste des modèles possibles basée sur le dashboard
        self.models_to_test = [
            # Gen-3 variants
            'gen3a_turbo',
            'gen3-alpha-turbo', 
            'gen3_alpha_turbo',
            'gen3-alpha',
            'gen3_alpha',
            'gen3a',
            'gen3',
            'gen-3-alpha-turbo',
            'gen-3-alpha',
            'gen-3',
            
            # Gen-4 variants  
            'gen4_turbo',
            'gen4-turbo',
            'gen4',
            'gen-4-turbo',
            'gen-4',
            'gen4_image',
            'gen4-image',
            'gen4_image_turbo',
            'gen4-image-turbo',
            'gen4_aleph',
            'gen4-aleph',
            
            # Autres modèles du dashboard
            'upscale',
            'act-two',
            'act_two',
            'veo-3',
            'veo_3',
            'veo3',
            
            # Noms génériques
            'runway',
            'runway-ml',
            'runwayml',
            'default'
        ]
    
    def test_model(self, model_name):
        """Test un modèle spécifique"""
        try:
            payload = {
                'model': model_name,
                'promptText': 'test generation',
                'ratio': '1280:720'
            }
            
            response = requests.post(
                f'{self.base_url}/text_to_video',
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'SUCCESS',
                    'model': model_name,
                    'task_id': result.get('id'),
                    'response': result
                }
            elif 'Model variant' in response.text and 'not available' in response.text:
                return {
                    'status': 'MODEL_NOT_AVAILABLE',
                    'model': model_name,
                    'error': response.text
                }
            else:
                return {
                    'status': 'OTHER_ERROR',
                    'model': model_name,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            return {
                'status': 'EXCEPTION',
                'model': model_name,
                'error': str(e)
            }
    
    def discover_models(self):
        """Découverte de tous les modèles"""
        print("🔍 Découverte des modèles RunwayML disponibles")
        print("=" * 60)
        
        results = {
            'working_models': [],
            'unavailable_models': [],
            'error_models': []
        }
        
        for i, model in enumerate(self.models_to_test, 1):
            print(f"\n{i:2d}/{len(self.models_to_test)} Test: {model:<20}", end=" ... ")
            
            result = self.test_model(model)
            
            if result['status'] == 'SUCCESS':
                print("✅ FONCTIONNE!")
                results['working_models'].append(result)
                print(f"    Task ID: {result['task_id']}")
            elif result['status'] == 'MODEL_NOT_AVAILABLE':
                print("❌ Non disponible")
                results['unavailable_models'].append(result)
            else:
                print(f"⚠️  Erreur ({result.get('status_code', 'N/A')})")
                results['error_models'].append(result)
        
        return results
    
    def print_summary(self, results):
        """Afficher le résumé"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE LA DÉCOUVERTE")
        print("=" * 60)
        
        if results['working_models']:
            print(f"\n✅ MODÈLES FONCTIONNELS ({len(results['working_models'])}):")
            for model in results['working_models']:
                print(f"   • {model['model']}")
        else:
            print("\n❌ AUCUN MODÈLE FONCTIONNEL TROUVÉ")
        
        print(f"\n❌ Modèles non disponibles: {len(results['unavailable_models'])}")
        print(f"⚠️  Erreurs autres: {len(results['error_models'])}")
        
        if results['error_models']:
            print("\n⚠️  ERREURS DÉTAILLÉES:")
            for error in results['error_models'][:3]:  # Max 3 erreurs
                print(f"   • {error['model']}: {error.get('status_code')} - {error.get('error', '')[:100]}")

def main():
    """Fonction principale"""
    discovery = RunwayMLModelDiscovery()
    
    if not discovery.api_key:
        print("❌ Clé API RunwayML non trouvée")
        return
    
    print(f"🔑 Clé API: ...{discovery.api_key[-8:]}")
    
    results = discovery.discover_models()
    discovery.print_summary(results)
    
    # Sauvegarder les résultats
    with open('/workspaces/IACherie/runwayml_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Résultats sauvegardés dans runwayml_discovery_results.json")

if __name__ == "__main__":
    main()