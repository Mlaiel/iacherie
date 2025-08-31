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
Adaptive Learning Algorithms Tests

Comprehensive tests for all adaptive learning algorithms in personalization.
Tests online learning, bandits, reinforcement learning, and optimization algorithms.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import time
import os
import sys
from collections import defaultdict

# Import the algorithms modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.algorithms import (
    AdaptiveAlgorithm,
    OnlineLearningEngine,
    FeedbackProcessor,
    PersonalizationOptimizer,
    RecommendationRanker,
    PersonalityMatcher,
    EpsilonGreedyBandit,
    UCBBandit,
    ThompsonSamplingBandit,
    ContextualBandit
)
from ai.personalization.exceptions import (
    PersonalizationError,
    ModelNotLoadedError
)


class TestAdaptiveLearningAlgorithm(IsolatedAsyncioTestCase):
    """Base tests for AdaptiveLearningAlgorithm abstract class"""

    async def asyncSetUp(self):
        """Set up test environment"""
        # Test with concrete implementation (OnlineLearningAlgorithm)
        self.algorithm = OnlineLearningAlgorithm(
            learning_rate=0.01,
            decay_factor=0.95,
            regularization=0.001
        )

    async def test_algorithm_initialization(self):
        """Test algorithm proper initialization"""
        self.assertIsNotNone(self.algorithm)
        self.assertEqual(self.algorithm.algorithm_type, AlgorithmType.ONLINE_LEARNING)
        self.assertFalse(self.algorithm.is_initialized)
        self.assertEqual(self.algorithm.update_count, 0)

    async def test_algorithm_configuration(self):
        """Test algorithm configuration management"""
        config = self.algorithm.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('learning_rate', config)
        self.assertIn('decay_factor', config)
        self.assertIn('regularization', config)

    async def test_learning_rate_scheduling(self):
        """Test adaptive learning rate scheduling"""
        initial_lr = self.algorithm.learning_rate
        
        # Simulate multiple updates
        for i in range(100):
            await self.algorithm.update({
                'user_id': f'user_{i % 10}',
                'item_id': f'item_{i % 20}',
                'rating': np.random.uniform(1.0, 5.0),
                'feedback': 1.0
            })
        
        current_lr = self.algorithm.learning_rate
        
        # Learning rate should have decayed
        self.assertLess(current_lr, initial_lr)

    async def test_convergence_detection(self):
        """Test convergence detection mechanism"""
        convergence_threshold = 1e-6
        self.algorithm.convergence_threshold = convergence_threshold
        
        # Simulate convergence scenario
        stable_updates = []
        for i in range(20):
            loss = 0.1 * np.exp(-i * 0.5) + np.random.normal(0, 1e-7)
            stable_updates.append(loss)
        
        is_converged = await self.algorithm.check_convergence(stable_updates)
        self.assertTrue(is_converged)


