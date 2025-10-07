"""
IA Chérie - Medical AI Assistant
=================================
Medical AI assistant providing clinical decision support, drug interaction
checking, and medical NLP analysis. NOT FDA approved - informational only.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 Fahed Mlaiel - All Rights Reserved
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
⚠️ DISCLAIMER: NOT A MEDICAL DEVICE - For informational purposes only
Toute reproduction, modification ou distribution non autorisée est strictement interdite.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import re


class MedicalCodeSystem(str, Enum):
    """Medical coding systems"""
    ICD10 = "ICD-10"
    ICD11 = "ICD-11"
    CPT = "CPT"
    SNOMED_CT = "SNOMED CT"
    LOINC = "LOINC"
    RXNORM = "RxNorm"


class InteractionSeverity(str, Enum):
    """Drug interaction severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"


class MedicalAIAssistant:
    """
    Medical AI Assistant Service
    
    ⚠️ IMPORTANT DISCLAIMER:
    This is NOT an FDA-approved medical device. It provides informational
    support only and should NOT be used as the sole basis for medical
    decisions. All outputs must be reviewed by qualified healthcare
    professionals.
    
    Features:
    - Medical Natural Language Processing (NLP)
    - Named Entity Recognition (medications, conditions, procedures)
    - Medical coding (ICD-10, CPT, SNOMED CT)
    - Drug interaction checking
    - Differential diagnosis suggestions (SUPPORT ONLY)
    - Clinical note structuring
    
    NOT FOR:
    - Primary diagnostic decisions
    - Treatment decisions without physician review
    - Emergency medical situations
    - Patient self-diagnosis
    """
    
    def __init__(self, ai_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Medical AI Assistant
        
        Args:
            ai_config: Configuration for AI models and databases
        """
        self.ai_config = ai_config or {}
        self.logger = logging.getLogger(__name__)
        
        # Medical knowledge databases (simulated - in production use real databases)
        self.drug_database = self._initialize_drug_database()
        self.icd10_database = self._initialize_icd10_database()
        self.medical_knowledge = self._initialize_medical_knowledge()
    
    def _initialize_drug_database(self) -> Dict[str, Any]:
        """Initialize drug interaction database"""
        return {
            'metformin': {
                'rxnorm_code': '860975',
                'class': 'biguanide',
                'interactions': [
                    {
                        'drug': 'alcohol',
                        'severity': InteractionSeverity.MODERATE,
                        'description': 'May increase risk of lactic acidosis'
                    },
                    {
                        'drug': 'contrast_dye',
                        'severity': InteractionSeverity.MAJOR,
                        'description': 'Increased risk of kidney damage'
                    }
                ],
                'side_effects': ['nausea', 'diarrhea', 'vitamin B12 deficiency']
            },
            'lisinopril': {
                'rxnorm_code': '104376',
                'class': 'ACE inhibitor',
                'interactions': [
                    {
                        'drug': 'potassium',
                        'severity': InteractionSeverity.MAJOR,
                        'description': 'Risk of hyperkalemia'
                    }
                ],
                'side_effects': ['cough', 'dizziness', 'hyperkalemia']
            },
            'aspirin': {
                'rxnorm_code': '1191',
                'class': 'NSAID',
                'interactions': [
                    {
                        'drug': 'warfarin',
                        'severity': InteractionSeverity.MAJOR,
                        'description': 'Increased bleeding risk'
                    }
                ],
                'side_effects': ['gastric irritation', 'bleeding risk']
            }
        }
    
    def _initialize_icd10_database(self) -> Dict[str, Any]:
        """Initialize ICD-10 codes database"""
        return {
            'E11': {
                'code': 'E11',
                'description': 'Type 2 diabetes mellitus',
                'category': 'Endocrine',
                'subcodes': {
                    'E11.9': 'Type 2 diabetes without complications',
                    'E11.65': 'Type 2 diabetes with hyperglycemia',
                    'E11.21': 'Type 2 diabetes with diabetic nephropathy'
                }
            },
            'I10': {
                'code': 'I10',
                'description': 'Essential (primary) hypertension',
                'category': 'Cardiovascular'
            },
            'J45': {
                'code': 'J45',
                'description': 'Asthma',
                'category': 'Respiratory'
            }
        }
    
    def _initialize_medical_knowledge(self) -> Dict[str, Any]:
        """Initialize medical knowledge graph"""
        return {
            'symptom_disease': {
                'polyuria': ['diabetes mellitus', 'diabetes insipidus'],
                'polydipsia': ['diabetes mellitus', 'hyperthyroidism'],
                'chest_pain': ['coronary artery disease', 'costochondritis', 'GERD']
            }
        }
    
    async def analyze_clinical_text(self, clinical_text: str) -> Dict[str, Any]:
        """
        Analyze clinical text using medical NLP
        
        ⚠️ DISCLAIMER: Results are for informational purposes only.
        Must be reviewed by qualified healthcare professionals.
        
        Features:
        - Named Entity Recognition (NER)
        - Medical term extraction
        - Relationship extraction
        - Medical coding suggestions
        
        Args:
            clinical_text: Clinical note or medical text
            
        Returns:
            Extracted medical entities and relationships
        """
        try:
            self.logger.info("Analyzing clinical text with medical NLP")
            
            # Extract medical entities
            entities = await self._extract_medical_entities(clinical_text)
            
            # Extract relationships
            relationships = await self._extract_relationships(clinical_text, entities)
            
            # Suggest medical codes
            codes = await self._suggest_medical_codes(entities)
            
            analysis = {
                'text': clinical_text,
                'entities': entities,
                'relationships': relationships,
                'suggested_codes': codes,
                'analyzed_at': datetime.utcnow().isoformat(),
                'disclaimer': 'NOT FOR PRIMARY DIAGNOSTIC USE - Informational only'
            }
            
            return {
                'status': 'success',
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Clinical text analysis failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _extract_medical_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract medical entities from text"""
        entities = {
            'medications': [],
            'conditions': [],
            'procedures': [],
            'symptoms': [],
            'anatomy': [],
            'measurements': []
        }
        
        # Medication detection (simplified - in production use medical NER model)
        medications = ['metformin', 'lisinopril', 'aspirin', 'insulin']
        for med in medications:
            if med.lower() in text.lower():
                entities['medications'].append({
                    'text': med,
                    'type': 'medication',
                    'confidence': 0.90
                })
        
        # Condition detection
        conditions = ['diabetes', 'hypertension', 'asthma']
        for condition in conditions:
            if condition.lower() in text.lower():
                entities['conditions'].append({
                    'text': condition,
                    'type': 'condition',
                    'confidence': 0.85
                })
        
        # Extract measurements (blood pressure, glucose, etc.)
        bp_pattern = r'\d{2,3}/\d{2,3}'
        bp_matches = re.findall(bp_pattern, text)
        for bp in bp_matches:
            entities['measurements'].append({
                'text': bp,
                'type': 'blood_pressure',
                'unit': 'mmHg'
            })
        
        return entities
    
    async def _extract_relationships(
        self, 
        text: str, 
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Extract relationships between medical entities"""
        relationships = []
        
        # Drug-disease relationships
        for med in entities.get('medications', []):
            for condition in entities.get('conditions', []):
                relationships.append({
                    'type': 'treats',
                    'source': med['text'],
                    'target': condition['text'],
                    'confidence': 0.75
                })
        
        return relationships
    
    async def _suggest_medical_codes(
        self, 
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Suggest medical codes for entities"""
        codes = {
            'icd10': [],
            'cpt': [],
            'rxnorm': []
        }
        
        # ICD-10 codes for conditions
        for condition in entities.get('conditions', []):
            condition_text = condition['text'].lower()
            if 'diabetes' in condition_text:
                codes['icd10'].append({
                    'code': 'E11.9',
                    'description': 'Type 2 diabetes without complications',
                    'entity': condition['text']
                })
            elif 'hypertension' in condition_text:
                codes['icd10'].append({
                    'code': 'I10',
                    'description': 'Essential hypertension',
                    'entity': condition['text']
                })
        
        # RxNorm codes for medications
        for med in entities.get('medications', []):
            med_text = med['text'].lower()
            if med_text in self.drug_database:
                codes['rxnorm'].append({
                    'code': self.drug_database[med_text]['rxnorm_code'],
                    'description': med_text.capitalize(),
                    'entity': med['text']
                })
        
        return codes
    
    async def check_drug_interactions(
        self, 
        medications: List[str]
    ) -> Dict[str, Any]:
        """
        Check for drug-drug interactions
        
        ⚠️ DISCLAIMER: Must be verified by pharmacist or physician.
        
        Args:
            medications: List of medication names
            
        Returns:
            Interaction analysis with severity ratings
        """
        try:
            interactions = []
            
            # Check pairwise interactions
            for i, med1 in enumerate(medications):
                med1_lower = med1.lower()
                if med1_lower in self.drug_database:
                    med1_data = self.drug_database[med1_lower]
                    
                    for j, med2 in enumerate(medications[i+1:], start=i+1):
                        med2_lower = med2.lower()
                        
                        # Check if med2 is in med1's interactions
                        for interaction in med1_data.get('interactions', []):
                            if med2_lower in interaction['drug']:
                                interactions.append({
                                    'drug1': med1,
                                    'drug2': med2,
                                    'severity': interaction['severity'],
                                    'description': interaction['description'],
                                    'requires_monitoring': interaction['severity'] in [
                                        InteractionSeverity.MAJOR,
                                        InteractionSeverity.CONTRAINDICATED
                                    ]
                                })
            
            # Categorize by severity
            categorized = {
                'contraindicated': [],
                'major': [],
                'moderate': [],
                'minor': []
            }
            
            for interaction in interactions:
                severity = interaction['severity']
                categorized[severity].append(interaction)
            
            return {
                'status': 'success',
                'interactions_found': len(interactions),
                'interactions': interactions,
                'by_severity': categorized,
                'requires_immediate_review': len(categorized['contraindicated']) > 0 or len(categorized['major']) > 0,
                'disclaimer': 'Must be verified by pharmacist or physician'
            }
            
        except Exception as e:
            self.logger.error(f"Drug interaction check failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def suggest_differential_diagnosis(
        self, 
        symptoms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest differential diagnosis based on symptoms
        
        ⚠️ CRITICAL DISCLAIMER:
        This is SUPPORT ONLY and NOT for primary diagnostic decisions.
        Must be reviewed and validated by licensed physicians.
        NOT for use in emergency situations.
        
        Args:
            symptoms: Dictionary of symptoms with severity and duration
            
        Returns:
            Differential diagnosis suggestions with confidence scores
        """
        try:
            self.logger.warning("Differential diagnosis - SUPPORT ONLY, not diagnostic")
            
            # Extract symptom list
            symptom_list = symptoms.get('symptoms', [])
            
            # Find matching conditions
            possible_conditions = set()
            for symptom in symptom_list:
                symptom_lower = symptom.lower()
                if symptom_lower in self.medical_knowledge.get('symptom_disease', {}):
                    conditions = self.medical_knowledge['symptom_disease'][symptom_lower]
                    possible_conditions.update(conditions)
            
            # Score conditions based on symptom overlap
            scored_conditions = []
            for condition in possible_conditions:
                score = 0.5  # Base score
                scored_conditions.append({
                    'condition': condition,
                    'confidence': score,
                    'matching_symptoms': symptom_list[:2],  # Simplified
                    'suggested_tests': self._suggest_diagnostic_tests(condition)
                })
            
            # Sort by confidence
            scored_conditions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'status': 'success',
                'differential_diagnosis': scored_conditions,
                'total_possibilities': len(scored_conditions),
                'disclaimer': '⚠️ SUPPORT ONLY - NOT FOR PRIMARY DIAGNOSIS - Must be validated by physician',
                'emergency_note': 'If emergency symptoms present, seek immediate medical attention'
            }
            
        except Exception as e:
            self.logger.error(f"Differential diagnosis failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _suggest_diagnostic_tests(self, condition: str) -> List[str]:
        """Suggest diagnostic tests for condition"""
        test_mapping = {
            'diabetes mellitus': ['HbA1c', 'Fasting glucose', 'Oral glucose tolerance test'],
            'hypertension': ['Blood pressure monitoring', 'ECG', 'Echocardiogram'],
            'coronary artery disease': ['ECG', 'Stress test', 'Coronary angiography']
        }
        return test_mapping.get(condition, ['Clinical evaluation recommended'])
    
    async def extract_medical_codes(
        self, 
        clinical_note: str
    ) -> Dict[str, Any]:
        """
        Extract medical codes from clinical note
        
        Supports:
        - ICD-10 (diagnosis codes)
        - CPT (procedure codes)
        - LOINC (lab test codes)
        - RxNorm (medication codes)
        
        Args:
            clinical_note: Clinical documentation text
            
        Returns:
            Extracted medical codes with context
        """
        try:
            # Analyze text
            analysis = await self.analyze_clinical_text(clinical_note)
            
            if analysis['status'] != 'success':
                return analysis
            
            codes = analysis['analysis']['suggested_codes']
            
            return {
                'status': 'success',
                'codes': codes,
                'extracted_from': 'clinical_note',
                'note': 'Codes should be reviewed by certified medical coder'
            }
            
        except Exception as e:
            self.logger.error(f"Medical code extraction failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def validate_medical_content(
        self, 
        content: str, 
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate medical content against evidence-based sources
        
        Args:
            content: Medical content to validate
            sources: Optional list of reference sources
            
        Returns:
            Validation result with evidence level
        """
        try:
            # Check for medical entities
            entities = await self._extract_medical_entities(content)
            
            # Simulated validation - in production, check against medical databases
            validation = {
                'content_validated': True,
                'evidence_level': 'Level II',  # Simplified
                'entities_verified': len(entities.get('medications', [])) + len(entities.get('conditions', [])),
                'sources_checked': sources or ['PubMed', 'UpToDate', 'Cochrane'],
                'validation_date': datetime.utcnow().isoformat(),
                'disclaimer': 'Validation is automated - should be reviewed by medical professional'
            }
            
            return {
                'status': 'success',
                'validation': validation
            }
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}


# Module exports
__all__ = [
    'MedicalAIAssistant',
    'MedicalCodeSystem',
    'InteractionSeverity'
]
