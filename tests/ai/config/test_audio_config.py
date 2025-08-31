# -*- coding: utf-8 -*-
"""Comprehensive Tests for Audio Configuration

Expert Team Specifications:
- Lead Dev + AI Architect: Fahed Mlaiel
- Backend Senior Developer: Fahed Mlaiel  
- Machine Learning Engineer: Fahed Mlaiel
- Database Administrator & Data Engineer: Fahed Mlaiel
- Backend Security Specialist: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Developer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer: Fahed Mlaiel

Creator: Fahed Mlaiel (mlaiel@live.de)

⚠️ COPYRIGHT WARNING ⚠️
STRICT INTELLECTUAL PROPERTY PROTECTION

This code, concept, and implementation are the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- ❌ NO copying, cloning, or reproduction without written authorization
- ❌ NO use of concepts, ideas, or implementation patterns
- ❌ NO reverse engineering or code inspiration
- ❌ NO commercial or private use without express permission

LEGAL CONSEQUENCES:
- 🚨 Legal action will be taken against violators
- 🚨 Full prosecution under German and international copyright law
- 🚨 Damages will be claimed
- 🚨 Immediate injunctions

FOR AUTHORIZATION: Contact Fahed Mlaiel at mlaiel@live.de with detailed usage request.

Comprehensive test suite for AudioConfig module ensuring 100% audio quality,
processing reliability, and professional mastering for musicians and content creators.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
import tempfile
import wave
import io

# Importation des modules de test
from . import TEST_CONFIG, TEST_DATA, logger, pytest_marks

# Import du module à tester
try:
    from ai.config.audio_config import AudioConfig, AudioFormat, AudioQuality
    from ai.config.audio_config import SampleRate, BitDepth, NoiseReductionLevel
except ImportError as e:
    logger.error(f"Failed to import AudioConfig: {e}")
    pytest.skip("AudioConfig module not available", allow_module_level=True)

class TestAudioConfig:
    """Tests complets pour la configuration audio."""    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuration avant chaque test."""        self.config = AudioConfig()
        self.test_env = test_environment
        self.sample_audio_data = self._generate_sample_audio_data()
        self.test_audio_files = self._create_test_audio_files()
        logger.info("TestAudioConfig setup completed")
    
    def _generate_sample_audio_data(self) -> Dict[str, Any]:
        """Génère des données audio de test."""        # Générer une sinusoïde de 440Hz (La) pendant 1 seconde
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_signal = np.sin(2 * np.pi * frequency * t)
        
        return {
            "raw_audio": {
                "signal": audio_signal,
                "sample_rate": sample_rate,
                "channels": 1,
                "bit_depth": 16,
                "duration": duration
            },
            "stereo_audio": {
                "signal": np.column_stack([audio_signal, audio_signal * 0.8]),
                "sample_rate": sample_rate,
                "channels": 2,
                "bit_depth": 24,
                "duration": duration
            },
            "high_quality": {
                "sample_rate": 96000,
                "bit_depth": 32,
                "channels": 2,
                "format": "float32"
            },
            "compressed": {
                "format": "mp3",
                "bitrate": 320,
                "sample_rate": 44100,
                "channels": 2
            }
        }
    
    def _create_test_audio_files(self) -> Dict[str, str]:
        """Crée des fichiers audio de test temporaires."""        test_files = {}
        
        # Créer un fichier WAV de test
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
            # Créer un fichier WAV simple
            sample_rate = 44100
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
            
            with wave.open(wav_file.name, 'w') as wav_writer:
                wav_writer.setnchannels(1)
                wav_writer.setsampwidth(2)
                wav_writer.setframerate(sample_rate)
                wav_writer.writeframes(audio_data.tobytes())
            
            test_files['wav'] = wav_file.name
        
        return test_files
    
    @pytest_marks["unit"]
    def test_config_initialization(self):
        """Test l'initialisation de base de la configuration audio."""        assert self.config is not None
        assert hasattr(self.config, 'audio_processor')
        assert hasattr(self.config, 'quality_analyzer')
        assert hasattr(self.config, 'mastering_engine')
        assert hasattr(self.config, 'format_converter')
        assert hasattr(self.config, 'realtime_processor')
        assert hasattr(self.config, 'spectrum_analyzer')
        logger.info("Audio configuration initialization test passed")
    
    @pytest_marks["unit"]
    def test_audio_quality_analysis(self):
        """Test l'analyse de qualité audio."""        audio_data = self.sample_audio_data["raw_audio"]
        
        # Analyse de qualité basique
        quality_analysis = self.config.analyze_audio_quality(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            analysis_type="comprehensive"
        )
        
        assert "overall_quality_score" in quality_analysis
        assert "dynamic_range" in quality_analysis
        assert "frequency_response" in quality_analysis
        assert "noise_floor" in quality_analysis
        assert "peak_levels" in quality_analysis
        assert "rms_levels" in quality_analysis
        
        # Vérifier que le score de qualité est dans la plage attendue
        assert 0 <= quality_analysis["overall_quality_score"] <= 10
        
        # Analyse de distorsion
        distortion_analysis = self.config.analyze_distortion(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"]
        )
        
        assert "thd_percent" in distortion_analysis  # Total Harmonic Distortion
        assert "thd_plus_n" in distortion_analysis   # THD+N
        assert "harmonic_analysis" in distortion_analysis
        assert "intermodulation_distortion" in distortion_analysis
        
        # Analyse spectrale
        spectral_analysis = self.config.analyze_spectrum(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            window_size=2048,
            overlap=0.5
        )
        
        assert "frequency_bins" in spectral_analysis
        assert "magnitude_spectrum" in spectral_analysis
        assert "phase_spectrum" in spectral_analysis
        assert "spectral_centroid" in spectral_analysis
        assert "spectral_rolloff" in spectral_analysis
        
        logger.info("Audio quality analysis test passed")
    
    @pytest_marks["unit"]
    def test_audio_processing_pipeline(self):
        """Test le pipeline de traitement audio."""        audio_data = self.sample_audio_data["stereo_audio"]
        
        # Configuration du pipeline de traitement
        processing_pipeline = self.config.create_processing_pipeline([
            {"type": "noise_reduction", "strength": 0.3},
            {"type": "eq", "bands": [
                {"frequency": 100, "gain": -2, "q": 1.0},
                {"frequency": 1000, "gain": 1, "q": 0.7},
                {"frequency": 8000, "gain": 2, "q": 1.2}
            ]},
            {"type": "compressor", "ratio": 4.0, "threshold": -12, "attack": 5, "release": 50},
            {"type": "limiter", "threshold": -1, "release": 10}
        ])
        
        assert processing_pipeline["pipeline_created"] is True
        assert len(processing_pipeline["processing_stages"]) == 4
        
        # Exécution du pipeline
        processed_audio = self.config.process_audio_pipeline(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            pipeline_config=processing_pipeline
        )
        
        assert processed_audio["success"] is True
        assert "processed_signal" in processed_audio
        assert "processing_metrics" in processed_audio
        assert processed_audio["processed_signal"].shape == audio_data["signal"].shape
        
        # Vérifier que le traitement a été appliqué
        assert not np.array_equal(processed_audio["processed_signal"], audio_data["signal"])
        
        logger.info("Audio processing pipeline test passed")
    
    @pytest_marks["business_logic"]
    def test_musician_specific_processing(self):
        """Test le traitement spécifique pour musiciens."""        # Test traitement pour musicien électronique
        electronic_music_data = {
            "signal": self.sample_audio_data["stereo_audio"]["signal"],
            "sample_rate": 44100,
            "genre": "electronic",
            "sub_genre": "house",
            "target_platform": "spotify"
        }
        
        electronic_processing = self.config.process_for_musician(
            audio_data=electronic_music_data,
            musician_type="electronic_producer",
            processing_goals=["club_ready", "streaming_optimized", "loud_master"]
        )
        
        assert electronic_processing["success"] is True
        assert "mastered_audio" in electronic_processing
        assert "lufs_measurement" in electronic_processing
        assert "peak_measurement" in electronic_processing
        assert electronic_processing["lufs_measurement"] >= -16  # Spotify loudness
        
        # Test traitement pour musicien acoustique
        acoustic_music_data = {
            "signal": self.sample_audio_data["raw_audio"]["signal"],
            "sample_rate": 96000,  # Haute résolution
            "genre": "folk",
            "instruments": ["acoustic_guitar", "vocals"],
            "recording_environment": "studio"
        }
        
        acoustic_processing = self.config.process_for_musician(
            audio_data=acoustic_music_data,
            musician_type="singer_songwriter",
            processing_goals=["natural_sound", "vocal_clarity", "audiophile_quality"]
        )
        
        assert acoustic_processing["success"] is True
        assert "natural_dynamics_preserved" in acoustic_processing
        assert "vocal_enhancement_applied" in acoustic_processing
        assert acoustic_processing["bit_depth"] >= 24  # Haute qualité
        
        # Test traitement pour musicien hip-hop
        hiphop_processing = self.config.process_for_musician(
            audio_data=electronic_music_data,
            musician_type="hip_hop_producer",
            processing_goals=["punchy_drums", "vocal_presence", "radio_ready"]
        )
        
        assert hiphop_processing["success"] is True
        assert "drum_enhancement" in hiphop_processing
        assert "vocal_processing" in hiphop_processing
        
        logger.info("Musician specific processing test passed")
    
    @pytest_marks["performance"]
    def test_realtime_audio_processing(self):
        """Test le traitement audio en temps réel."""        # Configuration du processeur temps réel
        realtime_config = {
            "buffer_size": 512,  # samples
            "sample_rate": 44100,
            "channels": 2,
            "latency_target": 10,  # ms
            "processing_chain": [
                {"type": "eq", "enabled": True},
                {"type": "compressor", "enabled": True},
                {"type": "reverb", "enabled": False}
            ]
        }
        
        realtime_setup = self.config.setup_realtime_processing(realtime_config)
        assert realtime_setup["realtime_ready"] is True
        assert realtime_setup["estimated_latency_ms"] <= realtime_config["latency_target"]
        
        # Test traitement de buffers en temps réel
        num_buffers = 100
        buffer_size = realtime_config["buffer_size"]
        start_time = time.time()
        
        for i in range(num_buffers):
            # Générer un buffer audio
            test_buffer = np.random.random((buffer_size, 2)) * 0.1
            
            # Traiter le buffer
            processed_buffer = self.config.process_realtime_buffer(
                audio_buffer=test_buffer,
                processor_id=realtime_setup["processor_id"]
            )
            
            assert processed_buffer["success"] is True
            assert processed_buffer["processed_buffer"].shape == test_buffer.shape
        
        total_time = time.time() - start_time
        avg_processing_time = (total_time / num_buffers) * 1000  # ms
        
        # Vérifier que le traitement est assez rapide pour le temps réel
        max_allowed_time = (buffer_size / realtime_config["sample_rate"]) * 1000  # ms
        assert avg_processing_time < max_allowed_time * 0.8  # 80% du temps disponible
        
        logger.info(f"Realtime audio processing test passed: {avg_processing_time:.2f}ms avg per buffer")
    
    @pytest_marks["unit"]
    def test_format_conversion_accuracy(self):
        """Test la précision de conversion de formats audio."""        source_audio = self.sample_audio_data["high_quality"]
        
        # Test conversion vers différents formats
        conversion_targets = [
            {"format": "mp3", "bitrate": 320, "sample_rate": 44100},
            {"format": "flac", "compression": 8, "sample_rate": 96000},
            {"format": "wav", "bit_depth": 24, "sample_rate": 48000},
            {"format": "aac", "bitrate": 256, "sample_rate": 44100},
            {"format": "ogg", "quality": 8, "sample_rate": 44100}
        ]
        
        conversion_results = {}
        
        for target in conversion_targets:
            conversion_result = self.config.convert_audio_format(
                audio_data=self.sample_audio_data["stereo_audio"]["signal"],
                source_format={
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "channels": 2
                },
                target_format=target
            )
            
            assert conversion_result["success"] is True
            assert "converted_data" in conversion_result
            assert "quality_metrics" in conversion_result
            assert "file_size_estimate" in conversion_result
            
            conversion_results[target["format"]] = conversion_result
        
        # Vérifier que FLAC a la meilleure qualité
        assert conversion_results["flac"]["quality_metrics"]["quality_score"] >= 9.0
        
        # Vérifier que MP3 320kbps a une qualité acceptable
        assert conversion_results["mp3"]["quality_metrics"]["quality_score"] >= 7.5
        
        # Vérifier les tailles de fichier relatives
        assert conversion_results["flac"]["file_size_estimate"] > conversion_results["mp3"]["file_size_estimate"]
        
        logger.info("Format conversion accuracy test passed")
    
    @pytest_marks["unit"]
    def test_mastering_engine_functionality(self):
        """Test la fonctionnalité du moteur de mastering."""        audio_data = self.sample_audio_data["stereo_audio"]
        
        # Test mastering pour streaming
        streaming_master = self.config.create_streaming_master(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            target_platform="spotify",
            mastering_style="modern"
        )
        
        assert streaming_master["success"] is True
        assert "mastered_audio" in streaming_master
        assert "lufs_measurement" in streaming_master
        assert "true_peak" in streaming_master
        assert "dynamic_range" in streaming_master
        
        # Vérifier la conformité aux standards Spotify
        assert -16 <= streaming_master["lufs_measurement"] <= -14
        assert streaming_master["true_peak"] <= -1.0
        
        # Test mastering pour vinyle
        vinyl_master = self.config.create_vinyl_master(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            vinyl_specifications={
                "rpm": 33,
                "diameter": 12,
                "side_duration": 22  # minutes
            }
        )
        
        assert vinyl_master["success"] is True
        assert "vinyl_optimized_audio" in vinyl_master
        assert "frequency_limitations_applied" in vinyl_master
        assert "stereo_width_adjusted" in vinyl_master
        
        # Test mastering pour CD
        cd_master = self.config.create_cd_master(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            dithering=True,
            noise_shaping=True
        )
        
        assert cd_master["success"] is True
        assert cd_master["final_sample_rate"] == 44100
        assert cd_master["final_bit_depth"] == 16
        assert "dithering_applied" in cd_master
        
        logger.info("Mastering engine functionality test passed")
    
    @pytest_marks["integration"]
    async def test_audio_ai_integration(self):
        """Test l'intégration avec l'IA audio."""        audio_data = self.sample_audio_data["raw_audio"]
        
        # Test analyse IA du contenu audio
        with patch.object(self.config, '_call_audio_ai_service') as mock_ai:
            mock_ai.return_value = {
                "genre_detection": {
                    "primary_genre": "electronic",
                    "sub_genres": ["house", "deep_house"],
                    "confidence": 0.89
                },
                "mood_analysis": {
                    "energy": 0.75,
                    "valence": 0.65,
                    "danceability": 0.82,
                    "tempo": 128
                },
                "instrument_detection": {
                    "instruments": ["synthesizer", "drum_machine", "bass_synth"],
                    "confidence_scores": [0.95, 0.87, 0.78]
                }
            }
            
            ai_analysis = await self.config.analyze_audio_with_ai(
                audio_signal=audio_data["signal"],
                sample_rate=audio_data["sample_rate"],
                analysis_types=["genre", "mood", "instruments"]
            )
            
            assert ai_analysis["genre_detection"]["primary_genre"] == "electronic"
            assert ai_analysis["mood_analysis"]["energy"] > 0.5
            assert len(ai_analysis["instrument_detection"]["instruments"]) > 0
        
        # Test génération audio par IA
        with patch.object(self.config, '_call_audio_generation_ai') as mock_generation:
            mock_generation.return_value = {
                "generated_audio": np.random.random(44100) * 0.5,  # 1 seconde
                "generation_metadata": {
                    "prompt": "electronic house beat",
                    "duration": 1.0,
                    "sample_rate": 44100,
                    "model_used": "audio_generation_v2"
                }
            }
            
            ai_generation = await self.config.generate_audio_with_ai(
                prompt="Generate a 1-second electronic house beat",
                duration=1.0,
                sample_rate=44100,
                style_reference=audio_data["signal"]
            )
            
            assert ai_generation["success"] is True
            assert "generated_audio" in ai_generation
            assert len(ai_generation["generated_audio"]) == 44100
        
        logger.info("Audio AI integration test passed")
    
    @pytest_marks["security"]
    def test_audio_security_validation(self):
        """Test la validation de sécurité audio."""        # Test détection de contenu malveillant
        suspicious_audio = np.random.random(44100) * 2.0  # Volume très élevé
        
        security_check = self.config.validate_audio_security(
            audio_signal=suspicious_audio,
            sample_rate=44100,
            security_level="high"
        )
        
        assert "safety_score" in security_check
        assert "detected_issues" in security_check
        assert "volume_violations" in security_check["detected_issues"]
        
        # Test validation de métadonnées
        metadata_validation = self.config.validate_audio_metadata(
            metadata={
                "title": "Test Track",
                "artist": "Test Artist",
                "duration": 180,
                "file_size": 5000000,
                "format": "wav"
            }
        )
        
        assert metadata_validation["metadata_valid"] is True
        assert "validation_issues" in metadata_validation
        
        # Test détection de plagiat audio
        plagiarism_check = self.config.check_audio_plagiarism(
            audio_signal=self.sample_audio_data["raw_audio"]["signal"],
            sample_rate=44100,
            database_search=True
        )
        
        assert "plagiarism_probability" in plagiarism_check
        assert "similar_tracks" in plagiarism_check
        assert "fingerprint_matches" in plagiarism_check
        
        logger.info("Audio security validation test passed")
    
    @pytest_marks["performance"]
    def test_batch_audio_processing(self):
        """Test le traitement audio en lot."""        # Créer un lot de fichiers audio de test
        audio_batch = []
        for i in range(20):
            audio_item = {
                "id": f"audio_batch_{i:03d}",
                "signal": np.random.random(22050) * 0.5,  # 0.5 seconde
                "sample_rate": 44100,
                "metadata": {
                    "title": f"Test Track {i}",
                    "artist": f"Artist {i % 5}",
                    "genre": ["electronic", "rock", "jazz", "classical", "pop"][i % 5]
                }
            }
            audio_batch.append(audio_item)
        
        start_time = time.time()
        
        # Traitement en lot
        batch_result = self.config.process_audio_batch(
            audio_batch=audio_batch,
            processing_template={
                "normalize": True,
                "eq": {"enabled": True, "preset": "balanced"},
                "compressor": {"enabled": True, "ratio": 3.0},
                "limiter": {"enabled": True, "threshold": -0.5}
            },
            output_format="wav",
            parallel_processing=True
        )
        
        processing_time = time.time() - start_time
        
        assert batch_result["total_processed"] == 20
        assert batch_result["success_rate"] > 0.95
        assert processing_time < 30  # Moins de 30 secondes pour 20 fichiers
        assert len(batch_result["processed_files"]) == 20
        
        logger.info(f"Batch audio processing test passed: {processing_time}s for 20 files")
    
    @pytest_marks["unit"]
    def test_audio_metrics_calculation(self):
        """Test le calcul des métriques audio."""        audio_data = self.sample_audio_data["stereo_audio"]
        
        # Calcul des métriques complètes
        audio_metrics = self.config.calculate_comprehensive_metrics(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"]
        )
        
        # Métriques de niveau
        assert "peak_level_db" in audio_metrics
        assert "rms_level_db" in audio_metrics
        assert "lufs_integrated" in audio_metrics
        assert "lufs_short_term" in audio_metrics
        assert "lufs_momentary" in audio_metrics
        
        # Métriques de dynamique
        assert "dynamic_range_db" in audio_metrics
        assert "crest_factor" in audio_metrics
        assert "peak_to_average_ratio" in audio_metrics
        
        # Métriques spectrales
        assert "spectral_centroid" in audio_metrics
        assert "spectral_bandwidth" in audio_metrics
        assert "spectral_rolloff" in audio_metrics
        assert "zero_crossing_rate" in audio_metrics
        
        # Métriques de qualité
        assert "snr_db" in audio_metrics
        assert "thd_percent" in audio_metrics
        assert "bit_depth_utilization" in audio_metrics
        
        # Vérifier les plages de valeurs
        assert -100 <= audio_metrics["peak_level_db"] <= 0
        assert -100 <= audio_metrics["rms_level_db"] <= 0
        assert 0 <= audio_metrics["crest_factor"] <= 50
        
        logger.info("Audio metrics calculation test passed")
    
    @pytest_marks["business_logic"]
    def test_platform_specific_optimization(self):
        """Test l'optimisation spécifique par plateforme."""        audio_data = self.sample_audio_data["stereo_audio"]
        
        # Optimisation pour Spotify
        spotify_optimization = self.config.optimize_for_platform(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            platform="spotify",
            content_type="music_track"
        )
        
        assert spotify_optimization["success"] is True
        assert spotify_optimization["target_lufs"] == -14
        assert spotify_optimization["true_peak_limit"] == -1.0
        assert "normalization_applied" in spotify_optimization
        
        # Optimisation pour YouTube
        youtube_optimization = self.config.optimize_for_platform(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            platform="youtube",
            content_type="video_audio"
        )
        
        assert youtube_optimization["success"] is True
        assert youtube_optimization["target_lufs"] == -13
        assert "stereo_enhancement" in youtube_optimization
        
        # Optimisation pour TikTok
        tiktok_optimization = self.config.optimize_for_platform(
            audio_signal=audio_data["signal"][:22050],  # Plus court pour TikTok
            sample_rate=audio_data["sample_rate"],
            platform="tiktok",
            content_type="short_video"
        )
        
        assert tiktok_optimization["success"] is True
        assert "mobile_optimization" in tiktok_optimization
        assert "loudness_maximized" in tiktok_optimization
        
        # Optimisation pour podcast
        podcast_optimization = self.config.optimize_for_platform(
            audio_signal=audio_data["signal"],
            sample_rate=audio_data["sample_rate"],
            platform="podcast",
            content_type="speech"
        )
        
        assert podcast_optimization["success"] is True
        assert "speech_enhancement" in podcast_optimization
        assert "noise_reduction_applied" in podcast_optimization
        
        logger.info("Platform specific optimization test passed")

