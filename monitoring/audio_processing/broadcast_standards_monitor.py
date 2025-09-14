"""
Broadcast Standards Monitor - Audio Processing Module
===================================================

Professional broadcast standards compliance monitoring for the Ainflue platform.
Implements EBU R128, ITU-R BS.1770, ITU-R BS.1771 and other international
broadcast standards for enterprise audio processing workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class BroadcastStandard(Enum):
    """International broadcast standards"""
    EBU_R128 = "ebu_r128"           # European Broadcasting Union R128
    ITU_R_BS_1770 = "itu_r_bs_1770"  # ITU-R BS.1770-4 (Loudness)
    ITU_R_BS_1771 = "itu_r_bs_1771"  # ITU-R BS.1771 (Loudness Range)
    ATSC_A85 = "atsc_a85"          # ATSC A/85 (US Digital TV)
    ARIB_TR_B32 = "arib_tr_b32"    # ARIB TR-B32 (Japan Broadcasting)
    CALM_ACT = "calm_act"          # Commercial Advertisement Loudness Mitigation Act
    OP_59 = "op_59"                # EBU Tech 3341 (OP-59)
    NETFLIX = "netflix"            # Netflix Delivery Specifications
    DOLBY_DIALOGUE = "dolby_dialogue"  # Dolby Dialogue Intelligence

class ComplianceLevel(Enum):
    """Compliance assessment levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    CRITICAL = "critical"

class MeasurementType(Enum):
    """Types of broadcast measurements"""
    INTEGRATED_LOUDNESS = "integrated_loudness"      # Program loudness (LUFS)
    SHORT_TERM_LOUDNESS = "short_term_loudness"      # 3-second loudness
    MOMENTARY_LOUDNESS = "momentary_loudness"        # 400ms loudness
    LOUDNESS_RANGE = "loudness_range"                # LRA (Loudness Range)
    TRUE_PEAK = "true_peak"                          # Maximum sample peak
    GATING_BLOCKS = "gating_blocks"                  # Gating analysis
    DIALOGUE_LOUDNESS = "dialogue_loudness"          # Speech-specific loudness
    MUSIC_LOUDNESS = "music_loudness"                # Music-specific loudness

@dataclass
class BroadcastMeasurement:
    """Individual broadcast standard measurement"""
    measurement_id: str
    content_id: str
    standard: BroadcastStandard
    measurement_type: MeasurementType
    value: float
    unit: str
    target_value: float
    tolerance: float
    compliance_level: ComplianceLevel
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StandardCompliance:
    """Compliance assessment for a specific standard"""
    standard: BroadcastStandard
    content_id: str
    overall_compliance: ComplianceLevel
    measurements: List[BroadcastMeasurement]
    violations: List[str]
    recommendations: List[str]
    assessed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BroadcastStandardsReport:
    """Comprehensive broadcast standards compliance report"""
    report_id: str
    content_id: str
    standards_assessed: List[BroadcastStandard]
    compliance_results: Dict[BroadcastStandard, StandardCompliance]
    overall_rating: str
    critical_issues: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

