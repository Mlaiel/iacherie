"""
🎵 Musician Workflow Intelligence - Intelligence Workflow Musiciens
================================================================

Module intelligence spécialisé pour surveillance workflow musiciens Ainflue.
Analytics performance, optimisation création musicale et collaboration.

Fonctionnalités:
- Analyse workflow création musicale
- Optimisation processus studio
- Tracking qualité audio
- Collaboration musicale intelligente
- Prédiction succès compositions
- Monitoring engagement fans
- Analytics streaming multiplateforme

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import statistics


class MusicGenre(Enum):
    """Genres musicaux supportés"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    FOLK = "folk"
    REGGAE = "reggae"


class WorkflowStage(Enum):
    """Étapes workflow musical"""
    COMPOSITION = "composition"
    RECORDING = "recording"
    MIXING = "mixing"
    MASTERING = "mastering"
    PRODUCTION = "production"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    PROMOTION = "promotion"


@dataclass
class MusicTrack:
    """Piste musicale"""
    track_id: str
    title: str
    artist_id: str
    genre: MusicGenre
    duration: float  # seconds
    bpm: Optional[int]
    key: Optional[str]
    audio_quality_score: float
    composition_date: datetime
    recording_date: Optional[datetime]
    release_date: Optional[datetime]
    collaboration_artists: List[str] = field(default_factory=list)
    workflow_stage: WorkflowStage = WorkflowStage.COMPOSITION


@dataclass
class MusicianProfile:
    """Profil musicien détaillé"""
    musician_id: str
    stage_name: str
    primary_genre: MusicGenre
    secondary_genres: List[MusicGenre]
    instruments: List[str]
    vocal_range: Optional[str]
    studio_setup_quality: float  # 0.0-1.0
    production_skills: Dict[str, float]  # composition, mixing, mastering
    collaboration_style: str
    fan_engagement_rate: float
    streaming_stats: Dict[str, int]
    workflow_efficiency: float
    creative_output_rate: float  # tracks per month


