# Docker AI Services

## Overview

The AI Services module provides enterprise-grade ML inference engines and content generation services for the Ainflue platform. This module enables advanced AI-powered content creation, enhancement, and processing through state-of-the-art machine learning models and neural networks.

## Architecture

### Services Overview

This module contains 11 specialized Docker services for AI and ML operations:

- **ml_inference_engine** - High-performance ML model inference and prediction service
- **content_generation** - AI-powered content creation and generation service
- **music_remix_engine** - AI-powered music remixing and audio manipulation service
- **style_transfer** - Neural style transfer for images and content transformation
- **content_enhancer** - AI-based content quality enhancement and optimization
- **creative_assistant** - Intelligent creative assistance and recommendation engine
- **variation_generator** - Automated content variation and alternative generation
- **quality_assessor** - AI-driven content quality assessment and scoring
- **trend_adapter** - Trend analysis and content adaptation service
- **format_converter** - Multi-format content conversion with AI optimization
- **neural_processor** - Advanced neural network processing and computation

### Technology Stack

- **Base Images**: Python 3.12-slim with optimized ML libraries
- **ML Frameworks**: PyTorch, TensorFlow, Scikit-learn, Transformers
- **AI/ML**: OpenAI APIs, Hugging Face Models, Custom Neural Networks
- **GPU Support**: CUDA-enabled containers for accelerated processing
- **Storage**: MinIO for model registry and artifact storage
- **Databases**: PostgreSQL for metadata, Redis for caching

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 3.8+
- 16GB RAM minimum (32GB recommended)
- GPU support recommended (NVIDIA CUDA)
- 100GB storage space for models

### Deployment

```bash
# Clone the repository
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue/docker/ai_services

# Start AI services
docker-compose -f docker-compose.ai.yml up -d

# Check service health
docker-compose ps
```

### Configuration

Copy the environment template and configure:

```bash
cp .env.example .env
```

Key configuration variables:
- `AI_DB_URL` - Database connection string
- `REDIS_URL` - Redis cache connection
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `AI_MINIO_PASSWORD` - MinIO storage password
- `CUDA_VISIBLE_DEVICES` - GPU device selection

## Service Details

### ML Inference Engine

High-performance machine learning inference service that provides real-time predictions and model serving capabilities.

**Key Features:**
- Multi-model serving and management
- Real-time inference with low latency
- GPU acceleration support
- Model versioning and A/B testing
- Batch processing capabilities
- Auto-scaling based on load

### Content Generation

AI-powered content creation service using advanced language models and generation algorithms.

**Key Features:**
- Text generation with GPT models
- Image generation with DALL-E integration
- Video content synthesis
- Multi-language content support
- Style and tone customization
- Context-aware generation

### Music Remix Engine

Advanced audio processing service for AI-powered music remixing and audio manipulation.

**Key Features:**
- Source separation and stem isolation
- AI-powered remixing algorithms
- Beat matching and tempo adjustment
- Audio effect application
- Format conversion and optimization
- Real-time audio processing

## API Endpoints

### Health Check
```
GET /health
```

### ML Inference
```
POST /api/v1/inference/predict
POST /api/v1/inference/batch
GET /api/v1/inference/models
```

### Content Generation
```
POST /api/v1/generate/text
POST /api/v1/generate/image
POST /api/v1/generate/audio
GET /api/v1/generate/status/{task_id}
```

### Quality Assessment
```
POST /api/v1/quality/assess
GET /api/v1/quality/metrics
```

## Performance

### Benchmarks

- **Inference Latency**: <100ms for most models
- **Throughput**: 1000+ requests/minute per service
- **GPU Utilization**: Up to 90% with proper batching
- **Memory Efficiency**: Optimized model loading and caching

### Scaling

Services support horizontal scaling:

```bash
# Scale inference engine
docker service scale ml-inference-engine=5

# Scale content generation
docker service scale content-generation=3
```

## Monitoring

### Health Checks

All services include comprehensive health checks:
- Model loading status
- GPU availability and utilization
- Memory usage and limits
- Database connectivity
- Cache performance

### Metrics

Key metrics collected:
- Inference latency and throughput
- Model accuracy and performance
- Resource utilization (CPU, GPU, Memory)
- Request success/failure rates
- Queue lengths and processing times

## Security

### Model Security

- Encrypted model storage
- Secure model loading and validation
- API key management and rotation
- Input sanitization and validation
- Output filtering and safety checks

### Data Protection

- PII detection and anonymization
- Secure data transmission
- Temporary data cleanup
- Audit logging for all operations

## Development

### Adding New Models

1. Place model files in the appropriate directory
2. Update model configuration
3. Rebuild the service container
4. Test with validation dataset

### Custom Services

1. Create new dockerfile following the pattern
2. Add service to docker-compose.yml
3. Implement FastAPI endpoints
4. Add health checks and monitoring

## Troubleshooting

### Common Issues

1. **Model loading failures**
   - Check model file paths and permissions
   - Verify available memory and storage
   - Review model compatibility

2. **GPU not detected**
   - Ensure NVIDIA Docker runtime is installed
   - Check CUDA_VISIBLE_DEVICES environment
   - Verify GPU driver compatibility

3. **High latency**
   - Check batch size configuration
   - Monitor GPU utilization
   - Review network connectivity

## License

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

## Support

For technical support and questions:
- Email: mlaiel@live.de
- GitHub Issues: https://github.com/Mlaiel/Ainflue/issues

## Changelog

### Version 1.0.0 (2025-09-10)
- Initial release
- 11 specialized AI services
- GPU acceleration support
- Model registry with MinIO
- Comprehensive monitoring and health checks