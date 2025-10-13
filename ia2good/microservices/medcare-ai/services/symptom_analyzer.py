"""
Symptom Analyzer Service
AI-powered symptom analysis and preliminary diagnosis
"""
from typing import Dict, List, Optional
import logging
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

logger = logging.getLogger(__name__)


class SymptomAnalyzerService:
    """
    Service for analyzing patient symptoms and generating preliminary diagnosis
    
    Uses NLP and rule-based algorithms to:
    1. Parse and understand symptom descriptions
    2. Classify into medical conditions
    3. Calculate urgency level
    4. Generate follow-up questions
    5. Provide recommendations
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._initialize_medical_knowledge()
        
    def _initialize_medical_knowledge(self):
        """
        Initialize medical knowledge base
        Maps symptoms to conditions with ICD-10 codes
        """
        # Common medical conditions with their symptoms and ICD-10 codes
        self.medical_knowledge = {
            "common_cold": {
                "icd10": "J00",
                "symptoms": ["runny nose", "sneezing", "sore throat", "cough", "mild fever", "congestion"],
                "severity_range": (1, 4),
                "duration_days": (3, 7)
            },
            "influenza": {
                "icd10": "J11",
                "symptoms": ["high fever", "body aches", "fatigue", "headache", "cough", "chills"],
                "severity_range": (5, 8),
                "duration_days": (5, 14)
            },
            "covid19": {
                "icd10": "U07.1",
                "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "fatigue", "shortness of breath"],
                "severity_range": (3, 9),
                "duration_days": (7, 21)
            },
            "migraine": {
                "icd10": "G43",
                "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound", "visual disturbances"],
                "severity_range": (6, 10),
                "duration_days": (0.5, 3)
            },
            "gastroenteritis": {
                "icd10": "K52.9",
                "symptoms": ["nausea", "vomiting", "diarrhea", "abdominal pain", "fever", "dehydration"],
                "severity_range": (4, 7),
                "duration_days": (1, 5)
            },
            "allergic_rhinitis": {
                "icd10": "J30.4",
                "symptoms": ["sneezing", "itchy eyes", "runny nose", "congestion", "watery eyes"],
                "severity_range": (2, 5),
                "duration_days": (1, 365)  # Can be chronic
            },
            "bronchitis": {
                "icd10": "J20",
                "symptoms": ["persistent cough", "mucus production", "chest discomfort", "fatigue", "mild fever"],
                "severity_range": (4, 7),
                "duration_days": (7, 21)
            },
            "urinary_tract_infection": {
                "icd10": "N39.0",
                "symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine", "fever"],
                "severity_range": (4, 7),
                "duration_days": (3, 7)
            },
            "hypertension": {
                "icd10": "I10",
                "symptoms": ["headache", "dizziness", "blurred vision", "chest pain", "shortness of breath"],
                "severity_range": (3, 8),
                "duration_days": (1, 365)  # Chronic
            },
            "anxiety_disorder": {
                "icd10": "F41.9",
                "symptoms": ["nervousness", "rapid heartbeat", "sweating", "trembling", "difficulty concentrating", "insomnia"],
                "severity_range": (3, 8),
                "duration_days": (14, 365)
            }
        }
        
        # Emergency symptoms that require immediate attention
        self.emergency_symptoms = [
            "chest pain", "difficulty breathing", "severe bleeding", "loss of consciousness",
            "severe head injury", "stroke symptoms", "seizure", "severe allergic reaction",
            "suicide thoughts", "severe abdominal pain", "compound fracture"
        ]
        
        # High urgency symptoms
        self.high_urgency_symptoms = [
            "high fever", "persistent vomiting", "severe pain", "blood in stool",
            "blood in urine", "severe dehydration", "confusion", "slurred speech"
        ]
        
    def analyze_symptoms(self, symptoms: Dict) -> Dict:
        """
        Analyze symptoms and generate preliminary diagnosis
        
        Algorithm:
        1. Parse symptoms (NLP with keyword extraction)
        2. Match against medical knowledge base
        3. Calculate similarity scores
        4. Generate top 3 probable conditions
        5. Calculate urgency (emergency/urgent/routine)
        6. Generate personalized recommendations
        
        Args:
            symptoms: Dictionary of symptoms from patient
            
        Returns:
            Dictionary with:
            - top_conditions: List of probable conditions with confidence
            - urgency: emergency/urgent/routine/monitor
            - recommendations: List of suggested actions
            - follow_up_questions: List of clarifying questions
            - medical_disclaimer: Important disclaimer text
        """
        # Extract symptom description
        symptom_description = symptoms.get("description", "")
        symptom_list = symptoms.get("symptoms", [])
        severity = symptoms.get("severity", 5)
        duration_hours = symptoms.get("duration_hours", 0)
        
        # Parse symptoms from text if provided
        if symptom_description and not symptom_list:
            symptom_list = self._parse_symptoms_from_text(symptom_description)
        
        # Calculate urgency first (may override everything)
        urgency = self.calculate_urgency(symptoms)
        
        # Match symptoms to conditions
        condition_matches = self._match_symptoms_to_conditions(symptom_list, severity, duration_hours)
        
        # Sort by confidence and get top 3
        top_conditions = sorted(condition_matches, key=lambda x: x["confidence"], reverse=True)[:3]
        
        # Generate follow-up questions
        follow_up_questions = self.ask_follow_up_questions(symptoms)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(urgency, top_conditions)
        
        return {
            "top_conditions": top_conditions,
            "urgency": urgency,
            "recommendations": recommendations,
            "follow_up_questions": follow_up_questions,
            "risk_factors": self._identify_risk_factors(symptoms),
            "suggested_specialists": self._suggest_specialists(top_conditions),
            "medical_disclaimer": (
                "This is a preliminary AI analysis and should not replace "
                "professional medical advice. Always consult with a qualified "
                "healthcare professional for accurate diagnosis and treatment."
            )
        }
    
    def _parse_symptoms_from_text(self, text: str) -> List[str]:
        """
        Extract symptoms from free-text description using NLP
        """
        text_lower = text.lower()
        extracted_symptoms = []
        
        # Build list of all known symptoms from knowledge base
        all_symptoms = set()
        for condition_data in self.medical_knowledge.values():
            all_symptoms.update(condition_data["symptoms"])
        
        # Find which symptoms are mentioned in the text
        for symptom in all_symptoms:
            if symptom in text_lower:
                extracted_symptoms.append(symptom)
        
        # Also extract common symptom patterns
        symptom_patterns = [
            r"pain in ([\w\s]+)",
            r"([\w]+) pain",
            r"feeling ([\w]+)",
            r"have ([\w\s]+)"
        ]
        
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    match = " ".join(match)
                if match and len(match.strip()) > 2:
                    extracted_symptoms.append(match.strip())
        
        return list(set(extracted_symptoms))  # Remove duplicates
    
    def _match_symptoms_to_conditions(self, symptom_list: List[str], severity: int, duration_hours: int) -> List[Dict]:
        """
        Match provided symptoms to medical conditions
        Returns list of conditions with confidence scores
        """
        condition_matches = []
        duration_days = duration_hours / 24.0
        
        for condition_name, condition_data in self.medical_knowledge.items():
            # Calculate symptom overlap
            condition_symptoms = set(condition_data["symptoms"])
            patient_symptoms = set([s.lower() for s in symptom_list])
            
            # Find matching symptoms
            matching_symptoms = condition_symptoms.intersection(patient_symptoms)
            
            if not matching_symptoms:
                # Try partial matching (e.g., "head" in "headache")
                for ps in patient_symptoms:
                    for cs in condition_symptoms:
                        if ps in cs or cs in ps:
                            matching_symptoms.add(cs)
            
            if len(matching_symptoms) > 0:
                # Calculate confidence based on:
                # 1. Percentage of condition's symptoms that match
                # 2. Severity alignment
                # 3. Duration alignment
                
                symptom_match_score = len(matching_symptoms) / len(condition_symptoms)
                
                # Check severity alignment
                sev_min, sev_max = condition_data["severity_range"]
                severity_match = 1.0 if sev_min <= severity <= sev_max else 0.5
                
                # Check duration alignment
                dur_min, dur_max = condition_data["duration_days"]
                duration_match = 1.0 if dur_min <= duration_days <= dur_max else 0.7
                
                # Combined confidence (weighted average)
                confidence = (
                    symptom_match_score * 0.6 +
                    severity_match * 0.2 +
                    duration_match * 0.2
                )
                
                condition_matches.append({
                    "name": condition_name.replace("_", " ").title(),
                    "confidence": round(confidence, 2),
                    "icd10": condition_data["icd10"],
                    "matching_symptoms": list(matching_symptoms)
                })
        
        return condition_matches
    
    def calculate_urgency(self, symptoms: Dict) -> str:
        """
        Calculate urgency level based on symptoms
        
        Factors considered:
        - Specific symptoms (chest pain = emergency)
        - Severity (>8/10 = urgent)
        - Duration (>72h = more urgent)
        - Age (elderly/children = higher urgency)
        - Pre-existing conditions
        
        Returns:
            'emergency' | 'urgent' | 'routine' | 'monitor'
        """
        severity = symptoms.get("severity", 5)
        duration_hours = symptoms.get("duration_hours", 0)
        symptom_description = symptoms.get("description", "").lower()
        symptom_list = [s.lower() for s in symptoms.get("symptoms", [])]
        age = symptoms.get("age", 40)
        pre_existing = symptoms.get("chronic_conditions", [])
        
        # Check for emergency symptoms (highest priority)
        for emergency_symptom in self.emergency_symptoms:
            if emergency_symptom in symptom_description or emergency_symptom in " ".join(symptom_list):
                return "emergency"
        
        # Check for high urgency symptoms
        urgency_count = 0
        for urgent_symptom in self.high_urgency_symptoms:
            if urgent_symptom in symptom_description or urgent_symptom in " ".join(symptom_list):
                urgency_count += 1
        
        # Age-based risk factors
        high_risk_age = age < 2 or age > 65
        
        # Decision logic
        if urgency_count >= 2 or (urgency_count >= 1 and high_risk_age):
            return "emergency"
        
        if severity >= 9:
            return "urgent"
        
        if severity >= 7 and (duration_hours > 48 or high_risk_age or len(pre_existing) > 0):
            return "urgent"
        
        if urgency_count >= 1:
            return "urgent"
        
        if severity >= 6 or (severity >= 5 and duration_hours > 72):
            return "routine"
        
        return "monitor"
    
    def ask_follow_up_questions(self, symptoms: Dict) -> List[str]:
        """
        Generate targeted follow-up questions to refine diagnosis
        
        Questions are dynamically selected based on initial symptoms
        to gather more specific information.
        """
        return self._get_follow_up_questions(symptoms)
    
    def _get_follow_up_questions(self, symptoms: Dict) -> List[str]:
        """Internal method to get follow-up questions based on symptoms"""
        questions = []
        symptom_description = symptoms.get("description", "").lower()
        symptom_list = [s.lower() for s in symptoms.get("symptoms", [])]
        all_symptoms = symptom_description + " " + " ".join(symptom_list)
        
        # General questions (always useful)
        general_questions = [
            "Have you had a fever in the last 24 hours? If yes, what temperature?",
            "Are you currently taking any medications?",
            "Do you have any known allergies (food, medication, environmental)?",
        ]
        
        # Symptom-specific questions
        if "pain" in all_symptoms:
            questions.append("On a scale of 1-10, how would you rate your pain?")
            questions.append("Is the pain constant or does it come and go?")
        
        if "cough" in all_symptoms:
            questions.append("Is your cough dry or are you producing mucus?")
            questions.append("Is there any blood in your mucus?")
        
        if "fever" in all_symptoms or "temperature" in all_symptoms:
            questions.append("Have you taken any fever-reducing medication (like acetaminophen or ibuprofen)?")
        
        if "nausea" in all_symptoms or "vomiting" in all_symptoms:
            questions.append("Are you able to keep fluids down?")
            questions.append("Have you noticed any blood in vomit?")
        
        if "headache" in all_symptoms:
            questions.append("Where exactly is the headache located?")
            questions.append("Did the headache come on suddenly or gradually?")
        
        if "breathing" in all_symptoms or "breath" in all_symptoms:
            questions.append("Are you able to speak full sentences without getting short of breath?")
            questions.append("Does the breathing difficulty get worse with exertion?")
        
        # Combine and limit to 5-6 questions
        all_questions = general_questions + questions
        return all_questions[:6]
    
    def _identify_risk_factors(self, symptoms: Dict) -> List[str]:
        """Identify risk factors that may affect diagnosis/treatment"""
        risk_factors = []
        
        age = symptoms.get("age", 40)
        if age < 2:
            risk_factors.append("Infant - requires special care considerations")
        elif age < 12:
            risk_factors.append("Child - pediatric assessment recommended")
        elif age > 65:
            risk_factors.append("Elderly - increased risk for complications")
        
        if symptoms.get("pregnant", False):
            risk_factors.append("Pregnancy - requires specialized care")
        
        chronic_conditions = symptoms.get("chronic_conditions", [])
        if chronic_conditions:
            risk_factors.append(f"Pre-existing conditions: {', '.join(chronic_conditions)}")
        
        if symptoms.get("immunocompromised", False):
            risk_factors.append("Immunocompromised - higher infection risk")
        
        return risk_factors
    
    def _suggest_specialists(self, top_conditions: List[Dict]) -> List[str]:
        """Suggest medical specialists based on probable conditions"""
        specialists = set()
        
        # Map conditions to specialists
        specialist_mapping = {
            "respiratory": ["pulmonologist", "respiratory therapist"],
            "cardiac": ["cardiologist"],
            "gastrointestinal": ["gastroenterologist"],
            "neurological": ["neurologist"],
            "urinary": ["urologist"],
            "mental_health": ["psychiatrist", "psychologist"],
            "allergies": ["allergist", "immunologist"]
        }
        
        for condition in top_conditions:
            condition_name = condition["name"].lower()
            icd10 = condition["icd10"]
            
            # Map by ICD-10 code first letter
            if icd10.startswith("J"):  # Respiratory
                specialists.update(["general practitioner", "pulmonologist"])
            elif icd10.startswith("I"):  # Cardiovascular
                specialists.update(["cardiologist"])
            elif icd10.startswith("K"):  # Digestive
                specialists.update(["gastroenterologist"])
            elif icd10.startswith("G"):  # Neurological
                specialists.update(["neurologist"])
            elif icd10.startswith("N"):  # Genitourinary
                specialists.update(["urologist"])
            elif icd10.startswith("F"):  # Mental/behavioral
                specialists.update(["psychiatrist"])
            else:
                specialists.add("general practitioner")
        
        return list(specialists) if specialists else ["general practitioner"]
    
    def _generate_recommendations(self, urgency: str, top_conditions: Optional[List[Dict]] = None) -> List[str]:
        """Generate recommendations based on urgency level and conditions"""
        base_recommendations = {
            "emergency": [
                "🚨 Seek emergency medical care IMMEDIATELY",
                "Call emergency services (911 or local equivalent)",
                "Do not drive yourself - ask someone or call ambulance",
                "Do not wait - this could be life-threatening"
            ],
            "urgent": [
                "Schedule a consultation with a doctor within 24 hours",
                "Monitor symptoms closely and seek emergency care if they worsen",
                "Avoid strenuous activities",
                "Stay hydrated and rest",
                "Keep a record of your symptoms"
            ],
            "routine": [
                "Schedule a check-up with your primary care doctor within 1-2 weeks",
                "Rest and monitor symptoms",
                "Maintain a healthy diet and stay hydrated",
                "Over-the-counter medications may help with minor symptoms (consult pharmacist)",
                "Document any changes in symptoms"
            ],
            "monitor": [
                "Continue monitoring symptoms for 24-48 hours",
                "Rest and maintain good health practices",
                "Consult a doctor if symptoms worsen or persist beyond 3-5 days",
                "Stay hydrated and eat nutritious meals",
                "Document symptoms in a diary"
            ]
        }
        
        recommendations = base_recommendations.get(urgency, base_recommendations["monitor"]).copy()
        
        # Add condition-specific recommendations
        if top_conditions:
            for condition in top_conditions[:2]:  # Top 2 conditions
                condition_name = condition["name"].lower()
                
                if "cold" in condition_name or "flu" in condition_name:
                    recommendations.append("💊 Get plenty of rest and drink warm fluids")
                    recommendations.append("Consider vitamin C supplements")
                
                if "gastro" in condition_name:
                    recommendations.append("💧 Stay hydrated - drink small amounts frequently")
                    recommendations.append("Avoid solid foods until vomiting stops")
                
                if "allergic" in condition_name or "allergy" in condition_name:
                    recommendations.append("🌿 Identify and avoid allergen triggers if possible")
                    recommendations.append("Consider over-the-counter antihistamines")
        
        return recommendations
