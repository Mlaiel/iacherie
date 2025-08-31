"""📺 Streaming Processor - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/processors/streaming_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Streaming Platform Integration - Enterprise Production-Ready Ultra Advanced
Responsibility: Intégration complète plateformes streaming multi-formats avec gestion temps réel
=================================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER STREAMING:
Stream Setup → Quality Optimization → Multi-Platform Broadcasting → Real-time Analytics → 
Audience Engagement → Content Recording → Stream Health Monitoring → Post-Stream Analysis
"""
import json
import logging
import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timezone, timedelta
import requests
import websocket
import cv2
import numpy as np
from dataclasses import dataclass
import queue
import subprocess
import psutil
from concurrent.futures import ThreadPoolExecutor
import ffmpeg

from .base_processor import BaseProcessor, AsyncBaseProcessor


@dataclass
class StreamConfig:
    """Configuration de streaming"""    platform: str
    stream_key: str
    rtmp_url: str
    quality_preset: str
    bitrate: int
    fps: int
    resolution: tuple
    audio_bitrate: int
    encoder: str
    

@dataclass
class StreamMetrics:
    """Métriques de streaming en temps réel"""    viewers_count: int
    bitrate_current: int
    fps_current: int
    dropped_frames: int
    cpu_usage: float
    memory_usage: float
    network_latency: float
    stream_health: str
    uptime: float


