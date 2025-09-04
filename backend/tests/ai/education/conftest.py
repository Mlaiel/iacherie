"""
Pytest Configuration for Education AI Tests
==========================================

Advanced test configuration with fixtures, mocks, and test utilities.
Provides enterprise-grade testing infrastructure for education AI components.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import tempfile
import shutil
import os
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

# Configure test logging
logging.basicConfig(level=logging.DEBUG)

# Import test configuration
from . import (
    EDUCATION_TEST_CONFIG, 
    EDUCATION_TEST_DATA_CONFIG, 
    MOCK_STUDENTS,
    MOCK_COURSE_REQUIREMENTS,
    MOCK_ASSESSMENT_DATA
)

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def education_test_config():
    """Global education test configuration fixture"""
    return EDUCATION_TEST_CONFIG.copy()


@pytest.fixture(scope="session") 
def education_test_data_config():
    """Education test data configuration fixture"""
    return EDUCATION_TEST_DATA_CONFIG.copy()


@pytest.fixture(scope="session")
def mock_students():
    """Mock student data fixture"""
    return MOCK_STUDENTS.copy()


@pytest.fixture(scope="session")
def mock_course_requirements():
    """Mock course requirements fixture"""
    return MOCK_COURSE_REQUIREMENTS.copy()


@pytest.fixture(scope="session")
def mock_assessment_data():
    """Mock assessment data fixture"""
    return MOCK_ASSESSMENT_DATA.copy()


@pytest.fixture
def temp_education_dir():
    """Temporary directory for education test files"""
    temp_dir = tempfile.mkdtemp(prefix="education_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_student_visual():
    """Sample visual learner student data"""
    return {
        "user_id": "visual_test_001",
        "name": "Visual Test Student",
        "learning_preferences": {
            "visual_content": 5,
            "diagrams": 4,
            "audio_content": 2,
            "hands_on": 2
        },
        "experience_level": "intermediate",
        "strengths": ["pattern_recognition", "spatial_reasoning"],
        "weaknesses": ["auditory_processing"],
        "interests": ["art", "design", "mathematics"],
        "learning_goals": ["improve_math_skills", "visual_design_fundamentals"]
    }


@pytest.fixture
def sample_student_auditory():
    """Sample auditory learner student data"""
    return {
        "user_id": "auditory_test_001",
        "name": "Auditory Test Student", 
        "learning_preferences": {
            "visual_content": 2,
            "diagrams": 1,
            "audio_content": 5,
            "discussions": 5
        },
        "experience_level": "beginner",
        "strengths": ["listening_skills", "verbal_communication"],
        "weaknesses": ["visual_processing", "note_taking"],
        "interests": ["music", "languages", "history"],
        "learning_goals": ["language_mastery", "communication_skills"]
    }


@pytest.fixture
def sample_course_math():
    """Sample mathematics course requirements"""
    return {
        "title": "Intermediate Mathematics",
        "subject_area": "mathematics",
        "difficulty_level": "intermediate",
        "duration_weeks": 10,
        "target_audience": "students",
        "description": "Comprehensive mathematics course covering algebra and geometry"
    }


@pytest.fixture
def sample_course_programming():
    """Sample programming course requirements"""
    return {
        "title": "Python Programming Fundamentals",
        "subject_area": "programming",
        "difficulty_level": "beginner", 
        "duration_weeks": 8,
        "target_audience": "developers",
        "description": "Introduction to Python programming language and basic concepts"
    }


@pytest.fixture
def sample_formative_assessment():
    """Sample formative assessment data"""
    return {
        "type": "formative",
        "responses": [
            {"question_id": "q1", "answer": "correct", "correct": True, "time_spent": 30},
            {"question_id": "q2", "answer": "incorrect", "correct": False, "time_spent": 45},
            {"question_id": "q3", "answer": "correct", "correct": True, "time_spent": 25},
            {"question_id": "q4", "answer": "correct", "correct": True, "time_spent": 35},
            {"question_id": "q5", "answer": "partial", "correct": False, "time_spent": 60}
        ],
        "duration_minutes": 12,
        "question_count": 5,
        "completion_rate": 1.0,
        "difficulty": "intermediate"
    }


@pytest.fixture
def sample_summative_assessment():
    """Sample summative assessment data"""
    return {
        "type": "summative",
        "responses": [
            {"question_id": "q1", "answer": "correct", "correct": True, "time_spent": 90},
            {"question_id": "q2", "answer": "correct", "correct": True, "time_spent": 120},
            {"question_id": "q3", "answer": "incorrect", "correct": False, "time_spent": 180},
            {"question_id": "q4", "answer": "correct", "correct": True, "time_spent": 100},
            {"question_id": "q5", "answer": "correct", "correct": True, "time_spent": 110},
            {"question_id": "q6", "answer": "partial", "correct": False, "time_spent": 200},
            {"question_id": "q7", "answer": "correct", "correct": True, "time_spent": 85},
            {"question_id": "q8", "answer": "correct", "correct": True, "time_spent": 95}
        ],
        "duration_minutes": 45,
        "question_count": 8,
        "completion_rate": 1.0,
        "difficulty": "advanced"
    }


@pytest.fixture
def mock_progress_data():
    """Mock learning progress data"""
    return {
        "completion_percentage": 75,
        "sessions_completed": 18,
        "total_sessions": 24,
        "average_score": 82,
        "time_spent_hours": 36,
        "last_activity": datetime.utcnow() - timedelta(days=1),
        "competency_scores": {
            "knowledge_retention": 85,
            "application_skills": 78,
            "critical_thinking": 80,
            "problem_solving": 88
        }
    }


@pytest.fixture
def mock_database():
    """Mock database connection and operations"""
    db_mock = Mock()
    
    # Mock common database operations
    db_mock.save_learning_profile = AsyncMock(return_value={"status": "success"})
    db_mock.save_course = AsyncMock(return_value={"status": "success"})
    db_mock.save_assessment_result = AsyncMock(return_value={"status": "success"})
    db_mock.get_progress_data = AsyncMock(return_value={
        "completion_percentage": 65,
        "sessions_completed": 15,
        "total_sessions": 20
    })
    
    return db_mock


@pytest.fixture
def mock_ai_models():
    """Mock AI/ML model connections"""
    models_mock = Mock()
    
    # Mock model inference calls
    models_mock.analyze_learning_style = AsyncMock(return_value="visual")
    models_mock.predict_performance = AsyncMock(return_value=0.85)
    models_mock.generate_content = AsyncMock(return_value="Generated educational content")
    models_mock.assess_competency = AsyncMock(return_value=75.5)
    
    return models_mock


@pytest.fixture
def mock_external_apis():
    """Mock external API services"""
    apis_mock = Mock()
    
    # Mock external educational services
    apis_mock.content_api = Mock()
    apis_mock.content_api.get_resources = AsyncMock(return_value=[
        {"title": "Resource 1", "type": "video", "duration": 600},
        {"title": "Resource 2", "type": "article", "words": 800}
    ])
    
    apis_mock.assessment_api = Mock() 
    apis_mock.assessment_api.validate_questions = AsyncMock(return_value=True)
    
    return apis_mock


@pytest.fixture(autouse=True)
def setup_test_environment(education_test_config):
    """Automatically setup test environment for each test"""
    # Set test-specific environment variables
    os.environ["EDUCATION_TEST_MODE"] = "true"
    os.environ["EDUCATION_LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup after test
    os.environ.pop("EDUCATION_TEST_MODE", None)
    os.environ.pop("EDUCATION_LOG_LEVEL", None)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Performance testing fixtures

@pytest.fixture
def performance_benchmark():
    """Performance benchmarking utilities"""
    import time
    
    class PerformanceBenchmark:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.perf_counter()
            
        def stop(self):
            self.end_time = time.perf_counter()
            
        def duration_ms(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return 0
            
        def assert_under_threshold(self, threshold_ms):
            duration = self.duration_ms()
            assert duration < threshold_ms, f"Operation took {duration}ms, expected < {threshold_ms}ms"
    
    return PerformanceBenchmark()


# Data validation fixtures

@pytest.fixture
def data_validator():
    """Data validation utilities"""
    
    class DataValidator:
        @staticmethod
        def validate_learning_profile(profile):
            """Validate learning profile structure"""
            required_fields = ["user_id", "learning_style", "skill_level", "strengths", "weaknesses"]
            return all(hasattr(profile, field) for field in required_fields)
        
        @staticmethod
        def validate_course_structure(course):
            """Validate course structure"""
            required_fields = ["course_id", "title", "modules", "learning_objectives"]
            return all(hasattr(course, field) for field in required_fields)
        
        @staticmethod
        def validate_assessment_result(result):
            """Validate assessment result structure"""
            required_fields = ["assessment_id", "user_id", "score", "competencies"]
            return all(hasattr(result, field) for field in required_fields)
    
    return DataValidator()


# Mock services for integration testing

@pytest.fixture
def mock_education_services():
    """Mock education-related services"""
    services = Mock()
    
    # Mock notification service
    services.notification = Mock()
    services.notification.send_progress_update = AsyncMock(return_value=True)
    services.notification.send_achievement_notification = AsyncMock(return_value=True)
    
    # Mock analytics service
    services.analytics = Mock()
    services.analytics.track_learning_event = AsyncMock(return_value={"event_id": "tracked"})
    services.analytics.generate_insights = AsyncMock(return_value=["insight1", "insight2"])
    
    # Mock content recommendation service
    services.recommendations = Mock()
    services.recommendations.get_personalized_content = AsyncMock(return_value=[
        {"content_id": "rec1", "relevance": 0.9},
        {"content_id": "rec2", "relevance": 0.8}
    ])
    
    return services


# Test data generators

@pytest.fixture
def test_data_generator():
    """Generate test data dynamically"""
    
    class TestDataGenerator:
        @staticmethod
        def generate_student_data(learning_style="visual", skill_level="intermediate"):
            """Generate student data with specified parameters"""
            return {
                "user_id": f"test_user_{learning_style}_{skill_level}",
                "name": f"Test {learning_style.title()} Student",
                "learning_preferences": TestDataGenerator._get_learning_preferences(learning_style),
                "experience_level": skill_level,
                "strengths": ["analytical_thinking", "persistence"],
                "weaknesses": ["time_management"],
                "interests": ["science", "technology"],
                "learning_goals": ["skill_improvement", "knowledge_expansion"]
            }
        
        @staticmethod
        def _get_learning_preferences(style):
            """Get learning preferences based on style"""
            preferences = {
                "visual": {"visual_content": 5, "diagrams": 4, "audio_content": 2},
                "auditory": {"audio_content": 5, "discussions": 4, "visual_content": 2},
                "kinesthetic": {"hands_on": 5, "interactive": 4, "text_content": 2},
                "reading_writing": {"text_content": 5, "reading": 4, "audio_content": 2}
            }
            return preferences.get(style, {"visual_content": 3, "audio_content": 3, "hands_on": 3})
        
        @staticmethod
        def generate_assessment_responses(correct_percentage=0.8, question_count=10):
            """Generate assessment responses with specified success rate"""
            import random
            responses = []
            
            for i in range(question_count):
                is_correct = random.random() < correct_percentage
                response = {
                    "question_id": f"q{i+1}",
                    "answer": "correct_answer" if is_correct else "incorrect_answer",
                    "correct": is_correct,
                    "time_spent": random.randint(30, 120)
                }
                responses.append(response)
            
            return responses
    
    return TestDataGenerator()


# Cleanup fixtures

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test"""
    test_files = []
    
    yield test_files
    
    # Cleanup any files created during tests
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.warning(f"Failed to cleanup test file {file_path}: {e}")


# Configuration for pytest-asyncio
@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async test backend"""
    return "asyncio"


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "education: mark test as education-specific test"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add education marker to all tests in this module
        item.add_marker(pytest.mark.education)
        
        # Add markers based on test name patterns
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)
        elif "integration" in item.name or "workflow" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)