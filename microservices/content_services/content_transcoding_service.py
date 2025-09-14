"""
Content Transcoding Service for Ainflue Microservices
Multi-format video/audio transcoding and optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
import aiofiles
import time

logger = logging.getLogger(__name__)


@dataclass
class TranscodingProfile:
    """Transcoding profile definition"""
    name: str
    container: str  # mp4, webm, mov, etc.
    video_codec: str  # h264, h265, vp9, av1, etc.
    audio_codec: str  # aac, opus, mp3, etc.
    resolution: str  # 1920x1080, 1280x720, etc.
    bitrate: str  # 2M, 1M, 500k, etc.
    framerate: int = 30
    audio_bitrate: str = "128k"
    quality: str = "medium"  # low, medium, high, ultra
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow


@dataclass
class TranscodingJob:
    """Transcoding job definition"""
    job_id: str
    input_file: str
    output_file: str
    profile: TranscodingProfile
    priority: int = 5  # 1-10, higher is more priority
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class MediaInfo:
    """Media file information"""
    duration: float
    width: int
    height: int
    fps: float
    video_codec: str
    audio_codec: str
    bitrate: int
    file_size: int
    format: str


class ContentTranscodingService:
    """Enterprise content transcoding service"""

    def __init__(self):
        self.transcoding_jobs = {}
        self.processing_queue = asyncio.Queue()
        self.completed_jobs = {}
        self.profiles = {}
        self.worker_count = int(os.getenv("TRANSCODING_WORKERS", "2"))
        self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_TRANSCODE", "4"))
        self.output_directory = os.getenv("TRANSCODE_OUTPUT_DIR", "/tmp/transcoded")
        self.temp_directory = os.getenv("TRANSCODE_TEMP_DIR", "/tmp/transcoding")
        
        # Initialize directories
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.temp_directory, exist_ok=True)
        
        # Initialize standard profiles
        self._initialize_standard_profiles()
        
        # Start workers
        for i in range(self.worker_count):
            asyncio.create_task(self._transcoding_worker(f"worker-{i}"))

    def _initialize_standard_profiles(self):
        """Initialize standard transcoding profiles"""
        profiles = [
            # Video profiles
            TranscodingProfile(
                name="4k_h264",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="3840x2160",
                bitrate="8M",
                framerate=30,
                quality="high",
                preset="medium"
            ),
            TranscodingProfile(
                name="1080p_h264",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1920x1080",
                bitrate="2M",
                framerate=30,
                quality="medium",
                preset="medium"
            ),
            TranscodingProfile(
                name="720p_h264",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1280x720",
                bitrate="1M",
                framerate=30,
                quality="medium",
                preset="fast"
            ),
            TranscodingProfile(
                name="480p_h264",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="854x480",
                bitrate="500k",
                framerate=30,
                quality="low",
                preset="fast"
            ),
            # Web optimized profiles
            TranscodingProfile(
                name="web_1080p",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1920x1080",
                bitrate="1.5M",
                framerate=30,
                quality="medium",
                preset="medium"
            ),
            TranscodingProfile(
                name="web_720p",
                container="webm",
                video_codec="libvpx-vp9",
                audio_codec="libopus",
                resolution="1280x720",
                bitrate="800k",
                framerate=30,
                quality="medium",
                preset="medium"
            ),
            # Audio profiles
            TranscodingProfile(
                name="audio_mp3_320",
                container="mp3",
                video_codec="",
                audio_codec="mp3",
                resolution="",
                bitrate="",
                audio_bitrate="320k",
                quality="high"
            ),
            TranscodingProfile(
                name="audio_aac_256",
                container="m4a",
                video_codec="",
                audio_codec="aac",
                resolution="",
                bitrate="",
                audio_bitrate="256k",
                quality="high"
            ),
            # Social media profiles
            TranscodingProfile(
                name="instagram_square",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1080x1080",
                bitrate="1M",
                framerate=30,
                quality="medium",
                preset="fast"
            ),
            TranscodingProfile(
                name="tiktok_vertical",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1080x1920",
                bitrate="1.5M",
                framerate=30,
                quality="medium",
                preset="fast"
            ),
            TranscodingProfile(
                name="youtube_1080p",
                container="mp4",
                video_codec="libx264",
                audio_codec="aac",
                resolution="1920x1080",
                bitrate="2.5M",
                framerate=30,
                quality="high",
                preset="medium"
            )
        ]
        
        for profile in profiles:
            self.profiles[profile.name] = profile

    async def submit_transcoding_job(
        self, 
        input_file: str, 
        profile_name: str,
        output_filename: Optional[str] = None,
        priority: int = 5
    ) -> str:
        """Submit transcoding job"""
        try:
            if profile_name not in self.profiles:
                raise ValueError(f"Profile not found: {profile_name}")
            
            profile = self.profiles[profile_name]
            
            # Generate job ID
            job_id = f"transcode_{int(time.time())}_{hash(input_file) % 10000}"
            
            # Generate output filename
            if not output_filename:
                base_name = Path(input_file).stem
                output_filename = f"{base_name}_{profile_name}.{profile.container}"
            
            output_file = os.path.join(self.output_directory, output_filename)
            
            # Create job
            job = TranscodingJob(
                job_id=job_id,
                input_file=input_file,
                output_file=output_file,
                profile=profile,
                priority=priority,
                metadata={}
            )
            
            # Validate input file exists
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            # Get media info
            media_info = await self._get_media_info(input_file)
            job.metadata["input_info"] = media_info.__dict__ if media_info else {}
            
            # Store job
            self.transcoding_jobs[job_id] = job
            
            # Add to queue
            await self.processing_queue.put(job)
            
            logger.info(f"Submitted transcoding job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to submit transcoding job: {str(e)}")
            raise

    async def _transcoding_worker(self, worker_id: str):
        """Transcoding worker process"""
        logger.info(f"Transcoding worker {worker_id} started")
        
        while True:
            try:
                # Get job from queue
                job = await self.processing_queue.get()
                
                logger.info(f"Worker {worker_id} processing job: {job.job_id}")
                
                # Update job status
                job.status = "processing"
                job.started_at = datetime.utcnow()
                
                # Process the job
                success = await self._process_transcoding_job(job, worker_id)
                
                if success:
                    job.status = "completed"
                    job.progress = 100.0
                    logger.info(f"Worker {worker_id} completed job: {job.job_id}")
                else:
                    job.status = "failed"
                    logger.error(f"Worker {worker_id} failed job: {job.job_id}")
                
                job.completed_at = datetime.utcnow()
                
                # Move to completed jobs
                self.completed_jobs[job.job_id] = job
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Transcoding worker {worker_id} error: {str(e)}")
                await asyncio.sleep(5)  # Brief pause before retrying

    async def _process_transcoding_job(self, job: TranscodingJob, worker_id: str) -> bool:
        """Process individual transcoding job"""
        try:
            profile = job.profile
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-y", "-i", job.input_file]
            
            # Video codec settings
            if profile.video_codec:
                cmd.extend(["-c:v", profile.video_codec])
                
                if profile.resolution:
                    cmd.extend(["-s", profile.resolution])
                
                if profile.bitrate:
                    cmd.extend(["-b:v", profile.bitrate])
                
                if profile.framerate:
                    cmd.extend(["-r", str(profile.framerate)])
                
                # Codec-specific settings
                if profile.video_codec == "libx264":
                    cmd.extend(["-preset", profile.preset])
                    if profile.quality == "high":
                        cmd.extend(["-crf", "18"])
                    elif profile.quality == "medium":
                        cmd.extend(["-crf", "23"])
                    else:
                        cmd.extend(["-crf", "28"])
                
                elif profile.video_codec == "libx265":
                    cmd.extend(["-preset", profile.preset])
                    cmd.extend(["-crf", "28"])
                
                elif profile.video_codec == "libvpx-vp9":
                    cmd.extend(["-deadline", "good"])
                    cmd.extend(["-cpu-used", "1"])
            else:
                # Audio only
                cmd.extend(["-vn"])
            
            # Audio codec settings
            if profile.audio_codec:
                cmd.extend(["-c:a", profile.audio_codec])
                cmd.extend(["-b:a", profile.audio_bitrate])
            
            # Output file
            cmd.append(job.output_file)
            
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Execute FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress (simplified - in production would parse FFmpeg output)
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Verify output file exists
                if os.path.exists(job.output_file):
                    # Get output media info
                    output_info = await self._get_media_info(job.output_file)
                    job.metadata["output_info"] = output_info.__dict__ if output_info else {}
                    
                    return True
                else:
                    job.error_message = "Output file not created"
                    return False
            else:
                job.error_message = stderr.decode() if stderr else "FFmpeg failed"
                return False
                
        except Exception as e:
            job.error_message = str(e)
            logger.error(f"Transcoding job {job.job_id} failed: {str(e)}")
            return False

    async def _get_media_info(self, file_path: str) -> Optional[MediaInfo]:
        """Get media file information using ffprobe"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                
                # Find video and audio streams
                video_stream = None
                audio_stream = None
                
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "video" and not video_stream:
                        video_stream = stream
                    elif stream.get("codec_type") == "audio" and not audio_stream:
                        audio_stream = stream
                
                # Extract information
                format_info = data.get("format", {})
                
                media_info = MediaInfo(
                    duration=float(format_info.get("duration", 0)),
                    width=int(video_stream.get("width", 0)) if video_stream else 0,
                    height=int(video_stream.get("height", 0)) if video_stream else 0,
                    fps=float(eval(video_stream.get("r_frame_rate", "0/1"))) if video_stream else 0,
                    video_codec=video_stream.get("codec_name", "") if video_stream else "",
                    audio_codec=audio_stream.get("codec_name", "") if audio_stream else "",
                    bitrate=int(format_info.get("bit_rate", 0)),
                    file_size=int(format_info.get("size", 0)),
                    format=format_info.get("format_name", "")
                )
                
                return media_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get media info for {file_path}: {str(e)}")
            return None

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        try:
            # Check active jobs
            if job_id in self.transcoding_jobs:
                job = self.transcoding_jobs[job_id]
                return {
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress,
                    "input_file": job.input_file,
                    "output_file": job.output_file,
                    "profile": job.profile.name,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "metadata": job.metadata
                }
            
            # Check completed jobs
            if job_id in self.completed_jobs:
                job = self.completed_jobs[job_id]
                return {
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress,
                    "input_file": job.input_file,
                    "output_file": job.output_file,
                    "profile": job.profile.name,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "metadata": job.metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return None

    async def get_available_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get available transcoding profiles"""
        return {
            name: {
                "name": profile.name,
                "container": profile.container,
                "video_codec": profile.video_codec,
                "audio_codec": profile.audio_codec,
                "resolution": profile.resolution,
                "bitrate": profile.bitrate,
                "framerate": profile.framerate,
                "audio_bitrate": profile.audio_bitrate,
                "quality": profile.quality,
                "preset": profile.preset
            }
            for name, profile in self.profiles.items()
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel transcoding job"""
        try:
            if job_id in self.transcoding_jobs:
                job = self.transcoding_jobs[job_id]
                
                if job.status == "pending":
                    job.status = "cancelled"
                    job.error_message = "Job cancelled by user"
                    self.completed_jobs[job_id] = job
                    del self.transcoding_jobs[job_id]
                    return True
                elif job.status == "processing":
                    # In production, would send signal to worker to stop
                    job.status = "cancelled"
                    job.error_message = "Job cancelled by user"
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            return False

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get transcoding queue status"""
        try:
            active_jobs = len([job for job in self.transcoding_jobs.values() if job.status == "processing"])
            pending_jobs = len([job for job in self.transcoding_jobs.values() if job.status == "pending"])
            
            return {
                "active_jobs": active_jobs,
                "pending_jobs": pending_jobs,
                "queue_size": self.processing_queue.qsize(),
                "completed_jobs": len(self.completed_jobs),
                "worker_count": self.worker_count,
                "max_concurrent_jobs": self.max_concurrent_jobs,
                "available_profiles": len(self.profiles),
                "output_directory": self.output_directory,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Transcoding service health check"""
        try:
            # Check if FFmpeg is available
            ffmpeg_available = True
            try:
                process = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                ffmpeg_available = process.returncode == 0
            except:
                ffmpeg_available = False
            
            queue_status = await self.get_queue_status()
            
            return {
                "status": "healthy" if ffmpeg_available else "unhealthy",
                "ffmpeg_available": ffmpeg_available,
                "worker_count": self.worker_count,
                "active_jobs": queue_status.get("active_jobs", 0),
                "pending_jobs": queue_status.get("pending_jobs", 0),
                "completed_jobs": queue_status.get("completed_jobs", 0),
                "available_profiles": len(self.profiles),
                "output_directory": self.output_directory,
                "temp_directory": self.temp_directory,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transcoding service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global transcoding service instance
transcoding_service = ContentTranscodingService()


async def submit_transcoding_job(input_file: str, profile_name: str, priority: int = 5) -> str:
    """Submit transcoding job"""
    return await transcoding_service.submit_transcoding_job(input_file, profile_name, priority=priority)


async def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status"""
    return await transcoding_service.get_job_status(job_id)


if __name__ == "__main__":
    async def test_transcoding_service():
        """Test transcoding service"""
        print("Testing Content Transcoding Service...")
        
        # Get available profiles
        profiles = await transcoding_service.get_available_profiles()
        print(f"Available profiles: {list(profiles.keys())}")
        
        # Get queue status
        queue_status = await transcoding_service.get_queue_status()
        print(f"Queue status: {queue_status}")
        
        # Health check
        health = await transcoding_service.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_transcoding_service())