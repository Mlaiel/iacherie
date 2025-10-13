"""
Celery Worker for Asynchronous Media Processing
Handles video transcoding, image optimization, and other heavy tasks
"""

from celery import Celery, Task
import os
from typing import Dict
import subprocess
import json

# Initialize Celery
celery_app = Celery(
    'media_worker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)


@celery_app.task(bind=True, name='process_video_transcode')
def process_video_transcode(
    self: Task,
    media_id: str,
    input_path: str,
    output_path: str,
    quality: str,
    params: Dict
) -> Dict:
    """
    Transcode video to specific quality using FFmpeg
    
    Args:
        media_id: Media ID
        input_path: Path to input video file
        output_path: Path for output video file
        quality: Quality level (low, medium, high, hd)
        params: Transcoding parameters (width, bitrate)
    
    Returns:
        Dict with transcoding results
    """
    try:
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Starting transcode', 'progress': 0}
        )
        
        # FFmpeg command for transcoding
        # Example: ffmpeg -i input.mp4 -vf scale=1280:-1 -c:v libx264 -b:v 2500k -c:a aac output.mp4
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f"scale={params['width']}:-1",  # Scale width, keep aspect ratio
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'medium',  # Encoding speed/quality tradeoff
            '-b:v', params['bitrate'],  # Video bitrate
            '-c:a', 'aac',  # Audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Enable streaming
            '-y',  # Overwrite output
            output_path
        ]
        
        # Run FFmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr}")
        
        # Get output file size
        output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            'status': 'completed',
            'media_id': media_id,
            'quality': quality,
            'output_path': output_path,
            'output_size': output_size,
            'params': params
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'status': 'Failed', 'error': str(e)}
        )
        raise


@celery_app.task(bind=True, name='generate_video_thumbnail')
def generate_video_thumbnail(
    self: Task,
    media_id: str,
    input_path: str,
    output_path: str,
    timestamp: str = "00:00:01"
) -> Dict:
    """
    Generate thumbnail from video at specific timestamp
    
    Args:
        media_id: Media ID
        input_path: Path to input video
        output_path: Path for thumbnail output
        timestamp: Timestamp to extract (HH:MM:SS format)
    
    Returns:
        Dict with thumbnail generation results
    """
    try:
        # FFmpeg command to extract frame
        # ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 -q:v 2 thumbnail.jpg
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ss', timestamp,
            '-vframes', '1',
            '-q:v', '2',  # JPEG quality (1-31, lower is better)
            '-y',
            output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg thumbnail error: {stderr}")
        
        output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            'status': 'completed',
            'media_id': media_id,
            'output_path': output_path,
            'output_size': output_size
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'status': 'Failed', 'error': str(e)}
        )
        raise


@celery_app.task(bind=True, name='extract_video_metadata')
def extract_video_metadata(
    self: Task,
    input_path: str
) -> Dict:
    """
    Extract video metadata using FFprobe
    
    Args:
        input_path: Path to video file
    
    Returns:
        Dict with video metadata
    """
    try:
        # FFprobe command
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            input_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        metadata = json.loads(result.stdout)
        
        # Extract useful information
        video_stream = next(
            (s for s in metadata.get('streams', []) if s['codec_type'] == 'video'),
            None
        )
        
        audio_stream = next(
            (s for s in metadata.get('streams', []) if s['codec_type'] == 'audio'),
            None
        )
        
        format_info = metadata.get('format', {})
        
        return {
            'duration': float(format_info.get('duration', 0)),
            'size': int(format_info.get('size', 0)),
            'bitrate': int(format_info.get('bit_rate', 0)),
            'format': format_info.get('format_name', 'unknown'),
            'video': {
                'codec': video_stream.get('codec_name', 'unknown') if video_stream else None,
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0
            } if video_stream else None,
            'audio': {
                'codec': audio_stream.get('codec_name', 'unknown') if audio_stream else None,
                'sample_rate': audio_stream.get('sample_rate', 0) if audio_stream else 0,
                'channels': audio_stream.get('channels', 0) if audio_stream else 0
            } if audio_stream else None
        }
        
    except Exception as e:
        return {'error': str(e)}


@celery_app.task(bind=True, name='process_complete_video')
def process_complete_video(
    self: Task,
    media_id: str,
    input_path: str,
    base_output_dir: str
) -> Dict:
    """
    Complete video processing: extract metadata, generate thumbnail, transcode to multiple qualities
    
    This is a composite task that chains multiple subtasks
    """
    results = {
        'media_id': media_id,
        'status': 'processing',
        'tasks': {}
    }
    
    try:
        # Step 1: Extract metadata
        self.update_state(state='PROCESSING', meta={'step': 'metadata', 'progress': 10})
        metadata = extract_video_metadata(input_path)
        results['metadata'] = metadata
        
        # Step 2: Generate thumbnail
        self.update_state(state='PROCESSING', meta={'step': 'thumbnail', 'progress': 20})
        thumbnail_path = os.path.join(base_output_dir, 'thumbnail.jpg')
        thumbnail_result = generate_video_thumbnail(media_id, input_path, thumbnail_path)
        results['thumbnail'] = thumbnail_result
        
        # Step 3: Transcode to multiple qualities
        qualities = {
            'low': {'width': 640, 'bitrate': '500k'},
            'medium': {'width': 854, 'bitrate': '1000k'},
            'high': {'width': 1280, 'bitrate': '2500k'}
        }
        
        transcoding_results = {}
        progress_per_quality = 60 / len(qualities)  # Remaining 60% divided by qualities
        
        for i, (quality, params) in enumerate(qualities.items()):
            self.update_state(
                state='PROCESSING',
                meta={'step': f'transcode_{quality}', 'progress': 30 + (i * progress_per_quality)}
            )
            
            output_path = os.path.join(base_output_dir, f'{quality}.mp4')
            transcode_result = process_video_transcode(
                media_id, input_path, output_path, quality, params
            )
            transcoding_results[quality] = transcode_result
        
        results['transcoding'] = transcoding_results
        results['status'] = 'completed'
        results['progress'] = 100
        
        return results
        
    except Exception as e:
        results['status'] = 'failed'
        results['error'] = str(e)
        raise


@celery_app.task(name='cleanup_temp_files')
def cleanup_temp_files(file_paths: list):
    """
    Clean up temporary files after processing
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Failed to delete {path}: {e}")


# Task routes
celery_app.conf.task_routes = {
    'process_video_transcode': {'queue': 'video'},
    'generate_video_thumbnail': {'queue': 'video'},
    'extract_video_metadata': {'queue': 'video'},
    'process_complete_video': {'queue': 'video'},
    'cleanup_temp_files': {'queue': 'default'}
}

if __name__ == '__main__':
    celery_app.start()
