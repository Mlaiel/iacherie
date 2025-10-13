"""
Celery tasks for analytics in IA2GOOD module
"""
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from celery import Task
from .celery_app import celery_app

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from microservices.ia2good.services.analytics_service import AnalyticsService
except ImportError:
    print("Warning: Could not import AnalyticsService")
    AnalyticsService = None


class AnalyticsTask(Task):
    """Base task with analytics service setup"""
    _analytics_service = None
    
    @property
    def analytics_service(self):
        if self._analytics_service is None and AnalyticsService:
            self._analytics_service = AnalyticsService()
        return self._analytics_service


@celery_app.task(base=AnalyticsTask, bind=True)
def aggregate_daily_metrics(
    self,
    date: str = None
) -> Dict[str, Any]:
    """
    Aggregate daily metrics for analytics dashboard
    
    This task runs daily at 1 AM to aggregate:
    - Cases created, completed, cancelled
    - Volunteers active, new registrations
    - Response times (avg, median, p95)
    - Completion times
    - Matching success rate
    - Geographic distribution
    
    Args:
        date: Optional date string (YYYY-MM-DD), defaults to yesterday
        
    Returns:
        Dict with aggregated metrics
    """
    try:
        # Default to yesterday if no date provided
        if date:
            target_date = datetime.fromisoformat(date).date()
        else:
            target_date = (datetime.utcnow() - timedelta(days=1)).date()
        
        print(f"Aggregating metrics for {target_date}")
        
        # Initialize metrics
        metrics = {
            'date': target_date.isoformat(),
            'cases': {
                'created': 0,
                'completed': 0,
                'cancelled': 0,
                'open': 0,
                'in_progress': 0,
                'by_type': defaultdict(int),
                'by_urgency': defaultdict(int)
            },
            'volunteers': {
                'active': 0,
                'new_registrations': 0,
                'total_verified': 0
            },
            'performance': {
                'avg_response_time_minutes': 0,
                'median_response_time_minutes': 0,
                'p95_response_time_minutes': 0,
                'avg_completion_time_minutes': 0,
                'matching_success_rate': 0
            },
            'geography': {
                'cities': defaultdict(int),
                'regions': defaultdict(int)
            }
        }
        
        # TODO: Query database for actual metrics
        # Cases created on target_date
        # SELECT COUNT(*) FROM ia2good_cases WHERE DATE(created_at) = target_date
        
        # Cases completed on target_date
        # SELECT COUNT(*) FROM ia2good_cases WHERE DATE(completed_at) = target_date
        
        # Active volunteers (accepted/completed assignments)
        # SELECT COUNT(DISTINCT volunteer_id) 
        # FROM ia2good_case_assignments 
        # WHERE DATE(accepted_at) = target_date OR DATE(completed_at) = target_date
        
        # Response times
        # SELECT 
        #   AVG(response_time_minutes),
        #   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_minutes),
        #   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_minutes)
        # FROM ia2good_case_assignments
        # WHERE DATE(accepted_at) = target_date
        
        # Store aggregated metrics in database
        # INSERT INTO ia2good_analytics_daily (date, metrics) 
        # VALUES (target_date, metrics)
        # ON CONFLICT (date) DO UPDATE SET metrics = EXCLUDED.metrics
        
        print(f"Aggregated metrics: {metrics['cases']['created']} cases created")
        return metrics
        
    except Exception as exc:
        print(f"Error aggregating daily metrics: {exc}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@celery_app.task(base=AnalyticsTask, bind=True)
def update_volunteer_statistics(
    self,
    volunteer_id: str = None
) -> Dict[str, Any]:
    """
    Update volunteer statistics (runs hourly or on-demand)
    
    Updates:
    - Total cases completed
    - Total hours volunteered
    - Average rating
    - Reliability score
    - Response time statistics
    
    Args:
        volunteer_id: Optional specific volunteer ID, or None to update all active
        
    Returns:
        Dict with update statistics
    """
    try:
        updated_count = 0
        
        if volunteer_id:
            # Update single volunteer
            volunteers = [volunteer_id]
        else:
            # Get all volunteers with recent activity (last 24h)
            # SELECT DISTINCT volunteer_id 
            # FROM ia2good_case_assignments
            # WHERE updated_at > NOW() - INTERVAL '24 hours'
            volunteers = []  # TODO: Fetch from DB
        
        for vol_id in volunteers:
            try:
                # Calculate statistics for volunteer
                stats = {
                    'total_cases_completed': 0,
                    'total_hours_volunteered': 0,
                    'average_rating': 0.0,
                    'total_ratings': 0,
                    'reliability_score': 100.0,
                    'avg_response_time_minutes': 0,
                    'updated_at': datetime.utcnow()
                }
                
                # TODO: Query assignments for this volunteer
                # Total completed
                # SELECT COUNT(*) FROM ia2good_case_assignments
                # WHERE volunteer_id = vol_id AND status = 'completed'
                
                # Total hours (sum of completion times)
                # SELECT SUM(completion_time_minutes) / 60.0
                # FROM ia2good_case_assignments
                # WHERE volunteer_id = vol_id AND status = 'completed'
                
                # Average rating
                # SELECT AVG(volunteer_rating), COUNT(volunteer_rating)
                # FROM ia2good_case_assignments
                # WHERE volunteer_id = vol_id AND volunteer_rating IS NOT NULL
                
                # Reliability score calculation
                # completed_count / (completed_count + cancelled_count) * 100
                # with adjustments for response time and ratings
                
                # Update volunteer profile
                # UPDATE ia2good_volunteer_profiles
                # SET 
                #   total_cases_completed = stats['total_cases_completed'],
                #   total_hours_volunteered = stats['total_hours_volunteered'],
                #   average_rating = stats['average_rating'],
                #   reliability_score = stats['reliability_score'],
                #   updated_at = NOW()
                # WHERE id = vol_id
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating stats for volunteer {vol_id}: {e}")
        
        print(f"Updated statistics for {updated_count} volunteer(s)")
        return {
            'updated': updated_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        print(f"Error updating volunteer statistics: {exc}")
        return {'updated': 0, 'error': str(exc)}


@celery_app.task(base=AnalyticsTask, bind=True)
def calculate_matching_metrics(
    self,
    period_hours: int = 24
) -> Dict[str, Any]:
    """
    Calculate matching algorithm performance metrics
    
    Args:
        period_hours: Time period to analyze (default 24 hours)
        
    Returns:
        Dict with matching metrics
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=period_hours)
        
        metrics = {
            'period_hours': period_hours,
            'total_assignments': 0,
            'accepted_assignments': 0,
            'declined_assignments': 0,
            'acceptance_rate': 0.0,
            'avg_match_score': 0.0,
            'avg_response_time_minutes': 0.0,
            'high_score_acceptance_rate': 0.0,  # Score > 80
            'low_score_acceptance_rate': 0.0   # Score < 50
        }
        
        # TODO: Query assignments in period
        # SELECT 
        #   COUNT(*) as total,
        #   SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
        #   SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined,
        #   AVG(match_score) as avg_score,
        #   AVG(response_time_minutes) as avg_response
        # FROM ia2good_case_assignments
        # WHERE assigned_at > cutoff
        
        # Calculate acceptance rates by match score brackets
        # High score (>80): How many were accepted?
        # Low score (<50): How many were accepted?
        
        if metrics['total_assignments'] > 0:
            metrics['acceptance_rate'] = metrics['accepted_assignments'] / metrics['total_assignments'] * 100
        
        print(f"Matching metrics for last {period_hours}h: {metrics['acceptance_rate']:.1f}% acceptance rate")
        return metrics
        
    except Exception as exc:
        print(f"Error calculating matching metrics: {exc}")
        return metrics


@celery_app.task(base=AnalyticsTask, bind=True)
def generate_impact_report(
    self,
    month: str = None
) -> Dict[str, Any]:
    """
    Generate monthly impact report
    
    Args:
        month: Month string (YYYY-MM), defaults to last month
        
    Returns:
        Dict with impact metrics
    """
    try:
        # Default to last month if not provided
        if month:
            target_month = datetime.strptime(month, '%Y-%m')
        else:
            now = datetime.utcnow()
            target_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        
        month_str = target_month.strftime('%Y-%m')
        print(f"Generating impact report for {month_str}")
        
        report = {
            'month': month_str,
            'cases': {
                'total_created': 0,
                'total_completed': 0,
                'completion_rate': 0.0,
                'by_type': {}
            },
            'volunteers': {
                'total_active': 0,
                'total_hours': 0,
                'new_volunteers': 0
            },
            'impact': {
                'people_helped': 0,
                'animals_rescued': 0,
                'emergencies_resolved': 0,
                'avg_satisfaction_rating': 0.0
            },
            'geographic': {
                'cities_covered': 0,
                'regions_covered': 0,
                'total_distance_km': 0.0
            },
            'community': {
                'total_ratings': 0,
                'avg_volunteer_rating': 0.0,
                'top_volunteers': []
            }
        }
        
        # TODO: Query database for monthly statistics
        # All cases in target month
        # All assignments completed in target month
        # Calculate totals, averages, distributions
        
        # Get top volunteers (by cases completed)
        # SELECT volunteer_id, COUNT(*) as cases_completed
        # FROM ia2good_case_assignments
        # WHERE DATE_TRUNC('month', completed_at) = target_month
        # GROUP BY volunteer_id
        # ORDER BY cases_completed DESC
        # LIMIT 10
        
        print(f"Impact report generated: {report['cases']['total_completed']} cases completed")
        return report
        
    except Exception as exc:
        print(f"Error generating impact report: {exc}")
        return report


@celery_app.task(bind=True)
def cleanup_old_analytics(
    self,
    retention_days: int = 365
) -> Dict[str, int]:
    """
    Clean up old analytics data (keep last N days)
    
    Args:
        retention_days: Number of days to retain (default 365)
        
    Returns:
        Dict with cleanup statistics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # TODO: Delete old analytics records
        # DELETE FROM ia2good_analytics_daily 
        # WHERE date < cutoff_date
        
        deleted = 0  # Count from DB
        
        print(f"Cleaned up analytics data older than {cutoff_date.date()}: {deleted} records")
        return {
            'deleted': deleted,
            'cutoff_date': cutoff_date.isoformat(),
            'retention_days': retention_days
        }
        
    except Exception as exc:
        print(f"Error cleaning up analytics: {exc}")
        return {'deleted': 0, 'error': str(exc)}
