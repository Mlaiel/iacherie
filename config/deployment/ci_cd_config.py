"""CI/CD Pipeline Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional continuous integration and deployment configuration
for multi-format content protection and AI-powered creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml


class PipelineStage(Enum):
    """CI/CD pipeline stages"""    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    CODE_QUALITY = "code_quality"
    DEPLOY_STAGING = "deploy_staging"
    INTEGRATION_TEST = "integration_test"
    DEPLOY_PRODUCTION = "deploy_production"
    PERFORMANCE_TEST = "performance_test"
    ROLLBACK = "rollback"


@dataclass
class GitHubActionsConfig:
    """GitHub Actions workflow configuration"""    name: str
    trigger_events: List[str] = field(default_factory=lambda: ["push", "pull_request"])
    branches: List[str] = field(default_factory=lambda: ["main", "develop"])
    python_versions: List[str] = field(default_factory=lambda: ["3.11"])
    node_versions: List[str] = field(default_factory=lambda: ["18"])
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    matrix_strategy: Optional[Dict[str, Any]] = None


@dataclass
class JenkinsConfig:
    """Jenkins pipeline configuration"""    agent: str = "any"
    stages: List[Dict[str, Any]] = field(default_factory=list)
    post_actions: Dict[str, List[str]] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)


@dataclass
class GitLabCIConfig:
    """GitLab CI/CD configuration"""    image: str = "python:3.11"
    stages: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)
    cache: Optional[Dict[str, Any]] = None


class CICDConfig:
    """    Professional CI/CD configuration manager for IA-Influencer Agent Platform.
    
    Manages deployment pipelines for:
    - AI fingerprinting services (audio, video, image, text)
    - Content protection microservices
    - Revenue tracking and monetization engines
    - Real-time monitoring and alerting systems
    - Multi-database clusters and caching layers
    - Web crawlers and content scanning services
    """    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.docker_registry = self._get_docker_registry()
        self.kubernetes_cluster = self._get_k8s_cluster()
        
    def _get_docker_registry(self) -> str:
        """Get Docker registry URL based on environment"""        registries = {
            "development": "localhost:5000",
            "staging": "registry.staging.ia-influencer.com",
            "production": "registry.ia-influencer.com"
        }
        return registries.get(self.environment, "localhost:5000")
    
    def _get_k8s_cluster(self) -> str:
        """Get Kubernetes cluster endpoint"""        clusters = {
            "development": "k8s.dev.ia-influencer.com",
            "staging": "k8s.staging.ia-influencer.com", 
            "production": "k8s.ia-influencer.com"
        }
        return clusters.get(self.environment, "localhost:6443")
    
    def get_github_actions_config(self) -> GitHubActionsConfig:
        """Generate GitHub Actions workflow configuration"""        return GitHubActionsConfig(
            name=f"IA-Influencer Agent {self.environment.title()} Pipeline",
            trigger_events=["push", "pull_request", "workflow_dispatch"],
            branches=["main", "develop", "release/*", "feature/*"],
            environment_variables={
                "ENVIRONMENT": self.environment,
                "PROJECT_NAME": self.project_name,
                "DOCKER_REGISTRY": self.docker_registry,
                "KUBERNETES_CLUSTER": self.kubernetes_cluster,
                "PYTHON_VERSION": "3.11",
                "NODE_VERSION": "18",
                "DATABASE_ENGINE": "postgresql",
                "CACHE_BACKEND": "redis",
                "AI_MODEL_REGISTRY": "mlflow",
                "CONTENT_PROTECTION_ENGINE": "faiss"
            },
            secrets=[
                "DOCKER_REGISTRY_TOKEN",
                "KUBERNETES_CONFIG",
                "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY",
                "DATABASE_URL",
                "REDIS_URL",
                "ELASTICSEARCH_URL",
                "SPOTIFY_CLIENT_ID",
                "SPOTIFY_CLIENT_SECRET",
                "YOUTUBE_API_KEY",
                "INSTAGRAM_API_TOKEN",
                "STRIPE_SECRET_KEY",
                "ML_MODEL_API_KEY",
                "CONTENT_PROTECTION_API_KEY",
                "MONITORING_API_KEY"
            ]
        )
    
    def get_jenkins_pipeline_config(self) -> JenkinsConfig:
        """Generate Jenkins pipeline configuration"""        stages = [
            {
                "name": "Checkout",
                "steps": [
                    "checkout scm",
                    "sh 'git submodule update --init --recursive'"
                ]
            },
            {
                "name": "Environment Setup",
                "steps": [
                    "sh 'python --version'",
                    "sh 'node --version'",
                    "sh 'docker --version'",
                    "sh 'kubectl version --client'"
                ]
            },
            {
                "name": "Dependencies Installation",
                "parallel": {
                    "Python Dependencies": [
                        "sh 'pip install --upgrade pip'",
                        "sh 'pip install -r requirements.txt'",
                        "sh 'pip install -r requirements-dev.txt'"
                    ],
                    "Node Dependencies": [
                        "sh 'npm ci'",
                        "sh 'npm audit fix'"
                    ]
                }
            },
            {
                "name": "Code Quality Checks",
                "parallel": {
                    "Python Linting": [
                        "sh 'flake8 backend/'",
                        "sh 'black --check backend/'",
                        "sh 'mypy backend/'",
                        "sh 'bandit -r backend/'"
                    ],
                    "JavaScript Linting": [
                        "sh 'npm run lint'",
                        "sh 'npm run type-check'"
                    ],
                    "Security Scanning": [
                        "sh 'safety check'",
                        "sh 'npm audit'"
                    ]
                }
            },
            {
                "name": "Unit Tests",
                "parallel": {
                    "Backend Tests": [
                        "sh 'pytest backend/tests/ -v --cov=backend --cov-report=xml'",
                        "publishTestResults testResultsFiles: 'junit.xml'",
                        "publishCoverageReports sourceFileResolver: sourceFiles('backend/')"
                    ],
                    "Frontend Tests": [
                        "sh 'npm run test:unit'",
                        "publishTestResults testResultsFiles: 'frontend/test-results.xml'"
                    ]
                }
            },
            {
                "name": "AI Model Validation",
                "steps": [
                    "sh 'python scripts/validate_ml_models.py'",
                    "sh 'python scripts/test_fingerprinting_accuracy.py'",
                    "sh 'python scripts/benchmark_ai_performance.py'"
                ]
            },
            {
                "name": "Build Docker Images",
                "parallel": {
                    "API Service": [
                        f"sh 'docker build -t {self.docker_registry}/{self.project_name}-api:$BUILD_NUMBER .'",
                        f"sh 'docker push {self.docker_registry}/{self.project_name}-api:$BUILD_NUMBER'"
                    ],
                    "AI Services": [
                        f"sh 'docker build -t {self.docker_registry}/{self.project_name}-ai:$BUILD_NUMBER -f docker/Dockerfile.ai .'",
                        f"sh 'docker push {self.docker_registry}/{self.project_name}-ai:$BUILD_NUMBER'"
                    ],
                    "Content Protection": [
                        f"sh 'docker build -t {self.docker_registry}/{self.project_name}-protection:$BUILD_NUMBER -f docker/Dockerfile.protection .'",
                        f"sh 'docker push {self.docker_registry}/{self.project_name}-protection:$BUILD_NUMBER'"
                    ]
                }
            },
            {
                "name": "Integration Tests",
                "steps": [
                    "sh 'docker-compose -f docker-compose.test.yml up -d'",
                    "sh 'pytest backend/tests_integration/ -v'",
                    "sh 'docker-compose -f docker-compose.test.yml down'"
                ]
            },
            {
                "name": f"Deploy to {self.environment.title()}",
                "when": f"environment name: '{self.environment}'",
                "steps": [
                    f"sh 'kubectl config use-context {self.kubernetes_cluster}'",
                    f"sh 'helm upgrade --install {self.project_name} ./helm/chart --namespace {self.environment} --set image.tag=$BUILD_NUMBER'",
                    "sh 'kubectl rollout status deployment/api-service -n {self.environment}'",
                    "sh 'kubectl rollout status deployment/ai-service -n {self.environment}'",
                    "sh 'kubectl rollout status deployment/protection-service -n {self.environment}'"
                ]
            },
            {
                "name": "Post-Deployment Tests",
                "steps": [
                    "sh 'python scripts/health_check.py'",
                    "sh 'python scripts/api_smoke_tests.py'",
                    "sh 'python scripts/performance_baseline.py'"
                ]
            }
        ]
        
        return JenkinsConfig(
            agent="kubernetes",
            stages=stages,
            environment={
                "ENVIRONMENT": self.environment,
                "PROJECT_NAME": self.project_name,
                "DOCKER_REGISTRY": self.docker_registry,
                "KUBERNETES_CLUSTER": self.kubernetes_cluster
            },
            post_actions={
                "always": [
                    "cleanWs()",
                    "publishTestResults testResultsFiles: '**/*test-results.xml'",
                    "publishCoverageReports sourceFileResolver: sourceFiles('backend/')"
                ],
                "failure": [
                    "emailext subject: 'Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}', body: 'Build failed. Check console output.', to: 'mlaiel@live.de'",
                    "slackSend channel: '#deployments', color: 'danger', message: 'Build failed for ${env.JOB_NAME} #${env.BUILD_NUMBER}'"
                ],
                "success": [
                    "slackSend channel: '#deployments', color: 'good', message: 'Successfully deployed ${env.JOB_NAME} #${env.BUILD_NUMBER} to ${ENVIRONMENT}'"
                ]
            },
            triggers=[
                "pollSCM('H/5 * * * *')",
                "cron('@daily')"
            ]
        )
    
    def get_gitlab_ci_config(self) -> GitLabCIConfig:
        """Generate GitLab CI/CD configuration"""        return GitLabCIConfig(
            image="python:3.11",
            stages=[
                "prepare",
                "build",
                "test",
                "security",
                "package",
                "deploy",
                "verify"
            ],
            variables={
                "DOCKER_DRIVER": "overlay2",
                "ENVIRONMENT": self.environment,
                "PROJECT_NAME": self.project_name,
                "DOCKER_REGISTRY": self.docker_registry,
                "KUBERNETES_CLUSTER": self.kubernetes_cluster,
                "PIP_CACHE_DIR": "$CI_PROJECT_DIR/.cache/pip",
                "NPM_CONFIG_CACHE": "$CI_PROJECT_DIR/.cache/npm"
            },
            before_script=[
                "python --version",
                "pip install --upgrade pip",
                "apt-get update -qy",
                "apt-get install -y nodejs npm docker.io kubectl"
            ],
            cache={
                "paths": [
                    ".cache/pip/",
                    ".cache/npm/",
                    "node_modules/"
                ]
            }
        )
    
    def generate_github_workflow_yaml(self) -> str:
        """Generate complete GitHub Actions workflow YAML"""        config = self.get_github_actions_config()
        
        workflow = {
            "name": config.name,
            "on": {
                "push": {
                    "branches": config.branches
                },
                "pull_request": {
                    "branches": config.branches
                },
                "workflow_dispatch": {}
            },
            "env": config.environment_variables,
            "jobs": {
                "build-and-test": {
                    "runs-on": "ubuntu-latest",
                    "strategy": {
                        "matrix": {
                            "python-version": config.python_versions,
                            "node-version": config.node_versions
                        }
                    },
                    "services": {
                        "postgres": {
                            "image": "postgres:15",
                            "env": {
                                "POSTGRES_PASSWORD": "postgres",
                                "POSTGRES_DB": "test_db"
                            },
                            "options": "--health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5",
                            "ports": ["5432:5432"]
                        },
                        "redis": {
                            "image": "redis:7",
                            "options": "--health-cmd 'redis-cli ping' --health-interval 10s --health-timeout 5s --health-retries 5",
                            "ports": ["6379:6379"]
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                            "with": {
                                "fetch-depth": 0
                            }
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "${{ matrix.python-version }}"
                            }
                        },
                        {
                            "name": "Set up Node.js",
                            "uses": "actions/setup-node@v3",
                            "with": {
                                "node-version": "${{ matrix.node-version }}"
                            }
                        },
                        {
                            "name": "Cache Python dependencies",
                            "uses": "actions/cache@v3",
                            "with": {
                                "path": "~/.cache/pip",
                                "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}",
                                "restore-keys": "${{ runner.os }}-pip-"
                            }
                        },
                        {
                            "name": "Cache Node dependencies", 
                            "uses": "actions/cache@v3",
                            "with": {
                                "path": "~/.npm",
                                "key": "${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}",
                                "restore-keys": "${{ runner.os }}-node-"
                            }
                        },
                        {
                            "name": "Install Python dependencies",
                            "run": "pip install -r requirements.txt && pip install -r requirements-dev.txt"
                        },
                        {
                            "name": "Install Node dependencies",
                            "run": "npm ci"
                        },
                        {
                            "name": "Run Python linting",
                            "run": "flake8 backend/ && black --check backend/ && mypy backend/"
                        },
                        {
                            "name": "Run JavaScript linting", 
                            "run": "npm run lint && npm run type-check"
                        },
                        {
                            "name": "Run security checks",
                            "run": "bandit -r backend/ && safety check && npm audit"
                        },
                        {
                            "name": "Run Python tests",
                            "run": "pytest backend/tests/ -v --cov=backend --cov-report=xml",
                            "env": {
                                "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/test_db",
                                "REDIS_URL": "redis://localhost:6379/0"
                            }
                        },
                        {
                            "name": "Run JavaScript tests",
                            "run": "npm run test:unit"
                        },
                        {
                            "name": "Validate AI models",
                            "run": "python scripts/validate_ml_models.py && python scripts/test_fingerprinting_accuracy.py"
                        },
                        {
                            "name": "Upload coverage to Codecov",
                            "uses": "codecov/codecov-action@v3",
                            "with": {
                                "file": "./coverage.xml",
                                "fail_ci_if_error": True
                            }
                        }
                    ]
                },
                "build-and-push": {
                    "needs": "build-and-test",
                    "runs-on": "ubuntu-latest",
                    "if": "github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3"
                        },
                        {
                            "name": "Login to Container Registry",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "registry": "${{ env.DOCKER_REGISTRY }}",
                                "username": "${{ secrets.DOCKER_REGISTRY_USERNAME }}",
                                "password": "${{ secrets.DOCKER_REGISTRY_TOKEN }}"
                            }
                        },
                        {
                            "name": "Build and push API image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "push": True,
                                "tags": "${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-api:${{ github.sha }},${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-api:latest",
                                "platforms": "linux/amd64,linux/arm64",
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max"
                            }
                        },
                        {
                            "name": "Build and push AI services image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "file": "docker/Dockerfile.ai",
                                "push": True,
                                "tags": "${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-ai:${{ github.sha }},${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-ai:latest"
                            }
                        },
                        {
                            "name": "Build and push Content Protection image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "file": "docker/Dockerfile.protection",
                                "push": True,
                                "tags": "${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-protection:${{ github.sha }},${{ env.DOCKER_REGISTRY }}/${{ env.PROJECT_NAME }}-protection:latest"
                            }
                        }
                    ]
                },
                "deploy": {
                    "needs": "build-and-push",
                    "runs-on": "ubuntu-latest",
                    "environment": self.environment,
                    "if": f"github.ref == 'refs/heads/main' && github.event_name == 'push'",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Configure kubectl",
                            "uses": "azure/k8s-set-context@v3",
                            "with": {
                                "method": "kubeconfig",
                                "kubeconfig": "${{ secrets.KUBERNETES_CONFIG }}"
                            }
                        },
                        {
                            "name": "Deploy to Kubernetes",
                            "run": f"helm upgrade --install {self.project_name} ./helm/chart --namespace {self.environment} --set image.tag=${{{{ github.sha }}}} --wait"
                        },
                        {
                            "name": "Verify deployment",
                            "run": f"kubectl rollout status deployment/api-service -n {self.environment} && python scripts/health_check.py"
                        },
                        {
                            "name": "Run smoke tests",
                            "run": "python scripts/api_smoke_tests.py"
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def generate_jenkins_pipeline_script(self) -> str:
        """Generate complete Jenkinsfile pipeline script"""        config = self.get_jenkins_pipeline_config()
        
        pipeline_script = f'''
pipeline {{
    agent {config.agent}
    
    environment {{
'''
        for key, value in config.environment.items():
            pipeline_script += f'        {key} = "{value}"\n'
        
        pipeline_script += '''    }
    
    parameters {
'''
        for param in config.parameters:
            pipeline_script += f'        {param}\n'
        
        pipeline_script += '''    }
    
    triggers {
'''
        for trigger in config.triggers:
            pipeline_script += f'        {trigger}\n'
            
        pipeline_script += '''    }
    
    stages {
'''
        
        for stage in config.stages:
            pipeline_script += f'''        stage('{stage["name"]}') {{
            steps {{
'''
            for step in stage.get("steps", []):
                pipeline_script += f'                {step}\n'
            
            if "parallel" in stage:
                pipeline_script += '''            parallel {
'''
                for parallel_name, parallel_steps in stage["parallel"].items():
                    pipeline_script += f'''                '{parallel_name}': {{
'''
                    for step in parallel_steps:
                        pipeline_script += f'                    {step}\n'
                    pipeline_script += '''                }
'''
                pipeline_script += '''            }
'''
            
            pipeline_script += '''            }
        }
        
'''
        
        pipeline_script += '''    }
    
    post {
'''
        for condition, actions in config.post_actions.items():
            pipeline_script += f'''        {condition} {{
'''
            for action in actions:
                pipeline_script += f'            {action}\n'
            pipeline_script += '''        }
'''
        
        pipeline_script += '''    }
}
'''
        
        return pipeline_script
    
    def generate_gitlab_ci_yaml(self) -> str:
        """Generate complete GitLab CI/CD YAML configuration"""        config = self.get_gitlab_ci_config()
        
        gitlab_ci = {
            "image": config.image,
            "stages": config.stages,
            "variables": config.variables,
            "cache": config.cache,
            "before_script": config.before_script,
            "prepare": {
                "stage": "prepare",
                "script": [
                    "echo 'Preparing environment...'",
                    "python --version",
                    "docker --version",
                    "kubectl version --client"
                ]
            },
            "build": {
                "stage": "build",
                "script": [
                    "pip install -r requirements.txt",
                    "pip install -r requirements-dev.txt",
                    "npm ci"
                ],
                "artifacts": {
                    "paths": ["node_modules/"],
                    "expire_in": "1 hour"
                }
            },
            "test:python": {
                "stage": "test",
                "services": ["postgres:15", "redis:7"],
                "variables": {
                    "DATABASE_URL": "postgresql://postgres:postgres@postgres:5432/test_db",
                    "REDIS_URL": "redis://redis:6379/0"
                },
                "script": [
                    "pytest backend/tests/ -v --cov=backend --cov-report=xml --junitxml=report.xml"
                ],
                "artifacts": {
                    "reports": {
                        "junit": "report.xml",
                        "coverage_report": {
                            "coverage_format": "cobertura",
                            "path": "coverage.xml"
                        }
                    }
                }
            },
            "test:javascript": {
                "stage": "test",
                "script": [
                    "npm run test:unit"
                ],
                "artifacts": {
                    "reports": {
                        "junit": "frontend/test-results.xml"
                    }
                }
            },
            "security:python": {
                "stage": "security",
                "script": [
                    "bandit -r backend/ -f json -o bandit-report.json",
                    "safety check --json --output safety-report.json"
                ],
                "artifacts": {
                    "reports": {
                        "sast": "bandit-report.json"
                    },
                    "paths": ["safety-report.json"]
                }
            },
            "security:javascript": {
                "stage": "security",
                "script": [
                    "npm audit --audit-level high --json > npm-audit.json"
                ],
                "artifacts": {
                    "paths": ["npm-audit.json"]
                }
            },
            "package:api": {
                "stage": "package",
                "script": [
                    f"docker build -t {self.docker_registry}/{self.project_name}-api:$CI_COMMIT_SHA .",
                    f"docker push {self.docker_registry}/{self.project_name}-api:$CI_COMMIT_SHA"
                ],
                "only": ["main", "develop"]
            },
            "package:ai": {
                "stage": "package", 
                "script": [
                    f"docker build -t {self.docker_registry}/{self.project_name}-ai:$CI_COMMIT_SHA -f docker/Dockerfile.ai .",
                    f"docker push {self.docker_registry}/{self.project_name}-ai:$CI_COMMIT_SHA"
                ],
                "only": ["main", "develop"]
            },
            "deploy:staging": {
                "stage": "deploy",
                "environment": {
                    "name": "staging",
                    "url": "https://staging.ia-influencer.com"
                },
                "script": [
                    f"kubectl config use-context {self.kubernetes_cluster}",
                    f"helm upgrade --install {self.project_name} ./helm/chart --namespace staging --set image.tag=$CI_COMMIT_SHA"
                ],
                "only": ["develop"]
            },
            "deploy:production": {
                "stage": "deploy",
                "environment": {
                    "name": "production",
                    "url": "https://ia-influencer.com"
                },
                "script": [
                    f"kubectl config use-context {self.kubernetes_cluster}",
                    f"helm upgrade --install {self.project_name} ./helm/chart --namespace production --set image.tag=$CI_COMMIT_SHA"
                ],
                "when": "manual",
                "only": ["main"]
            },
            "verify:health": {
                "stage": "verify",
                "script": [
                    "python scripts/health_check.py",
                    "python scripts/api_smoke_tests.py"
                ]
            }
        }
        
        return yaml.dump(gitlab_ci, default_flow_style=False, sort_keys=False)
    
    def get_deployment_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get deployment strategy configurations"""        return {
            "blue_green": {
                "name": "Blue-Green Deployment",
                "description": "Zero-downtime deployment with parallel environments",
                "rollback_time": "< 30 seconds",
                "resource_overhead": "2x",
                "risk_level": "low",
                "suitable_for": ["production", "critical_services"],
                "configuration": {
                    "parallel_environments": True,
                    "traffic_switching": "instant",
                    "health_checks": True,
                    "rollback_strategy": "traffic_redirect"
                }
            },
            "rolling_update": {
                "name": "Rolling Update",
                "description": "Gradual replacement of instances",
                "rollback_time": "2-5 minutes",
                "resource_overhead": "1.5x",
                "risk_level": "medium",
                "suitable_for": ["staging", "development"],
                "configuration": {
                    "max_unavailable": "25%",
                    "max_surge": "25%",
                    "readiness_probe": True,
                    "liveness_probe": True
                }
            },
            "canary": {
                "name": "Canary Deployment",
                "description": "Gradual traffic shifting with monitoring",
                "rollback_time": "1-2 minutes",
                "resource_overhead": "1.2x", 
                "risk_level": "low",
                "suitable_for": ["production", "a_b_testing"],
                "configuration": {
                    "traffic_split": [5, 10, 25, 50, 100],
                    "success_criteria": {
                        "error_rate": "< 0.1%",
                        "response_time": "< 200ms",
                        "success_rate": "> 99.9%"
                    },
                    "auto_rollback": True
                }
            }
        }
    
    def export_configurations(self, output_dir: str = "./ci-cd-configs") -> Dict[str, str]:
        """Export all CI/CD configurations to files"""        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        
        # GitHub Actions
        github_workflow = self.generate_github_workflow_yaml()
        github_path = os.path.join(output_dir, f"github-{self.environment}.yml")
        with open(github_path, 'w') as f:
            f.write(github_workflow)
        configs['github'] = github_path
        
        # Jenkins
        jenkins_pipeline = self.generate_jenkins_pipeline_script()
        jenkins_path = os.path.join(output_dir, f"Jenkinsfile-{self.environment}")
        with open(jenkins_path, 'w') as f:
            f.write(jenkins_pipeline)
        configs['jenkins'] = jenkins_path
        
        # GitLab CI
        gitlab_ci = self.generate_gitlab_ci_yaml()
        gitlab_path = os.path.join(output_dir, f"gitlab-ci-{self.environment}.yml")
        with open(gitlab_path, 'w') as f:
            f.write(gitlab_ci)
        configs['gitlab'] = gitlab_path
        
        return configs
