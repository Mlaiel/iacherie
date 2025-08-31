"""📋 Quality Compliance Engine - Platform Compliance System

Advanced compliance checking system for audio content across multiple
platforms and standards, ensuring content meets platform-specific requirements.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
import hashlib
from pathlib import Path

from .standards import QualityProfile, QualityLevel
from .metrics import QualityReport
from .validator import ValidationResult

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance severity levels"""    CRITICAL = "critical"       # Must fix before submission
    WARNING = "warning"         # Should fix for best results
    RECOMMENDATION = "recommendation"  # Optional improvements
    INFO = "info"              # Informational only


class PlatformType(Enum):
    """Supported platform types"""    STREAMING = "streaming"     # Spotify, Apple Music, etc.
    VIDEO = "video"            # YouTube, TikTok, Instagram
    BROADCAST = "broadcast"     # Radio, TV
    GAMING = "gaming"          # Games, VR applications
    PODCAST = "podcast"        # Podcast platforms
    SOCIAL = "social"          # Social media platforms
    CUSTOM = "custom"          # Custom platform requirements


@dataclass
class ComplianceRule:
    """Individual compliance rule"""    rule_id: str
    name: str
    description: str
    platform: str
    category: str
    level: ComplianceLevel
    check_function: str  # Function name to execute
    parameters: Dict[str, Any] = field(default_factory=dict)
    threshold: Optional[float] = None
    tolerance: float = 0.0
    error_message: str = ""
    fix_suggestion: str = ""
    documentation_url: str = ""
    priority: int = 1  # 1 = highest priority


@dataclass
class ComplianceViolation:
    """Compliance rule violation"""    rule: ComplianceRule
    current_value: Optional[Union[float, str, bool]]
    expected_value: Optional[Union[float, str, bool]]
    severity_score: float  # 0.0 to 1.0
    message: str
    fix_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceReport:
    """Complete compliance assessment report"""    platform: str
    audio_file: str
    total_rules_checked: int
    violations: List[ComplianceViolation]
    warnings: List[ComplianceViolation]
    recommendations: List[ComplianceViolation]
    overall_score: float  # 0.0 to 1.0
    compliance_status: str  # "compliant", "warnings", "violations"
    can_submit: bool
    processing_time: float
    checked_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def critical_violations(self) -> List[ComplianceViolation]:
        """Get critical violations"""        return [v for v in self.violations if v.rule.level == ComplianceLevel.CRITICAL]

    @property
    def has_critical_violations(self) -> bool:
        """Check if has critical violations"""        return len(self.critical_violations) > 0


