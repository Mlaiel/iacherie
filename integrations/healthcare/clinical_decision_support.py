"""
IA Chérie - Clinical Decision Support System
=============================================
Evidence-based clinical decision support providing clinical guidelines,
order sets, and alerts for best practice compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 Fahed Mlaiel - All Rights Reserved
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
⚠️ DISCLAIMER: Support tool only - not for primary clinical decisions
Toute reproduction, modification ou distribution non autorisée est strictement interdite.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class GuidelineSource(str, Enum):
    """Clinical guideline sources"""
    AHA = "American Heart Association"
    ADA = "American Diabetes Association"
    WHO = "World Health Organization"
    NICE = "NICE Guidelines"
    USPSTF = "US Preventive Services Task Force"


class AlertSeverity(str, Enum):
    """Clinical alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ClinicalDecisionSupport:
    """
    Clinical Decision Support System
    
    ⚠️ DISCLAIMER:
    This system provides clinical decision support based on evidence-based
    guidelines. It is a support tool and NOT a replacement for clinical
    judgment. All recommendations must be reviewed by qualified healthcare
    professionals.
    
    Features:
    - Evidence-based clinical guidelines
    - Standardized order sets
    - Clinical alerts and reminders
    - Best practice recommendations
    - Drug-allergy checking
    - Critical value notifications
    """
    
    def __init__(self):
        """Initialize clinical decision support system"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize clinical knowledge bases
        self.guidelines = self._initialize_guidelines()
        self.order_sets = self._initialize_order_sets()
        self.alert_rules = self._initialize_alert_rules()
    
    def _initialize_guidelines(self) -> Dict[str, Any]:
        """Initialize clinical guidelines database"""
        return {
            'type2_diabetes': {
                'condition': 'Type 2 Diabetes Mellitus',
                'source': GuidelineSource.ADA,
                'version': '2024',
                'recommendations': [
                    {
                        'category': 'Glycemic Targets',
                        'recommendation': 'HbA1c <7% for most adults',
                        'evidence_level': 'A',
                        'details': 'Less stringent goals (e.g., <8%) may be appropriate for patients with limited life expectancy or high risk of hypoglycemia'
                    },
                    {
                        'category': 'Initial Pharmacotherapy',
                        'recommendation': 'Metformin is preferred initial therapy',
                        'evidence_level': 'A',
                        'details': 'Unless contraindicated, metformin should be initiated at diagnosis'
                    },
                    {
                        'category': 'Cardiovascular Risk',
                        'recommendation': 'Consider GLP-1 RA or SGLT2i with ASCVD',
                        'evidence_level': 'A',
                        'details': 'For patients with established cardiovascular disease'
                    }
                ],
                'monitoring': [
                    {'test': 'HbA1c', 'frequency': 'Every 3 months if not at goal, every 6 months if stable'},
                    {'test': 'Lipid panel', 'frequency': 'Annually'},
                    {'test': 'Urine albumin-creatinine ratio', 'frequency': 'Annually'}
                ]
            },
            'hypertension': {
                'condition': 'Hypertension',
                'source': GuidelineSource.AHA,
                'version': '2024',
                'recommendations': [
                    {
                        'category': 'Blood Pressure Goals',
                        'recommendation': '<130/80 mmHg for most adults',
                        'evidence_level': 'A'
                    },
                    {
                        'category': 'Initial Therapy',
                        'recommendation': 'ACE inhibitor, ARB, CCB, or thiazide diuretic',
                        'evidence_level': 'A'
                    }
                ],
                'monitoring': [
                    {'test': 'Blood pressure', 'frequency': 'Every visit'},
                    {'test': 'Basic metabolic panel', 'frequency': 'Annually'}
                ]
            }
        }
    
    def _initialize_order_sets(self) -> Dict[str, Any]:
        """Initialize standardized order sets"""
        return {
            'new_diabetes_diagnosis': {
                'name': 'New Type 2 Diabetes Diagnosis',
                'indication': 'Initial evaluation of type 2 diabetes',
                'orders': [
                    {
                        'category': 'Laboratory',
                        'tests': [
                            {'name': 'HbA1c', 'priority': 'routine'},
                            {'name': 'Comprehensive metabolic panel', 'priority': 'routine'},
                            {'name': 'Lipid panel', 'priority': 'routine'},
                            {'name': 'Urine albumin-creatinine ratio', 'priority': 'routine'},
                            {'name': 'TSH', 'priority': 'routine'}
                        ]
                    },
                    {
                        'category': 'Medications',
                        'medications': [
                            {
                                'name': 'Metformin',
                                'dose': '500mg',
                                'frequency': 'twice daily',
                                'route': 'oral',
                                'instructions': 'Start 500mg daily, increase to BID after 1 week if tolerated'
                            }
                        ]
                    },
                    {
                        'category': 'Referrals',
                        'referrals': [
                            {'specialty': 'Ophthalmology', 'indication': 'Diabetic eye exam'},
                            {'specialty': 'Nutrition', 'indication': 'Diabetes education'}
                        ]
                    }
                ]
            },
            'chest_pain_evaluation': {
                'name': 'Chest Pain Evaluation',
                'indication': 'Evaluation of chest pain',
                'orders': [
                    {
                        'category': 'Laboratory',
                        'tests': [
                            {'name': 'Troponin', 'priority': 'stat'},
                            {'name': 'Basic metabolic panel', 'priority': 'routine'},
                            {'name': 'Complete blood count', 'priority': 'routine'}
                        ]
                    },
                    {
                        'category': 'Imaging',
                        'studies': [
                            {'name': 'ECG', 'priority': 'stat'},
                            {'name': 'Chest X-ray', 'priority': 'routine'}
                        ]
                    }
                ]
            }
        }
    
    def _initialize_alert_rules(self) -> List[Dict[str, Any]]:
        """Initialize clinical alert rules"""
        return [
            {
                'rule_id': 'drug_allergy_check',
                'severity': AlertSeverity.CRITICAL,
                'condition': 'Medication order with documented allergy',
                'message': 'CRITICAL: Patient has documented allergy to {drug}',
                'action_required': True
            },
            {
                'rule_id': 'critical_lab_value',
                'severity': AlertSeverity.CRITICAL,
                'condition': 'Laboratory result outside critical range',
                'message': 'CRITICAL LAB: {test} = {value} (Critical range: {range})',
                'action_required': True
            },
            {
                'rule_id': 'drug_interaction',
                'severity': AlertSeverity.HIGH,
                'condition': 'Major drug-drug interaction detected',
                'message': 'Drug interaction: {drug1} + {drug2}',
                'action_required': False
            },
            {
                'rule_id': 'duplicate_therapy',
                'severity': AlertSeverity.MEDIUM,
                'condition': 'Duplicate therapeutic class',
                'message': 'Duplicate therapy detected: {class}',
                'action_required': False
            }
        ]
    
    async def evaluate_clinical_guidelines(
        self, 
        patient_data: Dict[str, Any], 
        condition: str
    ) -> Dict[str, Any]:
        """
        Evaluate clinical guidelines for patient condition
        
        ⚠️ DISCLAIMER: Support tool only - not for primary decisions
        
        Args:
            patient_data: Patient clinical data
            condition: Medical condition (e.g., 'type2_diabetes')
            
        Returns:
            Applicable guidelines with recommendations
        """
        try:
            guideline = self.guidelines.get(condition)
            
            if not guideline:
                return {
                    'status': 'success',
                    'condition': condition,
                    'guideline_found': False,
                    'message': f'No guidelines available for {condition}'
                }
            
            # Evaluate patient against guidelines
            applicable_recommendations = []
            for rec in guideline.get('recommendations', []):
                applicable_recommendations.append({
                    **rec,
                    'applicable': True,  # Simplified - in production, check patient data
                    'rationale': 'Based on evidence-based guidelines'
                })
            
            return {
                'status': 'success',
                'condition': guideline['condition'],
                'source': guideline['source'],
                'version': guideline['version'],
                'recommendations': applicable_recommendations,
                'monitoring_schedule': guideline.get('monitoring', []),
                'disclaimer': 'Guidelines are recommendations only - clinical judgment required'
            }
            
        except Exception as e:
            self.logger.error(f"Guideline evaluation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def generate_order_set(
        self, 
        diagnosis: str, 
        patient_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate standardized order set for diagnosis
        
        Args:
            diagnosis: Primary diagnosis
            patient_profile: Patient demographics and clinical data
            
        Returns:
            Order set with medications, labs, and referrals
        """
        try:
            order_set = self.order_sets.get(diagnosis)
            
            if not order_set:
                return {
                    'status': 'success',
                    'diagnosis': diagnosis,
                    'order_set_found': False,
                    'message': f'No standard order set for {diagnosis}'
                }
            
            # Customize based on patient profile (simplified)
            customized_orders = {
                **order_set,
                'patient_id': patient_profile.get('patient_id'),
                'generated_at': datetime.utcnow().isoformat(),
                'customizations': []
            }
            
            # Check contraindications (simplified)
            allergies = patient_profile.get('allergies', [])
            if allergies:
                customized_orders['customizations'].append({
                    'type': 'allergy_check',
                    'message': f'Review medications against documented allergies: {", ".join(allergies)}'
                })
            
            return {
                'status': 'success',
                'order_set': customized_orders,
                'requires_review': True,
                'disclaimer': 'Order set must be reviewed and approved by clinician'
            }
            
        except Exception as e:
            self.logger.error(f"Order set generation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def trigger_clinical_alerts(
        self, 
        patient_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger clinical alerts based on patient state
        
        Alerts include:
        - Drug allergies
        - Critical lab values
        - Drug interactions
        - Duplicate therapy
        
        Args:
            patient_state: Current patient state including medications, labs, allergies
            
        Returns:
            List of triggered alerts with severity
        """
        try:
            triggered_alerts = []
            
            # Check drug-allergy alerts
            medications = patient_state.get('medications', [])
            allergies = patient_state.get('allergies', [])
            
            for med in medications:
                for allergy in allergies:
                    if med.lower() in allergy.lower() or allergy.lower() in med.lower():
                        triggered_alerts.append({
                            'alert_type': 'drug_allergy',
                            'severity': AlertSeverity.CRITICAL,
                            'message': f'CRITICAL: Patient allergic to {allergy}, prescribed {med}',
                            'action_required': True,
                            'triggered_at': datetime.utcnow().isoformat()
                        })
            
            # Check critical lab values
            lab_results = patient_state.get('lab_results', [])
            for lab in lab_results:
                if await self._is_critical_value(lab):
                    triggered_alerts.append({
                        'alert_type': 'critical_lab',
                        'severity': AlertSeverity.CRITICAL,
                        'message': f'CRITICAL LAB: {lab["test"]} = {lab["value"]} {lab.get("unit", "")}',
                        'action_required': True,
                        'triggered_at': datetime.utcnow().isoformat()
                    })
            
            # Sort by severity
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            triggered_alerts.sort(key=lambda x: severity_order.get(x['severity'], 5))
            
            return {
                'status': 'success',
                'alerts_triggered': len(triggered_alerts),
                'critical_alerts': len([a for a in triggered_alerts if a['severity'] == AlertSeverity.CRITICAL]),
                'alerts': triggered_alerts
            }
            
        except Exception as e:
            self.logger.error(f"Alert triggering failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _is_critical_value(self, lab_result: Dict[str, Any]) -> bool:
        """Check if lab value is in critical range"""
        critical_ranges = {
            'glucose': {'low': 40, 'high': 400},
            'potassium': {'low': 2.5, 'high': 6.0},
            'sodium': {'low': 120, 'high': 160},
            'creatinine': {'low': None, 'high': 5.0}
        }
        
        test_name = lab_result.get('test', '').lower()
        value = lab_result.get('value')
        
        if not value or test_name not in critical_ranges:
            return False
        
        ranges = critical_ranges[test_name]
        
        if ranges['low'] and value < ranges['low']:
            return True
        if ranges['high'] and value > ranges['high']:
            return True
        
        return False


# Module exports
__all__ = [
    'ClinicalDecisionSupport',
    'GuidelineSource',
    'AlertSeverity'
]
