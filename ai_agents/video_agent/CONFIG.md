# Video Agent Configuration

## Environment Variables

### Core Settings
```bash
# Video Processing Workers
VIDEO_PROCESSING_WORKERS=4

# File Size Limits
MAX_VIDEO_SIZE_GB=20
MAX_DURATION_HOURS=4

# Temporary Storage
TEMP_STORAGE_PATH=/tmp/video_processing
CLEANUP_INTERVAL_HOURS=24

# GPU Processing
ENABLE_GPU_ACCELERATION=true
CUDA_VISIBLE_DEVICES=0

# AI Model Settings
AI_MODEL_PATH=/models/video_processing
MODEL_CACHE_SIZE_GB=10
```

### Hardware Acceleration
```bash
# NVIDIA NVENC
ENABLE_NVENC=true

# Intel QuickSync
ENABLE_QSV=true

# VAAPI (Intel/AMD)
ENABLE_VAAPI=true

# Apple VideoToolbox (macOS)
ENABLE_VIDEOTOOLBOX=true

# AMD AMF
ENABLE_AMF=true
```

### Quality Settings
```bash
# Default Quality Profiles
DEFAULT_VIDEO_QUALITY=medium
DEFAULT_AUDIO_QUALITY=high

# Compression Settings
DEFAULT_CRF=23
DEFAULT_PRESET=medium

# Bitrate Settings
MIN_BITRATE_KBPS=500
MAX_BITRATE_MBPS=50
```

### Cloud Integration
```bash
# Cloud Storage
CLOUD_STORAGE_PROVIDER=aws_s3
CLOUD_STORAGE_BUCKET=video-processing-bucket
CLOUD_STORAGE_REGION=us-east-1

# CDN Settings
CDN_ENDPOINT=https://cdn.example.com
CDN_CACHE_CONTROL=max-age=31536000
```

### Security Settings
```bash
# Content Protection
ENABLE_WATERMARKING=true
WATERMARK_OPACITY=0.3
WATERMARK_POSITION=bottom_right

# DRM Settings
ENABLE_DRM=true
DRM_PROVIDER=widevine

# Encryption
ENABLE_CONTENT_ENCRYPTION=true
ENCRYPTION_KEY_ROTATION_DAYS=30
```

### API Configuration
```bash
# API Limits
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT_SECONDS=3600
MAX_RETRY_ATTEMPTS=3

# Rate Limiting
REQUESTS_PER_MINUTE=100
BURST_LIMIT=10

# Authentication
API_KEY_REQUIRED=true
JWT_SECRET_KEY=your-secret-key
```

### Monitoring & Analytics
```bash
# Metrics Collection
ENABLE_METRICS=true
METRICS_ENDPOINT=/metrics
PROMETHEUS_PORT=8090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30

# Health Checks
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
```

### Database Configuration
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/video_agent
DATABASE_POOL_SIZE=20
DATABASE_TIMEOUT=30

# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
CACHE_TTL_SECONDS=3600
```

## Configuration Examples

### Development Configuration
```python
config = {
    "max_workers": 2,
    "max_file_size": 5 * 1024 * 1024 * 1024,  # 5GB
    "max_duration": 3600,  # 1 hour
    "gpu_acceleration": False,
    "temp_dir": "/tmp/video_dev",
    "quality_profiles": {
        "draft": {"crf": 28, "preset": "fast"},
        "preview": {"crf": 23, "preset": "medium"}
    }
}
```

### Production Configuration
```python
config = {
    "max_workers": 8,
    "max_file_size": 20 * 1024 * 1024 * 1024,  # 20GB
    "max_duration": 14400,  # 4 hours
    "gpu_acceleration": True,
    "hardware_encoders": {
        "nvenc": True,
        "qsv": True,
        "vaapi": True
    },
    "temp_dir": "/var/tmp/video_processing",
    "cleanup_interval": 3600,  # 1 hour
    "quality_profiles": {
        "draft": {"crf": 32, "preset": "ultrafast"},
        "fast": {"crf": 28, "preset": "fast"},
        "balanced": {"crf": 23, "preset": "medium"},
        "quality": {"crf": 18, "preset": "slow"},
        "archival": {"crf": 15, "preset": "veryslow"}
    },
    "monitoring": {
        "enable_metrics": True,
        "prometheus_port": 8090,
        "health_checks": True
    },
    "security": {
        "enable_watermarking": True,
        "enable_drm": True,
        "content_encryption": True
    }
}
```

### Cloud Configuration
```python
config = {
    "cloud_storage": {
        "provider": "aws_s3",
        "bucket": "video-processing-prod",
        "region": "us-east-1",
        "cdn_endpoint": "https://d123456789.cloudfront.net"
    },
    "scaling": {
        "auto_scaling": True,
        "min_workers": 2,
        "max_workers": 20,
        "scale_up_threshold": 0.8,
        "scale_down_threshold": 0.2
    },
    "distributed": {
        "enable_cluster": True,
        "cluster_nodes": [
            "worker1.example.com",
            "worker2.example.com",
            "worker3.example.com"
        ],
        "load_balancer": "round_robin"
    }
}
```

## Performance Tuning

### CPU Optimization
```python
# Optimize for CPU-bound tasks
config = {
    "cpu_optimization": {
        "thread_count": "auto",  # Detect available cores
        "affinity": True,
        "nice_level": -5,
        "scheduler": "batch"
    },
    "encoding_presets": {
        "cpu_optimized": {
            "preset": "medium",
            "threads": 0,  # Auto-detect
            "slices": 4,
            "frame_threads": 2
        }
    }
}
```

### GPU Optimization
```python
# Optimize for GPU acceleration
config = {
    "gpu_optimization": {
        "cuda_devices": [0, 1],
        "memory_fraction": 0.8,
        "batch_size": 8,
        "mixed_precision": True
    },
    "encoding_presets": {
        "gpu_optimized": {
            "encoder": "h264_nvenc",
            "preset": "p7",  # Highest quality
            "rc": "vbr",
            "cq": 19
        }
    }
}
```

### Memory Optimization
```python
# Optimize memory usage
config = {
    "memory_optimization": {
        "max_memory_gb": 16,
        "stream_processing": True,
        "chunk_size_mb": 100,
        "buffer_size": 8192,
        "memory_mapping": True
    },
    "cleanup": {
        "aggressive_cleanup": True,
        "temp_file_cleanup": True,
        "memory_cleanup_interval": 300
    }
}
```

## Format-Specific Settings

### Social Media Optimization
```python
social_media_config = {
    "formats": {
        "instagram": {
            "max_resolution": "1080x1080",
            "max_duration": 60,
            "aspect_ratios": ["1:1", "4:5", "9:16"],
            "bitrate": "3500k"
        },
        "tiktok": {
            "max_resolution": "1080x1920",
            "max_duration": 180,
            "aspect_ratio": "9:16",
            "bitrate": "2500k"
        },
        "youtube": {
            "max_resolution": "3840x2160",
            "max_duration": 43200,  # 12 hours
            "aspect_ratios": ["16:9", "4:3"],
            "bitrate": "40000k"
        }
    }
}
```

### Streaming Optimization
```python
streaming_config = {
    "adaptive_streaming": {
        "hls": {
            "segment_duration": 6,
            "playlist_type": "vod",
            "encryption": True,
            "resolutions": ["240p", "360p", "480p", "720p", "1080p"]
        },
        "dash": {
            "segment_duration": 4,
            "encryption": True,
            "resolutions": ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        }
    },
    "encoding_ladder": {
        "240p": {"bitrate": "400k", "audio": "64k"},
        "360p": {"bitrate": "800k", "audio": "96k"},
        "480p": {"bitrate": "1200k", "audio": "128k"},
        "720p": {"bitrate": "2500k", "audio": "128k"},
        "1080p": {"bitrate": "5000k", "audio": "192k"},
        "1440p": {"bitrate": "10000k", "audio": "256k"},
        "2160p": {"bitrate": "20000k", "audio": "320k"}
    }
}
```
