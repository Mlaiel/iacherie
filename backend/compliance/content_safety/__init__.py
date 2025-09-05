"""Content Safety Module - AI-Powered Content Moderation

Advanced AI-powered content safety and moderation system with ML-based detection
for hate speech, violence, misinformation, harassment, and other harmful content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .hate_speech_detector import HateSpeechDetector, HateSpeechType, SeverityLevel
from .violence_detector import ViolenceDetector, ViolenceType, ThreatLevel
from .adult_content_filter import AdultContentFilter, NSFWCategory, FilterLevel
from .spam_detector import SpamDetector, SpamType, ConfidenceLevel
from .misinformation_detector import MisinformationDetector, FakeNewsType, VerificationStatus
from .harassment_detector import HarassmentDetector, HarassmentType, TargetCategory
from .cyberbullying_detector import CyberbullyingDetector, BullyingPattern, VictimProfile
from .self_harm_detector import SelfHarmDetector, SelfHarmType, RiskLevel
from .drug_content_detector import DrugContentDetector, SubstanceType, ContentRisk
from .terrorism_detector import TerrorismDetector, TerrorismType, ThreatAssessment
from .content_classifier import ContentClassifier, ContentCategory, ClassificationConfidence

__all__ = [
    # Hate Speech Detection
    "HateSpeechDetector",
    "HateSpeechType",
    "SeverityLevel",
    
    # Violence Detection
    "ViolenceDetector",
    "ViolenceType",
    "ThreatLevel",
    
    # Adult Content Filtering
    "AdultContentFilter",
    "NSFWCategory",
    "FilterLevel",
    
    # Spam Detection
    "SpamDetector",
    "SpamType",
    "ConfidenceLevel",
    
    # Misinformation Detection
    "MisinformationDetector",
    "FakeNewsType",
    "VerificationStatus",
    
    # Harassment Detection
    "HarassmentDetector",
    "HarassmentType",
    "TargetCategory",
    
    # Cyberbullying Detection
    "CyberbullyingDetector",
    "BullyingPattern",
    "VictimProfile",
    
    # Self-harm Detection
    "SelfHarmDetector",
    "SelfHarmType",
    "RiskLevel",
    
    # Drug Content Detection
    "DrugContentDetector",
    "SubstanceType",
    "ContentRisk",
    
    # Terrorism Detection
    "TerrorismDetector",
    "TerrorismType",
    "ThreatAssessment",
    
    # Content Classification
    "ContentClassifier",
    "ContentCategory",
    "ClassificationConfidence"
]