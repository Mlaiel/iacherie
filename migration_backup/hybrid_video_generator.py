#!/usr/bin/env python3
"""
🎬 SYSTÈME HYBRIDE DE GÉNÉRATION VIDÉO
=====================================

Gestionnaire intelligent qui choisit automatiquement:
- Pika Labs (GRATUIT) pour génération de masse
- RunwayML (PAYANT) uniquement pour cas premium spécifiques

Économie garantie: Préservation de vos 680 crédits RunwayML
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

class VideoProvider(Enum):
    PIKA_LABS = "pika_labs"
    RUNWAYML = "runwayml"

class VideoQuality(Enum):
    STANDARD = "standard"  # Pika Labs
    PREMIUM = "premium"    # RunwayML uniquement si critique

@dataclass
class VideoRequest:
    prompt: str
    duration: int = 8
    quality: VideoQuality = VideoQuality.STANDARD
    priority: str = "normal"  # normal, high, critical
    user_id: str = "default"
    
@dataclass
class VideoResponse:
    provider: VideoProvider
    status: str
    estimated_cost: float
    estimated_time: str
    task_id: Optional[str] = None
    message: str = ""

class HybridVideoGenerator:
    def __init__(self):
        self.runwayml_credits = 680  # Crédits restants
        self.min_credits_reserve = 200
        self.veo3_cost_per_second = 40
        
    def analyze_request(self, request: VideoRequest) -> VideoProvider:
        """Analyser la demande et choisir le provider optimal"""
        
        # Mots-clés qui nécessitent RunwayML
        premium_keywords = [
            "ultra realistic", "photorealistic", "4K", "cinema quality",
            "professional", "commercial", "broadcast", "hollywood"
        ]
        
        # Vérifier si c'est vraiment critique
        needs_premium = any(keyword in request.prompt.lower() 
                          for keyword in premium_keywords)
        
        # Logique de décision
        if request.quality == VideoQuality.PREMIUM and request.priority == "critical":
            if needs_premium and self.can_afford_runwayml(request.duration):
                return VideoProvider.RUNWAYML
        
        # Par défaut: Pika Labs (gratuit)
        return VideoProvider.PIKA_LABS
    
    def can_afford_runwayml(self, duration: int) -> bool:
        """Vérifier si on peut se permettre RunwayML"""
        cost = self.veo3_cost_per_second * duration
        available_budget = self.runwayml_credits - self.min_credits_reserve
        return cost <= available_budget
    
    def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Générer une vidéo avec le provider optimal"""
        
        provider = self.analyze_request(request)
        
        if provider == VideoProvider.PIKA_LABS:
            return self._generate_pika(request)
        else:
            return self._generate_runwayml(request)
    
    def _generate_pika(self, request: VideoRequest) -> VideoResponse:
        """Génération via Pika Labs (GRATUIT)"""
        return VideoResponse(
            provider=VideoProvider.PIKA_LABS,
            status="queued",
            estimated_cost=0.0,
            estimated_time="2-5 minutes",
            message=f"✅ Génération GRATUITE via Pika Labs Discord Bot"
        )
    
    def _generate_runwayml(self, request: VideoRequest) -> VideoResponse:
        """Génération via RunwayML (PAYANT)"""
        cost = self.veo3_cost_per_second * request.duration
        
        if not self.can_afford_runwayml(request.duration):
            # Fallback vers Pika Labs
            return VideoResponse(
                provider=VideoProvider.PIKA_LABS,
                status="fallback",
                estimated_cost=0.0,
                estimated_time="2-5 minutes",
                message=f"⚠️ RunwayML trop cher ({cost} crédits), basculement vers Pika Labs GRATUIT"
            )
        
        return VideoResponse(
            provider=VideoProvider.RUNWAYML,
            status="queued",
            estimated_cost=cost,
            estimated_time="3-8 minutes",
            message=f"💰 Génération PREMIUM via RunwayML Veo-3 ({cost} crédits)"
        )
    
    def batch_generate(self, requests: List[VideoRequest]) -> List[VideoResponse]:
        """Génération en masse avec optimisation automatique"""
        responses = []
        total_cost = 0
        
        print("🎬 GÉNÉRATION VIDÉO EN MASSE - MODE HYBRIDE")
        print("=" * 60)
        
        for i, request in enumerate(requests, 1):
            print(f"\n📹 Vidéo {i}/{len(requests)}")
            print(f"   Prompt: {request.prompt[:50]}...")
            
            response = self.generate_video(request)
            responses.append(response)
            total_cost += response.estimated_cost
            
            print(f"   Provider: {response.provider.value}")
            print(f"   Coût: {response.estimated_cost} crédits")
            print(f"   {response.message}")
        
        print(f"\n📊 RÉSUMÉ DE LA GÉNÉRATION:")
        pika_count = sum(1 for r in responses if r.provider == VideoProvider.PIKA_LABS)
        runwayml_count = sum(1 for r in responses if r.provider == VideoProvider.RUNWAYML)
        
        print(f"   Total vidéos: {len(requests)}")
        print(f"   Pika Labs (gratuit): {pika_count}")
        print(f"   RunwayML (payant): {runwayml_count}")
        print(f"   Coût total: {total_cost} crédits")
        print(f"   Économies: {(len(requests) * 320) - total_cost} crédits!")
        
        return responses

def demo_generation():
    """Démonstration du système hybride"""
    generator = HybridVideoGenerator()
    
    # Exemples de demandes variées
    requests = [
        VideoRequest("A cat playing in the garden", duration=5, quality=VideoQuality.STANDARD),
        VideoRequest("Mountain landscape at sunset", duration=8, quality=VideoQuality.STANDARD),
        VideoRequest("Ultra realistic commercial product shot 4K", duration=5, quality=VideoQuality.PREMIUM, priority="critical"),
        VideoRequest("Dancing people at a party", duration=6, quality=VideoQuality.STANDARD),
        VideoRequest("Simple animation for social media", duration=4, quality=VideoQuality.STANDARD),
    ]
    
    # Génération en masse
    responses = generator.batch_generate(requests)
    
    # Économies réalisées
    standard_cost = len(requests) * 320  # Si tout était sur RunwayML
    actual_cost = sum(r.estimated_cost for r in responses)
    savings = standard_cost - actual_cost
    
    print(f"\n💰 ANALYSE ÉCONOMIQUE:")
    print(f"   Coût si 100% RunwayML: {standard_cost} crédits")
    print(f"   Coût avec système hybride: {actual_cost} crédits")
    print(f"   ÉCONOMIES: {savings} crédits ({(savings/standard_cost)*100:.1f}%)")

if __name__ == "__main__":
    demo_generation()