class ComplianceRuleEngine:
    """    📋 Compliance Rule Engine
    
    Executes compliance checks and generates violation reports
    """    def __init__(self):
        self.custom_rules: Dict[str, ComplianceRule] = {}
        self.rule_execution_stats: Dict[str, Dict[str, Any]] = {}

    async def check_loudness_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check loudness compliance"""        
        target_lufs = rule.parameters.get('target_lufs', -14.0)
        tolerance = rule.tolerance or 1.0
        
        # Find loudness metrics
        current_lufs = None
        for score in quality_report.metrics.scores:
            if 'lufs' in score.name.lower() or 'loudness' in score.name.lower():
                current_lufs = score.value
                break
        
        if current_lufs is None:
            return None
        
        # Check compliance
        difference = abs(current_lufs - target_lufs)
        
        if difference > tolerance:
            severity = min(difference / (tolerance * 2), 1.0)
            
            return ComplianceViolation(
                rule=rule,
                current_value=current_lufs,
                expected_value=target_lufs,
                severity_score=severity,
                message=f"Loudness {current_lufs:.1f} LUFS exceeds tolerance of ±{tolerance} LUFS from target {target_lufs} LUFS",
                fix_suggestions=[
                    f"Adjust audio loudness to {target_lufs} LUFS",
                    f"Use loudness normalization to meet target",
                    f"Check if content requires dynamic range preservation"
                ]
            )
        
        return None

    async def check_dynamic_range_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check dynamic range compliance"""        
        min_dr = rule.parameters.get('min_dynamic_range', 6.0)
        max_dr = rule.parameters.get('max_dynamic_range', None)
        
        # Find dynamic range metrics
        current_dr = None
        for score in quality_report.metrics.scores:
            if 'dynamic_range' in score.name.lower() or 'dr' in score.name.lower():
                current_dr = score.value
                break
        
        if current_dr is None:
            return None
        
        violations = []
        
        # Check minimum dynamic range
        if current_dr < min_dr:
            severity = (min_dr - current_dr) / min_dr
            return ComplianceViolation(
                rule=rule,
                current_value=current_dr,
                expected_value=f">= {min_dr}",
                severity_score=severity,
                message=f"Dynamic range {current_dr:.1f} dB is below minimum {min_dr} dB",
                fix_suggestions=[
                    "Reduce compression ratio",
                    "Increase dynamic range in mastering",
                    "Avoid over-limiting"
                ]
            )
        
        # Check maximum dynamic range if specified
        if max_dr and current_dr > max_dr:
            severity = (current_dr - max_dr) / max_dr
            return ComplianceViolation(
                rule=rule,
                current_value=current_dr,
                expected_value=f"<= {max_dr}",
                severity_score=severity,
                message=f"Dynamic range {current_dr:.1f} dB exceeds maximum {max_dr} dB",
                fix_suggestions=[
                    "Apply light compression",
                    "Normalize volume levels",
                    "Check for excessive dynamics"
                ]
            )
        
        return None

    async def check_peak_level_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check peak level compliance"""        
        max_peak_db = rule.parameters.get('max_peak_db', -1.0)
        
        # Find peak level metrics
        current_peak = None
        for score in quality_report.metrics.scores:
            if 'peak' in score.name.lower():
                # Convert to dB if needed
                if score.value > 1.0:  # Already in dB
                    current_peak = score.value
                else:  # Linear value, convert to dB
                    current_peak = 20 * np.log10(max(score.value, 1e-10))
                break
        
        if current_peak is None:
            return None
        
        if current_peak > max_peak_db:
            severity = min((current_peak - max_peak_db) / abs(max_peak_db), 1.0)
            
            return ComplianceViolation(
                rule=rule,
                current_value=current_peak,
                expected_value=f"<= {max_peak_db}",
                severity_score=severity,
                message=f"Peak level {current_peak:.1f} dB exceeds maximum {max_peak_db} dB",
                fix_suggestions=[
                    "Apply peak limiting",
                    "Reduce overall volume",
                    "Check for clipping",
                    "Leave headroom for encoding"
                ]
            )
        
        return None

    async def check_frequency_response_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check frequency response compliance"""        
        min_freq = rule.parameters.get('min_frequency', 20)
        max_freq = rule.parameters.get('max_frequency', 20000)
        
        # This would need spectral analysis data from quality report
        # For now, return None (would be implemented with actual spectral data)
        return None

    async def check_file_format_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check file format compliance"""        
        allowed_formats = rule.parameters.get('allowed_formats', ['wav', 'flac', 'mp3'])
        max_bitrate = rule.parameters.get('max_bitrate', None)
        min_sample_rate = rule.parameters.get('min_sample_rate', 44100)
        
        # Get format info from metadata
        metadata = quality_report.metadata
        
        file_format = metadata.get('format', '').lower()
        bitrate = metadata.get('bitrate', 0)
        sample_rate = metadata.get('sample_rate', 0)
        
        violations = []
        
        # Check format
        if file_format and file_format not in [f.lower() for f in allowed_formats]:
            return ComplianceViolation(
                rule=rule,
                current_value=file_format,
                expected_value=f"One of: {', '.join(allowed_formats)}",
                severity_score=1.0,
                message=f"File format '{file_format}' not allowed. Allowed formats: {', '.join(allowed_formats)}",
                fix_suggestions=[
                    f"Convert to one of: {', '.join(allowed_formats)}",
                    "Use lossless format for best quality",
                    "Check platform-specific requirements"
                ]
            )
        
        # Check bitrate
        if max_bitrate and bitrate > max_bitrate:
            severity = min((bitrate - max_bitrate) / max_bitrate, 1.0)
            return ComplianceViolation(
                rule=rule,
                current_value=bitrate,
                expected_value=f"<= {max_bitrate}",
                severity_score=severity,
                message=f"Bitrate {bitrate} kbps exceeds maximum {max_bitrate} kbps",
                fix_suggestions=[
                    f"Reduce bitrate to {max_bitrate} kbps or lower",
                    "Use appropriate quality settings",
                    "Consider file size limitations"
                ]
            )
        
        # Check sample rate
        if sample_rate < min_sample_rate:
            severity = (min_sample_rate - sample_rate) / min_sample_rate
            return ComplianceViolation(
                rule=rule,
                current_value=sample_rate,
                expected_value=f">= {min_sample_rate}",
                severity_score=severity,
                message=f"Sample rate {sample_rate} Hz is below minimum {min_sample_rate} Hz",
                fix_suggestions=[
                    f"Increase sample rate to at least {min_sample_rate} Hz",
                    "Use standard sample rates (44.1kHz, 48kHz, 96kHz)",
                    "Check if upsampling is appropriate"
                ]
            )
        
        return None

    async def check_duration_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check audio duration compliance"""        
        min_duration = rule.parameters.get('min_duration', 0)
        max_duration = rule.parameters.get('max_duration', float('inf'))
        
        duration = quality_report.metadata.get('duration', 0)
        
        if duration < min_duration:
            severity = (min_duration - duration) / max(min_duration, 1)
            return ComplianceViolation(
                rule=rule,
                current_value=duration,
                expected_value=f">= {min_duration}s",
                severity_score=severity,
                message=f"Duration {duration:.1f}s is below minimum {min_duration}s",
                fix_suggestions=[
                    f"Extend audio to at least {min_duration} seconds",
                    "Add silence padding if appropriate",
                    "Check platform minimum requirements"
                ]
            )
        
        if duration > max_duration:
            severity = min((duration - max_duration) / max_duration, 1.0)
            return ComplianceViolation(
                rule=rule,
                current_value=duration,
                expected_value=f"<= {max_duration}s",
                severity_score=severity,
                message=f"Duration {duration:.1f}s exceeds maximum {max_duration}s",
                fix_suggestions=[
                    f"Trim audio to {max_duration} seconds or less",
                    "Split into multiple parts if needed",
                    "Check platform limitations"
                ]
            )
        
        return None

    async def check_silence_compliance(
        self,
        quality_report: QualityReport,
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check silence compliance"""        
        max_leading_silence = rule.parameters.get('max_leading_silence', 2.0)
        max_trailing_silence = rule.parameters.get('max_trailing_silence', 2.0)
        max_internal_silence = rule.parameters.get('max_internal_silence', 5.0)
        
        # Would need silence detection data from quality report
        # For now, return None (would be implemented with actual silence detection)
        return None

    def add_custom_rule(self, rule: ComplianceRule):
        """Add custom compliance rule"""        self.custom_rules[rule.rule_id] = rule
        logger.info(f"Added custom compliance rule: {rule.rule_id}")

    async def execute_rule(
        self,
        rule: ComplianceRule,
        quality_report: QualityReport
    ) -> Optional[ComplianceViolation]:
        """Execute a compliance rule"""        
        start_time = datetime.now()
        
        try:
            # Get the check function
            check_function = getattr(self, rule.check_function, None)
            if not check_function:
                logger.error(f"Check function '{rule.check_function}' not found for rule {rule.rule_id}")
                return None
            
            # Execute the check
            violation = await check_function(quality_report, rule)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if rule.rule_id not in self.rule_execution_stats:
                self.rule_execution_stats[rule.rule_id] = {
                    'executions': 0,
                    'violations': 0,
                    'total_time': 0.0,
                    'last_executed': None
                }
            
            stats = self.rule_execution_stats[rule.rule_id]
            stats['executions'] += 1
            stats['total_time'] += processing_time
            stats['last_executed'] = datetime.now()
            
            if violation:
                stats['violations'] += 1
            
            return violation
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.rule_id}: {e}")
            return None


class PlatformComplianceManager:
    """    📋 Platform Compliance Manager
    
    Manages compliance rules and standards for different platforms
    """    def __init__(self):
        self.platform_rules: Dict[str, List[ComplianceRule]] = {}
        self.rule_engine = ComplianceRuleEngine()
        self.compliance_history: List[ComplianceReport] = []
        
        # Initialize platform rules
        self._initialize_platform_rules()
        
        logger.info(f"PlatformComplianceManager initialized with {len(self.platform_rules)} platform rule sets")

    def _initialize_platform_rules(self):
        """Initialize compliance rules for different platforms"""        
        # Spotify compliance rules
        spotify_rules = [
            ComplianceRule(
                rule_id="spotify_loudness",
                name="Spotify Loudness",
                description="Audio should be normalized to -14 LUFS",
                platform="spotify",
                category="loudness",
                level=ComplianceLevel.WARNING,
                check_function="check_loudness_compliance",
                parameters={"target_lufs": -14.0},
                tolerance=1.0,
                error_message="Loudness not optimized for Spotify",
                fix_suggestion="Normalize to -14 LUFS for optimal Spotify playback",
                documentation_url="https://artists.spotify.com/help/article/loudness-normalization"
            ),
            ComplianceRule(
                rule_id="spotify_peak",
                name="Spotify Peak Level",
                description="Peak level should not exceed -1 dBTP",
                platform="spotify",
                category="levels",
                level=ComplianceLevel.CRITICAL,
                check_function="check_peak_level_compliance",
                parameters={"max_peak_db": -1.0},
                error_message="Peak level too high",
                fix_suggestion="Apply peak limiting to prevent clipping"
            ),
            ComplianceRule(
                rule_id="spotify_format",
                name="Spotify Format",
                description="Recommended formats and quality",
                platform="spotify",
                category="format",
                level=ComplianceLevel.RECOMMENDATION,
                check_function="check_file_format_compliance",
                parameters={
                    "allowed_formats": ["wav", "flac", "mp3"],
                    "min_sample_rate": 44100,
                    "max_bitrate": 320
                }
            )
        ]
        
        # YouTube compliance rules
        youtube_rules = [
            ComplianceRule(
                rule_id="youtube_loudness",
                name="YouTube Loudness",
                description="Audio should be normalized to -14 LUFS",
                platform="youtube",
                category="loudness",
                level=ComplianceLevel.WARNING,
                check_function="check_loudness_compliance",
                parameters={"target_lufs": -14.0},
                tolerance=1.0
            ),
            ComplianceRule(
                rule_id="youtube_peak",
                name="YouTube Peak Level",
                description="Peak level should not exceed -1 dBTP",
                platform="youtube",
                category="levels",
                level=ComplianceLevel.CRITICAL,
                check_function="check_peak_level_compliance",
                parameters={"max_peak_db": -1.0}
            ),
            ComplianceRule(
                rule_id="youtube_duration",
                name="YouTube Duration",
                description="Standard video length limits",
                platform="youtube",
                category="duration",
                level=ComplianceLevel.WARNING,
                check_function="check_duration_compliance",
                parameters={"max_duration": 43200}  # 12 hours
            )
        ]
        
        # TikTok compliance rules
        tiktok_rules = [
            ComplianceRule(
                rule_id="tiktok_loudness",
                name="TikTok Loudness",
                description="Audio should be normalized to -16 LUFS for mobile",
                platform="tiktok",
                category="loudness",
                level=ComplianceLevel.WARNING,
                check_function="check_loudness_compliance",
                parameters={"target_lufs": -16.0},
                tolerance=1.5
            ),
            ComplianceRule(
                rule_id="tiktok_duration",
                name="TikTok Duration",
                description="Maximum video duration",
                platform="tiktok",
                category="duration",
                level=ComplianceLevel.CRITICAL,
                check_function="check_duration_compliance",
                parameters={"min_duration": 1, "max_duration": 600}  # 1s to 10 minutes
            ),
            ComplianceRule(
                rule_id="tiktok_peak",
                name="TikTok Peak Level",
                description="Peak level for mobile playback",
                platform="tiktok",
                category="levels",
                level=ComplianceLevel.WARNING,
                check_function="check_peak_level_compliance",
                parameters={"max_peak_db": -2.0}  # More conservative for mobile
            )
        ]
        
        # Apple Music compliance rules
        apple_music_rules = [
            ComplianceRule(
                rule_id="apple_music_loudness",
                name="Apple Music Loudness",
                description="Audio should be normalized to -16 LUFS",
                platform="apple_music",
                category="loudness",
                level=ComplianceLevel.WARNING,
                check_function="check_loudness_compliance",
                parameters={"target_lufs": -16.0},
                tolerance=1.0
            ),
            ComplianceRule(
                rule_id="apple_music_format",
                name="Apple Music Format",
                description="High-quality format requirements",
                platform="apple_music",
                category="format",
                level=ComplianceLevel.RECOMMENDATION,
                check_function="check_file_format_compliance",
                parameters={
                    "allowed_formats": ["wav", "flac", "alac"],
                    "min_sample_rate": 44100
                }
            )
        ]
        
        # Podcast compliance rules
        podcast_rules = [
            ComplianceRule(
                rule_id="podcast_loudness",
                name="Podcast Loudness",
                description="Podcast audio should be around -16 to -20 LUFS",
                platform="podcast",
                category="loudness",
                level=ComplianceLevel.WARNING,
                check_function="check_loudness_compliance",
                parameters={"target_lufs": -18.0},
                tolerance=2.0
            ),
            ComplianceRule(
                rule_id="podcast_format",
                name="Podcast Format",
                description="Podcast format requirements",
                platform="podcast",
                category="format",
                level=ComplianceLevel.WARNING,
                check_function="check_file_format_compliance",
                parameters={
                    "allowed_formats": ["mp3", "wav"],
                    "max_bitrate": 128,
                    "min_sample_rate": 22050
                }
            ),
            ComplianceRule(
                rule_id="podcast_dynamic_range",
                name="Podcast Dynamic Range",
                description="Maintain good dynamic range for spoken content",
                platform="podcast",
                category="dynamics",
                level=ComplianceLevel.RECOMMENDATION,
                check_function="check_dynamic_range_compliance",
                parameters={"min_dynamic_range": 4.0, "max_dynamic_range": 20.0}
            )
        ]
        
        # Store platform rules
        self.platform_rules["spotify"] = spotify_rules
        self.platform_rules["youtube"] = youtube_rules
        self.platform_rules["tiktok"] = tiktok_rules
        self.platform_rules["apple_music"] = apple_music_rules
        self.platform_rules["podcast"] = podcast_rules

    async def check_compliance(
        self,
        platform: str,
        quality_report: QualityReport,
        audio_file: str = ""
    ) -> ComplianceReport:
        """Check compliance for a specific platform"""        
        start_time = datetime.now()
        
        if platform.lower() not in self.platform_rules:
            logger.error(f"Unknown platform: {platform}")
            return ComplianceReport(
                platform=platform,
                audio_file=audio_file,
                total_rules_checked=0,
                violations=[],
                warnings=[],
                recommendations=[],
                overall_score=0.0,
                compliance_status="unknown_platform",
                can_submit=False,
                processing_time=0.0
            )
        
        rules = self.platform_rules[platform.lower()]
        violations = []
        warnings = []
        recommendations = []
        
        # Execute all rules
        for rule in rules:
            try:
                violation = await self.rule_engine.execute_rule(rule, quality_report)
                
                if violation:
                    if rule.level == ComplianceLevel.CRITICAL:
                        violations.append(violation)
                    elif rule.level == ComplianceLevel.WARNING:
                        warnings.append(violation)
                    elif rule.level == ComplianceLevel.RECOMMENDATION:
                        recommendations.append(violation)
                    
                    logger.info(f"Compliance violation found: {rule.rule_id} - {violation.message}")
            
            except Exception as e:
                logger.error(f"Error checking rule {rule.rule_id}: {e}")
                continue
        
        # Calculate overall compliance score
        total_violations = len(violations) + len(warnings) + len(recommendations)
        total_rules = len(rules)
        
        if total_rules > 0:
            # Weight violations by severity
            violation_penalty = len(violations) * 1.0
            warning_penalty = len(warnings) * 0.5
            recommendation_penalty = len(recommendations) * 0.2
            
            total_penalty = violation_penalty + warning_penalty + recommendation_penalty
            max_penalty = total_rules * 1.0
            
            overall_score = max(0.0, 1.0 - (total_penalty / max_penalty))
        else:
            overall_score = 1.0
        
        # Determine compliance status
        if violations:
            compliance_status = "violations"
            can_submit = False
        elif warnings:
            compliance_status = "warnings"
            can_submit = True  # Can submit but with warnings
        elif recommendations:
            compliance_status = "recommendations"
            can_submit = True
        else:
            compliance_status = "compliant"
            can_submit = True
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        report = ComplianceReport(
            platform=platform,
            audio_file=audio_file,
            total_rules_checked=total_rules,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            overall_score=overall_score,
            compliance_status=compliance_status,
            can_submit=can_submit,
            processing_time=processing_time,
            metadata={
                'rules_executed': len(rules),
                'platform_type': self._get_platform_type(platform),
                'check_timestamp': datetime.now().isoformat()
            }
        )
        
        # Store in history
        self.compliance_history.append(report)
        
        logger.info(f"Compliance check completed for {platform}: {compliance_status} (score: {overall_score:.2f})")
        
        return report

    def _get_platform_type(self, platform: str) -> str:
        """Get platform type category"""        platform_types = {
            'spotify': PlatformType.STREAMING.value,
            'apple_music': PlatformType.STREAMING.value,
            'youtube': PlatformType.VIDEO.value,
            'tiktok': PlatformType.VIDEO.value,
            'podcast': PlatformType.PODCAST.value
        }
        
        return platform_types.get(platform.lower(), PlatformType.CUSTOM.value)

    async def check_multi_platform_compliance(
        self,
        platforms: List[str],
        quality_report: QualityReport,
        audio_file: str = ""
    ) -> Dict[str, ComplianceReport]:
        """Check compliance for multiple platforms"""        
        reports = {}
        
        for platform in platforms:
            try:
                report = await self.check_compliance(platform, quality_report, audio_file)
                reports[platform] = report
            except Exception as e:
                logger.error(f"Error checking compliance for {platform}: {e}")
                continue
        
        return reports

    def get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific requirements"""        
        if platform.lower() not in self.platform_rules:
            return {}
        
        rules = self.platform_rules[platform.lower()]
        requirements = {}
        
        for rule in rules:
            requirements[rule.rule_id] = {
                'name': rule.name,
                'description': rule.description,
                'category': rule.category,
                'level': rule.level.value,
                'parameters': rule.parameters,
                'threshold': rule.threshold,
                'tolerance': rule.tolerance
            }
        
        return requirements

    def add_platform_rule(self, platform: str, rule: ComplianceRule):
        """Add rule to platform"""        
        if platform.lower() not in self.platform_rules:
            self.platform_rules[platform.lower()] = []
        
        self.platform_rules[platform.lower()].append(rule)
        logger.info(f"Added rule {rule.rule_id} to platform {platform}")

    def get_compliance_statistics(self, platform: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get compliance statistics"""        
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter reports
        reports = [
            r for r in self.compliance_history 
            if r.checked_at >= cutoff_time and (platform is None or r.platform.lower() == platform.lower())
        ]
        
        if not reports:
            return {'no_data': True}
        
        total_checks = len(reports)
        compliant_checks = len([r for r in reports if r.compliance_status == "compliant"])
        
        # Calculate statistics
        avg_score = sum(r.overall_score for r in reports) / total_checks
        avg_processing_time = sum(r.processing_time for r in reports) / total_checks
        
        # Violation statistics
        total_violations = sum(len(r.violations) for r in reports)
        total_warnings = sum(len(r.warnings) for r in reports)
        total_recommendations = sum(len(r.recommendations) for r in reports)
        
        # Most common violations
        violation_counts = {}
        for report in reports:
            for violation in report.violations + report.warnings + report.recommendations:
                rule_id = violation.rule.rule_id
                violation_counts[rule_id] = violation_counts.get(rule_id, 0) + 1
        
        most_common_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_checks': total_checks,
            'compliant_checks': compliant_checks,
            'compliance_rate': compliant_checks / total_checks,
            'average_score': avg_score,
            'average_processing_time': avg_processing_time,
            'total_violations': total_violations,
            'total_warnings': total_warnings,
            'total_recommendations': total_recommendations,
            'most_common_violations': most_common_violations,
            'rule_execution_stats': self.rule_engine.rule_execution_stats
        }

    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""        return list(self.platform_rules.keys())

    def export_compliance_report(self, report: ComplianceReport, format: str = "json") -> str:
        """Export compliance report to specified format"""        
        if format.lower() == "json":
            # Convert to JSON-serializable format
            report_dict = {
                'platform': report.platform,
                'audio_file': report.audio_file,
                'total_rules_checked': report.total_rules_checked,
                'overall_score': report.overall_score,
                'compliance_status': report.compliance_status,
                'can_submit': report.can_submit,
                'processing_time': report.processing_time,
                'checked_at': report.checked_at.isoformat(),
                'violations': [
                    {
                        'rule_id': v.rule.rule_id,
                        'rule_name': v.rule.name,
                        'level': v.rule.level.value,
                        'current_value': v.current_value,
                        'expected_value': v.expected_value,
                        'severity_score': v.severity_score,
                        'message': v.message,
                        'fix_suggestions': v.fix_suggestions
                    }
                    for v in report.violations
                ],
                'warnings': [
                    {
                        'rule_id': v.rule.rule_id,
                        'rule_name': v.rule.name,
                        'level': v.rule.level.value,
                        'current_value': v.current_value,
                        'expected_value': v.expected_value,
                        'severity_score': v.severity_score,
                        'message': v.message,
                        'fix_suggestions': v.fix_suggestions
                    }
                    for v in report.warnings
                ],
                'recommendations': [
                    {
                        'rule_id': v.rule.rule_id,
                        'rule_name': v.rule.name,
                        'level': v.rule.level.value,
                        'current_value': v.current_value,
                        'expected_value': v.expected_value,
                        'severity_score': v.severity_score,
                        'message': v.message,
                        'fix_suggestions': v.fix_suggestions
                    }
                    for v in report.recommendations
                ]
            }
            
            return json.dumps(report_dict, indent=2, ensure_ascii=False)
        
        else:
            return f"Unsupported format: {format}"