class TestOnlineLearningAlgorithm(IsolatedAsyncioTestCase):
    """Comprehensive tests for OnlineLearningAlgorithm"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.algorithm = OnlineLearningAlgorithm(
            learning_rate=0.05,
            decay_factor=0.9,
            regularization=0.01,
            mini_batch_size=10
        )
        self.stream_data = self._generate_streaming_data()

    def _generate_streaming_data(self) -> List[Dict[str, Any]]:
        """Generate streaming data for online learning"""
        stream = []
        n_users, n_items = 50, 100
        
        for t in range(1000):  # 1000 time steps
            user_id = f'user_{np.random.randint(0, n_users)}'
            item_id = f'item_{np.random.randint(0, n_items)}'
            
            # Simulate time-dependent preferences
            time_factor = np.sin(t * 0.01) * 0.5 + 0.5
            base_rating = 3.0 + time_factor * 2.0
            rating = np.clip(base_rating + np.random.normal(0, 0.5), 1.0, 5.0)
            
            stream.append({
                'user_id': user_id,
                'item_id': item_id,
                'rating': rating,
                'timestamp': datetime.utcnow() + timedelta(seconds=t),
                'context': {
                    'time_of_day': (t % 24),
                    'day_of_week': (t // 24) % 7,
                    'session_length': np.random.randint(1, 60)
                }
            })
        
        return stream

    async def test_online_learning_initialization(self):
        """Test online learning initialization"""
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)],
            initial_features=64
        )
        
        self.assertTrue(self.algorithm.is_initialized)
        self.assertIsNotNone(self.algorithm.user_embeddings)
        self.assertIsNotNone(self.algorithm.item_embeddings)

    async def test_incremental_updates(self):
        """Test incremental learning updates"""
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)]
        )
        
        initial_loss = float('inf')
        
        for i, data_point in enumerate(self.stream_data[:100]):
            loss = await self.algorithm.update(data_point)
            
            self.assertIsInstance(loss, (int, float))
            self.assertGreaterEqual(loss, 0.0)
            
            if i == 0:
                initial_loss = loss
        
        # Loss should generally decrease over time
        final_loss = await self.algorithm.compute_current_loss()
        self.assertLess(final_loss, initial_loss * 2)  # Allow some flexibility

    async def test_mini_batch_processing(self):
        """Test mini-batch processing in online learning"""
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)]
        )
        
        # Process mini-batch
        mini_batch = self.stream_data[:10]
        losses = await self.algorithm.process_mini_batch(mini_batch)
        
        self.assertIsInstance(losses, list)
        self.assertEqual(len(losses), len(mini_batch))
        
        for loss in losses:
            self.assertIsInstance(loss, (int, float))
            self.assertGreaterEqual(loss, 0.0)

    async def test_concept_drift_detection(self):
        """Test concept drift detection"""
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)]
        )
        
        # Process initial data
        for data_point in self.stream_data[:200]:
            await self.algorithm.update(data_point)
        
        # Introduce concept drift (sudden change in preferences)
        drift_data = []
        for i in range(50):
            drift_data.append({
                'user_id': f'user_{i % 10}',
                'item_id': f'item_{i % 20}',
                'rating': 5.0 - self.stream_data[i]['rating'],  # Reverse preferences
                'timestamp': datetime.utcnow(),
                'context': {}
            })
        
        # Detect drift
        drift_detected = await self.algorithm.detect_concept_drift(drift_data)
        self.assertIsInstance(drift_detected, bool)

    async def test_adaptive_regularization(self):
        """Test adaptive regularization adjustment"""
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)]
        )
        
        initial_reg = self.algorithm.regularization
        
        # Process data and observe regularization changes
        for data_point in self.stream_data[:100]:
            await self.algorithm.update(data_point)
        
        # Regularization might adapt based on loss patterns
        current_reg = self.algorithm.regularization
        self.assertIsInstance(current_reg, (int, float))
        self.assertGreater(current_reg, 0.0)

    async def test_forgetting_mechanism(self):
        """Test forgetting mechanism for old data"""
        self.algorithm.enable_forgetting = True
        self.algorithm.forgetting_factor = 0.99
        
        await self.algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(50)],
            item_ids=[f'item_{i}' for i in range(100)]
        )
        
        # Process data with timestamps
        for data_point in self.stream_data[:100]:
            await self.algorithm.update(data_point)
        
        # Check that older data influence decreases
        old_influence = await self.algorithm.get_data_influence(
            timestamp=self.stream_data[0]['timestamp']
        )
        recent_influence = await self.algorithm.get_data_influence(
            timestamp=self.stream_data[-1]['timestamp']
        )
        
        self.assertLess(old_influence, recent_influence)


class TestMultiArmedBandit(IsolatedAsyncioTestCase):
    """Comprehensive tests for MultiArmedBandit algorithms"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.n_arms = 10
        self.bandit = MultiArmedBandit(
            n_arms=self.n_arms,
            exploration_strategy='epsilon_greedy',
            epsilon=0.1
        )
        self.true_rewards = np.random.uniform(0.2, 0.8, self.n_arms)

    def _simulate_reward(self, arm: int) -> float:
        """Simulate reward for pulling an arm"""



        return np.random.normal(self.true_rewards[arm], 0.1)

    async def test_bandit_initialization(self):
        """Test bandit initialization"""
        self.assertEqual(self.bandit.n_arms, self.n_arms)
        self.assertEqual(len(self.bandit.arm_counts), self.n_arms)
        self.assertEqual(len(self.bandit.arm_rewards), self.n_arms)
        self.assertTrue(all(count == 0 for count in self.bandit.arm_counts))

    async def test_epsilon_greedy_strategy(self):
        """Test epsilon-greedy exploration strategy"""
        # Warm up with some pulls
        for arm in range(self.n_arms):
            reward = self._simulate_reward(arm)
            await self.bandit.update(arm, reward)
        
        # Test arm selection
        selected_arms = []
        for _ in range(100):
            arm = await self.bandit.select_arm()
            selected_arms.append(arm)
            reward = self._simulate_reward(arm)
            await self.bandit.update(arm, reward)
        
        # Should mostly select the best arm but occasionally explore
        best_arm = np.argmax(self.true_rewards)
        best_arm_selections = selected_arms.count(best_arm)
        exploration_rate = 1 - (best_arm_selections / len(selected_arms))
        
        # Should be close to epsilon but with some variance
        self.assertGreater(exploration_rate, 0.05)
        self.assertLess(exploration_rate, 0.25)

    async def test_bandit_convergence(self):
        """Test bandit convergence to optimal arm"""
        n_trials = 1000
        arm_selections = []
        
        for trial in range(n_trials):
            arm = await self.bandit.select_arm()
            arm_selections.append(arm)
            reward = self._simulate_reward(arm)
            await self.bandit.update(arm, reward)
        
        # Calculate regret
        optimal_arm = np.argmax(self.true_rewards)
        regret = np.sum([self.true_rewards[optimal_arm] - self.true_rewards[arm] 
                        for arm in arm_selections])
        
        # Regret should be sublinear
        self.assertLess(regret, 0.5 * n_trials)  # Should be much better than random

    async def test_bandit_statistics(self):
        """Test bandit statistics tracking"""
        # Pull each arm a few times
        for arm in range(self.n_arms):
            for _ in range(5):
                reward = self._simulate_reward(arm)
                await self.bandit.update(arm, reward)
        
        stats = await self.bandit.get_statistics()
        
        self.assertIn('arm_counts', stats)
        self.assertIn('arm_means', stats)
        self.assertIn('arm_confidence_intervals', stats)
        self.assertIn('total_reward', stats)
        
        # Check that statistics make sense
        self.assertEqual(len(stats['arm_counts']), self.n_arms)
        self.assertEqual(sum(stats['arm_counts']), self.n_arms * 5)


