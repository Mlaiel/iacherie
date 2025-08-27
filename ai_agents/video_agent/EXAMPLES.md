# Video Agent Usage Examples

## Quick Start

### Basic Video Analysis
```python
from video_agent import VideoAgentIndex

# Initialize video agent
video_agent = VideoAgentIndex()

# Analyze video content
result = await video_agent.analyze_video(
    video_path="/path/to/video.mp4",
    analysis_types=["scenes", "quality", "motion", "color"]
)

print(f"Video duration: {result['video_properties']['duration']} seconds")
print(f"Quality score: {result['quality_analysis']['overall_quality_score']}")
print(f"Number of scenes: {result['scene_analysis']['total_scenes']}")
```

### Video Format Conversion
```python
# Convert video to different format
result = await video_agent.convert_video(
    input_path="/path/to/input.avi",
    output_format="mp4",
    preset="social_media"
)

print(f"Conversion successful: {result['success']}")
print(f"Output file: {result['output_path']}")
print(f"Size reduction: {result['size_reduction_percent']:.1f}%")
```

### Video Enhancement
```python
# Enhance video quality
result = await video_agent.enhance_video(
    input_path="/path/to/low_quality.mp4",
    enhancements=["upscale", "denoise", "sharpen", "color_correct"],
    quality_level="high"
)

print(f"Enhancement completed: {result['success']}")
print(f"Processing time: {result['processing_time']:.2f} seconds")
print(f"Quality improvements: {result['quality_metrics']}")
```

## Advanced Usage

### AI Video Generation
```python
# Generate video from text description
result = await video_agent.generate_video(
    generation_type="text_to_video",
    prompt="A peaceful sunset over mountain lake with birds flying",
    duration=15.0,
    style="cinematic",
    fps=30,
    quality="high"
)

print(f"Video generated: {result['output_path']}")
print(f"Total frames: {result['total_frames']}")
```

### Batch Processing
```python
# Process multiple videos in batch
jobs = [
    {
        "request_type": "convert",
        "input_path": "/videos/video1.avi",
        "output_format": "mp4",
        "preset": "streaming_hd"
    },
    {
        "request_type": "enhance", 
        "input_path": "/videos/video2.mov",
        "enhancements": ["stabilize", "denoise"],
        "quality_level": "medium"
    },
    {
        "request_type": "compress",
        "input_path": "/videos/video3.mkv",
        "target_size_mb": 100
    }
]

results = await video_agent.batch_process(jobs)

for i, result in enumerate(results):
    print(f"Job {i+1}: {'Success' if result['success'] else 'Failed'}")
```

### Adaptive Streaming Creation
```python
# Create HLS adaptive streaming
result = await video_agent.create_adaptive_stream(
    input_path="/path/to/source.mp4",
    output_dir="/streaming/output",
    resolutions=["360p", "720p", "1080p"],
    format_type="hls"
)

print(f"Master playlist: {result['master_playlist']}")
print(f"Stream variants: {result['stream_variants']}")
```

## Professional Workflows

### Content Creator Pipeline
```python
class ContentCreatorPipeline:
    def __init__(self):
        self.video_agent = VideoAgentIndex({
            "max_workers": 4,
            "gpu_acceleration": True,
            "quality_profiles": {
                "youtube": {"crf": 18, "preset": "slow"},
                "instagram": {"crf": 23, "preset": "medium"},
                "tiktok": {"crf": 25, "preset": "fast"}
            }
        })
    
    async def process_raw_footage(self, raw_video_path: str) -> Dict[str, Any]:
        """Process raw footage through complete pipeline"""
        
        # Step 1: Analyze raw footage
        analysis = await self.video_agent.analyze_video(
            video_path=raw_video_path,
            analysis_types=["quality", "scenes", "motion", "audio"]
        )
        
        # Step 2: Enhance if needed
        enhancements = []
        if analysis['quality_analysis']['overall_quality_score'] < 70:
            enhancements.extend(["denoise", "sharpen"])
        if analysis['quality_analysis']['average_sharpness'] < 50:
            enhancements.append("upscale")
        if analysis['motion_analysis']['overall_motion'] > 5.0:
            enhancements.append("stabilize")
        
        if enhancements:
            enhanced_result = await self.video_agent.enhance_video(
                input_path=raw_video_path,
                enhancements=enhancements,
                quality_level="high"
            )
            processed_path = enhanced_result['output_path']
        else:
            processed_path = raw_video_path
        
        # Step 3: Create platform-specific versions
        platforms = {
            "youtube": {"format": "mp4", "preset": "youtube"},
            "instagram": {"format": "mp4", "preset": "instagram"},
            "tiktok": {"format": "mp4", "preset": "tiktok"}
        }
        
        platform_versions = {}
        
        for platform, config in platforms.items():
            result = await self.video_agent.convert_video(
                input_path=processed_path,
                output_format=config["format"],
                preset=config["preset"]
            )
            platform_versions[platform] = result['output_path']
        
        return {
            "analysis": analysis,
            "enhancements_applied": enhancements,
            "platform_versions": platform_versions
        }

# Usage
pipeline = ContentCreatorPipeline()
result = await pipeline.process_raw_footage("/raw_footage/video.mov")
```

