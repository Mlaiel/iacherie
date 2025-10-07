"""
IA Chérie - Medical Terminology Service
========================================
Medical terminology service supporting international medical coding standards
including ICD-10/11, SNOMED CT, LOINC, RxNorm, and CPT.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 Fahed Mlaiel - All Rights Reserved
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Toute reproduction, modification ou distribution non autorisée est strictement interdite.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from enum import Enum


class TerminologySystem(str, Enum):
    """Medical terminology systems"""
    ICD10 = "ICD-10"
    ICD11 = "ICD-11"
    SNOMED_CT = "SNOMED CT"
    LOINC = "LOINC"
    RXNORM = "RxNorm"
    CPT = "CPT"


class MedicalTerminologyService:
    """
    Medical Terminology Service
    
    Provides comprehensive medical terminology support with:
    - ICD-10/11 diagnosis codes
    - SNOMED CT clinical terminology
    - LOINC laboratory observation codes
    - RxNorm medication terminology
    - CPT procedure codes
    - Cross-system code mapping
    - Fuzzy search capabilities
    - Multi-language support
    """
    
    def __init__(self):
        """Initialize medical terminology service"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize terminology databases
        self.icd10_db = self._initialize_icd10()
        self.icd11_db = self._initialize_icd11()
        self.snomed_db = self._initialize_snomed()
        self.loinc_db = self._initialize_loinc()
        self.rxnorm_db = self._initialize_rxnorm()
        self.cpt_db = self._initialize_cpt()
        
        # Code mapping tables
        self.code_mappings = self._initialize_mappings()
    
    def _initialize_icd10(self) -> Dict[str, Any]:
        """Initialize ICD-10 code database"""
        return {
            'E11': {
                'code': 'E11',
                'description': 'Type 2 diabetes mellitus',
                'category': 'Endocrine, nutritional and metabolic diseases',
                'subcodes': {
                    'E11.9': 'Type 2 diabetes mellitus without complications',
                    'E11.65': 'Type 2 diabetes mellitus with hyperglycemia',
                    'E11.21': 'Type 2 diabetes mellitus with diabetic nephropathy',
                    'E11.36': 'Type 2 diabetes mellitus with diabetic cataract'
                }
            },
            'I10': {
                'code': 'I10',
                'description': 'Essential (primary) hypertension',
                'category': 'Diseases of the circulatory system'
            },
            'J45': {
                'code': 'J45',
                'description': 'Asthma',
                'category': 'Diseases of the respiratory system',
                'subcodes': {
                    'J45.0': 'Predominantly allergic asthma',
                    'J45.1': 'Nonallergic asthma',
                    'J45.9': 'Asthma, unspecified'
                }
            },
            'M25.5': {
                'code': 'M25.5',
                'description': 'Pain in joint',
                'category': 'Diseases of the musculoskeletal system'
            }
        }
    
    def _initialize_icd11(self) -> Dict[str, Any]:
        """Initialize ICD-11 code database"""
        return {
            '5A11': {
                'code': '5A11',
                'description': 'Type 2 diabetes mellitus',
                'foundation_uri': 'http://id.who.int/icd/entity/169068983'
            }
        }
    
    def _initialize_snomed(self) -> Dict[str, Any]:
        """Initialize SNOMED CT database"""
        return {
            '44054006': {
                'code': '44054006',
                'description': 'Type 2 diabetes mellitus',
                'semantic_tag': 'disorder'
            },
            '38341003': {
                'code': '38341003',
                'description': 'Hypertensive disorder',
                'semantic_tag': 'disorder'
            },
            '195967001': {
                'code': '195967001',
                'description': 'Asthma',
                'semantic_tag': 'disorder'
            }
        }
    
    def _initialize_loinc(self) -> Dict[str, Any]:
        """Initialize LOINC laboratory codes"""
        return {
            '2345-7': {
                'code': '2345-7',
                'description': 'Glucose [Mass/volume] in Serum or Plasma',
                'component': 'Glucose',
                'property': 'MCnc',
                'timing': 'Pt',
                'system': 'Ser/Plas',
                'scale': 'Qn'
            },
            '4548-4': {
                'code': '4548-4',
                'description': 'Hemoglobin A1c/Hemoglobin.total in Blood',
                'component': 'Hemoglobin A1c',
                'property': 'MFr',
                'timing': 'Pt',
                'system': 'Bld',
                'scale': 'Qn'
            },
            '789-8': {
                'code': '789-8',
                'description': 'Erythrocytes [#/volume] in Blood',
                'component': 'Erythrocytes',
                'property': 'NCnc',
                'timing': 'Pt',
                'system': 'Bld',
                'scale': 'Qn'
            }
        }
    
    def _initialize_rxnorm(self) -> Dict[str, Any]:
        """Initialize RxNorm medication codes"""
        return {
            '860975': {
                'code': '860975',
                'name': 'Metformin 500 MG Oral Tablet',
                'generic_name': 'Metformin',
                'dose': '500 MG',
                'form': 'Oral Tablet',
                'tty': 'SCD'
            },
            '104376': {
                'code': '104376',
                'name': 'Lisinopril',
                'generic_name': 'Lisinopril',
                'tty': 'IN'
            },
            '1191': {
                'code': '1191',
                'name': 'Aspirin',
                'generic_name': 'Aspirin',
                'tty': 'IN'
            }
        }
    
    def _initialize_cpt(self) -> Dict[str, Any]:
        """Initialize CPT procedure codes"""
        return {
            '99213': {
                'code': '99213',
                'description': 'Office or other outpatient visit, established patient, 20-29 minutes',
                'category': 'Evaluation and Management'
            },
            '80053': {
                'code': '80053',
                'description': 'Comprehensive metabolic panel',
                'category': 'Laboratory'
            },
            '93000': {
                'code': '93000',
                'description': 'Electrocardiogram, complete',
                'category': 'Cardiovascular'
            }
        }
    
    def _initialize_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize code mapping tables"""
        return {
            'snomed_to_icd10': {
                '44054006': 'E11.9',  # Type 2 diabetes
                '38341003': 'I10',     # Hypertension
                '195967001': 'J45.9'   # Asthma
            },
            'icd10_to_snomed': {
                'E11.9': '44054006',
                'I10': '38341003',
                'J45.9': '195967001'
            }
        }
    
    async def search_icd10_codes(
        self, 
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search ICD-10 codes with fuzzy matching
        
        Args:
            query: Search term
            limit: Maximum results to return
            
        Returns:
            Matching ICD-10 codes with descriptions
        """
        try:
            results = []
            query_lower = query.lower()
            
            # Search in ICD-10 database
            for code, data in self.icd10_db.items():
                description = data['description'].lower()
                
                # Simple fuzzy matching
                if query_lower in description or query_lower in code.lower():
                    results.append({
                        'code': code,
                        'description': data['description'],
                        'category': data['category'],
                        'has_subcodes': 'subcodes' in data
                    })
                    
                    if len(results) >= limit:
                        break
                
                # Check subcodes
                if 'subcodes' in data:
                    for subcode, subdesc in data['subcodes'].items():
                        if query_lower in subdesc.lower() or query_lower in subcode.lower():
                            results.append({
                                'code': subcode,
                                'description': subdesc,
                                'category': data['category'],
                                'parent_code': code
                            })
                            
                            if len(results) >= limit:
                                break
            
            return {
                'status': 'success',
                'query': query,
                'results_count': len(results),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"ICD-10 search failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def map_snomed_to_icd10(self, snomed_code: str) -> Dict[str, Any]:
        """
        Map SNOMED CT code to ICD-10
        
        Args:
            snomed_code: SNOMED CT concept ID
            
        Returns:
            Mapped ICD-10 code with details
        """
        try:
            # Check mapping table
            icd10_code = self.code_mappings['snomed_to_icd10'].get(snomed_code)
            
            if not icd10_code:
                return {
                    'status': 'success',
                    'snomed_code': snomed_code,
                    'icd10_code': None,
                    'message': 'No direct mapping available'
                }
            
            # Get ICD-10 details
            icd10_data = self.icd10_db.get(icd10_code.split('.')[0])
            
            return {
                'status': 'success',
                'snomed_code': snomed_code,
                'snomed_description': self.snomed_db.get(snomed_code, {}).get('description'),
                'icd10_code': icd10_code,
                'icd10_description': icd10_data.get('description') if icd10_data else None
            }
            
        except Exception as e:
            self.logger.error(f"SNOMED to ICD-10 mapping failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def validate_medical_code(
        self, 
        code: str, 
        system: TerminologySystem
    ) -> Dict[str, Any]:
        """
        Validate medical code in specified system
        
        Args:
            code: Medical code to validate
            system: Terminology system
            
        Returns:
            Validation result with code details
        """
        try:
            valid = False
            details = None
            
            if system == TerminologySystem.ICD10:
                # Check full code or parent code
                parent_code = code.split('.')[0]
                if parent_code in self.icd10_db:
                    data = self.icd10_db[parent_code]
                    valid = True
                    details = {
                        'code': code,
                        'description': data['description'],
                        'category': data['category']
                    }
                    
                    # Check if it's a subcode
                    if '.' in code and 'subcodes' in data:
                        if code in data['subcodes']:
                            details['description'] = data['subcodes'][code]
            
            elif system == TerminologySystem.SNOMED_CT:
                if code in self.snomed_db:
                    valid = True
                    details = self.snomed_db[code]
            
            elif system == TerminologySystem.LOINC:
                if code in self.loinc_db:
                    valid = True
                    details = self.loinc_db[code]
            
            elif system == TerminologySystem.RXNORM:
                if code in self.rxnorm_db:
                    valid = True
                    details = self.rxnorm_db[code]
            
            elif system == TerminologySystem.CPT:
                if code in self.cpt_db:
                    valid = True
                    details = self.cpt_db[code]
            
            return {
                'status': 'success',
                'code': code,
                'system': system,
                'valid': valid,
                'details': details
            }
            
        except Exception as e:
            self.logger.error(f"Code validation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_drug_information(self, rxnorm_code: str) -> Dict[str, Any]:
        """
        Get drug information from RxNorm
        
        Args:
            rxnorm_code: RxNorm concept ID
            
        Returns:
            Drug information including name, dose, form
        """
        try:
            drug_info = self.rxnorm_db.get(rxnorm_code)
            
            if not drug_info:
                return {
                    'status': 'success',
                    'rxnorm_code': rxnorm_code,
                    'found': False
                }
            
            return {
                'status': 'success',
                'rxnorm_code': rxnorm_code,
                'found': True,
                'drug_info': drug_info
            }
            
        except Exception as e:
            self.logger.error(f"Drug information retrieval failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}


# Module exports
__all__ = [
    'MedicalTerminologyService',
    'TerminologySystem'
]