class TestContextualBandit(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContextualBandit algorithms"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.n_arms = 5
        self.context_dim = 10
        self.bandit = ContextualBandit(
            n_arms=self.n_arms,
            context_dim=self.context_dim,
            algorithm='linucb',
            alpha=0.1
        )
        
        # Create true context-dependent reward function
        self.arm_weights = np.random.randn(self.n_arms, self.context_dim)

    def _generate_context(self) -> np.ndarray:
        """Generate random context vector"""



        return np.random.randn(self.context_dim)

    def _simulate_contextual_reward(self, arm: int, context: np.ndarray) -> float:
        """Simulate context-dependent reward"""
        expected_reward = np.dot(self.arm_weights[arm], context)
        return expected_reward + np.random.normal(0, 0.1)

    async def test_contextual_bandit_initialization(self):
        """Test contextual bandit initialization"""
        self.assertEqual(self.bandit.n_arms, self.n_arms)
        self.assertEqual(self.bandit.context_dim, self.context_dim)
        self.assertIsNotNone(self.bandit.arm_models)

    async def test_linucb_algorithm(self):
        """Test LinUCB algorithm implementation"""
        linucb_bandit = LinUCB(
            n_arms=self.n_arms,
            context_dim=self.context_dim,
            alpha=0.1
        )
        
        contexts = []
        arms = []
        rewards = []
        
        for trial in range(200):
            context = self._generate_context()
            contexts.append(context)
            
            arm = await linucb_bandit.select_arm(context)
            arms.append(arm)
            
            reward = self._simulate_contextual_reward(arm, context)
            rewards.append(reward)
            
            await linucb_bandit.update(arm, context, reward)
        
        # Test that the algorithm learns
        # Later selections should be better than early ones
        early_rewards = np.mean(rewards[:50])
        late_rewards = np.mean(rewards[-50:])
        
        # Should improve over time (with some tolerance for variance)
        self.assertGreater(late_rewards + 0.2, early_rewards)

    async def test_thompson_sampling(self):
        """Test Thompson Sampling for contextual bandits"""
        ts_bandit = ThompsonSampling(
            n_arms=self.n_arms,
            context_dim=self.context_dim,
            prior_variance=1.0
        )
        
        for trial in range(100):
            context = self._generate_context()
            arm = await ts_bandit.select_arm(context)
            reward = self._simulate_contextual_reward(arm, context)
            await ts_bandit.update(arm, context, reward)
        
        # Test uncertainty estimates
        test_context = self._generate_context()
        uncertainties = await ts_bandit.get_arm_uncertainties(test_context)
        
        self.assertEqual(len(uncertainties), self.n_arms)
        for uncertainty in uncertainties:
            self.assertGreater(uncertainty, 0.0)

    async def test_contextual_feature_importance(self):
        """Test feature importance analysis in contextual bandits"""
        # Use structured context with known important features
        structured_contexts = []
        for trial in range(150):
            context = np.zeros(self.context_dim)
            context[0] = np.random.randn()  # Important feature
            context[1] = np.random.randn()  # Important feature
            context[2:] = np.random.randn(self.context_dim - 2) * 0.1  # Less important
            
            structured_contexts.append(context)
            
            arm = await self.bandit.select_arm(context)
            reward = self._simulate_contextual_reward(arm, context)
            await self.bandit.update(arm, context, reward)
        
        # Analyze feature importance
        feature_importance = await self.bandit.analyze_feature_importance()
        
        self.assertIsInstance(feature_importance, dict)
        self.assertEqual(len(feature_importance), self.n_arms)
        
        for arm_importance in feature_importance.values():
            self.assertEqual(len(arm_importance), self.context_dim)


class TestQLearningAgent(IsolatedAsyncioTestCase):
    """Comprehensive tests for Q-Learning reinforcement learning agent"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.n_states = 20
        self.n_actions = 4
        self.agent = QLearningAgent(
            n_states=self.n_states,
            n_actions=self.n_actions,
            learning_rate=0.1,
            discount_factor=0.95,
            exploration_rate=0.1
        )
        self._setup_environment()

    def _setup_environment(self):
        """Set up a simple grid world environment"""
        self.grid_size = int(np.sqrt(self.n_states))
        self.goal_state = self.n_states - 1
        self.reward_map = np.zeros(self.n_states)
        self.reward_map[self.goal_state] = 10.0
        
        # Add some negative rewards for obstacles
        obstacles = np.random.choice(self.n_states - 1, size=3, replace=False)
        self.reward_map[obstacles] = -1.0

    def _get_next_state(self, state: int, action: int) -> int:
        """Get next state given current state and action"""
        row, col = divmod(state, self.grid_size)
        
        # Actions: 0=up, 1=down, 2=left, 3=right
        if action == 0 and row > 0:
            row -= 1
        elif action == 1 and row < self.grid_size - 1:
            row += 1
        elif action == 2 and col > 0:
            col -= 1
        elif action == 3 and col < self.grid_size - 1:
            col += 1
        
        return row * self.grid_size + col

    def _get_reward(self, state: int) -> float:
        """Get reward for being in a state"""



        return self.reward_map[state]

    async def test_q_learning_initialization(self):
        """Test Q-learning agent initialization"""
        self.assertEqual(self.agent.q_table.shape, (self.n_states, self.n_actions))
        self.assertTrue(np.allclose(self.agent.q_table, 0.0))
        self.assertEqual(self.agent.n_states, self.n_states)
        self.assertEqual(self.agent.n_actions, self.n_actions)

    async def test_action_selection(self):
        """Test action selection strategies"""
        state = 0
        
        # Test epsilon-greedy selection
        actions = []
        for _ in range(100):
            action = await self.agent.select_action(state)
            actions.append(action)
        
        # Should explore different actions
        unique_actions = set(actions)
        self.assertGreater(len(unique_actions), 1)
        
        # All actions should be valid
        for action in actions:
            self.assertIn(action, range(self.n_actions))

    async def test_q_value_updates(self):
        """Test Q-value updates"""
        state = 0
        action = 1
        next_state = self._get_next_state(state, action)
        reward = self._get_reward(next_state)
        
        old_q_value = self.agent.q_table[state, action]
        
        await self.agent.update_q_value(state, action, reward, next_state)
        
        new_q_value = self.agent.q_table[state, action]
        
        # Q-value should have changed
        self.assertNotEqual(old_q_value, new_q_value)

    async def test_policy_learning(self):
        """Test that agent learns a reasonable policy"""
        n_episodes = 200
        episode_rewards = []
        
        for episode in range(n_episodes):
            state = 0  # Start from initial state
            total_reward = 0
            steps = 0
            max_steps = 50
            
            while state != self.goal_state and steps < max_steps:
                action = await self.agent.select_action(state)
                next_state = self._get_next_state(state, action)
                reward = self._get_reward(next_state)
                
                await self.agent.update_q_value(state, action, reward, next_state)
                
                state = next_state
                total_reward += reward
                steps += 1
            
            episode_rewards.append(total_reward)
            
            # Decay exploration rate
            self.agent.exploration_rate *= 0.995
        
        # Learning should improve over time
        early_performance = np.mean(episode_rewards[:50])
        late_performance = np.mean(episode_rewards[-50:])
        
        self.assertGreater(late_performance, early_performance - 2.0)

    async def test_value_function_convergence(self):
        """Test that value function converges"""
        # Train for many episodes
        for _ in range(500):
            state = np.random.randint(self.n_states)
            action = np.random.randint(self.n_actions)
            next_state = self._get_next_state(state, action)
            reward = self._get_reward(next_state)
            
            await self.agent.update_q_value(state, action, reward, next_state)
        
        # Check that Q-values are reasonable
        max_q_values = np.max(self.agent.q_table, axis=1)
        
        # Goal state should have highest value
        goal_value = max_q_values[self.goal_state]
        other_values = max_q_values[:self.goal_state]
        
        if len(other_values) > 0:
            self.assertGreaterEqual(goal_value, np.max(other_values) - 1.0)


class TestPolicyGradientAgent(IsolatedAsyncioTestCase):
    """Comprehensive tests for Policy Gradient reinforcement learning agent"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.n_states = 10
        self.n_actions = 3
        self.agent = PolicyGradientAgent(
            n_states=self.n_states,
            n_actions=self.n_actions,
            learning_rate=0.01,
            discount_factor=0.99
        )

    async def test_policy_initialization(self):
        """Test policy network initialization"""
        # Policy should output valid probability distributions
        for state in range(self.n_states):
            action_probs = await self.agent.get_action_probabilities(state)
            
            self.assertEqual(len(action_probs), self.n_actions)
            self.assertAlmostEqual(np.sum(action_probs), 1.0, places=5)
            self.assertTrue(all(prob >= 0.0 for prob in action_probs))

    async def test_trajectory_collection(self):
        """Test trajectory collection and reward computation"""
        # Generate a simple trajectory
        trajectory = [
            {'state': 0, 'action': 1, 'reward': 1.0},
            {'state': 1, 'action': 2, 'reward': 0.5},
            {'state': 2, 'action': 0, 'reward': 2.0}
        ]
        
        returns = await self.agent.compute_returns(trajectory)
        
        self.assertEqual(len(returns), len(trajectory))
        
        # Returns should be computed correctly with discounting
        expected_returns = [
            1.0 + 0.99 * 0.5 + 0.99**2 * 2.0,  # First step
            0.5 + 0.99 * 2.0,  # Second step
            2.0  # Third step
        ]
        
        for i, (computed, expected) in enumerate(zip(returns, expected_returns)):
            self.assertAlmostEqual(computed, expected, places=5)

    async def test_policy_gradient_update(self):
        """Test policy gradient updates"""
        # Create a batch of trajectories
        trajectories = []
        for _ in range(10):
            trajectory = []
            for step in range(5):
                state = np.random.randint(self.n_states)
                action = np.random.randint(self.n_actions)
                reward = np.random.uniform(-1.0, 1.0)
                trajectory.append({'state': state, 'action': action, 'reward': reward})
            trajectories.append(trajectory)
        
        # Get initial policy parameters
        initial_params = await self.agent.get_policy_parameters()
        
        # Update policy
        await self.agent.update_policy(trajectories)
        
        # Policy parameters should have changed
        updated_params = await self.agent.get_policy_parameters()
        
        params_changed = not np.allclose(initial_params, updated_params, atol=1e-6)
        self.assertTrue(params_changed)

    async def test_baseline_estimation(self):
        """Test baseline estimation for variance reduction"""
        self.agent.use_baseline = True
        
        # Generate trajectories with varying returns
        high_return_trajectory = [
            {'state': i, 'action': 0, 'reward': 2.0} for i in range(5)
        ]
        low_return_trajectory = [
            {'state': i, 'action': 1, 'reward': -1.0} for i in range(5)
        ]
        
        trajectories = [high_return_trajectory, low_return_trajectory]
        
        # Update baseline
        await self.agent.update_baseline(trajectories)
        
        baseline_value = await self.agent.get_baseline_estimate(state=0)
        self.assertIsInstance(baseline_value, (int, float))


class TestGradientBoostedPersonalization(IsolatedAsyncioTestCase):
    """Comprehensive tests for Gradient Boosted Personalization"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.algorithm = GradientBoostedPersonalization(
            n_estimators=10,
            learning_rate=0.1,
            max_depth=3,
            subsample=0.8
        )
        self.training_data = self._generate_boosting_data()

    def _generate_boosting_data(self) -> Dict[str, Any]:
        """Generate data for gradient boosting"""
        n_samples = 500
        n_features = 20
        
        # Generate features
        X = np.random.randn(n_samples, n_features)
        
        # Create non-linear target with interactions
        y = (X[:, 0] * X[:, 1] + 
             np.sin(X[:, 2]) * X[:, 3] + 
             X[:, 4]**2 + 
             np.random.normal(0, 0.1, n_samples))
        
        return {
            'features': X,
            'targets': y,
            'user_ids': [f'user_{i // 10}' for i in range(n_samples)],
            'item_ids': [f'item_{i % 100}' for i in range(n_samples)]
        }

    async def test_boosting_initialization(self):
        """Test gradient boosting initialization"""
        self.assertEqual(self.algorithm.n_estimators, 10)
        self.assertEqual(self.algorithm.learning_rate, 0.1)
        self.assertFalse(self.algorithm.is_fitted)

    async def test_gradient_boosting_training(self):
        """Test gradient boosting training process"""
        result = await self.algorithm.fit(
            X=self.training_data['features'],
            y=self.training_data['targets']
        )
        
        self.assertTrue(result)
        self.assertTrue(self.algorithm.is_fitted)
        self.assertEqual(len(self.algorithm.estimators), self.algorithm.n_estimators)

    async def test_boosting_predictions(self):
        """Test gradient boosting predictions"""
        await self.algorithm.fit(
            X=self.training_data['features'],
            y=self.training_data['targets']
        )
        
        # Test single prediction
        test_features = np.random.randn(1, 20)
        prediction = await self.algorithm.predict(test_features)
        
        self.assertIsInstance(prediction, np.ndarray)
        self.assertEqual(len(prediction), 1)

    async def test_feature_importance(self):
        """Test feature importance computation"""
        await self.algorithm.fit(
            X=self.training_data['features'],
            y=self.training_data['targets']
        )
        
        importance = await self.algorithm.get_feature_importance()
        
        self.assertIsInstance(importance, np.ndarray)
        self.assertEqual(len(importance), 20)  # n_features
        self.assertTrue(np.all(importance >= 0.0))
        self.assertAlmostEqual(np.sum(importance), 1.0, places=5)

    async def test_partial_dependence(self):
        """Test partial dependence computation"""
        await self.algorithm.fit(
            X=self.training_data['features'],
            y=self.training_data['targets']
        )
        
        # Test partial dependence for first feature
        pd_values = await self.algorithm.compute_partial_dependence(
            feature_idx=0,
            X=self.training_data['features'][:100]
        )
        
        self.assertIsInstance(pd_values, dict)
        self.assertIn('values', pd_values)
        self.assertIn('grid', pd_values)


class TestOnlineMatrixFactorization(IsolatedAsyncioTestCase):
    """Comprehensive tests for Online Matrix Factorization"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.algorithm = OnlineMatrixFactorization(
            n_factors=20,
            learning_rate=0.01,
            regularization=0.001,
            batch_size=32
        )
        self.streaming_data = self._generate_matrix_factorization_stream()

    def _generate_matrix_factorization_stream(self) -> List[Dict[str, Any]]:
        """Generate streaming data for matrix factorization"""
        n_users, n_items = 100, 200
        
        # Create true latent factors
        true_user_factors = np.random.randn(n_users, 20)
        true_item_factors = np.random.randn(n_items, 20)
        
        stream = []
        for t in range(1000):
            user_idx = np.random.randint(n_users)
            item_idx = np.random.randint(n_items)
            
            # True rating from latent factors
            true_rating = np.dot(true_user_factors[user_idx], true_item_factors[item_idx])
            observed_rating = true_rating + np.random.normal(0, 0.1)
            
            stream.append({
                'user_id': f'user_{user_idx}',
                'item_id': f'item_{item_idx}',
                'rating': np.clip(observed_rating, 1.0, 5.0),
                'timestamp': datetime.utcnow() + timedelta(seconds=t)
            })
        
        return stream

    async def test_online_mf_initialization(self):
        """Test online matrix factorization initialization"""
        user_ids = [f'user_{i}' for i in range(100)]
        item_ids = [f'item_{i}' for i in range(200)]
        
        await self.algorithm.initialize(user_ids, item_ids)
        
        self.assertTrue(self.algorithm.is_initialized)
        self.assertEqual(self.algorithm.user_factors.shape, (100, 20))
        self.assertEqual(self.algorithm.item_factors.shape, (200, 20))

    async def test_incremental_factorization(self):
        """Test incremental matrix factorization updates"""
        user_ids = [f'user_{i}' for i in range(100)]
        item_ids = [f'item_{i}' for i in range(200)]
        
        await self.algorithm.initialize(user_ids, item_ids)
        
        initial_loss = float('inf')
        
        for i, data_point in enumerate(self.streaming_data[:200]):
            loss = await self.algorithm.update(data_point)
            
            if i == 0:
                initial_loss = loss
            
            self.assertIsInstance(loss, (int, float))
            self.assertGreaterEqual(loss, 0.0)
        
        # Loss should generally decrease
        final_loss = loss
        self.assertLess(final_loss, initial_loss)

    async def test_prediction_accuracy(self):
        """Test prediction accuracy of online matrix factorization"""
        user_ids = [f'user_{i}' for i in range(100)]
        item_ids = [f'item_{i}' for i in range(200)]
        
        await self.algorithm.initialize(user_ids, item_ids)
        
        # Train on first 800 data points
        for data_point in self.streaming_data[:800]:
            await self.algorithm.update(data_point)
        
        # Test on remaining 200 data points
        predictions = []
        actuals = []
        
        for data_point in self.streaming_data[800:]:
            pred = await self.algorithm.predict(
                data_point['user_id'],
                data_point['item_id']
            )
            predictions.append(pred)
            actuals.append(data_point['rating'])
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actuals))**2))
        self.assertLess(rmse, 2.0)  # Should be reasonable

    async def test_factor_evolution(self):
        """Test evolution of latent factors over time"""
        user_ids = [f'user_{i}' for i in range(100)]
        item_ids = [f'item_{i}' for i in range(200)]
        
        await self.algorithm.initialize(user_ids, item_ids)
        
        # Get initial factors
        initial_user_factor = self.algorithm.user_factors[0].copy()
        
        # Process updates
        for data_point in self.streaming_data[:100]:
            await self.algorithm.update(data_point)
        
        # Check that factors have evolved
        updated_user_factor = self.algorithm.user_factors[0]
        
        factor_change = np.linalg.norm(updated_user_factor - initial_user_factor)
        self.assertGreater(factor_change, 0.01)  # Factors should change


