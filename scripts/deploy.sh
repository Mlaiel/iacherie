#!/bin/bash

# Ainflue Platform Deployment Script
# Automated deployment for production, staging, and development environments
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
NAMESPACE="ainflue"
DOCKER_REGISTRY="registry.ainflue.com"
IMAGE_TAG="latest"
DRY_RUN=false
SKIP_TESTS=false
FORCE_DEPLOY=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Ainflue Platform Deployment Script

OPTIONS:
    -e, --environment ENV    Target environment (production|staging|development) [default: production]
    -n, --namespace NAME     Kubernetes namespace [default: ainflue]
    -r, --registry URL       Docker registry URL [default: registry.ainflue.com]
    -t, --tag TAG           Docker image tag [default: latest]
    -d, --dry-run           Perform a dry run without making changes
    -s, --skip-tests        Skip running tests before deployment
    -f, --force             Force deployment even if tests fail
    -h, --help              Show this help message

EXAMPLES:
    $0                                          # Deploy to production
    $0 -e staging -t v1.2.0                   # Deploy version 1.2.0 to staging
    $0 -e development -d                       # Dry run deployment to development
    $0 -e production -t v1.0.0 -f             # Force deploy v1.0.0 to production

ENVIRONMENT VARIABLES:
    KUBECONFIG              Path to kubeconfig file
    DOCKER_USERNAME         Docker registry username
    DOCKER_PASSWORD         Docker registry password
    SLACK_WEBHOOK_URL       Slack webhook for notifications

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -r|--registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -s|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -f|--force)
                FORCE_DEPLOY=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check required tools
    local tools=("kubectl" "docker" "helm")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check Kubernetes connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check Docker registry access
    if ! docker info &> /dev/null; then
        print_error "Cannot connect to Docker daemon"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Validate environment
validate_environment() {
    print_status "Validating environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        production|staging|development)
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_error "Valid environments: production, staging, development"
            exit 1
            ;;
    esac
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_warning "Namespace '$NAMESPACE' does not exist"
        if [[ $DRY_RUN == false ]]; then
            print_status "Creating namespace '$NAMESPACE'..."
            kubectl create namespace "$NAMESPACE"
        fi
    fi
    
    print_success "Environment validation passed"
}

# Run tests
run_tests() {
    if [[ $SKIP_TESTS == true ]]; then
        print_warning "Skipping tests as requested"
        return 0
    fi
    
    print_status "Running test suite..."
    
    # Install test dependencies if needed
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt > /dev/null
    
    # Run tests
    print_status "Executing tests..."
    if pytest tests/ -v --tb=short; then
        print_success "All tests passed"
    else
        print_error "Tests failed"
        if [[ $FORCE_DEPLOY == false ]]; then
            print_error "Deployment aborted due to test failures"
            print_error "Use --force to deploy anyway or --skip-tests to skip testing"
            exit 1
        else
            print_warning "Proceeding with deployment despite test failures (--force flag used)"
        fi
    fi
    
    deactivate
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    local images=(
        "ainflue/platform:$IMAGE_TAG"
        "ainflue/crawler:$IMAGE_TAG"
        "ainflue/analytics:$IMAGE_TAG"
        "ainflue/ai-engine:$IMAGE_TAG"
    )
    
    for image in "${images[@]}"; do
        print_status "Building $image..."
        
        if [[ $DRY_RUN == false ]]; then
            docker build -t "$DOCKER_REGISTRY/$image" \
                --build-arg ENVIRONMENT="$ENVIRONMENT" \
                --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
                --build-arg VERSION="$IMAGE_TAG" \
                -f docker/Dockerfile .
        fi
    done
    
    print_success "Docker images built successfully"
}

# Push Docker images
push_images() {
    print_status "Pushing Docker images to registry..."
    
    # Login to Docker registry
    if [[ -n "$DOCKER_USERNAME" && -n "$DOCKER_PASSWORD" ]]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    local images=(
        "ainflue/platform:$IMAGE_TAG"
        "ainflue/crawler:$IMAGE_TAG"
        "ainflue/analytics:$IMAGE_TAG"
        "ainflue/ai-engine:$IMAGE_TAG"
    )
    
    for image in "${images[@]}"; do
        print_status "Pushing $DOCKER_REGISTRY/$image..."
        
        if [[ $DRY_RUN == false ]]; then
            docker push "$DOCKER_REGISTRY/$image"
        fi
    done
    
    print_success "Docker images pushed successfully"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_status "Deploying to Kubernetes..."
    
    # Set kubectl context
    kubectl config set-context --current --namespace="$NAMESPACE"
    
    # Apply configurations based on environment
    local config_dir="kubernetes/$ENVIRONMENT"
    
    if [[ ! -d "$config_dir" ]]; then
        print_error "Configuration directory not found: $config_dir"
        exit 1
    fi
    
    # Apply in order: namespace, secrets, configmaps, databases, services
    local apply_order=(
        "namespace.yaml"
        "secrets.yaml"
        "configmaps.yaml"
        "postgresql-deployment.yaml"
        "mongodb-deployment.yaml"
        "redis-deployment.yaml"
        "api-deployment.yaml"
        "crawler-deployment.yaml"
        "analytics-deployment.yaml"
        "ai-engine-deployment.yaml"
        "ingress.yaml"
        "monitoring.yaml"
        "hpa.yaml"
    )
    
    for config_file in "${apply_order[@]}"; do
        local file_path="$config_dir/$config_file"
        
        if [[ -f "$file_path" ]]; then
            print_status "Applying $config_file..."
            
            if [[ $DRY_RUN == false ]]; then
                # Replace image tags in deployment files
                sed "s|IMAGE_TAG|$IMAGE_TAG|g" "$file_path" | \
                sed "s|DOCKER_REGISTRY|$DOCKER_REGISTRY|g" | \
                kubectl apply -f -
            else
                print_status "DRY RUN: Would apply $config_file"
            fi
        else
            print_warning "Configuration file not found: $file_path"
        fi
    done
    
    print_success "Kubernetes deployment completed"
}

