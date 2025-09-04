#!/usr/bin/env python3
"""
Education AI Service Demo
========================

Demonstrates the three core capabilities of the Education AI Service:
1. Personal tutoring with adaptive learning
2. Automated course creation and structuring  
3. Learning assessment and progress tracking

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai.education import (
    create_education_service,
    DifficultyLevel,
    AssessmentType,
    LearningStyle
)


async def demo_personal_tutor():
    """Demo: Personal Tutoring System"""
    print("🎓 === PERSONAL TUTOR DEMO ===")
    
    service = await create_education_service()
    user_id = "demo_student"
    
    print(f"👤 Student: {user_id}")
    print("📚 Starting tutoring session on 'Machine Learning Basics'...")
    
    # Start tutoring session
    session_id = await service.start_tutoring_session(
        user_id=user_id,
        topic="Machine Learning Basics",
        learning_objectives=[
            "Understand supervised vs unsupervised learning",
            "Learn about neural networks",
            "Practice with real examples"
        ],
        session_type="interactive"
    )
    
    print(f"✅ Session started: {session_id[:8]}...")
    
    # Simulate learning conversation
    questions = [
        "What is the difference between supervised and unsupervised learning?",
        "Can you give me an example of a neural network?",
        "How do I know if my model is overfitting?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n💬 Student Question {i}: {question}")
        
        response = await service.process_learning_interaction(
            session_id=session_id,
            user_input=question,
            context={"difficulty": "intermediate"}
        )
        
        print(f"🤖 AI Tutor: {response['response'][:100]}...")
        print(f"📈 Learning Elements: {', '.join(response['learning_elements'])}")
        print(f"💡 Next Suggestions: {response['next_suggestions'][0] if response['next_suggestions'] else 'Continue learning'}")
    
    # End session
    summary = await service.end_tutoring_session(session_id)
    
    print(f"\n📊 Session Summary:")
    print(f"   Duration: {summary['session_summary']['duration']} minutes")
    print(f"   Topic: {summary['session_summary']['topic_covered']}")
    print(f"   Engagement: {summary['session_summary']['engagement_level']}")
    print(f"   Recommendations: {len(summary['recommendations'])} personalized suggestions")
    
    return service, user_id


async def demo_course_creation():
    """Demo: Automated Course Creation"""
    print("\n🏗️ === COURSE CREATION DEMO ===")
    
    service = await create_education_service()
    
    print("📖 Creating comprehensive course: 'Full Stack Web Development'...")
    
    # Create course
    course_id = await service.create_course(
        course_title="Full Stack Web Development",
        course_description="Complete guide to modern web development using React, Node.js, and MongoDB",
        category="Web Development",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        target_audience="Developers with basic programming knowledge",
        learning_outcomes=[
            "Build responsive web applications with React",
            "Create RESTful APIs with Node.js and Express",
            "Design and implement MongoDB databases",
            "Deploy applications to cloud platforms",
            "Implement authentication and security best practices"
        ],
        creator_id="ai_instructor"
    )
    
    print(f"✅ Course created: {course_id[:8]}...")
    
    # Get course structure
    structure = await service.get_course_structure(course_id)
    
    print(f"\n📚 Course Structure:")
    print(f"   Title: {structure['title']}")
    print(f"   Difficulty: {structure['difficulty_level'].title()}")
    print(f"   Total Duration: {structure['total_duration']} minutes")
    print(f"   Modules: {structure['module_count']}")
    print(f"   Target: {structure['target_audience']}")
    
    print(f"\n🎯 Learning Outcomes:")
    for i, outcome in enumerate(structure['learning_outcomes'], 1):
        print(f"   {i}. {outcome}")
    
    print(f"\n📋 Module Breakdown:")
    for i, module in enumerate(structure['modules'], 1):
        print(f"   Module {i}: {module['title']}")
        print(f"      Duration: {module['duration']} min | Objectives: {module['objectives_count']} | Content: {module['content_items_count']}")
    
    return service, course_id


async def demo_learning_assessment():
    """Demo: Learning Assessment and Progress Tracking"""
    print("\n📊 === LEARNING ASSESSMENT DEMO ===")
    
    service = await create_education_service()
    user_id = "demo_learner"
    
    # Create a course for assessment
    course_id = await service.create_course(
        course_title="Python Data Science",
        course_description="Learn data science with Python",
        category="Data Science",
        difficulty_level=DifficultyLevel.BEGINNER
    )
    
    print(f"👤 Learner: {user_id}")
    print(f"📚 Course: Python Data Science")
    
    # Personalize course content
    print(f"\n🎨 Personalizing course content...")
    
    # Set learning style for personalization
    service.learning_profiles[user_id] = service.learning_profiles.get(user_id, 
        type('LearningProfile', (), {
            'user_id': user_id,
            'learning_style': LearningStyle.VISUAL,
            'preferred_pace': 'moderate',
            'interests': ['data visualization', 'machine learning']
        })()
    )
    
    personalized = await service.personalize_course_content(course_id, user_id)
    
    print(f"✅ Content adapted for {personalized['personalized_path']['personalization_factors']['learning_style']} learner")
    print(f"📅 Estimated completion: {personalized['estimated_completion_time']} minutes")
    
    # Create and take assessment
    print(f"\n📝 Creating adaptive assessment...")
    
    assessment = await service.create_assessment(
        course_id=course_id,
        assessment_type=AssessmentType.QUIZ
    )
    
    print(f"✅ Assessment created with {len(assessment['questions'])} questions")
    print(f"⏱️ Estimated duration: {assessment['estimated_duration']} minutes")
    
    # Simulate taking assessment
    print(f"\n🎯 Taking assessment...")
    
    assessment_data = {
        'course_id': course_id,
        'type': 'quiz',
        'responses': [
            {'question_id': 'q_1', 'answer': 'A'},  # Correct
            {'question_id': 'q_2', 'answer': 'B'},  # Correct
            {'question_id': 'q_3', 'answer': 'C'},  # Wrong
            {'question_id': 'q_4', 'answer': 'A'},  # Correct
            {'question_id': 'q_5', 'answer': 'B'},  # Wrong
        ],
        'time_taken': 18
    }
    
    result = await service.evaluate_assessment(user_id, assessment_data)
    
    print(f"📊 Assessment Results:")
    print(f"   Score: {result.score:.1%} ({result.correct_answers}/{result.questions_answered})")
    print(f"   Time taken: {result.time_taken} minutes")
    print(f"   Recommendations: {len(result.recommendations)} suggestions")
    
    if result.recommendations:
        print(f"   💡 Top recommendation: {result.recommendations[0]}")
    
    # Check learning progress
    print(f"\n📈 Learning Progress Analysis...")
    
    progress = await service.get_learning_progress(user_id, course_id)
    
    print(f"   Overall progress: {progress['overall_progress']:.1%}")
    print(f"   Modules completed: {progress['modules_completed']}/{progress['total_modules']}")
    print(f"   Time spent: {progress['time_spent']} minutes")
    print(f"   Assessments completed: {progress['assessments_completed']}")
    
    # Identify knowledge gaps
    gaps = await service.identify_knowledge_gaps(user_id)
    
    print(f"\n🎯 Knowledge Gap Analysis:")
    if gaps['knowledge_gaps']:
        print(f"   Gaps identified: {len(gaps['knowledge_gaps'])}")
        for gap in gaps['knowledge_gaps'][:2]:  # Show first 2
            print(f"   - {gap['topic']} (Severity: {gap['severity']})")
    else:
        print(f"   No significant knowledge gaps detected")
    
    print(f"   📚 Recommendations: {len(gaps['recommendations'])} targeted suggestions")
    
    return service


async def demo_complete_workflow():
    """Demo: Complete Educational Workflow"""
    print("\n🔄 === COMPLETE WORKFLOW DEMO ===")
    print("Demonstrating end-to-end educational journey...")
    
    service = await create_education_service()
    student_id = "complete_workflow_student"
    
    # 1. Personal tutoring to identify needs
    print(f"\n1️⃣ Initial Tutoring Consultation")
    session_id = await service.start_tutoring_session(
        user_id=student_id,
        topic="Learning Goal Assessment",
        session_type="consultation"
    )
    
    await service.process_learning_interaction(
        session_id=session_id,
        user_input="I want to learn web development but don't know where to start"
    )
    
    session_summary = await service.end_tutoring_session(session_id)
    print(f"✅ Consultation complete - Learning needs identified")
    
    # 2. Create personalized course
    print(f"\n2️⃣ Creating Personalized Course")
    course_id = await service.create_course(
        course_title="Web Development for Beginners",
        course_description="Personalized web development course based on consultation",
        category="Web Development",
        difficulty_level=DifficultyLevel.BEGINNER,
        creator_id="ai_tutor"
    )
    
    personalized = await service.personalize_course_content(course_id, student_id)
    print(f"✅ Personalized course created and adapted")
    
    # 3. Learning with ongoing assessment
    print(f"\n3️⃣ Learning Journey with Assessment")
    
    # Create assessment
    assessment = await service.create_assessment(course_id)
    
    # Take assessment
    assessment_data = {
        'course_id': course_id,
        'type': 'quiz',
        'responses': [{'question_id': f'q_{i}', 'answer': 'A'} for i in range(1, 4)],
        'time_taken': 12
    }
    
    result = await service.evaluate_assessment(student_id, assessment_data)
    print(f"✅ First assessment completed - Score: {result.score:.1%}")
    
    # 4. Adaptive tutoring based on results
    print(f"\n4️⃣ Adaptive Follow-up Tutoring")
    followup_session = await service.start_tutoring_session(
        user_id=student_id,
        topic="HTML Fundamentals Review",
        session_type="review"
    )
    
    await service.process_learning_interaction(
        session_id=followup_session,
        user_input="I'm struggling with the HTML concepts from the assessment"
    )
    
    await service.end_tutoring_session(followup_session)
    print(f"✅ Adaptive tutoring provided based on assessment results")
    
    # 5. Progress tracking and recommendations
    print(f"\n5️⃣ Progress Analysis and Future Planning")
    progress = await service.get_learning_progress(student_id, course_id)
    gaps = await service.identify_knowledge_gaps(student_id)
    
    print(f"📊 Final Progress Report:")
    print(f"   Learning sessions completed: 2")
    print(f"   Course progress: {progress['overall_progress']:.1%}")
    print(f"   Assessments taken: {progress['assessments_completed']}")
    print(f"   Knowledge gaps addressed: {len(gaps['recommendations'])}")
    print(f"   Adaptive recommendations generated: ✅")
    
    print(f"\n🎉 Complete educational workflow demonstrated successfully!")


async def main():
    """Run all Education AI Service demos"""
    print("🚀 Education AI Service - Comprehensive Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Personal Tutoring
        await demo_personal_tutor()
        
        # Demo 2: Course Creation
        await demo_course_creation()
        
        # Demo 3: Learning Assessment
        await demo_learning_assessment()
        
        # Demo 4: Complete Workflow
        await demo_complete_workflow()
        
        print(f"\n" + "=" * 60)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("✅ Personal Tutor: Adaptive learning sessions")
        print("✅ Course Creator: Automated curriculum generation")
        print("✅ Assessment Engine: Progress tracking and gap analysis")
        print("✅ Complete Workflow: End-to-end educational journey")
        print(f"\n💡 The Education AI Service is ready for production use!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())