### Production House Workflow
```python
class ProductionHouseWorkflow:
    def __init__(self):
        self.video_agent = VideoAgentIndex({
            "max_workers": 8,
            "gpu_acceleration": True,
            "cloud_storage": {
                "provider": "aws_s3",
                "bucket": "production-videos"
            }
        })
    
    async def master_delivery_workflow(self, source_path: str) -> Dict[str, Any]:
        """Create master delivery formats"""
        
        deliverables = {}
        
        # Archive master (highest quality)
        archive_result = await self.video_agent.convert_video(
            input_path=source_path,
            output_format="mov",
            preset="archive",
            custom_settings={
                "video_codec": "prores",
                "quality": "archival"
            }
        )
        deliverables["archive_master"] = archive_result['output_path']
        
        # Broadcast master
        broadcast_result = await self.video_agent.convert_video(
            input_path=source_path,
            output_format="mxf",
            custom_settings={
                "video_codec": "dnxhd",
                "resolution": "1920x1080",
                "fps": 25
            }
        )
        deliverables["broadcast_master"] = broadcast_result['output_path']
        
        # Web delivery
        web_result = await self.video_agent.convert_video(
            input_path=source_path,
            output_format="mp4",
            preset="web_optimized"
        )
        deliverables["web_delivery"] = web_result['output_path']
        
        # Mobile version
        mobile_result = await self.video_agent.convert_video(
            input_path=source_path,
            output_format="mp4",
            preset="mobile"
        )
        deliverables["mobile_version"] = mobile_result['output_path']
        
        # Create streaming versions
        streaming_result = await self.video_agent.create_adaptive_stream(
            input_path=source_path,
            output_dir="/streaming/masters",
            resolutions=["240p", "360p", "480p", "720p", "1080p", "1440p"],
            format_type="hls"
        )
        deliverables["streaming_package"] = streaming_result['output_directory']
        
        return deliverables
```

### AI-Powered Content Generation
```python
class AIContentGenerator:
    def __init__(self):
        self.video_agent = VideoAgentIndex({
            "gpu_acceleration": True,
            "ai_models": {
                "text_to_video": True,
                "style_transfer": True,
                "scene_generation": True
            }
        })
    
    async def create_marketing_video(self, product_description: str, 
                                   brand_style: str, duration: float = 30.0) -> str:
        """Generate marketing video from product description"""
        
        # Generate base video from description
        base_video = await self.video_agent.generate_video(
            generation_type="text_to_video",
            prompt=f"Professional product showcase: {product_description}",
            duration=duration,
            style="commercial",
            fps=30
        )
        
        # Apply brand style
        styled_video = await self.video_agent.generate_video(
            generation_type="style_transfer",
            input_video_path=base_video['output_path'],
            style_prompt=f"Apply {brand_style} visual style with brand colors"
        )
        
        # Enhance quality
        final_video = await self.video_agent.enhance_video(
            input_path=styled_video['output_path'],
            enhancements=["sharpen", "color_correct", "upscale"],
            quality_level="high"
        )
        
        return final_video['output_path']
    
    async def create_social_media_variants(self, master_video: str) -> Dict[str, str]:
        """Create social media variants from master video"""
        
        variants = {}
        
        # Instagram Stories (9:16)
        instagram_stories = await self.video_agent.process_video(
            input_path=master_video,
            operations=["crop", "resize"],
            custom_params={
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "crop_mode": "smart_crop"
            }
        )
        variants["instagram_stories"] = instagram_stories['output_path']
        
        # Instagram Posts (1:1) 
        instagram_post = await self.video_agent.process_video(
            input_path=master_video,
            operations=["crop", "resize"],
            custom_params={
                "aspect_ratio": "1:1", 
                "resolution": "1080x1080",
                "crop_mode": "center_crop"
            }
        )
        variants["instagram_post"] = instagram_post['output_path']
        
        # YouTube Shorts (9:16)
        youtube_shorts = await self.video_agent.process_video(
            input_path=master_video,
            operations=["crop", "resize"],
            custom_params={
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "crop_mode": "smart_crop"
            }
        )
        variants["youtube_shorts"] = youtube_shorts['output_path']
        
        return variants
```

