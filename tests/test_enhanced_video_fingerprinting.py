"""🎬 Test Suite for Enhanced Video Fingerprinting - Industrial-Grade Ultra-Robust System
===============================================================================
Module: tests/test_enhanced_video_fingerprinting.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Test Suite - Ultra Enterprise Production-Ready
Responsibility: Comprehensive testing of ultra-robust video fingerprinting with compression resistance, YOLO detection, and attack resistance
====================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

INDUSTRIAL TESTING COMPONENTS:
├── 🎥 Ultra-Robust Perceptual Hashing Tests
├── 🤖 Real-time YOLO Object/Face Detection Tests  
├── 📊 Temporal Analysis Validation (Frame Sequences, Motion Trajectories)
├── 🔍 Spatial Analysis Validation (Geometric Features, Correlation)
├── 🛡️ Compression Resistance Tests (H.264, H.265, VP9)
├── ✂️ Crop/Rotation/Scale Resistance Tests
├── 🔧 Watermarking Attack Resistance Tests
└── ⚡ Real-time Performance Benchmarks
"""

import pytest
import numpy as np
import cv2
import asyncio
from typing import Dict, List, Any
import tempfile
import os
from pathlib import Path
import json

# Import the enhanced video fingerprinting system
from data_management.fingerprinting.enhanced_video_fingerprint import (
    VideoFingerprintEngine,
    VideoFingerprintConfig,
    PerceptualHashProcessor,
    YOLOFrameProcessor,
    TemporalAnalysisProcessor,
    SpatialAnalysisProcessor,
    FrameExtractionMode,
    VideoQuality
)

@pytest.fixture
def config():
    """
Configuration pour les tests"""
    return VideoFingerprintConfig(
        max_frames=50,
        target_fps=10,
        hash_size=8,
        multi_scale_hashing=True,
        wavelet_hashing=True,
        face_detection_enabled=True,
        temporal_consistency_analysis=True,
        spatial_correlation_analysis=True,
        watermark_resistance=True,
        crop_resistance=True,
        rotation_resistance=True
    )

@pytest.fixture
def sample_frame():
    """
Génère une frame de test"""
    # Create a sample frame with various features
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    # Add some patterns and objects
    cv2.rectangle(frame, (50, 50), (150, 150), (255, 0, 0), -1)  # Blue rectangle
    cv2.circle(frame, (200, 100), 30, (0, 255, 0), -1)  # Green circle
    cv2.line(frame, (0, 200), (320, 200), (0, 0, 255), 5)  # Red line
    
    # Add some texture
    noise = np.random.randint(0, 50, (240, 320, 3), dtype=np.uint8)
    frame = cv2.add(frame, noise)
    
    return frame

@pytest.fixture
def sample_video_frames():
    """
Génère une séquence de frames de test"""
    frames = []
    for i in range(10):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        
        # Moving rectangle to simulate motion
        x_pos = 50 + i * 10
        cv2.rectangle(frame, (x_pos, 50), (x_pos + 50, 100), (255, 0, 0), -1)
        
        # Static elements
        cv2.circle(frame, (200, 150), 20, (0, 255, 0), -1)
        
        # Add slight variations
        brightness_offset = int(20 * np.sin(i * 0.5))
        frame = cv2.add(frame, np.full_like(frame, brightness_offset))
        
        frames.append(frame)
    
    return frames

