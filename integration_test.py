#!/usr/bin/env python3
"""
Integration Test for Ainflue Platform - All 5 Systems
Tests that all required systems are working correctly
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all working systems
import audio_processing_working as audio
import protection_working as protection
import payment_working as payment
import notification_working as notification
import collaboration_working as collaboration

async def test_audio_processing():
    """Test audio processing pipeline"""
    print("🎵 Testing Audio Processing Pipeline...")
    
    try:
        # Create a simple mock audio file data
        import numpy as np
        mock_audio_data = np.random.random(22050)  # 1 second of audio at 22050 Hz
        
        processor = audio.AudioProcessor()
        
        # Test feature extraction
        features = await processor._extract_features(mock_audio_data)
        
        # Test fingerprint generation
        fingerprint = await processor._generate_fingerprint(mock_audio_data)
        
        print(f"   ✅ Features extracted: {len(features)} features")
        print(f"   ✅ Fingerprint generated: {fingerprint[:20]}...")
        print(f"   ✅ Audio processing pipeline: WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ Audio processing failed: {e}")
        return False

async def test_ai_protection():
    """Test AI protection system"""
    print("🛡️  Testing AI Protection System...")
    
    try:
        # Test content protection
        result = await protection.protect_content(
            "content_001", 
            "This is sample content to protect",
            {"type": "audio", "creator": "test_user"}
        )
        
        if result["status"] != "success":
            raise Exception(f"Protection failed: {result}")
        
        # Test violation scanning
        scan_result = await protection.scan_content(
            "This is sample content to protect",  # Same content should match
            "audio"
        )
        
        print(f"   ✅ Content protected: {result['content_id']}")
        print(f"   ✅ Violation scan: {scan_result['status']}")
        print(f"   ✅ AI protection system: WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ AI protection failed: {e}")
        return False

async def test_payment_integration():
    """Test payment integration (Stripe)"""
    print("💳 Testing Payment Integration (Stripe)...")
    
    try:
        # Test payment creation
        payment_result = await payment.create_payment(
            amount=25.00,
            currency="usd",
            payment_method="stripe",
            customer_id="customer_123",
            metadata={"order_id": "order_001"}
        )
        
        if payment_result["status"] != "success":
            raise Exception(f"Payment creation failed: {payment_result}")
        
        transaction_id = payment_result["transaction"]["transaction_id"]
        
        # Test payment confirmation
        confirm_result = await payment.confirm_payment(transaction_id)
        
        if confirm_result["status"] != "success":
            raise Exception(f"Payment confirmation failed: {confirm_result}")
        
        print(f"   ✅ Payment created: {transaction_id}")
        print(f"   ✅ Payment confirmed: {confirm_result['transaction']['status']}")
        print(f"   ✅ Payment integration (Stripe): WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ Payment integration failed: {e}")
        return False

async def test_notification_system():
    """Test notification system"""
    print("🔔 Testing Notification System...")
    
    try:
        # Test email notification
        email_result = await notification.send_email(
            "test@example.com",
            "Test Subject",
            "Test email content"
        )
        
        if email_result["status"] != "success":
            raise Exception(f"Email sending failed: {email_result}")
        
        # Test SMS notification
        sms_result = await notification.send_sms(
            "+1234567890",
            "Test SMS message"
        )
        
        if sms_result["status"] != "success":
            raise Exception(f"SMS sending failed: {sms_result}")
        
        # Test in-app notification
        in_app_result = await notification.create_in_app_notification(
            "user123",
            "Test Notification",
            "This is a test in-app notification"
        )
        
        if in_app_result["status"] != "success":
            raise Exception(f"In-app notification failed: {in_app_result}")
        
        print(f"   ✅ Email sent: {email_result['email_id']}")
        print(f"   ✅ SMS sent: {sms_result['sms_id']}")
        print(f"   ✅ In-app notification: {in_app_result['notification']['id']}")
        print(f"   ✅ Notification system: WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ Notification system failed: {e}")
        return False

async def test_collaboration_engine():
    """Test collaboration engine"""
    print("🤝 Testing Collaboration Engine...")
    
    try:
        # Initialize demo data
        await collaboration.collaboration_engine.initialize_demo_data()
        
        # Test project creation
        project_result = await collaboration.create_project(
            title="Test Music Project",
            description="A test collaboration project for music production",
            creator_id="user1",
            collaboration_type="music_production",
            budget=500.0
        )
        
        if project_result["status"] != "success":
            raise Exception(f"Project creation failed: {project_result}")
        
        project_id = project_result["project"]["project_id"]
        
        # Test finding collaborators
        collaborators_result = await collaboration.find_collaborators(
            project_id,
            ["vocals", "mixing"],
            max_results=5
        )
        
        if collaborators_result["status"] != "success":
            raise Exception(f"Finding collaborators failed: {collaborators_result}")
        
        # Test task creation
        task_result = await collaboration.create_task(
            project_id,
            "Record vocals",
            "Record the main vocal tracks for the song",
            assigned_to="user2",
            priority="high"
        )
        
        if task_result["status"] != "success":
            raise Exception(f"Task creation failed: {task_result}")
        
        print(f"   ✅ Project created: {project_id}")
        print(f"   ✅ Found {collaborators_result['count']} potential collaborators")
        print(f"   ✅ Task created: {task_result['task']['task_id']}")
        print(f"   ✅ Collaboration engine: WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ Collaboration engine failed: {e}")
        return False

async def run_integration_test():
    """Run complete integration test"""
    print("🚀 Starting Ainflue Platform Integration Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test all systems
    tests = [
        ("Audio Processing Pipeline", test_audio_processing),
        ("AI Protection System", test_ai_protection),
        ("Payment Integration (Stripe)", test_payment_integration),
        ("Notification System", test_notification_system),
        ("Collaboration Engine", test_collaboration_engine)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print()
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{len(results)} systems working")
    
    if passed == len(results):
        print("🎉 ALL SYSTEMS OPERATIONAL - AINFLUE PLATFORM READY!")
    else:
        print("⚠️  Some systems need attention")
    
    elapsed_time = time.time() - start_time
    print(f"⏱️  Test completed in {elapsed_time:.2f} seconds")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(run_integration_test())
    sys.exit(0 if success else 1)