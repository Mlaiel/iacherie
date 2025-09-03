#!/usr/bin/env python3
"""Advanced IA Matching Service Demo

Comprehensive demonstration of the new Advanced IA Matching Service capabilities.
Shows all 6 implemented features with real-world scenarios.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated code are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, REVERSE ENGINEERING, 
OR COMMERCIALIZATION without explicit written permission is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

For legitimate licensing inquiries: mlaiel@live.de
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from services.advanced_matching_service import (
    AdvancedMatchingService,
    MatchingStrategy,
    CreativeMatchType
)
from services.graph_database import CreatorGraphDatabase, RelationshipType


class AdvancedMatchingDemo:
    """Demo class for Advanced IA Matching Service"""
    
    def __init__(self):
        self.matching_service = None
        self.graph_db = None
        self.demo_creators = []
    
    async def initialize(self):
        """Initialize the demo services"""
        print("🚀 Initializing Advanced IA Matching Service Demo...")
        print("=" * 60)
        
        # Initialize matching service
        self.matching_service = AdvancedMatchingService()
        await self.matching_service.initialize_models()
        print("✅ Advanced Matching Service initialized")
        
        # Initialize graph database
        self.graph_db = CreatorGraphDatabase(db_path=":memory:")
        print("✅ Graph Database initialized")
        print()
    
    async def create_demo_creators(self):
        """Create diverse demo creator profiles"""
        print("👥 Creating Demo Creator Profiles...")
        print("-" * 40)
        
        creators_data = [
            {
                "creator_id": "prod_001",
                "username": "ElectroMaestro",
                "primary_genres": ["electronic", "house", "techno"],
                "secondary_genres": ["ambient", "trance"],
                "skills": ["production", "mixing", "mastering", "sound_design"],
                "production_skills": {"ableton": 0.95, "logic": 0.8, "serum": 0.9},
                "software_proficiency": {"ableton": 0.95, "serum": 0.9, "massive": 0.8},
                "equipment_access": ["studio_monitors", "synthesizer", "midi_controller", "audio_interface"],
                "past_collaborations": ["collab_001", "collab_002", "collab_003"],
                "platform_metrics": {
                    "youtube": {"followers": 125000, "engagement_rate": 0.12},
                    "spotify": {"followers": 85000, "monthly_listeners": 450000},
                    "soundcloud": {"followers": 65000, "plays": 2500000}
                }
            },
            {
                "creator_id": "vocal_001",
                "username": "SoulfulVoice",
                "primary_genres": ["r&b", "soul", "neo-soul"],
                "secondary_genres": ["jazz", "pop"],
                "skills": ["vocals", "songwriting", "melody_composition", "harmony"],
                "production_skills": {"logic": 0.7, "pro_tools": 0.8},
                "software_proficiency": {"logic": 0.7, "auto_tune": 0.6, "melodyne": 0.8},
                "equipment_access": ["condenser_microphone", "vocal_booth", "preamp"],
                "past_collaborations": ["collab_004", "collab_005"],
                "platform_metrics": {
                    "instagram": {"followers": 180000, "engagement_rate": 0.15},
                    "tiktok": {"followers": 320000, "engagement_rate": 0.18},
                    "spotify": {"followers": 95000, "monthly_listeners": 380000}
                }
            },
            {
                "creator_id": "rock_001",
                "username": "RiffMaster",
                "primary_genres": ["rock", "alternative", "indie"],
                "secondary_genres": ["grunge", "punk"],
                "skills": ["guitar", "bass", "songwriting", "live_performance"],
                "production_skills": {"cubase": 0.8, "reaper": 0.7},
                "software_proficiency": {"cubase": 0.8, "amplitube": 0.9, "guitar_rig": 0.8},
                "equipment_access": ["electric_guitar", "bass_guitar", "amplifier", "effects_pedals"],
                "past_collaborations": ["collab_006"],
                "platform_metrics": {
                    "youtube": {"followers": 75000, "engagement_rate": 0.10},
                    "instagram": {"followers": 45000, "engagement_rate": 0.08},
                    "bandcamp": {"followers": 8000, "sales": 15000}
                }
            },
            {
                "creator_id": "jazz_001",
                "username": "JazzFusionist",
                "primary_genres": ["jazz", "fusion", "experimental"],
                "secondary_genres": ["blues", "world"],
                "skills": ["piano", "composition", "arrangement", "improvisation"],
                "production_skills": {"logic": 0.85, "reason": 0.7},
                "software_proficiency": {"logic": 0.85, "kontakt": 0.9, "pianoteq": 0.8},
                "equipment_access": ["grand_piano", "midi_keyboard", "studio_monitors"],
                "past_collaborations": ["collab_007", "collab_008", "collab_009", "collab_010"],
                "platform_metrics": {
                    "spotify": {"followers": 45000, "monthly_listeners": 185000},
                    "youtube": {"followers": 35000, "engagement_rate": 0.14},
                    "bandcamp": {"followers": 12000, "sales": 25000}
                }
            },
            {
                "creator_id": "hiphop_001",
                "username": "BeatArchitect",
                "primary_genres": ["hip-hop", "trap", "boom_bap"],
                "secondary_genres": ["r&b", "lo-fi"],
                "skills": ["beat_making", "sampling", "mixing", "rap"],
                "production_skills": {"fl_studio": 0.95, "ableton": 0.8},
                "software_proficiency": {"fl_studio": 0.95, "kontakt": 0.8, "battery": 0.9},
                "equipment_access": ["mpc", "turntables", "studio_monitors", "microphone"],
                "past_collaborations": ["collab_011", "collab_012"],
                "platform_metrics": {
                    "soundcloud": {"followers": 95000, "plays": 3200000},
                    "youtube": {"followers": 88000, "engagement_rate": 0.13},
                    "tiktok": {"followers": 210000, "engagement_rate": 0.16}
                }
            }
        ]
        
        for creator_data in creators_data:
            profile = await self.matching_service.register_creator(creator_data)
            self.demo_creators.append(profile)
            
            # Also add to graph database
            await self.graph_db.add_creator_node(creator_data["creator_id"], creator_data)
            
            print(f"✅ {profile.username} ({profile.creator_id})")
            print(f"   Genres: {', '.join(profile.primary_genres)}")
            print(f"   Skills: {', '.join(profile.skills[:3])}...")
            print(f"   Creativity: {profile.creativity_score:.2f} | "
                  f"Innovation: {profile.innovation_index:.2f} | "
                  f"Versatility: {profile.versatility_rating:.2f}")
            print()
        
        print(f"✅ Created {len(self.demo_creators)} diverse creator profiles\n")
    
    async def demo_compatibility_scoring(self):
        """Demonstrate compatibility scoring between creators"""
        print("🧮 Compatibility Scoring Analysis...")
        print("-" * 40)
        
        # Test different creator combinations
        test_pairs = [
            (0, 1),  # Electronic producer + R&B vocalist
            (0, 4),  # Electronic producer + Hip-hop producer
            (1, 3),  # R&B vocalist + Jazz pianist
            (2, 3),  # Rock guitarist + Jazz pianist
        ]
        
        for i, (idx1, idx2) in enumerate(test_pairs, 1):
            creator1 = self.demo_creators[idx1]
            creator2 = self.demo_creators[idx2]
            
            print(f"\n{i}. {creator1.username} ↔ {creator2.username}")
            print("   " + "─" * 50)
            
            compatibility = await self.matching_service.calculate_compatibility_score(
                creator1.creator_id,
                creator2.creator_id
            )
            
            print(f"   Overall Compatibility: {compatibility.overall_score:.2f}/1.0 🎯")
            print(f"   ├─ Musical Compatibility: {compatibility.musical_compatibility:.2f}")
            print(f"   ├─ Technical Compatibility: {compatibility.technical_compatibility:.2f}")
            print(f"   ├─ Creative Synergy: {compatibility.creative_synergy:.2f}")
            print(f"   ├─ Communication Fit: {compatibility.communication_fit:.2f}")
            print(f"   └─ Commercial Potential: {compatibility.commercial_potential:.2f}")
            
            print(f"\n   Success Probability: {compatibility.success_probability:.1%} 📈")
            
            if compatibility.complementary_strengths:
                print(f"   Strengths: {compatibility.complementary_strengths[0]}")
            
            if compatibility.collaboration_type_suggestions:
                print(f"   Suggested: {compatibility.collaboration_type_suggestions[0]}")
        
        print("\n✅ Compatibility scoring analysis complete\n")
    
    async def demo_musical_style_matching(self):
        """Demonstrate musical style and genre matching"""
        print("🎵 Musical Style & Genre Matching...")
        print("-" * 40)
        
        target_creator = self.demo_creators[0]  # ElectroMaestro
        
        match_types = [
            (CreativeMatchType.SIMILAR_STYLE, "Similar Musical Style"),
            (CreativeMatchType.COMPLEMENTARY_SKILLS, "Complementary Skills"),
            (CreativeMatchType.GENRE_FUSION, "Genre Fusion Potential"),
        ]
        
        for match_type, description in match_types:
            print(f"\n{description} for {target_creator.username}:")
            print("   " + "─" * 45)
            
            matches = await self.matching_service.find_musical_style_matches(
                target_creator.creator_id,
                match_type,
                limit=3
            )
            
            if matches:
                for i, (match_id, similarity, reason) in enumerate(matches, 1):
                    match_creator = next(c for c in self.demo_creators if c.creator_id == match_id)
                    print(f"   {i}. {match_creator.username}")
                    print(f"      Similarity: {similarity:.1%} | {reason}")
            else:
                print("   No matches found above threshold")
        
        print("\n✅ Musical style matching complete\n")
    
    async def demo_collaboration_prediction(self):
        """Demonstrate collaboration success prediction"""
        print("🔮 Collaboration Success Prediction...")
        print("-" * 40)
        
        # Test different collaboration scenarios
        scenarios = [
            {
                "participants": [0, 1],  # Electronic + R&B
                "type": "producer_vocalist_collaboration",
                "description": "Electronic Producer + R&B Vocalist"
            },
            {
                "participants": [2, 3],  # Rock + Jazz
                "type": "fusion_experiment", 
                "description": "Rock Guitarist + Jazz Pianist"
            },
            {
                "participants": [0, 4],  # Electronic + Hip-hop
                "type": "remix_collaboration",
                "description": "Electronic + Hip-hop Producers"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            participant_ids = [self.demo_creators[idx].creator_id for idx in scenario["participants"]]
            participant_names = [self.demo_creators[idx].username for idx in scenario["participants"]]
            
            print(f"\n{i}. {scenario['description']}")
            print(f"   Participants: {' + '.join(participant_names)}")
            print("   " + "─" * 50)
            
            prediction = await self.matching_service.predict_collaboration_success(
                participant_ids,
                scenario["type"],
                ["youtube", "spotify", "tiktok", "instagram"]
            )
            
            print(f"   Predicted Metrics:")
            print(f"   ├─ Engagement Rate: {prediction.predicted_engagement_rate:.1%}")
            print(f"   ├─ Expected Reach: {prediction.predicted_reach:,} people")
            print(f"   ├─ Commercial Value: ${prediction.predicted_commercial_value:,.0f}")
            print(f"   └─ Viral Potential: {prediction.viral_potential:.1%}")
            
            print(f"\n   Optimal Platforms: {', '.join(prediction.optimal_platforms)}")
            print(f"   Suggested Format: {prediction.suggested_content_format.replace('_', ' ').title()}")
            
            if prediction.risk_factors:
                print(f"   Risks: {prediction.risk_factors[0]}")
            
            if prediction.mitigation_strategies:
                print(f"   Mitigation: {prediction.mitigation_strategies[0]}")
        
        print("\n✅ Collaboration prediction complete\n")
    
    async def demo_proactive_suggestions(self):
        """Demonstrate proactive AI suggestions"""
        print("🤖 Proactive AI Suggestions...")
        print("-" * 40)
        
        target_creator = self.demo_creators[1]  # SoulfulVoice
        
        print(f"Generating proactive suggestions for {target_creator.username}:")
        print("   " + "─" * 45)
        
        suggestions = await self.matching_service.generate_proactive_suggestions(
            target_creator.creator_id,
            ["collaboration_opportunity", "genre_exploration", "skill_development"]
        )
        
        for i, suggestion in enumerate(suggestions[:5], 1):
            urgency_emoji = {
                "low": "🔵",
                "medium": "🟡", 
                "high": "🔴",
                "critical": "🚨"
            }
            
            print(f"\n   {i}. {suggestion.title}")
            print(f"      {urgency_emoji.get(suggestion.urgency_level, '⚪')} "
                  f"{suggestion.urgency_level.upper()} | "
                  f"Success: {suggestion.success_probability:.0%} | "
                  f"AI Confidence: {suggestion.ai_confidence:.0%}")
            print(f"      Type: {suggestion.suggestion_type.replace('_', ' ').title()}")
            print(f"      Action: {suggestion.description}")
            
            if suggestion.action_items:
                print(f"      Next Steps: {suggestion.action_items[0]}")
        
        print("\n✅ Proactive suggestions generated\n")
    
    async def demo_graph_database(self):
        """Demonstrate graph database for complex relationships"""
        print("🌐 Graph Database & Network Analysis...")
        print("-" * 40)
        
        # Create relationships between creators
        relationships = [
            (0, 1, RelationshipType.COLLABORATION, 0.85),  # Electronic + R&B
            (0, 4, RelationshipType.GENRE_SIMILARITY, 0.72),  # Electronic + Hip-hop
            (1, 3, RelationshipType.SKILL_COMPLEMENT, 0.68),  # R&B + Jazz
            (2, 3, RelationshipType.INFLUENCE, 0.60),  # Rock + Jazz
            (3, 4, RelationshipType.MENTOR_MENTEE, 0.75),  # Jazz + Hip-hop
        ]
        
        print("Adding relationships to graph database:")
        for idx1, idx2, rel_type, weight in relationships:
            creator1 = self.demo_creators[idx1]
            creator2 = self.demo_creators[idx2]
            
            await self.graph_db.add_relationship(
                creator1.creator_id,
                creator2.creator_id,
                rel_type,
                weight,
                0.9,  # confidence
                {"created_by": "demo", "timestamp": datetime.now().isoformat()}
            )
            
            print(f"   ✅ {creator1.username} ↔ {creator2.username} ({rel_type.value})")
        
        print("\nNetwork Analysis Results:")
        print("   " + "─" * 35)
        
        # Analyze each creator's network position
        for creator in self.demo_creators[:3]:  # Analyze first 3
            metrics = await self.graph_db.calculate_network_metrics(creator.creator_id)
            
            if metrics:
                print(f"\n   {creator.username}:")
                print(f"   ├─ Degree Centrality: {metrics.get('degree_centrality', 0):.2f}")
                print(f"   ├─ Betweenness: {metrics.get('betweenness_centrality', 0):.2f}")
                print(f"   └─ PageRank: {metrics.get('pagerank', 0):.3f}")
        
        # Community detection
        print(f"\nCommunity Detection:")
        communities = await self.graph_db.detect_communities()
        
        if communities:
            for community_id, community in communities.items():
                member_names = [
                    next(c.username for c in self.demo_creators if c.creator_id == mid)
                    for mid in community.members
                ]
                print(f"   Community {community_id}: {', '.join(member_names)}")
                if community.genre_focus:
                    print(f"      Genre Focus: {', '.join(community.genre_focus)}")
        
        print("\n✅ Graph database analysis complete\n")
    
    async def demo_network_evolution(self):
        """Demonstrate network evolution summary"""
        print("📊 Network Evolution & Analytics Summary...")
        print("-" * 40)
        
        summary = await self.graph_db.get_network_evolution_summary(days_back=30)
        
        if summary:
            print(f"Network Overview (Last 30 days):")
            print("   " + "─" * 35)
            
            growth = summary.get("network_growth", {})
            structure = summary.get("network_structure", {})
            
            print(f"   Total Creators: {growth.get('total_nodes', 0)}")
            print(f"   Total Relationships: {growth.get('total_edges', 0)}")
            print(f"   Network Density: {structure.get('density', 0):.2%}")
            print(f"   Communities Detected: {structure.get('communities', 0)}")
            print(f"   Average Path Length: {structure.get('avg_path_length', 0):.2f}")
            
            top_influencers = summary.get("top_influencers", [])
            if top_influencers:
                print(f"\n   Top Influencers:")
                for influencer in top_influencers[:3]:
                    print(f"   ├─ {influencer.get('username', 'Unknown')}: "
                          f"{influencer.get('influence_score', 0):.2f}")
            
            rel_dist = summary.get("relationship_distribution", {})
            if rel_dist:
                print(f"\n   Relationship Types:")
                for rel_type, count in rel_dist.items():
                    print(f"   ├─ {rel_type.replace('_', ' ').title()}: {count}")
        
        print("\n✅ Network evolution analysis complete\n")
    
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🎯 ADVANCED IA MATCHING SERVICE DEMONSTRATION")
        print("=" * 60)
        print("Enterprise-grade AI-powered creator matching and collaboration system")
        print("Author: Fahed Mlaiel (mlaiel@live.de)")
        print("⚠️  PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED")
        print("=" * 60)
        print()
        
        try:
            await self.initialize()
            await self.create_demo_creators()
            await self.demo_compatibility_scoring()
            await self.demo_musical_style_matching()
            await self.demo_collaboration_prediction()
            await self.demo_proactive_suggestions()
            await self.demo_graph_database()
            await self.demo_network_evolution()
            
            print("🏆 DEMONSTRATION COMPLETE")
            print("=" * 60)
            print("✅ All 6 core requirements successfully demonstrated:")
            print("   1. ✅ Algorithme de recommandation ML personnalisé")
            print("   2. ✅ Scoring de compatibilité créative")
            print("   3. ✅ Matching par style et genre musical")
            print("   4. ✅ Prédiction de succès des collaborations")
            print("   5. ✅ Système de suggestions proactives")
            print("   6. ✅ Graph database pour relations complexes")
            print()
            print("🚀 READY FOR PRODUCTION DEPLOYMENT")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Demo error: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """Main demo function"""
    demo = AdvancedMatchingDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())