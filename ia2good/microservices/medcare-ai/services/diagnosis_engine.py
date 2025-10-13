"""
Diagnosis Engine Service
Generates medical diagnoses based on symptoms and test results
"""
from typing import Dict, List, Optional, Tuple
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class DiagnosisEngine:
    """
    Core diagnosis engine combining symptom analysis and medical knowledge
    
    Uses:
    - Medical knowledge base (ICD-10)
    - Clinical decision support rules
    - Differential diagnosis generation
    - Lab test interpretation
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._initialize_medical_knowledge()
        self._initialize_icd10_database()
        self._initialize_drug_interactions()
    
    def _initialize_medical_knowledge(self):
        """Initialize comprehensive medical knowledge base"""
        self.condition_database = {
            "upper_respiratory_infection": {
                "name": "Upper Respiratory Infection",
                "icd10": "J06.9",
                "category": "respiratory",
                "symptoms": ["sore throat", "runny nose", "cough", "congestion", "mild fever", "sneezing"],
                "risk_factors": ["contact with sick people", "cold weather", "weakened immunity"],
                "typical_duration_days": (5, 10),
                "severity": "mild-moderate",
                "tests": ["Rapid Strep Test", "Throat Culture"],
                "treatments": ["rest", "hydration", "OTC pain relievers", "decongestants"]
            },
            "common_cold": {
                "name": "Common Cold",
                "icd10": "J00",
                "category": "respiratory",
                "symptoms": ["runny nose", "sneezing", "sore throat", "cough", "mild fever"],
                "risk_factors": ["contact exposure", "season change"],
                "typical_duration_days": (3, 7),
                "severity": "mild",
                "tests": [],
                "treatments": ["rest", "fluids", "vitamin C", "zinc supplements"]
            },
            "influenza": {
                "name": "Influenza",
                "icd10": "J11.1",
                "category": "respiratory",
                "symptoms": ["high fever", "body aches", "fatigue", "cough", "headache", "chills"],
                "risk_factors": ["flu season", "unvaccinated", "crowded places"],
                "typical_duration_days": (5, 14),
                "severity": "moderate-severe",
                "tests": ["Rapid Flu Test", "RT-PCR"],
                "treatments": ["antiviral medication", "rest", "hydration", "fever reducers"]
            },
            "covid19": {
                "name": "COVID-19",
                "icd10": "U07.1",
                "category": "respiratory",
                "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "fatigue", "shortness of breath"],
                "risk_factors": ["exposure", "unvaccinated", "crowded places"],
                "typical_duration_days": (7, 21),
                "severity": "mild-severe",
                "tests": ["RT-PCR", "Rapid Antigen Test", "Antibody Test"],
                "treatments": ["isolation", "rest", "hydration", "antivirals if severe", "oxygen if needed"]
            },
            "acute_bronchitis": {
                "name": "Acute Bronchitis",
                "icd10": "J20.9",
                "category": "respiratory",
                "symptoms": ["persistent cough", "mucus production", "chest discomfort", "fatigue", "mild fever"],
                "risk_factors": ["smoking", "air pollution", "recent URI"],
                "typical_duration_days": (10, 21),
                "severity": "moderate",
                "tests": ["Chest X-ray", "Spirometry"],
                "treatments": ["rest", "hydration", "cough suppressants", "bronchodilators"]
            },
            "pneumonia": {
                "name": "Pneumonia",
                "icd10": "J18.9",
                "category": "respiratory",
                "symptoms": ["high fever", "productive cough", "chest pain", "shortness of breath", "fatigue"],
                "risk_factors": ["elderly", "weakened immunity", "chronic lung disease"],
                "typical_duration_days": (7, 21),
                "severity": "severe",
                "tests": ["Chest X-ray", "Complete Blood Count", "Sputum Culture"],
                "treatments": ["antibiotics", "rest", "hydration", "hospitalization if severe"]
            },
            "gastroenteritis": {
                "name": "Gastroenteritis",
                "icd10": "K52.9",
                "category": "gastrointestinal",
                "symptoms": ["nausea", "vomiting", "diarrhea", "abdominal pain", "fever"],
                "risk_factors": ["food contamination", "viral infection", "poor hygiene"],
                "typical_duration_days": (1, 5),
                "severity": "moderate",
                "tests": ["Stool Test", "Blood Test"],
                "treatments": ["oral rehydration", "rest", "bland diet", "anti-nausea medication"]
            },
            "urinary_tract_infection": {
                "name": "Urinary Tract Infection",
                "icd10": "N39.0",
                "category": "urinary",
                "symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine", "fever"],
                "risk_factors": ["female gender", "sexual activity", "poor hygiene"],
                "typical_duration_days": (3, 7),
                "severity": "moderate",
                "tests": ["Urinalysis", "Urine Culture"],
                "treatments": ["antibiotics", "hydration", "cranberry juice"]
            },
            "migraine": {
                "name": "Migraine",
                "icd10": "G43.909",
                "category": "neurological",
                "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound", "visual disturbances"],
                "risk_factors": ["family history", "stress", "certain foods", "hormonal changes"],
                "typical_duration_days": (0.5, 3),
                "severity": "severe",
                "tests": ["CT Scan", "MRI (if atypical)"],
                "treatments": ["pain relievers", "triptans", "rest in dark room", "preventive medication"]
            },
            "hypertension": {
                "name": "Hypertension",
                "icd10": "I10",
                "category": "cardiovascular",
                "symptoms": ["headache", "dizziness", "blurred vision", "chest pain", "shortness of breath"],
                "risk_factors": ["obesity", "high salt diet", "sedentary lifestyle", "family history"],
                "typical_duration_days": (365, 3650),  # Chronic
                "severity": "moderate-severe",
                "tests": ["Blood Pressure Monitoring", "ECG", "Blood Tests"],
                "treatments": ["lifestyle changes", "low salt diet", "exercise", "antihypertensive medication"]
            }
        }
    
    def _initialize_icd10_database(self):
        """Initialize ICD-10 code lookup database"""
        self.icd10_codes = {
            # Respiratory
            "J00": "Acute nasopharyngitis (common cold)",
            "J06.9": "Acute upper respiratory infection, unspecified",
            "J11.1": "Influenza with other respiratory manifestations",
            "J20.9": "Acute bronchitis, unspecified",
            "J18.9": "Pneumonia, unspecified organism",
            "J30.4": "Allergic rhinitis, unspecified",
            "U07.1": "COVID-19",
            
            # Gastrointestinal
            "K52.9": "Gastroenteritis and colitis, unspecified",
            "K59.00": "Constipation, unspecified",
            "K30": "Functional dyspepsia",
            
            # Urinary
            "N39.0": "Urinary tract infection, site not specified",
            
            # Neurological
            "G43.909": "Migraine, unspecified, not intractable, without status migrainosus",
            "G44.1": "Vascular headache, not elsewhere classified",
            
            # Cardiovascular
            "I10": "Essential (primary) hypertension",
            "I20.9": "Angina pectoris, unspecified",
            
            # General
            "R50.9": "Fever, unspecified",
            "R51": "Headache",
            "R69": "Illness, unspecified",
        }
    
    def _initialize_drug_interactions(self):
        """Initialize drug interaction and contraindication database"""
        self.drug_interactions = {
            "aspirin": {
                "allergies": ["nsaid allergy", "aspirin allergy"],
                "contraindications": ["bleeding disorder", "stomach ulcer", "severe kidney disease"],
                "interactions": ["warfarin", "ibuprofen", "naproxen"]
            },
            "ibuprofen": {
                "allergies": ["nsaid allergy", "ibuprofen allergy"],
                "contraindications": ["stomach ulcer", "heart disease", "kidney disease"],
                "interactions": ["aspirin", "warfarin", "prednisone"]
            },
            "acetaminophen": {
                "allergies": ["acetaminophen allergy"],
                "contraindications": ["severe liver disease", "alcohol abuse"],
                "interactions": ["warfarin"]
            },
            "penicillin": {
                "allergies": ["penicillin allergy", "beta-lactam allergy"],
                "contraindications": ["history of severe allergic reaction"],
                "interactions": ["methotrexate", "probenecid"]
            },
            "amoxicillin": {
                "allergies": ["penicillin allergy", "amoxicillin allergy"],
                "contraindications": ["mononucleosis"],
                "interactions": ["methotrexate", "probenecid"]
            }
        }
    
    def generate_diagnosis(
        self,
        symptoms: Dict,
        medical_history: Dict,
        test_results: Dict = None,
        images_analysis: List[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive diagnosis
        
        Combines:
        - Symptom analysis
        - Patient medical history
        - Lab test results (if available)
        - Medical image analysis (if available)
        
        Returns:
        - Primary diagnosis with confidence
        - Differential diagnoses
        - ICD-10 codes
        - Recommended tests/procedures
        - Treatment suggestions (general)
        """
        logger.info("Generating diagnosis based on symptoms and medical history")
        
        # Extract symptom information
        symptom_list = symptoms.get("symptoms", [])
        symptom_description = symptoms.get("description", "")
        severity = symptoms.get("severity", 5)
        duration_hours = symptoms.get("duration_hours", 0)
        
        # Parse symptoms if only description provided
        if symptom_description and not symptom_list:
            symptom_list = self._parse_symptoms(symptom_description)
        
        # Match symptoms to conditions
        condition_matches = self._match_conditions(
            symptom_list, 
            severity, 
            duration_hours,
            medical_history
        )
        
        # Apply test results if available
        if test_results:
            condition_matches = self._refine_with_test_results(condition_matches, test_results)
        
        # Apply image analysis if available
        if images_analysis:
            condition_matches = self._refine_with_images(condition_matches, images_analysis)
        
        # Sort by confidence
        condition_matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        if not condition_matches:
            return self._generate_unknown_diagnosis(symptoms)
        
        # Primary diagnosis (highest confidence)
        primary = condition_matches[0]
        
        # Differential diagnoses (next 3-5)
        differentials = condition_matches[1:6]
        
        # Get condition details
        condition_key = primary["condition_key"]
        condition_data = self.condition_database.get(condition_key, {})
        
        # Generate recommendations
        recommended_tests = self._recommend_tests(primary, differentials, test_results)
        treatment_suggestions = self._generate_treatment_suggestions(primary, medical_history)
        
        return {
            "primary_diagnosis": {
                "condition": primary["condition"],
                "confidence": primary["confidence"],
                "icd10": primary["icd10"],
                "category": condition_data.get("category", "general"),
                "severity": condition_data.get("severity", "unknown"),
                "typical_duration": condition_data.get("typical_duration_days", (1, 14))
            },
            "differential_diagnoses": [
                {
                    "condition": d["condition"],
                    "confidence": d["confidence"],
                    "icd10": d["icd10"]
                }
                for d in differentials
            ],
            "recommended_tests": recommended_tests,
            "general_treatment_suggestions": treatment_suggestions,
            "risk_factors_identified": self._identify_risk_factors(medical_history, primary),
            "follow_up_timeline": self._suggest_follow_up(primary),
            "red_flags": self._identify_red_flags(symptoms, primary),
            "medical_disclaimer": (
                "This is a preliminary AI diagnosis. Professional medical "
                "evaluation is required for accurate diagnosis and treatment."
            )
        }
    
    def _parse_symptoms(self, text: str) -> List[str]:
        """Parse symptoms from free text"""
        text_lower = text.lower()
        symptoms = []
        
        # Extract from known symptoms across all conditions
        for condition_data in self.condition_database.values():
            for symptom in condition_data["symptoms"]:
                if symptom in text_lower:
                    symptoms.append(symptom)
        
        return list(set(symptoms))
    
    def _match_conditions(
        self, 
        symptom_list: List[str], 
        severity: int,
        duration_hours: int,
        medical_history: Dict
    ) -> List[Dict]:
        """Match symptoms to conditions in knowledge base"""
        matches = []
        duration_days = duration_hours / 24.0
        
        patient_symptoms = set([s.lower() for s in symptom_list])
        
        for condition_key, condition_data in self.condition_database.items():
            condition_symptoms = set(condition_data["symptoms"])
            
            # Find matching symptoms
            matching = condition_symptoms.intersection(patient_symptoms)
            
            # Partial matching for related terms
            if not matching:
                for ps in patient_symptoms:
                    for cs in condition_symptoms:
                        if ps in cs or cs in ps:
                            matching.add(cs)
            
            if len(matching) > 0:
                # Calculate base confidence from symptom match
                symptom_score = len(matching) / len(condition_symptoms)
                
                # Adjust for severity alignment
                severity_match = 1.0
                if condition_data.get("severity") == "severe" and severity < 6:
                    severity_match = 0.6
                elif condition_data.get("severity") == "mild" and severity > 7:
                    severity_match = 0.7
                
                # Adjust for duration alignment
                dur_min, dur_max = condition_data.get("typical_duration_days", (1, 30))
                duration_match = 1.0 if dur_min <= duration_days <= dur_max else 0.8
                
                # Check risk factors
                risk_factor_match = 1.0
                patient_risk_factors = medical_history.get("risk_factors", [])
                condition_risk_factors = condition_data.get("risk_factors", [])
                
                for prf in patient_risk_factors:
                    if any(crf in prf.lower() for crf in condition_risk_factors):
                        risk_factor_match = 1.2  # Boost if risk factors present
                        break
                
                # Calculate final confidence
                confidence = min(
                    (symptom_score * 0.5 + 
                     severity_match * 0.2 + 
                     duration_match * 0.15 +
                     (risk_factor_match - 1.0) * 0.15),
                    0.95  # Cap at 95%
                )
                
                matches.append({
                    "condition": condition_data["name"],
                    "condition_key": condition_key,
                    "confidence": round(confidence, 2),
                    "icd10": condition_data["icd10"],
                    "matching_symptoms": list(matching)
                })
        
        return matches
    
    def _refine_with_test_results(self, matches: List[Dict], test_results: Dict) -> List[Dict]:
        """Refine diagnosis confidence based on test results"""
        # Boost confidence if test results confirm diagnosis
        for match in matches:
            condition_key = match["condition_key"]
            condition_data = self.condition_database.get(condition_key, {})
            
            # Example: Positive rapid flu test boosts flu diagnosis
            if "rapid_flu_test" in test_results:
                if test_results["rapid_flu_test"] == "positive" and "influenza" in condition_key:
                    match["confidence"] = min(match["confidence"] * 1.3, 0.95)
            
            # Positive strep test boosts strep throat
            if "rapid_strep_test" in test_results:
                if test_results["rapid_strep_test"] == "positive" and "strep" in match["condition"].lower():
                    match["confidence"] = min(match["confidence"] * 1.4, 0.95)
        
        return matches
    
    def _refine_with_images(self, matches: List[Dict], images_analysis: List[Dict]) -> List[Dict]:
        """Refine diagnosis based on medical image analysis"""
        # Boost conditions that match image findings
        for image in images_analysis:
            image_type = image.get("type", "").lower()
            findings = image.get("findings", [])
            
            for match in matches:
                condition_key = match["condition_key"]
                
                # Example: Chest X-ray showing infiltrates boosts pneumonia
                if "pneumonia" in condition_key and "infiltrate" in " ".join(findings).lower():
                    match["confidence"] = min(match["confidence"] * 1.25, 0.95)
        
        return matches
    
    def _recommend_tests(
        self, 
        primary: Dict, 
        differentials: List[Dict],
        existing_tests: Optional[Dict]
    ) -> List[str]:
        """Recommend diagnostic tests"""
        recommended = []
        existing_test_names = set(existing_tests.keys()) if existing_tests else set()
        
        # Get tests for primary diagnosis
        condition_key = primary["condition_key"]
        condition_data = self.condition_database.get(condition_key, {})
        
        for test in condition_data.get("tests", []):
            if test.lower().replace(" ", "_") not in existing_test_names:
                recommended.append(test)
        
        # Add tests from top differentials if confidence is close
        for diff in differentials[:2]:
            if diff["confidence"] > primary["confidence"] - 0.15:
                diff_key = diff["condition_key"]
                diff_data = self.condition_database.get(diff_key, {})
                for test in diff_data.get("tests", []):
                    if test not in recommended and test.lower().replace(" ", "_") not in existing_test_names:
                        recommended.append(test)
        
        return recommended[:5]  # Limit to 5 tests
    
    def _generate_treatment_suggestions(self, primary: Dict, medical_history: Dict) -> List[str]:
        """Generate general treatment suggestions"""
        condition_key = primary["condition_key"]
        condition_data = self.condition_database.get(condition_key, {})
        
        treatments = condition_data.get("treatments", []).copy()
        
        # Add general advice
        treatments.append("Follow medical professional's advice")
        treatments.append("Monitor symptoms and report any worsening")
        
        return treatments[:6]
    
    def _identify_risk_factors(self, medical_history: Dict, primary: Dict) -> List[str]:
        """Identify risk factors present in patient"""
        identified = []
        condition_key = primary["condition_key"]
        condition_data = self.condition_database.get(condition_key, {})
        
        condition_risk_factors = condition_data.get("risk_factors", [])
        patient_factors = medical_history.get("risk_factors", [])
        patient_conditions = medical_history.get("chronic_conditions", [])
        
        for crf in condition_risk_factors:
            if any(crf in pf.lower() for pf in patient_factors):
                identified.append(crf.title())
        
        return identified
    
    def _suggest_follow_up(self, primary: Dict) -> str:
        """Suggest follow-up timeline"""
        condition_key = primary["condition_key"]
        condition_data = self.condition_database.get(condition_key, {})
        severity = condition_data.get("severity", "moderate")
        
        if severity == "severe":
            return "Follow up within 2-3 days or sooner if symptoms worsen"
        elif severity == "moderate":
            return "Follow up within 1 week"
        else:
            return "Follow up in 1-2 weeks if symptoms persist"
    
    def _identify_red_flags(self, symptoms: Dict, primary: Dict) -> List[str]:
        """Identify red flag symptoms requiring immediate attention"""
        red_flags = []
        
        emergency_symptoms = [
            "chest pain", "difficulty breathing", "severe bleeding",
            "loss of consciousness", "severe head injury", "stroke symptoms"
        ]
        
        symptom_text = str(symptoms).lower()
        
        for flag in emergency_symptoms:
            if flag in symptom_text:
                red_flags.append(f"Emergency: {flag.title()} detected - seek immediate medical attention")
        
        return red_flags
    
    def _generate_unknown_diagnosis(self, symptoms: Dict) -> Dict:
        """Generate response when no clear diagnosis can be made"""
        return {
            "primary_diagnosis": {
                "condition": "Unspecified Illness",
                "confidence": 0.0,
                "icd10": "R69",
                "category": "general",
                "severity": "unknown",
                "typical_duration": (1, 7)
            },
            "differential_diagnoses": [],
            "recommended_tests": [
                "Complete Blood Count (CBC)",
                "Comprehensive Metabolic Panel",
                "Urinalysis"
            ],
            "general_treatment_suggestions": [
                "Consult with a healthcare provider for proper evaluation",
                "Monitor symptoms carefully",
                "Rest and stay hydrated",
                "Keep a symptom diary"
            ],
            "risk_factors_identified": [],
            "follow_up_timeline": "Consult doctor within 3-5 days",
            "red_flags": [],
            "medical_disclaimer": (
                "Unable to generate specific diagnosis. Please consult with "
                "a healthcare professional for proper evaluation."
            )
        }
    
    def lookup_icd10_code(self, condition_name: str) -> str:
        """
        Look up ICD-10 code for a condition
        
        ICD-10: International Classification of Diseases, 10th Revision
        
        Args:
            condition_name: Name of the condition
        
        Returns:
            ICD-10 code string
        """
        condition_lower = condition_name.lower()
        
        # Search in condition database
        for condition_key, condition_data in self.condition_database.items():
            if condition_lower in condition_data["name"].lower():
                return condition_data["icd10"]
        
        # Search directly in ICD-10 codes by description
        for code, description in self.icd10_codes.items():
            if condition_lower in description.lower():
                return code
        
        # Fuzzy matching - check for partial matches
        for condition_key, condition_data in self.condition_database.items():
            name_words = condition_data["name"].lower().split()
            condition_words = condition_lower.split()
            
            # Check if any significant word matches
            matches = [w for w in condition_words if w in name_words and len(w) > 3]
            if len(matches) >= 2 or (len(matches) == 1 and len(condition_words) == 1):
                logger.info(f"Fuzzy match: '{condition_name}' -> {condition_data['name']}")
                return condition_data["icd10"]
        
        logger.warning(f"ICD-10 code not found for: {condition_name}")
        return "R69"  # Unknown and unspecified causes of morbidity
    
    def get_icd10_details(self, code: str) -> Optional[Dict]:
        """
        Get detailed information about an ICD-10 code
        
        Args:
            code: ICD-10 code (e.g., "J06.9")
        
        Returns:
            Dictionary with code details or None if not found
        """
        if code in self.icd10_codes:
            return {
                "code": code,
                "description": self.icd10_codes[code],
                "category": self._get_icd10_category(code)
            }
        
        # Try partial match (without decimal)
        base_code = code.split(".")[0]
        for icd_code, description in self.icd10_codes.items():
            if icd_code.startswith(base_code):
                return {
                    "code": icd_code,
                    "description": description,
                    "category": self._get_icd10_category(icd_code),
                    "note": f"Closest match to {code}"
                }
        
        logger.warning(f"ICD-10 code not found: {code}")
        return None
    
    def _get_icd10_category(self, code: str) -> str:
        """Get ICD-10 category from code"""
        categories = {
            "A": "Infectious and Parasitic Diseases",
            "B": "Infectious and Parasitic Diseases",
            "C": "Neoplasms",
            "D": "Neoplasms / Blood Disorders",
            "E": "Endocrine, Nutritional and Metabolic Diseases",
            "F": "Mental and Behavioral Disorders",
            "G": "Nervous System",
            "H": "Eye, Ear, and Mastoid Process",
            "I": "Circulatory System",
            "J": "Respiratory System",
            "K": "Digestive System",
            "L": "Skin and Subcutaneous Tissue",
            "M": "Musculoskeletal System",
            "N": "Genitourinary System",
            "O": "Pregnancy, Childbirth, Puerperium",
            "P": "Perinatal Conditions",
            "Q": "Congenital Malformations",
            "R": "Symptoms, Signs, and Abnormal Findings",
            "S": "Injury and Poisoning",
            "T": "Injury and Poisoning",
            "U": "Special Purposes",
            "V": "External Causes",
            "W": "External Causes",
            "X": "External Causes",
            "Y": "External Causes",
            "Z": "Health Services Contact"
        }
        
        if code and len(code) > 0:
            first_char = code[0].upper()
            return categories.get(first_char, "Unknown")
        
        return "Unknown"
    
    def check_contraindications(
        self,
        diagnosis: str,
        medications: List[str],
        allergies: List[str],
        chronic_conditions: List[str]
    ) -> List[str]:
        """
        Check for contraindications in proposed treatment
        
        Validates:
        - Drug allergies
        - Drug-drug interactions
        - Drug-condition contraindications
        
        Returns list of warnings/contraindications
        """
        warnings = []
        
        # Normalize inputs
        medications_lower = [m.lower() for m in medications]
        allergies_lower = [a.lower() for a in allergies]
        conditions_lower = [c.lower() for c in chronic_conditions]
        
        # 1. Check drug allergies
        for med in medications:
            med_lower = med.lower()
            
            # Direct allergy match
            if any(allergy in med_lower or med_lower in allergy for allergy in allergies_lower):
                warnings.append(f"⚠️ CRITICAL: Patient is allergic to {med}")
                continue
            
            # Check drug-specific allergies from database
            if med_lower in self.drug_interactions:
                drug_data = self.drug_interactions[med_lower]
                
                for allergy in drug_data.get("allergies", []):
                    if any(allergy.lower() in a for a in allergies_lower):
                        warnings.append(
                            f"⚠️ CRITICAL: {med} contraindicated - "
                            f"patient allergic to {allergy}"
                        )
        
        # 2. Check contraindications with chronic conditions
        for med in medications:
            med_lower = med.lower()
            
            if med_lower in self.drug_interactions:
                drug_data = self.drug_interactions[med_lower]
                
                for contraindication in drug_data.get("contraindications", []):
                    contra_lower = contraindication.lower()
                    
                    # Check if patient has this condition
                    if any(contra_lower in cond or cond in contra_lower 
                           for cond in conditions_lower):
                        warnings.append(
                            f"⚠️ WARNING: {med} may be contraindicated - "
                            f"patient has {contraindication}"
                        )
        
        # 3. Check drug-drug interactions
        if len(medications) > 1:
            checked_pairs = set()
            
            for i, med1 in enumerate(medications):
                med1_lower = med1.lower()
                
                if med1_lower not in self.drug_interactions:
                    continue
                
                drug1_data = self.drug_interactions[med1_lower]
                
                for med2 in medications[i+1:]:
                    med2_lower = med2.lower()
                    
                    # Create pair key to avoid duplicates
                    pair_key = tuple(sorted([med1_lower, med2_lower]))
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)
                    
                    # Check if med2 is in med1's interaction list
                    for interaction in drug1_data.get("interactions", []):
                        interaction_lower = interaction.lower()
                        
                        if (med2_lower in interaction_lower or 
                            interaction_lower in med2_lower):
                            warnings.append(
                                f"⚠️ WARNING: Potential interaction between "
                                f"{med1} and {med2}"
                            )
                            break
        
        # 4. Special warnings for specific combinations
        if "aspirin" in medications_lower and "ibuprofen" in medications_lower:
            warnings.append(
                "⚠️ WARNING: Aspirin + Ibuprofen increases bleeding risk. "
                "Consult physician about timing and dosage."
            )
        
        # 5. Age-based warnings (if age info available in diagnosis)
        # This could be enhanced with patient age data
        
        # 6. Pregnancy warnings
        if any("pregnan" in cond for cond in conditions_lower):
            pregnancy_risk_meds = ["aspirin", "ibuprofen"]
            for med in medications_lower:
                if any(risk_med in med for risk_med in pregnancy_risk_meds):
                    warnings.append(
                        f"⚠️ WARNING: {med.title()} should be used with caution "
                        f"during pregnancy. Consult healthcare provider."
                    )
        
        # 7. Kidney/Liver disease warnings
        if any(kw in " ".join(conditions_lower) for kw in ["kidney", "renal", "liver", "hepatic"]):
            warnings.append(
                "⚠️ NOTE: Medication dosages may need adjustment for "
                "kidney/liver disease. Physician consultation required."
            )
        
        if not warnings:
            return ["✅ No contraindications detected based on available information"]
        
        # Add general disclaimer
        warnings.append(
            "📋 NOTE: This is not exhaustive. Always consult with a "
            "healthcare provider before starting new medications."
        )
        
        return warnings
