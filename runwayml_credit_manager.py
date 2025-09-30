#!/usr/bin/env python3
"""
GESTIONNAIRE DE CRÉDITS RUNWAYML - MODE ÉCONOMIE
================================================

🚨 ALERTE: 320 crédits consommés sur 1000 !
💰 Crédits restants: ~680
⚠️  Mode économie activé

COÛTS PAR MODÈLE (estimés):
- Veo-3: ~40 crédits/seconde (8s = 320 crédits!)
- Gen-4 Turbo: ~10-20 crédits/génération
- Gen-3 Alpha Turbo: ~5-10 crédits/génération
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class RunwayMLCreditManager:
    def __init__(self):
        self.api_key = os.getenv('RUNWAYML_API_KEY')
        self.base_url = 'https://api.dev.runwayml.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-Runway-Version': '2024-09-13',
            'Content-Type': 'application/json'
        }
        self.credits_limit = 680  # Crédits restants estimés
        self.min_credits_reserve = 200  # Réserve minimum
    
    def estimate_cost(self, model, duration=5):
        """Estimer le coût d'une génération"""
        cost_table = {
            'veo3': 40 * duration,  # 40 crédits/seconde
            'gen4_turbo': 15,       # Estimation
            'gen3a_turbo': 8,       # Estimation
            'gen3a': 5              # Estimation
        }
        return cost_table.get(model, 10)
    
    def safe_generate(self, prompt, model='gen4_turbo', duration=5):
        """Génération sécurisée avec vérification des crédits"""
        estimated_cost = self.estimate_cost(model, duration)
        
        print(f"🧮 Estimation coût: {estimated_cost} crédits")
        print(f"💰 Crédits disponibles: ~{self.credits_limit}")
        print(f"🛡️  Réserve minimum: {self.min_credits_reserve}")
        
        if estimated_cost > (self.credits_limit - self.min_credits_reserve):
            print("🚫 GÉNÉRATION REFUSÉE - Pas assez de crédits!")
            print(f"   Coût estimé: {estimated_cost}")
            print(f"   Budget disponible: {self.credits_limit - self.min_credits_reserve}")
            return None
        
        # Demander confirmation pour Veo-3
        if model == 'veo3':
            print("⚠️  VEO-3 EST TRÈS CHER! Voulez-vous continuer?")
            print(f"   Coût: {estimated_cost} crédits pour {duration}s")
            # En mode automatique, on refuse Veo-3
            print("🚫 VEO-3 BLOQUÉ en mode économie!")
            return None
        
        # Génération avec modèle moins cher
        try:
            payload = {
                'model': model,
                'promptText': prompt,
                'duration': duration,
                'ratio': '1280:720'
            }
            
            print(f"🎬 Génération avec {model}...")
            response = requests.post(
                f'{self.base_url}/text_to_video',
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Tâche créée: {result.get('id')}")
                # Déduire le coût estimé
                self.credits_limit -= estimated_cost
                print(f"💰 Crédits restants estimés: {self.credits_limit}")
                return result
            else:
                print(f"❌ Erreur: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return None
    
    def show_budget_status(self):
        """Afficher le statut du budget"""
        print("💰 STATUT BUDGET RUNWAYML")
        print("=" * 40)
        print(f"Crédits totaux: 1000")
        print(f"Crédits consommés: ~320")
        print(f"Crédits restants: ~{self.credits_limit}")
        print(f"Réserve minimum: {self.min_credits_reserve}")
        print(f"Budget utilisable: {self.credits_limit - self.min_credits_reserve}")
        
        print("\n🎯 RECOMMANDATIONS:")
        print("- Utiliser Gen-4 Turbo (15 crédits) ou Gen-3 Alpha (8 crédits)")
        print("- ÉVITER Veo-3 (320 crédits pour 8s!)")
        print("- Tester avec durées courtes (5s max)")
        print("- Garder 200 crédits en réserve")

def main():
    """Mode économie RunwayML"""
    print("🚨 RUNWAYML - MODE ÉCONOMIE ACTIVÉ")
    print("=" * 50)
    
    manager = RunwayMLCreditManager()
    manager.show_budget_status()
    
    print("\n🎬 Test génération économique...")
    # Test avec Gen-4 Turbo (plus économique)
    result = manager.safe_generate(
        prompt="A calm ocean at sunset, short and beautiful",
        model="gen4_turbo", 
        duration=5
    )
    
    if result:
        print(f"\n✅ Génération lancée avec succès!")
        print(f"   Task ID: {result.get('id')}")
    else:
        print(f"\n❌ Génération refusée pour économiser les crédits")

if __name__ == "__main__":
    main()