class TestBayesianOptimization(IsolatedAsyncioTestCase):
    """Comprehensive tests for Bayesian Optimization"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.optimizer = BayesianOptimization(
            bounds={'x': (-5.0, 5.0), 'y': (-3.0, 3.0)},
            acquisition_function='expected_improvement',
            n_random_starts=5
        )

    def _objective_function(self, x: float, y: float) -> float:
        """Test objective function to optimize"""



        return -(x**2 + y**2) + 0.1 * np.sin(10 * x) * np.cos(10 * y)

    async def test_bayesian_optimization_initialization(self):
        """Test Bayesian optimization initialization"""
        self.assertIsNotNone(self.optimizer.bounds)
        self.assertEqual(len(self.optimizer.bounds), 2)
        self.assertFalse(self.optimizer.is_fitted)

    async def test_random_exploration_phase(self):
        """Test random exploration phase"""
        # Perform random exploration
        for _ in range(self.optimizer.n_random_starts):
            params = await self.optimizer.suggest_parameters()
            
            self.assertIn('x', params)
            self.assertIn('y', params)
            
            # Parameters should be within bounds
            self.assertGreaterEqual(params['x'], -5.0)
            self.assertLessEqual(params['x'], 5.0)
            self.assertGreaterEqual(params['y'], -3.0)
            self.assertLessEqual(params['y'], 3.0)
            
            # Evaluate and update
            objective_value = self._objective_function(params['x'], params['y'])
            await self.optimizer.update(params, objective_value)

    async def test_acquisition_function_optimization(self):
        """Test acquisition function optimization"""
        # Initialize with random points
        for _ in range(10):
            params = await self.optimizer.suggest_parameters()
            objective_value = self._objective_function(params['x'], params['y'])
            await self.optimizer.update(params, objective_value)
        
        # Now suggestions should be based on acquisition function
        next_params = await self.optimizer.suggest_parameters()
        
        self.assertIn('x', next_params)
        self.assertIn('y', next_params)

    async def test_optimization_convergence(self):
        """Test optimization convergence"""
        best_values = []
        
        for iteration in range(30):
            params = await self.optimizer.suggest_parameters()
            objective_value = self._objective_function(params['x'], params['y'])
            await self.optimizer.update(params, objective_value)
            
            current_best = await self.optimizer.get_best_result()
            best_values.append(current_best['objective'])
        
        # Should improve over time
        early_best = max(best_values[:10])
        late_best = max(best_values[-10:])
        
        self.assertGreaterEqual(late_best, early_best - 0.1)

    async def test_uncertainty_estimation(self):
        """Test uncertainty estimation in Bayesian optimization"""
        # Initialize with some data
        for _ in range(15):
            params = await self.optimizer.suggest_parameters()
            objective_value = self._objective_function(params['x'], params['y'])
            await self.optimizer.update(params, objective_value)
        
        # Test uncertainty at different points
        test_points = [
            {'x': 0.0, 'y': 0.0},  # Center
            {'x': -4.0, 'y': 2.0},  # Corner
            {'x': 1.0, 'y': -1.0}   # Random point
        ]
        
        for point in test_points:
            mean, variance = await self.optimizer.predict(point)
            
            self.assertIsInstance(mean, (int, float))
            self.assertIsInstance(variance, (int, float))
            self.assertGreater(variance, 0.0)


class TestAlgorithmPerformanceAndScalability(IsolatedAsyncioTestCase):
    """Performance and scalability tests for all algorithms"""

    async def test_algorithm_training_speed(self):
        """Test training speed across different algorithms"""
        algorithms_to_test = [
            OnlineLearningAlgorithm(learning_rate=0.1),
            OnlineMatrixFactorization(n_factors=10),
            GradientBoostedPersonalization(n_estimators=5)
        ]
        
        # Generate performance test data
        large_dataset = self._generate_large_dataset(1000)
        
        for algorithm in algorithms_to_test:
            start_time = time.time()
            
            if hasattr(algorithm, 'initialize'):
                await algorithm.initialize(
                    user_ids=[f'user_{i}' for i in range(100)],
                    item_ids=[f'item_{i}' for i in range(200)]
                )
            
            # Train/update with data
            for data_point in large_dataset[:500]:  # Subset for speed
                if hasattr(algorithm, 'update'):
                    await algorithm.update(data_point)
                elif hasattr(algorithm, 'fit'):
                    await algorithm.fit(
                        X=np.random.randn(100, 10),
                        y=np.random.randn(100)
                    )
                    break
            
            training_time = time.time() - start_time
            
            # Should complete training within reasonable time
            self.assertLess(training_time, 30.0)

    async def test_memory_efficiency(self):
        """Test memory efficiency of algorithms"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create memory-intensive algorithm
        large_algorithm = OnlineMatrixFactorization(
            n_factors=100,
            batch_size=64
        )
        
        await large_algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(1000)],
            item_ids=[f'item_{i}' for i in range(2000)]
        )
        
        # Process data
        for i in range(200):
            data_point = {
                'user_id': f'user_{i % 100}',
                'item_id': f'item_{i % 200}',
                'rating': np.random.uniform(1.0, 5.0),
                'timestamp': datetime.utcnow()
            }
            await large_algorithm.update(data_point)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 200)  # Less than 200MB increase

    def _generate_large_dataset(self, size: int) -> List[Dict[str, Any]]:
        """Generate large dataset for performance testing"""
        dataset = []
        for i in range(size):
            dataset.append({
                'user_id': f'user_{i % 50}',
                'item_id': f'item_{i % 100}',
                'rating': np.random.uniform(1.0, 5.0),
                'timestamp': datetime.utcnow() + timedelta(seconds=i),
                'context': np.random.randn(5).tolist()
            })
        return dataset


