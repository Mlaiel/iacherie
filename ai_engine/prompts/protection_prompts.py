"""
Professional AI Protection Prompts System
Professional prompts for multi-format content protection (audio, video, image, text fingerprinting)

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

 COPYRIGHT WARNING 
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pydantic import BaseModel, Field
import hashlib
import uuid

logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ContentType(Enum):
    """Content types for protection"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    CODE = "code"
    MIXED_MEDIA = "mixed_media"

class FingerprintingMethod(Enum):
    """Fingerprinting methods available"""
    SPECTRAL = "spectral"
    PERCEPTUAL = "perceptual"
    CHROMAPRINT = "chromaprint"
    WATERMARK = "watermark"
    BLOCKCHAIN = "blockchain"
    AI_SIGNATURE = "ai_signature"

class MonitoringPlatform(Enum):
    """Platforms to monitor for content theft"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    GENERIC_WEB = "generic_web"

@dataclass
class ProtectionContext:
    """Context for protection prompt generation"""
    content_type: ContentType
    protection_level: ProtectionLevel
    fingerprinting_methods: List[FingerprintingMethod]
    monitoring_platforms: List[MonitoringPlatform]
    legal_requirements: Dict[str, Any]
    technical_specs: Dict[str, Any]

class AIProtectionPrompts:
    """Professional AI Protection Prompts System"""
    
    def __init__(self):
        """Initialize the AI protection prompts system"""
        self.protection_templates = {}
        self.fingerprinting_algorithms = {}
        self.legal_templates = {}
        self._load_protection_templates()
    
    def _load_protection_templates(self) -> None:
        """Load and initialize protection prompt templates"""
        self.protection_templates = {
            ContentType.AUDIO: {
                ProtectionLevel.BASIC: {
                    "id": "audio_basic_protection",
                    "template": """
                    Create basic audio content protection system:
                    
                    Audio Analysis:
                    - File path: {file_path}
                    - Duration: {duration} seconds
                    - Sample rate: {sample_rate} Hz
                    - Bit depth: {bit_depth} bit
                    - Channels: {channels}
                    - Format: {format}
                    
                    Basic Fingerprinting:
                    - Extract audio features using FFT analysis
                    - Generate spectral centroid fingerprint
                    - Create tempo and rhythm signature
                    - Calculate harmonic content hash
                    - Generate basic perceptual hash
                    
                    Protection Metadata:
                    - Creator: {creator_name}
                    - Copyright year: {copyright_year}
                    - Rights holder: {rights_holder}
                    - Usage license: {license_type}
                    - Contact information: {contact_info}
                    
                    Basic Monitoring:
                    - Platform coverage: {monitoring_platforms}
                    - Check frequency: {check_frequency}
                    - Match threshold: {match_threshold}%
                    - Alert method: {alert_method}
                    
                    Output Requirements:
                    1. Audio fingerprint signature (JSON format)
                    2. Protection metadata file
                    3. Basic monitoring configuration
                    4. Simple copyright notice template
                    5. Usage tracking setup
                    """,
                    "variables": ["file_path", "duration", "sample_rate", "bit_depth", "channels", "format", "creator_name", "copyright_year", "rights_holder", "license_type", "contact_info", "monitoring_platforms", "check_frequency", "match_threshold", "alert_method"],
                    "quality_score": 85
                },
                ProtectionLevel.PROFESSIONAL: {
                    "id": "audio_professional_protection",
                    "template": """
                    Create professional multi-layer audio content protection:
                    
                    Audio Technical Analysis:
                    - File: {file_path}
                    - Codec: {codec}
                    - Bitrate: {bitrate} kbps
                    - Sample rate: {sample_rate} Hz
                    - Bit depth: {bit_depth} bit
                    - Channel configuration: {channels}
                    - Dynamic range: {dynamic_range} dB
                    
                    Professional Fingerprinting Stack:
                    1. Spectral Fingerprinting:
                       - MFCC coefficients extraction
                       - Chroma features analysis
                       - Spectral rolloff computation
                       - Zero crossing rate analysis
                    
                    2. Perceptual Hashing:
                       - Psychoacoustic model application
                       - Masking threshold calculation
                       - Perceptual entropy measurement
                       - Loudness normalization fingerprint
                    
                    3. Temporal Analysis:
                       - Beat tracking and tempo extraction
                       - Onset detection fingerprinting
                       - Rhythm pattern signature
                       - Harmonic progression mapping
                    
                    4. AI-based Signature:
                       - Deep neural network feature extraction
                       - Learned audio representations
                       - Content-aware hashing
                       - Style and genre fingerprinting
                    
                    Watermarking System:
                    - Invisible watermark embedding: {watermark_strength}
                    - Spread spectrum technique: {spread_spectrum}
                    - Robustness level: {robustness_level}
                    - Payload capacity: {payload_bits} bits
                    
                    Multi-Platform Monitoring:
                    - Platforms: {monitoring_platforms}
                    - API integrations: {api_integrations}
                    - Real-time scanning: {realtime_scanning}
                    - Batch processing: {batch_processing}
                    - Match sensitivity: {sensitivity_level}
                    
                    Legal Protection Framework:
                    - Copyright registration: {copyright_reg}
                    - DMCA takedown preparation: {dmca_ready}
                    - International rights management: {intl_rights}
                    - Revenue tracking: {revenue_tracking}
                    - Infringement documentation: {infringement_docs}
                    
                    Output Requirements:
                    1. Multi-layer fingerprint database
                    2. Watermarked audio file
                    3. Advanced monitoring configuration
                    4. Legal documentation package
                    5. Revenue protection system
                    6. Infringement detection reports
                    """,
                    "variables": ["file_path", "codec", "bitrate", "sample_rate", "bit_depth", "channels", "dynamic_range", "watermark_strength", "spread_spectrum", "robustness_level", "payload_bits", "monitoring_platforms", "api_integrations", "realtime_scanning", "batch_processing", "sensitivity_level", "copyright_reg", "dmca_ready", "intl_rights", "revenue_tracking", "infringement_docs"],
                    "quality_score": 95
                }
            },
            
            ContentType.VIDEO: {
                ProtectionLevel.PROFESSIONAL: {
                    "id": "video_professional_protection",
                    "template": """
                    Create comprehensive video content protection system:
                    
                    Video Analysis:
                    - File: {video_file}
                    - Resolution: {resolution}
                    - Frame rate: {frame_rate} fps
                    - Codec: {video_codec}
                    - Bitrate: {video_bitrate} Mbps
                    - Duration: {duration}
                    - Container: {container_format}
                    
                    Audio Track Analysis:
                    - Audio codec: {audio_codec}
                    - Sample rate: {audio_sample_rate} Hz
                    - Channels: {audio_channels}
                    - Bitrate: {audio_bitrate} kbps
                    
                    Multi-Modal Fingerprinting:
                    1. Visual Fingerprinting:
                       - Keyframe extraction and analysis
                       - Scene change detection
                       - Color histogram signatures
                       - Edge detection patterns
                       - Motion vector analysis
                       - Spatial-temporal features
                    
                    2. Audio Fingerprinting:
                       - Spectral analysis of soundtrack
                       - Speech recognition patterns
                       - Music identification signatures
                       - Ambient sound fingerprints
                    
                    3. Content Understanding:
                       - Object detection and tracking
                       - Face recognition (privacy-compliant)
                       - Text overlay extraction (OCR)
                       - Logo and brand detection
                       - Scene classification
                    
                    Professional Watermarking:
                    - Invisible video watermark: {video_watermark}
                    - Audio watermark: {audio_watermark}
                    - Frame-based embedding: {frame_embedding}
                    - Temporal synchronization: {temporal_sync}
                    - Robustness testing: {robustness_tests}
                    
                    Platform-Specific Protection:
                    - YouTube Content ID: {youtube_protection}
                    - Facebook Rights Manager: {facebook_protection}
                    - Instagram copyright: {instagram_protection}
                    - TikTok protection: {tiktok_protection}
                    - Twitch DMCA: {twitch_protection}
                    
                    Legal and Monetization:
                    - Content registration: {content_registration}
                    - Revenue claim setup: {revenue_claims}
                    - Geographic restrictions: {geo_restrictions}
                    - Usage licensing: {usage_licensing}
                    - Infringement tracking: {infringement_tracking}
                    
                    Output Requirements:
                    1. Multi-modal fingerprint database
                    2. Watermarked video file
                    3. Platform-specific protection files
                    4. Legal documentation
                    5. Monetization configuration
                    6. Monitoring dashboard setup
                    """,
                    "variables": ["video_file", "resolution", "frame_rate", "video_codec", "video_bitrate", "duration", "container_format", "audio_codec", "audio_sample_rate", "audio_channels", "audio_bitrate", "video_watermark", "audio_watermark", "frame_embedding", "temporal_sync", "robustness_tests", "youtube_protection", "facebook_protection", "instagram_protection", "tiktok_protection", "twitch_protection", "content_registration", "revenue_claims", "geo_restrictions", "usage_licensing", "infringement_tracking"],
                    "quality_score": 97
                }
            },
            
            ContentType.IMAGE: {
                ProtectionLevel.PROFESSIONAL: {
                    "id": "image_professional_protection",
                    "template": """
                    Create professional image content protection system:
                    
                    Image Analysis:
                    - File: {image_file}
                    - Format: {image_format}
                    - Dimensions: {width}x{height}
                    - Color depth: {color_depth} bit
                    - Color space: {color_space}
                    - DPI/Resolution: {dpi}
                    - File size: {file_size} MB
                    
                    EXIF Data Enhancement:
                    - Camera information: {camera_info}
                    - Shooting parameters: {shooting_params}
                    - GPS coordinates: {gps_coords}
                    - Timestamp: {timestamp}
                    - Creator metadata: {creator_metadata}
                    
                    Professional Image Fingerprinting:
                    1. Perceptual Hashing:
                       - pHash (perceptual hash)
                       - aHash (average hash)
                       - dHash (difference hash)
                       - wHash (wavelet hash)
                    
                    2. Feature Extraction:
                       - SIFT (Scale-Invariant Feature Transform)
                       - SURF (Speeded-Up Robust Features)
                       - ORB (Oriented FAST and Rotated BRIEF)
                       - Local Binary Patterns
                    
                    3. Deep Learning Features:
                       - CNN-based feature extraction
                       - Semantic content analysis
                       - Style and artistic technique detection
                       - Composition analysis
                    
                    Digital Watermarking:
                    - Invisible watermark: {invisible_watermark}
                    - Visible watermark: {visible_watermark}
                    - LSB (Least Significant Bit) embedding
                    - DCT (Discrete Cosine Transform) domain
                    - Wavelet domain embedding
                    - Robustness level: {watermark_robustness}
                    
                    IPTC/XMP Metadata:
                    - Copyright information: {copyright_info}
                    - Rights management: {rights_info}
                    - Usage terms: {usage_terms}
                    - Contact details: {contact_details}
                    - Keywords and categories: {keywords}
                    
                    Protection Monitoring:
                    - Reverse image search: {reverse_search}
                    - Stock photo sites: {stock_monitoring}
                    - Social media platforms: {social_monitoring}
                    - E-commerce sites: {ecommerce_monitoring}
                    - Search engine monitoring: {search_monitoring}
                    
                    Legal Protection:
                    - Copyright registration: {copyright_registration}
                    - DMCA preparation: {dmca_preparation}
                    - Usage licensing: {licensing}
                    - Revenue tracking: {revenue_tracking}
                    
                    Output Requirements:
                    1. Multi-hash fingerprint database
                    2. Watermarked image variants
                    3. Enhanced metadata package
                    4. Monitoring configuration
                    5. Legal documentation
                    6. Revenue protection setup
                    """,
                    "variables": ["image_file", "image_format", "width", "height", "color_depth", "color_space", "dpi", "file_size", "camera_info", "shooting_params", "gps_coords", "timestamp", "creator_metadata", "invisible_watermark", "visible_watermark", "watermark_robustness", "copyright_info", "rights_info", "usage_terms", "contact_details", "keywords", "reverse_search", "stock_monitoring", "social_monitoring", "ecommerce_monitoring", "search_monitoring", "copyright_registration", "dmca_preparation", "licensing", "revenue_tracking"],
                    "quality_score": 94
                }
            },
            
            ContentType.TEXT: {
                ProtectionLevel.PROFESSIONAL: {
                    "id": "text_professional_protection",
                    "template": """
                    Create comprehensive text content protection system:
                    
                    Text Analysis:
                    - Content file: {text_file}
                    - Word count: {word_count}
                    - Language: {language}
                    - Encoding: {encoding}
                    - Content type: {content_type}
                    - Genre/Category: {genre}
                    
                    Linguistic Fingerprinting:
                    1. Stylometric Analysis:
                       - Sentence length distribution
                       - Word frequency patterns
                       - Punctuation usage patterns
                       - Vocabulary richness metrics
                       - Syntactic complexity analysis
                    
                    2. Semantic Fingerprinting:
                       - Topic modeling (LDA/LSA)
                       - Semantic embeddings (Word2Vec/BERT)
                       - Named entity patterns
                       - Concept relationship mapping
                       - Discourse structure analysis
                    
                    3. N-gram Analysis:
                       - Character n-grams (3-5)
                       - Word n-grams (2-4)
                       - Phrase pattern extraction
                       - Rare word combinations
                       - Linguistic signature creation
                    
                    Plagiarism Protection:
                    - Content originality score: {originality_score}%
                    - Reference database: {reference_db}
                    - Citation verification: {citation_check}
                    - Paraphrase detection: {paraphrase_detection}
                    - Translation plagiarism: {translation_check}
                    
                    Text Watermarking:
                    - Invisible watermark: {text_watermark}
                    - Synonym substitution: {synonym_watermark}
                    - Syntactic transformation: {syntactic_watermark}
                    - Zero-width character insertion: {zero_width_chars}
                    - Linguistic steganography: {steganography}
                    
                    Content Monitoring:
                    - Web scraping detection: {web_scraping}
                    - Search engine monitoring: {search_monitoring}
                    - Academic database checking: {academic_db}
                    - Social media monitoring: {social_monitoring}
                    - Blog/news site monitoring: {blog_monitoring}
                    
                    Legal Framework:
                    - Copyright registration: {copyright_reg}
                    - DMCA takedown: {dmca_takedown}
                    - Creative Commons licensing: {cc_licensing}
                    - Usage tracking: {usage_tracking}
                    - Attribution verification: {attribution_check}
                    
                    AI-Enhanced Protection:
                    - ML-based similarity detection
                    - Transformer model embeddings
                    - Contextual understanding
                    - Intent and purpose analysis
                    - Cross-language detection
                    
                    Output Requirements:
                    1. Comprehensive text fingerprint
                    2. Watermarked content versions
                    3. Monitoring configuration
                    4. Legal documentation package
                    5. Plagiarism detection setup
                    6. Revenue protection system
                    """,
                    "variables": ["text_file", "word_count", "language", "encoding", "content_type", "genre", "originality_score", "reference_db", "citation_check", "paraphrase_detection", "translation_check", "text_watermark", "synonym_watermark", "syntactic_watermark", "zero_width_chars", "steganography", "web_scraping", "search_monitoring", "academic_db", "social_monitoring", "blog_monitoring", "copyright_reg", "dmca_takedown", "cc_licensing", "usage_tracking", "attribution_check"],
                    "quality_score": 93
                }
            }
        }
    
    def generate_protection_prompt(self, context: ProtectionContext, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a protection prompt based on context"""



        try:
            # Get protection template
            content_templates = self.protection_templates.get(context.content_type, {})
            protection_template = content_templates.get(context.protection_level)
            
            if not protection_template:
                logger.warning(f"No protection template found for {context.content_type} - {context.protection_level}")
                return self._generate_fallback_protection_prompt(context)
            
            # Customize prompt based on fingerprinting methods
            customized_prompt = self._customize_for_fingerprinting(protection_template, context)
            
            # Apply technical specifications
            if context.technical_specs:
                customized_prompt = self._apply_technical_specs(customized_prompt, context.technical_specs)
            
            # Apply legal requirements
            if context.legal_requirements:
                customized_prompt = self._apply_legal_requirements(customized_prompt, context.legal_requirements)
            
            # Apply custom parameters
            if custom_params:
                customized_prompt = self._apply_custom_protection_params(customized_prompt, custom_params)
            
            # Add metadata
            customized_prompt["generation_timestamp"] = datetime.utcnow().isoformat()
            customized_prompt["protection_id"] = str(uuid.uuid4())
            customized_prompt["context_hash"] = self._generate_protection_hash(context)
            
            return customized_prompt
            
        except Exception as e:
            logger.error(f"Error generating protection prompt: {str(e)}")
            return self._generate_fallback_protection_prompt(context)
    
    def _customize_for_fingerprinting(self, template: Dict, context: ProtectionContext) -> Dict:
        """Customize template based on fingerprinting methods"""
        customized = template.copy()
        
        # Add fingerprinting method specific instructions
        fingerprinting_instructions = []
        for method in context.fingerprinting_methods:
            if method == FingerprintingMethod.SPECTRAL:
                fingerprinting_instructions.append("- Apply professional spectral analysis with FFT and MFCC")
            elif method == FingerprintingMethod.PERCEPTUAL:
                fingerprinting_instructions.append("- Generate perceptual hash using psychoacoustic/visual models")
            elif method == FingerprintingMethod.CHROMAPRINT:
                fingerprinting_instructions.append("- Create Chromaprint signature for audio content")
            elif method == FingerprintingMethod.WATERMARK:
                fingerprinting_instructions.append("- Embed invisible watermark using spread spectrum technique")
            elif method == FingerprintingMethod.BLOCKCHAIN:
                fingerprinting_instructions.append("- Register fingerprint on blockchain for immutable proof")
            elif method == FingerprintingMethod.AI_SIGNATURE:
                fingerprinting_instructions.append("- Extract AI-based semantic signatures using deep learning")
        
        if fingerprinting_instructions:
            template_text = customized.get("template", "")
            fingerprint_section = "\n\nAdditional Fingerprinting Methods:\n" + "\n".join(fingerprinting_instructions)
            customized["template"] = template_text + fingerprint_section
        
        return customized
    
    def _apply_technical_specs(self, prompt: Dict, tech_specs: Dict) -> Dict:
        """Apply technical specifications to prompt"""
        modified_prompt = prompt.copy()
        
        # Replace technical variables in template
        template = modified_prompt.get("template", "")
        for spec_key, spec_value in tech_specs.items():
            template = template.replace(f"{{{spec_key}}}", str(spec_value))
        
        modified_prompt["template"] = template
        modified_prompt["technical_specs_applied"] = tech_specs
        
        return modified_prompt
    
    def _apply_legal_requirements(self, prompt: Dict, legal_reqs: Dict) -> Dict:
        """Apply legal requirements to prompt"""
        modified_prompt = prompt.copy()
        
        # Add legal compliance section
        legal_section = "\n\nLegal Compliance Requirements:\n"
        for req_key, req_value in legal_reqs.items():
            legal_section += f"- {req_key.replace('_', ' ').title()}: {req_value}\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + legal_section
        modified_prompt["legal_requirements_applied"] = legal_reqs
        
        return modified_prompt
    
    def _apply_custom_protection_params(self, prompt: Dict, custom_params: Dict) -> Dict:
        """Apply custom protection parameters"""
        modified_prompt = prompt.copy()
        
        # Replace custom parameters in template
        template = modified_prompt.get("template", "")
        for param_key, param_value in custom_params.items():
            template = template.replace(f"{{{param_key}}}", str(param_value))
        
        modified_prompt["template"] = template
        modified_prompt["custom_parameters"] = custom_params
        
        return modified_prompt
    
    def _generate_fallback_protection_prompt(self, context: ProtectionContext) -> Dict[str, Any]:
        """Generate fallback protection prompt"""



        return {
            "id": "fallback_protection",
            "template": f"""
            Create {context.protection_level.value} protection for {context.content_type.value} content:
            
            Protection Requirements:
            - Content type: {context.content_type.value}
            - Protection level: {context.protection_level.value}
            - Fingerprinting methods: {[m.value for m in context.fingerprinting_methods]}
            - Monitoring platforms: {[p.value for p in context.monitoring_platforms]}
            
            Please provide:
            1. Content fingerprinting strategy
            2. Protection implementation plan
            3. Monitoring configuration
            4. Legal compliance framework
            5. Revenue protection setup
            """,
            "variables": [],
            "quality_score": 70,
            "is_fallback": True
        }
    
    def _generate_protection_hash(self, context: ProtectionContext) -> str:
        """Generate hash for protection context"""
        context_string = f"{context.content_type.value}_{context.protection_level.value}_{len(context.fingerprinting_methods)}"
        return hashlib.md5(context_string.encode()).hexdigest()[:12]

