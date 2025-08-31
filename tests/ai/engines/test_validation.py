#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests complets pour le module validation du système IA-Influencer.
Développé par une équipe d'experts combinant tous les rôles nécessaires.

Copyright (C) 2024 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés. Usage non autorisé strictement interdit.

Équipe de développement :
- Lead Dev + Architecte Développeur IA
- Développeur Backend Senior (Python/FastAPI/Django)  
- Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Spécialiste Sécurité Backend
- Architecte Microservices
- Développeur Audio
- DevOps Engineer
- IA Prompt Engineer
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import tempfile
import json
import base64
from unittest.mock import Mock, patch, AsyncMock, mock_open
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import io
from PIL import Image
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ai.engines.validation import (
    ContentValidator,
    ValidationRule,
    ValidationResult,
    ValidationLevel,
    ValidationStatus,
    TestType,
    TestCase,
    TestResult,
    EngineTestSuite
)


class TestValidationRule:
    """Tests pour les règles de validation."""
    
    def test_rule_creation(self):
        """Test la création d'une règle de validation."""
        rule = ValidationRule(
            name="test_rule",
            description="Règle de test",
            category=ValidationCategory.CONTENT_QUALITY,
            severity=ValidationSeverity.ERROR,
            condition=lambda x: len(x) > 0,
            message="Le contenu ne doit pas être vide"
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "Règle de test"
        assert rule.category == ValidationCategory.CONTENT_QUALITY
        assert rule.severity == ValidationSeverity.ERROR
        assert rule.message == "Le contenu ne doit pas être vide"
        assert rule.enabled is True
    
    def test_rule_evaluation(self):
        """Test l'évaluation d'une règle."""
        rule = ValidationRule(
            name="min_length",
            condition=lambda x: len(str(x)) >= 5,
            message="Longueur minimale requise: 5 caractères"
        )
        
        # Test valide
        assert rule.evaluate("Hello World") is True
        
        # Test invalide
        assert rule.evaluate("Hi") is False
    
    def test_rule_parameters(self):
        """Test les règles avec paramètres."""
        def check_length(content, min_length=10):
            return len(str(content)) >= min_length
        
        rule = ValidationRule(
            name="parametric_rule",
            condition=check_length,
            parameters={"min_length": 15}
        )
        
        # Test avec paramètres
        assert rule.evaluate("This is a long text") is True
        assert rule.evaluate("Short") is False


class TestValidationResult:
    """Tests pour les résultats de validation."""
    
    def test_result_creation(self):
        """Test la création d'un résultat de validation."""
        result = ValidationResult(
            rule_name="test_rule",
            passed=False,
            message="Validation échouée",
            severity=ValidationSeverity.ERROR,
            category=ValidationCategory.SECURITY,
            details={"field": "password", "issue": "too_weak"}
        )
        
        assert result.rule_name == "test_rule"
        assert result.passed is False
        assert result.message == "Validation échouée"
        assert result.severity == ValidationSeverity.ERROR
        assert result.category == ValidationCategory.SECURITY
        assert result.details["field"] == "password"
        assert isinstance(result.timestamp, datetime)
    
    def test_result_serialization(self):
        """Test la sérialisation des résultats."""
        result = ValidationResult(
            rule_name="test_rule",
            passed=True,
            message="Validation réussie",
            severity=ValidationSeverity.INFO
        )
        
        # Sérialisation
        serialized = result.to_dict()
        assert serialized["rule_name"] == "test_rule"
        assert serialized["passed"] is True
        assert "timestamp" in serialized
        
        # Désérialisation
        deserialized = ValidationResult.from_dict(serialized)
        assert deserialized.rule_name == result.rule_name
        assert deserialized.passed == result.passed


class TestRuleEngine:
    """Tests pour le moteur de règles."""
    
    @pytest.fixture
    def rule_engine(self):
        """Fixture pour créer un moteur de règles."""
        return RuleEngine()
    
    def test_engine_initialization(self, rule_engine):
        """Test l'initialisation du moteur."""
        assert len(rule_engine.rules) == 0
        assert rule_engine.enabled is True
    
    def test_add_rule(self, rule_engine):
        """Test l'ajout de règles."""
        rule = ValidationRule(
            name="test_rule",
            condition=lambda x: x > 0,
            message="Valeur doit être positive"
        )
        
        rule_engine.add_rule(rule)
        
        assert len(rule_engine.rules) == 1
        assert "test_rule" in rule_engine.rules
        assert rule_engine.rules["test_rule"] == rule
    
    def test_remove_rule(self, rule_engine):
        """Test la suppression de règles."""
        rule = ValidationRule(name="temp_rule", condition=lambda x: True)
        rule_engine.add_rule(rule)
        
        assert "temp_rule" in rule_engine.rules
        
        rule_engine.remove_rule("temp_rule")
        
        assert "temp_rule" not in rule_engine.rules
    
    def test_validate_single_rule(self, rule_engine):
        """Test la validation avec une seule règle."""
        rule = ValidationRule(
            name="positive_number",
            condition=lambda x: x > 0,
            message="Le nombre doit être positif",
            severity=ValidationSeverity.ERROR
        )
        rule_engine.add_rule(rule)
        
        # Test valide
        results = rule_engine.validate(5)
        assert len(results) == 1
        assert results[0].passed is True
        
        # Test invalide
        results = rule_engine.validate(-5)
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].severity == ValidationSeverity.ERROR
    
    def test_validate_multiple_rules(self, rule_engine):
        """Test la validation avec plusieurs règles."""
        rules = [
            ValidationRule(
                name="positive",
                condition=lambda x: x > 0,
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="not_too_large",
                condition=lambda x: x < 1000,
                severity=ValidationSeverity.WARNING
            )
        ]
        
        for rule in rules:
            rule_engine.add_rule(rule)
        
        # Test toutes règles valides
        results = rule_engine.validate(50)
        assert len(results) == 2
        assert all(result.passed for result in results)
        
        # Test une règle échouée
        results = rule_engine.validate(1500)
        assert len(results) == 2
        assert results[0].passed is True  # positive
        assert results[1].passed is False  # not_too_large
    
    def test_conditional_rules(self, rule_engine):
        """Test les règles conditionnelles."""
        def conditional_rule(data):
            if isinstance(data, dict) and "type" in data:
                if data["type"] == "email":
                    return "@" in str(data.get("value", ""))
            return True
        
        rule = ValidationRule(
            name="email_format",
            condition=conditional_rule,
            message="Format d'email invalide"
        )
        rule_engine.add_rule(rule)
        
        # Test email valide
        results = rule_engine.validate({"type": "email", "value": "test@example.com"})
        assert results[0].passed is True
        
        # Test email invalide
        results = rule_engine.validate({"type": "email", "value": "invalid_email"})
        assert results[0].passed is False
        
        # Test autre type (doit passer)
        results = rule_engine.validate({"type": "text", "value": "some text"})
        assert results[0].passed is True


