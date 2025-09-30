"""GitHub Actions CI/CD Template for Ainflue Platform
Enterprise-grade continuous integration and deployment pipeline template.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PipelineType(Enum):
    """CI/CD pipeline types"""
    CONTINUOUS_INTEGRATION = "ci"
    CONTINUOUS_DEPLOYMENT = "cd"
    SECURITY_SCAN = "security"
    PERFORMANCE_TEST = "performance"
    RELEASE = "release"


class EnvironmentType(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class GitHubActionsConfig:
    """GitHub Actions configuration structure"""
    project_name: str
    python_version: str = "3.11"
    node_version: str = "18"
    docker_registry: str = "ghcr.io"
    
    # Ainflue specific
    enable_ai_tests: bool = True
    enable_security_scan: bool = True
    enable_performance_tests: bool = True
    enable_e2e_tests: bool = True
    
    # Deployment targets
    auto_deploy_dev: bool = True
    auto_deploy_staging: bool = False
    auto_deploy_production: bool = False


class GitHubActionsTemplate:
    """Enterprise GitHub Actions Template for Ainflue Platform"""
    
    def __init__(self, config: GitHubActionsConfig):
        self.config = config
        
    def generate_ci_workflow(self) -> Dict[str, Any]:
        """Generate continuous integration workflow"""
        return {
            "name": "🚀 Ainflue Platform CI",
            "on": {
                "push": {
                    "branches": ["main", "develop", "feature/*"]
                },
                "pull_request": {
                    "branches": ["main", "develop"]
                }
            },
            "env": self._generate_environment_variables(),
            "jobs": {
                **self._generate_test_jobs(),
                **self._generate_security_jobs(),
                **self._generate_build_jobs()
            }
        }
    
    def generate_cd_workflow(self) -> Dict[str, Any]:
        """Generate continuous deployment workflow"""
        return {
            "name": "🚀 Ainflue Platform CD",
            "on": {
                "workflow_run": {
                    "workflows": ["🚀 Ainflue Platform CI"],
                    "types": ["completed"],
                    "branches": ["main", "develop"]
                },
                "workflow_dispatch": {
                    "inputs": {
                        "environment": {
                            "description": "Deployment environment",
                            "required": True,
                            "default": "development",
                            "type": "choice",
                            "options": ["development", "staging", "production"]
                        },
                        "version": {
                            "description": "Version to deploy",
                            "required": False,
                            "default": "latest"
                        }
                    }
                }
            },
            "env": self._generate_environment_variables(),
            "jobs": {
                **self._generate_deployment_jobs(),
                **self._generate_verification_jobs()
            }
        }
    
    def _generate_environment_variables(self) -> Dict[str, str]:
        """Generate workflow environment variables"""
        return {
            "PROJECT_NAME": self.config.project_name,
            "PYTHON_VERSION": self.config.python_version,
            "NODE_VERSION": self.config.node_version,
            "DOCKER_REGISTRY": self.config.docker_registry,
            "DOCKER_IMAGE_PREFIX": f"{self.config.docker_registry}/mlaiel/{self.config.project_name}",
            "PYTEST_WORKERS": "auto",
            "COVERAGE_THRESHOLD": "85"
        }
    
    def _generate_test_jobs(self) -> Dict[str, Any]:
        """Generate test jobs"""
        jobs = {
            "lint-and-format": {
                "name": "🔍 Lint & Format Check",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "${{ env.PYTHON_VERSION }}"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": |
                            python -m pip install --upgrade pip
                            pip install black isort flake8 mypy pylint
                            pip install -r requirements.txt
                    },
                    {
                        "name": "Run Black formatter check",
                        "run": "black --check --diff ."
                    },
                    {
                        "name": "Run isort import check",
                        "run": "isort --check-only --diff ."
                    },
                    {
                        "name": "Run flake8 linting",
                        "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
                    },
                    {
                        "name": "Run mypy type checking",
                        "run": "mypy --ignore-missing-imports ."
                    }
                ]
            },
            "unit-tests": {
                "name": "🧪 Unit Tests",
                "runs-on": "ubuntu-latest",
                "strategy": {
                    "matrix": {
                        "python-version": ["3.10", "3.11", "3.12"]
                    }
                },
                "services": {
                    "postgres": {
                        "image": "postgres:15",
                        "env": {
                            "POSTGRES_PASSWORD": "postgres",
                            "POSTGRES_DB": "ainflue_test"
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
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Python ${{ matrix.python-version }}",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "${{ matrix.python-version }}"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": |
                            python -m pip install --upgrade pip
                            pip install pytest pytest-cov pytest-xdist pytest-mock
                            pip install -r requirements.txt
                            pip install -r requirements-dev.txt
                    },
                    {
                        "name": "Run unit tests with coverage",
                        "run": |
                            pytest tests/unit/ \
                              --cov=. \
                              --cov-report=xml \
                              --cov-report=html \
                              --cov-fail-under=${{ env.COVERAGE_THRESHOLD }} \
                              -n ${{ env.PYTEST_WORKERS }} \
                              --junitxml=test-results.xml
                        ,
                        "env": {
                            "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/ainflue_test",
                            "REDIS_URL": "redis://localhost:6379",
                            "ENVIRONMENT": "testing"
                        }
                    },
                    {
                        "name": "Upload coverage to Codecov",
                        "uses": "codecov/codecov-action@v3",
                        "with": {
                            "file": "./coverage.xml",
                            "flags": "unittests",
                            "name": "codecov-umbrella"
                        }
                    }
                ]
            }
        }
        
        if self.config.enable_ai_tests:
            jobs["ai-model-tests"] = {
                "name": "🤖 AI Model Tests",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "${{ env.PYTHON_VERSION }}"}
                    },
                    {
                        "name": "Install AI/ML dependencies",
                        "run": |
                            python -m pip install --upgrade pip
                            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
                            pip install transformers librosa soundfile
                            pip install -r requirements-ml.txt
                    },
                    {
                        "name": "Run AI model tests",
                        "run": "pytest tests/ai/ -v --tb=short",
                        "env": {
                            "CUDA_VISIBLE_DEVICES": "",  # Force CPU for CI
                            "HF_DATASETS_OFFLINE": "1"
                        }
                    }
                ]
            }
        
        if self.config.enable_e2e_tests:
            jobs["e2e-tests"] = {
                "name": "🎭 E2E Tests",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "${{ env.PYTHON_VERSION }}"}
                    },
                    {
                        "name": "Set up Node.js",
                        "uses": "actions/setup-node@v3",
                        "with": {"node-version": "${{ env.NODE_VERSION }}"}
                    },
                    {
                        "name": "Start services with Docker Compose",
                        "run": |
                            docker-compose -f docker-compose.test.yml up -d
                            sleep 30  # Wait for services to be ready
                    },
                    {
                        "name": "Install test dependencies",
                        "run": |
                            pip install playwright pytest-playwright
                            playwright install chromium
                    },
                    {
                        "name": "Run E2E tests",
                        "run": "pytest tests/e2e/ -v --headed",
                        "env": {
                            "BASE_URL": "http://localhost:8000",
                            "PLAYWRIGHT_BROWSERS_PATH": "/home/runner/.cache/ms-playwright"
                        }
                    },
                    {
                        "name": "Upload E2E test artifacts",
                        "uses": "actions/upload-artifact@v3",
                        "if": "failure()",
                        "with": {
                            "name": "e2e-test-results",
                            "path": "test-results/"
                        }
                    }
                ]
            }
        
        return jobs
    
    def _generate_security_jobs(self) -> Dict[str, Any]:
        """Generate security scanning jobs"""
        if not self.config.enable_security_scan:
            return {}
        
        return {
            "security-scan": {
                "name": "🔒 Security Scan",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Run Bandit security scan",
                        "run": |
                            pip install bandit[toml]
                            bandit -r . -f json -o bandit-report.json || true
                    },
                    {
                        "name": "Run Safety vulnerability check",
                        "run": |
                            pip install safety
                            safety check --json --output safety-report.json || true
                    },
                    {
                        "name": "Run Semgrep SAST scan",
                        "uses": "returntocorp/semgrep-action@v1",
                        "with": {
                            "config": "auto"
                        }
                    },
                    {
                        "name": "Upload security scan results",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": "security-scan-results",
                            "path": "*-report.json"
                        }
                    }
                ]
            },
            "dependency-scan": {
                "name": "📦 Dependency Scan",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Run dependency vulnerability scan",
                        "uses": "pypa/gh-action-pip-audit@v1.0.8",
                        "with": {
                            "inputs": "requirements.txt requirements-production.txt"
                        }
                    }
                ]
            }
        }
    
    def _generate_build_jobs(self) -> Dict[str, Any]:
        """Generate build jobs"""
        return {
            "build-images": {
                "name": "🐳 Build Docker Images",
                "runs-on": "ubuntu-latest",
                "needs": ["lint-and-format", "unit-tests"],
                "if": "github.event_name == 'push'",
                "strategy": {
                    "matrix": {
                        "service": [
                            "api-gateway",
                            "auth-service", 
                            "content-processor",
                            "ai-services"
                        ]
                    }
                },
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Docker Buildx",
                        "uses": "docker/setup-buildx-action@v3"
                    },
                    {
                        "name": "Log in to Container Registry",
                        "uses": "docker/login-action@v3",
                        "with": {
                            "registry": "${{ env.DOCKER_REGISTRY }}",
                            "username": "${{ github.actor }}",
                            "password": "${{ secrets.GITHUB_TOKEN }}"
                        }
                    },
                    {
                        "name": "Extract metadata",
                        "id": "meta",
                        "uses": "docker/metadata-action@v5",
                        "with": {
                            "images": "${{ env.DOCKER_IMAGE_PREFIX }}-${{ matrix.service }}",
                            "tags": |
                                type=ref,event=branch
                                type=ref,event=pr
                                type=sha,prefix={{branch}}-
                                type=raw,value=latest,enable={{is_default_branch}}
                        }
                    },
                    {
                        "name": "Build and push Docker image",
                        "uses": "docker/build-push-action@v5",
                        "with": {
                            "context": f"./{matrix.service}",
                            "file": f"./{matrix.service}/Dockerfile",
                            "push": True,
                            "tags": "${{ steps.meta.outputs.tags }}",
                            "labels": "${{ steps.meta.outputs.labels }}",
                            "cache-from": "type=gha",
                            "cache-to": "type=gha,mode=max"
                        }
                    }
                ]
            }
        }
    
    def _generate_deployment_jobs(self) -> Dict[str, Any]:
        """Generate deployment jobs"""
        return {
            "deploy-development": {
                "name": "🚀 Deploy to Development",
                "runs-on": "ubuntu-latest",
                "if": f"github.ref == 'refs/heads/develop' && {str(self.config.auto_deploy_dev).lower()}",
                "environment": "development",
                "steps": self._generate_deployment_steps(EnvironmentType.DEVELOPMENT)
            },
            "deploy-staging": {
                "name": "🚀 Deploy to Staging", 
                "runs-on": "ubuntu-latest",
                "if": f"github.ref == 'refs/heads/main' && {str(self.config.auto_deploy_staging).lower()}",
                "environment": "staging",
                "steps": self._generate_deployment_steps(EnvironmentType.STAGING)
            },
            "deploy-production": {
                "name": "🚀 Deploy to Production",
                "runs-on": "ubuntu-latest",
                "if": f"github.event.inputs.environment == 'production' && {str(self.config.auto_deploy_production).lower()}",
                "environment": "production",
                "steps": self._generate_deployment_steps(EnvironmentType.PRODUCTION)
            }
        }
    
    def _generate_deployment_steps(self, environment: EnvironmentType) -> List[Dict[str, Any]]:
        """Generate deployment steps for specific environment"""
        return [
            {"uses": "actions/checkout@v4"},
            {
                "name": "Configure AWS credentials",
                "uses": "aws-actions/configure-aws-credentials@v4",
                "with": {
                    "aws-access-key-id": f"${{{{ secrets.AWS_ACCESS_KEY_ID_{environment.value.upper()} }}}}",
                    "aws-secret-access-key": f"${{{{ secrets.AWS_SECRET_ACCESS_KEY_{environment.value.upper()} }}}}",
                    "aws-region": "us-west-2"
                }
            },
            {
                "name": "Deploy to EKS",
                "run": |
                    aws eks update-kubeconfig --region us-west-2 --name ainflue-{environment.value}
                    kubectl apply -f k8s/{environment.value}/
                    kubectl rollout status deployment/ainflue-api-gateway -n ainflue-{environment.value}
            },
            {
                "name": "Run database migrations",
                "run": |
                    kubectl exec -n ainflue-{environment.value} deployment/ainflue-api-gateway -- python manage.py migrate
                ,
                "if": f"'{environment.value}' != 'production'"
            },
            {
                "name": "Verify deployment",
                "run": |
                    sleep 60  # Wait for deployment to stabilize
                    kubectl exec -n ainflue-{environment.value} deployment/ainflue-api-gateway -- python manage.py health_check
            },
            {
                "name": "Send deployment notification",
                "uses": "8398a7/action-slack@v3",
                "if": "always()",
                "with": {
                    "status": "${{ job.status }}",
                    "channel": "#deployments",
                    "webhook_url": "${{ secrets.SLACK_WEBHOOK }}"
                }
            }
        ]
    
    def _generate_verification_jobs(self) -> Dict[str, Any]:
        """Generate post-deployment verification jobs"""
        if not self.config.enable_performance_tests:
            return {}
        
        return {
            "performance-tests": {
                "name": "⚡ Performance Tests",
                "runs-on": "ubuntu-latest",
                "needs": ["deploy-development"],
                "if": "success()",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {
                        "name": "Install k6",
                        "run": |
                            sudo gpg -k
                            sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
                            echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
                            sudo apt-get update
                            sudo apt-get install k6
                    },
                    {
                        "name": "Run performance tests",
                        "run": "k6 run tests/performance/load_test.js",
                        "env": {
                            "BASE_URL": "https://dev.ainflue.com"
                        }
                    },
                    {
                        "name": "Upload performance results",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": "performance-test-results",
                            "path": "test-results/"
                        }
                    }
                ]
            }
        }
    
    def generate_release_workflow(self) -> Dict[str, Any]:
        """Generate release workflow"""
        return {
            "name": "🎉 Release Ainflue Platform",
            "on": {
                "push": {
                    "tags": ["v*.*.*"]
                }
            },
            "jobs": {
                "create-release": {
                    "name": "Create Release",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Create Release",
                            "uses": "actions/create-release@v1",
                            "env": {
                                "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                            },
                            "with": {
                                "tag_name": "${{ github.ref }}",
                                "release_name": "Ainflue Platform ${{ github.ref }}",
                                "draft": False,
                                "prerelease": False
                            }
                        }
                    ]
                }
            }
        }
    
    def save_workflows(self, output_dir: str) -> None:
        """Save all workflow files to .github/workflows directory"""
        workflows_path = Path(output_dir) / ".github" / "workflows"
        workflows_path.mkdir(parents=True, exist_ok=True)
        
        # CI workflow
        with open(workflows_path / "ci.yml", 'w') as f:
            yaml.dump(self.generate_ci_workflow(), f, default_flow_style=False, indent=2)
        
        # CD workflow
        with open(workflows_path / "cd.yml", 'w') as f:
            yaml.dump(self.generate_cd_workflow(), f, default_flow_style=False, indent=2)
        
        # Release workflow
        with open(workflows_path / "release.yml", 'w') as f:
            yaml.dump(self.generate_release_workflow(), f, default_flow_style=False, indent=2)
        
        logger.info(f"GitHub Actions workflows saved to {workflows_path}")


# Example usage
def create_production_config() -> GitHubActionsConfig:
    """Create production configuration"""
    return GitHubActionsConfig(
        project_name="ainflue-platform",
        python_version="3.11",
        node_version="18",
        enable_ai_tests=True,
        enable_security_scan=True,
        enable_performance_tests=True,
        enable_e2e_tests=True,
        auto_deploy_dev=True,
        auto_deploy_staging=False,
        auto_deploy_production=False
    )


if __name__ == "__main__":
    config = create_production_config()
    template = GitHubActionsTemplate(config)
    
    print("GitHub Actions Template for Ainflue Platform")
    print("Configuration:")
    print(f"- Python Version: {config.python_version}")
    print(f"- AI Tests: {config.enable_ai_tests}")
    print(f"- Security Scan: {config.enable_security_scan}")
    print(f"- Performance Tests: {config.enable_performance_tests}")
    print(f"- Auto Deploy Dev: {config.auto_deploy_dev}")
