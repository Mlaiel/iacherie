#!/usr/bin/env python3
"""
Service Companion IA - Demo Script
=================================

Interactive demonstration of the virtual AI companion service.
Shows the three main features:
- Ami virtuel (Virtual friend)
- Conversation naturelle (Natural conversation) 
- Mémoire à long terme (Long-term memory)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
from typing import Optional

from backend.ai import (
    create_friendly_companion,
    create_professional_companion, 
    create_creative_companion,
    CompanionPersonalityType,
    ConversationContext
)


class CompanionDemo:
    """Interactive demo of the companion service"""
    
    def __init__(self):
        self.companion = None
        self.session = None
        self.user_id = "demo_user"
    
    async def run_demo(self):
        """Run interactive demo"""
        print("🤖 Service Companion IA - Virtual AI Companion Demo")
        print("=" * 55)
        print()
        
        # Choose personality
        personality = await self._choose_personality()
        if not personality:
            return
        
        # Create companion
        self.companion = await self._create_companion(personality)
        print(f"✓ Companion créé avec la personnalité: {personality}")
        
        # Choose context
        context = await self._choose_context()
        if not context:
            return
        
        # Start conversation
        self.session = await self.companion.start_conversation(self.user_id, context)
        print(f"✓ Conversation démarrée (Context: {context.value})")
        print(f"Session ID: {self.session.session_id}")
        print()
        
        # Show greeting
        if self.session.messages:
            greeting = self.session.messages[0]
            print(f"🤖 Companion: {greeting['content']}")
            print()
        
        # Interactive conversation
        await self._interactive_chat()
        
        # Show memory demonstration
        await self._demonstrate_memory()
        
        # End demo
        await self.companion.end_conversation(self.session.session_id)
        print("✓ Conversation terminée et sauvegardée dans la mémoire à long terme")
    
    async def _choose_personality(self) -> Optional[str]:
        """Let user choose personality type"""
        print("Choisissez la personnalité du companion:")
        print("1. Friendly (Amical)")
        print("2. Professional (Professionnel)") 
        print("3. Creative (Créatif)")
        print("4. Mentor")
        print()
        
        return "friendly"  # Default for demo
    
    async def _choose_context(self) -> Optional[ConversationContext]:
        """Let user choose conversation context"""
        print("Choisissez le contexte de conversation:")
        print("1. Casual (Décontracté)")
        print("2. Business (Affaires)")
        print("3. Creative Session (Session Créative)")
        print("4. Problem Solving (Résolution de problèmes)")
        print()
        
        return ConversationContext.CASUAL  # Default for demo
    
    async def _create_companion(self, personality: str):
        """Create companion with specified personality"""
        if personality == "professional":
            return await create_professional_companion()
        elif personality == "creative":
            return await create_creative_companion()
        else:
            return await create_friendly_companion()
    
    async def _interactive_chat(self):
        """Simulate interactive chat"""
        print("💬 Conversation naturelle (tapez 'exit' pour terminer):")
        print("-" * 50)
        
        # Demo messages to showcase functionality
        demo_messages = [
            "Salut! Je suis un créateur de contenu musical.",
            "J'aimerais améliorer ma stratégie de contenu.",
            "Quels conseils peux-tu me donner pour ma chaîne YouTube?",
            "Je veux me souvenir: j'aime la musique électronique et je veux sortir un album l'année prochaine."
        ]
        
        for message in demo_messages:
            print(f"👤 Vous: {message}")
            
            response = await self.companion.process_message(self.session.session_id, message)
            
            print(f"🤖 Companion: {response.content}")
            print()
            
            if response.suggestions:
                print("💡 Suggestions:")
                for i, suggestion in enumerate(response.suggestions, 1):
                    print(f"   {i}. {suggestion}")
                print()
            
            if response.follow_up_questions:
                print("❓ Questions de suivi:")
                for i, question in enumerate(response.follow_up_questions, 1):
                    print(f"   {i}. {question}")
                print()
            
            # Short pause for demo
            await asyncio.sleep(1)
    
    async def _demonstrate_memory(self):
        """Demonstrate long-term memory capabilities"""
        print("🧠 Démonstration de la Mémoire à Long Terme:")
        print("-" * 45)
        
        # Get current memory
        memory = await self.companion.get_memory(self.user_id)
        
        print(f"📊 Statistiques de mémoire:")
        print(f"   • Souvenirs stockés: {len(memory.memories)}")
        print(f"   • Préférences: {len(memory.preferences)}")
        print(f"   • Objectifs: {len(memory.goals_and_aspirations)}")
        print(f"   • Conversations: {len(memory.conversation_history)}")
        print(f"   • Dernière interaction: {memory.last_interaction}")
        print()
        
        if memory.preferences:
            print("🎯 Préférences détectées:")
            for key, value in memory.preferences.items():
                print(f"   • {key}: {value}")
            print()
        
        if memory.goals_and_aspirations:
            print("🎯 Objectifs et aspirations:")
            for goal in memory.goals_and_aspirations:
                print(f"   • {goal}")
            print()
        
        # Test memory update
        new_memory = {
            "preferences": {"instrument": "synthesizer", "genre": "electronic"},
            "goals": ["collaborer avec d'autres artistes"],
            "important_info": "Préfère travailler le soir"
        }
        
        success = await self.companion.update_memory(self.user_id, new_memory)
        
        if success:
            print("✓ Mémoire mise à jour avec de nouvelles informations")
            
            updated_memory = await self.companion.get_memory(self.user_id)
            print(f"📈 Nouvelles statistiques:")
            print(f"   • Souvenirs: {len(updated_memory.memories)}")
            print(f"   • Préférences: {len(updated_memory.preferences)}")
            print(f"   • Objectifs: {len(updated_memory.goals_and_aspirations)}")
        print()


async def main():
    """Main demo function"""
    try:
        demo = CompanionDemo()
        await demo.run_demo()
        
        print("🎉 Démonstration terminée avec succès!")
        print()
        print("Fonctionnalités démontrées:")
        print("✓ Ami virtuel - Interface conversationnelle personnalisée")
        print("✓ Conversation naturelle - Traitement contextuel des messages")
        print("✓ Mémoire à long terme - Stockage et récupération d'informations")
        
    except Exception as e:
        print(f"❌ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Démarrage de la démonstration Service Companion IA...")
    asyncio.run(main())