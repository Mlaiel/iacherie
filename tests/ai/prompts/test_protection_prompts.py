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
Advanced Protection Prompts Tests
Ultra-professional test suite for AI Protection Prompts system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from ai.prompts.protection_prompts import (
    AIProtectionPrompts, ProtectionLevel, ContentType, FingerprintingMethod,
    MonitoringPlatform, ProtectionContext, BlockchainProtectionPrompts,
    get_protection_prompts, create_protection_context, PROTECTION_PROMPTS_REGISTRY
)


class TestProtectionPrompts:
    """Ultra-comprehensive test suite for Protection Prompts"""
    
    @pytest.fixture
    async def protection_prompts(self):
        """Create a fresh AIProtectionPrompts instance for each test"""
        prompts = AIProtectionPrompts()
        await prompts.initialize()
        yield prompts
        await prompts.cleanup()
    
    @pytest.fixture
    def sample_audio_protection_context(self):
        """Create sample audio protection context for testing"""
        return ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.ENTERPRISE,
            fingerprinting_methods=[
                FingerprintingMethod.SPECTRAL,
                FingerprintingMethod.CHROMAPRINT,
                FingerprintingMethod.AI_SIGNATURE
            ],
            monitoring_platforms=[
                MonitoringPlatform.SPOTIFY,
                MonitoringPlatform.YOUTUBE,
                MonitoringPlatform.SOUNDCLOUD
            ],
            legal_requirements={
                "dmca_compliance": True,
                "gdpr_compliance": True,
                "copyright_jurisdiction": "EU",
                "takedown_automation": True,
                "legal_documentation": True
            },
            technical_specs={
                "sample_rate": 48000,
                "bit_depth": 24,
                "channels": 2,
                "format": "WAV",
                "fingerprint_strength": "high",
                "watermark_type": "inaudible",
                "blockchain_network": "ethereum"
            }
        )
    
    @pytest.fixture
    def sample_video_protection_context(self):
        """Create sample video protection context for testing"""
        return ProtectionContext(
            content_type=ContentType.VIDEO,
            protection_level=ProtectionLevel.BLOCKCHAIN,
            fingerprinting_methods=[
                FingerprintingMethod.PERCEPTUAL,
                FingerprintingMethod.WATERMARK,
                FingerprintingMethod.BLOCKCHAIN
            ],
            monitoring_platforms=[
                MonitoringPlatform.YOUTUBE,
                MonitoringPlatform.TIKTOK,
                MonitoringPlatform.FACEBOOK
            ],
            legal_requirements={
                "content_id_registration": True,
                "copyright_metadata": True,
                "usage_tracking": True,
                "revenue_protection": True
            },
            technical_specs={
                "resolution": "4K",
                "framerate": 60,
                "codec": "H.264",
                "bitrate": 50000000,
                "watermark_opacity": 0.1,
                "fingerprint_intervals": 5,
                "blockchain_gas_limit": 200000
            }
        )
    
    @pytest.fixture
    def sample_image_protection_context(self):
        """Create sample image protection context for testing"""
        return ProtectionContext(
            content_type=ContentType.IMAGE,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[
                FingerprintingMethod.PERCEPTUAL,
                FingerprintingMethod.WATERMARK
            ],
            monitoring_platforms=[
                MonitoringPlatform.INSTAGRAM,
                MonitoringPlatform.GENERIC_WEB
            ],
            legal_requirements={
                "exif_copyright": True,
                "reverse_image_search_monitoring": True,
                "usage_licensing_tracking": True
            },
            technical_specs={
                "resolution": "high",
                "format": "JPEG",
                "quality": 95,
                "watermark_position": "bottom_right",
                "fingerprint_algorithm": "phash"
            }
        )
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_protection_prompts_initialization(self, protection_prompts):
        """Test AIProtectionPrompts initialization"""
        assert protection_prompts is not None
        assert hasattr(protection_prompts, 'protection_templates')
        assert hasattr(protection_prompts, 'fingerprinting_algorithms')
        assert hasattr(protection_prompts, 'legal_templates')
        
        assert isinstance(protection_prompts.protection_templates, dict)
        assert isinstance(protection_prompts.fingerprinting_algorithms, dict)
        assert isinstance(protection_prompts.legal_templates, dict)
    
    @pytest.mark.asyncio
    async def test_protection_registry_loading(self, protection_prompts):
        """Test that protection registry is properly loaded"""
        registry = PROTECTION_PROMPTS_REGISTRY
        assert registry is not None
        assert isinstance(registry, dict)
        
        # Check that all content types are represented
        for content_type in ContentType:
            assert content_type in registry
            
        # Check that each content type has all protection levels
        for content_type in ContentType:
            content_protections = registry[content_type]
            for protection_level in ProtectionLevel:
                assert protection_level in content_protections
    
    # ===== AUDIO PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_audio_basic_protection_prompts(self, protection_prompts):
        """Test basic audio protection prompts generation"""
        basic_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.BASIC,
            fingerprinting_methods=[FingerprintingMethod.SPECTRAL],
            monitoring_platforms=[MonitoringPlatform.YOUTUBE],
            legal_requirements={"dmca_compliance": True},
            technical_specs={
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "MP3"
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(basic_context)
        
        assert result["success"] is True
        assert "prompt" in result
        assert "metadata" in result
        
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify audio protection elements
        assert "audio" in prompt.lower()
        assert "spectral" in prompt.lower() or "fingerprinting" in prompt.lower()
        assert "youtube" in prompt.lower()
        assert "dmca" in prompt.lower()
        assert "44100" in prompt or "44.1" in prompt
        assert "mp3" in prompt.lower()
        
        # Verify metadata
        assert metadata["content_type"] == "audio"
        assert metadata["protection_level"] == "basic"
        assert "fingerprinting_methods" in metadata
    
    @pytest.mark.asyncio
    async def test_audio_enterprise_protection_prompts(self, protection_prompts, sample_audio_protection_context):
        """Test enterprise audio protection prompts generation"""
        result = await protection_prompts.generate_protection_prompt(sample_audio_protection_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify enterprise-level features
        assert "enterprise" in prompt.lower() or "advanced" in prompt.lower()
        assert "spectral" in prompt.lower()
        assert "chromaprint" in prompt.lower()
        assert "ai signature" in prompt.lower() or "ai_signature" in prompt.lower()
        assert "spotify" in prompt.lower()
        assert "gdpr" in prompt.lower()
        assert "blockchain" in prompt.lower() or "ethereum" in prompt.lower()
        assert "inaudible" in prompt.lower() or "watermark" in prompt.lower()
        
        # Verify technical specifications
        assert "48000" in prompt or "48" in prompt
        assert "24-bit" in prompt or "24 bit" in prompt
        assert "wav" in prompt.lower()
        
        # Verify comprehensive monitoring
        assert len(metadata["monitoring_platforms"]) >= 3
        assert len(metadata["fingerprinting_methods"]) >= 2
    
    @pytest.mark.asyncio
    async def test_audio_blockchain_protection_prompts(self, protection_prompts):
        """Test blockchain audio protection prompts"""
        blockchain_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.BLOCKCHAIN,
            fingerprinting_methods=[FingerprintingMethod.BLOCKCHAIN, FingerprintingMethod.AI_SIGNATURE],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "smart_contract_protection": True,
                "decentralized_copyright": True,
                "nft_integration": True
            },
            technical_specs={
                "blockchain_network": "polygon",
                "smart_contract_address": "0x1234567890abcdef",
                "gas_optimization": True,
                "ipfs_storage": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(blockchain_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify blockchain features
        assert "blockchain" in prompt.lower()
        assert "smart contract" in prompt.lower()
        assert "nft" in prompt.lower() or "decentralized" in prompt.lower()
        assert "polygon" in prompt.lower() or "ethereum" in prompt.lower()
        assert "ipfs" in prompt.lower()
        assert "gas" in prompt.lower()
    
    # ===== VIDEO PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_video_protection_prompts(self, protection_prompts, sample_video_protection_context):
        """Test video protection prompts generation"""
        result = await protection_prompts.generate_protection_prompt(sample_video_protection_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify video protection elements
        assert "video" in prompt.lower()
        assert "4k" in prompt.lower() or "resolution" in prompt.lower()
        assert "60" in prompt or "framerate" in prompt.lower()
        assert "h.264" in prompt.lower() or "codec" in prompt.lower()
        assert "watermark" in prompt.lower()
        assert "perceptual" in prompt.lower()
        assert "youtube" in prompt.lower()
        assert "content id" in prompt.lower() or "content_id" in prompt.lower()
        assert "revenue protection" in prompt.lower() or "monetization" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_video_content_id_registration(self, protection_prompts):
        """Test video Content ID registration prompts"""
        content_id_context = ProtectionContext(
            content_type=ContentType.VIDEO,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.PERCEPTUAL],
            monitoring_platforms=[MonitoringPlatform.YOUTUBE],
            legal_requirements={
                "content_id_registration": True,
                "automatic_claiming": True,
                "revenue_tracking": True,
                "usage_policy_enforcement": True
            },
            technical_specs={
                "minimum_duration": 30,
                "audio_quality_threshold": "high",
                "video_quality_threshold": "720p",
                "reference_file_format": "ProRes"
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(content_id_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify Content ID specific features
        assert "content id" in prompt.lower()
        assert "automatic" in prompt.lower() or "claiming" in prompt.lower()
        assert "revenue" in prompt.lower()
        assert "usage policy" in prompt.lower() or "policy" in prompt.lower()
        assert "30" in prompt or "duration" in prompt.lower()
        assert "720p" in prompt or "quality" in prompt.lower()
        assert "prores" in prompt.lower() or "reference" in prompt.lower()
    
    # ===== IMAGE PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_image_protection_prompts(self, protection_prompts, sample_image_protection_context):
        """Test image protection prompts generation"""
        result = await protection_prompts.generate_protection_prompt(sample_image_protection_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify image protection elements
        assert "image" in prompt.lower()
        assert "watermark" in prompt.lower()
        assert "perceptual" in prompt.lower() or "fingerprint" in prompt.lower()
        assert "instagram" in prompt.lower()
        assert "exif" in prompt.lower()
        assert "reverse image search" in prompt.lower() or "reverse_image_search" in prompt.lower()
        assert "jpeg" in prompt.lower()
        assert "bottom right" in prompt.lower() or "position" in prompt.lower()
        assert "phash" in prompt.lower() or "hash" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_image_reverse_search_monitoring(self, protection_prompts):
        """Test image reverse search monitoring prompts"""
        reverse_search_context = ProtectionContext(
            content_type=ContentType.IMAGE,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.PERCEPTUAL],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "reverse_image_search_monitoring": True,
                "unauthorized_usage_detection": True,
                "automated_takedown_requests": True,
                "usage_reporting": True
            },
            technical_specs={
                "search_engines": ["google", "bing", "yandex", "tineye"],
                "crawling_frequency": "daily",
                "similarity_threshold": 0.85,
                "monitoring_domains": "all_web"
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(reverse_search_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify reverse search monitoring features
        assert "reverse image search" in prompt.lower()
        assert "unauthorized" in prompt.lower()
        assert "takedown" in prompt.lower()
        assert "google" in prompt.lower() or "tineye" in prompt.lower()
        assert "daily" in prompt.lower() or "crawling" in prompt.lower()
        assert "similarity" in prompt.lower() or "threshold" in prompt.lower()
        assert "0.85" in prompt or "85%" in prompt
    
    # ===== TEXT PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_text_protection_prompts(self, protection_prompts):
        """Test text content protection prompts"""
        text_context = ProtectionContext(
            content_type=ContentType.TEXT,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.AI_SIGNATURE],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "plagiarism_detection": True,
                "ai_generated_content_marking": True,
                "copyright_attribution": True,
                "usage_licensing": True
            },
            technical_specs={
                "text_fingerprinting_algorithm": "semantic_hashing",
                "similarity_detection_threshold": 0.8,
                "language_support": ["en", "de", "fr", "es"],
                "ai_detection_confidence": 0.95
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(text_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify text protection elements
        assert "text" in prompt.lower()
        assert "plagiarism" in prompt.lower()
        assert "ai signature" in prompt.lower() or "ai_signature" in prompt.lower()
        assert "semantic" in prompt.lower() or "fingerprinting" in prompt.lower()
        assert "0.8" in prompt or "80%" in prompt
        assert "language" in prompt.lower()
        assert "ai detection" in prompt.lower() or "ai_detection" in prompt.lower()
        assert "0.95" in prompt or "95%" in prompt
    
    # ===== MIXED MEDIA PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_mixed_media_protection_prompts(self, protection_prompts):
        """Test mixed media content protection prompts"""
        mixed_media_context = ProtectionContext(
            content_type=ContentType.MIXED_MEDIA,
            protection_level=ProtectionLevel.ENTERPRISE,
            fingerprinting_methods=[
                FingerprintingMethod.SPECTRAL,
                FingerprintingMethod.PERCEPTUAL,
                FingerprintingMethod.AI_SIGNATURE,
                FingerprintingMethod.BLOCKCHAIN
            ],
            monitoring_platforms=[
                MonitoringPlatform.YOUTUBE,
                MonitoringPlatform.INSTAGRAM,
                MonitoringPlatform.TIKTOK,
                MonitoringPlatform.GENERIC_WEB
            ],
            legal_requirements={
                "comprehensive_protection": True,
                "multi_format_monitoring": True,
                "cross_platform_enforcement": True,
                "unified_reporting": True
            },
            technical_specs={
                "audio_fingerprinting": "chromaprint",
                "video_fingerprinting": "perceptual_hash",
                "image_fingerprinting": "phash",
                "text_fingerprinting": "semantic_hash",
                "blockchain_integration": True,
                "ai_powered_detection": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(mixed_media_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify comprehensive mixed media protection
        assert "mixed media" in prompt.lower() or "multimedia" in prompt.lower()
        assert "comprehensive" in prompt.lower()
        assert "audio" in prompt.lower() and "video" in prompt.lower() and "image" in prompt.lower()
        assert "chromaprint" in prompt.lower()
        assert "perceptual" in prompt.lower()
        assert "phash" in prompt.lower()
        assert "semantic" in prompt.lower()
        assert "cross-platform" in prompt.lower() or "cross platform" in prompt.lower()
        assert "unified" in prompt.lower()
    
    # ===== FINGERPRINTING ALGORITHM TESTS =====
    
    @pytest.mark.asyncio
    async def test_spectral_fingerprinting_prompts(self, protection_prompts):
        """Test spectral fingerprinting algorithm prompts"""
        spectral_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.SPECTRAL],
            monitoring_platforms=[MonitoringPlatform.SPOTIFY],
            legal_requirements={},
            technical_specs={
                "fft_size": 2048,
                "hop_length": 512,
                "frequency_bands": 32,
                "time_resolution": 0.1,
                "spectral_features": ["mfcc", "chroma", "spectral_centroid"]
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(spectral_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify spectral fingerprinting features
        assert "spectral" in prompt.lower()
        assert "fft" in prompt.lower()
        assert "2048" in prompt
        assert "512" in prompt
        assert "frequency" in prompt.lower()
        assert "mfcc" in prompt.lower()
        assert "chroma" in prompt.lower()
        assert "spectral centroid" in prompt.lower() or "centroid" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_perceptual_fingerprinting_prompts(self, protection_prompts):
        """Test perceptual fingerprinting algorithm prompts"""
        perceptual_context = ProtectionContext(
            content_type=ContentType.VIDEO,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.PERCEPTUAL],
            monitoring_platforms=[MonitoringPlatform.YOUTUBE],
            legal_requirements={},
            technical_specs={
                "frame_sampling_rate": 1,
                "feature_extraction": "deep_learning",
                "hash_algorithm": "locality_sensitive_hashing",
                "robustness_level": "high",
                "compression_resistance": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(perceptual_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify perceptual fingerprinting features
        assert "perceptual" in prompt.lower()
        assert "frame sampling" in prompt.lower() or "frame_sampling" in prompt.lower()
        assert "deep learning" in prompt.lower() or "deep_learning" in prompt.lower()
        assert "locality sensitive" in prompt.lower() or "lsh" in prompt.lower()
        assert "robustness" in prompt.lower()
        assert "compression" in prompt.lower()
    
    # ===== MONITORING PLATFORM TESTS =====
    
    @pytest.mark.asyncio
    async def test_youtube_monitoring_prompts(self, protection_prompts):
        """Test YouTube-specific monitoring prompts"""
        youtube_context = ProtectionContext(
            content_type=ContentType.VIDEO,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.PERCEPTUAL],
            monitoring_platforms=[MonitoringPlatform.YOUTUBE],
            legal_requirements={
                "content_id_integration": True,
                "monetization_claims": True,
                "automated_enforcement": True
            },
            technical_specs={
                "youtube_api_integration": True,
                "content_id_submission": True,
                "policy_enforcement": "strict",
                "revenue_tracking": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(youtube_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify YouTube-specific features
        assert "youtube" in prompt.lower()
        assert "content id" in prompt.lower() or "content_id" in prompt.lower()
        assert "monetization" in prompt.lower()
        assert "automated" in prompt.lower()
        assert "api" in prompt.lower()
        assert "revenue" in prompt.lower()
        assert "strict" in prompt.lower() or "enforcement" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_spotify_monitoring_prompts(self, protection_prompts):
        """Test Spotify-specific monitoring prompts"""
        spotify_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.CHROMAPRINT],
            monitoring_platforms=[MonitoringPlatform.SPOTIFY],
            legal_requirements={
                "royalty_tracking": True,
                "duplicate_detection": True,
                "licensing_verification": True
            },
            technical_specs={
                "spotify_api_access": True,
                "echo_nest_integration": True,
                "audio_features_matching": True,
                "playlist_monitoring": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(spotify_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify Spotify-specific features
        assert "spotify" in prompt.lower()
        assert "chromaprint" in prompt.lower()
        assert "royalty" in prompt.lower()
        assert "duplicate" in prompt.lower()
        assert "licensing" in prompt.lower()
        assert "echo nest" in prompt.lower() or "echonest" in prompt.lower() or "audio features" in prompt.lower()
        assert "playlist" in prompt.lower()
    
    # ===== LEGAL COMPLIANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_dmca_compliance_prompts(self, protection_prompts):
        """Test DMCA compliance prompts"""
        dmca_context = ProtectionContext(
            content_type=ContentType.MIXED_MEDIA,
            protection_level=ProtectionLevel.ADVANCED,
            fingerprinting_methods=[FingerprintingMethod.AI_SIGNATURE],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "dmca_compliance": True,
                "safe_harbor_provisions": True,
                "takedown_automation": True,
                "counter_notification_handling": True,
                "legal_documentation": True
            },
            technical_specs={
                "automated_takedown_generation": True,
                "legal_template_system": True,
                "evidence_collection": True,
                "response_tracking": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(dmca_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify DMCA compliance features
        assert "dmca" in prompt.lower()
        assert "safe harbor" in prompt.lower() or "safe_harbor" in prompt.lower()
        assert "takedown" in prompt.lower()
        assert "counter notification" in prompt.lower() or "counter_notification" in prompt.lower()
        assert "legal documentation" in prompt.lower() or "documentation" in prompt.lower()
        assert "automated" in prompt.lower()
        assert "evidence" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_gdpr_compliance_prompts(self, protection_prompts):
        """Test GDPR compliance prompts"""
        gdpr_context = ProtectionContext(
            content_type=ContentType.MIXED_MEDIA,
            protection_level=ProtectionLevel.ENTERPRISE,
            fingerprinting_methods=[FingerprintingMethod.AI_SIGNATURE],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "gdpr_compliance": True,
                "data_privacy_protection": True,
                "consent_management": True,
                "data_subject_rights": True,
                "privacy_by_design": True
            },
            technical_specs={
                "data_anonymization": True,
                "consent_tracking": True,
                "data_retention_policies": True,
                "cross_border_data_handling": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(gdpr_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify GDPR compliance features
        assert "gdpr" in prompt.lower()
        assert "privacy" in prompt.lower()
        assert "consent" in prompt.lower()
        assert "data subject" in prompt.lower() or "data_subject" in prompt.lower()
        assert "anonymization" in prompt.lower()
        assert "retention" in prompt.lower()
        assert "cross-border" in prompt.lower() or "cross border" in prompt.lower()
    
    # ===== BLOCKCHAIN PROTECTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_blockchain_integration_prompts(self, protection_prompts):
        """Test blockchain integration prompts"""
        blockchain_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.BLOCKCHAIN,
            fingerprinting_methods=[FingerprintingMethod.BLOCKCHAIN],
            monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
            legal_requirements={
                "smart_contract_copyright": True,
                "decentralized_verification": True,
                "immutable_ownership": True,
                "nft_integration": True
            },
            technical_specs={
                "blockchain_network": "ethereum",
                "smart_contract_language": "solidity",
                "gas_optimization": True,
                "ipfs_integration": True,
                "oracle_integration": True,
                "multi_chain_support": True
            }
        )
        
        result = await protection_prompts.generate_protection_prompt(blockchain_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify blockchain integration features
        assert "blockchain" in prompt.lower()
        assert "smart contract" in prompt.lower() or "smart_contract" in prompt.lower()
        assert "decentralized" in prompt.lower()
        assert "immutable" in prompt.lower()
        assert "nft" in prompt.lower()
        assert "ethereum" in prompt.lower()
        assert "solidity" in prompt.lower()
        assert "gas" in prompt.lower()
        assert "ipfs" in prompt.lower()
        assert "oracle" in prompt.lower()
        assert "multi-chain" in prompt.lower() or "multi chain" in prompt.lower()
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_invalid_content_type_error(self, protection_prompts):
        """Test error handling for invalid content type"""
        with pytest.raises(ValueError) or pytest.raises(TypeError):
            invalid_context = ProtectionContext(
                content_type="invalid_type",
                protection_level=ProtectionLevel.BASIC,
                fingerprinting_methods=[FingerprintingMethod.SPECTRAL],
                monitoring_platforms=[MonitoringPlatform.YOUTUBE],
                legal_requirements={},
                technical_specs={}
            )
            await protection_prompts.generate_protection_prompt(invalid_context)
    
    @pytest.mark.asyncio
    async def test_incompatible_fingerprinting_method_error(self, protection_prompts):
        """Test error handling for incompatible fingerprinting methods"""
        # Try to use audio-specific method on video content
        incompatible_context = ProtectionContext(
            content_type=ContentType.VIDEO,
            protection_level=ProtectionLevel.BASIC,
            fingerprinting_methods=[FingerprintingMethod.CHROMAPRINT],  # Audio-specific
            monitoring_platforms=[MonitoringPlatform.YOUTUBE],
            legal_requirements={},
            technical_specs={}
        )
        
        result = await protection_prompts.generate_protection_prompt(incompatible_context)
        
        # Should either succeed with warning or fail gracefully
        if not result["success"]:
            assert "incompatible" in result["error"].lower() or "mismatch" in result["error"].lower()
        else:
            assert "warnings" in result and len(result["warnings"]) > 0
    
    @pytest.mark.asyncio
    async def test_missing_technical_specs_handling(self, protection_prompts):
        """Test handling of missing technical specifications"""
        minimal_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel.BASIC,
            fingerprinting_methods=[FingerprintingMethod.SPECTRAL],
            monitoring_platforms=[MonitoringPlatform.SPOTIFY],
            legal_requirements={},
            technical_specs={}  # Empty specs
        )
        
        result = await protection_prompts.generate_protection_prompt(minimal_context)
        
        # Should succeed with default values
        assert result["success"] is True
        assert "used_defaults" in result["metadata"]
        assert len(result["metadata"]["used_defaults"]) > 0
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_protection_prompt_generation_performance(self, protection_prompts, sample_audio_protection_context):
        """Test protection prompt generation performance"""
        # Test single generation performance
        start_time = datetime.now()
        result = await protection_prompts.generate_protection_prompt(sample_audio_protection_context)
        single_duration = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert single_duration < 3.0  # Should complete within 3 seconds
        
        # Test batch generation performance
        contexts = [sample_audio_protection_context] * 5
        
        start_time = datetime.now()
        results = await protection_prompts.generate_batch_protection_prompts(contexts)
        batch_duration = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 5
        assert batch_duration < 10.0  # Should complete within 10 seconds
        assert batch_duration < single_duration * 5  # Should be more efficient than individual calls
    
    @pytest.mark.asyncio
    async def test_fingerprinting_algorithm_performance(self, protection_prompts):
        """Test fingerprinting algorithm recommendation performance"""
        test_contexts = []
        
        # Create contexts for different content types
        for content_type in ContentType:
            context = ProtectionContext(
                content_type=content_type,
                protection_level=ProtectionLevel.ADVANCED,
                fingerprinting_methods=[],  # Let system recommend
                monitoring_platforms=[MonitoringPlatform.GENERIC_WEB],
                legal_requirements={},
                technical_specs={}
            )
            test_contexts.append(context)
        
        start_time = datetime.now()
        for context in test_contexts:
            result = await protection_prompts.recommend_fingerprinting_methods(context)
            assert result["success"] is True
            assert len(result["recommended_methods"]) > 0
        
        total_duration = (datetime.now() - start_time).total_seconds()
        assert total_duration < 5.0  # Should complete all recommendations within 5 seconds
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_comprehensive_protection_workflow(self, protection_prompts):
        """Test comprehensive protection workflow integration"""
        # Step 1: Content analysis and protection level recommendation
        content_analysis_result = await protection_prompts.analyze_content_protection_needs({
            "content_type": "audio",
            "commercial_use": True,
            "distribution_platforms": ["spotify", "youtube", "apple_music"],
            "target_audience": "global",
            "budget": "enterprise"
        })
        
        assert content_analysis_result["success"] is True
        recommended_level = content_analysis_result["recommended_protection_level"]
        
        # Step 2: Fingerprinting method selection
        fingerprinting_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel(recommended_level),
            fingerprinting_methods=[],
            monitoring_platforms=[],
            legal_requirements={},
            technical_specs={}
        )
        
        fingerprinting_result = await protection_prompts.recommend_fingerprinting_methods(fingerprinting_context)
        assert fingerprinting_result["success"] is True
        recommended_methods = fingerprinting_result["recommended_methods"]
        
        # Step 3: Monitoring platform selection
        monitoring_result = await protection_prompts.recommend_monitoring_platforms(fingerprinting_context)
        assert monitoring_result["success"] is True
        recommended_platforms = monitoring_result["recommended_platforms"]
        
        # Step 4: Legal requirements assessment
        legal_result = await protection_prompts.assess_legal_requirements({
            "jurisdiction": "EU",
            "content_type": "audio",
            "commercial_use": True,
            "international_distribution": True
        })
        assert legal_result["success"] is True
        legal_requirements = legal_result["requirements"]
        
        # Step 5: Complete protection prompt generation
        final_context = ProtectionContext(
            content_type=ContentType.AUDIO,
            protection_level=ProtectionLevel(recommended_level),
            fingerprinting_methods=[FingerprintingMethod(method) for method in recommended_methods[:3]],
            monitoring_platforms=[MonitoringPlatform(platform) for platform in recommended_platforms[:3]],
            legal_requirements=legal_requirements,
            technical_specs={
                "sample_rate": 48000,
                "bit_depth": 24,
                "format": "WAV"
            }
        )
        
        final_result = await protection_prompts.generate_protection_prompt(final_context)
        assert final_result["success"] is True
        
        # Verify comprehensive integration
        final_prompt = final_result["prompt"]
        assert len(final_prompt) > 500  # Should be comprehensive
        assert recommended_level.lower() in final_prompt.lower()
        assert any(method.lower() in final_prompt.lower() for method in recommended_methods[:2])
        assert any(platform.lower() in final_prompt.lower() for platform in recommended_platforms[:2])
        
        # Step 6: Implementation guidance
        implementation_result = await protection_prompts.generate_implementation_guide(final_context)
        assert implementation_result["success"] is True
        assert "implementation_steps" in implementation_result
        assert len(implementation_result["implementation_steps"]) > 3
    
    @pytest.mark.asyncio
    async def test_multi_content_type_protection_strategy(self, protection_prompts):
        """Test protection strategy for multiple content types"""
        content_portfolio = {
            "audio_tracks": 50,
            "video_content": 20,
            "images": 200,
            "text_content": 100,
            "mixed_media_projects": 10
        }
        
        strategy_result = await protection_prompts.develop_portfolio_protection_strategy(content_portfolio)
        
        assert strategy_result["success"] is True
        assert "protection_strategies" in strategy_result
        
        strategies = strategy_result["protection_strategies"]
        
        # Verify strategies for all content types
        assert ContentType.AUDIO in strategies
        assert ContentType.VIDEO in strategies
        assert ContentType.IMAGE in strategies
        assert ContentType.TEXT in strategies
        assert ContentType.MIXED_MEDIA in strategies
        
        # Verify cost optimization recommendations
        assert "cost_optimization" in strategy_result
        assert "priority_ranking" in strategy_result
        assert "implementation_timeline" in strategy_result
        
        # Verify budget allocation
        cost_optimization = strategy_result["cost_optimization"]
        assert "total_estimated_cost" in cost_optimization
        assert "cost_per_content_type" in cost_optimization
        assert cost_optimization["total_estimated_cost"] > 0
