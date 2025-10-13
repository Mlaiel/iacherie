"""Analytics service for IA2GOOD module"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from models.case import Case
from models.volunteer import VolunteerProfile
from models.assignment import Assignment


class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_global_stats(self) -> Dict:
        """
        Get global platform statistics
        
        Returns:
            Dictionary of global stats
        """
        total_cases = self.db.query(Case).filter(
            Case.deleted_at.is_(None)
        ).count()
        
        open_cases = self.db.query(Case).filter(
            Case.status == 'open',
            Case.deleted_at.is_(None)
        ).count()
        
        completed_cases = self.db.query(Case).filter(
            Case.status == 'completed'
        ).count()
        
        total_volunteers = self.db.query(VolunteerProfile).count()
        
        active_volunteers = self.db.query(VolunteerProfile).filter(
            VolunteerProfile.availability_status == True,
            VolunteerProfile.verification_status == 'verified'
        ).count()
        
        total_assignments = self.db.query(Assignment).count()
        
        return {
            'total_cases': total_cases,
            'open_cases': open_cases,
            'completed_cases': completed_cases,
            'total_volunteers': total_volunteers,
            'active_volunteers': active_volunteers,
            'total_assignments': total_assignments,
            'completion_rate': (completed_cases / total_cases * 100) if total_cases > 0 else 0
        }
    
    def get_case_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get case statistics for a time period
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Case statistics
        """
        query = self.db.query(Case).filter(Case.deleted_at.is_(None))
        
        if start_date:
            query = query.filter(Case.created_at >= start_date)
        if end_date:
            query = query.filter(Case.created_at <= end_date)
        
        cases = query.all()
        
        if not cases:
            return {}
        
        # Type distribution
        type_counts = {}
        status_counts = {}
        urgency_distribution = {}
        
        for case in cases:
            # Count by type
            type_counts[case.type] = type_counts.get(case.type, 0) + 1
            
            # Count by status
            status_counts[case.status] = status_counts.get(case.status, 0) + 1
            
            # Urgency distribution
            urgency = case.urgency_level or 5
            urgency_distribution[urgency] = urgency_distribution.get(urgency, 0) + 1
        
        # Average urgency
        avg_urgency = sum(c.urgency_level or 5 for c in cases) / len(cases)
        
        return {
            'total_cases': len(cases),
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'urgency_distribution': urgency_distribution,
            'average_urgency': round(avg_urgency, 2)
        }
    
    def get_volunteer_statistics(
        self,
        volunteer_id: Optional[UUID] = None
    ) -> Dict:
        """
        Get volunteer statistics
        
        Args:
            volunteer_id: Optional volunteer ID for individual stats
            
        Returns:
            Volunteer statistics
        """
        if volunteer_id:
            # Individual volunteer stats
            volunteer = self.db.query(VolunteerProfile).filter(
                VolunteerProfile.id == volunteer_id
            ).first()
            
            if not volunteer:
                return {}
            
            assignments = self.db.query(Assignment).filter(
                Assignment.volunteer_id == volunteer_id
            ).all()
            
            return {
                'volunteer_id': str(volunteer.id),
                'total_cases_completed': volunteer.total_cases_completed,
                'total_hours_volunteered': volunteer.total_hours_volunteered,
                'reliability_score': volunteer.reliability_score,
                'average_rating': volunteer.average_rating,
                'total_ratings': volunteer.total_ratings,
                'total_assignments': len(assignments),
                'completed_assignments': len([a for a in assignments if a.status == 'completed']),
                'active_assignments': len([a for a in assignments if a.status in ['pending', 'accepted', 'in_progress']])
            }
        else:
            # Global volunteer stats
            volunteers = self.db.query(VolunteerProfile).all()
            
            if not volunteers:
                return {}
            
            total_volunteers = len(volunteers)
            verified_volunteers = len([v for v in volunteers if v.verification_status == 'verified'])
            active_volunteers = len([v for v in volunteers if v.availability_status])
            
            # Skills distribution
            skill_counts = {}
            for volunteer in volunteers:
                for skill in volunteer.skills or []:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Average reliability
            avg_reliability = sum(v.reliability_score for v in volunteers) / total_volunteers
            
            return {
                'total_volunteers': total_volunteers,
                'verified_volunteers': verified_volunteers,
                'active_volunteers': active_volunteers,
                'skill_distribution': skill_counts,
                'average_reliability_score': round(avg_reliability, 2)
            }
    
    def get_assignment_statistics(self) -> Dict:
        """
        Get assignment statistics
        
        Returns:
            Assignment statistics
        """
        assignments = self.db.query(Assignment).all()
        
        if not assignments:
            return {}
        
        # Status distribution
        status_counts = {}
        for assignment in assignments:
            status_counts[assignment.status] = status_counts.get(assignment.status, 0) + 1
        
        # Average response time
        response_times = [a.response_time_minutes for a in assignments if a.response_time_minutes]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Average completion time
        completion_times = [a.completion_time_minutes for a in assignments if a.completion_time_minutes]
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Average match score
        match_scores = [a.match_score for a in assignments if a.match_score]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
        
        return {
            'total_assignments': len(assignments),
            'status_distribution': status_counts,
            'average_response_time_minutes': round(avg_response_time, 2),
            'average_completion_time_minutes': round(avg_completion_time, 2),
            'average_match_score': round(avg_match_score, 2)
        }
    
    def get_leaderboard(
        self,
        metric: str = 'cases_completed',
        limit: int = 10
    ) -> List[Dict]:
        """
        Get volunteer leaderboard
        
        Args:
            metric: Metric to sort by (cases_completed, hours, rating, reliability)
            limit: Number of results
            
        Returns:
            List of top volunteers
        """
        query = self.db.query(VolunteerProfile).filter(
            VolunteerProfile.verification_status == 'verified'
        )
        
        if metric == 'cases_completed':
            query = query.order_by(VolunteerProfile.total_cases_completed.desc())
        elif metric == 'hours':
            query = query.order_by(VolunteerProfile.total_hours_volunteered.desc())
        elif metric == 'rating':
            query = query.order_by(VolunteerProfile.average_rating.desc())
        elif metric == 'reliability':
            query = query.order_by(VolunteerProfile.reliability_score.desc())
        
        volunteers = query.limit(limit).all()
        
        leaderboard = []
        for rank, volunteer in enumerate(volunteers, 1):
            leaderboard.append({
                'rank': rank,
                'volunteer_id': str(volunteer.id),
                'user_id': str(volunteer.user_id),
                'cases_completed': volunteer.total_cases_completed,
                'hours_volunteered': volunteer.total_hours_volunteered,
                'average_rating': volunteer.average_rating,
                'reliability_score': volunteer.reliability_score
            })
        
        return leaderboard
    
    def get_geographic_heatmap(self) -> List[Dict]:
        """
        Get geographic distribution of cases
        
        Returns:
            List of locations with case counts
        """
        # Group cases by city
        city_counts = self.db.query(
            Case.city,
            func.count(Case.id).label('count')
        ).filter(
            Case.deleted_at.is_(None),
            Case.city.isnot(None)
        ).group_by(Case.city).all()
        
        heatmap = []
        for city, count in city_counts:
            heatmap.append({
                'city': city,
                'case_count': count
            })
        
        return heatmap
