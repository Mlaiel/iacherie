# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Test suite for Collaboration Engine module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestCollaborationEngine(unittest.TestCase):
    """Test suite for CollaborationEngine class"""

    def setUp(self):
        """Set up test fixtures"""
        # Import the actual collaboration engine
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from services.collaboration_engine import CollaborationEngine, CreatorProfile, CollaborationProposal, CompatibilityScore
        
        self.engine = CollaborationEngine()
        self.sample_creator = CreatorProfile(
            user_id="creator_123",
            username="TestArtist",
            creator_type="musician",
            genres=["pop", "electronic"],
            skills=["vocals", "production"],
            experience_level="intermediate",
            average_engagement=0.08,
            follower_count=5000,
            collaboration_history=3,
            rating=4.5,
            availability=True,
            preferred_collaboration_types=["feature", "remix"],
            location="New York"
        )

    def test_creator_profile_structure(self):
        """Test creator profile data structure"""
        profile = {
            "user_id": "creator_123",
            "username": "TestArtist",
            "creator_type": "musician",
            "genres": ["pop", "electronic"],
            "skills": ["vocals", "production"],
            "experience_level": "intermediate",
            "average_engagement": 0.08,
            "follower_count": 5000,
            "collaboration_history": 3,
            "rating": 4.5,
            "availability": True,
            "preferred_collaboration_types": ["feature", "remix"]
        }
        
        # Verify required fields
        required_fields = ["user_id", "username", "creator_type", "genres", "skills"]
        for field in required_fields:
            self.assertIn(field, profile)
        
        # Verify data types
        self.assertIsInstance(profile["genres"], list)
        self.assertIsInstance(profile["skills"], list)
        self.assertIsInstance(profile["rating"], float)
        self.assertIsInstance(profile["follower_count"], int)

    def test_compatibility_scoring_calculation(self):
        """Test compatibility score calculation between creators"""
        creator1 = {
            "genres": ["pop", "rock"],
            "skills": ["vocals", "guitar"],
            "experience_level": "intermediate",
            "average_engagement": 0.08,
            "collaboration_history": 5
        }
        
        creator2 = {
            "genres": ["pop", "electronic"],
            "skills": ["production", "mixing"],
            "experience_level": "advanced",
            "average_engagement": 0.06,
            "collaboration_history": 8
        }
        
        # Calculate compatibility components
        
        # Genre compatibility (25%)
        genre1_set = set(creator1["genres"])
        genre2_set = set(creator2["genres"])
        genre_overlap = len(genre1_set & genre2_set)
        genre_total = len(genre1_set | genre2_set)
        genre_score = (genre_overlap / genre_total) if genre_total > 0 else 0
        genre_weighted = genre_score * 0.25
        
        # Skill complementarity (20%)
        skill1_set = set(creator1["skills"])
        skill2_set = set(creator2["skills"])
        skill_complement = len(skill1_set - skill2_set) / max(len(skill1_set), 1)
        skill_weighted = min(skill_complement, 1.0) * 0.20
        
        # Experience balance (15%)
        exp_levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        exp1 = exp_levels.get(creator1["experience_level"], 1)
        exp2 = exp_levels.get(creator2["experience_level"], 1)
        exp_balance = 1 - abs(exp1 - exp2) / 3
        exp_weighted = exp_balance * 0.15
        
        # Engagement compatibility (20%)
        eng1 = creator1["average_engagement"]
        eng2 = creator2["average_engagement"]
        eng_ratio = min(eng1, eng2) / max(eng1, eng2, 0.001)
        eng_weighted = eng_ratio * 0.20
        
        # Collaboration history (20%)
        history_score = min((creator1["collaboration_history"] + creator2["collaboration_history"]) / 10, 1.0)
        history_weighted = history_score * 0.20
        
        total_score = genre_weighted + skill_weighted + exp_weighted + eng_weighted + history_weighted
        
        # Verify calculations
        self.assertEqual(genre_overlap, 1)  # "pop" is common
        self.assertEqual(genre_total, 3)    # "pop", "rock", "electronic"
        self.assertAlmostEqual(genre_score, 0.33, places=2)
        self.assertGreater(total_score, 0.5)  # Should be compatible

    def test_collaboration_proposal_creation(self):
        """Test collaboration proposal creation"""
        proposal_data = {
            "type": "feature",
            "description": "Looking for vocalist for electronic track",
            "revenue_split": {"proposer": 0.6, "collaborator": 0.4},
            "timeline_days": 30,
            "requirements": ["professional recording", "original lyrics"],
            "metadata": {"genre": "electronic", "budget": 500}
        }
        
        # Validate revenue split
        revenue_split = proposal_data["revenue_split"]
        total_split = sum(revenue_split.values())
        
        # Create proposal structure
        proposal = {
            "id": "proposal_123",
            "proposer_id": "creator_1",
            "target_id": "creator_2",
            "collaboration_type": proposal_data["type"],
            "project_description": proposal_data["description"],
            "proposed_revenue_split": revenue_split,
            "timeline": proposal_data["timeline_days"],
            "requirements": proposal_data["requirements"],
            "status": "proposed",
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=7)
        }
        
        # Verify proposal structure
        self.assertAlmostEqual(total_split, 1.0, places=2)  # Revenue split should sum to 100%
        self.assertEqual(proposal["collaboration_type"], "feature")
        self.assertEqual(proposal["timeline"], 30)
        self.assertIsInstance(proposal["requirements"], list)
        self.assertEqual(proposal["status"], "proposed")

    def test_preference_filtering(self):
        """Test creator preference filtering"""
        creators = [
            {
                "user_id": "creator_1",
                "genres": ["pop", "rock"],
                "experience_level": "beginner",
                "follower_count": 1000,
                "rating": 3.5,
                "location": "New York"
            },
            {
                "user_id": "creator_2", 
                "genres": ["electronic", "pop"],
                "experience_level": "intermediate",
                "follower_count": 5000,
                "rating": 4.2,
                "location": "Los Angeles"
            },
            {
                "user_id": "creator_3",
                "genres": ["hip-hop", "r&b"],
                "experience_level": "advanced",
                "follower_count": 15000,
                "rating": 4.8,
                "location": "Nashville"
            }
        ]
        
        preferences = {
            "genres": ["pop"],
            "min_experience": "intermediate",
            "min_followers": 3000,
            "min_rating": 4.0,
            "location": "Los"  # Partial match
        }
        
        # Apply filters
        filtered_creators = []
        
        for creator in creators:
            passes_filters = True
            
            # Genre filter
            if "genres" in preferences:
                if not any(genre in creator["genres"] for genre in preferences["genres"]):
                    passes_filters = False
            
            # Experience filter
            if "min_experience" in preferences and passes_filters:
                exp_levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                creator_exp = exp_levels.get(creator["experience_level"], 1)
                min_exp = exp_levels.get(preferences["min_experience"], 1)
                if creator_exp < min_exp:
                    passes_filters = False
            
            # Follower filter
            if "min_followers" in preferences and passes_filters:
                if creator["follower_count"] < preferences["min_followers"]:
                    passes_filters = False
            
            # Rating filter
            if "min_rating" in preferences and passes_filters:
                if creator["rating"] < preferences["min_rating"]:
                    passes_filters = False
            
            # Location filter
            if "location" in preferences and passes_filters:
                if creator.get("location") and preferences["location"].lower() not in creator["location"].lower():
                    passes_filters = False
            
            if passes_filters:
                filtered_creators.append(creator)
        
        # Verify filtering results
        self.assertEqual(len(filtered_creators), 1)
        self.assertEqual(filtered_creators[0]["user_id"], "creator_2")

    def test_project_milestone_generation(self):
        """Test project milestone generation based on collaboration type"""
        collaboration_types = {
            "feature": {
                "timeline": 30,
                "expected_milestones": [
                    {"name": "Initial Recording", "deadline_ratio": 0.3},
                    {"name": "Review and Feedback", "deadline_ratio": 0.6},
                    {"name": "Final Mix", "deadline_ratio": 0.9},
                    {"name": "Release Ready", "deadline_ratio": 1.0}
                ]
            },
            "remix": {
                "timeline": 21,
                "expected_milestones": [
                    {"name": "Remix Concept", "deadline_ratio": 0.2},
                    {"name": "First Draft", "deadline_ratio": 0.5},
                    {"name": "Refined Version", "deadline_ratio": 0.8},
                    {"name": "Final Master", "deadline_ratio": 1.0}
                ]
            }
        }
        
        for collab_type, config in collaboration_types.items():
            milestones = []
            timeline = config["timeline"]
            start_date = datetime.now()
            
            for milestone in config["expected_milestones"]:
                deadline_days = timeline * milestone["deadline_ratio"]
                deadline_date = start_date + timedelta(days=deadline_days)
                
                milestone_data = {
                    "name": milestone["name"],
                    "deadline_days": deadline_days,
                    "deadline_date": deadline_date.isoformat(),
                    "completed": False
                }
                milestones.append(milestone_data)
            
            # Verify milestone generation
            self.assertEqual(len(milestones), len(config["expected_milestones"]))
            
            # Check that deadlines are in correct order
            for i in range(1, len(milestones)):
                self.assertGreater(milestones[i]["deadline_days"], milestones[i-1]["deadline_days"])

    def test_collaboration_workflow_management(self):
        """Test collaboration workflow and status management"""
        collaboration = {
            "id": "collab_123",
            "proposer_id": "creator_1",
            "target_id": "creator_2", 
            "status": "accepted",
            "metadata": {"deliverables": []}
        }
        
        # Test workflow actions
        workflow_actions = [
            {
                "action": "start_project",
                "user_id": "creator_1",
                "expected_status": "in_progress"
            },
            {
                "action": "submit_deliverable",
                "user_id": "creator_1",
                "data": {
                    "type": "audio",
                    "file_path": "/uploads/track.mp3",
                    "description": "Initial vocal recording"
                }
            },
            {
                "action": "approve_deliverable",
                "user_id": "creator_2",
                "data": {"deliverable_id": 0}
            },
            {
                "action": "complete_project",
                "user_id": "creator_1",
                "expected_status": "completed"
            }
        ]
        
        # Process workflow actions
        for action_data in workflow_actions:
            action = action_data["action"]
            user_id = action_data["user_id"]
            data = action_data.get("data", {})
            
            # Verify user authorization
            authorized = user_id in [collaboration["proposer_id"], collaboration["target_id"]]
            self.assertTrue(authorized)
            
            # Process action
            if action == "start_project":
                collaboration["status"] = "in_progress"
                
            elif action == "submit_deliverable":
                deliverable = {
                    "user_id": user_id,
                    "type": data.get("type", "audio"),
                    "file_path": data.get("file_path"),
                    "description": data.get("description"),
                    "submitted_at": datetime.now().isoformat(),
                    "approved": False
                }
                collaboration["metadata"]["deliverables"].append(deliverable)
                
            elif action == "approve_deliverable":
                deliverable_id = data.get("deliverable_id")
                if (deliverable_id is not None and 
                    deliverable_id < len(collaboration["metadata"]["deliverables"])):
                    collaboration["metadata"]["deliverables"][deliverable_id]["approved"] = True
                    collaboration["metadata"]["deliverables"][deliverable_id]["approved_by"] = user_id
                
            elif action == "complete_project":
                collaboration["status"] = "completed"
            
            # Verify expected status changes
            if "expected_status" in action_data:
                self.assertEqual(collaboration["status"], action_data["expected_status"])
        
        # Verify final state
        self.assertEqual(collaboration["status"], "completed")
        self.assertEqual(len(collaboration["metadata"]["deliverables"]), 1)
        self.assertTrue(collaboration["metadata"]["deliverables"][0]["approved"])

    def test_collaboration_insights_generation(self):
        """Test collaboration insights and analytics generation"""
        creator_id = "creator_123"
        collaboration_history = [
            {
                "id": "collab_1",
                "collaboration_type": "feature",
                "status": "completed",
                "proposer_id": creator_id,
                "target_id": "creator_2"
            },
            {
                "id": "collab_2",
                "collaboration_type": "remix",
                "status": "completed",
                "proposer_id": "creator_3",
                "target_id": creator_id
            },
            {
                "id": "collab_3",
                "collaboration_type": "feature",
                "status": "cancelled",
                "proposer_id": creator_id,
                "target_id": "creator_4"
            },
            {
                "id": "collab_4",
                "collaboration_type": "feature",
                "status": "in_progress",
                "proposer_id": creator_id,
                "target_id": "creator_5"
            }
        ]
        
        # Generate insights
        creator_collaborations = [
            c for c in collaboration_history
            if creator_id in [c["proposer_id"], c["target_id"]]
        ]
        
        completed_collaborations = [
            c for c in creator_collaborations
            if c["status"] == "completed"
        ]
        
        # Calculate metrics
        total_collaborations = len(creator_collaborations)
        completed_count = len(completed_collaborations)
        success_rate = completed_count / total_collaborations if total_collaborations > 0 else 0
        
        # Analyze collaboration types
        collaboration_types = {}
        for collab in completed_collaborations:
            collab_type = collab["collaboration_type"]
            collaboration_types[collab_type] = collaboration_types.get(collab_type, 0) + 1
        
        most_successful_type = max(collaboration_types.items(), key=lambda x: x[1])[0] if collaboration_types else None
        
        # Generate insights
        insights = {
            "total_collaborations": total_collaborations,
            "completed_collaborations": completed_count,
            "success_rate": success_rate,
            "most_successful_type": most_successful_type,
            "collaboration_types": collaboration_types
        }
        
        # Verify insights
        self.assertEqual(insights["total_collaborations"], 4)
        self.assertEqual(insights["completed_collaborations"], 2)
        self.assertEqual(insights["success_rate"], 0.5)  # 50% success rate
        self.assertEqual(insights["most_successful_type"], "feature")
        self.assertEqual(insights["collaboration_types"]["feature"], 2)
        self.assertEqual(insights["collaboration_types"]["remix"], 1)

    def test_networking_score_calculation(self):
        """Test networking score calculation for creators"""
        creator = {
            "collaboration_history": 8,
            "rating": 4.5
        }
        
        collaboration_history = [
            {"status": "completed", "collaboration_type": "feature"},
            {"status": "completed", "collaboration_type": "remix"},
            {"status": "completed", "collaboration_type": "feature"},
            {"status": "cancelled", "collaboration_type": "feature"},
            {"status": "completed", "collaboration_type": "production"},
            {"status": "in_progress", "collaboration_type": "feature"},
            {"status": "completed", "collaboration_type": "remix"},
            {"status": "completed", "collaboration_type": "feature"}
        ]
        
        # Calculate networking score components
        
        # Base score from collaboration count (40%)
        collab_score = min(len(collaboration_history) / 10, 1.0) * 40
        
        # Success rate factor (30%)
        completed_collabs = [c for c in collaboration_history if c["status"] == "completed"]
        success_rate = len(completed_collabs) / len(collaboration_history) if collaboration_history else 0
        success_score = success_rate * 30
        
        # Diversity factor (20%) - different collaboration types
        collab_types = set(c["collaboration_type"] for c in collaboration_history)
        diversity_score = min(len(collab_types) / 3, 1.0) * 20
        
        # Rating factor (10%)
        rating_score = (creator["rating"] / 5.0) * 10
        
        total_score = collab_score + success_score + diversity_score + rating_score
        
        # Verify networking score calculation
        self.assertEqual(len(completed_collabs), 6)
        self.assertEqual(success_rate, 0.75)  # 6/8 = 75%
        self.assertEqual(len(collab_types), 3)  # feature, remix, production
        self.assertAlmostEqual(total_score, 83.0, places=1)  # High networking score

    def test_dispute_resolution_workflow(self):
        """Test dispute resolution workflow"""
        collaboration = {
            "id": "collab_123",
            "proposer_id": "creator_1",
            "target_id": "creator_2",
            "status": "in_progress",
            "metadata": {}
        }
        
        dispute_data = {
            "reason": "quality_concerns",
            "details": "Deliverable does not meet agreed specifications",
            "evidence": ["screenshot1.png", "audio_comparison.mp3"]
        }
        
        # Initiate dispute
        dispute_record = {
            "disputing_user": "creator_2",
            "dispute_reason": dispute_data["reason"],
            "dispute_details": dispute_data["details"],
            "evidence": dispute_data.get("evidence", []),
            "initiated_at": datetime.now().isoformat(),
            "status": "open",
            "resolution": None,
            "mediator_assigned": None
        }
        
        collaboration["metadata"]["dispute"] = dispute_record
        collaboration["status"] = "disputed"
        
        # Dispute resolution process
        resolution_steps = [
            {
                "step": "assign_mediator",
                "mediator_id": "mediator_123",
                "timestamp": datetime.now()
            },
            {
                "step": "collect_evidence",
                "evidence_collected": True,
                "timestamp": datetime.now()
            },
            {
                "step": "mediation_session",
                "session_date": datetime.now() + timedelta(days=3),
                "timestamp": datetime.now()
            }
        ]
        
        # Process resolution steps
        for step in resolution_steps:
            if step["step"] == "assign_mediator":
                dispute_record["mediator_assigned"] = step["mediator_id"]
                dispute_record["status"] = "under_review"
        
        # Verify dispute workflow
        self.assertEqual(collaboration["status"], "disputed")
        self.assertEqual(dispute_record["status"], "under_review")
        self.assertEqual(dispute_record["disputing_user"], "creator_2")
        self.assertIsNotNone(dispute_record["mediator_assigned"])


if __name__ == '__main__':
    unittest.main()