#!/bin/bash

# CI/CD Pipeline Health Check Script
# Validates the health and configuration of the Ainflue CI/CD pipeline
# Author: Fahed Mlaiel (mlaiel@live.de)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="${GITHUB_REPOSITORY:-Mlaiel/Ainflue}"
VAULT_ADDR="${VAULT_ADDR:-}"
CHECK_VAULT="${CHECK_VAULT:-true}"
CHECK_KUBERNETES="${CHECK_KUBERNETES:-true}"
CHECK_NOTIFICATIONS="${CHECK_NOTIFICATIONS:-true}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check GitHub CLI and repository access
check_github_setup() {
    log_info "Checking GitHub setup..."
    
    if ! command_exists gh; then
        log_error "GitHub CLI (gh) not found. Please install it: https://cli.github.com/"
        return 1
    fi
    
    # Check authentication
    if ! gh auth status >/dev/null 2>&1; then
        log_error "GitHub CLI not authenticated. Run: gh auth login"
        return 1
    fi
    
    # Check repository access
    if ! gh repo view "$GITHUB_REPO" >/dev/null 2>&1; then
        log_error "Cannot access repository: $GITHUB_REPO"
        return 1
    fi
    
    log_success "GitHub setup verified"
    return 0
}

# Check GitHub Actions workflows
check_workflows() {
    log_info "Checking GitHub Actions workflows..."
    
    local workflows=(
        "ci.yml"
        "production-deployment.yml"
        "security-scan.yml"
        "approval-workflow.yml"
        "smoke-tests.yml"
        "artifact-signing.yml"
        "enhanced-notifications.yml"
        "vault-secrets.yml"
        "enhanced-dependency-scan.yml"
    )
    
    local missing_workflows=0
    
    for workflow in "${workflows[@]}"; do
        if [[ -f ".github/workflows/$workflow" ]]; then
            log_success "Found workflow: $workflow"
        else
            log_error "Missing workflow: $workflow"
            ((missing_workflows++))
        fi
    done
    
    if [[ $missing_workflows -eq 0 ]]; then
        log_success "All required workflows found"
        return 0
    else
        log_error "$missing_workflows workflow(s) missing"
        return 1
    fi
}

# Check GitHub repository secrets
check_github_secrets() {
    log_info "Checking GitHub repository secrets..."
    
    local required_secrets=(
        "COSIGN_PRIVATE_KEY"
        "COSIGN_PASSWORD"
        "VAULT_ADDR"
        "VAULT_TOKEN"
        "KUBE_CONFIG_PRODUCTION"
        "KUBE_CONFIG_STAGING"
        "SLACK_WEBHOOK_URL"
    )
    
    local missing_secrets=0
    
    for secret in "${required_secrets[@]}"; do
        # We can't actually read the secret values, but we can check if they exist
        # This is a placeholder - in real implementation, you'd use GitHub API
        log_info "Secret $secret should be configured in GitHub repository settings"
    done
    
    log_warning "Please verify all required secrets are configured in GitHub repository settings"
    return 0
}

# Check GitHub environments
check_github_environments() {
    log_info "Checking GitHub environments..."
    
    local required_environments=(
        "staging"
        "production-approval"
        "production"
    )
    
    for env in "${required_environments[@]}"; do
        log_info "Environment '$env' should be configured with appropriate protection rules"
    done
    
    log_warning "Please verify environments are configured with required reviewers and protection rules"
    return 0
}