## Integration Examples

### REST API Integration
```python
from fastapi import FastAPI, UploadFile, File
from video_agent import VideoAgentIndex

app = FastAPI()
video_agent = VideoAgentIndex()

@app.post("/api/video/analyze")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """Analyze uploaded video"""
    
    # Save uploaded file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Analyze video
    result = await video_agent.analyze_video(
        video_path=file_path,
        analysis_types=["quality", "scenes", "content"]
    )
    
    return {
        "filename": file.filename,
        "analysis": result
    }

@app.post("/api/video/enhance")
async def enhance_video_endpoint(
    file: UploadFile = File(...),
    enhancements: str = "denoise,sharpen",
    quality: str = "medium"
):
    """Enhance uploaded video"""
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    result = await video_agent.enhance_video(
        input_path=file_path,
        enhancements=enhancements.split(","),
        quality_level=quality
    )
    
    return {
        "success": result['success'],
        "enhanced_video": result['output_path'],
        "processing_time": result['processing_time']
    }
```

### Celery Task Integration
```python
from celery import Celery
from video_agent import VideoAgentIndex

app = Celery('video_processing')

@app.task(bind=True)
def process_video_task(self, video_path: str, operations: list):
    """Asynchronous video processing task"""
    
    video_agent = VideoAgentIndex()
    
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting processing'})
        
        # Process video
        result = await video_agent.process_video(
            input_path=video_path,
            operations=operations
        )
        
        return {
            'status': 'SUCCESS',
            'result': result
        }
        
    except Exception as e:
        return {
            'status': 'FAILURE',
            'error': str(e)
        }
    
    finally:
        await video_agent.cleanup()

# Usage
task = process_video_task.delay("/path/to/video.mp4", ["enhance", "compress"])
result = task.get(timeout=3600)  # 1 hour timeout
```

### WebSocket Integration
```python
import asyncio
import websockets
import json
from video_agent import VideoAgentIndex

class VideoProcessingServer:
    def __init__(self):
        self.video_agent = VideoAgentIndex()
        self.clients = set()
    
    async def register_client(self, websocket):
        self.clients.add(websocket)
    
    async def unregister_client(self, websocket):
        self.clients.discard(websocket)
    
    async def broadcast_progress(self, message):
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket, path):
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['action'] == 'process_video':
                    await self.process_video_with_progress(data)
                
        finally:
            await self.unregister_client(websocket)
    
    async def process_video_with_progress(self, request_data):
        video_path = request_data['video_path']
        operations = request_data['operations']
        
        # Send start notification
        await self.broadcast_progress({
            'status': 'started',
            'video_path': video_path,
            'operations': operations
        })
        
        try:
            # Process video with progress updates
            result = await self.video_agent.process_video(
                input_path=video_path,
                operations=operations
            )
            
            # Send completion notification
            await self.broadcast_progress({
                'status': 'completed',
                'result': result
            })
            
        except Exception as e:
            # Send error notification
            await self.broadcast_progress({
                'status': 'error',
                'error': str(e)
            })

# Start WebSocket server
server = VideoProcessingServer()
start_server = websockets.serve(server.handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## Performance Optimization

### Memory-Efficient Processing
```python
async def process_large_video_efficiently(video_path: str):
    """Process large video files efficiently"""
    
    video_agent = VideoAgentIndex({
        "memory_optimization": {
            "stream_processing": True,
            "chunk_size_mb": 100,
            "memory_limit_gb": 8
        }
    })
    
    # Process in chunks to avoid memory issues
    result = await video_agent.process_video(
        input_path=video_path,
        operations=["enhance", "compress"],
        custom_params={
            "streaming_mode": True,
            "chunk_processing": True
        }
    )
    
    return result
```

### GPU Batch Processing
```python
async def batch_process_with_gpu(video_files: List[str]):
    """Efficiently batch process multiple videos using GPU"""
    
    video_agent = VideoAgentIndex({
        "gpu_acceleration": True,
        "batch_processing": {
            "batch_size": 4,
            "gpu_memory_fraction": 0.8
        }
    })
    
    # Group videos for optimal GPU utilization
    batch_jobs = []
    for video_file in video_files:
        batch_jobs.append({
            "request_type": "enhance",
            "input_path": video_file,
            "enhancements": ["upscale", "denoise"],
            "quality_level": "high"
        })
    
    # Process in optimized batches
    results = await video_agent.batch_process(batch_jobs)
    
    return results
```