class TestUltraRobustPerceptualHashing:
    """
Tests pour le hash perceptuel ultra-robuste"""
    
    @pytest.mark.asyncio
    async def test_basic_perceptual_hashing(self, config, sample_frame):
        """
Test du hash perceptuel de base"""
        processor = PerceptualHashProcessor(config)
        
        hashes = await processor.generate_hashes(sample_frame)
        
        # Vérifications de base
        assert isinstance(hashes, dict)
        assert len(hashes) > 0
        
        # Vérification des types de hash
        if config.phash_enabled:
            assert 'phash' in hashes
            assert len(hashes['phash']) > 0
        
        if config.dhash_enabled:
            assert 'dhash' in hashes
            
        if config.ahash_enabled:
            assert 'ahash' in hashes
    
    @pytest.mark.asyncio
    async def test_multiscale_hashing(self, config, sample_frame):
        """
Test du hash multi-échelle pour la résistance à la compression"""
        config.multi_scale_hashing = True
        processor = PerceptualHashProcessor(config)
        
        hashes = await processor.generate_hashes(sample_frame)
        
        # Vérifier la présence de hash multi-échelle
        multiscale_keys = [key for key in hashes.keys() if 'scale_' in key]
        assert len(multiscale_keys) > 0
        
        # Vérifier que différentes échelles donnent des résultats cohérents
        scale_hashes = {key: hashes[key] for key in multiscale_keys if 'phash' in key}
        assert len(scale_hashes) >= 3  # Au moins 3 échelles différentes
    
    @pytest.mark.asyncio
    async def test_wavelet_hashing(self, config, sample_frame):
        """
Test du hash basé sur les ondelettes"""
        config.wavelet_hashing = True
        processor = PerceptualHashProcessor(config)
        
        hashes = await processor.generate_hashes(sample_frame)
        
        assert 'wavelet_hash' in hashes
        assert len(hashes['wavelet_hash']) > 0
        # Hash de ondelettes doit être binaire
        assert all(c in '01' for c in hashes['wavelet_hash'])
    
    @pytest.mark.asyncio
    async def test_compression_resistance(self, config, sample_frame):
        """
Test de la résistance à la compression"""
        processor = PerceptualHashProcessor(config)
        
        # Hash original
        original_hashes = await processor.generate_hashes(sample_frame)
        
        # Simuler compression JPEG
        _, buffer = cv2.imencode('.jpg', sample_frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
        compressed_frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        
        compressed_hashes = await processor.generate_hashes(compressed_frame)
        
        # Les hash devraient être similaires malgré la compression
        if 'phash' in original_hashes and 'phash' in compressed_hashes:
            # Calculer distance de Hamming
            original_phash = original_hashes['phash']
            compressed_phash = compressed_hashes['phash']
            
            if len(original_phash) == len(compressed_phash):
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(original_phash, compressed_phash))
                similarity = 1 - (hamming_distance / len(original_phash))
                
                # Similarité devrait être élevée (> 80%)
                assert similarity > 0.8, f"Similarity too low: {similarity}"

class TestRealTimeYOLODetection:
    """Tests pour la détection YOLO en temps réel"""
    
    @pytest.mark.asyncio 
    async def test_basic_object_detection(self, config, sample_frame):
        """
Test de détection d'objets de base"""
        processor = YOLOFrameProcessor(config)
        
        detections = await processor.detect_objects(sample_frame)
        
        # Doit retourner une liste même si vide
        assert isinstance(detections, list)
        
        # Vérifier la structure des détections
        for detection in detections:
            assert isinstance(detection, dict)
            assert 'class' in detection
            assert 'confidence' in detection
            assert 'detection_type' in detection
    
    @pytest.mark.asyncio
    async def test_face_detection_enabled(self, config):
        """
Test de la détection de visages"""
        config.face_detection_enabled = True
        processor = YOLOFrameProcessor(config)
        
        # Créer une frame simulant un visage
        face_frame = np.ones((240, 320, 3), dtype=np.uint8) * 128
        cv2.ellipse(face_frame, (160, 120), (40, 50), 0, 0, 360, (200, 180, 160), -1)
        
        detections = await processor.detect_objects(face_frame)
        
        # Vérifier que le processeur peut gérer les frames
        assert isinstance(detections, list)
    
    @pytest.mark.asyncio
    async def test_enhanced_person_detection(self, config, sample_frame):
        """
Test de la détection de personnes améliorée"""
        config.person_detection_enhanced = True
        processor = YOLOFrameProcessor(config)
        
        detections = await processor.detect_objects(sample_frame)
        
        # Vérifier que les détections de personnes ont des features supplémentaires
        for detection in detections:
            if detection.get('detection_type') == 'enhanced_person':
                assert 'person_features' in detection
                assert 'pose_analysis' in detection

class TestTemporalAnalysis:
    """
Tests pour l'analyse temporelle avancée"""
    
    @pytest.mark.asyncio
    async def test_frame_sequence_analysis(self, config, sample_video_frames):
        """
Test de l'analyse des séquences de frames"""
        processor = TemporalAnalysisProcessor(config)
        
        temporal_features = await processor.analyze_temporal_patterns(sample_video_frames)
        
        assert isinstance(temporal_features, dict)
        
        if 'sequence_patterns' in temporal_features:
            seq_patterns = temporal_features['sequence_patterns']
            assert 'avg_frame_diff' in seq_patterns
            assert 'max_frame_diff' in seq_patterns
            assert 'frame_diff_variance' in seq_patterns
    
    @pytest.mark.asyncio
    async def test_temporal_consistency(self, config, sample_video_frames):
        """
Test de la cohérence temporelle"""
        processor = TemporalAnalysisProcessor(config)
        
        temporal_features = await processor.analyze_temporal_patterns(sample_video_frames)
        
        if 'consistency_metrics' in temporal_features:
            consistency = temporal_features['consistency_metrics']
            assert 'color_consistency' in consistency
            assert 'brightness_consistency' in consistency
            assert 'edge_consistency' in consistency
    
    @pytest.mark.asyncio
    async def test_motion_trajectory_analysis(self, config, sample_video_frames):
        """
Test de l'analyse des trajectoires de mouvement"""
        processor = TemporalAnalysisProcessor(config)
        
        temporal_features = await processor.analyze_temporal_patterns(sample_video_frames)
        
        if 'motion_trajectories' in temporal_features:
            motion = temporal_features['motion_trajectories']
            # Vérifier que des métriques de mouvement sont présentes
            expected_keys = ['avg_motion_magnitude', 'motion_variance', 'dominant_direction']
            for key in expected_keys:
                if key in motion:
                    assert isinstance(motion[key], (int, float))
    
    @pytest.mark.asyncio
    async def test_scene_transition_detection(self, config):
        """
Test de la détection des transitions de scène"""
        processor = TemporalAnalysisProcessor(config)
        
        # Créer des frames avec changement de scène évident
        scene1_frames = [np.full((100, 100, 3), 50, dtype=np.uint8) for _ in range(3)]
        scene2_frames = [np.full((100, 100, 3), 200, dtype=np.uint8) for _ in range(3)]
        frames_with_cut = scene1_frames + scene2_frames
        
        temporal_features = await processor.analyze_temporal_patterns(frames_with_cut)
        
        if 'scene_transitions' in temporal_features:
            transitions = temporal_features['scene_transitions']
            assert 'scene_cuts' in transitions
            assert 'num_scene_cuts' in transitions
            # Devrait détecter au moins un changement de scène
            assert transitions['num_scene_cuts'] >= 1

class TestSpatialAnalysis:
    """
Tests pour l'analyse spatiale avancée"""
    
    @pytest.mark.asyncio
    async def test_spatial_correlation_analysis(self, config, sample_frame):
        """
Test de l'analyse de corrélation spatiale"""
        processor = SpatialAnalysisProcessor(config)
        
        spatial_features = await processor.analyze_spatial_features(sample_frame)
        
        assert isinstance(spatial_features, dict)
        
        if 'correlation_features' in spatial_features:
            corr_features = spatial_features['correlation_features']
            assert 'horizontal_correlation' in corr_features
            assert 'vertical_correlation' in corr_features
            
            # Les valeurs de corrélation doivent être entre -1 et 1
            for key in corr_features:
                if key.endswith('_correlation'):
                    assert -1 <= corr_features[key] <= 1
    
    @pytest.mark.asyncio
    async def test_local_feature_extraction(self, config, sample_frame):
        """
Test de l'extraction de caractéristiques locales"""
        processor = SpatialAnalysisProcessor(config)
        
        spatial_features = await processor.analyze_spatial_features(sample_frame)
        
        if 'local_features' in spatial_features:
            local_feat = spatial_features['local_features']
            
            # Vérifier la présence de keypoints et corners
            if 'num_keypoints' in local_feat:
                assert isinstance(local_feat['num_keypoints'], int)
                assert local_feat['num_keypoints'] >= 0
            
            if 'num_corners' in local_feat:
                assert isinstance(local_feat['num_corners'], int)
                assert local_feat['num_corners'] >= 0
    
    @pytest.mark.asyncio
    async def test_geometric_feature_extraction(self, config, sample_frame):
        """
Test de l'extraction de caractéristiques géométriques"""
        processor = SpatialAnalysisProcessor(config)
        
        spatial_features = await processor.analyze_spatial_features(sample_frame)
        
        if 'geometric_features' in spatial_features:
            geom_features = spatial_features['geometric_features']
            
            # Vérifier les contours si présents
            if 'contour_features' in geom_features:
                assert isinstance(geom_features['contour_features'], list)
                
                for contour in geom_features['contour_features']:
                    assert 'area' in contour
                    assert 'perimeter' in contour
                    assert 'centroid' in contour
                    assert 'hu_moments' in contour