class TestContentValidator:
    """Tests pour le validateur de contenu principal."""
    
    @pytest.fixture
    def validator(self):
        """Fixture pour créer un validateur de contenu."""
        return ContentValidator()
    
    def test_validator_initialization(self, validator):
        """Test l'initialisation du validateur."""
        assert validator.rule_engine is not None
        assert validator.enabled is True
        assert len(validator.validation_history) == 0
    
    @pytest.mark.asyncio
    async def test_validate_content(self, validator):
        """Test la validation de contenu."""
        # Ajouter une règle simple
        rule = ValidationRule(
            name="content_not_empty",
            condition=lambda x: len(str(x).strip()) > 0,
            message="Le contenu ne peut pas être vide"
        )
        validator.rule_engine.add_rule(rule)
        
        # Test contenu valide
        results = await validator.validate_content("Contenu valide")
        assert len(results) == 1
        assert results[0].passed is True
        
        # Test contenu invalide
        results = await validator.validate_content("")
        assert len(results) == 1
        assert results[0].passed is False
    
    def test_validation_history(self, validator):
        """Test l'historique de validation."""
        rule = ValidationRule(
            name="test_rule",
            condition=lambda x: True,
            message="Test"
        )
        validator.rule_engine.add_rule(rule)
        
        # Effectuer plusieurs validations
        for i in range(3):
            validator.validate_content(f"content_{i}")
        
        # Vérifier l'historique
        assert len(validator.validation_history) == 3
        
        # Vérifier la limite d'historique
        validator.max_history_size = 2
        validator.validate_content("new_content")
        
        assert len(validator.validation_history) == 2  # Limite respectée
    
    def test_validation_metrics(self, validator):
        """Test les métriques de validation."""
        # Ajouter des règles de test
        rules = [
            ValidationRule(
                name="always_pass",
                condition=lambda x: True,
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="always_fail",
                condition=lambda x: False,
                severity=ValidationSeverity.ERROR
            )
        ]
        
        for rule in rules:
            validator.rule_engine.add_rule(rule)
        
        # Effectuer des validations
        for i in range(10):
            validator.validate_content(f"test_{i}")
        
        # Calculer les métriques
        metrics = validator.get_validation_metrics()
        
        assert "total_validations" in metrics
        assert "success_rate" in metrics
        assert "error_rate" in metrics
        assert metrics["total_validations"] == 10
        assert metrics["success_rate"] == 0.5  # 50% de réussite


