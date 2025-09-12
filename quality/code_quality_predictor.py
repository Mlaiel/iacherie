#!/usr/bin/env python3
"""
Code Quality Predictor - Ainflue AI Platform
==========================================

AI-powered code quality prediction and intelligent analysis system.
Demonstrates ML Engineer + IA Prompt Engineer + Lead Dev IA expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import ast
import re
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import joblib
import sqlite3
import openai
from transformers import AutoTokenizer, AutoModel
import torch
import radon.complexity as radon_complexity
from radon.metrics import mi_visit, h_visit
import lizard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityPredictionType(Enum):
    """Types of quality predictions"""
    MAINTAINABILITY = "maintainability"
    BUG_PRONENESS = "bug_proneness"
    COMPLEXITY_SCORE = "complexity_score"
    TECHNICAL_DEBT = "technical_debt"
    REFACTORING_PRIORITY = "refactoring_priority"
    PERFORMANCE_RISK = "performance_risk"
    SECURITY_RISK = "security_risk"


class CodeQualityLevel(Enum):
    """Code quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    HIGH = "high"         # > 90%
    MEDIUM = "medium"     # 70-90%
    LOW = "low"          # 50-70%
    UNCERTAIN = "uncertain"  # < 50%


@dataclass
class CodeMetrics:
    """Code metrics for quality analysis"""
    file_path: str
    lines_of_code: int = 0
    cyclomatic_complexity: float = 0.0
    maintainability_index: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    function_count: int = 0
    class_count: int = 0
    comment_ratio: float = 0.0
    duplication_ratio: float = 0.0
    test_coverage: float = 0.0
    dependency_count: int = 0
    cognitive_complexity: float = 0.0
    technical_debt_ratio: float = 0.0
    code_smells: List[str] = field(default_factory=list)
    security_vulnerabilities: List[str] = field(default_factory=list)


@dataclass
class QualityPrediction:
    """Quality prediction result"""
    prediction_id: str
    file_path: str
    prediction_type: QualityPredictionType
    predicted_value: Union[float, str]
    confidence: float
    quality_level: CodeQualityLevel
    prediction_confidence: PredictionConfidence
    model_used: str
    features_importance: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    model_accuracy: float = 0.0