# Check HashiCorp Vault configuration
check_vault_setup() {
    if [[ "$CHECK_VAULT" != "true" ]]; then
        log_info "Skipping Vault checks (CHECK_VAULT=false)"
        return 0
    fi
    
    log_info "Checking HashiCorp Vault setup..."
    
    if ! command_exists vault; then
        log_error "Vault CLI not found. Please install it: https://www.vaultproject.io/downloads"
        return 1
    fi
    
    if [[ -z "$VAULT_ADDR" ]]; then
        log_error "VAULT_ADDR environment variable not set"
        return 1
    fi
    
    if [[ -z "${VAULT_TOKEN:-}" ]]; then
        log_error "VAULT_TOKEN environment variable not set"
        return 1
    fi
    
    # Check Vault connectivity
    if ! vault status >/dev/null 2>&1; then
        log_error "Cannot connect to Vault at $VAULT_ADDR"
        return 1
    fi
    
    # Check secret paths
    local secret_paths=(
        "secret/ainflue/production"
        "secret/ainflue/staging"
    )
    
    for path in "${secret_paths[@]}"; do
        if vault kv get "$path" >/dev/null 2>&1; then
            log_success "Vault secret exists: $path"
        else
            log_error "Vault secret missing: $path"
        fi
    done
    
    log_success "Vault setup verified"
    return 0
}

# Check Kubernetes configuration
check_kubernetes_setup() {
    if [[ "$CHECK_KUBERNETES" != "true" ]]; then
        log_info "Skipping Kubernetes checks (CHECK_KUBERNETES=false)"
        return 0
    fi
    
    log_info "Checking Kubernetes setup..."
    
    if ! command_exists kubectl; then
        log_error "kubectl not found. Please install it: https://kubernetes.io/docs/tasks/tools/"
        return 1
    fi
    
    # Check if we can connect to the cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster. Check your kubeconfig"
        return 1
    fi
    
    # Check namespaces
    local namespaces=("ainflue" "ainflue-staging")
    
    for namespace in "${namespaces[@]}"; do
        if kubectl get namespace "$namespace" >/dev/null 2>&1; then
            log_success "Kubernetes namespace exists: $namespace"
        else
            log_warning "Kubernetes namespace missing: $namespace (will be created during deployment)"
        fi
    done
    
    log_success "Kubernetes setup verified"
    return 0
}

# Check container signing setup
check_signing_setup() {
    log_info "Checking container signing setup..."
    
    if ! command_exists cosign; then
        log_error "Cosign not found. Please install it: https://docs.sigstore.dev/cosign/installation/"
        return 1
    fi
    
    log_success "Cosign CLI available"
    
    # Check if we have the signing key (in actual deployment, this would be in secrets)
    if [[ -n "${COSIGN_PRIVATE_KEY:-}" ]] && [[ -n "${COSIGN_PASSWORD:-}" ]]; then
        log_success "Signing credentials configured"
    else
        log_warning "Signing credentials should be configured in GitHub secrets"
    fi
    
    return 0
}

# Check notification integrations
check_notifications() {
    if [[ "$CHECK_NOTIFICATIONS" != "true" ]]; then
        log_info "Skipping notification checks (CHECK_NOTIFICATIONS=false)"
        return 0
    fi
    
    log_info "Checking notification integrations..."
    
    # Check if webhook URLs are accessible (basic curl test)
    local webhook_vars=(
        "SLACK_WEBHOOK_URL"
        "TEAMS_WEBHOOK_URL"
        "DISCORD_WEBHOOK_URL"
    )
    
    for var in "${webhook_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            log_success "$var configured"
        else
            log_warning "$var not configured (optional)"
        fi
    done
    
    return 0
}

