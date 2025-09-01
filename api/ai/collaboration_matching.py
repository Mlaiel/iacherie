"""IA Influencer Agent - Collaboration Matching Module
Advanced AI-powered creator collaboration and partnership matching system.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result 
in legal action.

(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import math
from collections import defaultdict

logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """
Types of content creators"""

    MUSICIAN = "musician"
    VIDEO_CREATOR = "video_creator"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    PODCASTER = "podcaster"
    COMEDIAN = "comedian"
    INFLUENCER = "influencer"
    STREAMER = "streamer"
    ARTIST = "artist"
    PRODUCER = "producer"

class CollaborationType(Enum):
    """Types of collaborations available"""

    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    JOINT_PROJECT = "joint_project"
    MENTORSHIP = "mentorship"
    BRAND_PARTNERSHIP = "brand_partnership"
    TOUR_COLLABORATION = "tour_collaboration"
    REMIX_COLLABORATION = "remix_collaboration"

class CompatibilityFactor(Enum):
    """Factors for collaboration compatibility"""

    CONTENT_STYLE = "content_style"
    AUDIENCE_OVERLAP = "audience_overlap"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    AVAILABILITY = "availability"
    LOCATION_PROXIMITY = "location_proximity"
    EXPERIENCE_LEVEL = "experience_level"
    BRAND_ALIGNMENT = "brand_alignment"
    COMMUNICATION_STYLE = "communication_style"

@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    creator_id: str
    name: str
    creator_type: CreatorType
    sub_specialties: List[str]
    skill_tags: List[str]
    content_categories: List[str]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    collaboration_history: List[str]
    availability: Dict[str, Any]
    location: Dict[str, str]
    preferred_collaboration_types: List[CollaborationType]
    portfolio_analysis: Dict[str, Any]
    social_metrics: Dict[str, int]
    brand_values: List[str]
    communication_preferences: Dict[str, Any]

@dataclass
class CollaborationOpportunity:
    """
Collaboration opportunity details"""
    opportunity_id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    required_skills: List[str]
    preferred_creator_types: List[CreatorType]
    duration: timedelta
    budget_range: Optional[Tuple[float, float]]
    deadline: Optional[datetime]
    location_requirements: Dict[str, Any]
    target_audience: Dict[str, Any]
    deliverables: List[str]
    posted_by: str
    status: str

@dataclass
class MatchResult:
    """
Result of collaboration matching"""
    match_id: str
    creator1: CreatorProfile
    creator2: Optional[CreatorProfile]
    opportunity: Optional[CollaborationOpportunity]
    compatibility_score: float
    compatibility_breakdown: Dict[CompatibilityFactor, float]
    match_reasons: List[str]
    potential_challenges: List[str]
    recommended_collaboration_types: List[CollaborationType]
    success_probability: float
    suggested_terms: Dict[str, Any]

class CreatorAnalyzer:
    """
Advanced creator profile analysis and categorization"""
    
    def __init__(self):
        self.skill_categories = {
            CreatorType.MUSICIAN: [
                'composition', 'production', 'vocals', 'instruments', 'mixing', 
                'mastering', 'songwriting', 'performance', 'recording'
            ],
            CreatorType.VIDEO_CREATOR: [
                'filming', 'editing', 'scripting', 'directing', 'animation',
                'motion_graphics', 'color_grading', 'storytelling'
            ],
            CreatorType.PHOTOGRAPHER: [
                'portrait', 'landscape', 'commercial', 'event', 'fashion',
                'product', 'editing', 'retouching', 'lighting'
            ],
            CreatorType.BLOGGER: [
                'writing', 'seo', 'research', 'photography', 'social_media',
                'content_strategy', 'copywriting', 'journalism'
            ]
        }
        
        self.complementary_skills = {
            'music_production': ['vocals', 'songwriting', 'mixing'],
            'video_production': ['editing', 'scripting', 'filming'],
            'content_marketing': ['writing', 'seo', 'social_media'],
            'visual_design': ['photography', 'editing', 'graphics']
        }
    
    async def analyze_creator_profile(
        self, 
        creator_data: Dict[str, Any], 
        content_history: List[Dict[str, Any]]
    ) -> CreatorProfile:
        """
