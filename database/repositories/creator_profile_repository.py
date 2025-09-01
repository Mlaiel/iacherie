"""Creator Profile Repository

Enterprise-grade repository for comprehensive creator profile management,
portfolio tracking, and professional networking capabilities.

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

from typing import Dict, List, Optional, Union, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import uuid
import json
import logging

from .base_repository import BaseRepository, RepositoryException
from ..models.creator_profile import CreatorProfile

logger = logging.getLogger(__name__)

class CreatorProfileRepository(BaseRepository[CreatorProfile]):
    """
    Repository for creator profile management with enterprise-grade
    features including portfolio management, networking, and professional analytics.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize Creator Profile Repository"""
        super().__init__(db_session, CreatorProfile)
        
    def create_creator_profile(self, 
                             user_id: int,
                             profile_data: Dict[str, Any],
                             portfolio_items: List[Dict[str, Any]],
                             specializations: List[str],
                             social_links: Dict[str, str]) -> CreatorProfile:
        """
        Create comprehensive creator profile
        
        Args:
            user_id: User ID
            profile_data: Basic profile information
            portfolio_items: Portfolio/showcase items
            specializations: Creator specializations/skills
            social_links: Social media and professional links
            
        Returns:
            Created creator profile instance
        """
        try:
            creator_profile_data = {
                'user_id': user_id,
                'display_name': profile_data.get('display_name'),
                'bio': profile_data.get('bio'),
                'location': profile_data.get('location'),
                'timezone': profile_data.get('timezone'),
                'creator_type': profile_data.get('creator_type'),
                'experience_level': profile_data.get('experience_level', 'beginner'),
                'portfolio_items': json.dumps(portfolio_items),
                'specializations': json.dumps(specializations),
                'social_links': json.dumps(social_links),
                'profile_settings': json.dumps(profile_data.get('settings', {})),
                'is_verified': False,
                'is_public': profile_data.get('is_public', True),
                'created_at': datetime.utcnow()
            }
            
            creator_profile = self.create(**creator_profile_data)
            
            self.logger.info(f"Created creator profile ID: {creator_profile.id} for user: {user_id}")
            return creator_profile
            
        except Exception as e:
            raise RepositoryException(f"Failed to create creator profile: {str(e)}")
            
    def update_profile_portfolio(self, 
                               profile_id: int,
                               portfolio_items: List[Dict[str, Any]],
                               action: str = 'replace') -> Optional[CreatorProfile]:
        """
        Update creator's portfolio items
        
        Args:
            profile_id: Creator profile ID
            portfolio_items: New portfolio items
            action: 'replace', 'append', or 'prepend'
            
        Returns:
            Updated creator profile
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None
                
            existing_portfolio = json.loads(profile.portfolio_items or '[]')
            
            if action == 'replace':
                updated_portfolio = portfolio_items
            elif action == 'append':
                updated_portfolio = existing_portfolio + portfolio_items
            elif action == 'prepend':
                updated_portfolio = portfolio_items + existing_portfolio
            else:
                raise ValueError(f"Invalid action: {action}")
            
            updated_profile = self.update(profile_id, 
                                        portfolio_items=json.dumps(updated_portfolio),
                                        updated_at=datetime.utcnow())
            
            if updated_profile:
                self.logger.info(f"Updated portfolio for profile: {profile_id}")
                
            return updated_profile
            
        except Exception as e:
            raise RepositoryException(f"Failed to update profile portfolio: {str(e)}")
            
    def update_profile_specializations(self, 
                                     profile_id: int,
                                     specializations: List[str]) -> Optional[CreatorProfile]:
        """
        Update creator's specializations
        
        Args:
            profile_id: Creator profile ID
            specializations: Updated specializations list
            
        Returns:
            Updated creator profile
        """
        try:
            updated_profile = self.update(profile_id, 
                                        specializations=json.dumps(specializations),
                                        updated_at=datetime.utcnow())
            
            if updated_profile:
                self.logger.info(f"Updated specializations for profile: {profile_id}")
                
            return updated_profile
            
        except Exception as e:
            raise RepositoryException(f"Failed to update profile specializations: {str(e)}")
            
    def get_creator_by_user_id(self, user_id: int) -> Optional[CreatorProfile]:
        """
        Get creator profile by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Creator profile if found
        """
        try:
            profile = self.db_session.query(CreatorProfile).filter(
                CreatorProfile.user_id == user_id
            ).first()
            
            return profile
            
        except Exception as e:
            raise RepositoryException(f"Failed to get creator by user ID: {str(e)}")
            
    def search_creators(self, 
                       search_params: Dict[str, Any],
                       limit: int = 20,
                       offset: int = 0) -> List[CreatorProfile]:
        """
        Search creators based on various criteria
        
        Args:
            search_params: Search parameters (specializations, location, creator_type, etc.)
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of matching creator profiles
        """
        try:
            query = self.db_session.query(CreatorProfile).filter(
                CreatorProfile.is_public == True
            )
            
            # Filter by creator type
            if 'creator_type' in search_params:
                query = query.filter(CreatorProfile.creator_type == search_params['creator_type'])
                
            # Filter by experience level
            if 'experience_level' in search_params:
                query = query.filter(CreatorProfile.experience_level == search_params['experience_level'])
                
            # Filter by location
            if 'location' in search_params:
                query = query.filter(CreatorProfile.location.ilike(f"%{search_params['location']}%"))
                
            # Filter by verification status
            if 'verified_only' in search_params and search_params['verified_only']:
                query = query.filter(CreatorProfile.is_verified == True)
                
            # Search in specializations (JSON contains)
            if 'specializations' in search_params:
                for specialization in search_params['specializations']:
                    query = query.filter(
                        CreatorProfile.specializations.contains(f'"{specialization}"')
                    )
            
            # Search in bio and display name
            if 'keyword' in search_params:
                keyword = search_params['keyword']
                query = query.filter(
                    or_(
                        CreatorProfile.display_name.ilike(f"%{keyword}%"),
                        CreatorProfile.bio.ilike(f"%{keyword}%")
                    )
                )
            
            # Order by verification status and profile completeness
            query = query.order_by(
                desc(CreatorProfile.is_verified),
                desc(CreatorProfile.profile_score),
                desc(CreatorProfile.updated_at)
            )
            
            # Apply pagination
            creators = query.offset(offset).limit(limit).all()
            
            return creators
            
        except Exception as e:
            raise RepositoryException(f"Failed to search creators: {str(e)}")
            
    def get_creator_analytics(self, profile_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics for creator profile
        
        Args:
            profile_id: Creator profile ID
            days: Number of days for analytics
            
        Returns:
            Creator analytics data
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                raise RepositoryException(f"Creator profile not found: {profile_id}")
                
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Profile views analytics (would need separate tracking table)
            # For now, return basic profile analytics
            analytics = {
                'profile_info': {
                    'display_name': profile.display_name,
                    'creator_type': profile.creator_type,
                    'experience_level': profile.experience_level,
                    'is_verified': profile.is_verified,
                    'profile_score': profile.profile_score or 0,
                    'member_since': profile.created_at.isoformat()
                },
                'portfolio_stats': self._analyze_portfolio(profile),
                'specialization_breakdown': self._analyze_specializations(profile),
                'social_presence': self._analyze_social_links(profile),
                'profile_completeness': self._calculate_profile_completeness(profile),
                'growth_metrics': {
                    'profile_updates': self._count_profile_updates(profile_id, start_date),
                    'portfolio_additions': self._count_portfolio_updates(profile_id, start_date)
                },
                'recommendations': self._generate_profile_recommendations(profile),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to get creator analytics: {str(e)}")
            
    def _analyze_portfolio(self, profile: CreatorProfile) -> Dict[str, Any]:
        """Analyze creator's portfolio"""
        try:
            portfolio_items = json.loads(profile.portfolio_items or '[]')
            
            if not portfolio_items:
                return {
                    'total_items': 0,
                    'item_types': {},
                    'latest_addition': None
                }
            
            # Analyze portfolio item types
            item_types = {}
            latest_item = None
            latest_date = None
            
            for item in portfolio_items:
                item_type = item.get('type', 'unknown')
                item_types[item_type] = item_types.get(item_type, 0) + 1
                
                # Track latest addition
                if 'created_at' in item:
                    item_date = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                    if not latest_date or item_date > latest_date:
                        latest_date = item_date
                        latest_item = item
            
            return {
                'total_items': len(portfolio_items),
                'item_types': item_types,
                'latest_addition': latest_item.get('title', 'Unknown') if latest_item else None,
                'average_items_per_type': round(len(portfolio_items) / len(item_types), 2) if item_types else 0
            }
            
        except (json.JSONDecodeError, KeyError):
            return {'total_items': 0, 'item_types': {}, 'latest_addition': None}
            
    def _analyze_specializations(self, profile: CreatorProfile) -> Dict[str, Any]:
        """
Analyze creator's specializations"""
        try:
            specializations = json.loads(profile.specializations or '[]')
            
            return {
                'total_specializations': len(specializations),
                'specializations_list': specializations,
                'specialization_diversity': len(set(spec.split()[0] for spec in specializations if spec)) if specializations else 0
            }
            
        except (json.JSONDecodeError, KeyError):
            return {'total_specializations': 0, 'specializations_list': [], 'specialization_diversity': 0}
            
    def _analyze_social_links(self, profile: CreatorProfile) -> Dict[str, Any]:
        """
Analyze creator's social media presence"""
        try:
            social_links = json.loads(profile.social_links or '{}')
            
            platform_count = len(social_links)
            platforms = list(social_links.keys())
            
            return {
                'connected_platforms': platform_count,
                'platforms': platforms,
                'has_professional_links': any(platform in ['linkedin', 'behance', 'dribbble'] for platform in platforms)
            }
            
        except (json.JSONDecodeError, KeyError):
            return {'connected_platforms': 0, 'platforms': [], 'has_professional_links': False}
            
    def _calculate_profile_completeness(self, profile: CreatorProfile) -> Dict[str, Any]:
        """
Calculate profile completeness score"""
        score = 0
        total_fields = 10
        completed_fields = []
        missing_fields = []
        
        # Check required fields
        if profile.display_name:
            score += 1
            completed_fields.append('display_name')
        else:
            missing_fields.append('display_name')
            
        if profile.bio and len(profile.bio) > 20:
            score += 1
            completed_fields.append('bio')
        else:
            missing_fields.append('bio')
            
        if profile.location:
            score += 1
            completed_fields.append('location')
        else:
            missing_fields.append('location')
            
        if profile.creator_type:
            score += 1
            completed_fields.append('creator_type')
        else:
            missing_fields.append('creator_type')
            
        # Check optional fields
        try:
            portfolio_items = json.loads(profile.portfolio_items or '[]')
            if len(portfolio_items) > 0:
                score += 2  # Portfolio is worth more
                completed_fields.append('portfolio')
            else:
                missing_fields.append('portfolio')
                
            specializations = json.loads(profile.specializations or '[]')
            if len(specializations) > 0:
                score += 1
                completed_fields.append('specializations')
            else:
                missing_fields.append('specializations')
                
            social_links = json.loads(profile.social_links or '{}')
            if len(social_links) > 0:
                score += 1
                completed_fields.append('social_links')
            else:
                missing_fields.append('social_links')
                
        except (json.JSONDecodeError, KeyError):
            missing_fields.extend(['portfolio', 'specializations', 'social_links'])
            
        if profile.timezone:
            score += 1
            completed_fields.append('timezone')
        else:
            missing_fields.append('timezone')
            
        if profile.experience_level and profile.experience_level != 'beginner':
            score += 1
            completed_fields.append('experience_level')
        else:
            missing_fields.append('experience_level')
            
        if profile.is_verified:
            score += 1
            completed_fields.append('verification')
        else:
            missing_fields.append('verification')
            
        completeness_percentage = (score / total_fields) * 100
        
        return {
            'score': score,
            'total_fields': total_fields,
            'completeness_percentage': round(completeness_percentage, 2),
            'completed_fields': completed_fields,
            'missing_fields': missing_fields
        }
        
    def _count_profile_updates(self, profile_id: int, start_date: datetime) -> int:
        """
Count profile updates in time period"""
        # This would require an audit log or update tracking
        # For now, return a placeholder
        return 0
        
    def _count_portfolio_updates(self, profile_id: int, start_date: datetime) -> int:
        """
Count portfolio updates in time period"""
        # This would require portfolio change tracking
        # For now, return a placeholder
        return 0
        
    def _generate_profile_recommendations(self, profile: CreatorProfile) -> List[str]:
        """
Generate profile improvement recommendations"""
        recommendations = []
        
        completeness = self._calculate_profile_completeness(profile)
        
        if completeness['completeness_percentage'] < 80:
            recommendations.append(f"Complete your profile ({completeness['completeness_percentage']:.0f}% complete)")
            
        if 'bio' in completeness['missing_fields']:
            recommendations.append("Add a compelling bio to attract potential collaborators")
            
        if 'portfolio' in completeness['missing_fields']:
            recommendations.append("Showcase your work by adding portfolio items")
            
        if 'specializations' in completeness['missing_fields']:
            recommendations.append("Add your specializations to help others find your skills")
            
        if 'social_links' in completeness['missing_fields']:
            recommendations.append("Connect your social media profiles to expand your reach")
            
        if not profile.is_verified:
            recommendations.append("Consider getting verified to increase trustworthiness")
            
        try:
            portfolio_items = json.loads(profile.portfolio_items or '[]')
            if len(portfolio_items) < 3:
                recommendations.append("Add more portfolio items to better showcase your work")
        except (json.JSONDecodeError, KeyError):
            pass
            
        return recommendations
        
    def get_trending_specializations(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get trending specializations among creators
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of trending specializations
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all creators created or updated in the period
            recent_profiles = self.db_session.query(CreatorProfile).filter(
                or_(
                    CreatorProfile.created_at >= start_date,
                    CreatorProfile.updated_at >= start_date
                )
            ).all()
            
            specialization_counts = {}
            
            for profile in recent_profiles:
                try:
                    specializations = json.loads(profile.specializations or '[]')
                    for spec in specializations:
                        spec_clean = spec.strip().lower()
                        specialization_counts[spec_clean] = specialization_counts.get(spec_clean, 0) + 1
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Sort by popularity
            trending = sorted(
                specialization_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return [
                {
                    'specialization': spec,
                    'creator_count': count,
                    'growth_indicator': 'trending' if count > 1 else 'emerging'
                }
                for spec, count in trending
            ]
            
        except Exception as e:
            raise RepositoryException(f"Failed to get trending specializations: {str(e)}")
            
    def get_creator_recommendations(self, 
                                  profile_id: int,
                                  recommendation_type: str = 'collaboration',
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get creator recommendations based on profile and preferences
        
        Args:
            profile_id: Creator profile ID
            recommendation_type: Type of recommendations ('collaboration', 'similar', 'complementary')
            limit: Maximum recommendations
            
        Returns:
            List of recommended creators
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                raise RepositoryException(f"Creator profile not found: {profile_id}")
                
            profile_specializations = json.loads(profile.specializations or '[]')
            
            query = self.db_session.query(CreatorProfile).filter(
                and_(
                    CreatorProfile.id != profile_id,
                    CreatorProfile.is_public == True
                )
            )
            
            if recommendation_type == 'similar':
                # Find creators with similar specializations
                similar_creators = []
                for candidate in query.all():
                    try:
                        candidate_specs = json.loads(candidate.specializations or '[]')
                        overlap = len(set(profile_specializations) & set(candidate_specs))
                        if overlap > 0:
                            similar_creators.append((candidate, overlap))
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                # Sort by overlap and take top results
                similar_creators.sort(key=lambda x: x[1], reverse=True)
                recommendations = [
                    {
                        'creator': creator,
                        'similarity_score': overlap,
                        'reason': f"{overlap} shared specializations"
                    }
                    for creator, overlap in similar_creators[:limit]
                ]
                
            elif recommendation_type == 'complementary':
                # Find creators with complementary skills
                complementary_creators = []
                for candidate in query.all():
                    try:
                        candidate_specs = json.loads(candidate.specializations or '[]')
                        # Look for minimal overlap but related skills
                        overlap = len(set(profile_specializations) & set(candidate_specs))
                        if overlap <= 1 and len(candidate_specs) > 0:
                            complementary_creators.append((candidate, len(candidate_specs)))
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                # Sort by skill diversity
                complementary_creators.sort(key=lambda x: x[1], reverse=True)
                recommendations = [
                    {
                        'creator': creator,
                        'complementary_score': skill_count,
                        'reason': "Complementary skills for collaboration"
                    }
                    for creator, skill_count in complementary_creators[:limit]
                ]
                
            else:  # collaboration
                # Mix of similar and complementary creators
                similar_limit = limit // 2
                complementary_limit = limit - similar_limit
                
                similar_recs = self.get_creator_recommendations(profile_id, 'similar', similar_limit)
                complementary_recs = self.get_creator_recommendations(profile_id, 'complementary', complementary_limit)
                
                recommendations = similar_recs + complementary_recs
            
            return recommendations
            
        except Exception as e:
            raise RepositoryException(f"Failed to get creator recommendations: {str(e)}")
            
    def update_profile_score(self, profile_id: int) -> Optional[CreatorProfile]:
        """
        Update and calculate profile score based on various factors
        
        Args:
            profile_id: Creator profile ID
            
        Returns:
            Updated creator profile
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None
                
            # Calculate profile score based on multiple factors
            score = 0
            
            # Completeness score (40% weight)
            completeness = self._calculate_profile_completeness(profile)
            score += (completeness['completeness_percentage'] / 100) * 40
            
            # Portfolio quality (30% weight)
            try:
                portfolio_items = json.loads(profile.portfolio_items or '[]')
                portfolio_score = min(len(portfolio_items) * 5, 30)  # Max 30 points for 6+ items
                score += portfolio_score
            except (json.JSONDecodeError, KeyError):
                pass
            
            # Social presence (20% weight)
            try:
                social_links = json.loads(profile.social_links or '{}')
                social_score = min(len(social_links) * 4, 20)  # Max 20 points for 5+ platforms
                score += social_score
            except (json.JSONDecodeError, KeyError):
                pass
            
            # Verification bonus (10% weight)
            if profile.is_verified:
                score += 10
                
            # Cap score at 100
            final_score = min(score, 100)
            
            updated_profile = self.update(profile_id, profile_score=final_score)
            
            if updated_profile:
                self.logger.info(f"Updated profile score for profile {profile_id}: {final_score}")
                
            return updated_profile
            
        except Exception as e:
            raise RepositoryException(f"Failed to update profile score: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