@dataclass
class WorkflowMetrics:
    """Métriques workflow musical"""
    musician_id: str
    avg_composition_time: float  # hours
    avg_recording_time: float
    avg_mixing_time: float
    avg_mastering_time: float
    total_workflow_time: float
    quality_consistency: float
    collaboration_frequency: float
    release_frequency: float  # tracks per month
    fan_engagement_growth: float
    revenue_per_track: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MusicianWorkflowIntelligence:
    """Intelligence workflow musiciens enterprise Ainflue"""
    
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()
        
        # Data stores
        self.musician_profiles: Dict[str, MusicianProfile] = {}
        self.music_tracks: Dict[str, MusicTrack] = {}
        self.workflow_metrics: Dict[str, List[WorkflowMetrics]] = {}
        self.collaboration_networks: Dict[str, List[str]] = {}
        
        # Analytics
        self.genre_trends: Dict[MusicGenre, float] = {}
        self.workflow_benchmarks: Dict[WorkflowStage, float] = {}
        self.quality_standards: Dict[str, float] = {}
        
        # ML predictions
        self.success_prediction_weights = {
            'audio_quality': 0.25,
            'genre_trend': 0.20,
            'artist_engagement': 0.20,
            'collaboration_factor': 0.15,
            'workflow_efficiency': 0.10,
            'release_timing': 0.10
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("musician_workflow")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation intelligence workflow musiciens"""
        self.logger.info("🎵 Initialisation Musician Workflow Intelligence...")
        
        # Initialize sample data
        await self._load_sample_musicians()
        await self._initialize_workflow_benchmarks()
        
        self.logger.info(f"✅ Intelligence musiciens initialisée - {len(self.musician_profiles)} musiciens")
    
    async def _load_sample_musicians(self):
        """Chargement musiciens exemples"""
        sample_musicians = [
            {
                'musician_id': 'musician_alex_harmony',
                'stage_name': 'Alex Harmony',
                'primary_genre': MusicGenre.POP,
                'secondary_genres': [MusicGenre.R_AND_B, MusicGenre.ELECTRONIC],
                'instruments': ['piano', 'guitar', 'vocals'],
                'vocal_range': 'tenor',
                'studio_setup_quality': 0.85,
                'production_skills': {'composition': 0.9, 'mixing': 0.7, 'mastering': 0.6}
            },
            {
                'musician_id': 'musician_beat_master',
                'stage_name': 'Beat Master',
                'primary_genre': MusicGenre.HIP_HOP,
                'secondary_genres': [MusicGenre.R_AND_B, MusicGenre.ELECTRONIC],
                'instruments': ['drums', 'sampler', 'synthesizer'],
                'vocal_range': 'baritone',
                'studio_setup_quality': 0.92,
                'production_skills': {'composition': 0.8, 'mixing': 0.95, 'mastering': 0.85}
            },
            {
                'musician_id': 'musician_indie_soul',
                'stage_name': 'Indie Soul',
                'primary_genre': MusicGenre.INDIE,
                'secondary_genres': [MusicGenre.FOLK, MusicGenre.ROCK],
                'instruments': ['guitar', 'vocals', 'harmonica'],
                'vocal_range': 'alto',
                'studio_setup_quality': 0.75,
                'production_skills': {'composition': 0.95, 'mixing': 0.6, 'mastering': 0.5}
            }
        ]
        
        for musician_data in sample_musicians:
            profile = MusicianProfile(
                musician_id=musician_data['musician_id'],
                stage_name=musician_data['stage_name'],
                primary_genre=musician_data['primary_genre'],
                secondary_genres=musician_data['secondary_genres'],
                instruments=musician_data['instruments'],
                vocal_range=musician_data['vocal_range'],
                studio_setup_quality=musician_data['studio_setup_quality'],
                production_skills=musician_data['production_skills'],
                collaboration_style="open" if len(musician_data['secondary_genres']) > 1 else "selective",
                fan_engagement_rate=0.12 + (musician_data['studio_setup_quality'] * 0.1),
                streaming_stats={
                    'spotify_monthly_listeners': int(10000 + musician_data['studio_setup_quality'] * 40000),
                    'youtube_subscribers': int(5000 + musician_data['studio_setup_quality'] * 20000),
                    'soundcloud_followers': int(2000 + musician_data['studio_setup_quality'] * 8000)
                },
                workflow_efficiency=0.7 + (sum(musician_data['production_skills'].values()) / 3) * 0.3,
                creative_output_rate=2.0 + musician_data['studio_setup_quality'] * 2.0
            )
            
            self.musician_profiles[musician_data['musician_id']] = profile
            
            # Generate sample tracks
            await self._generate_sample_tracks(musician_data['musician_id'], 3)
            
            # Generate workflow metrics
            await self._generate_sample_workflow_metrics(musician_data['musician_id'])
    
    async def _generate_sample_tracks(self, musician_id: str, count: int):
        """Génération pistes exemples"""
        musician = self.musician_profiles[musician_id]
        
        for i in range(count):
            track = MusicTrack(
                track_id=f"{musician_id}_track_{i+1}",
                title=f"Track {i+1} - {musician.stage_name}",
                artist_id=musician_id,
                genre=musician.primary_genre,
                duration=180.0 + (i * 30),  # 3-5 minutes
                bpm=120 + (i * 10),
                key="C" if i % 2 == 0 else "G",
                audio_quality_score=0.8 + (musician.studio_setup_quality * 0.2),
                composition_date=datetime.utcnow() - timedelta(days=30-i*10),
                recording_date=datetime.utcnow() - timedelta(days=25-i*8),
                release_date=datetime.utcnow() - timedelta(days=15-i*5) if i < 2 else None,
                workflow_stage=WorkflowStage.DISTRIBUTION if i < 2 else WorkflowStage.MASTERING
            )
            
            self.music_tracks[track.track_id] = track
    
    async def _generate_sample_workflow_metrics(self, musician_id: str):
        """Génération métriques workflow"""
        musician = self.musician_profiles[musician_id]
        
        # Base metrics influenced by skills and setup
        base_efficiency = musician.workflow_efficiency
        
        metrics = WorkflowMetrics(
            musician_id=musician_id,
            avg_composition_time=8.0 / base_efficiency,  # hours
            avg_recording_time=6.0 / base_efficiency,
            avg_mixing_time=4.0 / (musician.production_skills.get('mixing', 0.5) + 0.5),
            avg_mastering_time=3.0 / (musician.production_skills.get('mastering', 0.5) + 0.5),
            total_workflow_time=0,  # Will be calculated
            quality_consistency=musician.studio_setup_quality * 0.9 + 0.1,
            collaboration_frequency=len(musician.secondary_genres) * 0.5,
            release_frequency=musician.creative_output_rate,
            fan_engagement_growth=musician.fan_engagement_rate * 100,
            revenue_per_track=500 + musician.studio_setup_quality * 2000
        )
        
        # Calculate total workflow time
        metrics.total_workflow_time = (
            metrics.avg_composition_time +
            metrics.avg_recording_time +
            metrics.avg_mixing_time +
            metrics.avg_mastering_time
        )
        
        if musician_id not in self.workflow_metrics:
            self.workflow_metrics[musician_id] = []
        
        self.workflow_metrics[musician_id].append(metrics)
    
    async def _initialize_workflow_benchmarks(self):
        """Initialisation benchmarks workflow"""
        self.workflow_benchmarks = {
            WorkflowStage.COMPOSITION: 8.0,  # hours
            WorkflowStage.RECORDING: 6.0,
            WorkflowStage.MIXING: 4.0,
            WorkflowStage.MASTERING: 3.0,
            WorkflowStage.PRODUCTION: 2.0,
            WorkflowStage.COLLABORATION: 1.0,
            WorkflowStage.DISTRIBUTION: 0.5,
            WorkflowStage.PROMOTION: 2.0
        }
        
        self.quality_standards = {
            'audio_quality_min': 0.85,
            'consistency_min': 0.80,
            'engagement_growth_min': 5.0,  # % per month
            'release_frequency_optimal': 1.5  # tracks per month
        }
    
    async def analyze_workflow_efficiency(self, musician_id: str) -> Dict[str, Any]:
        """Analyse efficacité workflow"""
        if musician_id not in self.workflow_metrics:
            return {'error': 'No workflow data available'}
        
        musician = self.musician_profiles.get(musician_id)
        metrics_history = self.workflow_metrics[musician_id]
        latest_metrics = metrics_history[-1]
        
        # Efficiency analysis
        efficiency_scores = {}
        
        for stage, benchmark_time in self.workflow_benchmarks.items():
            if stage == WorkflowStage.COMPOSITION:
                actual_time = latest_metrics.avg_composition_time
            elif stage == WorkflowStage.RECORDING:
                actual_time = latest_metrics.avg_recording_time
            elif stage == WorkflowStage.MIXING:
                actual_time = latest_metrics.avg_mixing_time
            elif stage == WorkflowStage.MASTERING:
                actual_time = latest_metrics.avg_mastering_time
            else:
                continue
            
            # Efficiency = benchmark / actual (higher is better)
            efficiency = min(benchmark_time / actual_time, 2.0)  # Cap at 2.0x
            efficiency_scores[stage.value] = efficiency
        
        # Overall efficiency
        overall_efficiency = statistics.mean(efficiency_scores.values())
        
        # Bottleneck identification
        bottleneck_stage = min(efficiency_scores.items(), key=lambda x: x[1])
        
        # Improvement suggestions
        suggestions = await self._generate_workflow_suggestions(musician_id, efficiency_scores)
        
        return {
            'musician_id': musician_id,
            'musician_name': musician.stage_name if musician else 'Unknown',
            'overall_efficiency': overall_efficiency,
            'stage_efficiencies': efficiency_scores,
            'bottleneck_stage': bottleneck_stage[0],
            'bottleneck_efficiency': bottleneck_stage[1],
            'total_workflow_time': latest_metrics.total_workflow_time,
            'quality_consistency': latest_metrics.quality_consistency,
            'improvement_suggestions': suggestions,
            'benchmark_comparison': {
                stage.value: {
                    'actual': getattr(latest_metrics, f'avg_{stage.value}_time', 0),
                    'benchmark': benchmark_time,
                    'performance': 'above' if efficiency_scores.get(stage.value, 0) > 1.0 else 'below'
                }
                for stage, benchmark_time in self.workflow_benchmarks.items()
                if stage.value in efficiency_scores
            }
        }
    
    async def _generate_workflow_suggestions(self, musician_id: str, efficiency_scores: Dict[str, float]) -> List[str]:
        """Génération suggestions amélioration workflow"""
        suggestions = []
        musician = self.musician_profiles.get(musician_id)
        
        if not musician:
            return suggestions
        
        # Composition efficiency
        if efficiency_scores.get('composition', 1.0) < 0.8:
            suggestions.append("Consider using composition software templates to speed up initial creation")
            if musician.production_skills.get('composition', 0) < 0.8:
                suggestions.append("Invest in composition training or collaborate with experienced composers")
        
        # Recording efficiency
        if efficiency_scores.get('recording', 1.0) < 0.8:
            if musician.studio_setup_quality < 0.8:
                suggestions.append("Upgrade studio equipment for faster, higher-quality recording sessions")
            suggestions.append("Pre-plan recording sessions with detailed arrangements")
        
        # Mixing efficiency
        if efficiency_scores.get('mixing', 1.0) < 0.8:
            if musician.production_skills.get('mixing', 0) < 0.7:
                suggestions.append("Consider outsourcing mixing to specialists or invest in mixing education")
            suggestions.append("Use mixing templates and presets to speed up workflow")
        
        # Mastering efficiency
        if efficiency_scores.get('mastering', 1.0) < 0.8:
            if musician.production_skills.get('mastering', 0) < 0.7:
                suggestions.append("Outsource mastering to professional mastering engineers")
            suggestions.append("Use AI-powered mastering tools for initial passes")
        
        # General suggestions
        if len([s for s in efficiency_scores.values() if s < 0.9]) >= 2:
            suggestions.append("Consider workflow automation tools and project management software")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def predict_track_success(self, track_id: str) -> Dict[str, Any]:
        """Prédiction succès piste"""
        track = self.music_tracks.get(track_id)
        if not track:
            return {'error': 'Track not found'}
        
        musician = self.musician_profiles.get(track.artist_id)
        if not musician:
            return {'error': 'Musician not found'}
        
        # Success factors
        success_factors = {}
        
        # Audio quality factor
        success_factors['audio_quality'] = min(track.audio_quality_score, 1.0)
        
        # Genre trend factor (simplified)
        genre_popularity = {
            MusicGenre.POP: 0.9,
            MusicGenre.HIP_HOP: 0.85,
            MusicGenre.ELECTRONIC: 0.8,
            MusicGenre.R_AND_B: 0.75,
            MusicGenre.ROCK: 0.7,
            MusicGenre.INDIE: 0.65,
            MusicGenre.JAZZ: 0.6,
            MusicGenre.FOLK: 0.55,
            MusicGenre.CLASSICAL: 0.5,
            MusicGenre.REGGAE: 0.6
        }
        success_factors['genre_trend'] = genre_popularity.get(track.genre, 0.5)
        
        # Artist engagement factor
        success_factors['artist_engagement'] = musician.fan_engagement_rate
        
        # Collaboration factor
        success_factors['collaboration_factor'] = min(len(track.collaboration_artists) * 0.2 + 0.6, 1.0)
        
        # Workflow efficiency factor
        workflow_metrics = self.workflow_metrics.get(track.artist_id, [])
        if workflow_metrics:
            latest_metrics = workflow_metrics[-1]
            success_factors['workflow_efficiency'] = min(
                (20.0 / latest_metrics.total_workflow_time) if latest_metrics.total_workflow_time > 0 else 0.5,
                1.0
            )
        else:
            success_factors['workflow_efficiency'] = 0.5
        
        # Release timing factor (simplified - weekends are better)
        if track.release_date:
            release_weekday = track.release_date.weekday()
            success_factors['release_timing'] = 0.9 if release_weekday in [4, 5] else 0.7  # Fri, Sat
        else:
            success_factors['release_timing'] = 0.5
        
        # Calculate weighted success score
        success_score = sum(
            success_factors[factor] * self.success_prediction_weights[factor]
            for factor in success_factors
        )
        
        # Predict metrics
        base_streams = 10000
        predicted_streams = int(base_streams * (success_score ** 2) * 10)
        predicted_revenue = predicted_streams * 0.004  # ~$0.004 per stream
        
        return {
            'track_id': track_id,
            'track_title': track.title,
            'artist_name': musician.stage_name,
            'success_score': success_score,
            'success_factors': success_factors,
            'predictions': {
                'estimated_streams_first_month': predicted_streams,
                'estimated_revenue_first_month': round(predicted_revenue, 2),
                'viral_potential': 'high' if success_score > 0.8 else 'medium' if success_score > 0.6 else 'low',
                'recommended_promotion_budget': int(predicted_revenue * 0.3)  # 30% for promotion
            },
            'optimization_recommendations': await self._generate_track_optimization_recommendations(track, success_factors)
        }
    
    async def _generate_track_optimization_recommendations(self, track: MusicTrack, success_factors: Dict[str, float]) -> List[str]:
        """Génération recommandations optimisation piste"""
        recommendations = []
        
        if success_factors['audio_quality'] < 0.8:
            recommendations.append("Consider professional remastering to improve audio quality")
        
        if success_factors['collaboration_factor'] < 0.7:
            recommendations.append("Explore collaboration opportunities with complementary artists")
        
        if success_factors['release_timing'] < 0.8:
            recommendations.append("Plan release for Friday or Saturday for optimal engagement")
        
        if track.genre in [MusicGenre.CLASSICAL, MusicGenre.JAZZ]:
            recommendations.append("Target niche playlists and specialized streaming platforms")
        
        return recommendations[:3]
    
    async def analyze_collaboration_potential(self, musician1_id: str, musician2_id: str) -> Dict[str, Any]:
        """Analyse potentiel collaboration musicale"""
        musician1 = self.musician_profiles.get(musician1_id)
        musician2 = self.musician_profiles.get(musician2_id)
        
        if not musician1 or not musician2:
            return {'error': 'One or both musicians not found'}
        
        # Compatibility factors
        compatibility_score = 0.0
        
        # Genre compatibility
        genre_compatibility = 0.0
        if musician1.primary_genre == musician2.primary_genre:
            genre_compatibility = 1.0
        elif musician1.primary_genre in musician2.secondary_genres or musician2.primary_genre in musician1.secondary_genres:
            genre_compatibility = 0.8
        elif set(musician1.secondary_genres) & set(musician2.secondary_genres):
            genre_compatibility = 0.6
        else:
            genre_compatibility = 0.3
        
        # Skill complementarity
        skills1 = musician1.production_skills
        skills2 = musician2.production_skills
        skill_complementarity = 0.0
        
        for skill in ['composition', 'mixing', 'mastering']:
            skill_diff = abs(skills1.get(skill, 0.5) - skills2.get(skill, 0.5))
            # Moderate difference is good for complementarity
            skill_complementarity += 1.0 - skill_diff if skill_diff < 0.3 else 0.3
        
        skill_complementarity /= 3  # Average
        
        # Audience size compatibility
        streams1 = musician1.streaming_stats.get('spotify_monthly_listeners', 0)
        streams2 = musician2.streaming_stats.get('spotify_monthly_listeners', 0)
        audience_compatibility = min(streams1, streams2) / max(streams1, streams2) if max(streams1, streams2) > 0 else 0.5
        
        # Calculate overall compatibility
        compatibility_score = (
            genre_compatibility * 0.4 +
            skill_complementarity * 0.3 +
            audience_compatibility * 0.3
        )
        
        # Collaboration suggestions
        collaboration_type = self._suggest_collaboration_type(musician1, musician2, genre_compatibility)
        
        return {
            'musician1': {'id': musician1_id, 'name': musician1.stage_name},
            'musician2': {'id': musician2_id, 'name': musician2.stage_name},
            'compatibility_score': compatibility_score,
            'compatibility_factors': {
                'genre_compatibility': genre_compatibility,
                'skill_complementarity': skill_complementarity,
                'audience_compatibility': audience_compatibility
            },
            'collaboration_type': collaboration_type,
            'success_prediction': min(compatibility_score * 1.2, 1.0),  # Slight boost for optimism
            'recommended_approach': self._recommend_collaboration_approach(musician1, musician2, compatibility_score)
        }
    
    def _suggest_collaboration_type(self, musician1: MusicianProfile, musician2: MusicianProfile, genre_compatibility: float) -> str:
        """Suggestion type collaboration"""
        if genre_compatibility >= 0.8:
            return "full_track_collaboration"
        elif genre_compatibility >= 0.6:
            return "cross_genre_fusion"
        elif any(skill in musician1.instruments for skill in musician2.instruments):
            return "instrumental_collaboration"
        else:
            return "remix_collaboration"
    
    def _recommend_collaboration_approach(self, musician1: MusicianProfile, musician2: MusicianProfile, compatibility: float) -> str:
        """Recommandation approche collaboration"""
        if compatibility >= 0.8:
            return "Start with a full collaborative track - high success potential"
        elif compatibility >= 0.6:
            return "Begin with a remix or feature collaboration to test synergy"
        else:
            return "Consider a limited collaboration like instrumental backing or guest appearance"
    
    async def get_musician_insights(self, musician_id: str) -> Dict[str, Any]:
        """Insights détaillés musicien"""
        musician = self.musician_profiles.get(musician_id)
        if not musician:
            return {'error': 'Musician not found'}
        
        # Get workflow analysis
        workflow_analysis = await self.analyze_workflow_efficiency(musician_id)
        
        # Get tracks
        musician_tracks = [track for track in self.music_tracks.values() if track.artist_id == musician_id]
        
        # Track success predictions
        track_predictions = []
        for track in musician_tracks:
            prediction = await self.predict_track_success(track.track_id)
            if 'error' not in prediction:
                track_predictions.append(prediction)
        
        # Calculate averages
        avg_success_score = statistics.mean([p['success_score'] for p in track_predictions]) if track_predictions else 0
        total_predicted_revenue = sum([p['predictions']['estimated_revenue_first_month'] for p in track_predictions])
        
        return {
            'musician_profile': {
                'id': musician_id,
                'name': musician.stage_name,
                'primary_genre': musician.primary_genre.value,
                'instruments': musician.instruments,
                'studio_quality': musician.studio_setup_quality,
                'fan_engagement_rate': musician.fan_engagement_rate,
                'creative_output_rate': musician.creative_output_rate
            },
            'workflow_analysis': workflow_analysis,
            'track_portfolio': {
                'total_tracks': len(musician_tracks),
                'avg_success_score': avg_success_score,
                'total_predicted_revenue': round(total_predicted_revenue, 2),
                'top_track': max(track_predictions, key=lambda x: x['success_score']) if track_predictions else None
            },
            'optimization_priorities': await self._generate_musician_optimization_priorities(musician_id),
            'collaboration_readiness': musician.collaboration_style,
            'market_position': await self._analyze_market_position(musician)
        }
    
    async def _generate_musician_optimization_priorities(self, musician_id: str) -> List[str]:
        """Génération priorités optimisation musicien"""
        musician = self.musician_profiles.get(musician_id)
        workflow_analysis = await self.analyze_workflow_efficiency(musician_id)
        
        priorities = []
        
        # Workflow priorities
        if workflow_analysis.get('overall_efficiency', 1.0) < 0.8:
            priorities.append(f"Improve workflow efficiency - current bottleneck: {workflow_analysis.get('bottleneck_stage', 'unknown')}")
        
        # Skill priorities
        for skill, level in musician.production_skills.items():
            if level < 0.7:
                priorities.append(f"Develop {skill} skills (current: {level:.1f}/1.0)")
        
        # Equipment priorities
        if musician.studio_setup_quality < 0.8:
            priorities.append("Upgrade studio equipment for better production quality")
        
        # Output priorities
        if musician.creative_output_rate < 1.0:
            priorities.append("Increase creative output rate for better market presence")
        
        return priorities[:3]
    
    async def _analyze_market_position(self, musician: MusicianProfile) -> str:
        """Analyse position marché"""
        total_listeners = musician.streaming_stats.get('spotify_monthly_listeners', 0)
        
        if total_listeners > 100000:
            return "established"
        elif total_listeners > 50000:
            return "growing"
        elif total_listeners > 10000:
            return "emerging"
        else:
            return "starting"
    
    async def shutdown(self):
        """Arrêt propre module"""
        self.logger.info("⏹️ Arrêt Musician Workflow Intelligence...")
        
        # Clear data
        self.musician_profiles.clear()
        self.music_tracks.clear()
        self.workflow_metrics.clear()
        
        self.logger.info("✅ Musician Workflow Intelligence arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_musician_intelligence():
        class MockConfig:
            debug = True
        
        intelligence = MusicianWorkflowIntelligence(MockConfig())
        await intelligence.initialize()
        
        # Test workflow analysis
        analysis = await intelligence.analyze_workflow_efficiency('musician_alex_harmony')
        print(f"Workflow efficiency: {analysis.get('overall_efficiency', 0):.2f}")
        
        # Test track success prediction
        track_id = list(intelligence.music_tracks.keys())[0]
        prediction = await intelligence.predict_track_success(track_id)
        print(f"Track success score: {prediction.get('success_score', 0):.2f}")
        
        # Test collaboration analysis
        musicians = list(intelligence.musician_profiles.keys())
        if len(musicians) >= 2:
            collab = await intelligence.analyze_collaboration_potential(musicians[0], musicians[1])
            print(f"Collaboration compatibility: {collab.get('compatibility_score', 0):.2f}")
        
        print("✅ Musician Workflow Intelligence test passed")
        await intelligence.shutdown()
    
    asyncio.run(test_musician_intelligence())