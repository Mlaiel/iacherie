"""AI Content Generation Repository

Enterprise-grade repository for AI-generated content management including
audio, text, image, and video content generation tracking and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import uuid
import json
import logging

from .base_repository import BaseRepository, RepositoryException
from ..models.ai_content_generation import AIContentGeneration

logger = logging.getLogger(__name__)

class AIContentGenerationRepository(BaseRepository[AIContentGeneration]):
    """
    Repository for AI content generation management with enterprise-grade
    features including generation tracking, quality metrics, and optimization.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize AI Content Generation Repository"""
        super().__init__(db_session, AIContentGeneration)
        
    def create_generation_task(self, 
                             user_id: int,
                             content_type: str,
                             generation_prompt: str,
                             ai_model_name: str,
                             parameters: Dict[str, Any],
                             priority: str = 'normal') -> AIContentGeneration:
        """
        Create new AI content generation task
        
        Args:
            user_id: User creating the content
            content_type: Type of content (audio, text, image, video)
            generation_prompt: AI generation prompt
            ai_model_name: AI model used for generation
            parameters: Generation parameters
            priority: Task priority (low, normal, high, urgent)
            
        Returns:
            Created AI content generation instance
        """
        try:
            generation_data = {
                'user_id': user_id,
                'content_type': content_type,
                'generation_prompt': generation_prompt,
                'ai_model_name': ai_model_name,
                'parameters': json.dumps(parameters) if isinstance(parameters, dict) else parameters,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            generation = self.create(**generation_data)
            
            self.logger.info(f"Created AI generation task ID: {generation.id} for user: {user_id}")
            return generation
            
        except Exception as e:
            raise RepositoryException(f"Failed to create AI generation task: {str(e)}")
            
    def update_generation_status(self, 
                                generation_id: int,
                                status: str,
                                result_data: Optional[Dict[str, Any]] = None,
                                error_message: Optional[str] = None) -> Optional[AIContentGeneration]:
        """
        Update AI generation task status and results
        
        Args:
            generation_id: Generation task ID
            status: New status (pending, processing, completed, failed)
            result_data: Generation results data
            error_message: Error message if failed
            
        Returns:
            Updated generation instance
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if status == 'processing':
                update_data['started_at'] = datetime.utcnow()
            elif status in ['completed', 'failed']:
                update_data['completed_at'] = datetime.utcnow()
                
            if result_data:
                update_data['result_data'] = json.dumps(result_data)
                
            if error_message:
                update_data['error_message'] = error_message
                
            generation = self.update(generation_id, **update_data)
            
            if generation:
                self.logger.info(f"Updated generation task {generation_id} status to: {status}")
                
            return generation
            
        except Exception as e:
            raise RepositoryException(f"Failed to update generation status: {str(e)}")
            
    def get_user_generations(self, 
                           user_id: int,
                           content_type: Optional[str] = None,
                           status: Optional[str] = None,
                           limit: int = 50,
                           offset: int = 0) -> List[AIContentGeneration]:
        """
        Get user's AI content generations with filtering
        
        Args:
            user_id: User ID
            content_type: Filter by content type
            status: Filter by status
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of user's AI content generations
        """
        try:
            filters = {'user_id': user_id}
            
            if content_type:
                filters['content_type'] = content_type
                
            if status:
                filters['status'] = status
                
            generations = self.get_by_filters(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by='created_at',
                order_direction='desc'
            )
            
            return generations
            
        except Exception as e:
            raise RepositoryException(f"Failed to get user generations: {str(e)}")
            
    def get_pending_generations(self, 
                              priority: Optional[str] = None,
                              content_type: Optional[str] = None,
                              limit: int = 100) -> List[AIContentGeneration]:
        """
        Get pending AI generation tasks for processing
        
        Args:
            priority: Filter by priority
            content_type: Filter by content type
            limit: Maximum results
            
        Returns:
            List of pending generation tasks
        """
        try:
            filters = {'status': 'pending'}
            
            if priority:
                filters['priority'] = priority
                
            if content_type:
                filters['content_type'] = content_type
                
            # Order by priority and creation time
            generations = self.get_by_filters(
                filters=filters,
                limit=limit,
                order_by='created_at',
                order_direction='asc'
            )
            
            return generations
            
        except Exception as e:
            raise RepositoryException(f"Failed to get pending generations: {str(e)}")
            
    def get_generation_analytics(self, 
                               user_id: Optional[int] = None,
                               days: int = 30) -> Dict[str, Any]:
        """
        Get AI content generation analytics and statistics
        
        Args:
            user_id: Optional user ID filter
            days: Number of days for analytics
            
        Returns:
            Analytics data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            base_query = self.db_session.query(AIContentGeneration).filter(
                AIContentGeneration.created_at >= start_date
            )
            
            if user_id:
                base_query = base_query.filter(AIContentGeneration.user_id == user_id)
                
            # Total generations
            total_generations = base_query.count()
            
            # Generations by status
            status_stats = base_query.with_entities(
                AIContentGeneration.status,
                func.count(AIContentGeneration.id).label('count')
            ).group_by(AIContentGeneration.status).all()
            
            # Generations by content type
            content_type_stats = base_query.with_entities(
                AIContentGeneration.content_type,
                func.count(AIContentGeneration.id).label('count')
            ).group_by(AIContentGeneration.content_type).all()
            
            # Generations by AI model
            model_stats = base_query.with_entities(
                AIContentGeneration.ai_model_name,
                func.count(AIContentGeneration.id).label('count')
            ).group_by(AIContentGeneration.ai_model_name).all()
            
            # Daily generation counts
            daily_stats = base_query.with_entities(
                func.date(AIContentGeneration.created_at).label('date'),
                func.count(AIContentGeneration.id).label('count')
            ).group_by(func.date(AIContentGeneration.created_at)).order_by(
                func.date(AIContentGeneration.created_at)
            ).all()
            
            # Success rate
            completed_count = base_query.filter(
                AIContentGeneration.status == 'completed'
            ).count()
            
            success_rate = (completed_count / total_generations * 100) if total_generations > 0 else 0
            
            analytics = {
                'total_generations': total_generations,
                'success_rate': round(success_rate, 2),
                'status_distribution': {status: count for status, count in status_stats},
                'content_type_distribution': {content_type: count for content_type, count in content_type_stats},
                'model_usage': {model: count for model, count in model_stats},
                'daily_generation_counts': [
                    {'date': str(date), 'count': count} for date, count in daily_stats
                ],
                'period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to get generation analytics: {str(e)}")
            
    def get_model_performance_stats(self, ai_model_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Get performance statistics for specific AI model
        
        Args:
            ai_model_name: AI model name
            days: Number of days for statistics
            
        Returns:
            Model performance statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            model_generations = self.db_session.query(AIContentGeneration).filter(
                and_(
                    AIContentGeneration.ai_model_name == ai_model_name,
                    AIContentGeneration.created_at >= start_date
                )
            )
            
            total_tasks = model_generations.count()
            completed_tasks = model_generations.filter(
                AIContentGeneration.status == 'completed'
            ).count()
            failed_tasks = model_generations.filter(
                AIContentGeneration.status == 'failed'
            ).count()
            
            # Calculate average processing time for completed tasks
            completed_generations = model_generations.filter(
                and_(
                    AIContentGeneration.status == 'completed',
                    AIContentGeneration.started_at.isnot(None),
                    AIContentGeneration.completed_at.isnot(None)
                )
            ).all()
            
            processing_times = []
            for gen in completed_generations:
                if gen.started_at and gen.completed_at:
                    processing_time = (gen.completed_at - gen.started_at).total_seconds()
                    processing_times.append(processing_time)
                    
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            failure_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            stats = {
                'model_name': ai_model_name,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': round(success_rate, 2),
                'failure_rate': round(failure_rate, 2),
                'average_processing_time_seconds': round(avg_processing_time, 2),
                'period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            raise RepositoryException(f"Failed to get model performance stats: {str(e)}")
            
    def cleanup_old_generations(self, days_to_keep: int = 90) -> int:
        """
        Clean up old AI generation records
        
        Args:
            days_to_keep: Number of days to keep records
            
        Returns:
            Number of cleaned up records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Only delete completed or failed generations older than cutoff
            deleted_count = self.bulk_delete({
                'created_at': {'lt': cutoff_date},
                'status': {'in': ['completed', 'failed']}
            })
            
            self.logger.info(f"Cleaned up {deleted_count} old AI generation records")
            return deleted_count
            
        except Exception as e:
            raise RepositoryException(f"Failed to cleanup old generations: {str(e)}")
            
    def get_content_type_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics by content type
        
        Returns:
            Queue statistics by content type
        """
        try:
            # Get pending tasks by content type
            pending_stats = self.db_session.query(
                AIContentGeneration.content_type,
                func.count(AIContentGeneration.id).label('pending_count')
            ).filter(
                AIContentGeneration.status == 'pending'
            ).group_by(AIContentGeneration.content_type).all()
            
            # Get processing tasks by content type
            processing_stats = self.db_session.query(
                AIContentGeneration.content_type,
                func.count(AIContentGeneration.id).label('processing_count')
            ).filter(
                AIContentGeneration.status == 'processing'
            ).group_by(AIContentGeneration.content_type).all()
            
            # Combine statistics
            queue_stats = {}
            
            for content_type, pending_count in pending_stats:
                queue_stats[content_type] = {
                    'pending': pending_count,
                    'processing': 0
                }
                
            for content_type, processing_count in processing_stats:
                if content_type not in queue_stats:
                    queue_stats[content_type] = {'pending': 0, 'processing': processing_count}
                else:
                    queue_stats[content_type]['processing'] = processing_count
                    
            return {
                'queue_statistics': queue_stats,
                'total_pending': sum(stats['pending'] for stats in queue_stats.values()),
                'total_processing': sum(stats['processing'] for stats in queue_stats.values()),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RepositoryException(f"Failed to get queue stats: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