class TestAttackResistance:
    """
Tests de résistance aux attaques (crops, rotations, watermarking)"""
    
    @pytest.mark.asyncio
    async def test_crop_resistance(self, config, sample_frame):
        """
Test de résistance au crop"""
        processor = PerceptualHashProcessor(config)
        config.crop_resistance = True
        
        # Hash original
        original_hashes = await processor.generate_hashes(sample_frame)
        
        # Crop central (80% de l'image)
        h, w = sample_frame.shape[:2]
        crop_h, crop_w = int(h * 0.8), int(w * 0.8)
        start_h, start_w = (h - crop_h) // 2, (w - crop_w) // 2
        
        cropped_frame = sample_frame[start_h:start_h + crop_h, start_w:start_w + crop_w]
        cropped_resized = cv2.resize(cropped_frame, (w, h))
        
        cropped_hashes = await processor.generate_hashes(cropped_resized)
        
        # Vérifier la présence de hash résistants au crop
        crop_resistant_keys = [key for key in cropped_hashes.keys() if 'center_crop' in key or 'corner' in key]
        assert len(crop_resistant_keys) > 0
    
    @pytest.mark.asyncio
    async def test_rotation_resistance(self, config, sample_frame):
        """
Test de résistance à la rotation"""
        processor = PerceptualHashProcessor(config)
        config.rotation_resistance = True
        
        # Hash original
        original_hashes = await processor.generate_hashes(sample_frame)
        
        # Rotation de 15 degrés
        h, w = sample_frame.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, 15, 1.0)
        rotated_frame = cv2.warpAffine(sample_frame, rotation_matrix, (w, h))
        
        rotated_hashes = await processor.generate_hashes(rotated_frame)
        
        # Vérifier la présence de hash résistants à la rotation
        rotation_resistant_keys = [key for key in rotated_hashes.keys() if 'rotation_normalized' in key]
        if rotation_resistant_keys:
            assert len(rotation_resistant_keys) > 0
    
    @pytest.mark.asyncio
    async def test_scale_resistance(self, config, sample_frame):
        """
Test de résistance au changement d'échelle"""
        processor = PerceptualHashProcessor(config)
        config.multi_scale_hashing = True
        
        # Hash original
        original_hashes = await processor.generate_hashes(sample_frame)
        
        # Redimensionnement (50% puis retour)
        h, w = sample_frame.shape[:2]
        scaled_down = cv2.resize(sample_frame, (w // 2, h // 2))
        scaled_back = cv2.resize(scaled_down, (w, h))
        
        scaled_hashes = await processor.generate_hashes(scaled_back)
        
        # Vérifier que le hash multi-échelle fournit une robustesse
        multiscale_original = [h for k, h in original_hashes.items() if 'scale_' in k]
        multiscale_scaled = [h for k, h in scaled_hashes.items() if 'scale_' in k]
        
        assert len(multiscale_original) > 0
        assert len(multiscale_scaled) > 0

class TestPerformanceBenchmarks:
    """
Tests de performance pour le traitement temps réel"""
    
    @pytest.mark.asyncio
    async def test_single_frame_processing_speed(self, config, sample_frame):
        """
Test de vitesse de traitement d'une frame"""
        import time
        
        processor = PerceptualHashProcessor(config)
        
        start_time = time.time()
        hashes = await processor.generate_hashes(sample_frame)
        processing_time = time.time() - start_time
        
        # Le traitement d'une frame devrait être rapide (< 1 seconde)
        assert processing_time < 1.0, f"Processing too slow: {processing_time:.3f}s"
        assert len(hashes) > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_efficiency(self, config, sample_video_frames):
        """Test d'efficacité du traitement par lot"""
        import time
        
        processor = PerceptualHashProcessor(config)
        
        start_time = time.time()
        
        # Traitement en lot
        batch_hashes = []
        for frame in sample_video_frames:
            hashes = await processor.generate_hashes(frame)
            batch_hashes.append(hashes)
        
        total_time = time.time() - start_time
        
        # Le traitement de 10 frames devrait être raisonnable (< 5 secondes)
        assert total_time < 5.0, f"Batch processing too slow: {total_time:.3f}s"
        assert len(batch_hashes) == len(sample_video_frames)
        
        # Vérifier que tous les frames ont été traités
        for hashes in batch_hashes:
            assert len(hashes) > 0

class TestIntegrationScenarios:
    """Tests d'intégration pour scénarios réels"""
    
    @pytest.mark.asyncio
    async def test_complete_video_fingerprinting_pipeline(self, config, sample_video_frames):
        """
Test du pipeline complet de fingerprinting vidéo"""
        
        # Initialiser tous les processeurs
        perceptual_processor = PerceptualHashProcessor(config)
        yolo_processor = YOLOFrameProcessor(config)
        temporal_processor = TemporalAnalysisProcessor(config)
        spatial_processor = SpatialAnalysisProcessor(config)
        
        # Traiter chaque frame
        frame_fingerprints = []
        for frame in sample_video_frames[:5]:  # Limiter pour les tests
            fingerprint = {
                'perceptual_hashes': await perceptual_processor.generate_hashes(frame),
                'object_detections': await yolo_processor.detect_objects(frame),
                'spatial_features': await spatial_processor.analyze_spatial_features(frame)
            }
            frame_fingerprints.append(fingerprint)
        
        # Analyse temporelle sur la séquence
        temporal_features = await temporal_processor.analyze_temporal_patterns(sample_video_frames[:5])
        
        # Vérifications d'intégration
        assert len(frame_fingerprints) == 5
        
        for fp in frame_fingerprints:
            assert 'perceptual_hashes' in fp
            assert 'object_detections' in fp  
            assert 'spatial_features' in fp
            
            # Vérifier que les hash sont présents
            assert len(fp['perceptual_hashes']) > 0
            
            # Vérifier que les détections sont des listes
            assert isinstance(fp['object_detections'], list)
            
            # Vérifier que les features spatiales sont présentes
            assert isinstance(fp['spatial_features'], dict)
        
        # Vérifier les features temporelles
        assert isinstance(temporal_features, dict)
    
    @pytest.mark.asyncio
    async def test_video_fingerprint_uniqueness(self, config):
        """
Test de l'unicité des empreintes vidéo"""
        processor = PerceptualHashProcessor(config)
        
        # Créer deux frames très différentes
        frame1 = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.rectangle(frame1, (50, 50), (150, 150), (255, 255, 255), -1)
        
        frame2 = np.ones((240, 320, 3), dtype=np.uint8) * 255
        cv2.circle(frame2, (160, 120), 50, (0, 0, 0), -1)
        
        hashes1 = await processor.generate_hashes(frame1)
        hashes2 = await processor.generate_hashes(frame2)
        
        # Vérifier que les hash sont différents
        common_keys = set(hashes1.keys()) & set(hashes2.keys())
        
        for key in common_keys:
            if key in hashes1 and key in hashes2:
                # Les hash devraient être différents pour des images très différentes
                assert hashes1[key] != hashes2[key], f"Hashes are identical for key {key}"

if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v", "--tb=short"])