"""
AI Agents Learning System

Advanced learning and personalization system for AI agents to adapt and improve over time.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Learning modes for agent adaptation."""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"  
    REINFORCEMENT = "reinforcement"
    ACTIVE = "active"
    TRANSFER = "transfer"


@dataclass
class LearningMetrics:
    """Metrics for tracking learning progress."""
    accuracy: float = 0.0
    loss: float = float('inf')
    improvement_rate: float = 0.0
    confidence: float = 0.0
    samples_processed: int = 0
    learning_cycles: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalizationProfile:
    """User personalization profile."""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    behavior_patterns: Dict[str, List[float]] = field(default_factory=dict)
    interaction_history: List[Dict] = field(default_factory=list)
    adaptation_level: float = 0.0
    last_interaction: Optional[datetime] = None


class AgentLearningSystem:
    """Advanced learning system for AI agents."""
    
    def __init__(self, 
                 learning_rate: float = 0.01,
                 adaptation_threshold: float = 0.1,
                 max_memory_size: int = 10000):
        """Initialize the learning system."""
        self.learning_rate = learning_rate
        self.adaptation_threshold = adaptation_threshold
        self.max_memory_size = max_memory_size
        
        # Learning state
        self.metrics = LearningMetrics()
        self.memory = []
        self.knowledge_base = {}
        self.adaptation_history = []
        
        logger.info("Agent learning system initialized")
    
    def learn_from_interaction(self, 
                             interaction_data: Dict[str, Any],
                             feedback: Optional[float] = None,
                             mode: LearningMode = LearningMode.SUPERVISED) -> bool:
        """Learn from user interaction."""
        try:
            # Store interaction in memory
            self.memory.append({
                'data': interaction_data,
                'feedback': feedback,
                'mode': mode.value,
                'timestamp': datetime.now()
            })
            
            # Limit memory size
            if len(self.memory) > self.max_memory_size:
                self.memory.pop(0)
            
            # Update metrics
            self.metrics.samples_processed += 1
            
            # Perform learning based on mode
            if mode == LearningMode.SUPERVISED and feedback is not None:
                self._supervised_learning(interaction_data, feedback)
            elif mode == LearningMode.REINFORCEMENT:
                self._reinforcement_learning(interaction_data, feedback or 0.0)
            elif mode == LearningMode.UNSUPERVISED:
                self._unsupervised_learning(interaction_data)
            
            logger.info(f"Learned from interaction using {mode.value} mode")
            return True
            
        except Exception as e:
            logger.error(f"Learning from interaction failed: {e}")
            return False
    
    def _supervised_learning(self, data: Dict, feedback: float):
        """Supervised learning implementation."""
        # Simple gradient-like update
        error = feedback - self._predict(data)
        self.metrics.loss = abs(error)
        
        # Update knowledge base
        for key, value in data.items():
            if key not in self.knowledge_base:
                self.knowledge_base[key] = []
            self.knowledge_base[key].append({
                'value': value,
                'feedback': feedback,
                'weight': self.learning_rate * error
            })
    
    def _reinforcement_learning(self, data: Dict, reward: float):
        """Reinforcement learning implementation."""
        # Q-learning inspired update
        current_value = self._get_state_value(data)
        new_value = current_value + self.learning_rate * (reward - current_value)
        self._update_state_value(data, new_value)
        
        # Update metrics
        if reward > 0:
            self.metrics.improvement_rate += 0.1
    
    def _unsupervised_learning(self, data: Dict):
        """Unsupervised learning implementation."""
        # Pattern recognition and clustering
        patterns = self._extract_patterns(data)
        for pattern in patterns:
            if pattern not in self.knowledge_base:
                self.knowledge_base[pattern] = {'frequency': 0, 'contexts': []}
            self.knowledge_base[pattern]['frequency'] += 1
            self.knowledge_base[pattern]['contexts'].append(data)
    
    def _predict(self, data: Dict) -> float:
        """Predict outcome based on current knowledge."""
        # Simple prediction based on knowledge base
        prediction = 0.5  # Default neutral prediction
        
        for key, value in data.items():
            if key in self.knowledge_base:
                entries = self.knowledge_base[key]
                if entries:
                    avg_feedback = np.mean([entry['feedback'] for entry in entries if 'feedback' in entry])
                    prediction = (prediction + avg_feedback) / 2
        
        return prediction
    
    def _get_state_value(self, data: Dict) -> float:
        """Get current state value."""
        state_key = str(sorted(data.items()))
        return self.knowledge_base.get(state_key, {}).get('value', 0.0)
    
    def _update_state_value(self, data: Dict, value: float):
        """Update state value."""
        state_key = str(sorted(data.items()))
        if state_key not in self.knowledge_base:
            self.knowledge_base[state_key] = {}
        self.knowledge_base[state_key]['value'] = value
    
    def _extract_patterns(self, data: Dict) -> List[str]:
        """Extract patterns from data."""
        patterns = []
        for key, value in data.items():
            if isinstance(value, str):
                patterns.append(f"{key}:{value}")
            elif isinstance(value, (int, float)):
                patterns.append(f"{key}:numeric")
        return patterns
    
    def adapt_behavior(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt agent behavior based on learning."""
        try:
            adaptations = {}
            
            # Check if adaptation is needed
            if self.metrics.samples_processed > 10:  # Minimum samples needed
                confidence = min(1.0, self.metrics.samples_processed / 100)
                
                # Generate adaptations based on learned patterns
                for pattern, info in self.knowledge_base.items():
                    if isinstance(info, dict) and 'frequency' in info:
                        if info['frequency'] > 5:  # Pattern is significant
                            adaptations[pattern] = {
                                'confidence': confidence,
                                'frequency': info['frequency'],
                                'recommendation': 'high_priority'
                            }
            
            self.adaptation_history.append({
                'timestamp': datetime.now(),
                'context': context,
                'adaptations': adaptations,
                'metrics': self.metrics
            })
            
            logger.info(f"Generated {len(adaptations)} behavioral adaptations")
            return adaptations
            
        except Exception as e:
            logger.error(f"Behavior adaptation failed: {e}")
            return {}
    
    def get_learning_progress(self) -> Dict[str, Any]:
        """Get current learning progress."""
        return {
            'metrics': {
                'samples_processed': self.metrics.samples_processed,
                'learning_cycles': self.metrics.learning_cycles,
                'improvement_rate': self.metrics.improvement_rate,
                'confidence': min(1.0, self.metrics.samples_processed / 100)
            },
            'knowledge_base_size': len(self.knowledge_base),
            'memory_usage': len(self.memory),
            'last_updated': self.metrics.last_updated.isoformat()
        }
    
    def reset_learning(self):
        """Reset learning state."""
        self.metrics = LearningMetrics()
        self.memory = []
        self.knowledge_base = {}
        self.adaptation_history = []
        logger.info("Learning system reset")


class PersonalizationEngine:
    """Engine for personalizing user experience."""
    
    def __init__(self):
        """Initialize personalization engine."""
        self.profiles = {}
        self.global_patterns = {}
        self.learning_system = AgentLearningSystem()
        
        logger.info("Personalization engine initialized")
    
    def create_profile(self, user_id: str) -> PersonalizationProfile:
        """Create new user personalization profile."""
        profile = PersonalizationProfile(user_id=user_id)
        self.profiles[user_id] = profile
        logger.info(f"Created personalization profile for user {user_id}")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[PersonalizationProfile]:
        """Get user personalization profile."""
        return self.profiles.get(user_id)
    
    def update_preferences(self, 
                          user_id: str, 
                          preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        try:
            if user_id not in self.profiles:
                self.create_profile(user_id)
            
            profile = self.profiles[user_id]
            profile.preferences.update(preferences)
            profile.last_interaction = datetime.now()
            
            # Learn from preference update
            self.learning_system.learn_from_interaction(
                {'user_id': user_id, 'preferences': preferences},
                feedback=1.0,  # Positive feedback for preference updates
                mode=LearningMode.SUPERVISED
            )
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update preferences for user {user_id}: {e}")
            return False
    
    def track_behavior(self, 
                      user_id: str, 
                      action: str, 
                      context: Dict[str, Any]) -> bool:
        """Track user behavior for personalization."""
        try:
            if user_id not in self.profiles:
                self.create_profile(user_id)
            
            profile = self.profiles[user_id]
            
            # Add to interaction history
            interaction = {
                'action': action,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            profile.interaction_history.append(interaction)
            
            # Update behavior patterns
            if action not in profile.behavior_patterns:
                profile.behavior_patterns[action] = []
            
            # Simple pattern tracking (frequency over time)
            profile.behavior_patterns[action].append(1.0)
            
            # Limit history size
            if len(profile.interaction_history) > 1000:
                profile.interaction_history.pop(0)
            
            profile.last_interaction = datetime.now()
            
            # Learn from behavior
            self.learning_system.learn_from_interaction(
                {'user_id': user_id, 'action': action, 'context': context},
                mode=LearningMode.UNSUPERVISED
            )
            
            logger.info(f"Tracked behavior for user {user_id}: {action}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track behavior for user {user_id}: {e}")
            return False
    
    def get_recommendations(self, 
                           user_id: str, 
                           context: Optional[Dict] = None) -> List[Dict]:
        """Get personalized recommendations for user."""
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return []
            
            recommendations = []
            
            # Preference-based recommendations
            for pref_key, pref_value in profile.preferences.items():
                recommendations.append({
                    'type': 'preference',
                    'key': pref_key,
                    'value': pref_value,
                    'confidence': 0.8,
                    'reason': 'User preference'
                })
            
            # Behavior-based recommendations
            for action, patterns in profile.behavior_patterns.items():
                if len(patterns) > 3:  # Significant pattern
                    avg_frequency = np.mean(patterns[-10:])  # Recent pattern
                    if avg_frequency > 0.5:
                        recommendations.append({
                            'type': 'behavior',
                            'action': action,
                            'frequency': avg_frequency,
                            'confidence': min(0.9, len(patterns) / 10),
                            'reason': 'Behavior pattern'
                        })
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for user {user_id}: {e}")
            return []
    
    def adapt_interface(self, 
                       user_id: str, 
                       interface_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt interface based on user personalization."""
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return interface_config
            
            adapted_config = interface_config.copy()
            
            # Apply preference-based adaptations
            for pref_key, pref_value in profile.preferences.items():
                if pref_key in adapted_config:
                    adapted_config[pref_key] = pref_value
            
            # Apply behavior-based adaptations
            adaptations = self.learning_system.adapt_behavior({
                'user_id': user_id,
                'interface_config': interface_config
            })
            
            for adaptation_key, adaptation_info in adaptations.items():
                if adaptation_info.get('confidence', 0) > 0.7:
                    # Apply high-confidence adaptations
                    adapted_config[adaptation_key] = adaptation_info
            
            profile.adaptation_level = min(1.0, profile.adaptation_level + 0.1)
            
            logger.info(f"Adapted interface for user {user_id}")
            return adapted_config
            
        except Exception as e:
            logger.error(f"Failed to adapt interface for user {user_id}: {e}")
            return interface_config


# Module initialization
logger.info("Agent learning system module loaded successfully")
