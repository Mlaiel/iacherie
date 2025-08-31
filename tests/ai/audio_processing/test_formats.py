# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""🧪 Audio Formats Tests - Industrial-Grade Format Conversion Testing

Comprehensive testing for audio format conversion and optimization including:
- FormatConverter validation
- QualityOptimizer testing
- Multi-format conversion accuracy
- Quality preservation validation
- Performance benchmarking
- FFmpeg integration testing

Created by Expert Team: Audio Developer + Backend Senior + DevOps Engineer
© 2025 Fahed Mlaiel. All rights reserved.
"""import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the audio processing module
try:
    from ai.audio_processing.formats import (
        FormatConverter, QualityOptimizer, AudioFormat, 
        QualityLevel, ConversionSettings, ConversionResult
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.formats import (
        FormatConverter, QualityOptimizer, AudioFormat, 
        QualityLevel, ConversionSettings, ConversionResult
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestFormatConverter:
    """    Industrial-grade testing for FormatConverter class
    
    Test Coverage:
    - Multi-format conversion validation
    - Quality level preservation
    - FFmpeg integration testing
    - Conversion settings validation
    - Error handling
    - Performance optimization
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""        setup_test_environment()
        self.converter = FormatConverter()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.temp_output_dir = TEST_CONFIG["temp_output_dir"]
    
    def test_initialization(self):
        """Test FormatConverter initialization"""        converter = FormatConverter()
        assert converter is not None
        assert hasattr(converter, 'ffmpeg_path')
        assert hasattr(converter, 'temp_dir')
        assert hasattr(converter, 'supported_formats')
    
    def test_supported_formats(self):
        """Test supported format enumeration"""        # Check AudioFormat enum
        assert hasattr(AudioFormat, 'WAV')
        assert hasattr(AudioFormat, 'MP3')
        assert hasattr(AudioFormat, 'FLAC')
        assert hasattr(AudioFormat, 'OGG')
        assert hasattr(AudioFormat, 'AAC')
        assert hasattr(AudioFormat, 'M4A')
        
        # Check QualityLevel enum
        assert hasattr(QualityLevel, 'LOW')
        assert hasattr(QualityLevel, 'MEDIUM')
        assert hasattr(QualityLevel, 'HIGH')
        assert hasattr(QualityLevel, 'LOSSLESS')
    
    def test_convert_wav_to_mp3(self):
        """Test WAV to MP3 conversion"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        output_file = self.temp_output_dir / "test_output.mp3"
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.HIGH
        )
        
        assert result is not None
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.output_path == str(output_file)
        assert result.output_format == AudioFormat.MP3
        assert result.file_size > 0
        assert result.conversion_time > 0
        assert output_file.exists()
        
        # Verify converted file can be loaded
        converted_audio, sample_rate = self.processor.load_audio(str(output_file))
        assert converted_audio is not None
        assert len(converted_audio) > 0
    
    def test_convert_wav_to_flac(self):
        """Test WAV to FLAC conversion (lossless)"""        input_file = self.test_data_dir / "chirp_sweep.wav"
        output_file = self.temp_output_dir / "test_output.flac"
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.FLAC,
            quality=QualityLevel.LOSSLESS
        )
        
        assert result.success is True
        assert result.output_format == AudioFormat.FLAC
        assert output_file.exists()
        
        # FLAC should preserve quality better than MP3
        original_audio, _ = self.processor.load_audio(str(input_file))
        converted_audio, _ = self.processor.load_audio(str(output_file))
        
        # Length should be preserved
        assert abs(len(converted_audio) - len(original_audio)) < 1000  # Small tolerance
    
    def test_convert_with_custom_settings(self):
        """Test conversion with custom settings"""        input_file = self.test_data_dir / "white_noise.wav"
        output_file = self.temp_output_dir / "test_custom.mp3"
        
        settings = ConversionSettings(
            bitrate=192,  # kbps
            sample_rate=44100,
            channels=2,
            quality_factor=0.8,
            enable_vbr=True
        )
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            settings=settings
        )
        
        assert result.success is True
        assert result.settings.bitrate == 192
        assert result.settings.sample_rate == 44100
        assert output_file.exists()
    
    def test_convert_different_quality_levels(self):
        """Test conversion with different quality levels"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        
        quality_levels = [QualityLevel.LOW, QualityLevel.MEDIUM, QualityLevel.HIGH]
        results = {}
        
        for quality in quality_levels:
            output_file = self.temp_output_dir / f"test_{quality.value}.mp3"
            
            result = self.converter.convert_audio(
                input_path=str(input_file),
                output_path=str(output_file),
                output_format=AudioFormat.MP3,
                quality=quality
            )
            
            assert result.success is True
            results[quality] = result
        
        # Higher quality should generally result in larger files
        assert results[QualityLevel.HIGH].file_size >= results[QualityLevel.MEDIUM].file_size
        assert results[QualityLevel.MEDIUM].file_size >= results[QualityLevel.LOW].file_size
    
    def test_convert_ogg_format(self):
        """Test OGG Vorbis conversion"""        input_file = self.test_data_dir / "white_noise.wav"
        output_file = self.temp_output_dir / "test_output.ogg"
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.OGG,
            quality=QualityLevel.HIGH
        )
        
        assert result.success is True
        assert result.output_format == AudioFormat.OGG
        assert output_file.exists()
        
        # Verify OGG file can be loaded
        converted_audio, sample_rate = self.processor.load_audio(str(output_file))
        assert converted_audio is not None
    
    def test_convert_aac_format(self):
        """Test AAC conversion"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        output_file = self.temp_output_dir / "test_output.aac"
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.AAC,
            quality=QualityLevel.HIGH
        )
        
        assert result.success is True
        assert result.output_format == AudioFormat.AAC
        assert output_file.exists()
    
    def test_convert_nonexistent_file(self):
        """Test error handling for non-existent input file"""        output_file = self.temp_output_dir / "test_output.mp3"
        
        result = self.converter.convert_audio(
            input_path="nonexistent_file.wav",
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.HIGH
        )
        
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower() or "no such file" in result.error_message.lower()
    
    def test_convert_invalid_output_format(self):
        """Test error handling for invalid output format"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        output_file = self.temp_output_dir / "test_output.xyz"  # Invalid extension
        
        with pytest.raises((ValueError, TypeError)):
            self.converter.convert_audio(
                input_path=str(input_file),
                output_path=str(output_file),
                output_format="INVALID_FORMAT",  # Invalid format
                quality=QualityLevel.HIGH
            )
    
    def test_batch_conversion(self):
        """Test batch file conversion"""        input_files = [
            self.test_data_dir / "pure_tone_440hz.wav",
            self.test_data_dir / "white_noise.wav",
            self.test_data_dir / "chirp_sweep.wav"
        ]
        
        output_dir = self.temp_output_dir / "batch_output"
        output_dir.mkdir(exist_ok=True)
        
        results = self.converter.convert_batch(
            input_paths=[str(f) for f in input_files],
            output_dir=str(output_dir),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.MEDIUM
        )
        
        assert results is not None
        assert len(results) == len(input_files)
        
        # All conversions should succeed
        for result in results:
            assert result.success is True
            assert Path(result.output_path).exists()
    
    def test_format_detection(self):
        """Test automatic format detection"""        test_files = {
            "pure_tone_440hz.wav": AudioFormat.WAV
        }
        
        for filename, expected_format in test_files.items():
            file_path = self.test_data_dir / filename
            detected_format = self.converter.detect_format(str(file_path))
            assert detected_format == expected_format
    
    def test_conversion_metadata_preservation(self):
        """Test metadata preservation during conversion"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        output_file = self.temp_output_dir / "test_metadata.mp3"
        
        # Add metadata to conversion
        metadata = {
            "title": "Test Audio",
            "artist": "Test Artist",
            "album": "Test Album",
            "year": "2025"
        }
        
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.HIGH,
            metadata=metadata
        )
        
        assert result.success is True
        assert result.metadata is not None
        for key, value in metadata.items():
            assert result.metadata.get(key) == value
    
    def test_performance_benchmarking(self):
        """Test conversion performance"""        input_file = self.test_data_dir / "chirp_sweep.wav"
        output_file = self.temp_output_dir / "test_performance.mp3"
        
        start_time = time.time()
        result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.MEDIUM
        )
        end_time = time.time()
        
        conversion_time = (end_time - start_time) * 1000  # ms
        
        assert result.success is True
        assert conversion_time < TEST_CONFIG["performance_threshold_ms"] * 10  # Allow 10x for format conversion
        assert result.conversion_time > 0


class TestQualityOptimizer:
    """    Industrial-grade testing for QualityOptimizer class
    
    Test Coverage:
    - Quality assessment algorithms
    - Optimization recommendation engine
    - Format-specific optimizations
    - Quality metric validation
    - Perceptual quality testing
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""        setup_test_environment()
        self.optimizer = QualityOptimizer()
        self.processor = AudioProcessor()
        self.converter = FormatConverter()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.temp_output_dir = TEST_CONFIG["temp_output_dir"]
    
    def test_initialization(self):
        """Test QualityOptimizer initialization"""        optimizer = QualityOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'quality_metrics')
        assert hasattr(optimizer, 'optimization_rules')
    
    def test_analyze_audio_quality(self):
        """Test audio quality analysis"""        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        quality_analysis = self.optimizer.analyze_quality(audio_data, sample_rate)
        
        assert quality_analysis is not None
        assert isinstance(quality_analysis, dict)
        
        # Check required quality metrics
        required_metrics = [
            'snr', 'thd', 'dynamic_range', 'frequency_response',
            'peak_level', 'rms_level', 'quality_score'
        ]
        
        for metric in required_metrics:
            assert metric in quality_analysis
            assert isinstance(quality_analysis[metric], (int, float))
            assert not np.isnan(quality_analysis[metric])
    
    def test_recommend_conversion_settings(self):
        """Test conversion settings recommendation"""        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        recommendations = self.optimizer.recommend_settings(
            audio_data, 
            sample_rate,
            target_format=AudioFormat.MP3,
            target_quality=QualityLevel.HIGH
        )
        
        assert recommendations is not None
        assert isinstance(recommendations, ConversionSettings)
        assert recommendations.bitrate > 0
        assert recommendations.sample_rate > 0
        assert recommendations.channels > 0
        assert 0.0 <= recommendations.quality_factor <= 1.0
    
    def test_optimize_for_streaming(self):
        """Test optimization for streaming scenarios"""        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        streaming_settings = self.optimizer.optimize_for_streaming(
            audio_data, 
            sample_rate,
            target_bitrate=128  # kbps
        )
        
        assert streaming_settings is not None
        assert streaming_settings.bitrate <= 128
        assert streaming_settings.enable_vbr is True  # Better for streaming
        assert streaming_settings.quality_factor >= 0.6  # Reasonable quality
    
    def test_optimize_for_archival(self):
        """Test optimization for archival/preservation"""        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        archival_settings = self.optimizer.optimize_for_archival(
            audio_data, 
            sample_rate
        )
        
        assert archival_settings is not None
        assert archival_settings.quality_factor >= 0.9  # High quality for archival
        # Should prefer lossless or high-quality lossy
        assert archival_settings.bitrate >= 256 or archival_settings.lossless is True
    
    def test_optimize_for_mobile(self):
        """Test optimization for mobile devices"""        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        mobile_settings = self.optimizer.optimize_for_mobile(
            audio_data, 
            sample_rate
        )
        
        assert mobile_settings is not None
        assert mobile_settings.bitrate <= 192  # Conservative for mobile
        assert mobile_settings.sample_rate <= 44100  # Standard rate
        assert mobile_settings.channels <= 2  # Stereo or mono
    
    def test_quality_comparison(self):
        """Test quality comparison between formats"""        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        
        # Convert to different formats
        mp3_file = self.temp_output_dir / "comparison_test.mp3"
        flac_file = self.temp_output_dir / "comparison_test.flac"
        
        # Convert to MP3
        mp3_result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(mp3_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.HIGH
        )
        
        # Convert to FLAC
        flac_result = self.converter.convert_audio(
            input_path=str(input_file),
            output_path=str(flac_file),
            output_format=AudioFormat.FLAC,
            quality=QualityLevel.LOSSLESS
        )
        
        assert mp3_result.success and flac_result.success
        
        # Analyze quality of converted files
        mp3_audio, _ = self.processor.load_audio(str(mp3_file))
        flac_audio, _ = self.processor.load_audio(str(flac_file))
        
        mp3_quality = self.optimizer.analyze_quality(mp3_audio, 44100)
        flac_quality = self.optimizer.analyze_quality(flac_audio, 44100)
        
        # FLAC should have better quality metrics
        assert flac_quality['quality_score'] >= mp3_quality['quality_score']
        assert flac_quality['dynamic_range'] >= mp3_quality['dynamic_range']
    
    def test_perceptual_quality_assessment(self):
        """Test perceptual quality assessment"""        # Load reference audio
        reference_file = self.test_data_dir / "pure_tone_440hz.wav"
        reference_audio, sample_rate = self.processor.load_audio(str(reference_file))
        
        # Create degraded version (lower quality)
        degraded_file = self.temp_output_dir / "degraded.mp3"
        self.converter.convert_audio(
            input_path=str(reference_file),
            output_path=str(degraded_file),
            output_format=AudioFormat.MP3,
            quality=QualityLevel.LOW
        )
        degraded_audio, _ = self.processor.load_audio(str(degraded_file))
        
        # Compare perceptual quality
        perceptual_score = self.optimizer.compute_perceptual_quality(
            reference_audio, 
            degraded_audio, 
            sample_rate
        )
        
        assert perceptual_score is not None
        assert 0.0 <= perceptual_score <= 1.0
        assert perceptual_score < 0.9  # Should detect degradation
    
    def test_dynamic_range_optimization(self):
        """Test dynamic range optimization"""        # Create audio with poor dynamic range
        compressed_audio = np.tanh(np.random.randn(44100) * 5) * 0.3
        
        optimized_settings = self.optimizer.optimize_dynamic_range(
            compressed_audio, 
            44100,
            target_dynamic_range=0.8
        )
        
        assert optimized_settings is not None
        assert isinstance(optimized_settings, dict)
        assert 'expansion_ratio' in optimized_settings
        assert 'gain_adjustment' in optimized_settings
    
    def test_frequency_response_optimization(self):
        """Test frequency response optimization"""        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        fr_optimization = self.optimizer.optimize_frequency_response(
            audio_data, 
            sample_rate,
            target_response='flat'
        )
        
        assert fr_optimization is not None
        assert isinstance(fr_optimization, dict)
        assert 'eq_settings' in fr_optimization
        assert 'filter_settings' in fr_optimization
    
    def test_bitrate_optimization(self):
        """Test optimal bitrate calculation"""        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        optimal_bitrate = self.optimizer.calculate_optimal_bitrate(
            audio_data, 
            sample_rate,
            target_format=AudioFormat.MP3,
            quality_threshold=0.85
        )
        
        assert optimal_bitrate is not None
        assert isinstance(optimal_bitrate, int)
        assert 64 <= optimal_bitrate <= 320  # Reasonable range for MP3
    
    def test_format_recommendation(self):
        """Test format recommendation based on content"""        # Test different audio types
        test_cases = [
            ("pure_tone_440hz.wav", "music"),
            ("white_noise.wav", "noise"),
            ("silence.wav", "silence")
        ]
        
        for filename, content_type in test_cases:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            
            recommendation = self.optimizer.recommend_format(
                audio_data, 
                sample_rate,
                content_type=content_type,
                use_case="streaming"
            )
            
            assert recommendation is not None
            assert hasattr(AudioFormat, recommendation.format.name)
            assert isinstance(recommendation.quality, QualityLevel)
            assert recommendation.estimated_size > 0


