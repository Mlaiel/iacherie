"""
Guardian Moderation System
Content moderation for chat, uploads, missions
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import re

# Profanity list (basic example - should be expanded)
PROFANITY_LIST = {
    "en": ["fuck", "shit", "damn", "bitch", "asshole", "bastard"],
    "fr": ["merde", "putain", "connard", "salope", "enculé"],
    "de": ["scheiße", "arsch", "fick"],
    "ar": ["كلب", "حمار"]
}

# Suspicious patterns
SPAM_PATTERNS = [
    r'\b(?:buy|sell|cheap|discount)\s+(?:viagra|cialis|pills)\b',
    r'\b(?:make|earn)\s+\$\d+\s+(?:per|a)\s+(?:day|hour)\b',
    r'(?:click|visit)\s+(?:here|this|now)',
    r'(?:www\.|http)[^\s]+(?:\.com|\.net|\.org)',
    r'\b(?:lottery|winner|prize|claim)\b.*\$\d+'
]

class ModerationResult(BaseModel):
    is_clean: bool
    confidence: float
    reasons: List[str] = []
    flagged_words: List[str] = []
    suggested_action: str  # "allow", "warn", "block", "review"

class ContentModerator:
    """Content moderation engine"""
    
    def __init__(self):
        self.profanity_map = self._build_profanity_map()
        self.spam_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SPAM_PATTERNS]
    
    def _build_profanity_map(self):
        """Build a combined profanity dictionary"""
        combined = {}
        for lang, words in PROFANITY_LIST.items():
            for word in words:
                combined[word.lower()] = lang
        return combined
    
    def moderate_text(self, text: str, strict: bool = False) -> ModerationResult:
        """Moderate text content"""
        if not text:
            return ModerationResult(
                is_clean=True,
                confidence=1.0,
                suggested_action="allow"
            )
        
        text_lower = text.lower()
        reasons = []
        flagged_words = []
        
        # Check for profanity
        for word, lang in self.profanity_map.items():
            if word in text_lower:
                flagged_words.append(word)
                reasons.append(f"Profanity detected ({lang})")
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if pattern.search(text):
                reasons.append("Spam pattern detected")
                break
        
        # Check for excessive caps
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                reasons.append("Excessive capitalization")
        
        # Check for excessive repetition
        if len(text) > 5:
            char_counts = {}
            for char in text.lower():
                if char.isalnum():
                    char_counts[char] = char_counts.get(char, 0) + 1
            
            max_repetition = max(char_counts.values()) if char_counts else 0
            if max_repetition > len(text) * 0.4:
                reasons.append("Excessive character repetition")
        
        # Determine action
        is_clean = len(reasons) == 0
        confidence = 1.0 - (len(reasons) * 0.2)
        
        if len(flagged_words) > 0:
            suggested_action = "block" if strict else "warn"
        elif len(reasons) > 2:
            suggested_action = "review"
        elif len(reasons) > 0:
            suggested_action = "warn"
        else:
            suggested_action = "allow"
        
        return ModerationResult(
            is_clean=is_clean,
            confidence=max(0.0, confidence),
            reasons=reasons,
            flagged_words=flagged_words,
            suggested_action=suggested_action
        )
    
    def moderate_file(self, filename: str, file_size: int, mime_type: Optional[str] = None) -> ModerationResult:
        """Moderate file upload"""
        reasons = []
        
        # Check file size (100MB max)
        max_size = 100 * 1024 * 1024
        if file_size > max_size:
            reasons.append(f"File too large ({file_size / 1024 / 1024:.1f}MB > 100MB)")
        
        # Check suspicious extensions
        suspicious_extensions = ['.exe', '.bat', '.sh', '.cmd', '.scr', '.vbs', '.jar']
        if any(filename.lower().endswith(ext) for ext in suspicious_extensions):
            reasons.append("Suspicious file extension")
        
        # Check filename for malicious patterns
        if '..' in filename or '/' in filename or '\\' in filename:
            reasons.append("Suspicious filename pattern")
        
        is_clean = len(reasons) == 0
        
        return ModerationResult(
            is_clean=is_clean,
            confidence=1.0 if is_clean else 0.0,
            reasons=reasons,
            suggested_action="allow" if is_clean else "block"
        )
    
    def filter_text(self, text: str) -> str:
        """Filter profanity from text"""
        filtered = text
        for word in self.profanity_map.keys():
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            filtered = pattern.sub('*' * len(word), filtered)
        return filtered

# Singleton instance
_moderator_instance = None

def get_moderator() -> ContentModerator:
    """Get or create moderator instance"""
    global _moderator_instance
    if _moderator_instance is None:
        _moderator_instance = ContentModerator()
    return _moderator_instance
