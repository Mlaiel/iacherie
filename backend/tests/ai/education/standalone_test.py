#!/usr/bin/env python3
"""
Standalone Education AI Test Suite
=================================

Simple, comprehensive test suite for Education AI Service that runs independently
without relying on complex test infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.ai.education import (
    EducationAgents, 
    LearningStyle, 
    DifficultyLevel, 
    AssessmentType,
    LearningProfile,
    CourseStructure,
    AssessmentResult
)

class EducationTestRunner:
    """Simple test runner for education AI functionality"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.agents = EducationAgents()
    
    def assert_test(self, condition, test_name, message=""):
        """Simple assertion with test tracking"""
        try:
            if condition:
                print(f"✅ {test_name}")
                self.passed += 1
            else:
                print(f"❌ {test_name}: {message}")
                self.failed += 1
                self.errors.append(f"{test_name}: {message}")
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")
            self.failed += 1
            self.errors.append(f"{test_name}: Exception - {e}")
    
    async def test_learning_profile_creation(self):
        """Test learning profile creation for different learner types"""
        print("\n🧑‍🎓 Testing Learning Profile Creation...")
        
        # Test visual learner
        visual_data = {
            'user_id': 'visual_001',
            'learning_preferences': {'visual_content': 5, 'diagrams': 4, 'audio_content': 2},
            'experience_level': 'intermediate',
            'strengths': ['pattern_recognition'],
            'weaknesses': ['auditory_processing'],
            'interests': ['art', 'design'],
            'learning_goals': ['improve_math']
        }
        
        profile = await self.agents.create_learning_profile(visual_data)
        self.assert_test(isinstance(profile, LearningProfile), "Visual learner profile creation")
        self.assert_test(profile.learning_style == LearningStyle.VISUAL, "Visual learning style detection")
        self.assert_test(profile.skill_level == DifficultyLevel.INTERMEDIATE, "Skill level assessment")
        
        # Test auditory learner
        auditory_data = {
            'user_id': 'auditory_001',
            'learning_preferences': {'audio_content': 5, 'discussions': 5, 'visual_content': 1},
            'experience_level': 'beginner',
            'strengths': ['listening'],
            'weaknesses': ['visual_processing'],
            'interests': ['music'],
            'learning_goals': ['communication']
        }
        
        auditory_profile = await self.agents.create_learning_profile(auditory_data)
        self.assert_test(auditory_profile.learning_style == LearningStyle.AUDITORY, "Auditory learning style detection")
        self.assert_test(auditory_profile.skill_level == DifficultyLevel.BEGINNER, "Beginner skill level assessment")
        
        # Test multimodal learner
        multimodal_data = {
            'user_id': 'multimodal_001',
            'learning_preferences': {'visual_content': 3, 'audio_content': 3, 'hands_on': 3},
            'experience_level': 'advanced',
            'strengths': ['adaptability'],
            'weaknesses': ['focus'],
            'interests': ['science'],
            'learning_goals': ['expertise']
        }
        
        multimodal_profile = await self.agents.create_learning_profile(multimodal_data)
        self.assert_test(multimodal_profile.learning_style == LearningStyle.MULTIMODAL, "Multimodal learning style detection")
        
        return profile  # Return for use in other tests
    
    async def test_personalized_tutoring(self, learning_profile):
        """Test personalized tutoring session generation"""
        print("\n👨‍🏫 Testing Personalized Tutoring...")
        
        session_data = {"content": {"topic": "algebra", "difficulty": "intermediate"}}
        tutoring_session = await self.agents.provide_personalized_tutoring(
            learning_profile, "mathematics", session_data
        )
        
        self.assert_test(isinstance(tutoring_session, dict), "Tutoring session generation")
        self.assert_test("session_id" in tutoring_session, "Session ID generation")
        self.assert_test("exercises" in tutoring_session, "Exercise generation")
        self.assert_test(len(tutoring_session["exercises"]) == 5, "Correct number of exercises")
        self.assert_test("recommendations" in tutoring_session, "Recommendation generation")
        
        # Test adaptation for visual learner
        self.assert_test(
            tutoring_session["content"]["primary_format"] == "videos",
            "Content adaptation for visual learner"
        )
    
    async def test_course_creation(self):
        """Test dynamic course creation"""
        print("\n📚 Testing Course Creation...")
        
        # Test basic course
        basic_requirements = {
            'title': 'Introduction to Python',
            'subject_area': 'programming',
            'difficulty_level': 'beginner',
            'duration_weeks': 8,
            'target_audience': 'beginners',
            'description': 'Learn Python programming fundamentals'
        }
        
        course = await self.agents.create_dynamic_course(basic_requirements)
        self.assert_test(isinstance(course, CourseStructure), "Course structure creation")
        self.assert_test(course.title == 'Introduction to Python', "Course title setting")
        self.assert_test(course.difficulty_level == DifficultyLevel.BEGINNER, "Difficulty level setting")
        self.assert_test(len(course.modules) > 0, "Module creation")
        self.assert_test(len(course.learning_objectives) > 0, "Learning objectives generation")
        self.assert_test(course.duration_hours > 0, "Duration calculation")
        
        # Test advanced course
        advanced_requirements = {
            'title': 'Advanced Machine Learning',
            'subject_area': 'data_science',
            'difficulty_level': 'expert',
            'duration_weeks': 12,
            'target_audience': 'professionals'
        }
        
        advanced_course = await self.agents.create_dynamic_course(advanced_requirements)
        self.assert_test(advanced_course.difficulty_level == DifficultyLevel.EXPERT, "Expert difficulty level")
        self.assert_test(len(advanced_course.prerequisites) > 0, "Prerequisites for advanced course")
        
        return course  # Return for use in other tests
    
    async def test_course_adaptation(self, course, learning_profile):
        """Test course adaptation to learner profile"""
        print("\n🎯 Testing Course Adaptation...")
        
        adapted_course = await self.agents.adapt_course_content(course, learning_profile)
        
        self.assert_test(isinstance(adapted_course, CourseStructure), "Adapted course creation")
        self.assert_test(
            adapted_course.course_id.endswith(f"_adapted_{learning_profile.user_id}"),
            "Adapted course ID generation"
        )
        self.assert_test(
            adapted_course.title.endswith(" (Personalized)"),
            "Personalized course title"
        )
        self.assert_test(
            "adapted_for_user" in adapted_course.metadata,
            "Adaptation metadata"
        )
        
        # Test content adaptation for visual learner
        visual_content_found = False
        for module in adapted_course.modules:
            if "videos" in module.get("content_types", []):
                visual_content_found = True
                break
        
        self.assert_test(visual_content_found, "Visual content adaptation")
        
        return adapted_course
    
    async def test_learning_assessment(self, adapted_course, learning_profile):
        """Test learning assessment functionality"""
        print("\n📊 Testing Learning Assessment...")
        
        # Test formative assessment
        formative_data = {
            'type': 'formative',
            'responses': [
                {'question_id': 'q1', 'correct': True, 'time_spent': 30},
                {'question_id': 'q2', 'correct': True, 'time_spent': 45},
                {'question_id': 'q3', 'correct': False, 'time_spent': 60},
                {'question_id': 'q4', 'correct': True, 'time_spent': 35},
                {'question_id': 'q5', 'correct': True, 'time_spent': 40}
            ],
            'duration_minutes': 15,
            'question_count': 5,
            'completion_rate': 1.0,
            'difficulty': 'intermediate'
        }
        
        assessment_result = await self.agents.conduct_comprehensive_assessment(
            learning_profile.user_id, adapted_course.course_id, formative_data
        )
        
        self.assert_test(isinstance(assessment_result, AssessmentResult), "Assessment result creation")
        self.assert_test(assessment_result.assessment_type == AssessmentType.FORMATIVE, "Assessment type setting")
        self.assert_test(0 <= assessment_result.score <= 100, "Score in valid range")
        self.assert_test(len(assessment_result.competencies) > 0, "Competency analysis")
        self.assert_test(len(assessment_result.recommendations) > 0, "Recommendation generation")
        
        # Test summative assessment
        summative_data = {
            'type': 'summative',
            'responses': [
                {'question_id': 'q1', 'correct': True, 'time_spent': 120},
                {'question_id': 'q2', 'correct': True, 'time_spent': 150},
                {'question_id': 'q3', 'correct': False, 'time_spent': 180},
                {'question_id': 'q4', 'correct': True, 'time_spent': 135}
            ],
            'duration_minutes': 30,
            'question_count': 4,
            'completion_rate': 1.0,
            'difficulty': 'advanced'
        }
        
        summative_result = await self.agents.conduct_comprehensive_assessment(
            learning_profile.user_id, adapted_course.course_id, summative_data
        )
        
        self.assert_test(summative_result.assessment_type == AssessmentType.SUMMATIVE, "Summative assessment type")
        
        return assessment_result
    
    async def test_progress_tracking(self, learning_profile, adapted_course):
        """Test learning progress tracking"""
        print("\n📈 Testing Progress Tracking...")
        
        progress_report = await self.agents.track_learning_progress(
            learning_profile.user_id, adapted_course.course_id, "month"
        )
        
        self.assert_test(isinstance(progress_report, dict), "Progress report generation")
        self.assert_test("overall_progress" in progress_report, "Overall progress tracking")
        self.assert_test("learning_velocity" in progress_report, "Learning velocity calculation")
        self.assert_test("retention_analysis" in progress_report, "Retention analysis")
        self.assert_test("insights" in progress_report, "Progress insights")
        self.assert_test("performance_prediction" in progress_report, "Performance prediction")
        
        # Test different timeframes
        for timeframe in ["week", "all"]:
            timeframe_report = await self.agents.track_learning_progress(
                learning_profile.user_id, adapted_course.course_id, timeframe
            )
            self.assert_test(
                timeframe_report["timeframe"] == timeframe,
                f"Progress tracking for {timeframe} timeframe"
            )
    
    async def test_performance_benchmarks(self):
        """Test performance of education agents"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Test learning profile creation performance
        start_time = time.time()
        test_data = {
            'user_id': 'perf_test',
            'learning_preferences': {'visual_content': 4},
            'experience_level': 'intermediate'
        }
        await self.agents.create_learning_profile(test_data)
        profile_time = (time.time() - start_time) * 1000
        
        self.assert_test(profile_time < 100, f"Profile creation performance ({profile_time:.1f}ms < 100ms)")
        
        # Test course creation performance
        start_time = time.time()
        course_req = {
            'title': 'Performance Test Course',
            'subject_area': 'test',
            'difficulty_level': 'intermediate'
        }
        await self.agents.create_dynamic_course(course_req)
        course_time = (time.time() - start_time) * 1000
        
        self.assert_test(course_time < 500, f"Course creation performance ({course_time:.1f}ms < 500ms)")
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚨 Testing Error Handling...")
        
        # Test empty data handling
        try:
            await self.agents.create_learning_profile({})
            self.assert_test(False, "Empty profile data should raise exception")
        except Exception:
            self.assert_test(True, "Empty profile data exception handling")
        
        # Test minimal valid data
        minimal_data = {
            'user_id': 'minimal_test',
            'learning_preferences': {},
            'experience_level': 'beginner'
        }
        
        try:
            minimal_profile = await self.agents.create_learning_profile(minimal_data)
            self.assert_test(minimal_profile.user_id == 'minimal_test', "Minimal data profile creation")
        except Exception as e:
            self.assert_test(False, f"Minimal data should work: {e}")
    
    async def run_all_tests(self):
        """Run all education AI tests"""
        print("🚀 Starting Education AI Comprehensive Test Suite")
        print("=" * 60)
        
        # Run tests in logical order
        learning_profile = await self.test_learning_profile_creation()
        await self.test_personalized_tutoring(learning_profile)
        
        course = await self.test_course_creation()
        adapted_course = await self.test_course_adaptation(course, learning_profile)
        
        await self.test_learning_assessment(adapted_course, learning_profile)
        await self.test_progress_tracking(learning_profile, adapted_course)
        
        await self.test_performance_benchmarks()
        await self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
        else:
            print("\n🎉 All tests passed! Education AI Service is fully functional.")
        
        return self.failed == 0


async def main():
    """Run the education AI test suite"""
    test_runner = EducationTestRunner()
    success = await test_runner.run_all_tests()
    
    if success:
        print("\n🎓 Education AI Service implementation complete and verified!")
        return 0
    else:
        print("\n💥 Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())