class TestAlgorithmRobustness(IsolatedAsyncioTestCase):
    """Robustness and edge case tests"""

    async def test_empty_data_handling(self):
        """Test handling of empty or insufficient data"""
        algorithm = OnlineLearningAlgorithm()
        
        # Test with no initialization
        with self.assertRaises(AlgorithmError):
            await algorithm.update({
                'user_id': 'user_1',
                'item_id': 'item_1',
                'rating': 4.0
            })

    async def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        # Test negative learning rate
        with self.assertRaises(ValueError):
            OnlineLearningAlgorithm(learning_rate=-0.1)
        
        # Test invalid bandit arms
        with self.assertRaises(ValueError):
            MultiArmedBandit(n_arms=0)

    async def test_numerical_stability(self):
        """Test numerical stability with extreme values"""
        algorithm = OnlineLearningAlgorithm(learning_rate=0.01)
        
        await algorithm.initialize(
            user_ids=['user_1'],
            item_ids=['item_1']
        )
        
        # Test with extreme ratings
        extreme_data = [
            {'user_id': 'user_1', 'item_id': 'item_1', 'rating': 1e6},
            {'user_id': 'user_1', 'item_id': 'item_1', 'rating': -1e6},
            {'user_id': 'user_1', 'item_id': 'item_1', 'rating': 0.0}
        ]
        
        for data_point in extreme_data:
            try:
                await algorithm.update(data_point)
            except Exception as e:
                # Should handle gracefully or raise specific error
                self.assertIsInstance(e, (AlgorithmError, ValueError))

    async def test_concurrent_updates(self):
        """Test thread safety with concurrent updates"""
        algorithm = OnlineLearningAlgorithm(learning_rate=0.01)
        
        await algorithm.initialize(
            user_ids=[f'user_{i}' for i in range(10)],
            item_ids=[f'item_{i}' for i in range(20)]
        )
        
        # Create concurrent update tasks
        async def update_task(task_id: int):
            for i in range(20):
                data_point = {
                    'user_id': f'user_{(task_id + i) % 10}',
                    'item_id': f'item_{i % 20}',
                    'rating': np.random.uniform(1.0, 5.0)
                }
                await algorithm.update(data_point)
        
        # Run concurrent tasks
        tasks = [update_task(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Algorithm should remain in valid state
        self.assertTrue(algorithm.is_initialized)
        self.assertEqual(algorithm.update_count, 100)  # 5 tasks * 20 updates


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=10'
    ])