class BroadcastStandardsMonitor:
    """
    Professional broadcast standards compliance monitoring system.
    
    Provides comprehensive monitoring and assessment of audio content
    against international broadcast standards including EBU R128,
    ITU-R recommendations, and platform-specific requirements.
    """
    
    def __init__(self) -> None:
        self.measurements: List[BroadcastMeasurement] = []
        self.compliance_reports: Dict[str, BroadcastStandardsReport] = {}
        self.standard_specifications: Dict[BroadcastStandard, Dict[str, Any]] = {}
        self.real_time_monitoring: Dict[str, Dict[str, Any]] = {}
        self._initialize_standard_specifications()
        logger.info("Broadcast Standards Monitor initialized")
    
    def _initialize_standard_specifications(self) -> None:
        """Initialize broadcast standard specifications"""
        self.standard_specifications = {
            BroadcastStandard.EBU_R128: {
                'name': 'EBU R128 - Loudness normalisation and permitted maximum level',
                'region': 'Europe',
                'target_loudness': -23.0,  # LUFS
                'loudness_tolerance': 1.0,  # LU
                'max_true_peak': -1.0,     # dBTP
                'max_loudness_range': 20.0, # LU
                'gating_threshold': -70.0,  # LUFS (absolute)
                'relative_gating': -8.0,    # LU (relative to gated loudness)
                'measurement_window': {
                    'momentary': 0.4,       # seconds
                    'short_term': 3.0,      # seconds
                    'integrated': 'program_length'
                }
            },
            BroadcastStandard.ITU_R_BS_1770: {
                'name': 'ITU-R BS.1770-4 - Algorithms to measure audio programme loudness',
                'region': 'International',
                'target_loudness': -23.0,  # LUFS (default, varies by implementation)
                'loudness_tolerance': 1.0,
                'max_true_peak': -1.0,
                'gating_threshold': -70.0,
                'relative_gating': -8.0,
                'k_weighting': True,
                'measurement_window': {
                    'momentary': 0.4,
                    'short_term': 3.0,
                    'integrated': 'program_length'
                }
            },
            BroadcastStandard.ATSC_A85: {
                'name': 'ATSC A/85 - Techniques for Establishing and Maintaining Audio Loudness',
                'region': 'North America',
                'target_loudness': -24.0,  # LKFS (equivalent to LUFS)
                'loudness_tolerance': 2.0,  # More lenient than EBU
                'max_true_peak': -2.0,     # dBTP
                'dialogue_anchor': -27.0,   # LKFS (dialogue-specific)
                'commercial_loudness': -24.0, # LKFS
                'measurement_window': {
                    'momentary': 0.4,
                    'short_term': 3.0,
                    'integrated': 'program_length'
                }
            },
            BroadcastStandard.ARIB_TR_B32: {
                'name': 'ARIB TR-B32 - Operational Guidelines for Digital Television Broadcasting',
                'region': 'Japan',
                'target_loudness': -24.0,  # LUFS
                'loudness_tolerance': 2.0,
                'max_true_peak': -1.0,
                'max_loudness_range': 15.0,
                'measurement_window': {
                    'momentary': 0.4,
                    'short_term': 3.0,
                    'integrated': 'program_length'
                }
            },
            BroadcastStandard.NETFLIX: {
                'name': 'Netflix Audio Delivery Specifications',
                'region': 'Streaming Platform',
                'target_loudness': -27.0,  # LUFS (for dialogue)
                'loudness_tolerance': 2.0,
                'max_true_peak': -2.0,     # dBTP
                'max_loudness_range': 7.0,  # LU (stricter for streaming)
                'dialogue_loudness': -27.0, # LUFS
                'music_loudness': -16.0,    # LUFS (for music programs)
                'measurement_window': {
                    'momentary': 0.4,
                    'short_term': 3.0,
                    'integrated': 'program_length'
                }
            },
            BroadcastStandard.OP_59: {
                'name': 'EBU Tech 3341 - Loudness Metering (OP-59)',
                'region': 'Europe',
                'target_loudness': -23.0,  # LUFS
                'loudness_tolerance': 0.5,  # Stricter tolerance
                'max_true_peak': -1.0,
                'max_loudness_range': 15.0,
                'measurement_precision': 0.1, # LU
                'calibration_tone': -18.0,   # dBFS for 0 LUFS
                'measurement_window': {
                    'momentary': 0.4,
                    'short_term': 3.0,
                    'integrated': 'program_length'
                }
            }
        }
    
    async def assess_broadcast_compliance(self, content_id: str, audio_data: np.ndarray,
                                        sample_rate: int, standards: List[BroadcastStandard],
                                        metadata: Optional[Dict[str, Any]] = None) -> BroadcastStandardsReport:
        """
        Assess compliance against specified broadcast standards
        
        Args:
            content_id: Content identifier
            audio_data: Audio samples as numpy array
            sample_rate: Audio sample rate
            standards: List of standards to assess against
            metadata: Additional metadata for assessment
            
        Returns:
            Comprehensive broadcast standards compliance report
        """
        report_id = f"broadcast_report_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        compliance_results = {}
        critical_issues = []
        
        try:
            for standard in standards:
                compliance = await self._assess_standard_compliance(
                    content_id, audio_data, sample_rate, standard, metadata
                )
                compliance_results[standard] = compliance
                
                if compliance.overall_compliance == ComplianceLevel.CRITICAL:
                    critical_issues.extend(compliance.violations)
            
            # Determine overall rating
            overall_rating = self._calculate_overall_rating(compliance_results)
            
            report = BroadcastStandardsReport(
                report_id=report_id,
                content_id=content_id,
                standards_assessed=standards,
                compliance_results=compliance_results,
                overall_rating=overall_rating,
                critical_issues=critical_issues
            )
            
            self.compliance_reports[content_id] = report
            logger.info(f"Broadcast compliance assessment completed for {content_id}, rating: {overall_rating}")
            
            return report
            
        except Exception as e:
            logger.error(f"Broadcast compliance assessment failed for {content_id}: {e}")
            raise
    
    async def _assess_standard_compliance(self, content_id: str, audio_data: np.ndarray,
                                        sample_rate: int, standard: BroadcastStandard,
                                        metadata: Optional[Dict[str, Any]]) -> StandardCompliance:
        """Assess compliance for a specific standard"""
        spec = self.standard_specifications[standard]
        measurements = []
        violations = []
        recommendations = []
        
        # Perform integrated loudness measurement
        integrated_measurement = await self._measure_integrated_loudness(
            content_id, audio_data, sample_rate, standard
        )
        measurements.append(integrated_measurement)
        
        # Check integrated loudness compliance
        if integrated_measurement.compliance_level in [ComplianceLevel.NON_COMPLIANT, ComplianceLevel.CRITICAL]:
            violations.append(f"Integrated loudness ({integrated_measurement.value:.1f} LUFS) outside acceptable range")
            if integrated_measurement.value > spec['target_loudness']:
                recommendations.append("Reduce overall program loudness with gain adjustment or limiting")
            else:
                recommendations.append("Increase overall program loudness with gain adjustment")
        
        # Perform true peak measurement
        true_peak_measurement = await self._measure_true_peak_broadcast(
            content_id, audio_data, sample_rate, standard
        )
        measurements.append(true_peak_measurement)
        
        if true_peak_measurement.compliance_level in [ComplianceLevel.NON_COMPLIANT, ComplianceLevel.CRITICAL]:
            violations.append(f"True peak level ({true_peak_measurement.value:.1f} dBTP) exceeds maximum")
            recommendations.append("Apply true peak limiting to prevent intersample peaks")
        
        # Perform loudness range measurement (if applicable)
        if 'max_loudness_range' in spec:
            lra_measurement = await self._measure_loudness_range_broadcast(
                content_id, audio_data, sample_rate, standard
            )
            measurements.append(lra_measurement)
            
            if lra_measurement.compliance_level in [ComplianceLevel.NON_COMPLIANT, ComplianceLevel.CRITICAL]:
                violations.append(f"Loudness range ({lra_measurement.value:.1f} LU) exceeds maximum")
                recommendations.append("Apply compression to reduce loudness variation")
        
        # Perform short-term loudness analysis
        short_term_measurement = await self._measure_short_term_loudness(
            content_id, audio_data, sample_rate, standard
        )
        measurements.append(short_term_measurement)
        
        # Determine overall compliance level
        compliance_levels = [m.compliance_level for m in measurements]
        if ComplianceLevel.CRITICAL in compliance_levels:
            overall_compliance = ComplianceLevel.CRITICAL
        elif ComplianceLevel.NON_COMPLIANT in compliance_levels:
            overall_compliance = ComplianceLevel.NON_COMPLIANT
        elif ComplianceLevel.WARNING in compliance_levels:
            overall_compliance = ComplianceLevel.WARNING
        else:
            overall_compliance = ComplianceLevel.COMPLIANT
        
        if overall_compliance == ComplianceLevel.COMPLIANT:
            recommendations.append(f"Content fully complies with {standard.value} standard")
        
        return StandardCompliance(
            standard=standard,
            content_id=content_id,
            overall_compliance=overall_compliance,
            measurements=measurements,
            violations=violations,
            recommendations=recommendations
        )
    
    async def _measure_integrated_loudness(self, content_id: str, audio_data: np.ndarray,
                                         sample_rate: int, standard: BroadcastStandard) -> BroadcastMeasurement:
        """Measure integrated loudness according to standard specifications"""
        spec = self.standard_specifications[standard]
        
        # Simulate integrated loudness measurement (ITU-R BS.1770-4 algorithm)
        # In production, use a proper loudness measurement library
        
        # Apply K-weighting filter simulation
        # Stage 1: High-shelf filter
        # Stage 2: High-pass filter
        # This is a simplified simulation
        
        # Calculate gated loudness
        block_size = int(sample_rate * 0.4)  # 400ms blocks
        overlap = int(block_size * 0.75)     # 75% overlap
        
        momentary_loudness = []
        for i in range(0, len(audio_data) - block_size, overlap):
            block = audio_data[i:i + block_size]
            # Simplified loudness calculation (should use proper K-weighting)
            mean_square = np.mean(block**2)
            if mean_square > 0:
                loudness = -0.691 + 10 * np.log10(mean_square)
                momentary_loudness.append(loudness)
        
        # Apply absolute gating (remove blocks below -70 LUFS)
        gated_blocks = [l for l in momentary_loudness if l > spec['gating_threshold']]
        
        if gated_blocks:
            # Apply relative gating
            mean_gated = np.mean(gated_blocks)
            relative_threshold = mean_gated + spec['relative_gating']
            final_gated_blocks = [l for l in gated_blocks if l > relative_threshold]
            
            if final_gated_blocks:
                integrated_loudness = np.mean(final_gated_blocks)
            else:
                integrated_loudness = spec['gating_threshold']
        else:
            integrated_loudness = spec['gating_threshold']
        
        # Assess compliance
        target = spec['target_loudness']
        tolerance = spec['loudness_tolerance']
        deviation = abs(integrated_loudness - target)
        
        if deviation <= tolerance:
            compliance_level = ComplianceLevel.COMPLIANT
        elif deviation <= tolerance * 2:
            compliance_level = ComplianceLevel.WARNING
        elif deviation <= tolerance * 3:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        else:
            compliance_level = ComplianceLevel.CRITICAL
        
        measurement = BroadcastMeasurement(
            measurement_id=f"integrated_{standard.value}_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            standard=standard,
            measurement_type=MeasurementType.INTEGRATED_LOUDNESS,
            value=integrated_loudness,
            unit="LUFS",
            target_value=target,
            tolerance=tolerance,
            compliance_level=compliance_level,
            timestamp=datetime.utcnow(),
            metadata={
                'gated_blocks': len(final_gated_blocks) if 'final_gated_blocks' in locals() else 0,
                'total_blocks': len(momentary_loudness),
                'deviation': deviation
            }
        )
        
        self.measurements.append(measurement)
        return measurement
    
    async def _measure_true_peak_broadcast(self, content_id: str, audio_data: np.ndarray,
                                         sample_rate: int, standard: BroadcastStandard) -> BroadcastMeasurement:
        """Measure true peak level according to broadcast specifications"""
        spec = self.standard_specifications[standard]
        
        # Simulate true peak measurement with oversampling
        # In production, use proper oversampling and true peak detection
        
        # Upsample by factor of 4 (minimum for true peak detection)
        # This is a simplified simulation
        upsampled_length = len(audio_data) * 4
        # Simple linear interpolation simulation
        upsampled = np.interp(
            np.linspace(0, len(audio_data) - 1, upsampled_length),
            np.arange(len(audio_data)),
            audio_data
        )
        
        # Find maximum absolute sample
        true_peak_linear = np.max(np.abs(upsampled))
        true_peak_dbtp = 20 * np.log10(true_peak_linear + 1e-10)
        
        # Assess compliance
        max_true_peak = spec['max_true_peak']
        
        if true_peak_dbtp <= max_true_peak:
            compliance_level = ComplianceLevel.COMPLIANT
        elif true_peak_dbtp <= max_true_peak + 1:
            compliance_level = ComplianceLevel.WARNING
        elif true_peak_dbtp <= max_true_peak + 3:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        else:
            compliance_level = ComplianceLevel.CRITICAL
        
        measurement = BroadcastMeasurement(
            measurement_id=f"true_peak_{standard.value}_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            standard=standard,
            measurement_type=MeasurementType.TRUE_PEAK,
            value=true_peak_dbtp,
            unit="dBTP",
            target_value=max_true_peak,
            tolerance=0.0,  # No tolerance for true peak
            compliance_level=compliance_level,
            timestamp=datetime.utcnow(),
            metadata={
                'oversampling_factor': 4,
                'linear_peak': true_peak_linear,
                'headroom': max_true_peak - true_peak_dbtp
            }
        )
        
        self.measurements.append(measurement)
        return measurement
    
    async def _measure_loudness_range_broadcast(self, content_id: str, audio_data: np.ndarray,
                                              sample_rate: int, standard: BroadcastStandard) -> BroadcastMeasurement:
        """Measure loudness range according to ITU-R BS.1771"""
        spec = self.standard_specifications[standard]
        
        # Calculate short-term loudness (3-second sliding window)
        window_size = int(sample_rate * 3.0)  # 3 seconds
        step_size = int(sample_rate * 0.1)    # 100ms steps
        
        short_term_loudness = []
        for i in range(0, len(audio_data) - window_size, step_size):
            window = audio_data[i:i + window_size]
            mean_square = np.mean(window**2)
            if mean_square > 0:
                loudness = -0.691 + 10 * np.log10(mean_square)
                short_term_loudness.append(loudness)
        
        # Apply gating (remove measurements below -70 LUFS)
        gated_measurements = [l for l in short_term_loudness if l > -70.0]
        
        if len(gated_measurements) > 0:
            # Calculate loudness range (95th percentile - 10th percentile)
            lra_value = np.percentile(gated_measurements, 95) - np.percentile(gated_measurements, 10)
        else:
            lra_value = 0.0
        
        # Assess compliance
        max_lra = spec.get('max_loudness_range', 20.0)
        
        if lra_value <= max_lra:
            compliance_level = ComplianceLevel.COMPLIANT
        elif lra_value <= max_lra * 1.2:
            compliance_level = ComplianceLevel.WARNING
        elif lra_value <= max_lra * 1.5:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        else:
            compliance_level = ComplianceLevel.CRITICAL
        
        measurement = BroadcastMeasurement(
            measurement_id=f"lra_{standard.value}_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            standard=standard,
            measurement_type=MeasurementType.LOUDNESS_RANGE,
            value=lra_value,
            unit="LU",
            target_value=max_lra,
            tolerance=0.0,
            compliance_level=compliance_level,
            timestamp=datetime.utcnow(),
            metadata={
                'short_term_measurements': len(short_term_loudness),
                'gated_measurements': len(gated_measurements),
                'percentile_95': np.percentile(gated_measurements, 95) if gated_measurements else 0,
                'percentile_10': np.percentile(gated_measurements, 10) if gated_measurements else 0
            }
        )
        
        self.measurements.append(measurement)
        return measurement
    
    async def _measure_short_term_loudness(self, content_id: str, audio_data: np.ndarray,
                                         sample_rate: int, standard: BroadcastStandard) -> BroadcastMeasurement:
        """Measure short-term loudness characteristics"""
        spec = self.standard_specifications[standard]
        
        # Calculate 3-second loudness measurements
        window_size = int(sample_rate * 3.0)
        step_size = int(sample_rate * 0.1)
        
        short_term_values = []
        for i in range(0, len(audio_data) - window_size, step_size):
            window = audio_data[i:i + window_size]
            mean_square = np.mean(window**2)
            if mean_square > 0:
                loudness = -0.691 + 10 * np.log10(mean_square)
                short_term_values.append(loudness)
        
        if short_term_values:
            max_short_term = np.max(short_term_values)
            avg_short_term = np.mean(short_term_values)
            
            # Check for excessive short-term loudness peaks
            target = spec['target_loudness']
            
            if max_short_term <= target + 3:
                compliance_level = ComplianceLevel.COMPLIANT
            elif max_short_term <= target + 6:
                compliance_level = ComplianceLevel.WARNING
            else:
                compliance_level = ComplianceLevel.NON_COMPLIANT
        else:
            max_short_term = -70.0
            avg_short_term = -70.0
            compliance_level = ComplianceLevel.WARNING
        
        measurement = BroadcastMeasurement(
            measurement_id=f"short_term_{standard.value}_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            standard=standard,
            measurement_type=MeasurementType.SHORT_TERM_LOUDNESS,
            value=max_short_term,
            unit="LUFS",
            target_value=spec['target_loudness'] + 3,  # Allow 3 LU headroom
            tolerance=3.0,
            compliance_level=compliance_level,
            timestamp=datetime.utcnow(),
            metadata={
                'max_short_term': max_short_term,
                'avg_short_term': avg_short_term,
                'measurements_count': len(short_term_values)
            }
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def _calculate_overall_rating(self, compliance_results: Dict[BroadcastStandard, StandardCompliance]) -> str:
        """Calculate overall compliance rating"""
        if not compliance_results:
            return "not_assessed"
        
        compliance_levels = [c.overall_compliance for c in compliance_results.values()]
        
        if all(level == ComplianceLevel.COMPLIANT for level in compliance_levels):
            return "fully_compliant"
        elif any(level == ComplianceLevel.CRITICAL for level in compliance_levels):
            return "critical_violations"
        elif any(level == ComplianceLevel.NON_COMPLIANT for level in compliance_levels):
            return "non_compliant"
        elif any(level == ComplianceLevel.WARNING for level in compliance_levels):
            return "minor_issues"
        else:
            return "unknown"
    
    def get_compliance_report(self, content_id: str) -> Optional[BroadcastStandardsReport]:
        """Get compliance report for specific content"""
        return self.compliance_reports.get(content_id)
    
    def get_compliance_summary(self, standard: BroadcastStandard, days: int = 7) -> Dict[str, Any]:
        """Get compliance summary for specific standard over time"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get recent measurements for the standard
        recent_measurements = [
            m for m in self.measurements 
            if m.standard == standard and m.timestamp >= cutoff_time
        ]
        
        if not recent_measurements:
            return {"message": f"No measurements for {standard.value} in last {days} days"}
        
        # Calculate compliance statistics
        total_measurements = len(recent_measurements)
        compliant_count = len([m for m in recent_measurements if m.compliance_level == ComplianceLevel.COMPLIANT])
        warning_count = len([m for m in recent_measurements if m.compliance_level == ComplianceLevel.WARNING])
        non_compliant_count = len([m for m in recent_measurements if m.compliance_level == ComplianceLevel.NON_COMPLIANT])
        critical_count = len([m for m in recent_measurements if m.compliance_level == ComplianceLevel.CRITICAL])
        
        compliance_rate = compliant_count / total_measurements
        
        # Get measurement type breakdown
        type_breakdown = {}
        for measurement_type in MeasurementType:
            type_measurements = [m for m in recent_measurements if m.measurement_type == measurement_type]
            if type_measurements:
                type_compliance_rate = len([m for m in type_measurements if m.compliance_level == ComplianceLevel.COMPLIANT]) / len(type_measurements)
                type_breakdown[measurement_type.value] = {
                    'count': len(type_measurements),
                    'compliance_rate': round(type_compliance_rate, 3)
                }
        
        return {
            'standard': standard.value,
            'period_days': days,
            'total_measurements': total_measurements,
            'compliance_breakdown': {
                'compliant': compliant_count,
                'warning': warning_count,
                'non_compliant': non_compliant_count,
                'critical': critical_count
            },
            'overall_compliance_rate': round(compliance_rate, 3),
            'measurement_type_breakdown': type_breakdown,
            'standard_specification': self.standard_specifications[standard]
        }

# Global broadcast standards monitor instance
broadcast_standards_monitor = BroadcastStandardsMonitor()

# Export main components
__all__ = [
    'BroadcastStandardsMonitor',
    'BroadcastMeasurement',
    'StandardCompliance',
    'BroadcastStandardsReport',
    'BroadcastStandard',
    'ComplianceLevel',
    'MeasurementType',
    'broadcast_standards_monitor'
]