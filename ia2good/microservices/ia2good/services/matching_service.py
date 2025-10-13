"""Volunteer Matching Service - Core matching algorithm"""
from typing import List, Tuple, Optional
from uuid import UUID
import math


class VolunteerMatchingService:
    """
    Service for matching volunteers to cases based on multiple criteria.
    
    Scoring Algorithm (0-100 points):
    - Skills Matching: 0-40 points
    - Distance Proximity: 0-30 points
    - Availability: 0-15 points
    - Reliability History: 0-15 points
    """
    
    def __init__(self, db_session=None):
        """Initialize matching service"""
        self.db = db_session
    
    def calculate_match_score(
        self,
        case: dict,
        volunteer: dict
    ) -> Tuple[float, dict]:
        """
        Calculate matching score between a case and a volunteer.
        
        Args:
            case: Case data dictionary
            volunteer: Volunteer profile dictionary
            
        Returns:
            Tuple of (score, reasons_dict)
        """
        # 1. Skills Matching (0-40 points)
        skills_score = self._calculate_skills_score(case, volunteer)
        
        # 2. Distance Proximity (0-30 points)
        distance_score = self._calculate_distance_score(case, volunteer)
        
        # 3. Availability (0-15 points)
        availability_score = self._calculate_availability_score(volunteer)
        
        # 4. Reliability History (0-15 points)
        reliability_score = self._calculate_reliability_score(volunteer)
        
        # Total score
        total_score = skills_score + distance_score + availability_score + reliability_score
        
        # Reasons for the score
        reasons = {
            "skills_score": round(skills_score, 2),
            "distance_score": round(distance_score, 2),
            "availability_score": round(availability_score, 2),
            "reliability_score": round(reliability_score, 2),
            "total_score": round(total_score, 2)
        }
        
        return (round(total_score, 2), reasons)
    
    def _calculate_skills_score(self, case: dict, volunteer: dict) -> float:
        """
        Calculate skills matching score (0-40 points).
        
        Logic:
        - Count matching skills between required and available
        - Each matching skill: +10 points
        - Bonus for certification: +5 points per certified skill
        - Max: 40 points
        """
        required_skills = case.get('ai_classification', {}).get('skills_needed', [])
        volunteer_skills = set(volunteer.get('skills', []))
        certifications = volunteer.get('certifications', {})
        
        if not required_skills:
            # If no specific skills required, give base score
            return 20.0
        
        matching_skills = set(required_skills) & volunteer_skills
        skills_score = len(matching_skills) * 10
        
        # Bonus for certifications
        certified_bonus = 0
        for skill in matching_skills:
            skill_key = f"{skill}_certified"
            if certifications.get(skill_key, False):
                certified_bonus += 5
        
        skills_score += certified_bonus
        
        # Cap at 40 points
        return min(skills_score, 40.0)
    
    def _calculate_distance_score(self, case: dict, volunteer: dict) -> float:
        """
        Calculate distance proximity score (0-30 points).
        
        Scoring:
        - < 2km: 30 points
        - 2-5km: 25 points
        - 5-10km: 20 points
        - 10-20km: 10 points
        - > 20km: 5 points
        """
        case_location = case.get('location', {})
        volunteer_location = volunteer.get('location', {})
        
        if not case_location or not volunteer_location:
            return 10.0  # Default medium score if location missing
        
        distance_km = self._calculate_distance(
            case_location.get('latitude'),
            case_location.get('longitude'),
            volunteer_location.get('latitude'),
            volunteer_location.get('longitude')
        )
        
        if distance_km < 2:
            return 30.0
        elif distance_km < 5:
            return 25.0
        elif distance_km < 10:
            return 20.0
        elif distance_km < 20:
            return 10.0
        else:
            return 5.0
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two geographic points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        # Earth's radius in km
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _calculate_availability_score(self, volunteer: dict) -> float:
        """
        Calculate availability score (0-15 points).
        
        Logic:
        - Available now: 15 points
        - Not available: 5 points
        """
        availability_status = volunteer.get('availability_status', False)
        
        if availability_status:
            return 15.0
        else:
            return 5.0  # Still give some points for future availability
    
    def _calculate_reliability_score(self, volunteer: dict) -> float:
        """
        Calculate reliability history score (0-15 points).
        
        Logic:
        - Base score: (reliability_score / 100) * 15
        - Bonus if reliability > 90%: +5 points
        - Penalty if reliability < 50%: -5 points
        """
        reliability = volunteer.get('reliability_score', 100.0)
        
        # Base score (0-15 based on reliability percentage)
        score = (reliability / 100.0) * 15.0
        
        # Bonus for excellent reliability
        if reliability > 90:
            score += 5.0
        
        # Penalty for poor reliability
        elif reliability < 50:
            score -= 5.0
        
        # Ensure score stays in range
        score = max(0.0, min(score, 20.0))
        
        return score
    
    def recommend_volunteers(
        self,
        case: dict,
        volunteers: List[dict],
        top_n: int = 10
    ) -> List[dict]:
        """
        Recommend top N volunteers for a case.
        
        Args:
            case: Case data dictionary
            volunteers: List of volunteer dictionaries
            top_n: Number of top matches to return
            
        Returns:
            List of volunteer matches with scores
        """
        matches = []
        
        for volunteer in volunteers:
            score, reasons = self.calculate_match_score(case, volunteer)
            
            match = {
                'volunteer_id': volunteer.get('id'),
                'volunteer_name': volunteer.get('user', {}).get('full_name', 'Unknown'),
                'match_score': score,
                'distance_km': self._calculate_distance(
                    case.get('location', {}).get('latitude', 0),
                    case.get('location', {}).get('longitude', 0),
                    volunteer.get('location', {}).get('latitude', 0),
                    volunteer.get('location', {}).get('longitude', 0)
                ),
                'skills_match': list(
                    set(case.get('ai_classification', {}).get('skills_needed', [])) &
                    set(volunteer.get('skills', []))
                ),
                'availability': volunteer.get('availability_status', False),
                'match_reasons': reasons
            }
            
            matches.append(match)
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top N
        return matches[:top_n]
    
    def can_auto_assign(self, match_score: float, urgency_level: int = 5) -> bool:
        """
        Determine if a case can be auto-assigned based on match score and urgency.
        
        Args:
            match_score: The calculated match score (0-100)
            urgency_level: Case urgency level (1-10)
            
        Returns:
            True if auto-assignment criteria are met
        """
        # High urgency cases (8-10) can be auto-assigned with lower threshold
        if urgency_level >= 8:
            return match_score >= 75.0
        
        # Normal cases need score >= 80
        return match_score >= 80.0
    
    def optimize_team(
        self,
        case: dict,
        volunteers: List[dict],
        required_skills: List[str],
        team_size: int = 3
    ) -> List[dict]:
        """
        Optimize team selection for multi-volunteer cases.
        
        Uses a greedy algorithm to select complementary volunteers:
        1. Select volunteer with highest match score
        2. For remaining slots, prioritize volunteers with complementary skills
        3. Minimize total distance
        4. Maximize total reliability
        
        Args:
            case: Case data
            volunteers: Available volunteers
            required_skills: Skills needed for the case
            team_size: Number of volunteers needed
            
        Returns:
            List of selected volunteers
        """
        if not volunteers or team_size < 1:
            return []
        
        # Calculate match scores for all volunteers
        scored_volunteers = []
        for volunteer in volunteers:
            score, reasons = self.calculate_match_score(case, volunteer)
            scored_volunteers.append({
                'volunteer': volunteer,
                'score': score,
                'skills': set(volunteer.get('skills', []))
            })
        
        # Sort by score
        scored_volunteers.sort(key=lambda x: x['score'], reverse=True)
        
        # Select team
        team = []
        covered_skills = set()
        required_skills_set = set(required_skills)
        
        for candidate in scored_volunteers:
            if len(team) >= team_size:
                break
            
            volunteer_skills = candidate['skills']
            
            # First volunteer: pick highest score
            if not team:
                team.append(candidate['volunteer'])
                covered_skills.update(volunteer_skills)
                continue
            
            # Subsequent volunteers: prioritize complementary skills
            new_skills = volunteer_skills - covered_skills
            required_new_skills = new_skills & required_skills_set
            
            # Skip if no new value added and we still need specific skills
            if not new_skills and covered_skills < required_skills_set:
                continue
            
            team.append(candidate['volunteer'])
            covered_skills.update(volunteer_skills)
        
        return team


# Utility functions for external use
def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Helper function to calculate distance between two points.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    service = VolunteerMatchingService()
    return service._calculate_distance(lat1, lon1, lat2, lon2)
