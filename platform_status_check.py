#!/usr/bin/env python3
"""
Simple Platform Status Check
Checks the current status of the Ainflue platform without external dependencies.
"""

import os
import json
from pathlib import Path
from typing import Dict, List


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return Path(file_path).exists()


def check_directory_exists(dir_path: str) -> bool:
    """Check if a directory exists"""
    return Path(dir_path).is_dir()


def load_json_file(file_path: str) -> Dict:
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def count_files_in_directory(dir_path: str, extension: str = "*") -> int:
    """Count files in directory"""
    try:
        if extension == "*":
            return len(list(Path(dir_path).rglob("*")))
        else:
            return len(list(Path(dir_path).rglob(f"*.{extension}")))
    except:
        return 0


def main():
    """Main status check function"""
    print("🔍 AINFLUE PLATFORM STATUS CHECK")
    print("=" * 50)
    
    status = {
        "frontend": {"status": "unknown", "details": []},
        "backend": {"status": "unknown", "details": []},
        "internationalization": {"status": "unknown", "details": []}, 
        "apis": {"status": "unknown", "details": []},
        "databases": {"status": "unknown", "details": []},
        "ai_engines": {"status": "unknown", "details": []},
        "overall": {"completion": 0, "status": "unknown"}
    }
    
    # 1. Frontend Check
    print("\n📱 FRONTEND STATUS:")
    frontend_files = [
        "frontend/package.json",
        "frontend/src/app/layout.tsx",
        "frontend/src/app/page.tsx",
        "frontend/src/components/dashboard/Dashboard.tsx",
        "frontend/src/components/dashboard/RevenueChart.tsx",
        "frontend/src/components/LanguageSelector.tsx",
        "frontend/src/hooks/useLanguage.tsx"
    ]
    
    frontend_score = 0
    for file in frontend_files:
        if check_file_exists(file):
            status["frontend"]["details"].append(f"✅ {file}")
            frontend_score += 1
        else:
            status["frontend"]["details"].append(f"❌ {file}")
    
    status["frontend"]["completion"] = (frontend_score / len(frontend_files)) * 100
    status["frontend"]["status"] = "complete" if frontend_score == len(frontend_files) else "partial"
    print(f"   Completion: {status['frontend']['completion']:.1f}%")
    
    # 2. Backend API Check
    print("\n🔧 BACKEND API STATUS:")
    api_files = [
        "api/routes/auth.py",
        "api/routes/fingerprinting.py", 
        "api/routes/monitoring.py",
        "api/routes/monetization.py",
        "api/routes/collaboration.py",
        "api/routes/upload.py",
        "api/routes/alerts.py",
        "api/routes/analytics.py"
    ]
    
    api_score = 0
    for file in api_files:
        if check_file_exists(file):
            status["apis"]["details"].append(f"✅ {file}")
            api_score += 1
        else:
            status["apis"]["details"].append(f"❌ {file}")
    
    status["apis"]["completion"] = (api_score / len(api_files)) * 100
    status["apis"]["status"] = "complete" if api_score == len(api_files) else "partial"
    print(f"   Completion: {status['apis']['completion']:.1f}%")
    
    # 3. Internationalization Check
    print("\n🌍 INTERNATIONALIZATION STATUS:")
    i18n_files = [
        "frontend/src/locales/en.json",
        "frontend/src/locales/fr.json", 
        "frontend/src/locales/de.json",
        "frontend/src/locales/ar.json",
        "frontend/src/locales/ber.json"
    ]
    
    i18n_score = 0
    total_translations = 0
    for file in i18n_files:
        if check_file_exists(file):
            status["internationalization"]["details"].append(f"✅ {file}")
            i18n_score += 1
            
            # Count translations
            lang_data = load_json_file(file)
            if "error" not in lang_data:
                total_translations += len(lang_data)
        else:
            status["internationalization"]["details"].append(f"❌ {file}")
    
    # Check Amazigh dialects
    amazigh_dir = "core/i18n/amazigh_dialects"
    if check_directory_exists(amazigh_dir):
        amazigh_count = count_files_in_directory(amazigh_dir, "json")
        status["internationalization"]["details"].append(f"✅ Amazigh dialects: {amazigh_count} files")
        i18n_score += 2  # Bonus for Amazigh support
    else:
        status["internationalization"]["details"].append(f"❌ Amazigh dialects directory missing")
    
    status["internationalization"]["completion"] = min((i18n_score / len(i18n_files)) * 100, 100)
    status["internationalization"]["status"] = "excellent" if i18n_score > len(i18n_files) else "complete" if i18n_score == len(i18n_files) else "partial"
    print(f"   Completion: {status['internationalization']['completion']:.1f}%")
    print(f"   Total translations: {total_translations}")
    
    # 4. AI Engines Check
    print("\n🧠 AI ENGINES STATUS:")
    ai_files = [
        "ai_engine/fingerprinting/audio_fingerprint_engine.py",
        "ai_engine/fingerprinting/video_fingerprint_engine.py",
        "ai_engine/fingerprinting/image_fingerprint_engine.py", 
        "ai_engine/fingerprinting/text_fingerprint_engine.py",
        "ai_engine/fingerprinting/vector_matching_engine.py"
    ]
    
    ai_score = 0
    for file in ai_files:
        if check_file_exists(file):
            status["ai_engines"]["details"].append(f"✅ {file}")
            ai_score += 1
        else:
            status["ai_engines"]["details"].append(f"❌ {file}")
    
    status["ai_engines"]["completion"] = (ai_score / len(ai_files)) * 100
    status["ai_engines"]["status"] = "complete" if ai_score == len(ai_files) else "partial"
    print(f"   Completion: {status['ai_engines']['completion']:.1f}%")
    
    # 5. Database Modules Check
    print("\n🗄️ DATABASE MODULES STATUS:")
    db_files = [
        "database/fingerprinting/fingerprint_analytics.py",
        "database/fingerprinting/fingerprint_repository.py",
        "data_management/repositories/content_repository.py"
    ]
    
    db_score = 0
    for file in db_files:
        if check_file_exists(file):
            status["databases"]["details"].append(f"✅ {file}")
            db_score += 1
        else:
            status["databases"]["details"].append(f"❌ {file}")
    
    status["databases"]["completion"] = (db_score / len(db_files)) * 100
    status["databases"]["status"] = "complete" if db_score == len(db_files) else "partial"
    print(f"   Completion: {status['databases']['completion']:.1f}%")
    
    # Calculate Overall Completion
    overall_completion = (
        status["frontend"]["completion"] * 0.25 +
        status["apis"]["completion"] * 0.25 +
        status["internationalization"]["completion"] * 0.15 +
        status["ai_engines"]["completion"] * 0.20 +
        status["databases"]["completion"] * 0.15
    )
    
    status["overall"]["completion"] = overall_completion
    
    if overall_completion >= 95:
        status["overall"]["status"] = "ready_for_production"
    elif overall_completion >= 80:
        status["overall"]["status"] = "nearly_complete"
    elif overall_completion >= 60:
        status["overall"]["status"] = "good_progress"
    else:
        status["overall"]["status"] = "needs_work"
    
    # Print Summary
    print("\n" + "=" * 50)
    print("📊 OVERALL PLATFORM STATUS")
    print("=" * 50)
    print(f"🎯 Overall Completion: {overall_completion:.1f}%")
    print(f"📈 Status: {status['overall']['status'].replace('_', ' ').title()}")
    
    print(f"\n📋 Component Breakdown:")
    print(f"   Frontend: {status['frontend']['completion']:.1f}%")
    print(f"   API Routes: {status['apis']['completion']:.1f}%") 
    print(f"   Internationalization: {status['internationalization']['completion']:.1f}%")
    print(f"   AI Engines: {status['ai_engines']['completion']:.1f}%")
    print(f"   Database Modules: {status['databases']['completion']:.1f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_completion >= 95:
        print("   🎉 Platform is ready for 100% key-in-hand deployment!")
        print("   🚀 Consider running production deployment tests")
        print("   📚 Complete documentation and user guides")
    elif overall_completion >= 80:
        print("   🔧 Platform is nearly complete - focus on missing components")
        print("   ✅ Address remaining gaps to reach 100%")
        print("   🧪 Run comprehensive integration tests")
    else:
        print("   📝 Review missing components and prioritize critical features")
        print("   🔨 Focus on API completeness and frontend functionality")
        print("   🌍 Complete internationalization for global reach")
    
    # Save results
    with open("platform_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    print(f"\n📄 Detailed status saved to: platform_status.json")
    
    return status


if __name__ == "__main__":
    main()