class TestAudioProcessor:
    """Tests spécifiques pour le processeur audio."""    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuration avant chaque test."""        self.audio_processor = AudioProcessor()
    
    @pytest_marks["unit"]
    def test_audio_effects_chain(self):
        """Test la chaîne d'effets audio."""        test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Test EQ paramétrique
        eq_result = self.audio_processor.apply_parametric_eq(
            audio_signal=test_signal,
            sample_rate=44100,
            eq_bands=[
                {"frequency": 440, "gain": 6, "q": 2.0, "type": "bell"}
            ]
        )
        
        assert eq_result["success"] is True
        assert "processed_signal" in eq_result
        assert not np.array_equal(eq_result["processed_signal"], test_signal)
        
        # Test compresseur dynamique
        compressor_result = self.audio_processor.apply_dynamic_compressor(
            audio_signal=test_signal,
            sample_rate=44100,
            threshold=-12,
            ratio=4.0,
            attack_ms=5,
            release_ms=50
        )
        
        assert compressor_result["success"] is True
        assert "gain_reduction_applied" in compressor_result

class TestQualityAnalyzer:
    """Tests spécifiques pour l'analyseur de qualité."""    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuration avant chaque test."""        self.quality_analyzer = QualityAnalyzer()
    
    @pytest_marks["unit"]
    def test_quality_scoring_algorithm(self):
        """Test l'algorithme de scoring de qualité."""        # Signal de haute qualité
        high_quality_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        quality_score = self.quality_analyzer.calculate_quality_score(
            audio_signal=high_quality_signal,
            sample_rate=44100,
            reference_quality="studio"
        )
        
        assert 7 <= quality_score <= 10  # Haute qualité attendue
        
        # Signal dégradé
        degraded_signal = high_quality_signal + np.random.random(len(high_quality_signal)) * 0.1
        
        degraded_score = self.quality_analyzer.calculate_quality_score(
            audio_signal=degraded_signal,
            sample_rate=44100,
            reference_quality="studio"
        )
        
        assert degraded_score < quality_score  # Score plus bas pour signal dégradé

