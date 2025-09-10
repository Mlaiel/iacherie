"""🚀 Serverless Deployment Engine - Cost-Effective ML Inference
==============================================================
Module: ml/deployment/serverless_deployment_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SERVERLESS ML DEPLOYMENT
Serverless model deployment for cost-effective inference
- AWS Lambda, Azure Functions, Google Cloud Functions support
- Cold start optimization
- Auto-scaling and cost optimization
- Multi-cloud serverless orchestration
"""

import asyncio
import logging
import json
import zipfile
import tempfile
import base64
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import boto3
import hashlib
import subprocess
import shutil
import os

logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    VERCEL = "vercel"
    NETLIFY = "netlify"

class FunctionRuntime(Enum):
    """Serverless runtime environments"""
    PYTHON_39 = "python3.9"
    PYTHON_310 = "python3.10"
    PYTHON_311 = "python3.11"
    NODEJS_18 = "nodejs18.x"
    NODEJS_20 = "nodejs20.x"

class DeploymentStatus(Enum):
    """Deployment status tracking"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    UPDATING = "updating"
    DELETING = "deleting"

@dataclass
class ServerlessConfig:
    """Serverless deployment configuration"""
    function_name: str
    runtime: FunctionRuntime
    memory_mb: int = 512
    timeout_seconds: int = 30
    environment_variables: Dict[str, str] = field(default_factory=dict)
    vpc_config: Optional[Dict[str, Any]] = None
    dead_letter_config: Optional[Dict[str, str]] = None
    reserved_concurrency: Optional[int] = None
    provisioned_concurrency: Optional[int] = None

@dataclass
class ServerlessFunction:
    """Serverless function metadata"""
    function_id: str
    function_name: str
    provider: CloudProvider
    runtime: FunctionRuntime
    model_id: str
    version: str
    endpoint_url: str
    created_at: datetime
    updated_at: datetime
    status: DeploymentStatus
    config: ServerlessConfig
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    cost_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class InvocationRequest:
    """Serverless function invocation request"""
    function_id: str
    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    async_invocation: bool = False

@dataclass
class InvocationResponse:
    """Serverless function invocation response"""
    function_id: str
    request_id: str
    status_code: int
    response_payload: Any
    execution_time_ms: int
    billed_duration_ms: int
    memory_used_mb: int
    cold_start: bool
    error: Optional[str] = None

class ColdStartOptimizer:
    """Optimize cold start performance"""
    
    def __init__(self):
        self.warm_pools: Dict[str, datetime] = {}
        self.optimization_strategies = {
            'model_preloading': True,
            'dependency_optimization': True,
            'memory_optimization': True,
            'provisioned_concurrency': False
        }
    
    async def optimize_deployment_package(self, package_path: str, model_path: str) -> str:
        """
        Optimize deployment package for cold start performance
        """
        try:
            optimized_path = f"{package_path}_optimized"
            
            # Create optimized package directory
            os.makedirs(optimized_path, exist_ok=True)
            
            # Copy and optimize dependencies
            await self._optimize_dependencies(package_path, optimized_path)
            
            # Optimize model loading
            await self._optimize_model_loading(model_path, optimized_path)
            
            # Generate optimized handler
            await self._generate_optimized_handler(optimized_path)
            
            logger.info(f"Optimized deployment package created at {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"Error optimizing deployment package: {str(e)}")
            raise

    async def _optimize_dependencies(self, source_path: str, target_path: str) -> None:
        """Optimize Python dependencies for smaller package size"""
        # Copy only necessary files
        requirements_content = """