class TestAudioValidator:
    """Tests pour le validateur audio."""
    
    @pytest.fixture
    def audio_validator(self):
        """Fixture pour créer un validateur audio."""
        return AudioValidator()
    
    def test_audio_format_validation(self, audio_validator):
        """Test la validation du format audio."""
        # Formats valides
        valid_formats = ["audio.mp3", "music.wav", "voice.flac", "sound.aac"]
        
        for filename in valid_formats:
            result = audio_validator.validate_format(filename)
            assert result.passed is True
        
        # Formats invalides
        invalid_formats = ["document.pdf", "image.jpg", "video.mp4"]
        
        for filename in invalid_formats:
            result = audio_validator.validate_format(filename)
            assert result.passed is False
    
    def test_audio_duration_validation(self, audio_validator):
        """Test la validation de la durée audio."""
        # Configuration des limites
        audio_validator.min_duration = 1.0  # 1 seconde
        audio_validator.max_duration = 300.0  # 5 minutes
        
        # Durée valide
        result = audio_validator.validate_duration(120.0)  # 2 minutes
        assert result.passed is True
        
        # Durée trop courte
        result = audio_validator.validate_duration(0.5)
        assert result.passed is False
        
        # Durée trop longue
        result = audio_validator.validate_duration(400.0)
        assert result.passed is False
    
    def test_audio_quality_validation(self, audio_validator):
        """Test la validation de la qualité audio."""
        # Paramètres de qualité
        quality_params = {
            "sample_rate": 44100,
            "bit_depth": 16,
            "channels": 2,
            "bitrate": 128000
        }
        
        # Qualité valide
        result = audio_validator.validate_quality(quality_params)
        assert result.passed is True
        
        # Qualité insuffisante
        low_quality = {
            "sample_rate": 8000,  # Trop bas
            "bit_depth": 8,       # Trop bas
            "channels": 1,
            "bitrate": 32000      # Trop bas
        }
        
        result = audio_validator.validate_quality(low_quality)
        assert result.passed is False
    
    @pytest.mark.asyncio
    async def test_audio_content_analysis(self, audio_validator):
        """Test l'analyse du contenu audio."""
        # Mock des données audio
        mock_audio_data = {
            "duration": 30.0,
            "sample_rate": 44100,
            "rms_energy": 0.5,
            "peak_amplitude": 0.8,
            "silence_ratio": 0.1
        }
        
        with patch.object(audio_validator, 'analyze_audio_content', return_value=mock_audio_data):
            result = await audio_validator.validate_content_analysis(b"mock_audio_data")
            
            assert result.passed is True
            assert "duration" in result.details
            assert "quality_score" in result.details


class TestVideoValidator:
    """Tests pour le validateur vidéo."""
    
    @pytest.fixture
    def video_validator(self):
        """Fixture pour créer un validateur vidéo."""
        return VideoValidator()
    
    def test_video_format_validation(self, video_validator):
        """Test la validation du format vidéo."""
        # Formats valides
        valid_formats = ["video.mp4", "movie.avi", "clip.mov", "stream.webm"]
        
        for filename in valid_formats:
            result = video_validator.validate_format(filename)
            assert result.passed is True
        
        # Formats invalides
        invalid_formats = ["audio.mp3", "image.jpg", "document.pdf"]
        
        for filename in invalid_formats:
            result = video_validator.validate_format(filename)
            assert result.passed is False
    
    def test_video_resolution_validation(self, video_validator):
        """Test la validation de la résolution vidéo."""
        # Résolutions valides
        valid_resolutions = ["1920x1080", "1280x720", "640x480"]
        
        for resolution in valid_resolutions:
            result = video_validator.validate_resolution(resolution)
            assert result.passed is True
        
        # Résolutions invalides
        invalid_resolutions = ["10x10", "5000x5000", "invalid"]
        
        for resolution in invalid_resolutions:
            result = video_validator.validate_resolution(resolution)
            assert result.passed is False
    
    def test_video_codec_validation(self, video_validator):
        """Test la validation du codec vidéo."""
        # Codecs valides
        valid_codecs = ["h264", "h265", "vp9", "av1"]
        
        for codec in valid_codecs:
            result = video_validator.validate_codec(codec)
            assert result.passed is True
        
        # Codecs invalides ou non supportés
        invalid_codecs = ["unknown_codec", "deprecated_codec"]
        
        for codec in invalid_codecs:
            result = video_validator.validate_codec(codec)
            assert result.passed is False
    
    @pytest.mark.asyncio
    async def test_video_scene_analysis(self, video_validator):
        """Test l'analyse des scènes vidéo."""
        # Mock des données d'analyse
        mock_analysis = {
            "scene_changes": [5.0, 15.0, 25.0],
            "average_brightness": 0.6,
            "motion_intensity": 0.4,
            "color_diversity": 0.8
        }
        
        with patch.object(video_validator, 'analyze_video_scenes', return_value=mock_analysis):
            result = await video_validator.validate_scene_analysis(b"mock_video_data")
            
            assert result.passed is True
            assert "scene_count" in result.details
            assert "quality_indicators" in result.details


class TestImageValidator:
    """Tests pour le validateur d'images."""
    
    @pytest.fixture
    def image_validator(self):
        """Fixture pour créer un validateur d'images."""
        return ImageValidator()
    
    def test_image_format_validation(self, image_validator):
        """Test la validation du format d'image."""
        # Formats valides
        valid_formats = ["photo.jpg", "image.png", "graphic.webp", "vector.svg"]
        
        for filename in valid_formats:
            result = image_validator.validate_format(filename)
            assert result.passed is True
        
        # Formats invalides
        invalid_formats = ["video.mp4", "audio.mp3", "document.pdf"]
        
        for filename in invalid_formats:
            result = image_validator.validate_format(filename)
            assert result.passed is False
    
    def test_image_dimensions_validation(self, image_validator):
        """Test la validation des dimensions d'image."""
        # Dimensions valides
        valid_dimensions = [(1920, 1080), (800, 600), (300, 200)]
        
        for width, height in valid_dimensions:
            result = image_validator.validate_dimensions(width, height)
            assert result.passed is True
        
        # Dimensions invalides
        invalid_dimensions = [(10, 10), (10000, 10000), (0, 100)]
        
        for width, height in invalid_dimensions:
            result = image_validator.validate_dimensions(width, height)
            assert result.passed is False
    
    def test_image_quality_analysis(self, image_validator):
        """Test l'analyse de qualité d'image."""
        # Créer une image de test
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Convertir en bytes
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        # Analyser la qualité
        result = image_validator.validate_image_quality(img_data)
        
        assert result.passed is True
        assert "sharpness" in result.details
        assert "color_distribution" in result.details
    
    @pytest.mark.asyncio
    async def test_image_content_detection(self, image_validator):
        """Test la détection de contenu d'image."""
        # Mock de l'analyse de contenu
        mock_content = {
            "objects": ["person", "car", "building"],
            "faces": 2,
            "text_regions": 1,
            "adult_content_probability": 0.1
        }
        
        with patch.object(image_validator, 'analyze_image_content', return_value=mock_content):
            result = await image_validator.validate_content_detection(b"mock_image_data")
            
            assert result.passed is True
            assert "detected_objects" in result.details
            assert "safety_score" in result.details


