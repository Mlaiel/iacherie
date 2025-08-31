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
Comprehensive Tests for Protection Integration System
Testing content protection, copyright compliance, and security integration

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de

Team Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import hashlib
import base64
from typing import Dict, List, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from ai.recommendation.protection_integrator import (
    ProtectionIntegrator, RightsChecker, ContentFingerprint,
    ProtectionPolicy, ViolationAlert, RightsVerification,
    ProtectionLevel, RightsType, ViolationType
)
from ai.recommendation.models import (
    CreatorProfile, ContentType, Platform
)
from ai.recommendation.exceptions import ProtectionError, ValidationError


class TestProtectionIntegrator:
    """Comprehensive tests for the main protection integrator"""
    
    @pytest.mark.asyncio
    async def test_integrator_initialization(self):
        """Test protection integrator initialization"""
        integrator = ProtectionIntegrator()
        
        # Test initial state
        assert integrator.status.name == "INITIALIZING"
        
        # Test initialization
        success = await integrator.initialize()
        assert success is True
        assert integrator.status.name == "READY"
        
        # Test components are loaded
        assert integrator.copyright_analyzer is not None
        assert integrator.content_fingerprinter is not None
        assert integrator.legal_compliance_checker is not None
        assert integrator.brand_safety_monitor is not None
    
    @pytest.mark.asyncio
    async def test_analyze_content_protection(self, protection_integrator, sample_video_content):
        """Test comprehensive content protection analysis"""
        video_data = sample_video_content
        
        protection_report = await protection_integrator.analyze_content_protection(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE,
            creator_id="test_creator_001"
        )
        
        assert isinstance(protection_report, ProtectionReport)
        assert protection_report.content_id
        assert protection_report.analysis_timestamp
        assert protection_report.protection_score >= 0
        assert protection_report.copyright_analysis is not None
        assert protection_report.brand_safety_score is not None
        assert protection_report.legal_compliance is not None
    
    @pytest.mark.asyncio
    async def test_check_copyright_violations(self, protection_integrator, sample_audio_content):
        """Test copyright violation detection"""
        audio_data = sample_audio_content
        
        copyright_check = await protection_integrator.check_copyright_violations(
            content_data=audio_data,
            content_type=ContentType.AUDIO,
            check_databases=["youtube_content_id", "spotify_fingerprint", "audio_network"]
        )
        
        assert isinstance(copyright_check, CopyrightAnalysis)
        assert 0 <= copyright_check.violation_risk <= 1
        assert len(copyright_check.detected_matches) >= 0
        assert copyright_check.recommended_actions is not None
        
        # Test match details if violations found
        for match in copyright_check.detected_matches:
            assert 'source' in match
            assert 'confidence' in match
            assert 'match_duration' in match
            assert 'copyright_owner' in match
            assert 0 <= match['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_generate_content_fingerprint(self, protection_integrator, sample_video_content):
        """Test content fingerprint generation"""
        video_data = sample_video_content
        
        fingerprint = await protection_integrator.generate_content_fingerprint(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            fingerprint_types=["perceptual_hash", "audio_fingerprint", "visual_hash"]
        )
        
        assert 'perceptual_hash' in fingerprint
        assert 'audio_fingerprint' in fingerprint
        assert 'visual_hash' in fingerprint
        assert 'metadata_hash' in fingerprint
        
        # Test fingerprint validity
        for fp_type, fp_value in fingerprint.items():
            assert isinstance(fp_value, str)
            assert len(fp_value) > 0
            # Test it's a valid hash format
            assert all(c in '0123456789abcdef' for c in fp_value.lower())
    
    @pytest.mark.asyncio
    async def test_monitor_brand_safety(self, protection_integrator, sample_text_content):
        """Test brand safety monitoring"""
        text_data = sample_text_content
        
        brand_safety = await protection_integrator.monitor_brand_safety(
            content_data=text_data,
            content_type=ContentType.TEXT,
            brand_guidelines={
                "prohibited_topics": ["violence", "hate_speech", "adult_content"],
                "required_values": ["family_friendly", "positive", "educational"],
                "sensitivity_level": "high"
            }
        )
        
        assert isinstance(brand_safety, BrandSafetyScore)
        assert 0 <= brand_safety.overall_score <= 1
        assert 0 <= brand_safety.content_appropriateness <= 1
        assert 0 <= brand_safety.value_alignment <= 1
        assert brand_safety.risk_factors is not None
        assert brand_safety.recommendations is not None
    
    @pytest.mark.asyncio
    async def test_legal_compliance_check(self, protection_integrator, sample_video_content):
        """Test legal compliance verification"""
        video_data = sample_video_content
        
        compliance_check = await protection_integrator.check_legal_compliance(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            jurisdictions=["US", "EU", "GDPR"]
        )
        
        assert isinstance(compliance_check, LegalComplianceResult)
        assert 0 <= compliance_check.compliance_score <= 1
        assert len(compliance_check.platform_compliance) > 0
        assert compliance_check.identified_issues is not None
        assert compliance_check.remediation_steps is not None
        
        # Test platform-specific compliance
        for platform_result in compliance_check.platform_compliance:
            assert 'platform' in platform_result
            assert 'compliance_status' in platform_result
            assert 'specific_violations' in platform_result
            assert platform_result['compliance_status'] in ['compliant', 'warning', 'violation']
    
    @pytest.mark.asyncio
    async def test_dmca_takedown_protection(self, protection_integrator, sample_audio_content):
        """Test DMCA takedown protection analysis"""
        audio_data = sample_audio_content
        
        dmca_protection = await protection_integrator.analyze_dmca_protection(
            content_data=audio_data,
            content_type=ContentType.AUDIO,
            original_content_proof=True,
            creator_rights_documentation=True
        )
        
        assert 'takedown_risk' in dmca_protection
        assert 'protection_strength' in dmca_protection
        assert 'documentation_completeness' in dmca_protection
        assert 'recommended_protections' in dmca_protection
        
        # Test risk assessment
        takedown_risk = dmca_protection['takedown_risk']
        assert 0 <= takedown_risk <= 1
        
        protection_strength = dmca_protection['protection_strength']
        assert 0 <= protection_strength <= 1
    
    @pytest.mark.asyncio
    async def test_content_originality_verification(self, protection_integrator, sample_text_content):
        """Test content originality verification"""
        text_data = sample_text_content
        
        originality_check = await protection_integrator.verify_content_originality(
            content_data=text_data,
            content_type=ContentType.TEXT,
            plagiarism_databases=["academic", "web", "published_content"],
            similarity_threshold=0.15  # 15% similarity threshold
        )
        
        assert 'originality_score' in originality_check
        assert 'similarity_matches' in originality_check
        assert 'plagiarism_risk' in originality_check
        assert 'verification_confidence' in originality_check
        
        # Test originality score
        originality_score = originality_check['originality_score']
        assert 0 <= originality_score <= 1
        
        # Test similarity matches
        matches = originality_check['similarity_matches']
        for match in matches:
            assert 'source' in match
            assert 'similarity_percentage' in match
            assert 'matched_content' in match
            assert 0 <= match['similarity_percentage'] <= 1


class TestCopyrightAnalyzer:
    """Tests for copyright analysis algorithms"""
    
    @pytest.mark.asyncio
    async def test_audio_copyright_detection(self, copyright_analyzer, sample_audio_content):
        """Test audio copyright detection"""
        audio_data = sample_audio_content
        
        detection_result = await copyright_analyzer.detect_audio_copyright(
            audio_data=audio_data,
            detection_sensitivity="high",
            databases=["content_id", "audio_fingerprint_db", "music_recognition"]
        )
        
        assert 'copyright_matches' in detection_result
        assert 'confidence_scores' in detection_result
        assert 'match_segments' in detection_result
        assert 'owner_information' in detection_result
        
        # Test match segments
        segments = detection_result['match_segments']
        for segment in segments:
            assert 'start_time' in segment
            assert 'end_time' in segment
            assert 'confidence' in segment
            assert segment['start_time'] < segment['end_time']
            assert 0 <= segment['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_visual_copyright_detection(self, copyright_analyzer, sample_video_content):
        """Test visual copyright detection"""
        video_data = sample_video_content
        
        visual_detection = await copyright_analyzer.detect_visual_copyright(
            video_data=video_data,
            frame_sampling_rate=1.0,  # Sample every second
            databases=["image_recognition", "video_fingerprint", "visual_content_id"]
        )
        
        assert 'visual_matches' in visual_detection
        assert 'frame_matches' in visual_detection
        assert 'logo_detections' in visual_detection
        assert 'trademark_violations' in visual_detection
        
        # Test frame matches
        frame_matches = visual_detection['frame_matches']
        for match in frame_matches:
            assert 'frame_timestamp' in match
            assert 'match_confidence' in match
            assert 'source_reference' in match
            assert 0 <= match['match_confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_text_copyright_analysis(self, copyright_analyzer, sample_text_content):
        """Test text copyright analysis"""
        text_data = sample_text_content
        
        text_analysis = await copyright_analyzer.analyze_text_copyright(
            text_data=text_data,
            check_types=["exact_match", "paraphrase_detection", "quote_attribution"],
            databases=["published_works", "academic_papers", "web_content"]
        )
        
        assert 'text_matches' in text_analysis
        assert 'quote_attributions' in text_analysis
        assert 'fair_use_analysis' in text_analysis
        assert 'originality_percentage' in text_analysis
        
        # Test originality percentage
        originality = text_analysis['originality_percentage']
        assert 0 <= originality <= 1
        
        # Test fair use analysis
        fair_use = text_analysis['fair_use_analysis']
        assert 'commentary_ratio' in fair_use
        assert 'transformative_nature' in fair_use
        assert 'commercial_impact' in fair_use
    
    @pytest.mark.asyncio
    async def test_copyright_clearance_verification(self, copyright_analyzer, sample_audio_content):
        """Test copyright clearance verification"""
        audio_data = sample_audio_content
        
        clearance_verification = await copyright_analyzer.verify_copyright_clearance(
            content_data=audio_data,
            content_type=ContentType.AUDIO,
            license_documents=["sync_license.pdf", "master_license.pdf"],
            usage_rights=["streaming", "download", "commercial_use"]
        )
        
        assert 'clearance_status' in clearance_verification
        assert 'verified_rights' in clearance_verification
        assert 'missing_clearances' in clearance_verification
        assert 'license_validity' in clearance_verification
        
        # Test clearance status
        status = clearance_verification['clearance_status']
        assert status in ['fully_cleared', 'partially_cleared', 'not_cleared', 'verification_needed']
        
        # Test verified rights
        verified_rights = clearance_verification['verified_rights']
        assert isinstance(verified_rights, list)


class TestContentFingerprinter:
    """Tests for content fingerprinting algorithms"""
    
    @pytest.mark.asyncio
    async def test_generate_audio_fingerprint(self, content_fingerprinter, sample_audio_content):
        """Test audio fingerprint generation"""
        audio_data = sample_audio_content
        
        fingerprint = await content_fingerprinter.generate_audio_fingerprint(
            audio_data=audio_data,
            fingerprint_algorithm="chromaprint",
            quality_level="high"
        )
        
        assert 'fingerprint_hash' in fingerprint
        assert 'fingerprint_length' in fingerprint
        assert 'confidence_score' in fingerprint
        assert 'algorithm_version' in fingerprint
        
        # Test fingerprint validity
        fp_hash = fingerprint['fingerprint_hash']
        assert isinstance(fp_hash, str)
        assert len(fp_hash) > 0
        
        confidence = fingerprint['confidence_score']
        assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_generate_visual_fingerprint(self, content_fingerprinter, sample_video_content):
        """Test visual fingerprint generation"""
        video_data = sample_video_content
        
        visual_fingerprint = await content_fingerprinter.generate_visual_fingerprint(
            video_data=video_data,
            fingerprint_type="perceptual_hash",
            frame_extraction_method="keyframes"
        )
        
        assert 'visual_hash' in visual_fingerprint
        assert 'keyframe_hashes' in visual_fingerprint
        assert 'scene_signatures' in visual_fingerprint
        assert 'color_histogram' in visual_fingerprint
        
        # Test keyframe hashes
        keyframe_hashes = visual_fingerprint['keyframe_hashes']
        assert len(keyframe_hashes) > 0
        
        for kf_hash in keyframe_hashes:
            assert 'timestamp' in kf_hash
            assert 'hash_value' in kf_hash
            assert 'frame_number' in kf_hash
    
    @pytest.mark.asyncio
    async def test_generate_metadata_fingerprint(self, content_fingerprinter, sample_video_content):
        """Test metadata fingerprint generation"""
        video_data = sample_video_content
        
        metadata_fingerprint = await content_fingerprinter.generate_metadata_fingerprint(
            content_data=video_data,
            include_fields=["title", "description", "tags", "technical_metadata"],
            hash_algorithm="sha256"
        )
        
        assert 'metadata_hash' in metadata_fingerprint
        assert 'field_hashes' in metadata_fingerprint
        assert 'normalized_metadata' in metadata_fingerprint
        
        # Test metadata hash validity
        metadata_hash = metadata_fingerprint['metadata_hash']
        assert len(metadata_hash) == 64  # SHA256 length
        assert all(c in '0123456789abcdef' for c in metadata_hash.lower())
    
    @pytest.mark.asyncio
    async def test_compare_fingerprints(self, content_fingerprinter, sample_audio_content):
        """Test fingerprint comparison"""
        audio_data = sample_audio_content
        
        # Generate two fingerprints
        fingerprint1 = await content_fingerprinter.generate_audio_fingerprint(
            audio_data=audio_data,
            fingerprint_algorithm="chromaprint"
        )
        
        # Slightly modify audio data
        modified_audio = audio_data.copy()
        modified_audio['title'] = "Modified " + audio_data['title']
        
        fingerprint2 = await content_fingerprinter.generate_audio_fingerprint(
            audio_data=modified_audio,
            fingerprint_algorithm="chromaprint"
        )
        
        # Compare fingerprints
        comparison = await content_fingerprinter.compare_fingerprints(
            fingerprint1=fingerprint1,
            fingerprint2=fingerprint2,
            comparison_method="similarity"
        )
        
        assert 'similarity_score' in comparison
        assert 'match_confidence' in comparison
        assert 'comparison_details' in comparison
        
        # Test similarity score
        similarity = comparison['similarity_score']
        assert 0 <= similarity <= 1
        assert similarity > 0.8  # Should be very similar


class TestLegalComplianceChecker:
    """Tests for legal compliance checking"""
    
    @pytest.mark.asyncio
    async def test_check_platform_compliance(self, legal_compliance_checker, sample_video_content):
        """Test platform-specific compliance checking"""
        video_data = sample_video_content
        
        compliance_results = await legal_compliance_checker.check_platform_compliance(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platforms=[Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM],
            compliance_categories=["content_policy", "community_guidelines", "copyright"]
        )
        
        assert len(compliance_results) == 3  # One for each platform
        
        for result in compliance_results:
            assert 'platform' in result
            assert 'compliance_status' in result
            assert 'policy_violations' in result
            assert 'compliance_score' in result
            assert 'recommendations' in result
            
            # Test compliance score
            score = result['compliance_score']
            assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_check_gdpr_compliance(self, legal_compliance_checker, sample_text_content):
        """Test GDPR compliance checking"""
        text_data = sample_text_content
        
        gdpr_compliance = await legal_compliance_checker.check_gdpr_compliance(
            content_data=text_data,
            data_processing_purposes=["content_analysis", "recommendation_generation"],
            user_consent_status="explicit",
            data_retention_period=timedelta(days=365)
        )
        
        assert 'compliance_status' in gdpr_compliance
        assert 'data_protection_score' in gdpr_compliance
        assert 'privacy_risks' in gdpr_compliance
        assert 'required_actions' in gdpr_compliance
        
        # Test compliance status
        status = gdpr_compliance['compliance_status']
        assert status in ['compliant', 'needs_review', 'non_compliant']
    
    @pytest.mark.asyncio
    async def test_check_accessibility_compliance(self, legal_compliance_checker, sample_video_content):
        """Test accessibility compliance checking"""
        video_data = sample_video_content
        
        accessibility_check = await legal_compliance_checker.check_accessibility_compliance(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            standards=["WCAG_2.1", "ADA", "Section_508"],
            accessibility_features=["captions", "audio_description", "screen_reader_friendly"]
        )
        
        assert 'accessibility_score' in accessibility_check
        assert 'standard_compliance' in accessibility_check
        assert 'missing_features' in accessibility_check
        assert 'remediation_suggestions' in accessibility_check
        
        # Test standard compliance
        standard_compliance = accessibility_check['standard_compliance']
        for standard, compliance_data in standard_compliance.items():
            assert 'compliance_level' in compliance_data
            assert 'violations' in compliance_data
            assert 'score' in compliance_data
    
    @pytest.mark.asyncio
    async def test_check_age_restriction_compliance(self, legal_compliance_checker, sample_video_content):
        """Test age restriction compliance"""
        video_data = sample_video_content
        
        age_compliance = await legal_compliance_checker.check_age_restriction_compliance(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            target_age_groups=["13+", "16+", "18+"],
            jurisdictions=["US", "EU", "UK"]
        )
        
        assert 'age_appropriateness' in age_compliance
        assert 'restriction_recommendations' in age_compliance
        assert 'jurisdiction_compliance' in age_compliance
        assert 'content_warnings' in age_compliance
        
        # Test age appropriateness
        age_appropriateness = age_compliance['age_appropriateness']
        for age_group, appropriateness_data in age_appropriateness.items():
            assert 'suitable' in appropriateness_data
            assert 'confidence' in appropriateness_data
            assert 'reasons' in appropriateness_data


class TestBrandSafetyMonitor:
    """Tests for brand safety monitoring"""
    
    @pytest.mark.asyncio
    async def test_analyze_content_safety(self, brand_safety_monitor, sample_text_content):
        """Test content safety analysis"""
        text_data = sample_text_content
        
        safety_analysis = await brand_safety_monitor.analyze_content_safety(
            content_data=text_data,
            content_type=ContentType.TEXT,
            safety_categories=["hate_speech", "violence", "adult_content", "controversial_topics"],
            sensitivity_level="high"
        )
        
        assert 'overall_safety_score' in safety_analysis
        assert 'category_scores' in safety_analysis
        assert 'detected_issues' in safety_analysis
        assert 'risk_assessment' in safety_analysis
        
        # Test overall safety score
        overall_score = safety_analysis['overall_safety_score']
        assert 0 <= overall_score <= 1
        
        # Test category scores
        category_scores = safety_analysis['category_scores']
        for category, score in category_scores.items():
            assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_monitor_toxic_content(self, brand_safety_monitor, sample_text_content):
        """Test toxic content monitoring"""
        # Create potentially toxic content
        toxic_content = sample_text_content.copy()
        toxic_content['content'] = "This is a test for potentially harmful language detection."
        
        toxicity_analysis = await brand_safety_monitor.monitor_toxic_content(
            content_data=toxic_content,
            toxicity_types=["harassment", "hate_speech", "threats", "profanity"],
            detection_threshold=0.7
        )
        
        assert 'toxicity_score' in toxicity_analysis
        assert 'toxicity_categories' in toxicity_analysis
        assert 'confidence_levels' in toxicity_analysis
        assert 'moderation_recommendations' in toxicity_analysis
        
        # Test toxicity score
        toxicity_score = toxicity_analysis['toxicity_score']
        assert 0 <= toxicity_score <= 1
    
    @pytest.mark.asyncio
    async def test_check_advertiser_friendliness(self, brand_safety_monitor, sample_video_content):
        """Test advertiser-friendliness checking"""
        video_data = sample_video_content
        
        advertiser_check = await brand_safety_monitor.check_advertiser_friendliness(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            advertiser_categories=["family_brands", "tech_companies", "financial_services"],
            brand_safety_requirements="strict"
        )
        
        assert 'advertiser_friendliness_score' in advertiser_check
        assert 'category_suitability' in advertiser_check
        assert 'potential_concerns' in advertiser_check
        assert 'monetization_impact' in advertiser_check
        
        # Test category suitability
        category_suitability = advertiser_check['category_suitability']
        for category, suitability_data in category_suitability.items():
            assert 'suitable' in suitability_data
            assert 'risk_factors' in suitability_data
            assert 'mitigation_suggestions' in suitability_data
    
    @pytest.mark.asyncio
    async def test_analyze_controversy_risk(self, brand_safety_monitor, sample_text_content):
        """Test controversy risk analysis"""
        text_data = sample_text_content
        
        controversy_analysis = await brand_safety_monitor.analyze_controversy_risk(
            content_data=text_data,
            content_type=ContentType.TEXT,
            controversy_topics=["politics", "religion", "social_issues", "conspiracy_theories"],
            risk_tolerance="low"
        )
        
        assert 'controversy_risk_score' in controversy_analysis
        assert 'identified_topics' in controversy_analysis
        assert 'audience_reaction_prediction' in controversy_analysis
        assert 'mitigation_strategies' in controversy_analysis
        
        # Test controversy risk score
        risk_score = controversy_analysis['controversy_risk_score']
        assert 0 <= risk_score <= 1


class TestProtectionIntegrationPerformance:
    """Performance tests for protection integration"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_protection_analysis_performance(self, benchmark, protection_integrator, sample_video_content):
        """Benchmark protection analysis performance"""
        video_data = sample_video_content
        
        async def analyze_protection():
            return await protection_integrator.analyze_content_protection(
                content_data=video_data,
                content_type=ContentType.VIDEO,
                platform=Platform.YOUTUBE,
                creator_id="benchmark_creator"
            )
        
        result = await benchmark(analyze_protection)
        assert isinstance(result, ProtectionReport)
    
    @pytest.mark.asyncio
    async def test_batch_copyright_analysis(self, copyright_analyzer, sample_audio_content, sample_video_content):
        """Test batch copyright analysis performance"""
        content_batch = [
            (sample_audio_content, ContentType.AUDIO),
            (sample_video_content, ContentType.VIDEO),
            (sample_audio_content, ContentType.AUDIO)  # Duplicate for testing
        ]
        
        start_time = datetime.now()
        
        batch_results = await copyright_analyzer.analyze_batch_copyright(content_batch)
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        # Test results
        assert len(batch_results) == 3
        
        # Test performance
        assert analysis_time < 60.0  # Should complete within 1 minute
    
    @pytest.mark.asyncio
    async def test_concurrent_protection_checks(self, protection_integrator, sample_text_content):
        """Test concurrent protection checks"""
        text_data = sample_text_content
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(3):
            task = protection_integrator.check_legal_compliance(
                content_data=text_data,
                content_type=ContentType.TEXT,
                platforms=[Platform.TWITTER],
                jurisdictions=["US"]
            )
            tasks.append(task)
        
        # Execute concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        concurrent_time = (datetime.now() - start_time).total_seconds()
        
        # Test all requests completed successfully
        assert len(results) == 3
        assert all(isinstance(result, LegalComplianceResult) for result in results)
        
        # Test reasonable performance
        assert concurrent_time < 30.0  # Should handle concurrent requests efficiently


class TestProtectionIntegrationEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    @pytest.mark.asyncio
    async def test_protection_analysis_empty_content(self, protection_integrator):
        """Test protection analysis with empty content"""
        empty_content = {"content": "", "title": "", "description": ""}
        
        with pytest.raises(ValidationError):
            await protection_integrator.analyze_content_protection(
                content_data=empty_content,
                content_type=ContentType.TEXT,
                platform=Platform.TWITTER,
                creator_id="test_creator"
            )
    
    @pytest.mark.asyncio
    async def test_copyright_analysis_corrupted_content(self, copyright_analyzer):
        """Test copyright analysis with corrupted content"""
        corrupted_content = {
            "title": "Test Content",
            "audio_data": "corrupted_binary_data",
            "format": "mp3"
        }
        
        with pytest.raises(ProtectionError):
            await copyright_analyzer.detect_audio_copyright(
                audio_data=corrupted_content,
                detection_sensitivity="high"
            )
    
    @pytest.mark.asyncio
    async def test_fingerprint_generation_unsupported_format(self, content_fingerprinter):
        """Test fingerprint generation with unsupported format"""
        unsupported_content = {
            "title": "Test Content",
            "data": "some_data",
            "format": "unsupported_format"
        }
        
        with pytest.raises(ValidationError):
            await content_fingerprinter.generate_audio_fingerprint(
                audio_data=unsupported_content,
                fingerprint_algorithm="chromaprint"
            )
    
    @pytest.mark.asyncio
    async def test_brand_safety_analysis_timeout(self, brand_safety_monitor, sample_text_content):
        """Test brand safety analysis timeout handling"""
        text_data = sample_text_content
        
        try:
            # Set timeout to test timeout handling
            safety_analysis = await asyncio.wait_for(
                brand_safety_monitor.analyze_content_safety(
                    content_data=text_data,
                    content_type=ContentType.TEXT,
                    safety_categories=["hate_speech", "violence", "adult_content"],
                    sensitivity_level="high"
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Should complete within timeout
            assert 'overall_safety_score' in safety_analysis
            
        except asyncio.TimeoutError:
            pytest.fail("Brand safety analysis timed out")


class TestProtectionDataValidation:
    """Tests for protection data validation and accuracy"""
    
    @pytest.mark.asyncio
    async def test_protection_score_consistency(self, protection_integrator, sample_video_content):
        """Test consistency of protection scores"""
        video_data = sample_video_content
        
        # Analyze same content multiple times
        report1 = await protection_integrator.analyze_content_protection(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE,
            creator_id="consistency_test"
        )
        
        report2 = await protection_integrator.analyze_content_protection(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE,
            creator_id="consistency_test"
        )
        
        # Scores should be consistent
        score_diff = abs(report1.protection_score - report2.protection_score)
        assert score_diff < 0.1  # Within 10% variance
    
    @pytest.mark.asyncio
    async def test_fingerprint_uniqueness(self, content_fingerprinter, sample_audio_content):
        """Test uniqueness of content fingerprints"""
        audio_data = sample_audio_content
        
        # Generate fingerprints for same content
        fingerprint1 = await content_fingerprinter.generate_audio_fingerprint(
            audio_data=audio_data,
            fingerprint_algorithm="chromaprint"
        )
        
        fingerprint2 = await content_fingerprinter.generate_audio_fingerprint(
            audio_data=audio_data,
            fingerprint_algorithm="chromaprint"
        )
        
        # Fingerprints should be identical for same content
        assert fingerprint1['fingerprint_hash'] == fingerprint2['fingerprint_hash']
    
    @pytest.mark.asyncio
    async def test_compliance_score_validation(self, legal_compliance_checker, sample_text_content):
        """Test validation of compliance scores"""
        text_data = sample_text_content
        
        compliance_results = await legal_compliance_checker.check_platform_compliance(
            content_data=text_data,
            content_type=ContentType.TEXT,
            platforms=[Platform.TWITTER, Platform.INSTAGRAM],
            compliance_categories=["content_policy", "community_guidelines"]
        )
        
        for result in compliance_results:
            # All scores should be valid
            score = result['compliance_score']
            assert 0 <= score <= 1
            
            # Status should match score
            status = result['compliance_status']
            if score >= 0.8:
                assert status in ['compliant', 'good']
            elif score >= 0.6:
                assert status in ['warning', 'needs_review']
            else:
                assert status in ['violation', 'non_compliant']
