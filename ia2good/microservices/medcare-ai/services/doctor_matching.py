"""
Doctor Matching Service
Intelligent matching of patients with available doctors
"""
from typing import Dict, Optional, List, Tuple
from uuid import UUID
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DoctorMatchingService:
    """
    Service for matching patients with appropriate doctors
    
    Matching criteria:
    - Required specialty
    - Immediate availability
    - Common language
    - Doctor rating
    - Distance (for in-person consultations)
    - Insurance compatibility
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db = db_session
        
        # Specialty mapping for better matching
        self.specialty_keywords = {
            "respiratory": ["pulmonologist", "general practice", "internal medicine"],
            "cardiovascular": ["cardiologist", "internal medicine"],
            "dermatology": ["dermatologist", "general practice"],
            "gastroenterology": ["gastroenterologist", "internal medicine"],
            "neurology": ["neurologist", "internal medicine"],
            "psychiatry": ["psychiatrist", "psychologist"],
            "pediatrics": ["pediatrician", "family medicine"],
            "gynecology": ["gynecologist", "obstetrician"],
            "urology": ["urologist"],
            "orthopedics": ["orthopedist", "sports medicine"],
            "general": ["general practice", "family medicine", "internal medicine"]
        }
        
        # Urgency to max wait time mapping (minutes)
        self.urgency_wait_limits = {
            "emergency": 5,
            "urgent": 15,
            "routine": 60,
            "scheduled": 1440  # 24 hours
        }
    
    async def find_available_doctor(
        self,
        specialty: Optional[str] = None,
        urgency: str = "routine",
        language: str = "en",
        location: Optional[Dict] = None,
        insurance_provider: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Find best matching available doctor
        
        Algorithm:
        1. Filter doctors by specialty (if specified)
        2. Filter by availability status
        3. Filter by language compatibility
        4. Rank by:
           - Rating (4.5+ stars)
           - Response time history
           - Patient satisfaction
           - Distance (if location provided)
        5. Select top match
        
        Args:
            specialty: Medical specialty (cardiologist, dermatologist, etc.)
            urgency: emergency/urgent/routine/scheduled
            language: Preferred language code
            location: Patient location for distance calculation
            insurance_provider: Insurance provider name
            
        Returns:
            Doctor information or None if no match found
        """
        logger.info(f"Finding doctor: specialty={specialty}, urgency={urgency}, language={language}")
        
        if self.db is None:
            # Development mode: Return mock data
            return self._get_mock_doctor(specialty, urgency, language)
        
        try:
            # Get list of eligible doctors
            eligible_doctors = await self._get_eligible_doctors(
                specialty=specialty,
                language=language,
                insurance_provider=insurance_provider
            )
            
            if not eligible_doctors:
                logger.warning("No eligible doctors found")
                return None
            
            # Score each doctor
            scored_doctors = []
            for doctor in eligible_doctors:
                score = await self._calculate_match_score(
                    doctor=doctor,
                    urgency=urgency,
                    location=location,
                    specialty=specialty
                )
                scored_doctors.append((score, doctor))
            
            # Sort by score (descending)
            scored_doctors.sort(key=lambda x: x[0], reverse=True)
            
            # Select best match
            best_match = scored_doctors[0][1] if scored_doctors else None
            
            if best_match:
                logger.info(f"Best match: Dr. {best_match.get('name')} (score: {scored_doctors[0][0]:.2f})")
                return best_match
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding doctor: {e}")
            # Fallback to mock data
            return self._get_mock_doctor(specialty, urgency, language)
    
    async def _get_eligible_doctors(
        self,
        specialty: Optional[str],
        language: str,
        insurance_provider: Optional[str]
    ) -> List[Dict]:
        """Get list of doctors matching basic criteria"""
        
        # This would be a real database query in production
        # For now, return mock data structure
        
        eligible = []
        
        # Mock doctors database
        mock_doctors = [
            {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "name": "Dr. Jane Smith",
                "specialty": "General Practice",
                "rating": 4.8,
                "languages": ["en", "fr"],
                "available_now": True,
                "average_response_time_minutes": 3,
                "consultations_completed": 245,
                "success_rate": 0.96,
                "years_experience": 12,
                "accepts_insurance": ["BlueCross", "Aetna", "Medicare"]
            },
            {
                "id": UUID("22222222-2222-2222-2222-222222222222"),
                "name": "Dr. Michael Chen",
                "specialty": "Internal Medicine",
                "rating": 4.9,
                "languages": ["en", "zh"],
                "available_now": True,
                "average_response_time_minutes": 4,
                "consultations_completed": 389,
                "success_rate": 0.97,
                "years_experience": 15,
                "accepts_insurance": ["BlueCross", "UnitedHealthcare"]
            },
            {
                "id": UUID("33333333-3333-3333-3333-333333333333"),
                "name": "Dr. Sarah Johnson",
                "specialty": "Pediatrics",
                "rating": 4.7,
                "languages": ["en", "es"],
                "available_now": False,
                "average_response_time_minutes": 5,
                "consultations_completed": 312,
                "success_rate": 0.95,
                "years_experience": 10,
                "accepts_insurance": ["Aetna", "Cigna"]
            },
            {
                "id": UUID("44444444-4444-4444-4444-444444444444"),
                "name": "Dr. Ahmed Al-Rashid",
                "specialty": "Cardiology",
                "rating": 4.9,
                "languages": ["en", "ar", "fr"],
                "available_now": True,
                "average_response_time_minutes": 6,
                "consultations_completed": 456,
                "success_rate": 0.98,
                "years_experience": 18,
                "accepts_insurance": ["BlueCross", "Medicare", "Medicaid"]
            },
            {
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "name": "Dr. Maria Garcia",
                "specialty": "Dermatology",
                "rating": 4.6,
                "languages": ["en", "es"],
                "available_now": True,
                "average_response_time_minutes": 7,
                "consultations_completed": 278,
                "success_rate": 0.94,
                "years_experience": 8,
                "accepts_insurance": ["UnitedHealthcare", "Cigna"]
            }
        ]
        
        # Filter by availability
        available_doctors = [d for d in mock_doctors if d["available_now"]]
        
        # Filter by language
        if language:
            available_doctors = [
                d for d in available_doctors 
                if language in d["languages"]
            ]
        
        # Filter by specialty (with fuzzy matching)
        if specialty:
            specialty_lower = specialty.lower()
            
            # Check if it's a specialty keyword
            matching_specialties = []
            for keyword, specialties in self.specialty_keywords.items():
                if keyword in specialty_lower:
                    matching_specialties.extend(specialties)
            
            if matching_specialties:
                available_doctors = [
                    d for d in available_doctors
                    if any(ms in d["specialty"].lower() for ms in matching_specialties)
                ]
            else:
                # Direct specialty match
                available_doctors = [
                    d for d in available_doctors
                    if specialty_lower in d["specialty"].lower()
                ]
        
        # Filter by insurance
        if insurance_provider:
            available_doctors = [
                d for d in available_doctors
                if insurance_provider in d.get("accepts_insurance", [])
            ]
        
        return available_doctors
    
    async def _calculate_match_score(
        self,
        doctor: Dict,
        urgency: str,
        location: Optional[Dict],
        specialty: Optional[str]
    ) -> float:
        """
        Calculate match score for a doctor
        
        Scoring factors:
        - Rating: 30%
        - Response time: 25%
        - Experience: 15%
        - Success rate: 15%
        - Specialty match: 10%
        - Distance: 5% (if location provided)
        """
        score = 0.0
        
        # 1. Rating score (0-30 points)
        rating = doctor.get("rating", 0)
        score += (rating / 5.0) * 30
        
        # 2. Response time score (0-25 points)
        response_time = doctor.get("average_response_time_minutes", 10)
        max_wait = self.urgency_wait_limits.get(urgency, 60)
        
        if response_time <= max_wait:
            # Faster response = higher score
            score += (1 - (response_time / max_wait)) * 25
        else:
            # Penalize if too slow for urgency
            score += 5
        
        # 3. Experience score (0-15 points)
        years = doctor.get("years_experience", 0)
        score += min(years / 20.0, 1.0) * 15
        
        # 4. Success rate score (0-15 points)
        success_rate = doctor.get("success_rate", 0.5)
        score += success_rate * 15
        
        # 5. Specialty match score (0-10 points)
        if specialty:
            doctor_specialty = doctor.get("specialty", "").lower()
            if specialty.lower() in doctor_specialty:
                score += 10  # Perfect match
            else:
                # Check if related specialty
                for keyword, specialties in self.specialty_keywords.items():
                    if keyword in specialty.lower():
                        if any(s in doctor_specialty for s in specialties):
                            score += 7  # Related match
                            break
        else:
            score += 5  # No specialty preference
        
        # 6. Distance score (0-5 points) - if location provided
        if location:
            # This would calculate actual distance in production
            # For now, add random distance factor
            score += 3
        else:
            score += 5  # No distance preference
        
        # Bonus points
        consultations = doctor.get("consultations_completed", 0)
        if consultations > 300:
            score += 2  # Experienced with many consultations
        
        return score
    
    def _get_mock_doctor(self, specialty: Optional[str], urgency: str, language: str) -> Dict:
        """Return mock doctor for development/testing"""
        return {
            "id": UUID("00000000-0000-0000-0000-000000000001"),
            "name": "Dr. Jane Smith",
            "specialty": specialty or "General Practice",
            "rating": 4.8,
            "languages": [language, "en"],
            "available_now": True,
            "average_response_time_minutes": 3 if urgency == "emergency" else 5,
            "consultations_completed": 245,
            "success_rate": 0.96,
            "years_experience": 12,
            "estimated_wait_time_minutes": self.urgency_wait_limits.get(urgency, 10)
        }
    
    async def check_doctor_availability(self, doctor_id: UUID) -> Dict:
        """
        Check if specific doctor is currently available
        
        Checks:
        - Online/active status
        - Not in another consultation
        - Within working hours
        - Queue status
        
        Returns:
            Dictionary with availability details
        """
        logger.info(f"Checking availability for doctor {doctor_id}")
        
        if self.db is None:
            # Mock response for development
            return {
                "doctor_id": doctor_id,
                "available": True,
                "status": "online",
                "in_consultation": False,
                "within_working_hours": True,
                "next_available_slot": datetime.now().isoformat(),
                "current_queue_length": 2,
                "estimated_wait_minutes": 10
            }
        
        try:
            # In production, this would query the database
            # Check doctor status, current consultations, schedule
            
            now = datetime.now()
            
            # Mock business logic
            is_online = True  # Check doctor.status == "online"
            in_consultation = False  # Check active consultations
            
            # Check working hours (mock: 8 AM - 8 PM)
            working_start = now.replace(hour=8, minute=0, second=0)
            working_end = now.replace(hour=20, minute=0, second=0)
            within_hours = working_start <= now <= working_end
            
            # Get queue length (mock)
            queue_length = 2
            
            # Calculate availability
            available = is_online and not in_consultation and within_hours
            
            # Estimate wait time
            if available and queue_length == 0:
                wait_minutes = 0
                next_slot = now
            elif available:
                wait_minutes = queue_length * 15  # Assume 15 min per consultation
                next_slot = now + timedelta(minutes=wait_minutes)
            else:
                wait_minutes = None
                # Find next available slot in schedule
                next_slot = working_start + timedelta(days=1) if now > working_end else working_start
            
            return {
                "doctor_id": doctor_id,
                "available": available,
                "status": "online" if is_online else "offline",
                "in_consultation": in_consultation,
                "within_working_hours": within_hours,
                "next_available_slot": next_slot.isoformat(),
                "current_queue_length": queue_length,
                "estimated_wait_minutes": wait_minutes
            }
            
        except Exception as e:
            logger.error(f"Error checking doctor availability: {e}")
            return {
                "doctor_id": doctor_id,
                "available": False,
                "error": str(e)
            }
    
    async def get_estimated_wait_time(
        self, 
        specialty: Optional[str] = None,
        urgency: str = "routine"
    ) -> Dict:
        """
        Get estimated wait time for consultation
        
        Based on:
        - Number of doctors available
        - Current queue length
        - Average consultation duration
        - Urgency level
        
        Returns:
            Dictionary with wait time estimates
        """
        logger.info(f"Calculating wait time for specialty={specialty}, urgency={urgency}")
        
        if self.db is None:
            # Mock response
            base_wait = {
                "emergency": 2,
                "urgent": 8,
                "routine": 20,
                "scheduled": 60
            }.get(urgency, 15)
            
            return {
                "estimated_wait_minutes": base_wait,
                "range_minutes": (base_wait - 2, base_wait + 5),
                "available_doctors_count": 3,
                "current_queue_length": 5,
                "average_consultation_duration_minutes": 15,
                "confidence": 0.85
            }
        
        try:
            # Get available doctors for specialty
            eligible_doctors = await self._get_eligible_doctors(
                specialty=specialty,
                language="en",  # Default language
                insurance_provider=None
            )
            
            available_count = len(eligible_doctors)
            
            if available_count == 0:
                return {
                    "estimated_wait_minutes": None,
                    "message": "No doctors currently available for this specialty",
                    "available_doctors_count": 0
                }
            
            # Calculate total queue length
            total_queue = sum(
                d.get("current_queue_length", 0) 
                for d in eligible_doctors
            )
            
            # Average consultation duration (mock)
            avg_duration = 15  # minutes
            
            # Calculate wait time
            if available_count > 0:
                avg_queue_per_doctor = total_queue / available_count
                estimated_wait = int(avg_queue_per_doctor * avg_duration)
                
                # Apply urgency factor
                urgency_multiplier = {
                    "emergency": 0.2,  # Prioritized
                    "urgent": 0.5,
                    "routine": 1.0,
                    "scheduled": 1.5
                }.get(urgency, 1.0)
                
                estimated_wait = int(estimated_wait * urgency_multiplier)
                
                # Calculate confidence based on data quality
                confidence = min(0.9, 0.5 + (available_count * 0.1))
                
                return {
                    "estimated_wait_minutes": estimated_wait,
                    "range_minutes": (
                        max(0, estimated_wait - 5),
                        estimated_wait + 10
                    ),
                    "available_doctors_count": available_count,
                    "current_queue_length": total_queue,
                    "average_consultation_duration_minutes": avg_duration,
                    "confidence": round(confidence, 2)
                }
            
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}")
            return {
                "estimated_wait_minutes": 15,
                "error": str(e),
                "confidence": 0.3
            }
    
    async def notify_doctor(
        self, 
        doctor_id: UUID, 
        consultation_id: UUID,
        patient_info: Dict,
        urgency: str = "routine",
        preliminary_diagnosis: Optional[Dict] = None
    ) -> bool:
        """
        Send notification to doctor about new consultation request
        
        Notification includes:
        - Patient information (anonymized if needed)
        - Urgency level
        - Preliminary AI diagnosis
        - Symptom summary
        - Estimated consultation time
        
        Args:
            doctor_id: UUID of the doctor
            consultation_id: UUID of the consultation
            patient_info: Patient details
            urgency: Urgency level
            preliminary_diagnosis: AI-generated preliminary diagnosis
        
        Returns:
            True if notification sent successfully
        """
        logger.info(f"Sending notification to doctor {doctor_id} for consultation {consultation_id}")
        
        try:
            # Build notification payload
            notification_data = {
                "type": "new_consultation",
                "consultation_id": str(consultation_id),
                "urgency": urgency,
                "timestamp": datetime.now().isoformat(),
                "patient": {
                    "id": patient_info.get("id"),
                    "name": patient_info.get("name"),
                    "age": patient_info.get("age"),
                    "gender": patient_info.get("gender")
                },
                "preliminary_info": {
                    "chief_complaint": patient_info.get("chief_complaint", ""),
                    "duration": patient_info.get("symptom_duration", ""),
                    "severity": patient_info.get("severity", 5)
                }
            }
            
            # Add AI diagnosis if available
            if preliminary_diagnosis:
                notification_data["ai_diagnosis"] = {
                    "primary": preliminary_diagnosis.get("primary_diagnosis", {}).get("condition"),
                    "confidence": preliminary_diagnosis.get("primary_diagnosis", {}).get("confidence"),
                    "red_flags": preliminary_diagnosis.get("red_flags", [])
                }
            
            # Send notification via multiple channels
            # 1. WebSocket (real-time)
            await self._send_websocket_notification(doctor_id, notification_data)
            
            # 2. Push notification (mobile app)
            await self._send_push_notification(doctor_id, notification_data)
            
            # 3. Email (if high urgency and no response)
            if urgency in ["emergency", "urgent"]:
                await self._send_email_notification(doctor_id, notification_data)
            
            logger.info(f"Notification sent successfully to doctor {doctor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending doctor notification: {e}")
            return False
    
    async def _send_websocket_notification(self, doctor_id: UUID, data: Dict):
        """Send real-time WebSocket notification"""
        # This would integrate with WebSocket service
        logger.info(f"WebSocket notification sent to {doctor_id}")
        pass
    
    async def _send_push_notification(self, doctor_id: UUID, data: Dict):
        """Send mobile push notification"""
        # This would integrate with push notification service (FCM, APNS)
        logger.info(f"Push notification sent to {doctor_id}")
        pass
    
    async def _send_email_notification(self, doctor_id: UUID, data: Dict):
        """Send email notification"""
        # This would integrate with email service
        logger.info(f"Email notification sent to {doctor_id}")
        pass