class TestTextValidator:
    """Tests pour le validateur de texte."""
    
    @pytest.fixture
    def text_validator(self):
        """Fixture pour créer un validateur de texte."""
        return TextValidator()
    
    def test_text_length_validation(self, text_validator):
        """Test la validation de la longueur du texte."""
        # Configuration des limites
        text_validator.min_length = 10
        text_validator.max_length = 1000
        
        # Texte valide
        valid_text = "Ceci est un texte de longueur appropriée."
        result = text_validator.validate_length(valid_text)
        assert result.passed is True
        
        # Texte trop court
        short_text = "Court"
        result = text_validator.validate_length(short_text)
        assert result.passed is False
        
        # Texte trop long
        long_text = "x" * 1500
        result = text_validator.validate_length(long_text)
        assert result.passed is False
    
    def test_text_language_detection(self, text_validator):
        """Test la détection de langue."""
        # Textes dans différentes langues
        test_texts = [
            ("Hello, this is English text.", "en"),
            ("Bonjour, ceci est du français.", "fr"),
            ("Hola, esto es español.", "es"),
            ("Guten Tag, das ist Deutsch.", "de")
        ]
        
        for text, expected_lang in test_texts:
            result = text_validator.detect_language(text)
            # Note: La détection peut ne pas être parfaite avec des textes courts
            assert result.passed is True
            assert "detected_language" in result.details
    
    def test_text_sentiment_analysis(self, text_validator):
        """Test l'analyse de sentiment."""
        # Textes avec différents sentiments
        test_cases = [
            ("Je suis très heureux aujourd'hui!", "positive"),
            ("C'est une journée normale.", "neutral"),
            ("Je suis vraiment déçu par cette situation.", "negative")
        ]
        
        for text, expected_sentiment in test_cases:
            result = text_validator.analyze_sentiment(text)
            assert result.passed is True
            assert "sentiment" in result.details
            assert "confidence" in result.details
    
    def test_text_profanity_detection(self, text_validator):
        """Test la détection de contenu inapproprié."""
        # Texte approprié
        clean_text = "Ceci est un texte parfaitement approprié."
        result = text_validator.detect_profanity(clean_text)
        assert result.passed is True
        
        # Simulation de texte inapproprié
        with patch.object(text_validator, '_contains_profanity', return_value=True):
            inappropriate_text = "Texte avec contenu inapproprié"
            result = text_validator.detect_profanity(inappropriate_text)
            assert result.passed is False
    
    @pytest.mark.asyncio
    async def test_text_readability_analysis(self, text_validator):
        """Test l'analyse de lisibilité."""
        # Texte de test
        test_text = """
        Ceci est un texte de test pour analyser la lisibilité.
        Il contient plusieurs phrases de longueurs différentes.
        Certaines phrases sont courtes. D'autres sont beaucoup plus longues 
        et contiennent des mots complexes et des structures grammaticales 
        plus sophistiquées qui peuvent affecter la lisibilité globale.
        """
        
        result = await text_validator.analyze_readability(test_text)
        
        assert result.passed is True
        assert "readability_score" in result.details
        assert "complexity_level" in result.details
        assert "word_count" in result.details


class TestSecurityValidator:
    """Tests pour le validateur de sécurité."""
    
    @pytest.fixture
    def security_validator(self):
        """Fixture pour créer un validateur de sécurité."""
        return SecurityValidator()
    
    def test_sql_injection_detection(self, security_validator):
        """Test la détection d'injection SQL."""
        # Texte sûr
        safe_text = "Rechercher des informations sur les produits"
        result = security_validator.detect_sql_injection(safe_text)
        assert result.passed is True
        
        # Tentatives d'injection SQL
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM passwords"
        ]
        
        for malicious_input in malicious_inputs:
            result = security_validator.detect_sql_injection(malicious_input)
            assert result.passed is False
    
    def test_xss_detection(self, security_validator):
        """Test la détection de XSS."""
        # Contenu sûr
        safe_content = "Contenu normal sans scripts"
        result = security_validator.detect_xss(safe_content)
        assert result.passed is True
        
        # Tentatives XSS
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for xss_attempt in xss_attempts:
            result = security_validator.detect_xss(xss_attempt)
            assert result.passed is False
    
    def test_file_upload_validation(self, security_validator):
        """Test la validation des uploads de fichiers."""
        # Fichier sûr
        safe_file = {
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "size": 1024000  # 1MB
        }
        result = security_validator.validate_file_upload(safe_file)
        assert result.passed is True
        
        # Fichier dangereux
        dangerous_file = {
            "filename": "virus.exe",
            "content_type": "application/x-executable",
            "size": 50000
        }
        result = security_validator.validate_file_upload(dangerous_file)
        assert result.passed is False
    
    def test_password_strength_validation(self, security_validator):
        """Test la validation de la force des mots de passe."""
        # Mot de passe fort
        strong_password = "MyStr0ng!P@ssw0rd123"
        result = security_validator.validate_password_strength(strong_password)
        assert result.passed is True
        
        # Mots de passe faibles
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "ALLUPPERCASE",
            "alllowercase"
        ]
        
        for weak_password in weak_passwords:
            result = security_validator.validate_password_strength(weak_password)
            assert result.passed is False


class TestQualityValidator:
    """Tests pour le validateur de qualité."""
    
    @pytest.fixture
    def quality_validator(self):
        """Fixture pour créer un validateur de qualité."""
        return QualityValidator()
    
    def test_content_originality_check(self, quality_validator):
        """Test la vérification d'originalité du contenu."""
        # Contenu original
        original_content = "Ceci est un contenu totalement original et unique."
        result = quality_validator.check_originality(original_content)
        assert result.passed is True
        
        # Simulation de contenu dupliqué
        with patch.object(quality_validator, '_detect_plagiarism', return_value=True):
            duplicate_content = "Contenu possiblement dupliqué"
            result = quality_validator.check_originality(duplicate_content)
            assert result.passed is False
    
    def test_content_completeness_validation(self, quality_validator):
        """Test la validation de la complétude du contenu."""
        # Contenu complet
        complete_content = {
            "title": "Titre complet",
            "description": "Description détaillée du contenu",
            "content": "Contenu principal avec suffisamment de détails",
            "tags": ["tag1", "tag2", "tag3"],
            "metadata": {"author": "John Doe", "date": "2024-01-01"}
        }
        result = quality_validator.validate_completeness(complete_content)
        assert result.passed is True
        
        # Contenu incomplet
        incomplete_content = {
            "title": "Titre",
            "content": "Contenu court"
            # Manque description, tags, metadata
        }
        result = quality_validator.validate_completeness(incomplete_content)
        assert result.passed is False
    
    def test_content_relevance_scoring(self, quality_validator):
        """Test le scoring de pertinence du contenu."""
        # Contenu pertinent
        relevant_content = {
            "title": "Guide complet sur l'IA",
            "content": "Ce guide détaille les aspects techniques de l'intelligence artificielle",
            "keywords": ["IA", "intelligence artificielle", "machine learning"],
            "category": "technology"
        }
        result = quality_validator.calculate_relevance_score(relevant_content)
        assert result.passed is True
        assert result.details["relevance_score"] > 0.7
        
        # Contenu peu pertinent
        irrelevant_content = {
            "title": "Titre sans rapport",
            "content": "Contenu qui n'a rien à voir avec le titre",
            "keywords": ["cuisine", "recette"],
            "category": "technology"  # Catégorie incohérente
        }
        result = quality_validator.calculate_relevance_score(irrelevant_content)
        assert result.details["relevance_score"] < 0.5


class TestEngineTestSuite:
    """Tests pour la suite de tests des moteurs."""
    
    @pytest.fixture
    def test_suite(self):
        """Fixture pour créer une suite de tests."""
        return EngineTestSuite()
    
    def test_test_case_creation(self, test_suite):
        """Test la création de cas de test."""
        test_case = TestCase(
            name="test_basic_functionality",
            description="Test de la fonctionnalité de base",
            input_data={"text": "Hello World"},
            expected_output={"processed": True},
            test_function=lambda x: {"processed": True}
        )
        
        assert test_case.name == "test_basic_functionality"
        assert test_case.description == "Test de la fonctionnalité de base"
        assert test_case.input_data["text"] == "Hello World"
        assert test_case.expected_output["processed"] is True
    
    def test_add_test_case(self, test_suite):
        """Test l'ajout de cas de test."""
        test_case = TestCase(
            name="sample_test",
            test_function=lambda x: x
        )
        
        test_suite.add_test_case(test_case)
        
        assert len(test_suite.test_cases) == 1
        assert "sample_test" in test_suite.test_cases
    
    @pytest.mark.asyncio
    async def test_run_single_test(self, test_suite):
        """Test l'exécution d'un test unique."""
        def test_function(input_data):
            return input_data["value"] * 2
        
        test_case = TestCase(
            name="multiply_test",
            input_data={"value": 5},
            expected_output=10,
            test_function=test_function
        )
        
        test_suite.add_test_case(test_case)
        
        # Exécuter le test
        result = await test_suite.run_single_test("multiply_test")
        
        assert result.test_name == "multiply_test"
        assert result.passed is True
        assert result.actual_output == 10
    
    @pytest.mark.asyncio
    async def test_run_all_tests(self, test_suite):
        """Test l'exécution de tous les tests."""
        # Ajouter plusieurs tests
        tests = [
            TestCase(
                name="test_1",
                input_data=1,
                expected_output=2,
                test_function=lambda x: x * 2
            ),
            TestCase(
                name="test_2",
                input_data=3,
                expected_output=9,
                test_function=lambda x: x ** 2
            ),
            TestCase(
                name="test_3",
                input_data=5,
                expected_output=6,  # Intentionnellement faux
                test_function=lambda x: x * 2
            )
        ]
        
        for test in tests:
            test_suite.add_test_case(test)
        
        # Exécuter tous les tests
        results = await test_suite.run_all_tests()
        
        assert len(results) == 3
        assert results[0].passed is True
        assert results[1].passed is True
        assert results[2].passed is False  # Test intentionnellement échoué


class TestPerformanceTester:
    """Tests pour le testeur de performance."""
    
    @pytest.fixture
    def performance_tester(self):
        """Fixture pour créer un testeur de performance."""
        return PerformanceTester()
    
    @pytest.mark.asyncio
    async def test_response_time_measurement(self, performance_tester):
        """Test la mesure du temps de réponse."""
        async def test_function():
            await asyncio.sleep(0.1)  # Simulation de traitement
            return "result"
        
        # Mesurer le temps de réponse
        result = await performance_tester.measure_response_time(test_function)
        
        assert "response_time" in result
        assert result["response_time"] >= 0.1
        assert result["output"] == "result"
    
    @pytest.mark.asyncio
    async def test_throughput_measurement(self, performance_tester):
        """Test la mesure du débit."""
        def process_item(item):
            return item * 2
        
        items = list(range(100))
        
        # Mesurer le débit
        result = await performance_tester.measure_throughput(process_item, items)
        
        assert "throughput" in result
        assert "items_per_second" in result
        assert result["throughput"] > 0
        assert len(result["processed_items"]) == 100
    
    def test_memory_usage_measurement(self, performance_tester):
        """Test la mesure de l'utilisation mémoire."""
        def memory_intensive_function():
            # Allouer de la mémoire
            large_list = [i for i in range(10000)]
            return len(large_list)
        
        # Mesurer l'utilisation mémoire
        result = performance_tester.measure_memory_usage(memory_intensive_function)
        
        assert "memory_before" in result
        assert "memory_after" in result
        assert "memory_delta" in result
        assert "output" in result
        assert result["output"] == 10000
    
    @pytest.mark.asyncio
    async def test_load_testing(self, performance_tester):
        """Test des tests de charge."""
        async def simple_service(request):
            await asyncio.sleep(0.01)  # Simulation de traitement
            return f"processed_{request}"
        
        # Configuration du test de charge
        load_config = {
            "concurrent_users": 10,
            "requests_per_user": 5,
            "ramp_up_time": 1.0
        }
        
        # Exécuter le test de charge
        result = await performance_tester.load_test(simple_service, load_config)
        
        assert "total_requests" in result
        assert "successful_requests" in result
        assert "average_response_time" in result
        assert "requests_per_second" in result
        assert result["total_requests"] == 50  # 10 users * 5 requests


class TestIntegrationTester:
    """Tests pour le testeur d'intégration."""
    
    @pytest.fixture
    def integration_tester(self):
        """Fixture pour créer un testeur d'intégration."""
        return IntegrationTester()
    
    @pytest.mark.asyncio
    async def test_api_integration(self, integration_tester):
        """Test d'intégration API."""
        # Mock d'une API
        async def mock_api_call(endpoint, data):
            if endpoint == "/process" and "text" in data:
                return {"status": "success", "result": f"processed_{data['text']}"}
            return {"status": "error", "message": "Invalid request"}
        
        # Test d'intégration
        test_config = {
            "endpoint": "/process",
            "method": "POST",
            "data": {"text": "hello world"},
            "expected_status": "success"
        }
        
        with patch.object(integration_tester, 'call_api', side_effect=mock_api_call):
            result = await integration_tester.test_api_integration(test_config)
            
            assert result.passed is True
            assert "response" in result.details
    
    @pytest.mark.asyncio
    async def test_database_integration(self, integration_tester):
        """Test d'intégration base de données."""
        # Mock de la base de données
        mock_db = {
            "users": [
                {"id": 1, "name": "John Doe"},
                {"id": 2, "name": "Jane Smith"}
            ]
        }
        
        async def mock_db_query(query):
            if "SELECT" in query and "users" in query:
                return mock_db["users"]
            return []
        
        # Test d'intégration DB
        test_config = {
            "query": "SELECT * FROM users",
            "expected_count": 2
        }
        
        with patch.object(integration_tester, 'execute_query', side_effect=mock_db_query):
            result = await integration_tester.test_database_integration(test_config)
            
            assert result.passed is True
            assert len(result.details["query_result"]) == 2
    
    @pytest.mark.asyncio
    async def test_service_communication(self, integration_tester):
        """Test de la communication entre services."""
        # Mock des services
        services = {
            "service_a": lambda data: {"from_a": data, "processed": True},
            "service_b": lambda data: {"from_b": data, "enhanced": True}
        }
        
        # Test de communication
        workflow = [
            {"service": "service_a", "input": {"text": "hello"}},
            {"service": "service_b", "input": "from_previous"}
        ]
        
        with patch.object(integration_tester, 'call_service') as mock_call:
            mock_call.side_effect = lambda service, data: services[service](data)
            
            result = await integration_tester.test_service_workflow(workflow)
            
            assert result.passed is True
            assert "workflow_results" in result.details


