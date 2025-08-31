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

"""Image Quality Analysis Tests

Comprehensive test suite for professional image quality assessment with advanced image analysis,
composition evaluation, color accuracy assessment, and platform-specific image standards validation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Project Team Specialties:
✅ Lead Dev + AI Developer Architect - Fahed Mlaiel
✅ Senior Backend Developer (Python/FastAPI/Django) - Fahed Mlaiel  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face) - Fahed Mlaiel
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB) - Fahed Mlaiel
✅ Backend Security Specialist - Fahed Mlaiel
✅ Microservices Architect - Fahed Mlaiel
✅ Audio Developer - Fahed Mlaiel
✅ DevOps Engineer - Fahed Mlaiel
✅ AI Prompt Engineer - Fahed Mlaiel

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

ANYONE WHO THINKS OF STEALING THE IDEA, CONCEPT, OR CODE WITHOUT MY PERSONAL, CLEAR, 
AND WRITTEN AUTHORIZATION WILL FACE SEVERE LEGAL CONSEQUENCES.

Contact: Fahed Mlaiel - mlaiel@live.de
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
import tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from unittest import TestCase
from pathlib import Path
from typing import Dict, List, Any, Optional
import cv2

from ai.quality_assessment.image_quality import (
    ImageQualityAnalyzer,
    ImageQualityMetrics,
    ImageQualityProfile,
    ImageSharpness,
    ColorAccuracy,
    CompositionAnalysis
)


class TestImageQualityAnalyzer(TestCase):
    """Comprehensive test suite for ImageQualityAnalyzer with professional image standards."""    
    def setUp(self):
        """Set up test environment with various image samples and configurations."""        self.analyzer = ImageQualityAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        
        # Image generation parameters
        self.width = 1920
        self.height = 1080
        self.high_res_width = 3840
        self.high_res_height = 2160
        
        # Generate test images with different characteristics
        self.high_quality_image_path = Path(self.temp_dir) / "high_quality.jpg"
        self._generate_high_quality_image(self.high_quality_image_path)
        
        self.low_quality_image_path = Path(self.temp_dir) / "low_quality.jpg"
        self._generate_low_quality_image(self.low_quality_image_path)
        
        self.portrait_image_path = Path(self.temp_dir) / "portrait.jpg"
        self._generate_portrait_image(self.portrait_image_path)
        
        self.landscape_image_path = Path(self.temp_dir) / "landscape.jpg"
        self._generate_landscape_image(self.landscape_image_path)
        
        self.composition_image_path = Path(self.temp_dir) / "composition.jpg"
        self._generate_composition_test_image(self.composition_image_path)
        
        self.color_test_image_path = Path(self.temp_dir) / "color_test.jpg"
        self._generate_color_test_image(self.color_test_image_path)
        
        # Platform-specific test configurations
        self.platform_configs = {
            'instagram': {
                'preferred_ratios': [(1, 1), (4, 5), (16, 9)],
                'min_resolution': (1080, 1080),
                'max_file_size': 8 * 1024 * 1024,  # 8MB
                'supported_formats': ['jpeg', 'png']
            },
            'pinterest': {
                'preferred_ratios': [(2, 3), (1, 2.1), (9, 16)],
                'min_resolution': (600, 900),
                'max_file_size': 20 * 1024 * 1024,  # 20MB
                'supported_formats': ['jpeg', 'png']
            },
            'facebook': {
                'preferred_ratios': [(16, 9), (1, 1), (4, 5)],
                'min_resolution': (1200, 630),
                'max_file_size': 4 * 1024 * 1024,  # 4MB
                'supported_formats': ['jpeg', 'png']
            }
        }
    
    def _generate_high_quality_image(self, file_path: Path):
        """Generate a high-quality test image with rich details and good composition."""        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Create a gradient background
        for y in range(self.height):
            for x in range(self.width):
                r = int(100 + (x / self.width) * 155)
                g = int(150 + (y / self.height) * 105)
                b = int(200 - (x + y) / (self.width + self.height) * 100)
                image.putpixel((x, y), (r, g, b))
        
        # Add geometric shapes with good composition
        # Golden ratio positioning
        golden_x = int(self.width * 0.618)
        golden_y = int(self.height * 0.618)
        
        # Main subject (circle)
        draw.ellipse([golden_x - 150, golden_y - 150, golden_x + 150, golden_y + 150], 
                    fill=(255, 200, 100), outline=(200, 150, 50), width=5)
        
        # Secondary elements
        draw.rectangle([50, 50, 200, 200], fill=(100, 150, 255), outline=(50, 100, 200), width=3)
        draw.polygon([(self.width - 200, 100), (self.width - 100, 100), (self.width - 150, 200)], 
                    fill=(255, 100, 150), outline=(200, 50, 100), width=3)
        
        # Add fine details and textures
        for i in range(100):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            size = np.random.randint(2, 8)
            color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
            draw.ellipse([x, y, x + size, y + size], fill=color)
        
        # Apply subtle sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # Save with high quality
        image.save(file_path, quality=95, optimize=True)
    
    def _generate_low_quality_image(self, file_path: Path):
        """Generate a low-quality test image with noise, blur, and compression artifacts."""        # Start with smaller resolution
        small_width, small_height = 640, 480
        image = Image.new('RGB', (small_width, small_height), color=(128, 128, 128))
        draw = ImageDraw.Draw(image)
        
        # Add noise
        pixels = image.load()
        for y in range(small_height):
            for x in range(small_width):
                noise_r = int(np.random.normal(0, 30))
                noise_g = int(np.random.normal(0, 30))
                noise_b = int(np.random.normal(0, 30))
                
                r = np.clip(128 + noise_r, 0, 255)
                g = np.clip(128 + noise_g, 0, 255)
                b = np.clip(128 + noise_b, 0, 255)
                pixels[x, y] = (r, g, b)
        
        # Add some simple shapes with poor composition
        draw.rectangle([100, 100, 300, 200], fill=(255, 0, 0))
        draw.ellipse([200, 150, 400, 350], fill=(0, 255, 0))
        
        # Apply blur to simulate poor focus
        image = image.filter(ImageFilter.GaussianBlur(radius=2))
        
        # Resize back to target resolution (will introduce interpolation artifacts)
        image = image.resize((self.width, self.height), Image.NEAREST)
        
        # Save with low quality
        image.save(file_path, quality=30, optimize=False)
    
    def _generate_portrait_image(self, file_path: Path):
        """Generate a portrait-oriented test image."""        # Portrait orientation (taller than wide)
        portrait_width = 1080
        portrait_height = 1350
        
        image = Image.new('RGB', (portrait_width, portrait_height), color=(245, 240, 235))
        draw = ImageDraw.Draw(image)
        
        # Simulate a portrait composition
        # Face area (oval)
        face_center_x = portrait_width // 2
        face_center_y = portrait_height // 3
        face_width = 200
        face_height = 250
        
        draw.ellipse([
            face_center_x - face_width//2, face_center_y - face_height//2,
            face_center_x + face_width//2, face_center_y + face_height//2
        ], fill=(255, 220, 177), outline=(200, 180, 140), width=2)
        
        # Eyes
        eye_y = face_center_y - 30
        left_eye_x = face_center_x - 40
        right_eye_x = face_center_x + 40
        
        for eye_x in [left_eye_x, right_eye_x]:
            draw.ellipse([eye_x - 15, eye_y - 10, eye_x + 15, eye_y + 10], 
                        fill=(100, 150, 200), outline=(50, 100, 150), width=2)
        
        # Mouth
        mouth_y = face_center_y + 40
        draw.arc([face_center_x - 30, mouth_y - 15, face_center_x + 30, mouth_y + 15], 
                start=0, end=180, fill=(200, 100, 100), width=3)
        
        # Background elements
        draw.rectangle([0, portrait_height//2, portrait_width, portrait_height], 
                      fill=(100, 120, 140))
        
        image.save(file_path, quality=85)
    
    def _generate_landscape_image(self, file_path: Path):
        """Generate a landscape-oriented test image."""        # Landscape orientation (wider than tall)
        landscape_width = 1920
        landscape_height = 1080
        
        image = Image.new('RGB', (landscape_width, landscape_height), color=(135, 206, 235))
        draw = ImageDraw.Draw(image)
        
        # Sky gradient
        for y in range(landscape_height // 2):
            intensity = int(135 + (y / (landscape_height // 2)) * 120)
            color = (intensity, intensity + 50, 235)
            draw.line([(0, y), (landscape_width, y)], fill=color)
        
        # Ground
        draw.rectangle([0, landscape_height // 2, landscape_width, landscape_height], 
                      fill=(34, 139, 34))
        
        # Mountains
        mountain_points = [
            (0, landscape_height // 2),
            (200, landscape_height // 4),
            (400, landscape_height // 3),
            (600, landscape_height // 5),
            (800, landscape_height // 3),
            (1000, landscape_height // 4),
            (1200, landscape_height // 6),
            (landscape_width, landscape_height // 2)
        ]
        draw.polygon(mountain_points, fill=(105, 105, 105))
        
        # Sun
        sun_x = landscape_width - 200
        sun_y = 150
        draw.ellipse([sun_x - 50, sun_y - 50, sun_x + 50, sun_y + 50], 
                    fill=(255, 255, 0), outline=(255, 215, 0), width=3)
        
        # Trees
        for i in range(5):
            tree_x = 100 + i * 300
            tree_y = landscape_height // 2
            # Trunk
            draw.rectangle([tree_x - 10, tree_y, tree_x + 10, tree_y + 100], fill=(139, 69, 19))
            # Leaves
            draw.ellipse([tree_x - 40, tree_y - 60, tree_x + 40, tree_y + 20], fill=(0, 128, 0))
        
        image.save(file_path, quality=90)
    
    def _generate_composition_test_image(self, file_path: Path):
        """Generate an image specifically for composition analysis testing."""        image = Image.new('RGB', (self.width, self.height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Rule of thirds grid demonstration
        third_x1 = self.width // 3
        third_x2 = 2 * self.width // 3
        third_y1 = self.height // 3
        third_y2 = 2 * self.height // 3
        
        # Place interesting elements at intersection points
        # Top-left intersection
        draw.ellipse([third_x1 - 50, third_y1 - 50, third_x1 + 50, third_y1 + 50], 
                    fill=(255, 0, 0), outline=(200, 0, 0), width=3)
        
        # Bottom-right intersection
        draw.rectangle([third_x2 - 60, third_y2 - 40, third_x2 + 60, third_y2 + 40], 
                      fill=(0, 255, 0), outline=(0, 200, 0), width=3)
        
        # Leading lines
        draw.line([(0, 0), (self.width, self.height)], fill=(0, 0, 255), width=5)
        draw.line([(0, self.height//4), (self.width, self.height//2)], fill=(255, 165, 0), width=3)
        
        # Symmetry elements
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Symmetric shapes
        for offset in [-200, 200]:
            draw.polygon([
                (center_x + offset, center_y - 100),
                (center_x + offset - 50, center_y + 100),
                (center_x + offset + 50, center_y + 100)
            ], fill=(128, 0, 128), outline=(100, 0, 100), width=2)
        
        # Depth indicators (perspective)
        for i in range(5):
            size = 100 - i * 15
            y_pos = center_y + i * 50
            draw.ellipse([center_x - size//2, y_pos - size//2, 
                         center_x + size//2, y_pos + size//2], 
                        fill=(255, 255 - i * 40, 0), outline=(200, 200 - i * 30, 0), width=2)
        
        image.save(file_path, quality=95)
    
    def _generate_color_test_image(self, file_path: Path):
        """Generate an image specifically for color analysis testing."""        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Color bands for analysis
        band_width = self.width // 8
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),    # Blue
            (128, 0, 128),  # Purple
            (255, 192, 203) # Pink
        ]
        
        for i, color in enumerate(colors):
            x_start = i * band_width
            x_end = (i + 1) * band_width
            draw.rectangle([x_start, 0, x_end, self.height // 3], fill=color)
        
        # Saturation gradient
        for x in range(self.width):
            saturation = x / self.width
            for y in range(self.height // 3, 2 * self.height // 3):
                # Create a saturation gradient from gray to red
                red = int(128 + saturation * 127)
                green = int(128 * (1 - saturation))
                blue = int(128 * (1 - saturation))
                image.putpixel((x, y), (red, green, blue))
        
        # Brightness gradient
        for x in range(self.width):
            for y in range(2 * self.height // 3, self.height):
                brightness = x / self.width
                value = int(brightness * 255)
                image.putpixel((x, y), (value, value, value))
        
        # Color harmony test areas
        # Complementary colors
        draw.ellipse([100, self.height // 2, 300, self.height // 2 + 200], 
                    fill=(255, 0, 0))  # Red
        draw.ellipse([350, self.height // 2, 550, self.height // 2 + 200], 
                    fill=(0, 255, 0))  # Green (complementary)
        
        # Analogous colors
        draw.ellipse([self.width - 400, 100, self.width - 200, 300], 
                    fill=(255, 0, 0))    # Red
        draw.ellipse([self.width - 350, 150, self.width - 150, 350], 
                    fill=(255, 165, 0))  # Orange (analogous)
        
        image.save(file_path, quality=95)
    
    @pytest.mark.asyncio
    async def test_comprehensive_image_analysis(self):
        """Test comprehensive image quality analysis with all metrics."""        analysis_result = await self.analyzer.analyze_image_quality(
            str(self.high_quality_image_path),
            platform='instagram',
            content_type='photography'
        )
        
        # Validate result structure
        self.assertIsInstance(analysis_result, dict)
        self.assertIn('overall_score', analysis_result)
        self.assertIn('technical_quality', analysis_result)
        self.assertIn('aesthetic_quality', analysis_result)
        self.assertIn('composition_analysis', analysis_result)
        self.assertIn('color_analysis', analysis_result)
        self.assertIn('platform_compliance', analysis_result)
        self.assertIn('recommendations', analysis_result)
        
        # Validate score range
        self.assertGreaterEqual(analysis_result['overall_score'], 0.0)
        self.assertLessEqual(analysis_result['overall_score'], 100.0)
        
        # Validate technical quality metrics
        tech_quality = analysis_result['technical_quality']
        expected_tech_metrics = [
            'resolution', 'sharpness', 'noise_level', 'compression_quality',
            'color_depth', 'dynamic_range', 'file_size_efficiency'
        ]
        
        for metric in expected_tech_metrics:
            self.assertIn(metric, tech_quality)
            self.assertIsInstance(tech_quality[metric], (int, float, dict))
        
        # Validate aesthetic quality metrics
        aesthetic_quality = analysis_result['aesthetic_quality']
        expected_aesthetic_metrics = [
            'composition_score', 'color_harmony', 'visual_balance', 
            'contrast', 'lighting_quality', 'artistic_appeal'
        ]
        
        for metric in expected_aesthetic_metrics:
            self.assertIn(metric, aesthetic_quality)
            self.assertIsInstance(aesthetic_quality[metric], (int, float, dict))
    
    @pytest.mark.asyncio
    async def test_technical_quality_assessment(self):
        """Test technical image quality assessment."""        # Test high-quality image
        hq_result = await self.analyzer.assess_technical_quality(
            str(self.high_quality_image_path)
        )
        
        self.assertIsInstance(hq_result, TechnicalQuality)
        self.assertIsNotNone(hq_result.resolution_score)
        self.assertIsNotNone(hq_result.sharpness_score)
        self.assertIsNotNone(hq_result.noise_level)
        self.assertIsNotNone(hq_result.compression_artifacts)
        self.assertIsNotNone(hq_result.color_accuracy)
        
        # Test low-quality image
        lq_result = await self.analyzer.assess_technical_quality(
            str(self.low_quality_image_path)
        )
        
        # High-quality image should score better
        self.assertGreater(hq_result.resolution_score, lq_result.resolution_score)
        self.assertGreater(hq_result.sharpness_score, lq_result.sharpness_score)
        self.assertLess(hq_result.noise_level, lq_result.noise_level)
        self.assertLess(hq_result.compression_artifacts, lq_result.compression_artifacts)
        
        # Validate score ranges
        for result in [hq_result, lq_result]:
            self.assertGreaterEqual(result.resolution_score, 0.0)
            self.assertLessEqual(result.resolution_score, 100.0)
            self.assertGreaterEqual(result.sharpness_score, 0.0)
            self.assertLessEqual(result.sharpness_score, 100.0)
            self.assertGreaterEqual(result.noise_level, 0.0)
            self.assertLessEqual(result.noise_level, 100.0)
    
    @pytest.mark.asyncio
    async def test_composition_analysis(self):
        """Test image composition analysis with rule of thirds, balance, and leading lines."""        composition_result = await self.analyzer.analyze_composition(
            str(self.composition_test_image_path)
        )
        
        # Validate composition analysis structure
        self.assertIsInstance(composition_result, CompositionAnalysis)
        self.assertIsNotNone(composition_result.rule_of_thirds_score)
        self.assertIsNotNone(composition_result.balance_score)
        self.assertIsNotNone(composition_result.leading_lines)
        self.assertIsNotNone(composition_result.symmetry_score)
        self.assertIsNotNone(composition_result.depth_perception)
        
        # Validate score ranges
        self.assertGreaterEqual(composition_result.rule_of_thirds_score, 0.0)
        self.assertLessEqual(composition_result.rule_of_thirds_score, 100.0)
        
        self.assertGreaterEqual(composition_result.balance_score, 0.0)
        self.assertLessEqual(composition_result.balance_score, 100.0)
        
        self.assertGreaterEqual(composition_result.symmetry_score, 0.0)
        self.assertLessEqual(composition_result.symmetry_score, 100.0)
        
        # Validate leading lines detection
        self.assertIsInstance(composition_result.leading_lines, list)
        if len(composition_result.leading_lines) > 0:
            for line in composition_result.leading_lines:
                self.assertIn('strength', line)
                self.assertIn('direction', line)
                self.assertIn('start_point', line)
                self.assertIn('end_point', line)
        
        # Validate depth perception analysis
        depth = composition_result.depth_perception
        self.assertIn('layers_detected', depth)
        self.assertIn('perspective_strength', depth)
        self.assertIn('foreground_background_separation', depth)
    
    @pytest.mark.asyncio
    async def test_color_analysis_comprehensive(self):
        """Test comprehensive color analysis including harmony, temperature, and saturation."""        color_result = await self.analyzer.analyze_color_quality(
            str(self.color_test_image_path)
        )
        
        # Validate color analysis structure
        self.assertIsInstance(color_result, dict)
        self.assertIsNotNone(color_result.color_harmony_score)
        self.assertIsNotNone(color_result.color_temperature)
        self.assertIsNotNone(color_result.saturation_levels)
        self.assertIsNotNone(color_result.color_distribution)
        self.assertIsNotNone(color_result.white_balance)
        
        # Validate color harmony
        self.assertGreaterEqual(color_result.color_harmony_score, 0.0)
        self.assertLessEqual(color_result.color_harmony_score, 100.0)
        
        # Validate color temperature
        temp = color_result.color_temperature
        self.assertIn('kelvin', temp)
        self.assertIn('classification', temp)
        self.assertGreater(temp['kelvin'], 0)
        self.assertIn(temp['classification'], ['warm', 'neutral', 'cool'])
        
        # Validate saturation levels
        saturation = color_result.saturation_levels
        self.assertIn('average_saturation', saturation)
        self.assertIn('saturation_distribution', saturation)
        self.assertIn('oversaturation_areas', saturation)
        
        # Validate color distribution
        distribution = color_result.color_distribution
        self.assertIn('dominant_colors', distribution)
        self.assertIn('color_palette', distribution)
        self.assertIn('color_variance', distribution)
        
        # Validate dominant colors
        self.assertIsInstance(distribution['dominant_colors'], list)
        self.assertGreater(len(distribution['dominant_colors']), 0)
        
        for color in distribution['dominant_colors']:
            self.assertIn('rgb', color)
            self.assertIn('percentage', color)
            self.assertIn('hex', color)
    
    @pytest.mark.asyncio
    async def test_aesthetic_quality_evaluation(self):
        """Test aesthetic quality evaluation including visual appeal and artistic merit."""        # Test high-quality image
        aesthetic_result = await self.analyzer.evaluate_aesthetic_quality(
            str(self.high_quality_image_path)
        )
        
        # Validate aesthetic quality structure
        self.assertIsInstance(aesthetic_result, AestheticQuality)
        self.assertIsNotNone(aesthetic_result.visual_appeal_score)
        self.assertIsNotNone(aesthetic_result.artistic_merit)
        self.assertIsNotNone(aesthetic_result.emotional_impact)
        self.assertIsNotNone(aesthetic_result.creativity_score)
        self.assertIsNotNone(aesthetic_result.style_consistency)
        
        # Validate score ranges
        self.assertGreaterEqual(aesthetic_result.visual_appeal_score, 0.0)
        self.assertLessEqual(aesthetic_result.visual_appeal_score, 100.0)
        
        self.assertGreaterEqual(aesthetic_result.artistic_merit, 0.0)
        self.assertLessEqual(aesthetic_result.artistic_merit, 100.0)
        
        self.assertGreaterEqual(aesthetic_result.creativity_score, 0.0)
        self.assertLessEqual(aesthetic_result.creativity_score, 100.0)
        
        # Validate emotional impact analysis
        emotional = aesthetic_result.emotional_impact
        self.assertIn('mood_classification', emotional)
        self.assertIn('emotional_intensity', emotional)
        self.assertIn('viewer_engagement_prediction', emotional)
        
        # Validate style analysis
        style = aesthetic_result.style_consistency
        self.assertIn('style_classification', style)
        self.assertIn('consistency_score', style)
        self.assertIn('genre_alignment', style)
    
    @pytest.mark.asyncio
    async def test_platform_specific_compliance(self):
        """Test platform-specific image compliance validation."""        for platform, config in self.platform_configs.items():
            compliance_result = await self.analyzer.check_platform_compliance(
                str(self.high_quality_image_path),
                platform=platform
            )
            
            # Validate compliance structure
            self.assertIsInstance(compliance_result, dict)
            self.assertIn('compliant', compliance_result)
            self.assertIn('violations', compliance_result)
            self.assertIn('recommendations', compliance_result)
            self.assertIn('platform_standards', compliance_result)
            
            # Validate platform standards
            standards = compliance_result['platform_standards']
            self.assertIn('preferred_aspect_ratios', standards)
            self.assertIn('minimum_resolution', standards)
            self.assertIn('maximum_file_size', standards)
            self.assertIn('supported_formats', standards)
            
            # Platform-specific validations
            if platform == 'pinterest':
                # Pinterest prefers vertical images
                ratios = standards['preferred_aspect_ratios']
                vertical_ratios = [ratio for ratio in ratios if ratio[1] > ratio[0]]
                self.assertGreater(len(vertical_ratios), 0, "Pinterest should prefer vertical ratios")
            
            elif platform == 'instagram':
                # Instagram supports square and vertical formats
                ratios = standards['preferred_aspect_ratios']
                square_ratio = (1, 1) in ratios
                self.assertTrue(square_ratio, "Instagram should support square format")
    
    @pytest.mark.asyncio
    async def test_resolution_and_quality_analysis(self):
        """Test resolution analysis and image quality correlation."""        # Test different resolution scenarios
        test_images = [
            (self.high_quality_image_path, "high_quality"),
            (self.low_quality_image_path, "low_quality")
        ]
        
        results = {}
        for image_path, image_type in test_images:
            resolution_result = await self.analyzer.analyze_resolution(str(image_path))
            results[image_type] = resolution_result
            
            # Validate resolution analysis
            self.assertIn('width', resolution_result)
            self.assertIn('height', resolution_result)
            self.assertIn('pixel_density', resolution_result)
            self.assertIn('aspect_ratio', resolution_result)
            self.assertIn('quality_classification', resolution_result)
            
            # Validate values
            self.assertGreater(resolution_result['width'], 0)
            self.assertGreater(resolution_result['height'], 0)
            self.assertGreater(resolution_result['pixel_density'], 0)
            self.assertGreater(resolution_result['aspect_ratio'], 0)
        
        # High-quality image should have better metrics
        hq_result = results['high_quality']
        lq_result = results['low_quality']
        
        # Note: Both images have same resolution, but quality should differ
        self.assertEqual(hq_result['width'], lq_result['width'])
        self.assertEqual(hq_result['height'], lq_result['height'])
    
    @pytest.mark.asyncio
    async def test_noise_and_artifacts_detection(self):
        """Test noise detection and compression artifacts analysis."""        # Test high-quality image (should have low noise)
        hq_noise_result = await self.analyzer.detect_noise_and_artifacts(
            str(self.high_quality_image_path)
        )
        
        # Test low-quality image (should have high noise)
        lq_noise_result = await self.analyzer.detect_noise_and_artifacts(
            str(self.low_quality_image_path)
        )
        
        # Validate noise analysis structure
        for result in [hq_noise_result, lq_noise_result]:
            self.assertIn('noise_level', result)
            self.assertIn('noise_type', result)
            self.assertIn('compression_artifacts', result)
            self.assertIn('artifact_locations', result)
            
            # Validate noise level
            self.assertGreaterEqual(result['noise_level'], 0.0)
            self.assertLessEqual(result['noise_level'], 100.0)
            
            # Validate noise type classification
            self.assertIn(result['noise_type'], ['gaussian', 'salt_pepper', 'poisson', 'speckle', 'minimal'])
            
            # Validate compression artifacts
            artifacts = result['compression_artifacts']
            self.assertIn('jpeg_blocking', artifacts)
            self.assertIn('ringing', artifacts)
            self.assertIn('color_bleeding', artifacts)
        
        # Low-quality image should have more noise and artifacts
        self.assertGreater(lq_noise_result['noise_level'], hq_noise_result['noise_level'])
        self.assertGreater(
            lq_noise_result['compression_artifacts']['jpeg_blocking'],
            hq_noise_result['compression_artifacts']['jpeg_blocking']
        )
    
    @pytest.mark.asyncio
    async def test_lighting_and_exposure_analysis(self):
        """Test lighting quality and exposure analysis."""        lighting_result = await self.analyzer.analyze_lighting_exposure(
            str(self.high_quality_image_path)
        )
        
        # Validate lighting analysis structure
        self.assertIn('exposure_quality', lighting_result)
        self.assertIn('dynamic_range', lighting_result)
        self.assertIn('shadow_detail', lighting_result)
        self.assertIn('highlight_detail', lighting_result)
        self.assertIn('overall_lighting_score', lighting_result)
        
        # Validate exposure quality
        exposure = lighting_result['exposure_quality']
        self.assertIn('exposure_level', exposure)
        self.assertIn('exposure_classification', exposure)
        self.assertIn('clipping_analysis', exposure)
        
        self.assertIn(exposure['exposure_classification'], 
                     ['underexposed', 'properly_exposed', 'overexposed'])
        
        # Validate dynamic range
        dynamic_range = lighting_result['dynamic_range']
        self.assertIn('range_score', dynamic_range)
        self.assertIn('histogram_analysis', dynamic_range)
        self.assertIn('contrast_ratio', dynamic_range)
        
        # Validate clipping analysis
        clipping = exposure['clipping_analysis']
        self.assertIn('shadow_clipping_percentage', clipping)
        self.assertIn('highlight_clipping_percentage', clipping)
        
        # Validate overall lighting score
        self.assertGreaterEqual(lighting_result['overall_lighting_score'], 0.0)
        self.assertLessEqual(lighting_result['overall_lighting_score'], 100.0)
    
    @pytest.mark.asyncio
    async def test_orientation_specific_analysis(self):
        """Test analysis for different image orientations."""        # Test portrait orientation
        portrait_result = await self.analyzer.analyze_image_quality(
            str(self.portrait_image_path),
            platform='instagram',
            content_type='portrait'
        )
        
        # Test landscape orientation
        landscape_result = await self.analyzer.analyze_image_quality(
            str(self.landscape_image_path),
            platform='instagram',
            content_type='landscape'
        )
        
        # Validate orientation detection
        portrait_orientation = portrait_result['technical_quality']['orientation']
        landscape_orientation = landscape_result['technical_quality']['orientation']
        
        self.assertEqual(portrait_orientation['type'], 'portrait')
        self.assertEqual(landscape_orientation['type'], 'landscape')
        
        # Validate aspect ratios
        portrait_ratio = portrait_orientation['aspect_ratio']
        landscape_ratio = landscape_orientation['aspect_ratio']
        
        self.assertLess(portrait_ratio, 1.0)  # Height > Width
        self.assertGreater(landscape_ratio, 1.0)  # Width > Height
        
        # Validate composition recommendations differ by orientation
        portrait_recommendations = portrait_result['recommendations']
        landscape_recommendations = landscape_result['recommendations']
        
        self.assertIsInstance(portrait_recommendations, list)
        self.assertIsInstance(landscape_recommendations, list)
        self.assertNotEqual(portrait_recommendations, landscape_recommendations)
    
    def test_image_quality_metrics_data_model(self):
        """Test ImageQualityMetrics data model validation."""        metrics = ImageQualityMetrics(
            overall_score=89.5,
            technical_score=92.0,
            aesthetic_score=87.0,
            composition_score=85.0,
            color_score=91.0,
            resolution_score=95.0,
            sharpness_score=88.0,
            noise_level=12.0  # Lower is better for noise
        )
        
        # Validate metrics structure
        self.assertEqual(metrics.overall_score, 89.5)
        self.assertEqual(metrics.technical_score, 92.0)
        self.assertEqual(metrics.aesthetic_score, 87.0)
        
        # Test metrics serialization
        metrics_dict = metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertIn('overall_score', metrics_dict)
        
        # Test quality level classification
        quality_level = metrics.get_quality_level()
        self.assertIn(quality_level, ['excellent', 'good', 'acceptable', 'poor'])
    
    def test_image_quality_profile_functionality(self):
        """Test ImageQualityProfile class with comprehensive image characteristics."""        profile = ImageQualityProfile(
            content_type='photography',
            platform='instagram',
            target_audience='art_enthusiasts',
            quality_requirements={
                'minimum_resolution': (1080, 1080),
                'minimum_sharpness': 80.0,
                'maximum_noise': 15.0,
                'minimum_composition_score': 75.0
            }
        )
        
        # Validate profile properties
        self.assertEqual(profile.content_type, 'photography')
        self.assertEqual(profile.platform, 'instagram')
        self.assertEqual(profile.target_audience, 'art_enthusiasts')
        
        # Test profile validation
        test_metrics = {
            'resolution': (1920, 1080),
            'sharpness_score': 85.0,
            'noise_level': 12.0,
            'composition_score': 78.0
        }
        
        validation_result = profile.validate_metrics(test_metrics)
        self.assertIsInstance(validation_result, dict)
        self.assertIn('compliant', validation_result)
        self.assertIn('violations', validation_result)
    
    def test_platform_image_standards_validation(self):
        """Test PlatformImageStandards compliance checking."""        standards = PlatformImageStandards()
        
        # Test Instagram standards
        instagram_standards = standards.get_standards('instagram')
        self.assertIsInstance(instagram_standards, dict)
        self.assertIn('preferred_aspect_ratios', instagram_standards)
        self.assertIn('minimum_resolution', instagram_standards)
        self.assertIn('maximum_file_size', instagram_standards)
        
        # Test Pinterest standards
        pinterest_standards = standards.get_standards('pinterest')
        self.assertIsInstance(pinterest_standards, dict)
        self.assertNotEqual(instagram_standards['preferred_aspect_ratios'], 
                           pinterest_standards['preferred_aspect_ratios'])
        
        # Test compliance validation
        test_image_specs = {
            'width': 1080,
            'height': 1080,
            'file_size': 2 * 1024 * 1024,  # 2MB
            'format': 'jpeg',
            'aspect_ratio': 1.0
        }
        
        compliance = standards.check_compliance('instagram', test_image_specs)
        self.assertIsInstance(compliance, dict)
        self.assertIn('compliant', compliance)
        self.assertIn('violations', compliance)
    
    def tearDown(self):
        """Clean up test environment and temporary files."""        import shutil
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)


if __name__ == '__main__':
    # Run comprehensive image quality test suite
    pytest.main([str(Path(__file__)), '-v', '--tb=short'])