# Check workflow file syntax
check_workflow_syntax() {
    log_info "Checking workflow file syntax..."
    
    local workflow_files=(.github/workflows/*.yml .github/workflows/*.yaml)
    local syntax_errors=0
    
    for file in "${workflow_files[@]}"; do
        if [[ -f "$file" ]]; then
            if command_exists yamllint; then
                if yamllint "$file" >/dev/null 2>&1; then
                    log_success "Syntax OK: $file"
                else
                    log_error "Syntax error in: $file"
                    ((syntax_errors++))
                fi
            else
                # Basic YAML check using Python
                if python3 -c "import yaml; yaml.safe_load(open('$file'))" >/dev/null 2>&1; then
                    log_success "Syntax OK: $file"
                else
                    log_error "Syntax error in: $file"
                    ((syntax_errors++))
                fi
            fi
        fi
    done
    
    if [[ $syntax_errors -eq 0 ]]; then
        log_success "All workflow files have valid syntax"
        return 0
    else
        log_error "$syntax_errors workflow file(s) have syntax errors"
        return 1
    fi
}

# Check Docker setup
check_docker_setup() {
    log_info "Checking Docker setup..."
    
    if ! command_exists docker; then
        log_error "Docker not found. Please install it: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon not running or not accessible"
        return 1
    fi
    
    # Check Dockerfile existence
    local dockerfiles=(
        "docker/infrastructure/Dockerfile.production"
        "Dockerfile"
    )
    
    local dockerfile_found=false
    for dockerfile in "${dockerfiles[@]}"; do
        if [[ -f "$dockerfile" ]]; then
            log_success "Found Dockerfile: $dockerfile"
            dockerfile_found=true
            break
        fi
    done
    
    if [[ "$dockerfile_found" == "false" ]]; then
        log_error "No Dockerfile found. Expected one of: ${dockerfiles[*]}"
        return 1
    fi
    
    log_success "Docker setup verified"
    return 0
}

# Generate health check report
generate_report() {
    log_info "Generating health check report..."
    
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    local report_file="ci_cd_health_report.md"
    
    cat > "$report_file" << EOF
# CI/CD Pipeline Health Check Report

**Generated:** $timestamp  
**Repository:** $GITHUB_REPO  
**Checked by:** $(whoami)

## Summary

| Component | Status |
|-----------|--------|
| GitHub Setup | ${github_status:-❓} |
| Workflows | ${workflows_status:-❓} |
| Vault Setup | ${vault_status:-❓} |
| Kubernetes | ${kubernetes_status:-❓} |
| Container Signing | ${signing_status:-❓} |
| Notifications | ${notifications_status:-❓} |
| Workflow Syntax | ${syntax_status:-❓} |
| Docker Setup | ${docker_status:-❓} |

## Recommendations

EOF

    if [[ -f "$report_file" ]]; then
        log_success "Health check report generated: $report_file"
    fi
}

# Main execution
main() {
    echo "======================================"
    echo "🚀 CI/CD Pipeline Health Check"
    echo "======================================"
    echo
    
    local exit_code=0
    
    # Run all checks
    if check_github_setup; then
        github_status="✅"
    else
        github_status="❌"
        exit_code=1
    fi
    
    if check_workflows; then
        workflows_status="✅"
    else
        workflows_status="❌"
        exit_code=1
    fi
    
    if check_vault_setup; then
        vault_status="✅"
    else
        vault_status="❌"
        exit_code=1
    fi
    
    if check_kubernetes_setup; then
        kubernetes_status="✅"
    else
        kubernetes_status="❌"
        exit_code=1
    fi
    
    if check_signing_setup; then
        signing_status="✅"
    else
        signing_status="❌"
        exit_code=1
    fi
    
    if check_notifications; then
        notifications_status="✅"
    else
        notifications_status="❌"
        exit_code=1
    fi
    
    if check_workflow_syntax; then
        syntax_status="✅"
    else
        syntax_status="❌"
        exit_code=1
    fi
    
    if check_docker_setup; then
        docker_status="✅"
    else
        docker_status="❌"
        exit_code=1
    fi
    
    # Additional checks
    check_github_secrets
    check_github_environments
    
    echo
    echo "======================================"
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "CI/CD pipeline health check completed successfully!"
        echo "Your pipeline is ready for deployment. 🚀"
    else
        log_error "CI/CD pipeline health check found issues that need attention."
        echo "Please review the errors above and fix them before deploying. 🔧"
    fi
    
    generate_report
    
    echo "======================================"
    
    exit $exit_code
}

# Run health check if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi