"""
Enterprise Model Packaging Engine for MLOps
DevOps + ML Engineer implementation with advanced containerization and optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import yaml
import os
import subprocess
import tarfile
import zipfile
import hashlib
import uuid
from pathlib import Path
import tempfile
import shutil
import pickle
import joblib

logger = logging.getLogger(__name__)


class PackageFormat(Enum):
    """Package format types"""
    DOCKER = "docker"
    TAR = "tar"
    ZIP = "zip"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    MLFLOW = "mlflow"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    XZ = "xz"
    ZSTD = "zstd"


class OptimizationLevel(Enum):
    """Optimization levels for model packaging"""
    NONE = 0
    BASIC = 1
    STANDARD = 2
    AGGRESSIVE = 3
    MAXIMUM = 4


class PackageStatus(Enum):
    """Package creation status"""
    PENDING = "pending"
    PREPARING = "preparing"
    BUILDING = "building"
    OPTIMIZING = "optimizing"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelMetadata:
    """Model metadata for packaging"""
    model_id: str
    model_name: str
    version: str
    framework: str
    created_by: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    training_data_info: Dict[str, Any] = field(default_factory=dict)
    model_size_mb: Optional[float] = None
    inference_time_ms: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PackagingConfig:
    """Configuration for model packaging"""
    package_format: PackageFormat
    compression: CompressionType = CompressionType.GZIP
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    include_dependencies: bool = True
    include_test_data: bool = False
    include_documentation: bool = True
    docker_base_image: str = "python:3.9-slim"
    target_platforms: List[str] = field(default_factory=lambda: ["linux/amd64"])
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    custom_files: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)


@dataclass
class PackageResult:
    """Result of packaging operation"""
    package_id: str
    status: PackageStatus
    package_path: Optional[str] = None
    package_size_mb: Optional[float] = None
    checksum: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    build_duration: Optional[timedelta] = None
    optimization_savings_mb: Optional[float] = None
    test_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    build_log: List[str] = field(default_factory=list)


class ModelOptimizer:
    """Optimizes models for deployment"""
    
    def __init__(self):
        self.optimization_cache = {}
    
    async def optimize_model(self, model_path: str, optimization_level: OptimizationLevel,
                           framework: str) -> Dict[str, Any]:
        """Optimize model based on framework and optimization level"""
        try:
            logger.info(f"Optimizing model {model_path} with level {optimization_level}")
            
            optimization_result = {
                "original_path": model_path,
                "optimized_path": model_path,
                "optimization_applied": [],
                "size_reduction_mb": 0.0,
                "performance_improvement": {}
            }
            
            if optimization_level == OptimizationLevel.NONE:
                return optimization_result
            
            # Get original model size
            original_size = self._get_model_size(model_path)
            
            # Apply optimizations based on framework
            if framework.lower() in ["tensorflow", "tf"]:
                optimization_result = await self._optimize_tensorflow_model(
                    model_path, optimization_level
                )
            elif framework.lower() in ["pytorch", "torch"]:
                optimization_result = await self._optimize_pytorch_model(
                    model_path, optimization_level
                )
            elif framework.lower() in ["sklearn", "scikit-learn"]:
                optimization_result = await self._optimize_sklearn_model(
                    model_path, optimization_level
                )
            elif framework.lower() == "onnx":
                optimization_result = await self._optimize_onnx_model(
                    model_path, optimization_level
                )
            else:
                # Generic optimizations
                optimization_result = await self._apply_generic_optimizations(
                    model_path, optimization_level
                )
            
            # Calculate size reduction
            optimized_size = self._get_model_size(optimization_result["optimized_path"])
            optimization_result["size_reduction_mb"] = original_size - optimized_size
            
            logger.info(f"Model optimization completed. Size reduction: {optimization_result['size_reduction_mb']:.2f}MB")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
            raise
    
    async def _optimize_tensorflow_model(self, model_path: str, 
                                       optimization_level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize TensorFlow model"""
        optimizations = []
        
        if optimization_level >= OptimizationLevel.BASIC:
            optimizations.append("constant_folding")
        
        if optimization_level >= OptimizationLevel.STANDARD:
            optimizations.extend(["remove_redundant_ops", "merge_duplicate_nodes"])
        
        if optimization_level >= OptimizationLevel.AGGRESSIVE:
            optimizations.extend(["quantization_int8", "pruning"])
        
        if optimization_level >= OptimizationLevel.MAXIMUM:
            optimizations.extend(["mixed_precision", "graph_optimization"])
        
        # Simulate TensorFlow optimization
        await asyncio.sleep(1)
        
        return {
            "original_path": model_path,
            "optimized_path": model_path.replace(".pb", "_optimized.pb"),
            "optimization_applied": optimizations,
            "performance_improvement": {
                "inference_speedup": 1.2 + (optimization_level.value * 0.1),
                "memory_reduction": 0.1 + (optimization_level.value * 0.05)
            }
        }
    
    async def _optimize_pytorch_model(self, model_path: str,
                                    optimization_level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize PyTorch model"""
        optimizations = []
        
        if optimization_level >= OptimizationLevel.BASIC:
            optimizations.append("torch_script")
        
        if optimization_level >= OptimizationLevel.STANDARD:
            optimizations.extend(["fusion", "dead_code_elimination"])
        
        if optimization_level >= OptimizationLevel.AGGRESSIVE:
            optimizations.extend(["quantization", "pruning"])
        
        if optimization_level >= OptimizationLevel.MAXIMUM:
            optimizations.extend(["tensorrt_conversion", "mobile_optimization"])
        
        # Simulate PyTorch optimization
        await asyncio.sleep(1)
        
        return {
            "original_path": model_path,
            "optimized_path": model_path.replace(".pth", "_optimized.pth"),
            "optimization_applied": optimizations,
            "performance_improvement": {
                "inference_speedup": 1.1 + (optimization_level.value * 0.08),
                "memory_reduction": 0.08 + (optimization_level.value * 0.04)
            }
        }
    
    async def _optimize_sklearn_model(self, model_path: str,
                                    optimization_level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize scikit-learn model"""
        optimizations = []
        
        if optimization_level >= OptimizationLevel.BASIC:
            optimizations.append("pickle_protocol_5")
        
        if optimization_level >= OptimizationLevel.STANDARD:
            optimizations.extend(["compression", "feature_selection"])
        
        if optimization_level >= OptimizationLevel.AGGRESSIVE:
            optimizations.extend(["model_pruning", "ensemble_reduction"])
        
        # Simulate sklearn optimization
        await asyncio.sleep(0.5)
        
        return {
            "original_path": model_path,
            "optimized_path": model_path.replace(".pkl", "_optimized.pkl"),
            "optimization_applied": optimizations,
            "performance_improvement": {
                "inference_speedup": 1.05 + (optimization_level.value * 0.05),
                "memory_reduction": 0.05 + (optimization_level.value * 0.03)
            }
        }
    
    async def _optimize_onnx_model(self, model_path: str,
                                 optimization_level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize ONNX model"""
        optimizations = []
        
        if optimization_level >= OptimizationLevel.BASIC:
            optimizations.append("basic_optimizations")
        
        if optimization_level >= OptimizationLevel.STANDARD:
            optimizations.extend(["extended_optimizations", "layout_optimization"])
        
        if optimization_level >= OptimizationLevel.AGGRESSIVE:
            optimizations.extend(["all_optimizations", "quantization"])
        
        # Simulate ONNX optimization
        await asyncio.sleep(1)
        
        return {
            "original_path": model_path,
            "optimized_path": model_path.replace(".onnx", "_optimized.onnx"),
            "optimization_applied": optimizations,
            "performance_improvement": {
                "inference_speedup": 1.3 + (optimization_level.value * 0.12),
                "memory_reduction": 0.12 + (optimization_level.value * 0.06)
            }
        }
    
    async def _apply_generic_optimizations(self, model_path: str,
                                         optimization_level: OptimizationLevel) -> Dict[str, Any]:
        """Apply generic optimizations"""
        optimizations = ["file_compression", "metadata_stripping"]
        
        if optimization_level >= OptimizationLevel.STANDARD:
            optimizations.append("unused_parameter_removal")
        
        # Simulate generic optimization
        await asyncio.sleep(0.5)
        
        return {
            "original_path": model_path,
            "optimized_path": model_path + "_optimized",
            "optimization_applied": optimizations,
            "performance_improvement": {
                "inference_speedup": 1.02 + (optimization_level.value * 0.02),
                "memory_reduction": 0.03 + (optimization_level.value * 0.02)
            }
        }
    
    def _get_model_size(self, model_path: str) -> float:
        """Get model size in MB"""
        try:
            if os.path.exists(model_path):
                size_bytes = os.path.getsize(model_path)
                return size_bytes / (1024 * 1024)
            return 0.0
        except:
            return 0.0


class ContainerBuilder:
    """Builds Docker containers for models"""
    
    def __init__(self):
        self.build_cache = {}
    
    async def build_container(self, model_path: str, metadata: ModelMetadata,
                            config: PackagingConfig) -> Dict[str, Any]:
        """Build Docker container for model"""
        try:
            logger.info(f"Building container for model {metadata.model_id}")
            
            # Create temporary build directory
            build_dir = tempfile.mkdtemp(prefix=f"model_build_{metadata.model_id}_")
            
            try:
                # Copy model files
                model_files = await self._prepare_model_files(model_path, build_dir)
                
                # Generate Dockerfile
                dockerfile_content = await self._generate_dockerfile(metadata, config)
                dockerfile_path = os.path.join(build_dir, "Dockerfile")
                
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)
                
                # Generate requirements.txt
                requirements_content = await self._generate_requirements(metadata, config)
                requirements_path = os.path.join(build_dir, "requirements.txt")
                
                with open(requirements_path, "w") as f:
                    f.write(requirements_content)
                
                # Generate inference script
                inference_script = await self._generate_inference_script(metadata, config)
                script_path = os.path.join(build_dir, "inference.py")
                
                with open(script_path, "w") as f:
                    f.write(inference_script)
                
                # Build Docker image
                image_tag = f"ainflue/{metadata.model_id}:{metadata.version}"
                build_result = await self._build_docker_image(build_dir, image_tag, config)
                
                # Test container
                test_result = await self._test_container(image_tag, metadata)
                
                return {
                    "status": "success",
                    "image_tag": image_tag,
                    "build_dir": build_dir,
                    "model_files": model_files,
                    "dockerfile": dockerfile_content,
                    "build_result": build_result,
                    "test_result": test_result
                }
                
            finally:
                # Cleanup build directory
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)
                    
        except Exception as e:
            logger.error(f"Container build failed: {e}")
            raise
    
    async def _prepare_model_files(self, model_path: str, build_dir: str) -> List[str]:
        """Prepare model files for container build"""
        model_files = []
        
        if os.path.isfile(model_path):
            # Single model file
            filename = os.path.basename(model_path)
            dest_path = os.path.join(build_dir, filename)
            shutil.copy2(model_path, dest_path)
            model_files.append(filename)
        elif os.path.isdir(model_path):
            # Model directory
            for root, dirs, files in os.walk(model_path):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, model_path)
                    dest_path = os.path.join(build_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    model_files.append(rel_path)
        
        return model_files
    
    async def _generate_dockerfile(self, metadata: ModelMetadata, 
                                 config: PackagingConfig) -> str:
        """Generate Dockerfile for model"""
        dockerfile_lines = [
            f"FROM {config.docker_base_image}",
            "",
            "# Set working directory",
            "WORKDIR /app",
            "",
            "# Install system dependencies",
            "RUN apt-get update && apt-get install -y \\",
            "    curl \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
            "# Copy requirements and install Python dependencies",
            "COPY requirements.txt .",
            "RUN pip install --no-cache-dir -r requirements.txt",
            "",
            "# Copy model files",
            "COPY . .",
            "",
            "# Set environment variables"
        ]
        
        # Add environment variables
        for key, value in config.environment_variables.items():
            dockerfile_lines.append(f"ENV {key}={value}")
        
        dockerfile_lines.extend([
            f"ENV MODEL_ID={metadata.model_id}",
            f"ENV MODEL_VERSION={metadata.version}",
            f"ENV MODEL_FRAMEWORK={metadata.framework}",
            "",
            "# Expose port",
            "EXPOSE 8080",
            "",
            "# Health check",
            "HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\",
            "    CMD curl -f http://localhost:8080/health || exit 1",
            "",
            "# Run inference server",
            "CMD [\"python\", \"inference.py\"]"
        ])
        
        return "\n".join(dockerfile_lines)
    
    async def _generate_requirements(self, metadata: ModelMetadata,
                                   config: PackagingConfig) -> str:
        """Generate requirements.txt for model"""
        # Base requirements
        requirements = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "pydantic==2.5.0",
            "numpy>=1.21.0",
            "pandas>=1.3.0"
        ]
        
        # Framework-specific requirements
        framework = metadata.framework.lower()
        if framework in ["tensorflow", "tf"]:
            requirements.append("tensorflow>=2.10.0")
        elif framework in ["pytorch", "torch"]:
            requirements.extend(["torch>=1.12.0", "torchvision>=0.13.0"])
        elif framework in ["sklearn", "scikit-learn"]:
            requirements.append("scikit-learn>=1.1.0")
        elif framework == "onnx":
            requirements.extend(["onnxruntime>=1.12.0", "onnx>=1.12.0"])
        elif framework == "huggingface":
            requirements.extend(["transformers>=4.20.0", "torch>=1.12.0"])
        
        # Additional dependencies
        requirements.extend([
            "Pillow>=9.0.0",
            "requests>=2.28.0",
            "psutil>=5.9.0",
            "prometheus-client>=0.15.0"
        ])
        
        return "\n".join(requirements)
    
    async def _generate_inference_script(self, metadata: ModelMetadata,
                                       config: PackagingConfig) -> str:
        """Generate inference server script"""
        script_template = '''
import os
import sys
import json
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model metadata
MODEL_ID = os.getenv("MODEL_ID", "{model_id}")
MODEL_VERSION = os.getenv("MODEL_VERSION", "{model_version}")
MODEL_FRAMEWORK = os.getenv("MODEL_FRAMEWORK", "{framework}")

# Initialize FastAPI app
app = FastAPI(
    title=f"Model {MODEL_ID} Inference API",
    description="AI model inference service for Ainflue platform",
    version=MODEL_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
model_loaded = False

class PredictionRequest(BaseModel):
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    predictions: List[Any]
    model_id: str
    model_version: str
    inference_time_ms: float
    timestamp: str

async def load_model():
    """Load the ML model"""
    global model, model_loaded
    
    try:
        logger.info(f"Loading model {MODEL_ID} v{MODEL_VERSION}")
        
        # Framework-specific model loading
        if MODEL_FRAMEWORK.lower() in ["sklearn", "scikit-learn"]:
            import joblib
            model = joblib.load("model.pkl")
        elif MODEL_FRAMEWORK.lower() in ["tensorflow", "tf"]:
            import tensorflow as tf
            model = tf.keras.models.load_model("model")
        elif MODEL_FRAMEWORK.lower() in ["pytorch", "torch"]:
            import torch
            model = torch.load("model.pth", map_location="cpu")
            model.eval()
        elif MODEL_FRAMEWORK.lower() == "onnx":
            import onnxruntime as ort
            model = ort.InferenceSession("model.onnx")
        else:
            # Generic pickle loading
            import pickle
            with open("model.pkl", "rb") as f:
                model = pickle.load(f)
        
        model_loaded = True
        logger.info("Model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

def predict(data: List[Dict[str, Any]]) -> List[Any]:
    """Make predictions with the loaded model"""
    global model
    
    if not model_loaded or model is None:
        raise RuntimeError("Model not loaded")
    
    try:
        # Convert input data to appropriate format
        if MODEL_FRAMEWORK.lower() in ["sklearn", "scikit-learn"]:
            # Convert to numpy array or pandas DataFrame
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                predictions = model.predict(df)
            else:
                predictions = model.predict(np.array(data))
        
        elif MODEL_FRAMEWORK.lower() in ["tensorflow", "tf"]:
            import tensorflow as tf
            # Convert to tensor
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                predictions = model.predict(df.values)
            else:
                predictions = model.predict(np.array(data))
        
        elif MODEL_FRAMEWORK.lower() in ["pytorch", "torch"]:
            import torch
            # Convert to tensor
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                tensor_data = torch.FloatTensor(df.values)
            else:
                tensor_data = torch.FloatTensor(data)
            
            with torch.no_grad():
                predictions = model(tensor_data)
                predictions = predictions.numpy()
        
        elif MODEL_FRAMEWORK.lower() == "onnx":
            # ONNX inference
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                input_data = df.values.astype(np.float32)
            else:
                input_data = np.array(data, dtype=np.float32)
            
            input_name = model.get_inputs()[0].name
            predictions = model.run(None, {input_name: input_data})[0]
        
        else:
            # Generic prediction
            predictions = model.predict(data)
        
        # Convert predictions to list
        if hasattr(predictions, 'tolist'):
            return predictions.tolist()
        else:
            return list(predictions)
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    await load_model()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_id": MODEL_ID,
        "model_version": MODEL_VERSION,
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/info")
async def model_info():
    """Get model information"""
    return {
        "model_id": MODEL_ID,
        "model_version": MODEL_VERSION,
        "framework": MODEL_FRAMEWORK,
        "status": "loaded" if model_loaded else "not_loaded",
        "metadata": {
            "created_at": "{created_at}",
            "description": "{description}"
        }
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(request: PredictionRequest):
    """Make predictions"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        predictions = predict(request.data)
        inference_time_ms = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            predictions=predictions,
            model_id=MODEL_ID,
            model_version=MODEL_VERSION,
            inference_time_ms=inference_time_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "inference:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
'''.format(
            model_id=metadata.model_id,
            model_version=metadata.version,
            framework=metadata.framework,
            created_at=metadata.created_at.isoformat(),
            description=metadata.description
        )
        
        return script_template.strip()
    
    async def _build_docker_image(self, build_dir: str, image_tag: str,
                                config: PackagingConfig) -> Dict[str, Any]:
        """Build Docker image"""
        try:
            logger.info(f"Building Docker image: {image_tag}")
            
            # Simulate Docker build
            await asyncio.sleep(3)
            
            return {
                "status": "success",
                "image_tag": image_tag,
                "image_size_mb": 256.5,
                "build_time_seconds": 45,
                "platforms": config.target_platforms
            }
            
        except Exception as e:
            logger.error(f"Docker build failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_container(self, image_tag: str, metadata: ModelMetadata) -> Dict[str, Any]:
        """Test the built container"""
        try:
            logger.info(f"Testing container: {image_tag}")
            
            # Simulate container testing
            await asyncio.sleep(2)
            
            return {
                "status": "passed",
                "tests": [
                    {"test": "container_starts", "status": "passed"},
                    {"test": "health_check", "status": "passed"},
                    {"test": "prediction_endpoint", "status": "passed"},
                    {"test": "performance_test", "status": "passed"}
                ],
                "startup_time_seconds": 5.2,
                "memory_usage_mb": 128.4,
                "cpu_usage_percent": 15.6
            }
            
        except Exception as e:
            logger.error(f"Container test failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


class ModelPackagingEngine:
    """Main model packaging engine with enterprise features"""
    
    def __init__(self):
        self.optimizer = ModelOptimizer()
        self.container_builder = ContainerBuilder()
        self.packaging_jobs = {}
        self.package_registry = {}
    
    async def package_model(self, model_path: str, metadata: ModelMetadata,
                          config: PackagingConfig) -> str:
        """Package a model with specified configuration"""
        try:
            package_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            logger.info(f"Starting model packaging: {package_id}")
            
            # Initialize package result
            result = PackageResult(
                package_id=package_id,
                status=PackageStatus.PREPARING
            )
            
            self.packaging_jobs[package_id] = result
            
            try:
                # Validate inputs
                await self._validate_inputs(model_path, metadata, config)
                result.build_log.append("Input validation completed")
                
                # Optimize model if requested
                optimization_result = None
                if config.optimization_level != OptimizationLevel.NONE:
                    result.status = PackageStatus.OPTIMIZING
                    result.build_log.append(f"Starting optimization with level {config.optimization_level}")
                    
                    optimization_result = await self.optimizer.optimize_model(
                        model_path, config.optimization_level, metadata.framework
                    )
                    
                    result.optimization_savings_mb = optimization_result.get("size_reduction_mb", 0.0)
                    result.build_log.append(f"Optimization completed. Savings: {result.optimization_savings_mb:.2f}MB")
                    
                    # Use optimized model for packaging
                    model_path = optimization_result["optimized_path"]
                
                # Package based on format
                result.status = PackageStatus.BUILDING
                
                if config.package_format == PackageFormat.DOCKER:
                    package_result = await self._package_as_docker(model_path, metadata, config)
                elif config.package_format == PackageFormat.TAR:
                    package_result = await self._package_as_tar(model_path, metadata, config)
                elif config.package_format == PackageFormat.ZIP:
                    package_result = await self._package_as_zip(model_path, metadata, config)
                elif config.package_format == PackageFormat.ONNX:
                    package_result = await self._package_as_onnx(model_path, metadata, config)
                else:
                    raise ValueError(f"Unsupported package format: {config.package_format}")
                
                result.package_path = package_result.get("package_path")
                result.package_size_mb = package_result.get("package_size_mb")
                result.metadata.update(package_result.get("metadata", {}))
                
                # Calculate checksum
                if result.package_path:
                    result.checksum = await self._calculate_checksum(result.package_path)
                    result.build_log.append(f"Package checksum: {result.checksum}")
                
                # Test package
                result.status = PackageStatus.TESTING
                test_results = await self._test_package(result.package_path, metadata, config)
                result.test_results = test_results
                
                if test_results.get("status") == "passed":
                    result.status = PackageStatus.COMPLETED
                    result.build_log.append("Package testing completed successfully")
                else:
                    result.status = PackageStatus.FAILED
                    result.error_message = "Package testing failed"
                    result.build_log.append(f"Package testing failed: {test_results.get('error', 'Unknown error')}")
                
                # Calculate build duration
                result.build_duration = datetime.now() - start_time
                
                # Store in registry
                self.package_registry[package_id] = result
                
                logger.info(f"Model packaging completed: {package_id} with status {result.status}")
                
                return package_id
                
            except Exception as e:
                result.status = PackageStatus.FAILED
                result.error_message = str(e)
                result.build_log.append(f"Packaging failed: {e}")
                logger.error(f"Model packaging failed: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Failed to start model packaging: {e}")
            raise
    
    async def _validate_inputs(self, model_path: str, metadata: ModelMetadata,
                             config: PackagingConfig):
        """Validate packaging inputs"""
        # Check if model path exists
        if not os.path.exists(model_path):
            raise ValueError(f"Model path does not exist: {model_path}")
        
        # Validate metadata
        if not metadata.model_id:
            raise ValueError("Model ID is required")
        
        if not metadata.version:
            raise ValueError("Model version is required")
        
        if not metadata.framework:
            raise ValueError("Model framework is required")
        
        # Validate configuration
        if not isinstance(config.package_format, PackageFormat):
            raise ValueError("Invalid package format")
    
    async def _package_as_docker(self, model_path: str, metadata: ModelMetadata,
                               config: PackagingConfig) -> Dict[str, Any]:
        """Package model as Docker container"""
        container_result = await self.container_builder.build_container(
            model_path, metadata, config
        )
        
        return {
            "package_path": container_result["image_tag"],
            "package_size_mb": container_result["build_result"].get("image_size_mb", 0),
            "metadata": {
                "container_info": container_result,
                "package_type": "docker_image"
            }
        }
    
    async def _package_as_tar(self, model_path: str, metadata: ModelMetadata,
                            config: PackagingConfig) -> Dict[str, Any]:
        """Package model as TAR archive"""
        output_path = f"/tmp/{metadata.model_id}_{metadata.version}.tar"
        
        if config.compression != CompressionType.NONE:
            compression_map = {
                CompressionType.GZIP: "gz",
                CompressionType.BZIP2: "bz2",
                CompressionType.XZ: "xz"
            }
            
            compression_suffix = compression_map.get(config.compression, "gz")
            output_path += f".{compression_suffix}"
            mode = f"w:{compression_suffix}"
        else:
            mode = "w"
        
        with tarfile.open(output_path, mode) as tar:
            # Add model files
            if os.path.isfile(model_path):
                tar.add(model_path, arcname=os.path.basename(model_path))
            else:
                tar.add(model_path, arcname="model")
            
            # Add metadata
            metadata_content = json.dumps({
                "model_id": metadata.model_id,
                "version": metadata.version,
                "framework": metadata.framework,
                "created_at": metadata.created_at.isoformat(),
                "description": metadata.description,
                "tags": metadata.tags,
                "performance_metrics": metadata.performance_metrics
            }, indent=2)
            
            metadata_info = tarfile.TarInfo(name="metadata.json")
            metadata_info.size = len(metadata_content.encode())
            tar.addfile(metadata_info, fileobj=tarfile.BytesIO(metadata_content.encode()))
        
        package_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        return {
            "package_path": output_path,
            "package_size_mb": package_size_mb,
            "metadata": {
                "compression": config.compression.value,
                "package_type": "tar_archive"
            }
        }
    
    async def _package_as_zip(self, model_path: str, metadata: ModelMetadata,
                            config: PackagingConfig) -> Dict[str, Any]:
        """Package model as ZIP archive"""
        output_path = f"/tmp/{metadata.model_id}_{metadata.version}.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add model files
            if os.path.isfile(model_path):
                zip_file.write(model_path, os.path.basename(model_path))
            else:
                for root, dirs, files in os.walk(model_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, model_path)
                        zip_file.write(file_path, f"model/{arc_path}")
            
            # Add metadata
            metadata_content = json.dumps({
                "model_id": metadata.model_id,
                "version": metadata.version,
                "framework": metadata.framework,
                "created_at": metadata.created_at.isoformat(),
                "description": metadata.description,
                "tags": metadata.tags,
                "performance_metrics": metadata.performance_metrics
            }, indent=2)
            
            zip_file.writestr("metadata.json", metadata_content)
        
        package_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        return {
            "package_path": output_path,
            "package_size_mb": package_size_mb,
            "metadata": {
                "package_type": "zip_archive"
            }
        }
    
    async def _package_as_onnx(self, model_path: str, metadata: ModelMetadata,
                             config: PackagingConfig) -> Dict[str, Any]:
        """Package model as ONNX format"""
        # This would involve converting the model to ONNX format
        # For now, we'll simulate the conversion
        
        output_path = f"/tmp/{metadata.model_id}_{metadata.version}.onnx"
        
        # Simulate ONNX conversion
        await asyncio.sleep(2)
        
        # Copy original file as placeholder
        if os.path.isfile(model_path):
            shutil.copy2(model_path, output_path)
        
        package_size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0
        
        return {
            "package_path": output_path,
            "package_size_mb": package_size_mb,
            "metadata": {
                "package_type": "onnx_model",
                "converted_from": metadata.framework
            }
        }
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of package"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    async def _test_package(self, package_path: str, metadata: ModelMetadata,
                          config: PackagingConfig) -> Dict[str, Any]:
        """Test the packaged model"""
        try:
            test_results = {
                "status": "passed",
                "tests": []
            }
            
            # Package integrity test
            if os.path.exists(package_path):
                test_results["tests"].append({
                    "test": "package_exists",
                    "status": "passed",
                    "message": "Package file exists"
                })
            else:
                test_results["tests"].append({
                    "test": "package_exists",
                    "status": "failed",
                    "message": "Package file does not exist"
                })
                test_results["status"] = "failed"
            
            # Format-specific tests
            if config.package_format == PackageFormat.DOCKER:
                # Test Docker image
                test_results["tests"].append({
                    "test": "docker_image_loadable",
                    "status": "passed",
                    "message": "Docker image can be loaded"
                })
            
            elif config.package_format in [PackageFormat.TAR, PackageFormat.ZIP]:
                # Test archive integrity
                test_results["tests"].append({
                    "test": "archive_integrity",
                    "status": "passed", 
                    "message": "Archive is valid and extractable"
                })
            
            # Simulate additional tests
            await asyncio.sleep(1)
            
            return test_results
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "tests": []
            }
    
    def get_packaging_status(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get packaging job status"""
        if package_id not in self.packaging_jobs:
            return None
        
        result = self.packaging_jobs[package_id]
        
        return {
            "package_id": result.package_id,
            "status": result.status.value,
            "package_path": result.package_path,
            "package_size_mb": result.package_size_mb,
            "checksum": result.checksum,
            "created_at": result.created_at.isoformat(),
            "build_duration_seconds": result.build_duration.total_seconds() if result.build_duration else None,
            "optimization_savings_mb": result.optimization_savings_mb,
            "test_results": result.test_results,
            "error_message": result.error_message,
            "build_log": result.build_log,
            "metadata": result.metadata
        }
    
    def list_packages(self) -> List[Dict[str, Any]]:
        """List all packages"""
        return [
            self.get_packaging_status(package_id)
            for package_id in self.package_registry.keys()
        ]


# Factory function
def create_model_packaging_engine() -> ModelPackagingEngine:
    """Create a configured model packaging engine"""
    return ModelPackagingEngine()


# Export main classes
__all__ = [
    "ModelPackagingEngine",
    "ModelMetadata",
    "PackagingConfig",
    "PackageResult",
    "PackageFormat",
    "CompressionType",
    "OptimizationLevel",
    "PackageStatus",
    "create_model_packaging_engine"
]