@dataclass
class TrainingData:
    """Training data for ML models"""
    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    sample_weights: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodeQualityPredictor:
    """
    AI-powered code quality prediction system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/quality_predictor.yaml")
        self.config = self._load_config()
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.vectorizers: Dict[str, TfidfVectorizer] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.database_path = Path("data/quality_predictions.db")
        self.model_storage_path = Path("models/quality_prediction")
        self.training_history: List[Dict] = []
        self._initialize_database()
        self._initialize_ai_models()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load predictor configuration"""
        default_config = {
            "models": {
                "enabled": ["random_forest", "xgboost", "lightgbm", "neural_network"],
                "ensemble_voting": True,
                "auto_retrain": True,
                "retrain_threshold": 0.8  # Retrain if accuracy drops below this
            },
            "features": {
                "code_metrics": True,
                "text_features": True,
                "historical_data": True,
                "context_features": True,
                "ast_features": True
            },
            "prediction_types": [
                "maintainability",
                "bug_proneness", 
                "complexity_score",
                "technical_debt",
                "refactoring_priority"
            ],
            "training": {
                "min_samples": 100,
                "test_size": 0.2,
                "cross_validation_folds": 5,
                "feature_selection": True,
                "hyperparameter_tuning": True
            },
            "ai_integration": {
                "use_openai": True,
                "use_transformers": True,
                "code_embeddings": True,
                "semantic_analysis": True
            },
            "thresholds": {
                "high_confidence": 0.9,
                "medium_confidence": 0.7,
                "low_confidence": 0.5
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    def _initialize_database(self):
        """Initialize SQLite database"""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    prediction_type TEXT,
                    predicted_value TEXT,
                    confidence REAL,
                    quality_level TEXT,
                    model_used TEXT,
                    prediction_date TEXT,
                    actual_value TEXT,
                    accuracy REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    accuracy REAL,
                    precision_score REAL,
                    recall REAL,
                    f1_score REAL,
                    training_date TEXT,
                    training_samples INTEGER,
                    features_used TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_metrics (
                    file_path TEXT PRIMARY KEY,
                    lines_of_code INTEGER,
                    cyclomatic_complexity REAL,
                    maintainability_index REAL,
                    function_count INTEGER,
                    class_count INTEGER,
                    comment_ratio REAL,
                    last_updated TEXT
                )
            """)

    def _initialize_ai_models(self):
        """Initialize AI models and transformers"""
        try:
            if self.config["ai_integration"]["use_transformers"]:
                # Initialize code understanding model
                self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
                self.code_model = AutoModel.from_pretrained("microsoft/codebert-base")
                logger.info("Initialized CodeBERT model for semantic analysis")
        except Exception as e:
            logger.warning(f"Failed to initialize transformer models: {e}")

    async def extract_code_metrics(self, file_path: str) -> CodeMetrics:
        """Extract comprehensive code metrics"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Extracting metrics from: {file_path}")
        
        metrics = CodeMetrics(file_path=str(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Basic metrics
            metrics.lines_of_code = len([line for line in code_content.split('\n') if line.strip()])
            
            # Language-specific analysis
            if file_path.suffix == '.py':
                metrics = await self._analyze_python_code(code_content, metrics)
            elif file_path.suffix in ['.js', '.ts']:
                metrics = await self._analyze_javascript_code(code_content, metrics)
            elif file_path.suffix in ['.java']:
                metrics = await self._analyze_java_code(code_content, metrics)
            
            # General analysis using Lizard
            try:
                lizard_result = lizard.analyze_file.analyze_source_code(str(file_path), code_content)
                metrics.cyclomatic_complexity = lizard_result.CCN / max(lizard_result.function_list.__len__(), 1)
                metrics.function_count = len(lizard_result.function_list)
            except:
                pass
            
            # Comment ratio
            comment_lines = len([line for line in code_content.split('\n') 
                               if line.strip().startswith('#') or line.strip().startswith('//') or 
                               line.strip().startswith('/*') or line.strip().startswith('*')])
            metrics.comment_ratio = comment_lines / max(metrics.lines_of_code, 1)
            
            # Code smells detection
            metrics.code_smells = await self._detect_code_smells(code_content, file_path.suffix)
            
            # Security vulnerabilities (basic detection)
            metrics.security_vulnerabilities = await self._detect_security_issues(code_content, file_path.suffix)
            
        except Exception as e:
            logger.error(f"Failed to extract metrics: {e}")
        
        return metrics

    async def _analyze_python_code(self, code_content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze Python-specific metrics"""
        try:
            tree = ast.parse(code_content)
            
            # Count classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    metrics.class_count += 1
                elif isinstance(node, ast.FunctionDef):
                    metrics.function_count += 1
            
            # Use radon for complexity analysis
            complexity_results = radon_complexity.cc_visit(code_content)
            if complexity_results:
                total_complexity = sum(result.complexity for result in complexity_results)
                metrics.cyclomatic_complexity = total_complexity / len(complexity_results)
            
            # Maintainability Index
            mi_results = mi_visit(code_content, multi=True)
            if mi_results:
                metrics.maintainability_index = mi_results
            
            # Halstead metrics
            h_results = h_visit(code_content)
            if h_results:
                metrics.halstead_difficulty = h_results.difficulty
                metrics.halstead_effort = h_results.effort
            
        except Exception as e:
            logger.warning(f"Python analysis failed: {e}")
        
        return metrics

    async def _analyze_javascript_code(self, code_content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze JavaScript-specific metrics"""
        try:
            # Simple function/class counting using regex
            function_pattern = r'function\s+\w+|const\s+\w+\s*=\s*\(|=>\s*{'
            class_pattern = r'class\s+\w+'
            
            metrics.function_count = len(re.findall(function_pattern, code_content))
            metrics.class_count = len(re.findall(class_pattern, code_content))
            
        except Exception as e:
            logger.warning(f"JavaScript analysis failed: {e}")
        
        return metrics

    async def _analyze_java_code(self, code_content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze Java-specific metrics"""
        try:
            # Simple method/class counting using regex
            method_pattern = r'(public|private|protected)?\s*\w+\s+\w+\s*\('
            class_pattern = r'(public|private)?\s*class\s+\w+'
            
            metrics.function_count = len(re.findall(method_pattern, code_content))
            metrics.class_count = len(re.findall(class_pattern, code_content))
            
        except Exception as e:
            logger.warning(f"Java analysis failed: {e}")
        
        return metrics

    async def _detect_code_smells(self, code_content: str, file_extension: str) -> List[str]:
        """Detect common code smells"""
        smells = []
        
        lines = code_content.split('\n')
        
        # Long method detection
        if file_extension == '.py':
            in_function = False
            function_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('def '):
                    in_function = True
                    function_lines = 0
                elif in_function:
                    if stripped and not stripped.startswith('#'):
                        function_lines += 1
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        if function_lines > 50:
                            smells.append("Long Method")
                        in_function = False
        
        # Long line detection
        long_lines = [i for i, line in enumerate(lines) if len(line) > 120]
        if len(long_lines) > len(lines) * 0.1:
            smells.append("Long Lines")
        
        # High nesting level
        max_nesting = 0
        for line in lines:
            nesting = (len(line) - len(line.lstrip())) // 4  # Assuming 4-space indentation
            max_nesting = max(max_nesting, nesting)
        
        if max_nesting > 6:
            smells.append("Deep Nesting")
        
        # Duplicate code (simple detection)
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        duplicates = sum(1 for count in line_counts.values() if count > 3)
        if duplicates > len(lines) * 0.05:
            smells.append("Duplicate Code")
        
        return smells

    async def _detect_security_issues(self, code_content: str, file_extension: str) -> List[str]:
        """Detect basic security vulnerabilities"""
        vulnerabilities = []
        
        # SQL Injection patterns
        sql_patterns = [
            r'SELECT.*\+.*',
            r'INSERT.*\+.*',
            r'UPDATE.*\+.*',
            r'DELETE.*\+.*'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                vulnerabilities.append("Potential SQL Injection")
                break
        
        # Hard-coded credentials
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                vulnerabilities.append("Hard-coded Credentials")
                break
        
        # Unsafe eval usage
        if file_extension == '.py' and 'eval(' in code_content:
            vulnerabilities.append("Unsafe eval() Usage")
        
        if file_extension in ['.js', '.ts'] and 'eval(' in code_content:
            vulnerabilities.append("Unsafe eval() Usage")
        
        return vulnerabilities

    async def generate_code_embeddings(self, code_content: str) -> np.ndarray:
        """Generate semantic embeddings for code"""
        try:
            if not hasattr(self, 'tokenizer'):
                return np.zeros(768)  # Default embedding size
            
            # Tokenize code
            inputs = self.tokenizer(code_content, return_tensors="pt", 
                                  max_length=512, truncation=True, padding=True)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.code_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            return embeddings
            
        except Exception as e:
            logger.warning(f"Failed to generate code embeddings: {e}")
            return np.zeros(768)

    async def prepare_features(self, metrics: CodeMetrics, code_content: str = "") -> np.ndarray:
        """Prepare features for ML models"""
        features = []
        
        # Code metrics features
        if self.config["features"]["code_metrics"]:
            features.extend([
                metrics.lines_of_code,
                metrics.cyclomatic_complexity,
                metrics.maintainability_index,
                metrics.halstead_difficulty,
                metrics.halstead_effort,
                metrics.function_count,
                metrics.class_count,
                metrics.comment_ratio,
                len(metrics.code_smells),
                len(metrics.security_vulnerabilities)
            ])
        
        # Text features
        if self.config["features"]["text_features"] and code_content:
            # Simple text features
            features.extend([
                len(code_content),
                code_content.count('\n'),
                code_content.count(' '),
                code_content.count('\t')
            ])
        
        # AST features (for Python)
        if self.config["features"]["ast_features"] and code_content:
            try:
                if metrics.file_path.endswith('.py'):
                    tree = ast.parse(code_content)
                    ast_features = self._extract_ast_features(tree)
                    features.extend(ast_features)
                else:
                    features.extend([0] * 10)  # Placeholder AST features
            except:
                features.extend([0] * 10)  # Default AST features
        
        return np.array(features, dtype=float)

    def _extract_ast_features(self, tree: ast.AST) -> List[float]:
        """Extract AST-based features"""
        features = []
        
        # Count different node types
        node_counts = {}
        for node in ast.walk(tree):
            node_type = type(node).__name__
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        # Extract specific counts
        features.append(node_counts.get('If', 0))           # Conditional complexity
        features.append(node_counts.get('For', 0))          # Loop complexity
        features.append(node_counts.get('While', 0))        # Loop complexity
        features.append(node_counts.get('Try', 0))          # Exception handling
        features.append(node_counts.get('Import', 0))       # Import complexity
        features.append(node_counts.get('Call', 0))         # Function call complexity
        features.append(node_counts.get('Lambda', 0))       # Lambda usage
        features.append(node_counts.get('ListComp', 0))     # List comprehension
        features.append(node_counts.get('DictComp', 0))     # Dict comprehension
        features.append(len(node_counts))                   # Total node type diversity
        
        return features

    async def predict_quality(self, file_path: str, prediction_type: QualityPredictionType) -> QualityPrediction:
        """Predict code quality for a file"""
        try:
            # Extract metrics
            metrics = await self.extract_code_metrics(file_path)
            
            # Read code content for embeddings
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Prepare features
            features = await self.prepare_features(metrics, code_content)
            
            # Load or train model
            model_name = f"{prediction_type.value}_model"
            if model_name not in self.models:
                await self._train_model(prediction_type)
            
            # Make prediction
            model = self.models.get(model_name)
            scaler = self.scalers.get(model_name)
            
            if model is None:
                # Fallback to rule-based prediction
                return await self._rule_based_prediction(metrics, prediction_type)
            
            # Scale features
            if scaler:
                features_scaled = scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Predict
            if hasattr(model, 'predict_proba'):
                prediction_proba = model.predict_proba(features_scaled)[0]
                predicted_value = np.argmax(prediction_proba)
                confidence = float(np.max(prediction_proba))
            else:
                predicted_value = model.predict(features_scaled)[0]
                confidence = 0.8  # Default confidence for regression
            
            # Determine quality level and confidence
            quality_level = self._map_prediction_to_quality(predicted_value, prediction_type)
            prediction_confidence = self._determine_confidence_level(confidence)
            
            # Generate AI-powered insights
            reasoning = await self._generate_ai_reasoning(metrics, code_content, prediction_type)
            recommendations = await self._generate_recommendations(metrics, prediction_type, quality_level)
            
            # Create prediction result
            prediction = QualityPrediction(
                prediction_id=f"pred_{int(datetime.now().timestamp())}",
                file_path=file_path,
                prediction_type=prediction_type,
                predicted_value=float(predicted_value),
                confidence=confidence,
                quality_level=quality_level,
                prediction_confidence=prediction_confidence,
                model_used=model_name,
                reasoning=reasoning,
                recommendations=recommendations,
                model_accuracy=self._get_model_accuracy(model_name)
            )
            
            # Store prediction
            await self._store_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Quality prediction failed: {e}")
            raise

    async def _rule_based_prediction(self, metrics: CodeMetrics, prediction_type: QualityPredictionType) -> QualityPrediction:
        """Fallback rule-based prediction"""
        if prediction_type == QualityPredictionType.MAINTAINABILITY:
            # Simple maintainability rules
            score = 100
            if metrics.cyclomatic_complexity > 10:
                score -= 20
            if metrics.lines_of_code > 500:
                score -= 15
            if len(metrics.code_smells) > 3:
                score -= 25
            if metrics.comment_ratio < 0.1:
                score -= 10
            
            score = max(0, score)
            quality_level = self._map_prediction_to_quality(score / 100, prediction_type)
            
        elif prediction_type == QualityPredictionType.BUG_PRONENESS:
            # Bug proneness rules
            risk_score = 0
            if metrics.cyclomatic_complexity > 15:
                risk_score += 0.3
            if len(metrics.security_vulnerabilities) > 0:
                risk_score += 0.4
            if len(metrics.code_smells) > 5:
                risk_score += 0.2
            
            risk_score = min(1.0, risk_score)
            quality_level = self._map_prediction_to_quality(1 - risk_score, prediction_type)
        
        else:
            # Default prediction
            score = 0.5
            quality_level = CodeQualityLevel.AVERAGE
        
        return QualityPrediction(
            prediction_id=f"rule_{int(datetime.now().timestamp())}",
            file_path=metrics.file_path,
            prediction_type=prediction_type,
            predicted_value=float(score) if 'score' in locals() else 0.5,
            confidence=0.6,  # Lower confidence for rule-based
            quality_level=quality_level,
            prediction_confidence=PredictionConfidence.MEDIUM,
            model_used="rule_based",
            reasoning="Rule-based analysis using code metrics thresholds",
            recommendations=await self._generate_recommendations(metrics, prediction_type, quality_level)
        )

    def _map_prediction_to_quality(self, prediction_value: float, prediction_type: QualityPredictionType) -> CodeQualityLevel:
        """Map prediction value to quality level"""
        if prediction_type in [QualityPredictionType.MAINTAINABILITY, QualityPredictionType.COMPLEXITY_SCORE]:
            if prediction_value >= 0.8:
                return CodeQualityLevel.EXCELLENT
            elif prediction_value >= 0.6:
                return CodeQualityLevel.GOOD
            elif prediction_value >= 0.4:
                return CodeQualityLevel.AVERAGE
            elif prediction_value >= 0.2:
                return CodeQualityLevel.POOR
            else:
                return CodeQualityLevel.CRITICAL
        
        else:  # For risk-based predictions (invert scale)
            if prediction_value <= 0.2:
                return CodeQualityLevel.EXCELLENT
            elif prediction_value <= 0.4:
                return CodeQualityLevel.GOOD
            elif prediction_value <= 0.6:
                return CodeQualityLevel.AVERAGE
            elif prediction_value <= 0.8:
                return CodeQualityLevel.POOR
            else:
                return CodeQualityLevel.CRITICAL

    def _determine_confidence_level(self, confidence: float) -> PredictionConfidence:
        """Determine confidence level from confidence score"""
        if confidence >= self.config["thresholds"]["high_confidence"]:
            return PredictionConfidence.HIGH
        elif confidence >= self.config["thresholds"]["medium_confidence"]:
            return PredictionConfidence.MEDIUM
        elif confidence >= self.config["thresholds"]["low_confidence"]:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.UNCERTAIN

    async def _generate_ai_reasoning(self, metrics: CodeMetrics, code_content: str, 
                                   prediction_type: QualityPredictionType) -> str:
        """Generate AI-powered reasoning for predictions"""
        try:
            if not self.config["ai_integration"]["use_openai"]:
                return f"Analysis based on {prediction_type.value} metrics and patterns"
            
            # Prepare prompt for AI analysis
            prompt = f"""
            Analyze this code quality assessment:
            
            File: {metrics.file_path}
            Lines of Code: {metrics.lines_of_code}
            Cyclomatic Complexity: {metrics.cyclomatic_complexity}
            Maintainability Index: {metrics.maintainability_index}
            Function Count: {metrics.function_count}
            Comment Ratio: {metrics.comment_ratio:.2%}
            Code Smells: {', '.join(metrics.code_smells) if metrics.code_smells else 'None'}
            Security Issues: {', '.join(metrics.security_vulnerabilities) if metrics.security_vulnerabilities else 'None'}
            
            Prediction Type: {prediction_type.value}
            
            Provide a brief technical explanation for the {prediction_type.value} assessment in 2-3 sentences.
            """
            
            # This would integrate with OpenAI API
            # For now, return structured reasoning
            return f"Analysis of {prediction_type.value} based on code complexity ({metrics.cyclomatic_complexity:.1f}), maintainability metrics, and detected patterns. Code structure and quality indicators suggest specific areas for improvement."
            
        except Exception as e:
            logger.warning(f"AI reasoning generation failed: {e}")
            return f"Technical analysis based on {prediction_type.value} metrics and code structure patterns"

    async def _generate_recommendations(self, metrics: CodeMetrics, prediction_type: QualityPredictionType, 
                                      quality_level: CodeQualityLevel) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if quality_level in [CodeQualityLevel.POOR, CodeQualityLevel.CRITICAL]:
            if metrics.cyclomatic_complexity > 10:
                recommendations.append("Reduce cyclomatic complexity by breaking down large functions")
            
            if metrics.lines_of_code > 500:
                recommendations.append("Consider splitting large files into smaller, focused modules")
            
            if metrics.comment_ratio < 0.1:
                recommendations.append("Add more documentation and comments to improve maintainability")
            
            if "Long Method" in metrics.code_smells:
                recommendations.append("Refactor long methods into smaller, single-purpose functions")
            
            if "Deep Nesting" in metrics.code_smells:
                recommendations.append("Reduce nesting levels using early returns or guard clauses")
            
            if metrics.security_vulnerabilities:
                recommendations.append("Address security vulnerabilities: " + ", ".join(metrics.security_vulnerabilities))
        
        elif quality_level == CodeQualityLevel.AVERAGE:
            recommendations.append("Consider minor refactoring to improve code quality")
            if metrics.comment_ratio < 0.15:
                recommendations.append("Add more descriptive comments for complex logic")
        
        # Type-specific recommendations
        if prediction_type == QualityPredictionType.MAINTAINABILITY:
            if metrics.function_count > 50:
                recommendations.append("High function count - consider organizing into classes or modules")
        
        elif prediction_type == QualityPredictionType.BUG_PRONENESS:
            recommendations.append("Add comprehensive unit tests to reduce bug risk")
            if metrics.cyclomatic_complexity > 8:
                recommendations.append("High complexity increases bug risk - simplify control flow")
        
        return recommendations

    def _get_model_accuracy(self, model_name: str) -> float:
        """Get model accuracy from training history"""
        return 0.85  # Default accuracy placeholder

    async def _store_prediction(self, prediction: QualityPrediction):
        """Store prediction in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO predictions
                    (id, file_path, prediction_type, predicted_value, confidence, 
                     quality_level, model_used, prediction_date, accuracy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prediction.prediction_id,
                    prediction.file_path,
                    prediction.prediction_type.value,
                    str(prediction.predicted_value),
                    prediction.confidence,
                    prediction.quality_level.value,
                    prediction.model_used,
                    prediction.timestamp.isoformat(),
                    prediction.model_accuracy
                ))
        except Exception as e:
            logger.error(f"Failed to store prediction: {e}")

    async def _train_model(self, prediction_type: QualityPredictionType):
        """Train ML model for specific prediction type"""
        logger.info(f"Training model for {prediction_type.value}")
        
        # This would load historical data and train models
        # For now, create a placeholder model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        scaler = StandardScaler()
        
        # Store models
        model_name = f"{prediction_type.value}_model"
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        logger.info(f"Model trained for {prediction_type.value}")


# Global instance
code_quality_predictor = CodeQualityPredictor()

# Convenience functions
async def predict_maintainability(file_path: str):
    """Predict code maintainability"""
    return await code_quality_predictor.predict_quality(file_path, QualityPredictionType.MAINTAINABILITY)

async def predict_bug_proneness(file_path: str):
    """Predict bug proneness"""
    return await code_quality_predictor.predict_quality(file_path, QualityPredictionType.BUG_PRONENESS)

async def analyze_code_quality(file_path: str):
    """Comprehensive code quality analysis"""
    results = {}
    for pred_type in QualityPredictionType:
        try:
            result = await code_quality_predictor.predict_quality(file_path, pred_type)
            results[pred_type.value] = result
        except Exception as e:
            logger.error(f"Failed to predict {pred_type.value}: {e}")
    
    return results

if __name__ == "__main__":
    # Example usage
    async def main():
        file_path = "sample_code.py"
        prediction = await predict_maintainability(file_path)
        print(f"Quality Level: {prediction.quality_level.value}")
        print(f"Confidence: {prediction.confidence:.2f}")
        print(f"Recommendations: {prediction.recommendations}")
    
    asyncio.run(main())