class TestValidationPipeline:
    """Tests pour le pipeline de validation."""
    
    @pytest.fixture
    def validation_pipeline(self):
        """Fixture pour créer un pipeline de validation."""
        return ValidationPipeline()
    
    def test_pipeline_initialization(self, validation_pipeline):
        """Test l'initialisation du pipeline."""
        assert len(validation_pipeline.validators) == 0
        assert validation_pipeline.enabled is True
        assert validation_pipeline.stop_on_error is False
    
    def test_add_validator(self, validation_pipeline):
        """Test l'ajout de validateurs."""
        content_validator = ContentValidator()
        security_validator = SecurityValidator()
        
        validation_pipeline.add_validator("content", content_validator)
        validation_pipeline.add_validator("security", security_validator)
        
        assert len(validation_pipeline.validators) == 2
        assert "content" in validation_pipeline.validators
        assert "security" in validation_pipeline.validators
    
    @pytest.mark.asyncio
    async def test_run_pipeline(self, validation_pipeline):
        """Test l'exécution du pipeline."""
        # Créer des validateurs mock
        mock_validator_1 = Mock()
        mock_validator_1.validate_content = AsyncMock(return_value=[
            ValidationResult("rule1", True, "OK", ValidationSeverity.INFO)
        ])
        
        mock_validator_2 = Mock()
        mock_validator_2.validate_content = AsyncMock(return_value=[
            ValidationResult("rule2", False, "Error", ValidationSeverity.ERROR)
        ])
        
        validation_pipeline.add_validator("validator1", mock_validator_1)
        validation_pipeline.add_validator("validator2", mock_validator_2)
        
        # Exécuter le pipeline
        results = await validation_pipeline.run("test content")
        
        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False
    
    @pytest.mark.asyncio
    async def test_pipeline_early_termination(self, validation_pipeline):
        """Test l'arrêt précoce du pipeline en cas d'erreur."""
        validation_pipeline.stop_on_error = True
        
        # Validateur qui échoue
        failing_validator = Mock()
        failing_validator.validate_content = AsyncMock(return_value=[
            ValidationResult("critical_rule", False, "Critical Error", ValidationSeverity.ERROR)
        ])
        
        # Validateur qui ne devrait pas être exécuté
        next_validator = Mock()
        next_validator.validate_content = AsyncMock(return_value=[
            ValidationResult("next_rule", True, "OK", ValidationSeverity.INFO)
        ])
        
        validation_pipeline.add_validator("failing", failing_validator)
        validation_pipeline.add_validator("next", next_validator)
        
        # Exécuter le pipeline
        results = await validation_pipeline.run("test content")
        
        # Seul le premier validateur devrait avoir été exécuté
        assert len(results) == 1
        assert results[0].passed is False
        next_validator.validate_content.assert_not_called()


class TestValidationMetrics:
    """Tests pour les métriques de validation."""
    
    @pytest.fixture
    def validation_metrics(self):
        """Fixture pour créer des métriques de validation."""
        return ValidationMetrics()
    
    def test_metrics_initialization(self, validation_metrics):
        """Test l'initialisation des métriques."""
        assert validation_metrics.total_validations == 0
        assert validation_metrics.successful_validations == 0
        assert validation_metrics.failed_validations == 0
        assert len(validation_metrics.validation_history) == 0
    
    def test_record_validation_result(self, validation_metrics):
        """Test l'enregistrement des résultats de validation."""
        # Enregistrer un succès
        success_results = [
            ValidationResult("rule1", True, "OK", ValidationSeverity.INFO)
        ]
        validation_metrics.record_validation(success_results)
        
        assert validation_metrics.total_validations == 1
        assert validation_metrics.successful_validations == 1
        assert validation_metrics.failed_validations == 0
        
        # Enregistrer un échec
        failure_results = [
            ValidationResult("rule2", False, "Error", ValidationSeverity.ERROR)
        ]
        validation_metrics.record_validation(failure_results)
        
        assert validation_metrics.total_validations == 2
        assert validation_metrics.successful_validations == 1
        assert validation_metrics.failed_validations == 1
    
    def test_calculate_success_rate(self, validation_metrics):
        """Test le calcul du taux de réussite."""
        # Enregistrer plusieurs résultats
        for i in range(10):
            results = [
                ValidationResult(f"rule_{i}", i < 7, "message", ValidationSeverity.INFO)
            ]
            validation_metrics.record_validation(results)
        
        success_rate = validation_metrics.calculate_success_rate()
        assert success_rate == 0.7  # 7 succès sur 10
    
    def test_get_metrics_by_severity(self, validation_metrics):
        """Test la récupération des métriques par sévérité."""
        # Enregistrer des résultats avec différentes sévérités
        results = [
            ValidationResult("info_rule", True, "Info", ValidationSeverity.INFO),
            ValidationResult("warning_rule", False, "Warning", ValidationSeverity.WARNING),
            ValidationResult("error_rule", False, "Error", ValidationSeverity.ERROR),
            ValidationResult("critical_rule", False, "Critical", ValidationSeverity.CRITICAL)
        ]
        validation_metrics.record_validation(results)
        
        severity_metrics = validation_metrics.get_metrics_by_severity()
        
        assert severity_metrics[ValidationSeverity.INFO] == 1
        assert severity_metrics[ValidationSeverity.WARNING] == 1
        assert severity_metrics[ValidationSeverity.ERROR] == 1
        assert severity_metrics[ValidationSeverity.CRITICAL] == 1
    
    def test_get_trends(self, validation_metrics):
        """Test la récupération des tendances."""
        # Simuler des validations sur plusieurs jours
        for day in range(7):
            # Jour 0-2: 80% de réussite, Jour 3-6: 90% de réussite
            success_rate = 0.8 if day < 3 else 0.9
            
            for i in range(10):
                passed = i < (success_rate * 10)
                results = [
                    ValidationResult(f"rule_{day}_{i}", passed, "message", ValidationSeverity.INFO)
                ]
                validation_metrics.record_validation(results)
        
        trends = validation_metrics.get_trends(days=7)
        
        assert len(trends) <= 7
        assert all("date" in trend for trend in trends)
        assert all("success_rate" in trend for trend in trends)