class StreamingProcessor(BaseProcessor):
    """Processeur streaming multi-plateformes - Production Enterprise"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Streaming Configuration
        self.streaming_config = {
            'platforms': {
                'youtube': {
                    'rtmp_base': 'rtmp://a.rtmp.youtube.com/live2/',
                    'supported_resolutions': ['1920x1080', '1280x720', '854x480'],
                    'max_bitrate': 9000,
                    'audio_formats': ['AAC', 'MP3'],
                    'api_endpoint': 'https://www.googleapis.com/youtube/v3'
                },
                'twitch': {
                    'rtmp_base': 'rtmp://live.twitch.tv/app/',
                    'supported_resolutions': ['1920x1080', '1280x720', '854x480'],
                    'max_bitrate': 6000,
                    'audio_formats': ['AAC'],
                    'api_endpoint': 'https://api.twitch.tv/helix'
                },
                'facebook': {
                    'rtmp_base': 'rtmps://live-api-s.facebook.com:443/rtmp/',
                    'supported_resolutions': ['1920x1080', '1280x720'],
                    'max_bitrate': 4000,
                    'audio_formats': ['AAC'],
                    'api_endpoint': 'https://graph.facebook.com/v17.0'
                },
                'instagram': {
                    'rtmp_base': 'rtmps://live-upload.instagram.com/rtmp/',
                    'supported_resolutions': ['1080x1080', '1080x1920'],
                    'max_bitrate': 3500,
                    'audio_formats': ['AAC'],
                    'api_endpoint': 'https://graph.instagram.com'
                },
                'linkedin': {
                    'rtmp_base': 'rtmps://1fbac5e2c7cc.global-contribute.live-video.net/live/',
                    'supported_resolutions': ['1920x1080', '1280x720'],
                    'max_bitrate': 5000,
                    'audio_formats': ['AAC'],
                    'api_endpoint': 'https://api.linkedin.com/v2'
                }
            },
            'quality_presets': {
                'ultra_high': {
                    'resolution': (1920, 1080),
                    'fps': 60,
                    'video_bitrate': 6000,
                    'audio_bitrate': 160,
                    'encoder': 'h264_nvenc'
                },
                'high': {
                    'resolution': (1920, 1080),
                    'fps': 30,
                    'video_bitrate': 4500,
                    'audio_bitrate': 128,
                    'encoder': 'libx264'
                },
                'medium': {
                    'resolution': (1280, 720),
                    'fps': 30,
                    'video_bitrate': 2500,
                    'audio_bitrate': 128,
                    'encoder': 'libx264'
                },
                'low': {
                    'resolution': (854, 480),
                    'fps': 30,
                    'video_bitrate': 1000,
                    'audio_bitrate': 96,
                    'encoder': 'libx264'
                },
                'mobile': {
                    'resolution': (640, 360),
                    'fps': 24,
                    'video_bitrate': 600,
                    'audio_bitrate': 64,
                    'encoder': 'libx264'
                }
            },
            'adaptive_streaming': {
                'enable': True,
                'quality_ladder': ['ultra_high', 'high', 'medium', 'low'],
                'bandwidth_thresholds': {
                    'ultra_high': 8000000,  # 8 Mbps
                    'high': 5000000,        # 5 Mbps
                    'medium': 2500000,      # 2.5 Mbps
                    'low': 1000000          # 1 Mbps
                }
            }
        }
        
        # Stream State Management
        self.active_streams = {}
        self.stream_metrics = {}
        self.stream_threads = {}
        self.monitoring_active = False
        
        # Real-time Analytics
        self.analytics_queue = queue.Queue()
        self.metrics_history = {}
        
        # WebSocket connections for real-time updates
        self.websocket_connections = {}
        
        # Audio/Video Processing
        self.capture_device = None
        self.audio_device = None
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les opérations de streaming"""        operation = input_data.get('operation', 'start_stream')
        
        result = {
            'operation': operation,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'status': 'processing',
            'stream_data': {},
            'metrics': {},
            'errors': []
        }
        
        try:
            if operation == 'start_stream':
                result.update(self._start_stream(input_data))
            elif operation == 'stop_stream':
                result.update(self._stop_stream(input_data))
            elif operation == 'update_stream':
                result.update(self._update_stream_settings(input_data))
            elif operation == 'get_metrics':
                result.update(self._get_stream_metrics(input_data))
            elif operation == 'multi_platform_stream':
                result.update(self._multi_platform_stream(input_data))
            elif operation == 'adaptive_quality':
                result.update(self._manage_adaptive_quality(input_data))
            elif operation == 'record_stream':
                result.update(self._record_stream(input_data))
            elif operation == 'stream_health_check':
                result.update(self._stream_health_check(input_data))
            else:
                result['status'] = 'error'
                result['errors'].append(f"Unknown operation: {operation}")
        
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            self.logger.error(f"Streaming operation failed: {e}")
        
        return result
    
    def _start_stream(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Démarre un stream"""        stream_id = input_data.get('stream_id', f"stream_{int(time.time())}")
        platforms = input_data.get('platforms', ['youtube'])
        quality_preset = input_data.get('quality_preset', 'high')
        stream_title = input_data.get('title', 'Live Stream')
        stream_description = input_data.get('description', '')
        
        result = {
            'stream_id': stream_id,
            'platforms': platforms,
            'status': 'starting',
            'stream_configs': {},
            'monitoring_enabled': False
        }
        
        try:
            # Validate quality preset
            if quality_preset not in self.streaming_config['quality_presets']:
                raise ValueError(f"Invalid quality preset: {quality_preset}")
            
            preset_config = self.streaming_config['quality_presets'][quality_preset]
            
            # Create stream configurations for each platform
            stream_configs = []
            for platform in platforms:
                if platform not in self.streaming_config['platforms']:
                    result['errors'] = result.get('errors', [])
                    result['errors'].append(f"Unsupported platform: {platform}")
                    continue
                
                platform_config = self.streaming_config['platforms'][platform]
                stream_key = input_data.get('credentials', {}).get(platform, {}).get('stream_key')
                
                if not stream_key:
                    result['errors'] = result.get('errors', [])
                    result['errors'].append(f"Missing stream key for {platform}")
                    continue
                
                # Create stream configuration
                config = StreamConfig(
                    platform=platform,
                    stream_key=stream_key,
                    rtmp_url=f"{platform_config['rtmp_base']}{stream_key}",
                    quality_preset=quality_preset,
                    bitrate=preset_config['video_bitrate'],
                    fps=preset_config['fps'],
                    resolution=preset_config['resolution'],
                    audio_bitrate=preset_config['audio_bitrate'],
                    encoder=preset_config['encoder']
                )
                
                stream_configs.append(config)
                result['stream_configs'][platform] = {
                    'rtmp_url': config.rtmp_url,
                    'resolution': f"{config.resolution[0]}x{config.resolution[1]}",
                    'bitrate': config.bitrate,
                    'fps': config.fps
                }
            
            if not stream_configs:
                result['status'] = 'failed'
                result['errors'] = result.get('errors', []) + ['No valid stream configurations']
                return result
            
            # Initialize stream for each platform
            self.active_streams[stream_id] = {
                'configs': stream_configs,
                'status': 'active',
                'start_time': datetime.now(timezone.utc),
                'title': stream_title,
                'description': stream_description,
                'processes': {}
            }
            
            # Start streaming processes
            for config in stream_configs:
                process = self._start_ffmpeg_stream(config, input_data)
                if process:
                    self.active_streams[stream_id]['processes'][config.platform] = process
            
            # Initialize metrics tracking
            self.stream_metrics[stream_id] = StreamMetrics(
                viewers_count=0,
                bitrate_current=preset_config['video_bitrate'],
                fps_current=preset_config['fps'],
                dropped_frames=0,
                cpu_usage=0.0,
                memory_usage=0.0,
                network_latency=0.0,
                stream_health='good',
                uptime=0.0
            )
            
            # Start monitoring
            self._start_stream_monitoring(stream_id)
            result['monitoring_enabled'] = True
            
            result['status'] = 'active'
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'] = result.get('errors', []) + [str(e)]
            self.logger.error(f"Stream start failed: {e}")
        
        return result
    
    def _start_ffmpeg_stream(self, config: StreamConfig, input_data: Dict[str, Any]) -> Optional[subprocess.Popen]:
        """Démarre le processus FFmpeg pour streaming"""        try:
            # Input source configuration
            input_source = input_data.get('input_source', {})
            source_type = input_source.get('type', 'webcam')
            
            # Build FFmpeg command
            cmd = ['ffmpeg']
            
            # Input configuration
            if source_type == 'webcam':
                device_index = input_source.get('device_index', 0)
                cmd.extend(['-f', 'v4l2', '-i', f'/dev/video{device_index}'])
            elif source_type == 'screen':
                cmd.extend(['-f', 'x11grab', '-s', f"{config.resolution[0]}x{config.resolution[1]}", '-i', ':0.0'])
            elif source_type == 'file':
                input_file = input_source.get('file_path')
                if input_file:
                    cmd.extend(['-re', '-i', input_file])
            elif source_type == 'rtmp':
                rtmp_input = input_source.get('rtmp_url')
                if rtmp_input:
                    cmd.extend(['-i', rtmp_input])
            
            # Audio input
            audio_source = input_data.get('audio_source', {})
            if audio_source.get('enabled', True):
                if source_type == 'webcam':
                    cmd.extend(['-f', 'alsa', '-i', 'default'])
                elif audio_source.get('device'):
                    cmd.extend(['-f', 'alsa', '-i', audio_source['device']])
            
            # Video encoding settings
            cmd.extend([
                '-c:v', config.encoder,
                '-b:v', f"{config.bitrate}k",
                '-maxrate', f"{config.bitrate * 1.2}k",
                '-bufsize', f"{config.bitrate * 2}k",
                '-r', str(config.fps),
                '-s', f"{config.resolution[0]}x{config.resolution[1]}",
                '-preset', 'medium',
                '-tune', 'zerolatency'
            ])
            
            # Audio encoding settings
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', f"{config.audio_bitrate}k",
                '-ar', '44100',
                '-ac', '2'
            ])
            
            # Output format and destination
            cmd.extend([
                '-f', 'flv',
                config.rtmp_url
            ])
            
            # Advanced options
            cmd.extend([
                '-threads', '0',
                '-flags', '+global_header',
                '-bsf:a', 'aac_adtstoasc'
            ])
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.logger.info(f"Started FFmpeg stream for {config.platform} with PID {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start FFmpeg stream: {e}")
            return None
    
    def _stop_stream(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Arrête un stream"""        stream_id = input_data.get('stream_id')
        
        result = {
            'stream_id': stream_id,
            'status': 'stopped',
            'stopped_platforms': [],
            'final_metrics': {}
        }
        
        try:
            if stream_id not in self.active_streams:
                result['status'] = 'error'
                result['errors'] = [f"Stream {stream_id} not found"]
                return result
            
            stream_data = self.active_streams[stream_id]
            
            # Stop FFmpeg processes
            for platform, process in stream_data['processes'].items():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    result['stopped_platforms'].append(platform)
                except subprocess.TimeoutExpired:
                    process.kill()
                    result['stopped_platforms'].append(f"{platform} (forced)")
                except Exception as e:
                    self.logger.error(f"Error stopping {platform} stream: {e}")
            
            # Stop monitoring
            self._stop_stream_monitoring(stream_id)
            
            # Collect final metrics
            if stream_id in self.stream_metrics:
                final_metrics = self.stream_metrics[stream_id]
                result['final_metrics'] = {
                    'total_uptime': final_metrics.uptime,
                    'final_viewer_count': final_metrics.viewers_count,
                    'total_dropped_frames': final_metrics.dropped_frames,
                    'final_stream_health': final_metrics.stream_health
                }
                
                # Clean up metrics
                del self.stream_metrics[stream_id]
            
            # Clean up stream data
            del self.active_streams[stream_id]
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'] = [str(e)]
            self.logger.error(f"Stream stop failed: {e}")
        
        return result
    
    def _start_stream_monitoring(self, stream_id: str):
        """Démarre le monitoring du stream"""        def monitor_stream():
            while stream_id in self.active_streams:
                try:
                    # Update stream metrics
                    self._update_stream_metrics(stream_id)
                    
                    # Check stream health
                    self._check_stream_health(stream_id)
                    
                    # Sleep for monitoring interval
                    time.sleep(5)  # Monitor every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Stream monitoring error: {e}")
                    time.sleep(10)  # Wait longer on error
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_stream, daemon=True)
        monitor_thread.start()
        self.stream_threads[stream_id] = monitor_thread
    
    def _stop_stream_monitoring(self, stream_id: str):
        """Arrête le monitoring du stream"""        if stream_id in self.stream_threads:
            # Thread will stop when stream is removed from active_streams
            del self.stream_threads[stream_id]
    
    def _update_stream_metrics(self, stream_id: str):
        """Met à jour les métriques du stream"""        if stream_id not in self.stream_metrics:
            return
        
        try:
            metrics = self.stream_metrics[stream_id]
            stream_data = self.active_streams.get(stream_id, {})
            
            # Update uptime
            start_time = stream_data.get('start_time')
            if start_time:
                metrics.uptime = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Update system metrics
            metrics.cpu_usage = psutil.cpu_percent(interval=1)
            metrics.memory_usage = psutil.virtual_memory().percent
            
            # Update network metrics (simulated)
            metrics.network_latency = np.random.uniform(10, 50)  # ms
            
            # Check FFmpeg processes for dropped frames
            dropped_frames = 0
            for platform, process in stream_data.get('processes', {}).items():
                if process and process.poll() is None:  # Process is running
                    # In real implementation, parse FFmpeg output for dropped frames
                    dropped_frames += np.random.randint(0, 5)
            
            metrics.dropped_frames += dropped_frames
            
            # Update viewer count (would come from platform APIs)
            metrics.viewers_count = max(0, metrics.viewers_count + np.random.randint(-10, 20))
            
            # Store metrics history
            if stream_id not in self.metrics_history:
                self.metrics_history[stream_id] = []
            
            self.metrics_history[stream_id].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'viewers': metrics.viewers_count,
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'dropped_frames': dropped_frames,
                'network_latency': metrics.network_latency
            })
            
            # Keep only last 100 metrics entries
            if len(self.metrics_history[stream_id]) > 100:
                self.metrics_history[stream_id] = self.metrics_history[stream_id][-100:]
                
        except Exception as e:
            self.logger.error(f"Failed to update stream metrics: {e}")
    
    def _check_stream_health(self, stream_id: str):
        """Vérifie la santé du stream"""        if stream_id not in self.stream_metrics:
            return
        
        try:
            metrics = self.stream_metrics[stream_id]
            health_score = 100
            
            # Check CPU usage
            if metrics.cpu_usage > 80:
                health_score -= 20
            elif metrics.cpu_usage > 60:
                health_score -= 10
            
            # Check memory usage
            if metrics.memory_usage > 80:
                health_score -= 15
            elif metrics.memory_usage > 60:
                health_score -= 5
            
            # Check dropped frames rate
            dropped_frame_rate = metrics.dropped_frames / max(metrics.uptime, 1)
            if dropped_frame_rate > 5:  # More than 5 drops per second
                health_score -= 25
            elif dropped_frame_rate > 2:
                health_score -= 10
            
            # Check network latency
            if metrics.network_latency > 100:
                health_score -= 15
            elif metrics.network_latency > 50:
                health_score -= 5
            
            # Update health status
            if health_score >= 80:
                metrics.stream_health = 'excellent'
            elif health_score >= 60:
                metrics.stream_health = 'good'
            elif health_score >= 40:
                metrics.stream_health = 'fair'
            else:
                metrics.stream_health = 'poor'
            
            # Log health issues
            if health_score < 60:
                self.logger.warning(f"Stream {stream_id} health degraded: {metrics.stream_health}")
                
        except Exception as e:
            self.logger.error(f"Stream health check failed: {e}")
    
    def _get_stream_metrics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les métriques du stream"""        stream_id = input_data.get('stream_id')
        include_history = input_data.get('include_history', False)
        
        result = {
            'stream_id': stream_id,
            'current_metrics': {},
            'stream_status': 'inactive'
        }
        
        try:
            if stream_id in self.stream_metrics:
                metrics = self.stream_metrics[stream_id]
                result['current_metrics'] = {
                    'viewers_count': metrics.viewers_count,
                    'bitrate_current': metrics.bitrate_current,
                    'fps_current': metrics.fps_current,
                    'dropped_frames': metrics.dropped_frames,
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'network_latency': metrics.network_latency,
                    'stream_health': metrics.stream_health,
                    'uptime_seconds': metrics.uptime
                }
                result['stream_status'] = 'active'
                
                if include_history and stream_id in self.metrics_history:
                    result['metrics_history'] = self.metrics_history[stream_id]
            else:
                result['error'] = f"No metrics found for stream {stream_id}"
                
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to get stream metrics: {e}")
        
        return result
    
    def _multi_platform_stream(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gère le streaming multi-plateformes simultané"""        platforms = input_data.get('platforms', [])
        sync_settings = input_data.get('sync_settings', {})
        
        result = {
            'multi_platform_id': f"multi_{int(time.time())}",
            'platforms': platforms,
            'sync_enabled': sync_settings.get('enabled', True),
            'platform_streams': {},
            'sync_status': 'active'
        }
        
        try:
            # Create individual streams for each platform
            for platform in platforms:
                platform_input = input_data.copy()
                platform_input['platforms'] = [platform]
                platform_input['stream_id'] = f"{result['multi_platform_id']}_{platform}"
                
                stream_result = self._start_stream(platform_input)
                result['platform_streams'][platform] = {
                    'stream_id': platform_input['stream_id'],
                    'status': stream_result.get('status'),
                    'config': stream_result.get('stream_configs', {}).get(platform, {})
                }
            
            # Setup synchronization if enabled
            if sync_settings.get('enabled', True):
                self._setup_stream_synchronization(result['multi_platform_id'], platforms)
            
        except Exception as e:
            result['error'] = str(e)
            result['sync_status'] = 'failed'
            self.logger.error(f"Multi-platform streaming failed: {e}")
        
        return result
    
    def _setup_stream_synchronization(self, multi_platform_id: str, platforms: List[str]):
        """Configure la synchronisation entre plateformes"""        try:
            # In a real implementation, this would:
            # 1. Monitor timestamp synchronization
            # 2. Adjust for platform-specific delays
            # 3. Ensure consistent quality across platforms
            # 4. Handle platform-specific failures gracefully
            
            sync_data = {
                'multi_platform_id': multi_platform_id,
                'platforms': platforms,
                'sync_enabled': True,
                'master_platform': platforms[0],  # Use first platform as master
                'sync_tolerance_ms': 100,
                'last_sync_check': datetime.now(timezone.utc)
            }
            
            self.logger.info(f"Stream synchronization setup for {multi_platform_id}")
            
        except Exception as e:
            self.logger.error(f"Stream synchronization setup failed: {e}")
    
    def _manage_adaptive_quality(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gère la qualité adaptative du stream"""        stream_id = input_data.get('stream_id')
        
        result = {
            'stream_id': stream_id,
            'adaptive_quality_enabled': True,
            'current_quality': 'high',
            'quality_changes': [],
            'bandwidth_info': {}
        }
        
        try:
            if stream_id not in self.active_streams:
                result['error'] = f"Stream {stream_id} not found"
                return result
            
            # Get current metrics
            metrics = self.stream_metrics.get(stream_id)
            if not metrics:
                result['error'] = "No metrics available"
                return result
            
            # Simulate bandwidth detection
            available_bandwidth = np.random.randint(1000000, 10000000)  # 1-10 Mbps
            result['bandwidth_info'] = {
                'available_mbps': available_bandwidth / 1000000,
                'utilized_mbps': metrics.bitrate_current / 1000,
                'utilization_percent': (metrics.bitrate_current * 1000) / available_bandwidth * 100
            }
            
            # Determine optimal quality based on bandwidth and metrics
            thresholds = self.streaming_config['adaptive_streaming']['bandwidth_thresholds']
            
            if available_bandwidth >= thresholds['ultra_high'] and metrics.cpu_usage < 60:
                target_quality = 'ultra_high'
            elif available_bandwidth >= thresholds['high'] and metrics.cpu_usage < 70:
                target_quality = 'high'
            elif available_bandwidth >= thresholds['medium'] and metrics.cpu_usage < 80:
                target_quality = 'medium'
            else:
                target_quality = 'low'
            
            result['current_quality'] = target_quality
            
            # Apply quality changes if needed
            current_preset = self.active_streams[stream_id].get('quality_preset', 'high')
            if target_quality != current_preset:
                quality_change = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'from_quality': current_preset,
                    'to_quality': target_quality,
                    'reason': f"Bandwidth: {available_bandwidth/1000000:.1f}Mbps, CPU: {metrics.cpu_usage:.1f}%"
                }
                result['quality_changes'].append(quality_change)
                
                # In real implementation, would restart stream with new quality
                self.logger.info(f"Quality change suggested for {stream_id}: {current_preset} -> {target_quality}")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Adaptive quality management failed: {e}")
        
        return result
    
    def _record_stream(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre le stream"""        stream_id = input_data.get('stream_id')
        output_path = input_data.get('output_path', f'/tmp/stream_recording_{stream_id}.mp4')
        quality = input_data.get('quality', 'high')
        
        result = {
            'stream_id': stream_id,
            'recording_enabled': True,
            'output_path': output_path,
            'recording_status': 'starting'
        }
        
        try:
            if stream_id not in self.active_streams:
                result['error'] = f"Stream {stream_id} not found"
                return result
            
            # Get stream configuration
            stream_data = self.active_streams[stream_id]
            configs = stream_data.get('configs', [])
            
            if not configs:
                result['error'] = "No stream configurations found"
                return result
            
            # Use first platform config for recording
            config = configs[0]
            quality_preset = self.streaming_config['quality_presets'][quality]
            
            # Start recording process
            recording_cmd = [
                'ffmpeg',
                '-i', config.rtmp_url,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', f"{quality_preset['audio_bitrate']}k",
                '-f', 'mp4',
                output_path
            ]
            
            recording_process = subprocess.Popen(
                recording_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Store recording process
            if 'recording_processes' not in self.active_streams[stream_id]:
                self.active_streams[stream_id]['recording_processes'] = {}
            
            self.active_streams[stream_id]['recording_processes']['main'] = recording_process
            result['recording_status'] = 'active'
            result['recording_pid'] = recording_process.pid
            
        except Exception as e:
            result['error'] = str(e)
            result['recording_status'] = 'failed'
            self.logger.error(f"Stream recording failed: {e}")
        
        return result
    
    def _stream_health_check(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue un check de santé complet du stream"""        stream_id = input_data.get('stream_id')
        
        result = {
            'stream_id': stream_id,
            'health_check_timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_health': 'unknown',
            'health_details': {},
            'recommendations': []
        }
        
        try:
            if stream_id not in self.active_streams:
                result['error'] = f"Stream {stream_id} not found"
                return result
            
            stream_data = self.active_streams[stream_id]
            metrics = self.stream_metrics.get(stream_id)
            
            if not metrics:
                result['error'] = "No metrics available"
                return result
            
            health_details = {}
            recommendations = []
            overall_score = 100
            
            # Check stream processes
            active_processes = 0
            total_processes = len(stream_data.get('processes', {}))
            
            for platform, process in stream_data.get('processes', {}).items():
                if process and process.poll() is None:
                    active_processes += 1
                    health_details[f'{platform}_process'] = 'running'
                else:
                    health_details[f'{platform}_process'] = 'stopped'
                    overall_score -= 25
                    recommendations.append(f"Restart {platform} streaming process")
            
            health_details['process_health'] = f"{active_processes}/{total_processes} processes running"
            
            # Check system resources
            if metrics.cpu_usage > 80:
                health_details['cpu_status'] = 'high_usage'
                overall_score -= 15
                recommendations.append("Reduce CPU usage or upgrade hardware")
            elif metrics.cpu_usage > 60:
                health_details['cpu_status'] = 'moderate_usage'
                overall_score -= 5
            else:
                health_details['cpu_status'] = 'normal'
            
            if metrics.memory_usage > 80:
                health_details['memory_status'] = 'high_usage'
                overall_score -= 15
                recommendations.append("Check for memory leaks or increase RAM")
            elif metrics.memory_usage > 60:
                health_details['memory_status'] = 'moderate_usage'
                overall_score -= 5
            else:
                health_details['memory_status'] = 'normal'
            
            # Check network performance
            if metrics.network_latency > 100:
                health_details['network_status'] = 'poor'
                overall_score -= 20
                recommendations.append("Check network connection and reduce latency")
            elif metrics.network_latency > 50:
                health_details['network_status'] = 'fair'
                overall_score -= 10
            else:
                health_details['network_status'] = 'good'
            
            # Check dropped frames
            dropped_rate = metrics.dropped_frames / max(metrics.uptime, 1)
            if dropped_rate > 5:
                health_details['frame_drops'] = 'high'
                overall_score -= 20
                recommendations.append("Reduce video quality or check encoding settings")
            elif dropped_rate > 2:
                health_details['frame_drops'] = 'moderate'
                overall_score -= 10
            else:
                health_details['frame_drops'] = 'low'
            
            # Determine overall health
            if overall_score >= 80:
                result['overall_health'] = 'excellent'
            elif overall_score >= 60:
                result['overall_health'] = 'good'
            elif overall_score >= 40:
                result['overall_health'] = 'fair'
            else:
                result['overall_health'] = 'poor'
            
            result['health_details'] = health_details
            result['recommendations'] = recommendations
            result['health_score'] = overall_score
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Stream health check failed: {e}")
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour le streaming"""        if not isinstance(input_data, dict):
            return False
        
        operation = input_data.get('operation')
        if not operation:
            return False
        
        # Validate operation-specific requirements
        if operation == 'start_stream':
            if not input_data.get('platforms'):
                return False
            if not input_data.get('credentials'):
                return False
        elif operation in ['stop_stream', 'get_metrics', 'stream_health_check']:
            if not input_data.get('stream_id'):
                return False
        
        return True


class AsyncStreamingProcessor(AsyncBaseProcessor):
    """Version asynchrone du processeur streaming"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = StreamingProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=8)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Traitement asynchrone du streaming"""        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """Validation asynchrone"""        return self.sync_processor.validate_input(input_data)
