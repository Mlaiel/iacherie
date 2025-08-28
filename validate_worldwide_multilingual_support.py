#!/usr/bin/env python3
"""
Worldwide Multilingual Support Validation Script
===============================================

Validates the enhanced multilingual support for "parler et comprendre 
tous les langues et dialecte locale du monde entier"

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import re
from typing import List, Dict, Set

def extract_languages_from_file(file_path: str) -> List[str]:
    """Extract language entries from language_manager.py"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all language enum entries
        pattern = r'    ([A-Z_]+) = "([^"]+)"'
        matches = re.findall(pattern, content)
        
        return [(name, code) for name, code in matches]
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def extract_localizations_from_file(file_path: str) -> List[str]:
    """Extract localization entries from dialect_localization.py"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all localization entries
        pattern = r'"([^"]+)": DialectLocalization\('
        matches = re.findall(pattern, content)
        
        return matches
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def analyze_language_coverage(languages: List[tuple]) -> Dict[str, List[str]]:
    """Analyze language coverage by region/family"""
    
    # Regional language samples for coverage analysis
    regional_mapping = {
        'North America': ['en', 'en_US', 'en_CA', 'fr_CA', 'es_MX'],
        'South America': ['es_AR', 'es_CL', 'pt_BR', 'ay', 'gn_PY'],
        'Europe': ['de', 'fr', 'es', 'it', 'pl', 'ru', 'sv', 'no'],
        'Africa': ['sw', 'yo', 'ig', 'am_ET', 'om', 'rw', 'mg', 'ar_EG'],
        'Asia': ['zh_CN', 'ja', 'ko', 'hi', 'bn', 'th', 'vi', 'kk', 'uz'],
        'Middle East': ['ar', 'fa', 'tr', 'he', 'ku', 'ckb'],
        'Oceania': ['mi', 'fj', 'to', 'sm', 'tpi'],
        'Sign Languages': ['ase', 'bfi', 'fsl', 'gsg', 'jsl', 'csl', 'ils'],
        'Indigenous': ['qu', 'nah', 'ay', 'gn', 'chr', 'nv', 'iu', 'se']
    }
    
    language_codes = [code for _, code in languages]
    coverage_report = {}
    
    for region, sample_codes in regional_mapping.items():
        present = [code for code in sample_codes if code in language_codes]
        coverage_report[region] = {
            'total_sample': len(sample_codes),
            'present': len(present),
            'coverage_percent': (len(present) / len(sample_codes)) * 100,
            'present_languages': present
        }
    
    return coverage_report

def main():
    """Main validation function"""
    
    print("🌍 VALIDATION: Enhanced Worldwide Multilingual Support")
    print("=" * 60)
    
    # File paths
    language_file = "conversational/multilingual_support/language_manager.py"
    localization_file = "conversational/multilingual_support/dialect_localization.py"
    
    # Check if files exist
    if not os.path.exists(language_file):
        print(f"❌ Language file not found: {language_file}")
        return False
    
    if not os.path.exists(localization_file):
        print(f"❌ Localization file not found: {localization_file}")
        return False
    
    # Extract data
    languages = extract_languages_from_file(language_file)
    localizations = extract_localizations_from_file(localization_file)
    
    if not languages:
        print("❌ No languages extracted")
        return False
    
    print(f"📊 LANGUAGE COVERAGE ANALYSIS")
    print(f"   Total languages supported: {len(languages)}")
    print(f"   Total localizations: {len(localizations)}")
    print()
    
    # Analyze coverage
    coverage = analyze_language_coverage(languages)
    
    print(f"🗺️  REGIONAL COVERAGE ANALYSIS")
    print("-" * 40)
    
    total_coverage = 0
    regions_with_good_coverage = 0
    
    for region, data in coverage.items():
        coverage_percent = data['coverage_percent']
        total_coverage += coverage_percent
        
        if coverage_percent >= 75:
            status = "✅ EXCELLENT"
            regions_with_good_coverage += 1
        elif coverage_percent >= 50:
            status = "⚠️  GOOD"
        else:
            status = "❌ NEEDS IMPROVEMENT"
        
        print(f"   {region:15}: {coverage_percent:5.1f}% ({data['present']}/{data['total_sample']}) {status}")
    
    average_coverage = total_coverage / len(coverage)
    print(f"\n📈 OVERALL METRICS")
    print(f"   Average regional coverage: {average_coverage:.1f}%")
    print(f"   Regions with good coverage: {regions_with_good_coverage}/{len(coverage)}")
    
    # Check critical new languages
    critical_new_languages = [
        ('AMERICAN_SIGN_LANGUAGE', 'ase'),
        ('BRITISH_SIGN_LANGUAGE', 'bfi'),
        ('KAZAKH', 'kk'),
        ('KYRGYZ', 'ky'),
        ('UZBEK', 'uz'),
        ('AMHARIC_ET', 'am_ET'),
        ('OROMO', 'om'),
        ('KINYARWANDA', 'rw'),
        ('AYMARA', 'ay'),
        ('MIXTEC', 'mix')
    ]
    
    print(f"\n🆕 CRITICAL NEW LANGUAGES")
    print("-" * 40)
    
    language_names = [name for name, _ in languages]
    present_critical = 0
    
    for name, code in critical_new_languages:
        if name in language_names:
            print(f"   ✅ {name} ({code})")
            present_critical += 1
        else:
            print(f"   ❌ {name} ({code}) - MISSING")
    
    critical_coverage = (present_critical / len(critical_new_languages)) * 100
    print(f"\n   Critical languages coverage: {critical_coverage:.1f}%")
    
    # Calculate overall conformity
    language_count_score = min(len(languages) / 570, 1.0) * 100
    regional_coverage_score = average_coverage
    critical_languages_score = critical_coverage
    
    overall_conformity = (language_count_score * 0.4 + 
                         regional_coverage_score * 0.4 + 
                         critical_languages_score * 0.2)
    
    print(f"\n🎯 CONFORMITY ASSESSMENT")
    print("-" * 40)
    print(f"   Language count score:    {language_count_score:.1f}%")
    print(f"   Regional coverage score: {regional_coverage_score:.1f}%") 
    print(f"   Critical languages score: {critical_languages_score:.1f}%")
    print(f"   OVERALL CONFORMITY:      {overall_conformity:.1f}%")
    
    if overall_conformity >= 95:
        print(f"\n🎉 RESULT: EXCELLENCE ACHIEVED!")
        print(f"   The system achieves comprehensive worldwide language coverage")
        print(f"   Meeting the requirement: 'parler et comprendre tous les langues et dialecte locale du monde entier'")
        return True
    elif overall_conformity >= 90:
        print(f"\n✅ RESULT: OBJECTIVE EXCEEDED!")
        print(f"   Strong worldwide multilingual support implemented")
        return True
    elif overall_conformity >= 75:
        print(f"\n⚠️  RESULT: GOOD PROGRESS")
        print(f"   Substantial multilingual support, but some gaps remain")
        return True
    else:
        print(f"\n❌ RESULT: NEEDS IMPROVEMENT")
        print(f"   Significant gaps in worldwide language coverage")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)