class TestConversionSettings:
    """Test ConversionSettings data structure"""    
    def test_settings_creation(self):
        """Test ConversionSettings creation"""        settings = ConversionSettings(
            bitrate=192,
            sample_rate=44100,
            channels=2,
            quality_factor=0.8,
            enable_vbr=True
        )
        
        assert settings.bitrate == 192
        assert settings.sample_rate == 44100
        assert settings.channels == 2
        assert settings.quality_factor == 0.8
        assert settings.enable_vbr is True
    
    def test_settings_validation(self):
        """Test settings validation"""        # Valid settings
        valid_settings = ConversionSettings(
            bitrate=128,
            sample_rate=44100,
            channels=2,
            quality_factor=0.7
        )
        assert valid_settings.is_valid()
        
        # Invalid settings
        with pytest.raises(ValueError):
            ConversionSettings(
                bitrate=-1,  # Invalid bitrate
                sample_rate=44100,
                channels=2,
                quality_factor=0.7
            )


class TestConversionResult:
    """Test ConversionResult data structure"""    
    def test_result_creation(self):
        """Test ConversionResult creation"""        result = ConversionResult(
            success=True,
            output_path="/path/to/output.mp3",
            output_format=AudioFormat.MP3,
            file_size=1024000,
            conversion_time=2.5,
            error_message=None
        )
        
        assert result.success is True
        assert result.output_path == "/path/to/output.mp3"
        assert result.output_format == AudioFormat.MP3
        assert result.file_size == 1024000
        assert result.conversion_time == 2.5
        assert result.error_message is None


