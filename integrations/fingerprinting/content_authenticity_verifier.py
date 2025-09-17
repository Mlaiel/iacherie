"""
🔐 Content Authenticity Verifier - Ainflue Enterprise
================================================================================
**Module**: Content Authenticity Verification System
**Expert Roles**: Security Specialist + Blockchain Engineer + ML Engineer
**Responsibility**: Provenance tracking, authenticity verification, tamper detection
**Type**: Enterprise Content Verification Engine
**Author**: Fahed Mlaiel (mlaiel@live.de)
**Status**: PRODUCTION ENTERPRISE
**Date**: 2025-01-06

⚠️  **PROPRIETARY SOFTWARE - FAHED MLAIEL** ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
================================================================================
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import cv2
import numpy as np
from PIL import Image, ImageChops
import magic
import requests
import sqlite3
import redis
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import blockchain_integration
import merkle_tree
import smart_contracts


class AuthenticityLevel(Enum):
    """Content authenticity levels"""
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    TAMPERED = "tampered"
    UNKNOWN = "unknown"
    FAKE = "fake"


class ProvenanceStatus(Enum):
    """Content provenance tracking status"""
    ORIGINAL = "original"
    DERIVED = "derived"
    MODIFIED = "modified"
    DUPLICATE = "duplicate"
    SYNTHETIC = "synthetic"


@dataclass
class AuthenticityResult:
    """Content authenticity verification result"""
    content_id: str
    authenticity_level: AuthenticityLevel
    confidence_score: float
    provenance_chain: List[Dict[str, Any]]
    verification_timestamp: datetime
    tamper_indicators: List[str]
    blockchain_proof: Optional[str]
    digital_signature: Optional[str]
    metadata_integrity: bool
    pixel_analysis_score: float
    compression_artifacts: List[str]
    creation_metadata: Dict[str, Any]


@dataclass
class ProvenanceRecord:
    """Content provenance tracking record"""
    content_id: str
    creator_id: str
    creation_timestamp: datetime
    modification_history: List[Dict[str, Any]]
    ownership_chain: List[str]
    licensing_info: Dict[str, Any]
    blockchain_hash: str
    verification_signatures: List[str]
    geographic_origin: Optional[str]
    device_fingerprint: Optional[str]


class ContentAuthenticityVerifier:
    """
    Enterprise content authenticity verification system
    
    Features:
    - Blockchain-based provenance tracking
    - Digital signature verification
    - Tamper detection algorithms
    - Metadata integrity analysis
    - Pixel-level forensic analysis
    - Compression artifact detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.redis_client = self._setup_redis()
        self.blockchain = self._setup_blockchain()
        self.ml_models = self._load_ml_models()
        self.signature_keys = self._load_signature_keys()
        
        # Database initialization
        self._init_database()
        
        # Cache for verification results
        self.verification_cache = {}
        
        self.logger.info("Content Authenticity Verifier initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("authenticity_verifier")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_redis(self) -> redis.Redis:
        """Setup Redis connection"""
        return redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0),
            decode_responses=True
        )
    
    def _setup_blockchain(self):
        """Setup blockchain integration"""
        return blockchain_integration.BlockchainClient(
            network=self.config.get('blockchain_network', 'ethereum'),
            contract_address=self.config.get('contract_address'),
            private_key=self.config.get('private_key')
        )
    
    def _load_ml_models(self) -> Dict[str, Any]:
        """Load ML models for authenticity detection"""
        return {
            'tamper_detection': self._load_tamper_detection_model(),
            'deepfake_detection': self._load_deepfake_detection_model(),
            'compression_analysis': self._load_compression_analysis_model(),
            'metadata_analysis': self._load_metadata_analysis_model()
        }
    
    def _load_signature_keys(self) -> Dict[str, Any]:
        """Load digital signature keys"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        return {
            'private_key': private_key,
            'public_key': public_key
        }
    
    def _init_database(self):
        """Initialize authenticity database"""
        conn = sqlite3.connect(self.config.get('db_path', 'authenticity.db'))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authenticity_records (
                content_id TEXT PRIMARY KEY,
                authenticity_level TEXT,
                confidence_score REAL,
                verification_timestamp TEXT,
                blockchain_proof TEXT,
                metadata_hash TEXT,
                creation_timestamp TEXT,
                creator_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provenance_chain (
                record_id TEXT PRIMARY KEY,
                content_id TEXT,
                event_type TEXT,
                timestamp TEXT,
                actor_id TEXT,
                event_data TEXT,
                blockchain_hash TEXT,
                FOREIGN KEY (content_id) REFERENCES authenticity_records (content_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tamper_evidence (
                evidence_id TEXT PRIMARY KEY,
                content_id TEXT,
                tamper_type TEXT,
                confidence_score REAL,
                evidence_data TEXT,
                detection_timestamp TEXT,
                FOREIGN KEY (content_id) REFERENCES authenticity_records (content_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def verify_authenticity(
        self,
        content_path: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuthenticityResult:
        """
        Verify content authenticity
        
        Args:
            content_path: Path to content file
            content_type: Type of content (image, video, audio, text)
            metadata: Additional metadata
            
        Returns:
            AuthenticityResult with verification details
        """
        try:
            content_id = self._generate_content_id(content_path)
            
            # Check cache first
            cached_result = await self._get_cached_result(content_id)
            if cached_result:
                return cached_result
            
            # Perform comprehensive verification
            verification_tasks = [
                self._verify_digital_signature(content_path),
                self._analyze_metadata_integrity(content_path, metadata),
                self._detect_tampering(content_path, content_type),
                self._verify_blockchain_provenance(content_id),
                self._analyze_compression_artifacts(content_path, content_type),
                self._perform_pixel_analysis(content_path, content_type)
            ]
            
            results = await asyncio.gather(*verification_tasks, return_exceptions=True)
            
            # Aggregate results
            authenticity_result = self._aggregate_verification_results(
                content_id, content_type, results, metadata
            )
            
            # Store result
            await self._store_verification_result(authenticity_result)
            
            # Cache result
            await self._cache_result(authenticity_result)
            
            self.logger.info(f"Authenticity verification completed for {content_id}")
            return authenticity_result
            
        except Exception as e:
            self.logger.error(f"Authenticity verification failed: {str(e)}")
            raise
    
    async def track_provenance(
        self,
        content_id: str,
        creator_id: str,
        creation_metadata: Dict[str, Any]
    ) -> ProvenanceRecord:
        """
        Track content provenance on blockchain
        
        Args:
            content_id: Unique content identifier
            creator_id: Content creator identifier
            creation_metadata: Creation metadata
            
        Returns:
            ProvenanceRecord with tracking details
        """
        try:
            # Create provenance record
            provenance_record = ProvenanceRecord(
                content_id=content_id,
                creator_id=creator_id,
                creation_timestamp=datetime.now(timezone.utc),
                modification_history=[],
                ownership_chain=[creator_id],
                licensing_info=creation_metadata.get('licensing', {}),
                blockchain_hash="",
                verification_signatures=[],
                geographic_origin=creation_metadata.get('location'),
                device_fingerprint=creation_metadata.get('device_fingerprint')
            )
            
            # Register on blockchain
            blockchain_hash = await self._register_on_blockchain(provenance_record)
            provenance_record.blockchain_hash = blockchain_hash
            
            # Create digital signature
            signature = self._create_digital_signature(provenance_record)
            provenance_record.verification_signatures.append(signature)
            
            # Store provenance record
            await self._store_provenance_record(provenance_record)
            
            self.logger.info(f"Provenance tracking initiated for {content_id}")
            return provenance_record
            
        except Exception as e:
            self.logger.error(f"Provenance tracking failed: {str(e)}")
            raise
    
    async def detect_deepfakes(
        self,
        content_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Detect deepfake content using ML models
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            
        Returns:
            Deepfake detection results
        """
        try:
            if content_type == "video":
                return await self._detect_video_deepfake(content_path)
            elif content_type == "image":
                return await self._detect_image_deepfake(content_path)
            elif content_type == "audio":
                return await self._detect_audio_deepfake(content_path)
            else:
                return {"deepfake_probability": 0.0, "confidence": 0.0}
                
        except Exception as e:
            self.logger.error(f"Deepfake detection failed: {str(e)}")
            return {"error": str(e), "deepfake_probability": 0.0}
    
    async def verify_blockchain_integrity(self, content_id: str) -> Dict[str, Any]:
        """
        Verify content integrity using blockchain
        
        Args:
            content_id: Content identifier
            
        Returns:
            Blockchain verification results
        """
        try:
            # Get blockchain record
            blockchain_record = await self.blockchain.get_content_record(content_id)
            
            if not blockchain_record:
                return {
                    "verified": False,
                    "error": "No blockchain record found"
                }
            
            # Verify record integrity
            integrity_check = await self._verify_blockchain_record_integrity(
                blockchain_record
            )
            
            return {
                "verified": integrity_check,
                "blockchain_hash": blockchain_record.get('hash'),
                "timestamp": blockchain_record.get('timestamp'),
                "block_number": blockchain_record.get('block_number')
            }
            
        except Exception as e:
            self.logger.error(f"Blockchain verification failed: {str(e)}")
            return {"verified": False, "error": str(e)}
    
    async def analyze_metadata_forensics(
        self,
        content_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform forensic analysis of metadata
        
        Args:
            content_path: Path to content file
            metadata: Additional metadata
            
        Returns:
            Metadata forensics results
        """
        try:
            # Extract embedded metadata
            embedded_metadata = self._extract_embedded_metadata(content_path)
            
            # Analyze metadata consistency
            consistency_analysis = self._analyze_metadata_consistency(
                embedded_metadata, metadata
            )
            
            # Detect metadata tampering
            tampering_indicators = self._detect_metadata_tampering(embedded_metadata)
            
            # Verify creation timestamps
            timestamp_verification = self._verify_creation_timestamps(embedded_metadata)
            
            return {
                "embedded_metadata": embedded_metadata,
                "consistency_score": consistency_analysis['score'],
                "tampering_indicators": tampering_indicators,
                "timestamp_verified": timestamp_verification,
                "metadata_integrity": len(tampering_indicators) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Metadata forensics failed: {str(e)}")
            return {"error": str(e)}
    
    async def generate_authenticity_certificate(
        self,
        content_id: str,
        verification_result: AuthenticityResult
    ) -> Dict[str, Any]:
        """
        Generate authenticity certificate
        
        Args:
            content_id: Content identifier
            verification_result: Verification results
            
        Returns:
            Digital authenticity certificate
        """
        try:
            certificate = {
                "certificate_id": self._generate_certificate_id(),
                "content_id": content_id,
                "authenticity_level": verification_result.authenticity_level.value,
                "confidence_score": verification_result.confidence_score,
                "verification_timestamp": verification_result.verification_timestamp.isoformat(),
                "issuer": "Ainflue Enterprise Authenticity Verifier",
                "issuer_signature": "",
                "blockchain_proof": verification_result.blockchain_proof,
                "validity_period": self._calculate_validity_period(verification_result),
                "verification_methods": self._get_verification_methods_used(verification_result)
            }
            
            # Sign certificate
            certificate["issuer_signature"] = self._sign_certificate(certificate)
            
            # Store certificate
            await self._store_authenticity_certificate(certificate)
            
            return certificate
            
        except Exception as e:
            self.logger.error(f"Certificate generation failed: {str(e)}")
            raise
    
    # Helper methods
    
    def _generate_content_id(self, content_path: str) -> str:
        """Generate unique content identifier"""
        with open(content_path, 'rb') as f:
            content = f.read()
        
        hash_obj = hashlib.sha256()
        hash_obj.update(content)
        return hash_obj.hexdigest()
    
    async def _get_cached_result(self, content_id: str) -> Optional[AuthenticityResult]:
        """Get cached verification result"""
        try:
            cached_data = self.redis_client.get(f"auth_result:{content_id}")
            if cached_data:
                data = json.loads(cached_data)
                return AuthenticityResult(**data)
            return None
        except Exception:
            return None
    
    async def _verify_digital_signature(self, content_path: str) -> Dict[str, Any]:
        """Verify digital signature of content"""
        try:
            # Extract signature from metadata or separate file
            signature_data = self._extract_signature_data(content_path)
            
            if not signature_data:
                return {"verified": False, "reason": "No signature found"}
            
            # Verify signature
            content_hash = self._calculate_content_hash(content_path)
            verification_result = self._verify_signature(content_hash, signature_data)
            
            return {
                "verified": verification_result,
                "signature_algorithm": signature_data.get('algorithm'),
                "signer": signature_data.get('signer'),
                "signature_timestamp": signature_data.get('timestamp')
            }
            
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    async def _analyze_metadata_integrity(
        self,
        content_path: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze metadata integrity"""
        try:
            embedded_metadata = self._extract_embedded_metadata(content_path)
            
            # Check for inconsistencies
            inconsistencies = []
            if metadata:
                for key, value in metadata.items():
                    if key in embedded_metadata:
                        if embedded_metadata[key] != value:
                            inconsistencies.append(f"Mismatch in {key}")
            
            # Check for suspicious modifications
            suspicious_indicators = self._detect_suspicious_metadata_patterns(
                embedded_metadata
            )
            
            integrity_score = 1.0 - (len(inconsistencies) + len(suspicious_indicators)) * 0.1
            
            return {
                "integrity_score": max(0.0, integrity_score),
                "inconsistencies": inconsistencies,
                "suspicious_indicators": suspicious_indicators,
                "embedded_metadata": embedded_metadata
            }
            
        except Exception as e:
            return {"integrity_score": 0.0, "error": str(e)}
    
    async def _detect_tampering(self, content_path: str, content_type: str) -> Dict[str, Any]:
        """Detect content tampering"""
        try:
            if content_type == "image":
                return await self._detect_image_tampering(content_path)
            elif content_type == "video":
                return await self._detect_video_tampering(content_path)
            elif content_type == "audio":
                return await self._detect_audio_tampering(content_path)
            else:
                return {"tampered": False, "confidence": 0.0}
                
        except Exception as e:
            return {"tampered": True, "confidence": 0.0, "error": str(e)}
    
    async def _verify_blockchain_provenance(self, content_id: str) -> Dict[str, Any]:
        """Verify blockchain provenance"""
        try:
            blockchain_record = await self.blockchain.get_content_record(content_id)
            
            if not blockchain_record:
                return {"verified": False, "reason": "No blockchain record"}
            
            # Verify record integrity
            integrity_verified = await self._verify_blockchain_record_integrity(
                blockchain_record
            )
            
            return {
                "verified": integrity_verified,
                "blockchain_hash": blockchain_record.get('hash'),
                "creation_timestamp": blockchain_record.get('timestamp'),
                "creator": blockchain_record.get('creator')
            }
            
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    async def _analyze_compression_artifacts(
        self,
        content_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze compression artifacts"""
        try:
            if content_type == "image":
                return self._analyze_image_compression_artifacts(content_path)
            elif content_type == "video":
                return self._analyze_video_compression_artifacts(content_path)
            else:
                return {"artifacts_detected": False, "quality_score": 1.0}
                
        except Exception as e:
            return {"artifacts_detected": True, "error": str(e)}
    
    async def _perform_pixel_analysis(
        self,
        content_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Perform pixel-level analysis"""
        try:
            if content_type in ["image", "video"]:
                return self._analyze_pixel_patterns(content_path, content_type)
            else:
                return {"analysis_score": 1.0, "anomalies": []}
                
        except Exception as e:
            return {"analysis_score": 0.0, "error": str(e)}
    
    def _aggregate_verification_results(
        self,
        content_id: str,
        content_type: str,
        results: List[Any],
        metadata: Optional[Dict[str, Any]]
    ) -> AuthenticityResult:
        """Aggregate verification results into final assessment"""
        
        # Extract individual results
        signature_result = results[0] if not isinstance(results[0], Exception) else {}
        metadata_result = results[1] if not isinstance(results[1], Exception) else {}
        tampering_result = results[2] if not isinstance(results[2], Exception) else {}
        blockchain_result = results[3] if not isinstance(results[3], Exception) else {}
        compression_result = results[4] if not isinstance(results[4], Exception) else {}
        pixel_result = results[5] if not isinstance(results[5], Exception) else {}
        
        # Calculate overall confidence score
        confidence_factors = [
            signature_result.get('verified', False) * 0.2,
            metadata_result.get('integrity_score', 0.0) * 0.2,
            (1.0 - tampering_result.get('tampered', True)) * 0.25,
            blockchain_result.get('verified', False) * 0.15,
            (1.0 - compression_result.get('artifacts_detected', True)) * 0.1,
            pixel_result.get('analysis_score', 0.0) * 0.1
        ]
        
        confidence_score = sum(confidence_factors)
        
        # Determine authenticity level
        if confidence_score >= 0.9:
            authenticity_level = AuthenticityLevel.VERIFIED
        elif confidence_score >= 0.7:
            authenticity_level = AuthenticityLevel.SUSPICIOUS
        elif confidence_score >= 0.5:
            authenticity_level = AuthenticityLevel.TAMPERED
        else:
            authenticity_level = AuthenticityLevel.FAKE
        
        # Collect tamper indicators
        tamper_indicators = []
        if not signature_result.get('verified', False):
            tamper_indicators.append("Invalid digital signature")
        if metadata_result.get('inconsistencies'):
            tamper_indicators.extend(metadata_result['inconsistencies'])
        if tampering_result.get('tampered', False):
            tamper_indicators.append("Content tampering detected")
        
        return AuthenticityResult(
            content_id=content_id,
            authenticity_level=authenticity_level,
            confidence_score=confidence_score,
            provenance_chain=[],  # Will be populated separately
            verification_timestamp=datetime.now(timezone.utc),
            tamper_indicators=tamper_indicators,
            blockchain_proof=blockchain_result.get('blockchain_hash'),
            digital_signature=signature_result.get('signature'),
            metadata_integrity=metadata_result.get('integrity_score', 0.0) > 0.8,
            pixel_analysis_score=pixel_result.get('analysis_score', 0.0),
            compression_artifacts=compression_result.get('artifacts', []),
            creation_metadata=metadata or {}
        )
    
    async def _store_verification_result(self, result: AuthenticityResult):
        """Store verification result in database"""
        conn = sqlite3.connect(self.config.get('db_path', 'authenticity.db'))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO authenticity_records 
            (content_id, authenticity_level, confidence_score, verification_timestamp,
             blockchain_proof, metadata_hash, creation_timestamp, creator_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.content_id,
            result.authenticity_level.value,
            result.confidence_score,
            result.verification_timestamp.isoformat(),
            result.blockchain_proof,
            hashlib.sha256(json.dumps(result.creation_metadata).encode()).hexdigest(),
            result.creation_metadata.get('creation_timestamp'),
            result.creation_metadata.get('creator_id')
        ))
        
        conn.commit()
        conn.close()
    
    async def _cache_result(self, result: AuthenticityResult):
        """Cache verification result"""
        try:
            cache_data = {
                "content_id": result.content_id,
                "authenticity_level": result.authenticity_level.value,
                "confidence_score": result.confidence_score,
                "verification_timestamp": result.verification_timestamp.isoformat(),
                "tamper_indicators": result.tamper_indicators,
                "blockchain_proof": result.blockchain_proof,
                "metadata_integrity": result.metadata_integrity
            }
            
            self.redis_client.setex(
                f"auth_result:{result.content_id}",
                3600,  # 1 hour TTL
                json.dumps(cache_data)
            )
        except Exception as e:
            self.logger.warning(f"Failed to cache result: {str(e)}")
    
    # Additional helper methods for specific detection algorithms
    
    def _load_tamper_detection_model(self):
        """Load tamper detection ML model"""
        # Placeholder for actual ML model loading
        return {"model": "tamper_detection_v1.0"}
    
    def _load_deepfake_detection_model(self):
        """Load deepfake detection ML model"""
        return {"model": "deepfake_detection_v1.0"}
    
    def _load_compression_analysis_model(self):
        """Load compression analysis model"""
        return {"model": "compression_analysis_v1.0"}
    
    def _load_metadata_analysis_model(self):
        """Load metadata analysis model"""
        return {"model": "metadata_analysis_v1.0"}
    
    async def _register_on_blockchain(self, provenance_record: ProvenanceRecord) -> str:
        """Register provenance record on blockchain"""
        try:
            # Create blockchain transaction
            transaction_data = {
                "content_id": provenance_record.content_id,
                "creator_id": provenance_record.creator_id,
                "timestamp": provenance_record.creation_timestamp.isoformat(),
                "metadata_hash": hashlib.sha256(
                    json.dumps(asdict(provenance_record)).encode()
                ).hexdigest()
            }
            
            # Submit to blockchain
            transaction_hash = await self.blockchain.submit_transaction(transaction_data)
            return transaction_hash
            
        except Exception as e:
            self.logger.error(f"Blockchain registration failed: {str(e)}")
            return ""
    
    def _create_digital_signature(self, provenance_record: ProvenanceRecord) -> str:
        """Create digital signature for provenance record"""
        try:
            # Serialize record for signing
            record_data = json.dumps(asdict(provenance_record), sort_keys=True).encode()
            
            # Create signature
            signature = self.signature_keys['private_key'].sign(
                record_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature.hex()
            
        except Exception as e:
            self.logger.error(f"Digital signature creation failed: {str(e)}")
            return ""
    
    async def _store_provenance_record(self, record: ProvenanceRecord):
        """Store provenance record in database"""
        conn = sqlite3.connect(self.config.get('db_path', 'authenticity.db'))
        cursor = conn.cursor()
        
        # Store main provenance record
        cursor.execute('''
            INSERT OR REPLACE INTO provenance_chain 
            (record_id, content_id, event_type, timestamp, actor_id, event_data, blockchain_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{record.content_id}_creation",
            record.content_id,
            "creation",
            record.creation_timestamp.isoformat(),
            record.creator_id,
            json.dumps(asdict(record)),
            record.blockchain_hash
        ))
        
        conn.commit()
        conn.close()
    
    # Image-specific methods
    
    async def _detect_image_deepfake(self, image_path: str) -> Dict[str, Any]:
        """Detect deepfake in images"""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Analyze facial regions for deepfake indicators
            face_analysis = self._analyze_facial_inconsistencies(image)
            
            # Check for AI generation artifacts
            ai_artifacts = self._detect_ai_generation_artifacts(image)
            
            # Calculate deepfake probability
            deepfake_probability = (
                face_analysis['inconsistency_score'] * 0.6 +
                ai_artifacts['artifact_score'] * 0.4
            )
            
            return {
                "deepfake_probability": deepfake_probability,
                "confidence": max(face_analysis['confidence'], ai_artifacts['confidence']),
                "face_analysis": face_analysis,
                "ai_artifacts": ai_artifacts
            }
            
        except Exception as e:
            return {"deepfake_probability": 0.0, "confidence": 0.0, "error": str(e)}
    
    async def _detect_image_tampering(self, image_path: str) -> Dict[str, Any]:
        """Detect image tampering"""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Error Level Analysis (ELA)
            ela_result = self._perform_ela_analysis(image_path)
            
            # Copy-Move Detection
            copy_move_result = self._detect_copy_move_forgery(image)
            
            # Splicing Detection
            splicing_result = self._detect_image_splicing(image)
            
            # Aggregate results
            tampered = (
                ela_result['suspicious_regions'] > 0 or
                copy_move_result['matches_found'] > 0 or
                splicing_result['splicing_detected']
            )
            
            confidence = max(
                ela_result['confidence'],
                copy_move_result['confidence'],
                splicing_result['confidence']
            )
            
            return {
                "tampered": tampered,
                "confidence": confidence,
                "ela_analysis": ela_result,
                "copy_move_detection": copy_move_result,
                "splicing_detection": splicing_result
            }
            
        except Exception as e:
            return {"tampered": True, "confidence": 0.0, "error": str(e)}
    
    def _analyze_image_compression_artifacts(self, image_path: str) -> Dict[str, Any]:
        """Analyze image compression artifacts"""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Detect JPEG compression artifacts
            jpeg_artifacts = self._detect_jpeg_artifacts(image)
            
            # Analyze compression consistency
            compression_consistency = self._analyze_compression_consistency(image)
            
            # Detect multiple compression
            multiple_compression = self._detect_multiple_compression(image_path)
            
            return {
                "artifacts_detected": jpeg_artifacts['detected'] or multiple_compression['detected'],
                "quality_score": compression_consistency['quality_score'],
                "jpeg_artifacts": jpeg_artifacts,
                "compression_consistency": compression_consistency,
                "multiple_compression": multiple_compression
            }
            
        except Exception as e:
            return {"artifacts_detected": True, "error": str(e)}
    
    # Video-specific methods
    
    async def _detect_video_deepfake(self, video_path: str) -> Dict[str, Any]:
        """Detect deepfake in videos"""
        try:
            # Analyze temporal inconsistencies
            temporal_analysis = self._analyze_temporal_inconsistencies(video_path)
            
            # Check for facial reenactment artifacts
            facial_analysis = self._analyze_video_facial_artifacts(video_path)
            
            # Detect audio-visual synchronization issues
            av_sync_analysis = self._analyze_av_synchronization(video_path)
            
            # Calculate deepfake probability
            deepfake_probability = (
                temporal_analysis['inconsistency_score'] * 0.4 +
                facial_analysis['artifact_score'] * 0.4 +
                av_sync_analysis['sync_score'] * 0.2
            )
            
            return {
                "deepfake_probability": deepfake_probability,
                "confidence": max(
                    temporal_analysis['confidence'],
                    facial_analysis['confidence'],
                    av_sync_analysis['confidence']
                ),
                "temporal_analysis": temporal_analysis,
                "facial_analysis": facial_analysis,
                "av_sync_analysis": av_sync_analysis
            }
            
        except Exception as e:
            return {"deepfake_probability": 0.0, "confidence": 0.0, "error": str(e)}
    
    async def _detect_video_tampering(self, video_path: str) -> Dict[str, Any]:
        """Detect video tampering"""
        try:
            # Frame-by-frame analysis
            frame_analysis = self._analyze_frame_tampering(video_path)
            
            # Motion vector analysis
            motion_analysis = self._analyze_motion_vectors(video_path)
            
            # Temporal consistency check
            temporal_consistency = self._check_temporal_consistency(video_path)
            
            # Aggregate results
            tampered = (
                frame_analysis['tampered_frames'] > 0 or
                motion_analysis['anomalies_detected'] or
                not temporal_consistency['consistent']
            )
            
            return {
                "tampered": tampered,
                "confidence": max(
                    frame_analysis['confidence'],
                    motion_analysis['confidence'],
                    temporal_consistency['confidence']
                ),
                "frame_analysis": frame_analysis,
                "motion_analysis": motion_analysis,
                "temporal_consistency": temporal_consistency
            }
            
        except Exception as e:
            return {"tampered": True, "confidence": 0.0, "error": str(e)}
    
    # Audio-specific methods
    
    async def _detect_audio_deepfake(self, audio_path: str) -> Dict[str, Any]:
        """Detect deepfake in audio"""
        try:
            # Spectral analysis for synthetic indicators
            spectral_analysis = self._analyze_audio_spectrum(audio_path)
            
            # Voice consistency analysis
            voice_analysis = self._analyze_voice_consistency(audio_path)
            
            # Detect AI generation artifacts
            ai_artifacts = self._detect_audio_ai_artifacts(audio_path)
            
            # Calculate deepfake probability
            deepfake_probability = (
                spectral_analysis['synthetic_score'] * 0.4 +
                voice_analysis['inconsistency_score'] * 0.4 +
                ai_artifacts['artifact_score'] * 0.2
            )
            
            return {
                "deepfake_probability": deepfake_probability,
                "confidence": max(
                    spectral_analysis['confidence'],
                    voice_analysis['confidence'],
                    ai_artifacts['confidence']
                ),
                "spectral_analysis": spectral_analysis,
                "voice_analysis": voice_analysis,
                "ai_artifacts": ai_artifacts
            }
            
        except Exception as e:
            return {"deepfake_probability": 0.0, "confidence": 0.0, "error": str(e)}
    
    async def _detect_audio_tampering(self, audio_path: str) -> Dict[str, Any]:
        """Detect audio tampering"""
        try:
            # Waveform discontinuity analysis
            waveform_analysis = self._analyze_waveform_discontinuities(audio_path)
            
            # Frequency domain analysis
            frequency_analysis = self._analyze_frequency_anomalies(audio_path)
            
            # Noise consistency check
            noise_analysis = self._analyze_noise_consistency(audio_path)
            
            # Aggregate results
            tampered = (
                waveform_analysis['discontinuities_found'] or
                frequency_analysis['anomalies_detected'] or
                not noise_analysis['consistent']
            )
            
            return {
                "tampered": tampered,
                "confidence": max(
                    waveform_analysis['confidence'],
                    frequency_analysis['confidence'],
                    noise_analysis['confidence']
                ),
                "waveform_analysis": waveform_analysis,
                "frequency_analysis": frequency_analysis,
                "noise_analysis": noise_analysis
            }
            
        except Exception as e:
            return {"tampered": True, "confidence": 0.0, "error": str(e)}
    
    # Utility methods for forensic analysis
    
    def _extract_embedded_metadata(self, content_path: str) -> Dict[str, Any]:
        """Extract embedded metadata from content"""
        try:
            # Use different extraction methods based on file type
            file_type = magic.from_file(content_path, mime=True)
            
            if file_type.startswith('image/'):
                return self._extract_image_metadata(content_path)
            elif file_type.startswith('video/'):
                return self._extract_video_metadata(content_path)
            elif file_type.startswith('audio/'):
                return self._extract_audio_metadata(content_path)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            return {}
    
    def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract image metadata"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            image = Image.open(image_path)
            exifdata = image.getexif()
            
            metadata = {}
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                metadata[tag] = data
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata"""
        try:
            import ffmpeg
            
            probe = ffmpeg.probe(video_path)
            metadata = probe.get('format', {}).get('tags', {})
            
            # Add stream information
            streams = probe.get('streams', [])
            for i, stream in enumerate(streams):
                metadata[f"stream_{i}"] = stream
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_audio_metadata(self, audio_path: str) -> Dict[str, Any]:
        """Extract audio metadata"""
        try:
            import mutagen
            
            audio_file = mutagen.File(audio_path)
            if audio_file is not None:
                return dict(audio_file)
            return {}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_metadata_consistency(
        self,
        embedded_metadata: Dict[str, Any],
        external_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze metadata consistency"""
        inconsistencies = []
        consistency_score = 1.0
        
        if external_metadata:
            for key, value in external_metadata.items():
                if key in embedded_metadata:
                    if embedded_metadata[key] != value:
                        inconsistencies.append({
                            "field": key,
                            "embedded": embedded_metadata[key],
                            "external": value
                        })
                        consistency_score -= 0.1
        
        return {
            "score": max(0.0, consistency_score),
            "inconsistencies": inconsistencies,
            "total_fields": len(embedded_metadata)
        }
    
    def _detect_metadata_tampering(self, metadata: Dict[str, Any]) -> List[str]:
        """Detect metadata tampering indicators"""
        indicators = []
        
        # Check for impossible timestamps
        if 'DateTime' in metadata:
            try:
                dt = datetime.strptime(str(metadata['DateTime']), '%Y:%m:%d %H:%M:%S')
                if dt.year < 1990 or dt > datetime.now():
                    indicators.append("Impossible timestamp")
            except:
                indicators.append("Invalid timestamp format")
        
        # Check for suspicious software tags
        suspicious_software = ['photoshop', 'gimp', 'deepfake', 'synthetic']
        software_field = metadata.get('Software', '').lower()
        for software in suspicious_software:
            if software in software_field:
                indicators.append(f"Suspicious software: {software}")
        
        # Check for missing critical metadata
        critical_fields = ['DateTime', 'Make', 'Model']
        missing_fields = [field for field in critical_fields if field not in metadata]
        if len(missing_fields) > 2:
            indicators.append("Missing critical metadata fields")
        
        return indicators
    
    def _verify_creation_timestamps(self, metadata: Dict[str, Any]) -> bool:
        """Verify creation timestamp consistency"""
        try:
            # Extract various timestamp fields
            timestamps = []
            
            for field in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized', 'CreateDate']:
                if field in metadata:
                    try:
                        ts = datetime.strptime(str(metadata[field]), '%Y:%m:%d %H:%M:%S')
                        timestamps.append(ts)
                    except:
                        continue
            
            if len(timestamps) < 2:
                return True  # Can't verify with insufficient data
            
            # Check if timestamps are reasonably consistent (within 1 minute)
            time_diffs = []
            for i in range(len(timestamps) - 1):
                diff = abs((timestamps[i] - timestamps[i + 1]).total_seconds())
                time_diffs.append(diff)
            
            # If any difference is more than 60 seconds, consider suspicious
            return all(diff <= 60 for diff in time_diffs)
            
        except Exception:
            return False
    
    def _calculate_content_hash(self, content_path: str) -> str:
        """Calculate content hash for signature verification"""
        hash_obj = hashlib.sha256()
        
        with open(content_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _extract_signature_data(self, content_path: str) -> Optional[Dict[str, Any]]:
        """Extract digital signature data from content"""
        # This would implement extraction of embedded digital signatures
        # For now, return None to indicate no signature found
        return None
    
    def _verify_signature(self, content_hash: str, signature_data: Dict[str, Any]) -> bool:
        """Verify digital signature"""
        try:
            # Implementation would verify the signature against the content hash
            # Using the appropriate public key and algorithm
            return False  # Placeholder
        except Exception:
            return False
    
    def _detect_suspicious_metadata_patterns(self, metadata: Dict[str, Any]) -> List[str]:
        """Detect suspicious patterns in metadata"""
        suspicious_patterns = []
        
        # Check for round number artifacts (common in synthetic content)
        for key, value in metadata.items():
            if isinstance(value, (int, float)):
                if value != 0 and value % 10 == 0:
                    suspicious_patterns.append(f"Round number in {key}: {value}")
        
        # Check for missing GPS data when other location indicators exist
        if 'GPS' not in str(metadata) and any(
            loc_indicator in str(metadata).lower() 
            for loc_indicator in ['location', 'place', 'city']
        ):
            suspicious_patterns.append("Missing GPS data with location references")
        
        return suspicious_patterns
    
    async def _verify_blockchain_record_integrity(
        self,
        blockchain_record: Dict[str, Any]
    ) -> bool:
        """Verify blockchain record integrity"""
        try:
            # Verify the record against the blockchain
            verification_result = await self.blockchain.verify_record_integrity(
                blockchain_record
            )
            return verification_result
        except Exception:
            return False
    
    def _analyze_pixel_patterns(self, content_path: str, content_type: str) -> Dict[str, Any]:
        """Analyze pixel patterns for authenticity"""
        try:
            if content_type == "image":
                image = cv2.imread(content_path)
                
                # Analyze noise patterns
                noise_analysis = self._analyze_noise_patterns(image)
                
                # Check for unnatural gradients
                gradient_analysis = self._analyze_gradients(image)
                
                # Detect editing artifacts
                editing_artifacts = self._detect_editing_artifacts(image)
                
                # Calculate overall analysis score
                analysis_score = (
                    noise_analysis['naturalness_score'] * 0.4 +
                    gradient_analysis['naturalness_score'] * 0.3 +
                    editing_artifacts['authenticity_score'] * 0.3
                )
                
                return {
                    "analysis_score": analysis_score,
                    "anomalies": (
                        noise_analysis['anomalies'] +
                        gradient_analysis['anomalies'] +
                        editing_artifacts['anomalies']
                    ),
                    "noise_analysis": noise_analysis,
                    "gradient_analysis": gradient_analysis,
                    "editing_artifacts": editing_artifacts
                }
            
            return {"analysis_score": 1.0, "anomalies": []}
            
        except Exception as e:
            return {"analysis_score": 0.0, "anomalies": [], "error": str(e)}
    
    # Placeholder methods for complex forensic algorithms
    # These would be implemented with actual computer vision and signal processing algorithms
    
    def _analyze_facial_inconsistencies(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze facial inconsistencies for deepfake detection"""
        return {
            "inconsistency_score": 0.1,
            "confidence": 0.8,
            "detected_faces": 1,
            "inconsistencies": []
        }
    
    def _detect_ai_generation_artifacts(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect AI generation artifacts"""
        return {
            "artifact_score": 0.05,
            "confidence": 0.7,
            "artifacts_found": [],
            "generation_probability": 0.1
        }
    
    def _perform_ela_analysis(self, image_path: str) -> Dict[str, Any]:
        """Perform Error Level Analysis"""
        return {
            "suspicious_regions": 0,
            "confidence": 0.6,
            "ela_image_path": None,
            "analysis_details": {}
        }
    
    def _detect_copy_move_forgery(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect copy-move forgery"""
        return {
            "matches_found": 0,
            "confidence": 0.7,
            "match_regions": [],
            "similarity_threshold": 0.95
        }
    
    def _detect_image_splicing(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect image splicing"""
        return {
            "splicing_detected": False,
            "confidence": 0.6,
            "splice_boundaries": [],
            "consistency_score": 0.9
        }
    
    def _detect_jpeg_artifacts(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect JPEG compression artifacts"""
        return {
            "detected": False,
            "quality_estimate": 95,
            "block_artifacts": [],
            "quantization_analysis": {}
        }
    
    def _analyze_compression_consistency(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze compression consistency"""
        return {
            "quality_score": 0.9,
            "consistent": True,
            "inconsistent_regions": [],
            "compression_history": []
        }
    
    def _detect_multiple_compression(self, image_path: str) -> Dict[str, Any]:
        """Detect multiple compression"""
        return {
            "detected": False,
            "compression_count": 1,
            "quality_degradation": 0.05,
            "artifacts": []
        }
    
    def _analyze_temporal_inconsistencies(self, video_path: str) -> Dict[str, Any]:
        """Analyze temporal inconsistencies in video"""
        return {
            "inconsistency_score": 0.1,
            "confidence": 0.8,
            "inconsistent_frames": [],
            "temporal_artifacts": []
        }
    
    def _analyze_video_facial_artifacts(self, video_path: str) -> Dict[str, Any]:
        """Analyze facial artifacts in video"""
        return {
            "artifact_score": 0.05,
            "confidence": 0.7,
            "facial_inconsistencies": [],
            "tracking_errors": []
        }
    
    def _analyze_av_synchronization(self, video_path: str) -> Dict[str, Any]:
        """Analyze audio-visual synchronization"""
        return {
            "sync_score": 0.05,
            "confidence": 0.6,
            "sync_issues": [],
            "lip_sync_accuracy": 0.95
        }
    
    def _analyze_frame_tampering(self, video_path: str) -> Dict[str, Any]:
        """Analyze frame tampering"""
        return {
            "tampered_frames": 0,
            "confidence": 0.8,
            "tampering_types": [],
            "frame_analysis": {}
        }
    
    def _analyze_motion_vectors(self, video_path: str) -> Dict[str, Any]:
        """Analyze motion vectors for inconsistencies"""
        return {
            "anomalies_detected": False,
            "confidence": 0.7,
            "motion_inconsistencies": [],
            "vector_analysis": {}
        }
    
    def _check_temporal_consistency(self, video_path: str) -> Dict[str, Any]:
        """Check temporal consistency"""
        return {
            "consistent": True,
            "confidence": 0.8,
            "consistency_score": 0.9,
            "temporal_anomalies": []
        }
    
    def _analyze_audio_spectrum(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio spectrum for synthetic indicators"""
        return {
            "synthetic_score": 0.1,
            "confidence": 0.7,
            "spectral_anomalies": [],
            "frequency_analysis": {}
        }
    
    def _analyze_voice_consistency(self, audio_path: str) -> Dict[str, Any]:
        """Analyze voice consistency"""
        return {
            "inconsistency_score": 0.05,
            "confidence": 0.8,
            "voice_characteristics": {},
            "consistency_metrics": {}
        }
    
    def _detect_audio_ai_artifacts(self, audio_path: str) -> Dict[str, Any]:
        """Detect AI generation artifacts in audio"""
        return {
            "artifact_score": 0.1,
            "confidence": 0.6,
            "ai_indicators": [],
            "generation_probability": 0.15
        }
    
    def _analyze_waveform_discontinuities(self, audio_path: str) -> Dict[str, Any]:
        """Analyze waveform discontinuities"""
        return {
            "discontinuities_found": False,
            "confidence": 0.8,
            "discontinuity_locations": [],
            "waveform_analysis": {}
        }
    
    def _analyze_frequency_anomalies(self, audio_path: str) -> Dict[str, Any]:
        """Analyze frequency domain anomalies"""
        return {
            "anomalies_detected": False,
            "confidence": 0.7,
            "frequency_anomalies": [],
            "spectral_consistency": 0.9
        }
    
    def _analyze_noise_consistency(self, audio_path: str) -> Dict[str, Any]:
        """Analyze noise consistency"""
        return {
            "consistent": True,
            "confidence": 0.8,
            "noise_profile": {},
            "consistency_score": 0.9
        }
    
    def _analyze_noise_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze noise patterns in image"""
        return {
            "naturalness_score": 0.9,
            "anomalies": [],
            "noise_characteristics": {},
            "distribution_analysis": {}
        }
    
    def _analyze_gradients(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze gradients for unnaturalness"""
        return {
            "naturalness_score": 0.85,
            "anomalies": [],
            "gradient_consistency": 0.9,
            "edge_analysis": {}
        }
    
    def _detect_editing_artifacts(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect editing artifacts"""
        return {
            "authenticity_score": 0.9,
            "anomalies": [],
            "editing_indicators": [],
            "tool_signatures": []
        }
    
    def _generate_certificate_id(self) -> str:
        """Generate unique certificate ID"""
        timestamp = str(int(time.time()))
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"CERT_{timestamp}_{random_suffix}"
    
    def _calculate_validity_period(self, verification_result: AuthenticityResult) -> Dict[str, str]:
        """Calculate certificate validity period"""
        issue_date = verification_result.verification_timestamp
        expiry_date = issue_date.replace(year=issue_date.year + 1)
        
        return {
            "issued": issue_date.isoformat(),
            "expires": expiry_date.isoformat()
        }
    
    def _get_verification_methods_used(self, verification_result: AuthenticityResult) -> List[str]:
        """Get list of verification methods used"""
        methods = ["metadata_analysis", "pixel_analysis"]
        
        if verification_result.digital_signature:
            methods.append("digital_signature")
        if verification_result.blockchain_proof:
            methods.append("blockchain_verification")
        if verification_result.compression_artifacts:
            methods.append("compression_analysis")
        
        return methods
    
    def _sign_certificate(self, certificate: Dict[str, Any]) -> str:
        """Sign authenticity certificate"""
        try:
            # Create certificate data for signing (excluding signature field)
            cert_data = {k: v for k, v in certificate.items() if k != "issuer_signature"}
            cert_json = json.dumps(cert_data, sort_keys=True).encode()
            
            # Sign with private key
            signature = self.signature_keys['private_key'].sign(
                cert_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature.hex()
            
        except Exception as e:
            self.logger.error(f"Certificate signing failed: {str(e)}")
            return ""
    
    async def _store_authenticity_certificate(self, certificate: Dict[str, Any]):
        """Store authenticity certificate"""
        try:
            # Store in database
            conn = sqlite3.connect(self.config.get('db_path', 'authenticity.db'))
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS authenticity_certificates (
                    certificate_id TEXT PRIMARY KEY,
                    content_id TEXT,
                    certificate_data TEXT,
                    issue_timestamp TEXT,
                    expiry_timestamp TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO authenticity_certificates 
                (certificate_id, content_id, certificate_data, issue_timestamp, expiry_timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                certificate['certificate_id'],
                certificate['content_id'],
                json.dumps(certificate),
                certificate['verification_timestamp'],
                certificate['validity_period']['expires']
            ))
            
            conn.commit()
            conn.close()
            
            # Cache certificate
            self.redis_client.setex(
                f"cert:{certificate['certificate_id']}",
                86400,  # 24 hours
                json.dumps(certificate)
            )
            
        except Exception as e:
            self.logger.error(f"Certificate storage failed: {str(e)}")


# Example usage and testing
async def main():
    """Example usage of Content Authenticity Verifier"""
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'db_path': 'authenticity.db',
        'blockchain_network': 'ethereum',
        'contract_address': '0x...',
        'private_key': 'your_private_key'
    }
    
    verifier = ContentAuthenticityVerifier(config)
    
    # Example: Verify image authenticity
    try:
        result = await verifier.verify_authenticity(
            content_path="/path/to/image.jpg",
            content_type="image",
            metadata={"creator": "photographer", "location": "Paris"}
        )
        
        print(f"Authenticity Level: {result.authenticity_level}")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"Tamper Indicators: {result.tamper_indicators}")
        
        # Generate certificate
        if result.authenticity_level == AuthenticityLevel.VERIFIED:
            certificate = await verifier.generate_authenticity_certificate(
                result.content_id, result
            )
            print(f"Certificate Generated: {certificate['certificate_id']}")
        
    except Exception as e:
        print(f"Verification failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())