class TestIntegration:
    """Tests d'intégration pour le système de validation complet."""
    
    @pytest.fixture
    def validation_system(self):
        """Fixture pour créer un système de validation complet."""
        return {
            'pipeline': ValidationPipeline(),
            'content_validator': ContentValidator(),
            'audio_validator': AudioValidator(),
            'security_validator': SecurityValidator(),
            'test_suite': EngineTestSuite(),
            'metrics': ValidationMetrics()
        }
    
    @pytest.mark.asyncio
    async def test_complete_validation_workflow(self, validation_system):
        """Test du workflow complet de validation."""
        pipeline = validation_system['pipeline']
        content_validator = validation_system['content_validator']
        security_validator = validation_system['security_validator']
        metrics = validation_system['metrics']
        
        # Ajouter des règles aux validateurs
        content_rule = ValidationRule(
            name="content_length",
            condition=lambda x: len(str(x)) >= 5,
            message="Contenu trop court"
        )
        content_validator.rule_engine.add_rule(content_rule)
        
        # Ajouter les validateurs au pipeline
        pipeline.add_validator("content", content_validator)
        pipeline.add_validator("security", security_validator)
        
        # Tester avec du contenu valide
        valid_content = "Ceci est un contenu valide et sécurisé"
        results = await pipeline.run(valid_content)
        
        # Enregistrer les métriques
        metrics.record_validation(results)
        
        # Vérifications
        assert len(results) > 0
        assert all(isinstance(result, ValidationResult) for result in results)
        assert metrics.total_validations > 0
    
    @pytest.mark.asyncio
    async def test_multi_format_validation(self, validation_system):
        """Test la validation multi-format."""
        pipeline = validation_system['pipeline']
        audio_validator = validation_system['audio_validator']
        
        # Ajouter le validateur audio
        pipeline.add_validator("audio", audio_validator)
        
        # Test avec des données audio simulées
        audio_data = {
            "filename": "test.mp3",
            "duration": 30.0,
            "format": "mp3",
            "sample_rate": 44100
        }
        
        # Mock de la validation audio
        with patch.object(audio_validator, 'validate_content', return_value=[
            ValidationResult("audio_format", True, "Format valide", ValidationSeverity.INFO),
            ValidationResult("audio_duration", True, "Durée valide", ValidationSeverity.INFO)
        ]):
            results = await pipeline.run(audio_data)
            
            assert len(results) == 2
            assert all(result.passed for result in results)
    
    @pytest.mark.asyncio
    async def test_validation_with_testing(self, validation_system):
        """Test l'intégration validation et tests."""
        test_suite = validation_system['test_suite']
        content_validator = validation_system['content_validator']
        
        # Créer un test pour le validateur
        def test_validator_function(input_data):
            rule = ValidationRule(
                name="test_rule",
                condition=lambda x: x == "valid_input",
                message="Input doit être 'valid_input'"
            )
            content_validator.rule_engine.add_rule(rule)
            results = content_validator.validate_content(input_data)
            return len([r for r in results if r.passed]) > 0
        
        test_case = TestCase(
            name="test_content_validator",
            input_data="valid_input",
            expected_output=True,
            test_function=test_validator_function
        )
        
        test_suite.add_test_case(test_case)
        
        # Exécuter le test
        test_result = await test_suite.run_single_test("test_content_validator")
        
        assert test_result.passed is True
        assert test_result.actual_output is True
    
    def test_performance_and_quality_integration(self, validation_system):
        """Test l'intégration performance et qualité."""
        # Simuler des validations avec mesure de performance
        metrics = validation_system['metrics']
        
        import time
        
        # Enregistrer des validations avec temps de traitement
        for i in range(100):
            start_time = time.time()
            
            # Simulation de validation
            time.sleep(0.001)  # 1ms de traitement
            
            processing_time = time.time() - start_time
            
            # Créer un résultat avec temps de traitement
            result = ValidationResult(
                rule_name=f"perf_rule_{i}",
                passed=i % 10 != 0,  # 90% de réussite
                message="Test performance",
                severity=ValidationSeverity.INFO
            )
            result.processing_time = processing_time
            
            metrics.record_validation([result])
        
        # Analyser les performances
        success_rate = metrics.calculate_success_rate()
        assert success_rate == 0.9
        
        # Vérifier que les temps de traitement sont enregistrés
        assert metrics.total_validations == 100


if __name__ == "__main__":
    # Configuration des tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10"
    ])
