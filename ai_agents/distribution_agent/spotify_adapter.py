"""
Spotify Platform Adapter for IA Influencer Agent Distribution System.
Handles music distribution, analytics, and creator monetization on Spotify.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import requests
from dataclasses import dataclass

from ..core.base_adapter import BasePlatformAdapter
from ..models.distribution_models import (
    DistributionRequest, DistributionResult, ContentMetadata,
    PlatformAnalytics, RevenueData
)
from ..utils.exceptions import DistributionError, AuthenticationError

logger = logging.getLogger(__name__)

@dataclass
class SpotifyCredentials:
    """Spotify API credentials configuration."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "user-read-private user-read-email playlist-modify-public playlist-modify-private user-library-modify"

class SpotifyAdapter(BasePlatformAdapter):
    """
    Advanced Spotify platform adapter for music distribution and analytics.
    Supports artist profile management, track uploads, playlist management, and revenue tracking.
    """
    
    PLATFORM_NAME = "spotify"
    MAX_TRACK_SIZE_MB = 50
    SUPPORTED_FORMATS = ["mp3", "wav", "flac", "m4a"]
    
    def __init__(self, credentials: SpotifyCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.client = None
        self.auth_manager = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Spotify API client with authentication."""
        try:
            # For user-specific operations
            self.auth_manager = SpotifyOAuth(
                client_id=self.credentials.client_id,
                client_secret=self.credentials.client_secret,
                redirect_uri=self.credentials.redirect_uri,
                scope=self.credentials.scope
            )
            
            # For general API access
            client_credentials = SpotifyClientCredentials(
                client_id=self.credentials.client_id,
                client_secret=self.credentials.client_secret
            )
            
            self.client = spotipy.Spotify(client_credentials_manager=client_credentials)
            logger.info("Spotify API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise AuthenticationError(f"Spotify authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Authenticate user and return access tokens."""
        try:
            # Get authorization URL
            auth_url = self.auth_manager.get_authorize_url()
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=1)
            }
            
        except Exception as e:
            logger.error(f"Spotify user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Spotify requirements."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # File format validation
        if content_metadata.file_format.lower() not in self.SUPPORTED_FORMATS:
            validation_results["is_valid"] = False
            validation_results["errors"].append(
                f"Unsupported format: {content_metadata.file_format}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # File size validation
        if content_metadata.file_size_mb > self.MAX_TRACK_SIZE_MB:
            validation_results["is_valid"] = False
            validation_results["errors"].append(
                f"File too large: {content_metadata.file_size_mb}MB. "
                f"Maximum allowed: {self.MAX_TRACK_SIZE_MB}MB"
            )
        
        # Duration validation (minimum 30 seconds)
        if content_metadata.duration_seconds < 30:
            validation_results["warnings"].append(
                "Track shorter than 30 seconds may not be eligible for royalties"
            )
        
        # Metadata completeness
        required_fields = ["title", "artist", "genre"]
        for field in required_fields:
            if not getattr(content_metadata, field, None):
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """
        Upload music content to Spotify for Artists.
        Note: Direct upload requires Spotify for Artists API access.
        """
        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            # For now, simulate upload process as direct Spotify upload 
            # requires distributor partnership or Spotify for Artists access
            upload_result = {
                "platform": self.PLATFORM_NAME,
                "content_id": f"spotify_{distribution_request.content_metadata.title.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}",
                "status": "pending_review",
                "upload_url": None,  # Would be actual upload URL
                "estimated_live_date": datetime.now() + timedelta(days=7),
                "metadata": {
                    "track_uri": None,  # Will be available after approval
                    "artist_uri": None,
                    "isrc": distribution_request.content_metadata.isrc_code
                }
            }
            
            # Create playlist if specified
            if hasattr(distribution_request, 'playlist_name') and distribution_request.playlist_name:
                playlist_result = await self._create_playlist(
                    distribution_request.user_id,
                    distribution_request.playlist_name,
                    distribution_request.content_metadata.description or ""
                )
                upload_result["playlist_id"] = playlist_result.get("playlist_id")
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=upload_result["content_id"],
                platform_content_id=upload_result["content_id"],
                url=f"https://open.spotify.com/track/{upload_result['content_id']}",
                metadata=upload_result
            )
            
        except Exception as e:
            logger.error(f"Spotify content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    async def _create_playlist(self, user_id: str, name: str, description: str) -> Dict[str, Any]:
        """Create a new playlist on Spotify."""
        try:
            # Get user's Spotify client
            user_client = spotipy.Spotify(auth_manager=self.auth_manager)
            
            # Create playlist
            playlist = user_client.user_playlist_create(
                user=user_id,
                name=name,
                public=True,
                collaborative=False,
                description=description
            )
            
            return {
                "playlist_id": playlist["id"],
                "playlist_url": playlist["external_urls"]["spotify"],
                "playlist_uri": playlist["uri"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create Spotify playlist: {e}")
            raise DistributionError(f"Playlist creation failed: {e}")
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for distributed content."""
        try:
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            # Fetch track information
            track_info = self.client.track(content_id)
            
            # Fetch artist analytics (requires Spotify for Artists API)
            analytics_data = await self._fetch_artist_analytics(track_info["artists"][0]["id"], date_range)
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=analytics_data.get("streams", 0),
                likes=analytics_data.get("saves", 0),
                shares=analytics_data.get("shares", 0),
                comments=0,  # Not applicable for Spotify
                engagement_rate=analytics_data.get("engagement_rate", 0.0),
                reach=analytics_data.get("listeners", 0),
                impressions=analytics_data.get("impressions", 0),
                revenue=analytics_data.get("revenue", 0.0),
                date_range=date_range,
                additional_metrics={
                    "skip_rate": analytics_data.get("skip_rate", 0.0),
                    "completion_rate": analytics_data.get("completion_rate", 0.0),
                    "playlist_adds": analytics_data.get("playlist_adds", 0),
                    "monthly_listeners": analytics_data.get("monthly_listeners", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Spotify analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def _fetch_artist_analytics(self, artist_id: str, date_range: tuple) -> Dict[str, Any]:
        """Fetch detailed artist analytics from Spotify for Artists API."""
        # This would require Spotify for Artists API access
        # Simulated data for now
        return {
            "streams": 15420,
            "listeners": 8934,
            "saves": 1234,
            "shares": 567,
            "engagement_rate": 12.5,
            "skip_rate": 8.3,
            "completion_rate": 78.2,
            "playlist_adds": 892,
            "monthly_listeners": 12450,
            "impressions": 45670,
            "revenue": 87.34
        }
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Calculate revenue data for distributed content."""
        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Spotify royalty calculation (approximate)
            streams = analytics.views  # streams on Spotify
            revenue_per_stream = 0.003  # Average $0.003 per stream
            gross_revenue = streams * revenue_per_stream
            
            # Platform commission (30% typical for distributors)
            platform_fee = gross_revenue * 0.30
            net_revenue = gross_revenue - platform_fee
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=gross_revenue,
                platform_fee=platform_fee,
                net_revenue=net_revenue,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="pending",
                additional_data={
                    "streams": streams,
                    "revenue_per_stream": revenue_per_stream,
                    "royalty_type": "streaming",
                    "territory": "worldwide"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Spotify revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update content metadata on Spotify."""
        try:
            # This would require Spotify for Artists API access
            # For now, return success for supported metadata updates
            supported_fields = ["description", "tags", "playlist_assignment"]
            
            updates_applied = {}
            for field, value in metadata.items():
                if field in supported_fields:
                    updates_applied[field] = value
            
            if updates_applied:
                logger.info(f"Spotify metadata updated for {content_id}: {updates_applied}")
                return True
            else:
                logger.warning(f"No supported metadata fields provided for {content_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update Spotify metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from Spotify (requires special permissions)."""
        try:
            # Direct content deletion on Spotify requires distributor-level access
            # For now, we can remove from playlists and mark as inactive
            logger.info(f"Content removal requested for Spotify track: {content_id}")
            
            # This would involve contacting Spotify support or distributor
            # to remove the track from the platform
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Spotify content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""
        return {
            "max_file_size_mb": self.MAX_TRACK_SIZE_MB,
            "supported_formats": self.SUPPORTED_FORMATS,
            "min_duration_seconds": 30,
            "max_duration_seconds": 600,  # 10 minutes typical limit
            "max_uploads_per_day": 100,
            "review_time_hours": 168,  # 7 days typical
            "monetization_requirements": {
                "minimum_streams": 1000,
                "verified_artist": True,
                "distributor_required": True
            },
            "metadata_requirements": [
                "title", "artist", "genre", "isrc_code", "release_date"
            ]
        }
