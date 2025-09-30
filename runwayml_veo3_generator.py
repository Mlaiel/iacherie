#!/usr/bin/env python3
"""
RunwayML Veo-3 Integration complète
Génération vidéo en masse pour votre plateforme
"""

import requests
import json
import time
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class RunwayMLVeo3Generator:
    def __init__(self):
        self.api_key = os.getenv('RUNWAYML_API_KEY')
        self.base_url = 'https://api.dev.runwayml.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-Runway-Version': '2024-09-13',
            'Content-Type': 'application/json'
        }
        self.model = 'veo3'
        self.supported_ratios = ['1280:720', '720:1280', '1104:832', '832:1104', '960:960', '1584:672']
        
    def generate_video(self, prompt, ratio='1280:720', duration=8):
        """Générer une vidéo avec Veo-3"""
        try:
            if ratio not in self.supported_ratios:
                ratio = '1280:720'  # Default
                
            payload = {
                'model': self.model,
                'promptText': prompt,
                'ratio': ratio,
                'duration': duration  # Veo-3 nécessite duration=8
            }
            
            print(f"🎬 Génération: {prompt[:50]}...")
            response = requests.post(
                f'{self.base_url}/text_to_video',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('id')
                print(f"✅ Génération lancée - ID: {task_id}")
                return {
                    'success': True,
                    'task_id': task_id,
                    'prompt': prompt,
                    'status': 'INITIATED'
                }
            else:
                print(f"❌ Erreur génération: {response.status_code}")
                return {
                    'success': False,
                    'error': response.text,
                    'prompt': prompt
                }
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt
            }
    
    def check_status(self, task_id):
        """Vérifier le statut d'une génération"""
        try:
            response = requests.get(
                f'{self.base_url}/tasks/{task_id}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Status check failed: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def wait_for_completion(self, task_id, max_wait=600):
        """Attendre la completion d'une génération (max 10 minutes)"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_status(task_id)
            
            if 'error' in status:
                return status
                
            current_status = status.get('status', 'UNKNOWN')
            progress = status.get('progress', 0)
            
            print(f"📊 {task_id[:8]}... - {current_status} ({progress*100:.1f}%)")
            
            if current_status == 'SUCCEEDED':
                return {
                    'status': 'COMPLETED',
                    'video_url': status.get('artifacts', [{}])[0].get('url'),
                    'full_response': status
                }
            elif current_status == 'FAILED':
                return {
                    'status': 'FAILED',
                    'error': status.get('failure_reason', 'Unknown failure'),
                    'full_response': status
                }
            
            time.sleep(15)  # Attendre 15 secondes entre les vérifications
        
        return {'status': 'TIMEOUT', 'error': 'Generation took too long'}
    
    def bulk_generate(self, prompts, batch_size=3):
        """Génération en masse avec gestion de la concurrence"""
        print(f"🚀 Génération en masse de {len(prompts)} vidéos")
        print(f"📦 Taille des lots: {batch_size}")
        print("=" * 60)
        
        results = []
        
        # Traiter par lots pour respecter les limites de concurrence
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\n📋 Lot {batch_num}/{(len(prompts)-1)//batch_size + 1}")
            
            # Lancer toutes les générations du lot
            batch_tasks = []
            for prompt in batch:
                result = self.generate_video(prompt)
                if result['success']:
                    batch_tasks.append(result)
                else:
                    results.append(result)
            
            # Attendre la completion de toutes les tâches du lot
            for task in batch_tasks:
                completion = self.wait_for_completion(task['task_id'])
                task.update(completion)
                results.append(task)
                
                if completion.get('status') == 'COMPLETED':
                    print(f"🎉 Vidéo prête: {task['prompt'][:30]}...")
                    print(f"🔗 URL: {completion.get('video_url')}")
                else:
                    print(f"💥 Échec: {task['prompt'][:30]}...")
            
            # Pause entre les lots pour éviter le rate limiting
            if i + batch_size < len(prompts):
                print("⏳ Pause entre les lots (30s)...")
                time.sleep(30)
        
        return results
    
    def generate_platform_content(self):
        """Générer du contenu vidéo pour votre plateforme d'influenceurs"""
        platform_prompts = [
            "Modern fashion influencer showcasing street style in urban setting",
            "Beauty guru demonstrating makeup tutorial with professional lighting",
            "Fitness influencer doing workout in modern gym environment",
            "Food blogger preparing aesthetic dish in stylish kitchen",
            "Travel vlogger exploring beautiful mountain landscape",
            "Tech reviewer unboxing latest gadget with clean background",
            "Lifestyle influencer morning routine in minimalist bedroom",
            "Dance creator performing trending choreography in studio"
        ]
        
        print("🌟 Génération de contenu pour votre plateforme d'influenceurs")
        return self.bulk_generate(platform_prompts, batch_size=2)

def main():
    """Test principal"""
    generator = RunwayMLVeo3Generator()
    
    if not generator.api_key:
        print("❌ Clé API RunwayML non trouvée")
        return
    
    print("🎬 RunwayML Veo-3 Generator")
    print(f"🔑 API Key: ...{generator.api_key[-8:]}")
    print("=" * 50)
    
    # Test simple
    print("\n1️⃣ Test simple...")
    result = generator.generate_video("Professional influencer creating content in modern studio")
    
    if result['success']:
        completion = generator.wait_for_completion(result['task_id'])
        if completion.get('status') == 'COMPLETED':
            print(f"🎉 Test réussi!")
            print(f"🔗 Vidéo: {completion['video_url']}")
        else:
            print(f"💥 Test échoué: {completion.get('error')}")
    
    # Génération plateforme
    print("\n2️⃣ Génération contenu plateforme...")
    platform_results = generator.generate_platform_content()
    
    # Résumé
    successful = len([r for r in platform_results if r.get('status') == 'COMPLETED'])
    print(f"\n📊 RÉSUMÉ: {successful}/{len(platform_results)} vidéos générées avec succès")
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'runwayml_generation_results_{timestamp}.json'
    
    with open(f'/workspaces/IACherie/{filename}', 'w') as f:
        json.dump(platform_results, f, indent=2)
    
    print(f"💾 Résultats sauvegardés: {filename}")

if __name__ == "__main__":
    main()