Analyze and create comprehensive creator profile"""
        try:
            # Extract basic information
            creator_id = creator_data.get('id', '')
            name = creator_data.get('name', '')
            creator_type = CreatorType(creator_data.get('type', 'influencer'))
            
            # Analyze skills and specialties
            skill_analysis = await self._analyze_creator_skills(content_history, creator_type)
            
            # Analyze audience demographics
            audience_analysis = await self._analyze_audience_demographics(creator_data, content_history)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(content_history)
            
            # Analyze collaboration history
            collaboration_history = await self._extract_collaboration_history(content_history)
            
            # Extract availability and location
            availability = creator_data.get('availability', {})
            location = creator_data.get('location', {})
            
            # Determine preferred collaboration types
            preferred_collabs = await self._determine_collaboration_preferences(
                creator_type, skill_analysis, collaboration_history
            )
            
            # Analyze portfolio
            portfolio_analysis = await self._analyze_portfolio(content_history)
            
            # Extract social metrics
            social_metrics = creator_data.get('social_metrics', {})
            
            # Determine brand values
            brand_values = await self._extract_brand_values(creator_data, content_history)
            
            # Communication preferences
            communication_preferences = creator_data.get('communication_preferences', {})
            
            return CreatorProfile(
                creator_id=creator_id,
                name=name,
                creator_type=creator_type,
                sub_specialties=skill_analysis['specialties'],
                skill_tags=skill_analysis['skills'],
                content_categories=skill_analysis['categories'],
                audience_demographics=audience_analysis,
                engagement_metrics=engagement_metrics,
                collaboration_history=collaboration_history,
                availability=availability,
                location=location,
                preferred_collaboration_types=preferred_collabs,
                portfolio_analysis=portfolio_analysis,
                social_metrics=social_metrics,
                brand_values=brand_values,
                communication_preferences=communication_preferences
            )
            
        except Exception as e:
            logger.error(f"Creator profile analysis failed: {str(e)}")
            raise
    
    async def _analyze_creator_skills(
        self, 
        content_history: List[Dict[str, Any]], 
        creator_type: CreatorType
    ) -> Dict[str, Any]:
        """Analyze creator skills from content history"""
        skills = []
        specialties = []
        categories = []
        
        # Get base skills for creator type
        base_skills = self.skill_categories.get(creator_type, [])
        skills.extend(base_skills)
        
        # Analyze content for additional skills
        for content in content_history:
            content_tags = content.get('tags', [])
            content_type = content.get('type', '')
            
            # Add content-specific skills
            if content_type == 'music':
                if 'original' in content_tags:
                    skills.append('composition')
                if 'cover' in content_tags:
                    skills.append('performance')
            elif content_type == 'video':
                if 'tutorial' in content_tags:
                    skills.append('teaching')
                if 'animation' in content_tags:
                    skills.append('animation')
            
            # Extract categories
            categories.extend(content.get('categories', []))
        
        # Determine specialties based on skill frequency
        skill_counts = defaultdict(int)
        for content in content_history:
            for tag in content.get('tags', []):
                skill_counts[tag] += 1
        
        # Top skills become specialties
        specialties = [skill for skill, count in 
                      sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return {
            'skills': list(set(skills)),
            'specialties': specialties,
            'categories': list(set(categories))
        }
    
    async def _analyze_audience_demographics(
        self, 
        creator_data: Dict[str, Any], 
        content_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
Analyze audience demographics"""
        # Extract from creator data if available
        existing_demographics = creator_data.get('audience_demographics', {})
        
        if existing_demographics:
            return existing_demographics
        
        # Estimate from content analysis
        estimated_demographics = {
            'age_groups': {'18-24': 0.3, '25-34': 0.4, '35-44': 0.2, '45+': 0.1},
            'gender': {'male': 0.45, 'female': 0.55},
            'interests': [],
            'locations': {},
            'languages': ['english']
        }
        
        # Extract interests from content
        all_tags = []
        for content in content_history:
            all_tags.extend(content.get('tags', []))
        
        tag_counts = Counter(all_tags)
        estimated_demographics['interests'] = [tag for tag, count in tag_counts.most_common(10)]
        
        return estimated_demographics
    
    async def _calculate_engagement_metrics(self, content_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
Calculate engagement metrics from content history"""
        if not content_history:
            return {'average_engagement': 0.05, 'consistency_score': 0.5}
        
        engagement_rates = []
        for content in content_history:
            views = content.get('views', 1)
            likes = content.get('likes', 0)
            comments = content.get('comments', 0)
            shares = content.get('shares', 0)
            
            if views > 0:
                engagement_rate = (likes + comments + shares) / views
                engagement_rates.append(engagement_rate)
        
        if not engagement_rates:
            return {'average_engagement': 0.05, 'consistency_score': 0.5}
        
        avg_engagement = sum(engagement_rates) / len(engagement_rates)
        
        # Calculate consistency (low standard deviation = high consistency)
        mean_engagement = avg_engagement
        variance = sum((x - mean_engagement) ** 2 for x in engagement_rates) / len(engagement_rates)
        std_dev = math.sqrt(variance)
        consistency_score = max(0, 1 - std_dev)
        
        return {
            'average_engagement': avg_engagement,
            'consistency_score': consistency_score,
            'total_content': len(content_history),
            'viral_content_count': len([c for c in content_history if c.get('views', 0) > 100000])
        }
    
    async def _extract_collaboration_history(self, content_history: List[Dict[str, Any]]) -> List[str]:
        """
Extract collaboration history from content"""
        collaborations = []
        
        for content in content_history:
            # Look for collaboration indicators
            title = content.get('title', '').lower()
            description = content.get('description', '').lower()
            tags = [tag.lower() for tag in content.get('tags', [])]
            
            collab_indicators = ['collab', 'featuring', 'ft.', 'with', 'x ', 'collaboration']
            
            if any(indicator in title or indicator in description for indicator in collab_indicators):
                collaborations.append(content.get('id', ''))
            
            if 'collaboration' in tags or 'featuring' in tags:
                collaborations.append(content.get('id', ''))
        
        return collaborations
    
    async def _determine_collaboration_preferences(
        self, 
        creator_type: CreatorType, 
        skill_analysis: Dict[str, Any], 
        collaboration_history: List[str]
    ) -> List[CollaborationType]:
        """
Determine preferred collaboration types"""
        preferences = []
        
        # Base preferences by creator type
        type_preferences = {
            CreatorType.MUSICIAN: [
                CollaborationType.REMIX_COLLABORATION,
                CollaborationType.CONTENT_CREATION,
                CollaborationType.CROSS_PROMOTION
            ],
            CreatorType.VIDEO_CREATOR: [
                CollaborationType.CONTENT_CREATION,
                CollaborationType.JOINT_PROJECT,
                CollaborationType.CROSS_PROMOTION
            ],
            CreatorType.PHOTOGRAPHER: [
                CollaborationType.CONTENT_CREATION,
                CollaborationType.BRAND_PARTNERSHIP,
                CollaborationType.SKILL_EXCHANGE
            ]
        }
        
        preferences.extend(type_preferences.get(creator_type, [CollaborationType.CONTENT_CREATION]))
        
        # Add preferences based on collaboration history
        if len(collaboration_history) > 3:
            preferences.append(CollaborationType.JOINT_PROJECT)
        
        # Add preferences based on skills
        if 'teaching' in skill_analysis.get('skills', []):
            preferences.append(CollaborationType.MENTORSHIP)
        
        return list(set(preferences))
    
    async def _analyze_portfolio(self, content_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Analyze creator portfolio quality and diversity"""
        if not content_history:
            return {'quality_score': 0.5, 'diversity_score': 0.5, 'consistency_score': 0.5}
        
        # Quality indicators
        high_quality_count = len([c for c in content_history if c.get('views', 0) > 10000])
        quality_score = min(high_quality_count / len(content_history), 1.0)
        
        # Diversity - unique categories and types
        all_categories = set()
        all_types = set()
        for content in content_history:
            all_categories.update(content.get('categories', []))
            all_types.add(content.get('type', ''))
        
        diversity_score = min((len(all_categories) + len(all_types)) / 10, 1.0)
        
        # Consistency - regular posting
        if len(content_history) >= 12:  # At least 12 pieces of content
            consistency_score = 0.9
        elif len(content_history) >= 6:
            consistency_score = 0.7
        else:
            consistency_score = 0.5
        
        return {
            'quality_score': quality_score,
            'diversity_score': diversity_score,
            'consistency_score': consistency_score,
            'total_content': len(content_history),
            'categories': list(all_categories),
            'content_types': list(all_types)
        }
    
    async def _extract_brand_values(
        self, 
        creator_data: Dict[str, Any], 
        content_history: List[Dict[str, Any]]
    ) -> List[str]:
        """
Extract brand values from creator profile and content"""
        brand_values = []
        
        # From explicit data
        explicit_values = creator_data.get('brand_values', [])
        brand_values.extend(explicit_values)
        
        # Inferred from content
        all_tags = []
        for content in content_history:
            all_tags.extend(content.get('tags', []))
        
        # Map tags to brand values
        value_keywords = {
            'authenticity': ['authentic', 'real', 'genuine', 'honest'],
            'creativity': ['creative', 'innovative', 'unique', 'original'],
            'professionalism': ['professional', 'quality', 'high-end'],
            'education': ['tutorial', 'learn', 'educational', 'teaching'],
            'entertainment': ['fun', 'funny', 'entertaining', 'comedy'],
            'inspiration': ['motivational', 'inspiring', 'uplifting']
        }
        
        for value, keywords in value_keywords.items():
            if any(keyword in tag.lower() for tag in all_tags for keyword in keywords):
                brand_values.append(value)
        
        return list(set(brand_values))

class CompatibilityCalculator:
    """
Advanced compatibility calculation for creator matching"""
    
    def __init__(self):
        self.factor_weights = {
            CompatibilityFactor.CONTENT_STYLE: 0.2,
            CompatibilityFactor.AUDIENCE_OVERLAP: 0.18,
            CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.15,
            CompatibilityFactor.AVAILABILITY: 0.12,
            CompatibilityFactor.LOCATION_PROXIMITY: 0.1,
            CompatibilityFactor.EXPERIENCE_LEVEL: 0.1,
            CompatibilityFactor.BRAND_ALIGNMENT: 0.08,
            CompatibilityFactor.COMMUNICATION_STYLE: 0.07
        }
    
    async def calculate_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None
    ) -> Tuple[float, Dict[CompatibilityFactor, float]]:
        """
Calculate comprehensive compatibility score between creators"""
        try:
            factor_scores = {}
            
            # Calculate each compatibility factor
            factor_scores[CompatibilityFactor.CONTENT_STYLE] = await self._calculate_content_style_compatibility(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.SKILL_COMPLEMENTARITY] = await self._calculate_skill_complementarity(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.AVAILABILITY] = await self._calculate_availability_compatibility(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.LOCATION_PROXIMITY] = await self._calculate_location_compatibility(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.EXPERIENCE_LEVEL] = await self._calculate_experience_compatibility(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.BRAND_ALIGNMENT] = await self._calculate_brand_alignment(
                creator1, creator2
            )
            factor_scores[CompatibilityFactor.COMMUNICATION_STYLE] = await self._calculate_communication_compatibility(
                creator1, creator2
            )
            
            # Adjust weights based on collaboration type
            adjusted_weights = self._adjust_weights_for_collaboration_type(collaboration_type)
            
            # Calculate overall compatibility score
            overall_score = sum(
                factor_scores[factor] * adjusted_weights[factor] 
                for factor in factor_scores
            )
            
            return overall_score, factor_scores
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {str(e)}")
            return 0.0, {}
    
    async def _calculate_content_style_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """Calculate content style compatibility"""
        # Compare content categories
        categories1 = set(creator1.content_categories)
        categories2 = set(creator2.content_categories)
        
        if not categories1 or not categories2:
            return 0.5
        
        # Calculate Jaccard similarity
        intersection = len(categories1 & categories2)
        union = len(categories1 | categories2)
        
        if union == 0:
            return 0.5
        
        category_similarity = intersection / union
        
        # Consider portfolio quality similarity
        quality1 = creator1.portfolio_analysis.get('quality_score', 0.5)
        quality2 = creator2.portfolio_analysis.get('quality_score', 0.5)
        quality_similarity = 1 - abs(quality1 - quality2)
        
        # Combine scores
        return (category_similarity * 0.7 + quality_similarity * 0.3)
    
    async def _calculate_audience_overlap(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate audience overlap score"""
        demo1 = creator1.audience_demographics
        demo2 = creator2.audience_demographics
        
        if not demo1 or not demo2:
            return 0.5
        
        # Compare interests
        interests1 = set(demo1.get('interests', []))
        interests2 = set(demo2.get('interests', []))
        
        if interests1 and interests2:
            interest_overlap = len(interests1 & interests2) / len(interests1 | interests2)
        else:
            interest_overlap = 0.5
        
        # Compare age groups (optimal overlap: not too high, not too low)
        age1 = demo1.get('age_groups', {})
        age2 = demo2.get('age_groups', {})
        
        age_overlap = 0.5
        if age1 and age2:
            # Calculate overlap in age distribution
            common_ages = set(age1.keys()) & set(age2.keys())
            if common_ages:
                overlap_values = [min(age1[age], age2[age]) for age in common_ages]
                age_overlap = sum(overlap_values)
        
        # Optimal audience overlap is around 0.3-0.7 (not too much, not too little)
        if 0.3 <= interest_overlap <= 0.7:
            overlap_score = 1.0
        else:
            overlap_score = 1 - abs(interest_overlap - 0.5) * 2
        
        return overlap_score * 0.6 + age_overlap * 0.4
    
    async def _calculate_skill_complementarity(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate skill complementarity score"""
        skills1 = set(creator1.skill_tags)
        skills2 = set(creator2.skill_tags)
        
        if not skills1 or not skills2:
            return 0.3
        
        # Perfect complementarity: minimal overlap with high value skills
        overlap = len(skills1 & skills2)
        total_unique = len(skills1 | skills2)
        
        if total_unique == 0:
            return 0.3
        
        # High complementarity when skills don't overlap much but are valuable together
        complementarity_score = 1 - (overlap / total_unique)
        
        # Boost for known complementary skill pairs
        complementary_pairs = [
            ('composition', 'vocals'),
            ('filming', 'editing'),
            ('writing', 'photography'),
            ('production', 'mixing')
        ]
        
        bonus = 0
        for skill1, skill2 in complementary_pairs:
            if (skill1 in skills1 and skill2 in skills2) or (skill1 in skills2 and skill2 in skills1):
                bonus += 0.2
        
        return min(complementarity_score + bonus, 1.0)
    
    async def _calculate_availability_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate availability compatibility"""
        avail1 = creator1.availability
        avail2 = creator2.availability
        
        if not avail1 or not avail2:
            return 0.5
        
        # Compare time zones
        tz1 = avail1.get('timezone', 'UTC')
        tz2 = avail2.get('timezone', 'UTC')
        
        # Simple timezone compatibility (same or close)
        tz_score = 1.0 if tz1 == tz2 else 0.7
        
        # Compare working hours
        hours1 = avail1.get('working_hours', {})
        hours2 = avail2.get('working_hours', {})
        
        if hours1 and hours2:
            # Calculate overlap in working hours
            start1 = hours1.get('start', 9)
            end1 = hours1.get('end', 17)
            start2 = hours2.get('start', 9)
            end2 = hours2.get('end', 17)
            
            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)
            
            if overlap_start < overlap_end:
                overlap_hours = overlap_end - overlap_start
                total_hours = max(end1 - start1, end2 - start2)
                hours_score = overlap_hours / total_hours
            else:
                hours_score = 0.0
        else:
            hours_score = 0.5
        
        return tz_score * 0.4 + hours_score * 0.6
    
    async def _calculate_location_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate location compatibility"""
        loc1 = creator1.location
        loc2 = creator2.location
        
        if not loc1 or not loc2:
            return 0.5  # Unknown locations get neutral score
        
        # Compare countries
        country1 = loc1.get('country', '')
        country2 = loc2.get('country', '')
        
        if country1 == country2:
            # Same country - check cities/regions
            city1 = loc1.get('city', '')
            city2 = loc2.get('city', '')
            
            if city1 == city2:
                return 1.0  # Same city
            else:
                return 0.8  # Same country, different city
        else:
            # Different countries - check continents or regions
            return 0.4  # Different countries
    
    async def _calculate_experience_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate experience level compatibility"""
        # Use social metrics and portfolio analysis as experience indicators
        metrics1 = creator1.social_metrics
        metrics2 = creator2.social_metrics
        portfolio1 = creator1.portfolio_analysis
        portfolio2 = creator2.portfolio_analysis
        
        # Calculate experience scores
        exp1 = self._calculate_experience_score(metrics1, portfolio1)
        exp2 = self._calculate_experience_score(metrics2, portfolio2)
        
        # Optimal: similar experience levels or mentorship opportunity
        exp_diff = abs(exp1 - exp2)
        
        if exp_diff < 0.2:
            return 1.0  # Very similar experience
        elif exp_diff < 0.4:
            return 0.8  # Somewhat similar
        elif exp_diff > 0.6:
            return 0.9  # Good for mentorship
        else:
            return 0.6  # Moderate compatibility
    
    def _calculate_experience_score(
        self, 
        social_metrics: Dict[str, int], 
        portfolio_analysis: Dict[str, Any]
    ) -> float:
        """
Calculate single experience score"""
        followers = social_metrics.get('followers', 0)
        total_content = portfolio_analysis.get('total_content', 0)
        quality_score = portfolio_analysis.get('quality_score', 0)
        
        # Normalize followers (log scale)
        follower_score = min(math.log10(max(followers, 10)) / 6, 1.0)  # Max at 1M followers
        content_score = min(total_content / 50, 1.0)  # Max at 50 pieces of content
        
        return (follower_score * 0.4 + content_score * 0.3 + quality_score * 0.3)
    
    async def _calculate_brand_alignment(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate brand alignment score"""
        values1 = set(creator1.brand_values)
        values2 = set(creator2.brand_values)
        
        if not values1 or not values2:
            return 0.5
        
        # Calculate overlap in brand values
        common_values = len(values1 & values2)
        total_values = len(values1 | values2)
        
        if total_values == 0:
            return 0.5
        
        alignment_score = common_values / total_values
        
        # High alignment is good for brand partnerships
        return alignment_score
    
    async def _calculate_communication_compatibility(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate communication style compatibility"""
        comm1 = creator1.communication_preferences
        comm2 = creator2.communication_preferences
        
        if not comm1 or not comm2:
            return 0.5
        
        # Compare preferred communication methods
        methods1 = set(comm1.get('preferred_methods', []))
        methods2 = set(comm2.get('preferred_methods', []))
        
        if methods1 and methods2:
            method_overlap = len(methods1 & methods2) / len(methods1 | methods2)
        else:
            method_overlap = 0.5
        
        # Compare response times
        response1 = comm1.get('response_time', 'medium')
        response2 = comm2.get('response_time', 'medium')
        
        response_compatibility = 1.0 if response1 == response2 else 0.7
        
        return method_overlap * 0.6 + response_compatibility * 0.4
    
    def _adjust_weights_for_collaboration_type(
        self, 
        collaboration_type: Optional[CollaborationType]
    ) -> Dict[CompatibilityFactor, float]:
        """
Adjust factor weights based on collaboration type"""
        weights = self.factor_weights.copy()
        
        if not collaboration_type:
            return weights
        
        # Adjust weights based on collaboration type
        if collaboration_type == CollaborationType.SKILL_EXCHANGE:
            weights[CompatibilityFactor.SKILL_COMPLEMENTARITY] *= 1.5
        elif collaboration_type == CollaborationType.BRAND_PARTNERSHIP:
            weights[CompatibilityFactor.BRAND_ALIGNMENT] *= 1.5
            weights[CompatibilityFactor.AUDIENCE_OVERLAP] *= 1.2
        elif collaboration_type == CollaborationType.MENTORSHIP:
            weights[CompatibilityFactor.EXPERIENCE_LEVEL] *= 1.5
        elif collaboration_type == CollaborationType.TOUR_COLLABORATION:
            weights[CompatibilityFactor.LOCATION_PROXIMITY] *= 1.3
        
        # Normalize weights
        total_weight = sum(weights.values())
        for factor in weights:
            weights[factor] /= total_weight
        
        return weights

class CollaborationMatcher:
    """
Main collaboration matching engine"""
    
    def __init__(self):
        self.creator_analyzer = CreatorAnalyzer()
        self.compatibility_calculator = CompatibilityCalculator()
        self.creator_database = {}  # In production, use proper database
        self.opportunity_database = {}
    
    async def find_collaboration_matches(
        self, 
        creator_profile: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None,
        max_matches: int = 10
    ) -> List[MatchResult]:
        """
Find best collaboration matches for a creator"""
        try:
            matches = []
            
            # Find creator-to-creator matches
            creator_matches = await self._find_creator_matches(
                creator_profile, collaboration_type, max_matches
            )
            matches.extend(creator_matches)
            
            # Find opportunity matches
            opportunity_matches = await self._find_opportunity_matches(
                creator_profile, collaboration_type, max_matches
            )
            matches.extend(opportunity_matches)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            return matches[:max_matches]
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            return []
    
    async def _find_creator_matches(
        self, 
        target_creator: CreatorProfile,
        collaboration_type: Optional[CollaborationType],
        max_matches: int
    ) -> List[MatchResult]:
        """Find matches with other creators"""
        matches = []
        
        for creator_id, creator_profile in self.creator_database.items():
            if creator_id == target_creator.creator_id:
                continue  # Skip self
            
            # Calculate compatibility
            compatibility_score, breakdown = await self.compatibility_calculator.calculate_compatibility(
                target_creator, creator_profile, collaboration_type
            )
            
            # Only consider matches above threshold
            if compatibility_score < 0.4:
                continue
            
            # Generate match reasons
            match_reasons = await self._generate_match_reasons(
                target_creator, creator_profile, breakdown
            )
            
            # Identify potential challenges
            challenges = await self._identify_challenges(
                target_creator, creator_profile, breakdown
            )
            
            # Recommend collaboration types
            recommended_types = await self._recommend_collaboration_types(
                target_creator, creator_profile, breakdown
            )
            
            # Calculate success probability
            success_probability = await self._calculate_success_probability(
                compatibility_score, target_creator, creator_profile
            )
            
            # Generate suggested terms
            suggested_terms = await self._generate_suggested_terms(
                target_creator, creator_profile, recommended_types[0] if recommended_types else None
            )
            
            match = MatchResult(
                match_id=f"match_{target_creator.creator_id}_{creator_id}",
                creator1=target_creator,
                creator2=creator_profile,
                opportunity=None,
                compatibility_score=compatibility_score,
                compatibility_breakdown=breakdown,
                match_reasons=match_reasons,
                potential_challenges=challenges,
                recommended_collaboration_types=recommended_types,
                success_probability=success_probability,
                suggested_terms=suggested_terms
            )
            
            matches.append(match)
        
        return matches
    
    async def _find_opportunity_matches(
        self, 
        creator_profile: CreatorProfile,
        collaboration_type: Optional[CollaborationType],
        max_matches: int
    ) -> List[MatchResult]:
        """Find matches with collaboration opportunities"""
        matches = []
        
        for opp_id, opportunity in self.opportunity_database.items():
            # Check if creator type matches
            if (opportunity.preferred_creator_types and 
                creator_profile.creator_type not in opportunity.preferred_creator_types):
                continue
            
            # Check if collaboration type matches
            if (collaboration_type and 
                opportunity.collaboration_type != collaboration_type):
                continue
            
            # Calculate match score for opportunity
            match_score = await self._calculate_opportunity_match_score(
                creator_profile, opportunity
            )
            
            if match_score < 0.5:
                continue
            
            # Generate match details
            match_reasons = await self._generate_opportunity_match_reasons(
                creator_profile, opportunity, match_score
            )
            
            challenges = await self._identify_opportunity_challenges(
                creator_profile, opportunity
            )
            
            success_probability = min(match_score * 1.2, 1.0)  # Boost for good opportunities
            
            suggested_terms = await self._generate_opportunity_terms(
                creator_profile, opportunity
            )
            
            match = MatchResult(
                match_id=f"opp_match_{creator_profile.creator_id}_{opp_id}",
                creator1=creator_profile,
                creator2=None,
                opportunity=opportunity,
                compatibility_score=match_score,
                compatibility_breakdown={},
                match_reasons=match_reasons,
                potential_challenges=challenges,
                recommended_collaboration_types=[opportunity.collaboration_type],
                success_probability=success_probability,
                suggested_terms=suggested_terms
            )
            
            matches.append(match)
        
        return matches
    
    async def _calculate_opportunity_match_score(
        self, 
        creator: CreatorProfile, 
        opportunity: CollaborationOpportunity
    ) -> float:
        """Calculate match score for opportunity"""
        score_factors = []
        
        # Skill match
        creator_skills = set(creator.skill_tags)
        required_skills = set(opportunity.required_skills)
        
        if required_skills:
            skill_match = len(creator_skills & required_skills) / len(required_skills)
            score_factors.append(skill_match)
        
        # Experience level match
        creator_exp = self.compatibility_calculator._calculate_experience_score(
            creator.social_metrics, creator.portfolio_analysis
        )
        
        # Assume opportunities have experience requirements
        if creator_exp > 0.7:  # High experience creator
            score_factors.append(0.9)
        elif creator_exp > 0.4:  # Medium experience
            score_factors.append(0.8)
        else:  # Beginner
            score_factors.append(0.6)
        
        # Location match
        if opportunity.location_requirements:
            req_location = opportunity.location_requirements
            creator_location = creator.location
            
            if (req_location.get('remote_ok', True) or 
                creator_location.get('country') == req_location.get('country')):
                score_factors.append(0.9)
            else:
                score_factors.append(0.3)
        else:
            score_factors.append(0.8)  # No location restrictions
        
        return sum(score_factors) / len(score_factors) if score_factors else 0.5
    
    async def _generate_match_reasons(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        breakdown: Dict[CompatibilityFactor, float]
    ) -> List[str]:
        """
Generate human-readable match reasons"""
        reasons = []
        
        # High compatibility factors
        for factor, score in breakdown.items():
            if score > 0.7:
                if factor == CompatibilityFactor.SKILL_COMPLEMENTARITY:
                    reasons.append("Complementary skills for productive collaboration")
                elif factor == CompatibilityFactor.AUDIENCE_OVERLAP:
                    reasons.append("Similar target audiences for cross-promotion")
                elif factor == CompatibilityFactor.CONTENT_STYLE:
                    reasons.append("Compatible content styles and quality")
                elif factor == CompatibilityFactor.BRAND_ALIGNMENT:
                    reasons.append("Aligned brand values and messaging")
        
        # Common interests
        common_categories = set(creator1.content_categories) & set(creator2.content_categories)
        if common_categories:
            reasons.append(f"Shared interests in {', '.join(list(common_categories)[:2])}")
        
        # Experience compatibility
        if abs(self.compatibility_calculator._calculate_experience_score(
            creator1.social_metrics, creator1.portfolio_analysis
        ) - self.compatibility_calculator._calculate_experience_score(
            creator2.social_metrics, creator2.portfolio_analysis
        )) < 0.2:
            reasons.append("Similar experience levels for effective partnership")
        
        return reasons[:3]  # Top 3 reasons
    
    async def _identify_challenges(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        breakdown: Dict[CompatibilityFactor, float]
    ) -> List[str]:
        """Identify potential collaboration challenges"""
        challenges = []
        
        # Low compatibility factors
        for factor, score in breakdown.items():
            if score < 0.4:
                if factor == CompatibilityFactor.LOCATION_PROXIMITY:
                    challenges.append("Different locations may require remote collaboration")
                elif factor == CompatibilityFactor.AVAILABILITY:
                    challenges.append("Different time zones or schedules")
                elif factor == CompatibilityFactor.COMMUNICATION_STYLE:
                    challenges.append("Different communication preferences")
                elif factor == CompatibilityFactor.EXPERIENCE_LEVEL:
                    challenges.append("Significant experience gap may require mentorship approach")
        
        return challenges[:2]  # Top 2 challenges
    
    async def _recommend_collaboration_types(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        breakdown: Dict[CompatibilityFactor, float]
    ) -> List[CollaborationType]:
        """Recommend best collaboration types"""
        recommendations = []
        
        # Based on compatibility strengths
        if breakdown.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0) > 0.7:
            recommendations.append(CollaborationType.SKILL_EXCHANGE)
            recommendations.append(CollaborationType.JOINT_PROJECT)
        
        if breakdown.get(CompatibilityFactor.AUDIENCE_OVERLAP, 0) > 0.6:
            recommendations.append(CollaborationType.CROSS_PROMOTION)
        
        if breakdown.get(CompatibilityFactor.BRAND_ALIGNMENT, 0) > 0.8:
            recommendations.append(CollaborationType.BRAND_PARTNERSHIP)
        
        # Based on creator types
        if (creator1.creator_type == CreatorType.MUSICIAN and 
            creator2.creator_type == CreatorType.MUSICIAN):
            recommendations.append(CollaborationType.REMIX_COLLABORATION)
        
        # Default fallback
        if not recommendations:
            recommendations.append(CollaborationType.CONTENT_CREATION)
        
        return list(set(recommendations))[:3]  # Top 3 unique recommendations
    
    async def _calculate_success_probability(
        self, 
        compatibility_score: float, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """
Calculate probability of successful collaboration"""
        base_probability = compatibility_score
        
        # Boost for collaboration experience
        collab_exp1 = len(creator1.collaboration_history) > 0
        collab_exp2 = len(creator2.collaboration_history) > 0
        
        if collab_exp1 and collab_exp2:
            base_probability += 0.1
        elif collab_exp1 or collab_exp2:
            base_probability += 0.05
        
        # Boost for high engagement creators
        if (creator1.engagement_metrics.get('average_engagement', 0) > 0.05 and
            creator2.engagement_metrics.get('average_engagement', 0) > 0.05):
            base_probability += 0.1
        
        return min(base_probability, 1.0)
    
    async def _generate_suggested_terms(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        collaboration_type: Optional[CollaborationType]
    ) -> Dict[str, Any]:
        """
Generate suggested collaboration terms"""
        terms = {
            'duration': '1-3 months',
            'deliverables': [],
            'revenue_split': '50/50',
            'responsibilities': {},
            'timeline': {}
        }
        
        if not collaboration_type:
            return terms
        
        # Customize based on collaboration type
        if collaboration_type == CollaborationType.CONTENT_CREATION:
            terms['deliverables'] = ['joint content piece', 'cross-promotion posts']
            terms['timeline'] = {
                'planning': '1 week',
                'creation': '2 weeks', 
                'promotion': '1 week'
            }
        elif collaboration_type == CollaborationType.SKILL_EXCHANGE:
            terms['deliverables'] = ['skill sharing sessions', 'collaborative project']
            terms['duration'] = '2-4 weeks'
        
        # Customize responsibilities based on skills
        skills1 = creator1.skill_tags
        skills2 = creator2.skill_tags
        
        if 'production' in skills1:
            terms['responsibilities'][creator1.name] = 'Production and technical aspects'
        if 'marketing' in skills2:
            terms['responsibilities'][creator2.name] = 'Marketing and promotion'
        
        return terms
    
    async def _generate_opportunity_match_reasons(
        self, 
        creator: CreatorProfile, 
        opportunity: CollaborationOpportunity,
        match_score: float
    ) -> List[str]:
        """
Generate reasons for opportunity match"""
        reasons = []
        
        # Skill alignment
        creator_skills = set(creator.skill_tags)
        required_skills = set(opportunity.required_skills)
        matching_skills = creator_skills & required_skills
        
        if matching_skills:
            reasons.append(f"Strong skill match: {', '.join(list(matching_skills)[:2])}")
        
        # Experience level
        creator_exp = self.compatibility_calculator._calculate_experience_score(
            creator.social_metrics, creator.portfolio_analysis
        )
        
        if creator_exp > 0.7:
            reasons.append("High experience level suitable for professional projects")
        
        # Portfolio quality
        quality = creator.portfolio_analysis.get('quality_score', 0)
        if quality > 0.7:
            reasons.append("High-quality portfolio demonstrates capability")
        
        return reasons[:2]
    
    async def _identify_opportunity_challenges(
        self, 
        creator: CreatorProfile, 
        opportunity: CollaborationOpportunity
    ) -> List[str]:
        """Identify challenges for opportunity match"""
        challenges = []
        
        # Timeline challenges
        if opportunity.deadline:
            days_left = (opportunity.deadline - datetime.utcnow()).days
            if days_left < 30:
                challenges.append("Tight deadline requires immediate start")
        
        # Location challenges
        if opportunity.location_requirements:
            if not opportunity.location_requirements.get('remote_ok', True):
                challenges.append("On-site work required")
        
        # Skill gaps
        creator_skills = set(creator.skill_tags)
        required_skills = set(opportunity.required_skills)
        missing_skills = required_skills - creator_skills
        
        if missing_skills:
            challenges.append(f"May need to develop: {', '.join(list(missing_skills)[:2])}")
        
        return challenges[:2]
    
    async def _generate_opportunity_terms(
        self, 
        creator: CreatorProfile, 
        opportunity: CollaborationOpportunity
    ) -> Dict[str, Any]:
        """Generate terms for opportunity match"""
        return {
            'duration': str(opportunity.duration) if opportunity.duration else 'To be determined',
            'budget_range': opportunity.budget_range,
            'deliverables': opportunity.deliverables,
            'deadline': opportunity.deadline.isoformat() if opportunity.deadline else None,
            'collaboration_type': opportunity.collaboration_type.value,
            'requirements': opportunity.required_skills
        }

# Export main classes
__all__ = [
    'CreatorType',
    'CollaborationType',
    'CompatibilityFactor',
    'CreatorProfile',
    'CollaborationOpportunity',
    'MatchResult',
    'CreatorAnalyzer',
    'CompatibilityCalculator',
    'CollaborationMatcher'
]