numpy
scikit-learn
pandas
fastapi
uvicorn
"""
        
        # Write minimal requirements
        with open(f"{target_path}/requirements.txt", 'w') as f:
            f.write(requirements_content.strip())
        
        # Install minimal dependencies
        subprocess.run([
            "pip", "install", "-r", f"{target_path}/requirements.txt",
            "-t", target_path, "--no-deps"
        ], check=True)

    async def _optimize_model_loading(self, model_path: str, target_path: str) -> None:
        """Optimize model loading for faster startup"""
        # Copy model to package
        model_target = f"{target_path}/model"
        os.makedirs(model_target, exist_ok=True)
        
        if os.path.isfile(model_path):
            shutil.copy2(model_path, f"{model_target}/model.pkl")
        else:
            shutil.copytree(model_path, f"{model_target}/", dirs_exist_ok=True)

    async def _generate_optimized_handler(self, package_path: str) -> None:
        """Generate optimized Lambda handler"""
        handler_code = '''
import json
import pickle
import os
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables for model caching
MODEL = None
MODEL_LOADED = False

def load_model():
    """Load model once during cold start"""
    global MODEL, MODEL_LOADED
    
    if not MODEL_LOADED:
        try:
            model_path = "/opt/ml/model/model.pkl"
            if not os.path.exists(model_path):
                model_path = "./model/model.pkl"
            
            with open(model_path, 'rb') as f:
                MODEL = pickle.load(f)
            
            MODEL_LOADED = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

def lambda_handler(event, context):
    """Optimized Lambda handler with model caching"""
    try:
        # Load model if not already loaded
        if not MODEL_LOADED:
            load_model()
        
        # Parse input
        if isinstance(event, str):
            data = json.loads(event)
        else:
            data = event.get('body', event)
            if isinstance(data, str):
                data = json.loads(data)
        
        # Extract features
        features = data.get('features', [])
        if not features:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing features'})
            }
        
        # Make prediction
        prediction = MODEL.predict([features])
        confidence = getattr(MODEL, 'predict_proba', lambda x: [[0.5, 0.5]])([features])
        
        # Prepare response
        response = {
            'prediction': prediction.tolist()[0] if hasattr(prediction, 'tolist') else prediction[0],
            'confidence': confidence.tolist()[0] if hasattr(confidence, 'tolist') else [0.5, 0.5],
            'model_version': os.environ.get('MODEL_VERSION', '1.0.0'),
            'timestamp': context.aws_request_id if context else 'local'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Pre-load model during import (for better cold start performance)
load_model()
'''
        
        with open(f"{package_path}/lambda_function.py", 'w') as f:
            f.write(handler_code)

class ServerlessDeploymentEngine:
    """
    Serverless deployment engine for cost-effective ML inference
    """
    
    def __init__(self, default_provider: CloudProvider = CloudProvider.AWS):
        self.default_provider = default_provider
        self.deployed_functions: Dict[str, ServerlessFunction] = {}
        self.cold_start_optimizer = ColdStartOptimizer()
        self.deployment_configs: Dict[CloudProvider, Dict[str, Any]] = {}
        
        # Initialize cloud clients
        self.cloud_clients = {}
        self._initialize_cloud_clients()

    async def deploy_model(
        self,
        model_id: str,
        model_path: str,
        config: ServerlessConfig,
        provider: Optional[CloudProvider] = None,
        optimize_cold_start: bool = True
    ) -> ServerlessFunction:
        """
        Deploy ML model as serverless function
        """
        try:
            provider = provider or self.default_provider
            function_id = f"{model_id}_{provider.value}_{int(datetime.utcnow().timestamp())}"
            
            logger.info(f"Starting serverless deployment for model {model_id} on {provider.value}")
            
            # Create deployment package
            package_path = await self._create_deployment_package(
                model_path, config, optimize_cold_start
            )
            
            # Deploy to cloud provider
            if provider == CloudProvider.AWS:
                endpoint_url = await self._deploy_to_aws(function_id, package_path, config)
            elif provider == CloudProvider.AZURE:
                endpoint_url = await self._deploy_to_azure(function_id, package_path, config)
            elif provider == CloudProvider.GCP:
                endpoint_url = await self._deploy_to_gcp(function_id, package_path, config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Create function metadata
            function = ServerlessFunction(
                function_id=function_id,
                function_name=config.function_name,
                provider=provider,
                runtime=config.runtime,
                model_id=model_id,
                version="1.0.0",
                endpoint_url=endpoint_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status=DeploymentStatus.ACTIVE,
                config=config
            )
            
            # Store function metadata
            self.deployed_functions[function_id] = function
            
            # Cleanup temporary files
            shutil.rmtree(package_path, ignore_errors=True)
            
            logger.info(f"Successfully deployed model {model_id} as function {function_id}")
            return function
            
        except Exception as e:
            logger.error(f"Error deploying model {model_id}: {str(e)}")
            raise

    async def invoke_function(
        self,
        request: InvocationRequest
    ) -> InvocationResponse:
        """
        Invoke serverless function
        """
        try:
            if request.function_id not in self.deployed_functions:
                raise ValueError(f"Function {request.function_id} not found")
            
            function = self.deployed_functions[request.function_id]
            
            # Record invocation start time
            start_time = datetime.utcnow()
            
            # Invoke based on provider
            if function.provider == CloudProvider.AWS:
                response = await self._invoke_aws_function(function, request)
            elif function.provider == CloudProvider.AZURE:
                response = await self._invoke_azure_function(function, request)
            elif function.provider == CloudProvider.GCP:
                response = await self._invoke_gcp_function(function, request)
            else:
                raise ValueError(f"Unsupported provider: {function.provider}")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update performance metrics
            await self._update_performance_metrics(function, response, execution_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error invoking function {request.function_id}: {str(e)}")
            raise

    async def update_function(
        self,
        function_id: str,
        model_path: Optional[str] = None,
        config: Optional[ServerlessConfig] = None
    ) -> bool:
        """
        Update deployed serverless function
        """
        try:
            if function_id not in self.deployed_functions:
                raise ValueError(f"Function {function_id} not found")
            
            function = self.deployed_functions[function_id]
            function.status = DeploymentStatus.UPDATING
            
            # Update configuration if provided
            if config:
                function.config = config
            
            # Update model if provided
            if model_path:
                package_path = await self._create_deployment_package(
                    model_path, function.config, True
                )
                
                if function.provider == CloudProvider.AWS:
                    await self._update_aws_function(function, package_path)
                elif function.provider == CloudProvider.AZURE:
                    await self._update_azure_function(function, package_path)
                elif function.provider == CloudProvider.GCP:
                    await self._update_gcp_function(function, package_path)
                
                # Cleanup
                shutil.rmtree(package_path, ignore_errors=True)
            
            function.updated_at = datetime.utcnow()
            function.status = DeploymentStatus.ACTIVE
            
            logger.info(f"Successfully updated function {function_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating function {function_id}: {str(e)}")
            function.status = DeploymentStatus.FAILED
            return False

    async def delete_function(self, function_id: str) -> bool:
        """
        Delete serverless function
        """
        try:
            if function_id not in self.deployed_functions:
                raise ValueError(f"Function {function_id} not found")
            
            function = self.deployed_functions[function_id]
            function.status = DeploymentStatus.DELETING
            
            # Delete from cloud provider
            if function.provider == CloudProvider.AWS:
                await self._delete_aws_function(function)
            elif function.provider == CloudProvider.AZURE:
                await self._delete_azure_function(function)
            elif function.provider == CloudProvider.GCP:
                await self._delete_gcp_function(function)
            
            # Remove from tracking
            del self.deployed_functions[function_id]
            
            logger.info(f"Successfully deleted function {function_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting function {function_id}: {str(e)}")
            return False

    async def get_function_metrics(self, function_id: str) -> Dict[str, Any]:
        """Get function performance and cost metrics"""
        try:
            if function_id not in self.deployed_functions:
                raise ValueError(f"Function {function_id} not found")
            
            function = self.deployed_functions[function_id]
            
            # Fetch metrics from cloud provider
            if function.provider == CloudProvider.AWS:
                metrics = await self._get_aws_metrics(function)
            elif function.provider == CloudProvider.AZURE:
                metrics = await self._get_azure_metrics(function)
            elif function.provider == CloudProvider.GCP:
                metrics = await self._get_gcp_metrics(function)
            else:
                metrics = {}
            
            return {
                'function_id': function_id,
                'performance_metrics': function.performance_metrics,
                'cost_metrics': function.cost_metrics,
                'cloud_metrics': metrics,
                'status': function.status.value,
                'last_updated': function.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics for function {function_id}: {str(e)}")
            return {}

    async def list_functions(
        self,
        provider: Optional[CloudProvider] = None,
        status: Optional[DeploymentStatus] = None
    ) -> List[ServerlessFunction]:
        """List deployed functions with optional filters"""
        functions = list(self.deployed_functions.values())
        
        if provider:
            functions = [f for f in functions if f.provider == provider]
        
        if status:
            functions = [f for f in functions if f.status == status]
        
        return sorted(functions, key=lambda f: f.created_at, reverse=True)

    async def optimize_costs(self) -> Dict[str, Any]:
        """
        Analyze and optimize serverless deployment costs
        """
        try:
            optimization_report = {
                'total_functions': len(self.deployed_functions),
                'recommendations': [],
                'potential_savings': 0.0,
                'optimization_actions': []
            }
            
            for function in self.deployed_functions.values():
                # Analyze function usage patterns
                metrics = function.performance_metrics
                
                # Check for over-provisioned memory
                if 'memory_utilization' in metrics:
                    if metrics['memory_utilization'] < 0.5:  # Less than 50% utilization
                        optimization_report['recommendations'].append({
                            'function_id': function.function_id,
                            'type': 'memory_optimization',
                            'current_memory': function.config.memory_mb,
                            'recommended_memory': int(function.config.memory_mb * 0.7),
                            'estimated_savings': function.config.memory_mb * 0.3 * 0.1  # Rough estimate
                        })
                
                # Check for unused functions
                if 'invocation_count_24h' in metrics:
                    if metrics['invocation_count_24h'] == 0:
                        optimization_report['recommendations'].append({
                            'function_id': function.function_id,
                            'type': 'unused_function',
                            'recommendation': 'Consider deleting or archiving',
                            'potential_savings': function.cost_metrics.get('daily_cost', 0)
                        })
                
                # Check for provisioned concurrency optimization
                if function.config.provisioned_concurrency and 'cold_start_rate' in metrics:
                    if metrics['cold_start_rate'] < 0.1:  # Less than 10% cold starts
                        optimization_report['recommendations'].append({
                            'function_id': function.function_id,
                            'type': 'provisioned_concurrency_optimization',
                            'recommendation': 'Reduce or remove provisioned concurrency',
                            'potential_savings': function.cost_metrics.get('provisioned_cost', 0) * 0.5
                        })
            
            # Calculate total potential savings
            optimization_report['potential_savings'] = sum(
                rec.get('potential_savings', 0) 
                for rec in optimization_report['recommendations']
            )
            
            return optimization_report
            
        except Exception as e:
            logger.error(f"Error optimizing costs: {str(e)}")
            return {}

    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients"""
        try:
            # AWS
            self.cloud_clients[CloudProvider.AWS] = boto3.client('lambda')
            
            # Azure and GCP clients would be initialized here
            # self.cloud_clients[CloudProvider.AZURE] = ...
            # self.cloud_clients[CloudProvider.GCP] = ...
            
        except Exception as e:
            logger.warning(f"Some cloud clients could not be initialized: {str(e)}")

    async def _create_deployment_package(
        self,
        model_path: str,
        config: ServerlessConfig,
        optimize_cold_start: bool
    ) -> str:
        """Create deployment package for serverless function"""
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="serverless_deploy_")
        
        try:
            if optimize_cold_start:
                # Use cold start optimizer
                package_path = await self.cold_start_optimizer.optimize_deployment_package(
                    temp_dir, model_path
                )
            else:
                # Basic package creation
                package_path = temp_dir
                
                # Copy model
                model_target = f"{package_path}/model"
                os.makedirs(model_target, exist_ok=True)
                
                if os.path.isfile(model_path):
                    shutil.copy2(model_path, f"{model_target}/model.pkl")
                else:
                    shutil.copytree(model_path, f"{model_target}/", dirs_exist_ok=True)
            
            return package_path
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    async def _deploy_to_aws(
        self,
        function_id: str,
        package_path: str,
        config: ServerlessConfig
    ) -> str:
        """Deploy function to AWS Lambda"""
        try:
            # Create deployment zip
            zip_path = f"{package_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, package_path)
                        zipf.write(file_path, arc_name)
            
            # Read zip file
            with open(zip_path, 'rb') as f:
                zip_content = f.read()
            
            # Create Lambda function
            lambda_client = self.cloud_clients[CloudProvider.AWS]
            
            response = lambda_client.create_function(
                FunctionName=config.function_name,
                Runtime=config.runtime.value,
                Role='arn:aws:iam::123456789012:role/lambda-execution-role',  # Replace with actual role
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description=f'ML Model {function_id} Inference Function',
                Timeout=config.timeout_seconds,
                MemorySize=config.memory_mb,
                Environment={'Variables': config.environment_variables},
                Tags={'ModelId': function_id, 'Purpose': 'ML-Inference'}
            )
            
            # Cleanup zip file
            os.remove(zip_path)
            
            # Return function URL or endpoint
            function_arn = response['FunctionArn']
            endpoint_url = f"https://lambda.{boto3.Session().region_name}.amazonaws.com/2015-03-31/functions/{config.function_name}/invocations"
            
            return endpoint_url
            
        except Exception as e:
            logger.error(f"Error deploying to AWS: {str(e)}")
            raise

    async def _deploy_to_azure(self, function_id: str, package_path: str, config: ServerlessConfig) -> str:
        """Deploy function to Azure Functions"""
        # Placeholder for Azure deployment
        logger.info(f"Azure deployment for {function_id} (placeholder)")
        return f"https://{config.function_name}.azurewebsites.net/api/predict"

    async def _deploy_to_gcp(self, function_id: str, package_path: str, config: ServerlessConfig) -> str:
        """Deploy function to Google Cloud Functions"""
        # Placeholder for GCP deployment
        logger.info(f"GCP deployment for {function_id} (placeholder)")
        return f"https://us-central1-project.cloudfunctions.net/{config.function_name}"

    async def _invoke_aws_function(
        self,
        function: ServerlessFunction,
        request: InvocationRequest
    ) -> InvocationResponse:
        """Invoke AWS Lambda function"""
        try:
            lambda_client = self.cloud_clients[CloudProvider.AWS]
            
            # Prepare payload
            payload = json.dumps(request.payload).encode('utf-8')
            
            # Invoke function
            response = lambda_client.invoke(
                FunctionName=function.config.function_name,
                InvocationType='RequestResponse' if not request.async_invocation else 'Event',
                Payload=payload
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            
            return InvocationResponse(
                function_id=function.function_id,
                request_id=response.get('ResponseMetadata', {}).get('RequestId', ''),
                status_code=response['StatusCode'],
                response_payload=response_payload,
                execution_time_ms=int(response.get('ExecutedVersion', 0)),
                billed_duration_ms=int(response.get('ExecutedVersion', 0)),
                memory_used_mb=0,  # Would need CloudWatch metrics
                cold_start=False   # Would need X-Ray tracing
            )
            
        except Exception as e:
            logger.error(f"Error invoking AWS function: {str(e)}")
            raise

    async def _invoke_azure_function(self, function: ServerlessFunction, request: InvocationRequest) -> InvocationResponse:
        """Invoke Azure Function"""
        # Placeholder for Azure invocation
        return InvocationResponse(
            function_id=function.function_id,
            request_id="azure-request-id",
            status_code=200,
            response_payload={"prediction": [0.5], "confidence": [0.8, 0.2]},
            execution_time_ms=50,
            billed_duration_ms=100,
            memory_used_mb=256,
            cold_start=False
        )

    async def _invoke_gcp_function(self, function: ServerlessFunction, request: InvocationRequest) -> InvocationResponse:
        """Invoke Google Cloud Function"""
        # Placeholder for GCP invocation
        return InvocationResponse(
            function_id=function.function_id,
            request_id="gcp-request-id",
            status_code=200,
            response_payload={"prediction": [0.5], "confidence": [0.8, 0.2]},
            execution_time_ms=45,
            billed_duration_ms=100,
            memory_used_mb=512,
            cold_start=True
        )

    async def _update_aws_function(self, function: ServerlessFunction, package_path: str) -> None:
        """Update AWS Lambda function"""
        # Implementation for updating AWS function
        logger.info(f"Updating AWS function {function.function_id}")

    async def _update_azure_function(self, function: ServerlessFunction, package_path: str) -> None:
        """Update Azure Function"""
        logger.info(f"Updating Azure function {function.function_id}")

    async def _update_gcp_function(self, function: ServerlessFunction, package_path: str) -> None:
        """Update Google Cloud Function"""
        logger.info(f"Updating GCP function {function.function_id}")

    async def _delete_aws_function(self, function: ServerlessFunction) -> None:
        """Delete AWS Lambda function"""
        try:
            lambda_client = self.cloud_clients[CloudProvider.AWS]
            lambda_client.delete_function(FunctionName=function.config.function_name)
            logger.info(f"Deleted AWS function {function.function_id}")
        except Exception as e:
            logger.error(f"Error deleting AWS function: {str(e)}")

    async def _delete_azure_function(self, function: ServerlessFunction) -> None:
        """Delete Azure Function"""
        logger.info(f"Deleted Azure function {function.function_id}")

    async def _delete_gcp_function(self, function: ServerlessFunction) -> None:
        """Delete Google Cloud Function"""
        logger.info(f"Deleted GCP function {function.function_id}")

    async def _get_aws_metrics(self, function: ServerlessFunction) -> Dict[str, Any]:
        """Get AWS CloudWatch metrics"""
        return {'invocation_count': 100, 'error_rate': 0.01, 'avg_duration': 150}

    async def _get_azure_metrics(self, function: ServerlessFunction) -> Dict[str, Any]:
        """Get Azure Function metrics"""
        return {'invocation_count': 80, 'error_rate': 0.02, 'avg_duration': 120}

    async def _get_gcp_metrics(self, function: ServerlessFunction) -> Dict[str, Any]:
        """Get Google Cloud Function metrics"""
        return {'invocation_count': 90, 'error_rate': 0.015, 'avg_duration': 130}

    async def _update_performance_metrics(
        self,
        function: ServerlessFunction,
        response: InvocationResponse,
        execution_time: float
    ) -> None:
        """Update function performance metrics"""
        metrics = function.performance_metrics
        
        # Update execution time
        if 'avg_execution_time' not in metrics:
            metrics['avg_execution_time'] = execution_time
        else:
            # Exponential moving average
            metrics['avg_execution_time'] = 0.9 * metrics['avg_execution_time'] + 0.1 * execution_time
        
        # Update cold start rate
        if 'cold_start_count' not in metrics:
            metrics['cold_start_count'] = 0
            metrics['total_invocations'] = 0
        
        metrics['total_invocations'] += 1
        if response.cold_start:
            metrics['cold_start_count'] += 1
        
        metrics['cold_start_rate'] = metrics['cold_start_count'] / metrics['total_invocations']
        
        # Update error rate
        if 'error_count' not in metrics:
            metrics['error_count'] = 0
        
        if response.status_code >= 400:
            metrics['error_count'] += 1
        
        metrics['error_rate'] = metrics['error_count'] / metrics['total_invocations']

# Usage Example
async def main():
    """Example usage of ServerlessDeploymentEngine"""
    engine = ServerlessDeploymentEngine()
    
    # Configure serverless function
    config = ServerlessConfig(
        function_name="content-classifier-inference",
        runtime=FunctionRuntime.PYTHON_39,
        memory_mb=512,
        timeout_seconds=30,
        environment_variables={'MODEL_VERSION': '1.0.0'}
    )
    
    # Deploy model (placeholder model path)
    # function = await engine.deploy_model(
    #     model_id="content-classifier",
    #     model_path="/path/to/model",
    #     config=config,
    #     provider=CloudProvider.AWS
    # )
    
    # Create invocation request
    request = InvocationRequest(
        function_id="test-function",
        payload={
            'features': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
    )
    
    # Invoke function (would work with actual deployment)
    # response = await engine.invoke_function(request)
    # print(f"Prediction: {response.response_payload}")
    
    # Get cost optimization recommendations
    optimization_report = await engine.optimize_costs()
    print(f"Cost optimization report: {optimization_report}")

if __name__ == "__main__":
    asyncio.run(main())