class TestFormatsIntegration:
    """    Integration tests for format conversion workflow
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.temp_output_dir = TEST_CONFIG["temp_output_dir"]
    
    def test_complete_conversion_workflow(self):
        """Test complete conversion workflow with optimization"""        processor = AudioProcessor()
        optimizer = QualityOptimizer()
        converter = FormatConverter()
        
        # 1. Load audio
        input_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = processor.load_audio(str(input_file))
        
        # 2. Analyze quality and get recommendations
        quality_analysis = optimizer.analyze_quality(audio_data, sample_rate)
        recommended_settings = optimizer.recommend_settings(
            audio_data, sample_rate, 
            target_format=AudioFormat.MP3,
            target_quality=QualityLevel.HIGH
        )
        
        # 3. Convert with optimized settings
        output_file = self.temp_output_dir / "workflow_test.mp3"
        result = converter.convert_audio(
            input_path=str(input_file),
            output_path=str(output_file),
            output_format=AudioFormat.MP3,
            settings=recommended_settings
        )
        
        # 4. Verify workflow
        assert quality_analysis is not None
        assert recommended_settings is not None
        assert result.success is True
        assert output_file.exists()
        
        # Verify converted file quality
        converted_audio, _ = processor.load_audio(str(output_file))
        converted_quality = optimizer.analyze_quality(converted_audio, sample_rate)
        assert converted_quality['quality_score'] >= TEST_CONFIG["quality_threshold"]
    
    def test_cross_format_compatibility(self):
        """Test conversion between multiple formats"""        converter = FormatConverter()
        
        input_file = self.test_data_dir / "pure_tone_440hz.wav"
        
        # Test conversion chain: WAV -> MP3 -> FLAC -> OGG
        formats = [AudioFormat.MP3, AudioFormat.FLAC, AudioFormat.OGG]
        
        current_input = str(input_file)
        for i, target_format in enumerate(formats):
            output_file = self.temp_output_dir / f"chain_{i}.{target_format.value.lower()}"
            
            result = converter.convert_audio(
                input_path=current_input,
                output_path=str(output_file),
                output_format=target_format,
                quality=QualityLevel.HIGH
            )
            
            assert result.success is True
            assert output_file.exists()
            
            current_input = str(output_file)  # Use as input for next conversion


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