# Wait for deployment to be ready
wait_for_deployment() {
    print_status "Waiting for deployment to be ready..."
    
    local deployments=(
        "ainflue-api"
        "ainflue-crawler"
        "ainflue-analytics"
        "ainflue-ai-engine"
    )
    
    for deployment in "${deployments[@]}"; do
        print_status "Waiting for $deployment..."
        
        if [[ $DRY_RUN == false ]]; then
            kubectl wait --for=condition=Available \
                deployment/"$deployment" \
                -n "$NAMESPACE" \
                --timeout=600s
        fi
    done
    
    print_success "All deployments are ready"
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Get service endpoint
    local api_endpoint
    if [[ $ENVIRONMENT == "production" ]]; then
        api_endpoint="https://api.ainflue.com"
    elif [[ $ENVIRONMENT == "staging" ]]; then
        api_endpoint="https://staging-api.ainflue.com"
    else
        api_endpoint="http://localhost:8000"
    fi
    
    # Check API health
    print_status "Checking API health at $api_endpoint..."
    
    if [[ $DRY_RUN == false ]]; then
        local max_attempts=30
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -f -s "$api_endpoint/health" > /dev/null; then
                print_success "API health check passed"
                break
            else
                print_status "Attempt $attempt/$max_attempts: API not ready yet..."
                sleep 10
                ((attempt++))
            fi
        done
        
        if [[ $attempt -gt $max_attempts ]]; then
            print_error "API health check failed after $max_attempts attempts"
            exit 1
        fi
    fi
    
    print_success "Health checks completed"
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        local color
        case $status in
            success) color="good" ;;
            error) color="danger" ;;
            warning) color="warning" ;;
            *) color="#439FE0" ;;
        esac
        
        local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "Ainflue Deployment Notification",
            "fields": [
                {
                    "title": "Environment",
                    "value": "$ENVIRONMENT",
                    "short": true
                },
                {
                    "title": "Version",
                    "value": "$IMAGE_TAG",
                    "short": true
                },
                {
                    "title": "Status",
                    "value": "$status",
                    "short": true
                },
                {
                    "title": "Deployed By",
                    "value": "$(whoami)",
                    "short": true
                }
            ],
            "text": "$message",
            "ts": $(date +%s)
        }
    ]
}
EOF
        )
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$payload" \
            "$SLACK_WEBHOOK_URL" &> /dev/null || true
    fi
}

# Rollback deployment
rollback_deployment() {
    print_error "Deployment failed. Initiating rollback..."
    
    local deployments=(
        "ainflue-api"
        "ainflue-crawler"
        "ainflue-analytics"
        "ainflue-ai-engine"
    )
    
    for deployment in "${deployments[@]}"; do
        print_status "Rolling back $deployment..."
        
        if [[ $DRY_RUN == false ]]; then
            kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE" || true
        fi
    done
    
    send_notification "error" "Deployment failed and was rolled back"
    exit 1
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Remove temporary files
    rm -f /tmp/ainflue-deploy-*
    
    # Logout from Docker registry
    docker logout "$DOCKER_REGISTRY" &> /dev/null || true
}

# Main deployment function
main() {
    print_status "Starting Ainflue Platform Deployment"
    print_status "Environment: $ENVIRONMENT"
    print_status "Namespace: $NAMESPACE"
    print_status "Image Tag: $IMAGE_TAG"
    print_status "Docker Registry: $DOCKER_REGISTRY"
    
    if [[ $DRY_RUN == true ]]; then
        print_warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Trap errors for rollback
    trap rollback_deployment ERR
    
    # Set cleanup trap
    trap cleanup EXIT
    
    # Execute deployment steps
    check_prerequisites
    validate_environment
    run_tests
    build_images
    push_images
    deploy_kubernetes
    wait_for_deployment
    run_health_checks
    
    # Success notification
    local deployment_time=$(date)
    print_success "🎉 Deployment completed successfully!"
    print_success "Environment: $ENVIRONMENT"
    print_success "Version: $IMAGE_TAG"
    print_success "Time: $deployment_time"
    
    send_notification "success" "Deployment completed successfully at $deployment_time"
    
    # Show useful information
    cat << EOF

📊 Deployment Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment:    $ENVIRONMENT
Namespace:      $NAMESPACE
Version:        $IMAGE_TAG
Registry:       $DOCKER_REGISTRY
Deployed At:    $deployment_time
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 Useful Commands:
• View pods:        kubectl get pods -n $NAMESPACE
• View services:    kubectl get svc -n $NAMESPACE
• View logs:        kubectl logs -f deployment/ainflue-api -n $NAMESPACE
• Scale deployment: kubectl scale deployment ainflue-api --replicas=5 -n $NAMESPACE

📧 Support: mlaiel@live.de
© 2025 Fahed Mlaiel. All rights reserved.

EOF
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi