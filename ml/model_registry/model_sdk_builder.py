#!/usr/bin/env python3
"""
🚀 **Model SDK Builder - Enterprise ML SDK Generation**

**Author:** Fahed Mlaiel (mlaiel@live.de) - Lead Dev IA  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: LEAD DEV IA - SDK ORCHESTRATION MASTERY**

Enterprise-grade SDK generation for ML models across multiple programming languages
with seamless integration, authentication, and creator-specific optimization.
"""

import os
import json
import asyncio
import shutil
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import subprocess

from jinja2 import Environment, FileSystemLoader
import yaml

class SDKLanguage(Enum):
    """Supported SDK languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"

class CreatorType(Enum):
    """Creator specialization for SDK generation"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

@dataclass
class SDKConfig:
    """Configuration for SDK generation"""
    language: SDKLanguage
    package_name: str
    version: str
    author: str
    description: str
    repository_url: str
    license: str = "Proprietary"
    dependencies: List[str] = None
    creator_specific: bool = False

@dataclass
class SDKMethod:
    """SDK method specification"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    return_type: str
    example_code: str
    async_method: bool = False
    creator_specific: bool = False

@dataclass
class SDKClass:
    """SDK class specification"""
    name: str
    description: str
    methods: List[SDKMethod]
    properties: List[Dict[str, Any]]
    inheritance: Optional[str] = None

@dataclass
class SDKSpec:
    """Complete SDK specification"""
    model_id: str
    model_name: str
    sdk_configs: List[SDKConfig]
    classes: List[SDKClass]
    authentication: Dict[str, Any]
    base_url: str
    examples: List[Dict[str, Any]]
    documentation: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ModelSDKBuilder:
    """
    🚀 **Enterprise Model SDK Builder**
    
    **Lead Dev IA Role:** Multi-language SDK generation with enterprise standards
    - Multi-language support (Python, JS, Java, C#, Go, etc.)
    - Authentication and authorization integration
    - Creator-specific SDK optimization
    - Package management integration
    - Documentation generation
    - CI/CD integration for SDK releases
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_env = Environment(
            loader=FileSystemLoader(config.get('template_dir', 'templates/sdk'))
        )
        self.output_dir = Path(config.get('output_dir', 'generated_sdks'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Language-specific configurations
        self.language_configs = {
            SDKLanguage.PYTHON: {
                'file_extension': '.py',
                'package_manager': 'pip',
                'test_framework': 'pytest',
                'doc_format': 'sphinx'
            },
            SDKLanguage.JAVASCRIPT: {
                'file_extension': '.js',
                'package_manager': 'npm',
                'test_framework': 'jest',
                'doc_format': 'jsdoc'
            },
            SDKLanguage.TYPESCRIPT: {
                'file_extension': '.ts',
                'package_manager': 'npm',
                'test_framework': 'jest',
                'doc_format': 'typedoc'
            },
            SDKLanguage.JAVA: {
                'file_extension': '.java',
                'package_manager': 'maven',
                'test_framework': 'junit',
                'doc_format': 'javadoc'
            },
            SDKLanguage.CSHARP: {
                'file_extension': '.cs',
                'package_manager': 'nuget',
                'test_framework': 'nunit',
                'doc_format': 'xmldoc'
            },
            SDKLanguage.GO: {
                'file_extension': '.go',
                'package_manager': 'go mod',
                'test_framework': 'go test',
                'doc_format': 'godoc'
            }
        }
        
        # Creator-specific configurations
        self.creator_configs = {
            CreatorType.MUSICIAN: {
                'additional_methods': ['analyzeAudio', 'extractFeatures', 'generateRecommendations'],
                'specialized_types': ['AudioData', 'MusicAnalysis', 'GenreClassification'],
                'examples': ['audio_classification', 'tempo_detection', 'mood_analysis']
            },
            CreatorType.PHOTOGRAPHER: {
                'additional_methods': ['analyzeAesthetics', 'enhanceImage', 'styleTransfer'],
                'specialized_types': ['ImageData', 'AestheticAnalysis', 'StyleMetrics'],
                'examples': ['aesthetic_scoring', 'composition_analysis', 'style_classification']
            },
            CreatorType.BLOGGER: {
                'additional_methods': ['optimizeContent', 'analyzeSEO', 'generateSuggestions'],
                'specialized_types': ['ContentData', 'SEOAnalysis', 'OptimizationSuggestions'],
                'examples': ['content_optimization', 'readability_analysis', 'seo_suggestions']
            }
        }
    
    async def generate_sdk_for_model(
        self,
        model_id: str,
        api_spec: Dict[str, Any],
        languages: List[SDKLanguage],
        creator_type: CreatorType = CreatorType.GENERIC
    ) -> SDKSpec:
        """
        Generate complete SDK specification for a model
        
        **Lead Dev IA Expertise:**
        - Multi-language SDK generation
        - API specification parsing
        - Creator-specific optimization
        """
        # Generate SDK configurations for each language
        sdk_configs = []
        for language in languages:
            config = await self._generate_sdk_config(
                model_id, api_spec, language, creator_type
            )
            sdk_configs.append(config)
        
        # Generate SDK classes and methods
        classes = await self._generate_sdk_classes(api_spec, creator_type)
        
        # Generate examples
        examples = await self._generate_examples(api_spec, creator_type)
        
        # Create SDK specification
        sdk_spec = SDKSpec(
            model_id=model_id,
            model_name=api_spec.get('info', {}).get('title', f'Model {model_id}'),
            sdk_configs=sdk_configs,
            classes=classes,
            authentication=api_spec.get('components', {}).get('securitySchemes', {}),
            base_url=api_spec.get('servers', [{}])[0].get('url', ''),
            examples=examples,
            documentation={
                'generated_at': datetime.utcnow().isoformat(),
                'generator_version': '1.0.0',
                'api_version': api_spec.get('info', {}).get('version', '1.0.0')
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return sdk_spec
    
    async def _generate_sdk_config(
        self,
        model_id: str,
        api_spec: Dict[str, Any],
        language: SDKLanguage,
        creator_type: CreatorType
    ) -> SDKConfig:
        """Generate SDK configuration for specific language"""
        package_name = self._generate_package_name(model_id, language, creator_type)
        
        dependencies = self._get_language_dependencies(language)
        if creator_type != CreatorType.GENERIC:
            dependencies.extend(self._get_creator_dependencies(language, creator_type))
        
        return SDKConfig(
            language=language,
            package_name=package_name,
            version=api_spec.get('info', {}).get('version', '1.0.0'),
            author="Fahed Mlaiel <mlaiel@live.de>",
            description=f"SDK for {api_spec.get('info', {}).get('title', model_id)} - {creator_type.value} optimized",
            repository_url=f"https://github.com/ainflue/{package_name}",
            dependencies=dependencies,
            creator_specific=creator_type != CreatorType.GENERIC
        )
    
    def _generate_package_name(
        self,
        model_id: str,
        language: SDKLanguage,
        creator_type: CreatorType
    ) -> str:
        """Generate language-appropriate package name"""
        base_name = model_id.replace('-', '_').lower()
        
        if creator_type != CreatorType.GENERIC:
            base_name = f"{creator_type.value}_{base_name}"
        
        if language == SDKLanguage.PYTHON:
            return f"ainflue_{base_name}"
        elif language == SDKLanguage.JAVASCRIPT or language == SDKLanguage.TYPESCRIPT:
            return f"@ainflue/{base_name.replace('_', '-')}"
        elif language == SDKLanguage.JAVA:
            return f"com.ainflue.{base_name}"
        elif language == SDKLanguage.CSHARP:
            return f"Ainflue.{base_name.title().replace('_', '')}"
        elif language == SDKLanguage.GO:
            return f"github.com/ainflue/{base_name.replace('_', '-')}"
        else:
            return f"ainflue-{base_name}"
    
    def _get_language_dependencies(self, language: SDKLanguage) -> List[str]:
        """Get standard dependencies for each language"""
        dependencies = {
            SDKLanguage.PYTHON: ["requests", "pydantic", "typing-extensions"],
            SDKLanguage.JAVASCRIPT: ["axios", "form-data"],
            SDKLanguage.TYPESCRIPT: ["axios", "form-data", "@types/node"],
            SDKLanguage.JAVA: ["com.fasterxml.jackson.core:jackson-core", "okhttp3:okhttp"],
            SDKLanguage.CSHARP: ["Newtonsoft.Json", "System.Net.Http"],
            SDKLanguage.GO: ["github.com/go-resty/resty/v2"]
        }
        return dependencies.get(language, [])
    
    def _get_creator_dependencies(self, language: SDKLanguage, creator_type: CreatorType) -> List[str]:
        """Get creator-specific dependencies"""
        creator_deps = {
            CreatorType.MUSICIAN: {
                SDKLanguage.PYTHON: ["librosa", "soundfile", "pydub"],
                SDKLanguage.JAVASCRIPT: ["node-wav", "fluent-ffmpeg"]
            },
            CreatorType.PHOTOGRAPHER: {
                SDKLanguage.PYTHON: ["Pillow", "opencv-python"],
                SDKLanguage.JAVASCRIPT: ["sharp", "jimp"]
            },
            CreatorType.BLOGGER: {
                SDKLanguage.PYTHON: ["beautifulsoup4", "markdown"],
                SDKLanguage.JAVASCRIPT: ["cheerio", "marked"]
            }
        }
        return creator_deps.get(creator_type, {}).get(language, [])
    
    async def _generate_sdk_classes(self, api_spec: Dict[str, Any], creator_type: CreatorType) -> List[SDKClass]:
        """Generate SDK classes based on API specification"""
        classes = []
        
        # Main client class
        client_class = await self._generate_client_class(api_spec, creator_type)
        classes.append(client_class)
        
        # Model-specific classes
        if creator_type != CreatorType.GENERIC:
            specialized_class = await self._generate_specialized_class(api_spec, creator_type)
            classes.append(specialized_class)
        
        # Data model classes
        data_classes = await self._generate_data_model_classes(api_spec)
        classes.extend(data_classes)
        
        return classes
    
    async def _generate_client_class(self, api_spec: Dict[str, Any], creator_type: CreatorType) -> SDKClass:
        """Generate main client class"""
        methods = []
        
        # Extract methods from API paths
        for path, path_item in api_spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete']:
                    sdk_method = await self._generate_sdk_method(
                        path, method, operation, creator_type
                    )
                    methods.append(sdk_method)
        
        return SDKClass(
            name="ModelClient",
            description=f"Main client class for {api_spec.get('info', {}).get('title', 'Model API')}",
            methods=methods,
            properties=[
                {"name": "base_url", "type": "str", "description": "API base URL"},
                {"name": "api_key", "type": "str", "description": "Authentication API key"},
                {"name": "timeout", "type": "int", "description": "Request timeout in seconds"}
            ]
        )
    
    async def _generate_specialized_class(self, api_spec: Dict[str, Any], creator_type: CreatorType) -> SDKClass:
        """Generate creator-specific specialized class"""
        creator_config = self.creator_configs.get(creator_type, {})
        
        methods = []
        for method_name in creator_config.get('additional_methods', []):
            method = SDKMethod(
                name=method_name,
                description=f"Specialized {method_name} method for {creator_type.value}s",
                parameters=[
                    {"name": "data", "type": "Any", "description": "Input data"},
                    {"name": "options", "type": "Dict", "description": "Processing options", "optional": True}
                ],
                return_type="Dict[str, Any]",
                example_code=f"result = client.{method_name}(data)",
                async_method=True,
                creator_specific=True
            )
            methods.append(method)
        
        class_name = f"{creator_type.value.title()}Client"
        return SDKClass(
            name=class_name,
            description=f"Specialized client for {creator_type.value}s",
            methods=methods,
            properties=[],
            inheritance="ModelClient"
        )
    
    async def _generate_sdk_method(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any],
        creator_type: CreatorType
    ) -> SDKMethod:
        """Generate SDK method from API operation"""
        method_name = operation.get('operationId', path.replace('/', '_').strip('_'))
        
        # Extract parameters
        parameters = []
        
        # Add path parameters
        if '{' in path:
            import re
            path_params = re.findall(r'\{(\w+)\}', path)
            for param in path_params:
                parameters.append({
                    "name": param,
                    "type": "str",
                    "description": f"Path parameter: {param}"
                })
        
        # Add request body parameters
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            json_content = content.get('application/json', {})
            if json_content:
                parameters.append({
                    "name": "data",
                    "type": "Dict[str, Any]",
                    "description": "Request data"
                })
        
        # Add optional parameters
        parameters.append({
            "name": "timeout", 
            "type": "Optional[int]",
            "description": "Request timeout",
            "optional": True
        })
        
        # Determine return type
        responses = operation.get('responses', {})
        success_response = responses.get('200', {})
        return_type = "Dict[str, Any]"  # Default
        
        # Generate example code
        example_code = self._generate_method_example(method_name, parameters, creator_type)
        
        return SDKMethod(
            name=method_name,
            description=operation.get('summary', f"Call {method_name} endpoint"),
            parameters=parameters,
            return_type=return_type,
            example_code=example_code,
            async_method=True
        )
    
    def _generate_method_example(
        self,
        method_name: str,
        parameters: List[Dict[str, Any]],
        creator_type: CreatorType
    ) -> str:
        """Generate example code for method"""
        # Build parameter list
        param_names = [p['name'] for p in parameters if not p.get('optional', False)]
        optional_params = [p['name'] for p in parameters if p.get('optional', False)]
        
        all_params = param_names + [f"{p}=None" for p in optional_params]
        param_str = ", ".join(all_params)
        
        example = f"""
# Basic usage
result = await client.{method_name}({param_str})
print(result)

# With error handling
try:
    result = await client.{method_name}({param_str})
    print(f"Success: {{result}}")
except Exception as e:
    print(f"Error: {{e}}")
"""
        
        return example.strip()
    
    async def _generate_data_model_classes(self, api_spec: Dict[str, Any]) -> List[SDKClass]:
        """Generate data model classes from API schemas"""
        classes = []
        
        schemas = api_spec.get('components', {}).get('schemas', {})
        for schema_name, schema_def in schemas.items():
            if schema_def.get('type') == 'object':
                properties = []
                for prop_name, prop_def in schema_def.get('properties', {}).items():
                    properties.append({
                        "name": prop_name,
                        "type": self._map_openapi_type_to_language_type(prop_def.get('type')),
                        "description": prop_def.get('description', '')
                    })
                
                data_class = SDKClass(
                    name=schema_name,
                    description=schema_def.get('description', f"Data model for {schema_name}"),
                    methods=[],
                    properties=properties
                )
                classes.append(data_class)
        
        return classes
    
    def _map_openapi_type_to_language_type(self, openapi_type: str) -> str:
        """Map OpenAPI types to language-specific types"""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict'
        }
        return type_mapping.get(openapi_type, 'Any')
    
    async def _generate_examples(self, api_spec: Dict[str, Any], creator_type: CreatorType) -> List[Dict[str, Any]]:
        """Generate usage examples"""
        examples = []
        
        # Basic example
        basic_example = {
            "name": "basic_usage",
            "title": "Basic Usage Example",
            "description": "Basic usage of the SDK",
            "code": """
from ainflue_sdk import ModelClient

# Initialize client
client = ModelClient(
    api_key="your_api_key",
    base_url="https://api.ainflue.com"
)

# Make a prediction
result = await client.predict({"text": "Hello world"})
print(result)
"""
        }
        examples.append(basic_example)
        
        # Creator-specific examples
        if creator_type != CreatorType.GENERIC:
            creator_config = self.creator_configs.get(creator_type, {})
            for example_name in creator_config.get('examples', []):
                example = await self._generate_creator_example(example_name, creator_type)
                examples.append(example)
        
        return examples
    
    async def _generate_creator_example(self, example_name: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Generate creator-specific example"""
        examples_map = {
            CreatorType.MUSICIAN: {
                "audio_classification": {
                    "title": "Audio Classification Example",
                    "description": "Classify audio genre and mood",
                    "code": """
from ainflue_sdk import MusicianClient
import base64

# Initialize musician client
client = MusicianClient(api_key="your_api_key")

# Load audio file
with open("song.mp3", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

# Analyze audio
result = await client.analyzeAudio({
    "audio_data": audio_data,
    "analysis_type": "genre"
})

print(f"Genre: {result['genre']}")
print(f"Confidence: {result['confidence']}")
"""
                }
            },
            CreatorType.PHOTOGRAPHER: {
                "aesthetic_scoring": {
                    "title": "Aesthetic Scoring Example",
                    "description": "Analyze image aesthetics",
                    "code": """
from ainflue_sdk import PhotographerClient
import base64

# Initialize photographer client
client = PhotographerClient(api_key="your_api_key")

# Load image
with open("photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Analyze aesthetics
result = await client.analyzeAesthetics({
    "image_data": image_data,
    "analysis_aspects": ["composition", "lighting", "color"]
})

print(f"Aesthetic Score: {result['aesthetic_score']}")
print(f"Composition: {result['composition_rating']}")
"""
                }
            },
            CreatorType.BLOGGER: {
                "content_optimization": {
                    "title": "Content Optimization Example",
                    "description": "Optimize blog content for SEO",
                    "code": """
from ainflue_sdk import BloggerClient

# Initialize blogger client
client = BloggerClient(api_key="your_api_key")

# Optimize content
result = await client.optimizeContent({
    "content": "Your blog post content here...",
    "target_audience": "tech professionals",
    "seo_focus": "machine learning",
    "optimization_goals": ["readability", "seo", "engagement"]
})

print(f"SEO Score: {result['seo_score']}")
print(f"Readability Score: {result['readability_score']}")
print("Suggestions:", result['optimization_suggestions'])
"""
                }
            }
        }
        
        creator_examples = examples_map.get(creator_type, {})
        example_data = creator_examples.get(example_name, {})
        
        return {
            "name": example_name,
            "title": example_data.get("title", example_name.title()),
            "description": example_data.get("description", ""),
            "code": example_data.get("code", "").strip()
        }
    
    async def generate_sdk_code(self, sdk_spec: SDKSpec, language: SDKLanguage) -> Dict[str, str]:
        """
        Generate SDK code for specific language
        
        **Lead Dev IA Excellence:** Multi-language code generation
        """
        # Get SDK config for this language
        sdk_config = next(
            (config for config in sdk_spec.sdk_configs if config.language == language),
            None
        )
        
        if not sdk_config:
            raise ValueError(f"No SDK config found for {language}")
        
        generated_files = {}
        
        # Generate main client file
        client_template = f"{language.value}_client.j2"
        try:
            template = self.template_env.get_template(client_template)
            client_code = template.render(
                sdk_spec=sdk_spec,
                sdk_config=sdk_config,
                classes=sdk_spec.classes,
                examples=sdk_spec.examples
            )
            
            file_ext = self.language_configs[language]['file_extension']
            generated_files[f"client{file_ext}"] = client_code
        except Exception as e:
            # Fallback to generic template
            generated_files[f"client{self.language_configs[language]['file_extension']}"] = \
                await self._generate_generic_client(sdk_spec, sdk_config, language)
        
        # Generate package configuration files
        package_files = await self._generate_package_files(sdk_config, language)
        generated_files.update(package_files)
        
        # Generate examples
        example_files = await self._generate_example_files(sdk_spec.examples, language)
        generated_files.update(example_files)
        
        # Generate tests
        test_files = await self._generate_test_files(sdk_spec, language)
        generated_files.update(test_files)
        
        return generated_files
    
    async def _generate_generic_client(
        self, 
        sdk_spec: SDKSpec, 
        sdk_config: SDKConfig, 
        language: SDKLanguage
    ) -> str:
        """Generate generic client code when no template is available"""
        if language == SDKLanguage.PYTHON:
            return await self._generate_python_client(sdk_spec, sdk_config)
        elif language == SDKLanguage.JAVASCRIPT:
            return await self._generate_javascript_client(sdk_spec, sdk_config)
        elif language == SDKLanguage.TYPESCRIPT:
            return await self._generate_typescript_client(sdk_spec, sdk_config)
        else:
            return f"# SDK for {sdk_config.package_name}\n# Language: {language.value}\n# TODO: Implement client"
    
    async def _generate_python_client(self, sdk_spec: SDKSpec, sdk_config: SDKConfig) -> str:
        """Generate Python client code"""
        return f'''"""
{sdk_config.description}

Generated by Ainflue SDK Builder
Author: {sdk_config.author}
Version: {sdk_config.version}
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import base64


class ModelClient:
    """Main client for {sdk_spec.model_name} API"""
    
    def __init__(self, api_key: str, base_url: str = "{sdk_spec.base_url}", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={{"Authorization": f"Bearer {{self.api_key}}"}}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def predict(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a prediction using the model"""
        payload = {{"data": data}}
        if options:
            payload["options"] = options
        
        async with self.session.post(f"{{self.base_url}}/predict", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def batch_predict(self, batch_data: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make batch predictions"""
        payload = {{"batch_data": batch_data}}
        if options:
            payload["options"] = options
        
        async with self.session.post(f"{{self.base_url}}/batch-predict", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        async with self.session.get(f"{{self.base_url}}/info") as response:
            response.raise_for_status()
            return await response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check model service health"""
        async with self.session.get(f"{{self.base_url}}/health") as response:
            response.raise_for_status()
            return await response.json()


# Usage example
async def main():
    async with ModelClient(api_key="your_api_key") as client:
        # Get model info
        info = await client.get_model_info()
        print(f"Model: {{info}}")
        
        # Make prediction
        result = await client.predict({{"text": "Hello world"}})
        print(f"Prediction: {{result}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    async def _generate_package_files(self, sdk_config: SDKConfig, language: SDKLanguage) -> Dict[str, str]:
        """Generate package configuration files"""
        files = {}
        
        if language == SDKLanguage.PYTHON:
            # setup.py
            files["setup.py"] = f'''from setuptools import setup, find_packages

setup(
    name="{sdk_config.package_name}",
    version="{sdk_config.version}",
    author="{sdk_config.author}",
    description="{sdk_config.description}",
    packages=find_packages(),
    install_requires={sdk_config.dependencies or []},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
            
            # requirements.txt
            files["requirements.txt"] = "\\n".join(sdk_config.dependencies or [])
            
            # __init__.py
            files["__init__.py"] = f'''"""
{sdk_config.description}
"""

__version__ = "{sdk_config.version}"
__author__ = "{sdk_config.author}"

from .client import ModelClient

__all__ = ["ModelClient"]
'''
        
        elif language == SDKLanguage.JAVASCRIPT or language == SDKLanguage.TYPESCRIPT:
            # package.json
            files["package.json"] = json.dumps({
                "name": sdk_config.package_name,
                "version": sdk_config.version,
                "description": sdk_config.description,
                "main": "index.js" if language == SDKLanguage.JAVASCRIPT else "dist/index.js",
                "types": "dist/index.d.ts" if language == SDKLanguage.TYPESCRIPT else None,
                "scripts": {
                    "build": "tsc" if language == SDKLanguage.TYPESCRIPT else "echo 'No build needed'",
                    "test": "jest",
                    "prepublishOnly": "npm run build" if language == SDKLanguage.TYPESCRIPT else "echo 'No build needed'"
                },
                "dependencies": {dep: "latest" for dep in (sdk_config.dependencies or [])},
                "devDependencies": {
                    "jest": "^29.0.0",
                    "@types/node": "^18.0.0" if language == SDKLanguage.TYPESCRIPT else None,
                    "typescript": "^4.8.0" if language == SDKLanguage.TYPESCRIPT else None
                },
                "keywords": ["ainflue", "ml", "api", "sdk"],
                "author": sdk_config.author,
                "license": sdk_config.license
            }, indent=2)
        
        return {k: v for k, v in files.items() if v is not None}
    
    async def _generate_example_files(self, examples: List[Dict[str, Any]], language: SDKLanguage) -> Dict[str, str]:
        """Generate example files"""
        files = {}
        
        for example in examples:
            file_ext = self.language_configs[language]['file_extension']
            filename = f"examples/{example['name']}{file_ext}"
            
            # Add language-specific header comments
            if language == SDKLanguage.PYTHON:
                header = f'"""\n{example["title"]}\n\n{example["description"]}\n"""\n\n'
            elif language in [SDKLanguage.JAVASCRIPT, SDKLanguage.TYPESCRIPT]:
                header = f'/*\n * {example["title"]}\n * \n * {example["description"]}\n */\n\n'
            else:
                header = f'// {example["title"]}\n// {example["description"]}\n\n'
            
            files[filename] = header + example["code"]
        
        return files
    
    async def _generate_test_files(self, sdk_spec: SDKSpec, language: SDKLanguage) -> Dict[str, str]:
        """Generate test files"""
        files = {}
        
        if language == SDKLanguage.PYTHON:
            files["tests/test_client.py"] = f'''"""
Test suite for {sdk_spec.model_name} SDK
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from {sdk_spec.sdk_configs[0].package_name.replace("-", "_")} import ModelClient


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization"""
    client = ModelClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "{sdk_spec.base_url}"


@pytest.mark.asyncio
async def test_predict():
    """Test prediction functionality"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.json.return_value = {{"prediction": "test_result"}}
        mock_session.return_value.post.return_value.__aenter__.return_value = mock_response
        
        async with ModelClient(api_key="test_key") as client:
            result = await client.predict({{"text": "test"}})
            assert result == {{"prediction": "test_result"}}


@pytest.mark.asyncio
async def test_health_check():
    """Test health check functionality"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.json.return_value = {{"status": "healthy"}}
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_response
        
        async with ModelClient(api_key="test_key") as client:
            result = await client.health_check()
            assert result == {{"status": "healthy"}}
'''
        
        return files
    
    async def save_generated_sdk(
        self, 
        sdk_spec: SDKSpec, 
        language: SDKLanguage,
        include_docs: bool = True
    ) -> Dict[str, Path]:
        """Save generated SDK artifacts"""
        output_paths = {}
        
        sdk_dir = self.output_dir / sdk_spec.model_id / language.value
        sdk_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate and save SDK code
        sdk_files = await self.generate_sdk_code(sdk_spec, language)
        
        for filename, content in sdk_files.items():
            file_path = sdk_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            output_paths[filename] = file_path
        
        # Save SDK specification
        spec_path = sdk_dir / 'sdk_spec.json'
        with open(spec_path, 'w') as f:
            json.dump(asdict(sdk_spec), f, indent=2, default=str)
        output_paths['spec'] = spec_path
        
        # Generate documentation
        if include_docs:
            docs_path = await self._generate_documentation(sdk_spec, language, sdk_dir)
            output_paths['docs'] = docs_path
        
        return output_paths
    
    async def _generate_documentation(
        self, 
        sdk_spec: SDKSpec, 
        language: SDKLanguage, 
        output_dir: Path
    ) -> Path:
        """Generate SDK documentation"""
        docs_dir = output_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        # Generate README
        readme_content = f"""# {sdk_spec.model_name} SDK - {language.value.title()}

{next(config for config in sdk_spec.sdk_configs if config.language == language).description}

## Installation

```bash
{self._get_install_command(language, next(config for config in sdk_spec.sdk_configs if config.language == language).package_name)}
```

## Quick Start

```{language.value}
{sdk_spec.examples[0]['code'] if sdk_spec.examples else '// Example coming soon'}
```

## API Reference

### ModelClient

Main client class for interacting with the {sdk_spec.model_name} API.

{self._generate_api_docs(sdk_spec.classes)}

## Examples

{self._generate_example_docs(sdk_spec.examples)}

## License

{next(config for config in sdk_spec.sdk_configs if config.language == language).license}

## Support

For support, please contact: mlaiel@live.de
"""
        
        readme_path = docs_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        return readme_path
    
    def _get_install_command(self, language: SDKLanguage, package_name: str) -> str:
        """Get installation command for language"""
        commands = {
            SDKLanguage.PYTHON: f"pip install {package_name}",
            SDKLanguage.JAVASCRIPT: f"npm install {package_name}",
            SDKLanguage.TYPESCRIPT: f"npm install {package_name}",
            SDKLanguage.JAVA: f"# Add to pom.xml or gradle",
            SDKLanguage.CSHARP: f"dotnet add package {package_name}",
            SDKLanguage.GO: f"go get {package_name}"
        }
        return commands.get(language, f"# Install {package_name}")
    
    def _generate_api_docs(self, classes: List[SDKClass]) -> str:
        """Generate API documentation"""
        docs = ""
        for cls in classes:
            docs += f"\n#### {cls.name}\n\n{cls.description}\n\n"
            
            if cls.methods:
                docs += "**Methods:**\n\n"
                for method in cls.methods:
                    params = ", ".join([f"{p['name']}: {p['type']}" for p in method.parameters])
                    docs += f"- `{method.name}({params}) -> {method.return_type}`\n"
                    docs += f"  {method.description}\n\n"
        
        return docs
    
    def _generate_example_docs(self, examples: List[Dict[str, Any]]) -> str:
        """Generate example documentation"""
        docs = ""
        for example in examples:
            docs += f"\n### {example['title']}\n\n{example['description']}\n\n"
            docs += f"```python\n{example['code']}\n```\n\n"
        
        return docs

# Usage example
async def main():
    """Example usage of ModelSDKBuilder"""
    config = {
        'output_dir': 'generated_sdks',
        'template_dir': 'templates/sdk'
    }
    
    builder = ModelSDKBuilder(config)
    
    # Mock API specification
    api_spec = {
        "info": {"title": "Musician Audio Classifier", "version": "1.0.0"},
        "servers": [{"url": "https://api.ainflue.com"}],
        "paths": {
            "/predict": {
                "post": {
                    "operationId": "predict",
                    "summary": "Make prediction"
                }
            }
        }
    }
    
    # Generate SDK
    sdk_spec = await builder.generate_sdk_for_model(
        model_id="musician_audio_classifier",
        api_spec=api_spec,
        languages=[SDKLanguage.PYTHON, SDKLanguage.JAVASCRIPT],
        creator_type=CreatorType.MUSICIAN
    )
    
    # Save SDK for Python
    output_paths = await builder.save_generated_sdk(sdk_spec, SDKLanguage.PYTHON)
    print(f"Python SDK generated: {output_paths}")

if __name__ == "__main__":
    asyncio.run(main())