class TestAudioPerformance:
    """Tests de performance pour les fonctionnalités audio."""    
    @pytest_marks["performance"]
    @pytest.mark.slow
    def test_large_file_processing(self):
        """Test de traitement de gros fichiers audio."""        config = AudioConfig()
        
        # Simuler un fichier audio de 5 minutes en stéréo
        duration = 300  # 5 minutes
        sample_rate = 44100
        large_audio = np.random.random((int(duration * sample_rate), 2)) * 0.1
        
        start_time = time.time()
        
        processing_result = config.process_large_audio_file(
            audio_signal=large_audio,
            sample_rate=sample_rate,
            processing_chain=[
                {"type": "normalize"},
                {"type": "eq", "preset": "mastering"},
                {"type": "compressor", "ratio": 2.5},
                {"type": "limiter"}
            ],
            chunk_size=44100  # 1 seconde par chunk
        )
        
        processing_time = time.time() - start_time
        
        assert processing_result["success"] is True
        assert processing_time < 60  # Moins d'1 minute pour 5 minutes d'audio
        
        logger.info(f"Large file processing: 5min audio processed in {processing_time}s")

# Configuration pytest pour les tests audio
def pytest_configure(config):
    """Configuration pytest pour les tests audio."""    config.addinivalue_line(
        "markers", "audio_quality: Audio quality analysis tests"
    )
    config.addinivalue_line(
        "markers", "audio_processing: Audio processing pipeline tests"
    )
    config.addinivalue_line(
        "markers", "mastering: Audio mastering tests"
    )
    config.addinivalue_line(
        "markers", "format_conversion: Audio format conversion tests"
    )
    config.addinivalue_line(
        "markers", "realtime: Real-time audio processing tests"
    )

if __name__ == "__main__":
    # Exécution directe pour tests de développement
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