class BlockchainProtectionPrompts:
    """Blockchain-based content protection prompts"""
    
    def __init__(self):
        """Initialize blockchain protection system"""
        self.blockchain_templates = {}
        self._load_blockchain_templates()
    
    def _load_blockchain_templates(self) -> None:
        """Load blockchain protection templates"""
        self.blockchain_templates = {
            "content_registration": {
                "template": """
                Create blockchain-based content registration system:
                
                Content Registration:
                - Content hash: {content_hash}
                - Creator wallet: {creator_wallet}
                - Registration timestamp: {timestamp}
                - Content metadata: {metadata}
                
                Smart Contract Deployment:
                - Contract address: {contract_address}
                - Network: {blockchain_network}
                - Gas optimization: {gas_optimization}
                - Royalty distribution: {royalty_percentage}%
                
                Immutable Proof Creation:
                - Content fingerprint hash
                - Creator digital signature
                - Timestamp proof
                - Merkle tree inclusion proof
                
                Legal Framework Integration:
                - Copyright law compliance
                - International IP protection
                - DMCA integration
                - Revenue distribution automation
                
                Output Requirements:
                1. Smart contract code
                2. Registration transaction hash
                3. Immutable proof certificate
                4. Legal documentation
                5. Royalty distribution setup
                """,
                "variables": ["content_hash", "creator_wallet", "timestamp", "metadata", "contract_address", "blockchain_network", "gas_optimization", "royalty_percentage"],
                "quality_score": 96
            }
        }
    
    def generate_blockchain_prompt(self, content_type: ContentType, custom_params: Dict) -> Dict[str, Any]:
        """Generate blockchain protection prompt"""
        template = self.blockchain_templates.get("content_registration")
        if not template:
            return {"error": "Blockchain template not found"}
        
        # Apply custom parameters
        template_text = template["template"]
        for param_key, param_value in custom_params.items():
            template_text = template_text.replace(f"{{{param_key}}}", str(param_value))
        
        return {
            "id": "blockchain_protection",
            "template": template_text,
            "blockchain_enabled": True,
            "content_type": content_type.value,
            "generation_timestamp": datetime.utcnow().isoformat()
        }

# Protection prompts registry
PROTECTION_PROMPTS_REGISTRY = {
    "audio_protection": AIProtectionPrompts(),
    "video_protection": AIProtectionPrompts(),
    "image_protection": AIProtectionPrompts(),
    "text_protection": AIProtectionPrompts(),
    "blockchain_protection": BlockchainProtectionPrompts()
}

def get_protection_prompts() -> AIProtectionPrompts:
    """Get the main protection prompts instance"""



    return AIProtectionPrompts()

def create_protection_context(
    content_type: str,
    protection_level: str,
    fingerprinting_methods: List[str],
    monitoring_platforms: List[str],
    legal_requirements: Optional[Dict] = None,
    technical_specs: Optional[Dict] = None
) -> ProtectionContext:
    """Create a protection context for content protection"""



    return ProtectionContext(
        content_type=ContentType(content_type),
        protection_level=ProtectionLevel(protection_level),
        fingerprinting_methods=[FingerprintingMethod(m) for m in fingerprinting_methods],
        monitoring_platforms=[MonitoringPlatform(p) for p in monitoring_platforms],
        legal_requirements=legal_requirements or {},
        technical_specs=technical_specs or {}
    )
