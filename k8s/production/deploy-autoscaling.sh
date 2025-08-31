#!/bin/bash
# Production Autoscaling Deployment Script for Ainflue Platform
# Deploys HPA, Cluster Autoscaler, Spot Instances, and SLA Monitoring
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

set -euo pipefail

# Configuration
NAMESPACE="ainflue-production"
KUBE_SYSTEM_NAMESPACE="kube-system"
CLUSTER_NAME="ainflue-production"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Get AWS Account ID if not provided
    if [[ -z "$AWS_ACCOUNT_ID" ]]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        log_info "Detected AWS Account ID: $AWS_ACCOUNT_ID"
    fi
    
    log_success "Prerequisites check completed"
}

# Create IAM roles for autoscaling components
create_iam_roles() {
    log_info "Creating IAM roles for autoscaling components..."
    
    # Cluster Autoscaler IAM Role
    cat > cluster-autoscaler-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/$(aws eks describe-cluster --name ${CLUSTER_NAME} --query 'cluster.identity.oidc.issuer' --output text | cut -d '/' -f 3-)"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "$(aws eks describe-cluster --name ${CLUSTER_NAME} --query 'cluster.identity.oidc.issuer' --output text | cut -d '/' -f 3-):sub": "system:serviceaccount:kube-system:cluster-autoscaler",
          "$(aws eks describe-cluster --name ${CLUSTER_NAME} --query 'cluster.identity.oidc.issuer' --output text | cut -d '/' -f 3-):aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF

    # Create Cluster Autoscaler IAM role
    if ! aws iam get-role --role-name cluster-autoscaler-role &> /dev/null; then
        aws iam create-role \
            --role-name cluster-autoscaler-role \
            --assume-role-policy-document file://cluster-autoscaler-trust-policy.json
        log_success "Created cluster-autoscaler-role"
    else
        log_info "cluster-autoscaler-role already exists"
    fi

    # Cluster Autoscaler IAM Policy
    cat > cluster-autoscaler-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeLaunchConfigurations",
                "autoscaling:DescribeTags",
                "autoscaling:SetDesiredCapacity",
                "autoscaling:TerminateInstanceInAutoScalingGroup",
                "ec2:DescribeLaunchTemplateVersions",
                "ec2:DescribeInstanceTypes"
            ],
            "Resource": "*"
        }
    ]
}
EOF

    # Attach policy to role
    if ! aws iam get-role-policy --role-name cluster-autoscaler-role --policy-name cluster-autoscaler-policy &> /dev/null; then
        aws iam put-role-policy \
            --role-name cluster-autoscaler-role \
            --policy-name cluster-autoscaler-policy \
            --policy-document file://cluster-autoscaler-policy.json
        log_success "Attached cluster-autoscaler-policy"
    else
        log_info "cluster-autoscaler-policy already attached"
    fi

    # Node Termination Handler IAM Role
    cat > node-termination-handler-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/$(aws eks describe-cluster --name ${CLUSTER_NAME} --query 'cluster.identity.oidc.issuer' --output text | cut -d '/' -f 3-)"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "$(aws eks describe-cluster --name ${CLUSTER_NAME} --query 'cluster.identity.oidc.issuer' --output text | cut -d '/' -f 3-):sub": "system:serviceaccount:kube-system:aws-node-termination-handler"
        }
      }
    }
  ]
}
EOF

    # Create Node Termination Handler IAM role
    if ! aws iam get-role --role-name aws-node-termination-handler-role &> /dev/null; then
        aws iam create-role \
            --role-name aws-node-termination-handler-role \
            --assume-role-policy-document file://node-termination-handler-trust-policy.json
        log_success "Created aws-node-termination-handler-role"
    else
        log_info "aws-node-termination-handler-role already exists"
    fi

    # Node Termination Handler IAM Policy
    cat > node-termination-handler-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:CompleteLifecycleAction",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeTags",
                "ec2:DescribeInstances",
                "sqs:DeleteMessage",
                "sqs:ReceiveMessage"
            ],
            "Resource": "*"
        }
    ]
}
EOF

    # Attach policy to role
    if ! aws iam get-role-policy --role-name aws-node-termination-handler-role --policy-name node-termination-handler-policy &> /dev/null; then
        aws iam put-role-policy \
            --role-name aws-node-termination-handler-role \
            --policy-name node-termination-handler-policy \
            --policy-document file://node-termination-handler-policy.json
        log_success "Attached node-termination-handler-policy"
    else
        log_info "node-termination-handler-policy already attached"
    fi

    # Clean up temporary files
    rm -f cluster-autoscaler-trust-policy.json cluster-autoscaler-policy.json
    rm -f node-termination-handler-trust-policy.json node-termination-handler-policy.json
    
    log_success "IAM roles creation completed"
}

# Update Kubernetes configurations with AWS Account ID
update_k8s_configs() {
    log_info "Updating Kubernetes configurations with AWS Account ID..."
    
    # Update cluster-autoscaler.yaml
    if [[ -f "cluster-autoscaler.yaml" ]]; then
        sed -i "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" cluster-autoscaler.yaml
        log_success "Updated cluster-autoscaler.yaml"
    fi
    
    # Update spot-node-groups.yaml
    if [[ -f "spot-node-groups.yaml" ]]; then
        sed -i "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" spot-node-groups.yaml
        log_success "Updated spot-node-groups.yaml"
    fi
}

# Deploy components in order
deploy_autoscaling_components() {
    log_info "Deploying autoscaling components..."
    
    # 1. Deploy namespaces
    log_info "Creating namespaces..."
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. Deploy autoscaling configuration
    log_info "Deploying autoscaling configuration..."
    if [[ -f "autoscaling-config.yaml" ]]; then
        kubectl apply -f autoscaling-config.yaml
        log_success "Applied autoscaling-config.yaml"
    fi
    
    # 3. Deploy HPA configurations
    log_info "Deploying HPA configurations..."
    if [[ -f "hpa.yaml" ]]; then
        kubectl apply -f hpa.yaml
        log_success "Applied hpa.yaml"
    fi
    
    # 4. Deploy Cluster Autoscaler
    log_info "Deploying Cluster Autoscaler..."
    if [[ -f "cluster-autoscaler.yaml" ]]; then
        kubectl apply -f cluster-autoscaler.yaml
        log_success "Applied cluster-autoscaler.yaml"
    fi
    
    # 5. Deploy Spot Instance configurations (informational)
    log_info "Spot instance configurations available in spot-node-groups.yaml"
    log_warning "Note: Spot instance node groups should be created via Terraform or AWS CLI"
    
    # 6. Deploy SLA monitoring rules
    log_info "Deploying SLA monitoring rules..."
    if [[ -f "../monitoring/prometheus/sla_alert_rules.yml" ]]; then
        # Create ConfigMap for SLA rules
        kubectl create configmap sla-alert-rules \
            --from-file=../monitoring/prometheus/sla_alert_rules.yml \
            --namespace=monitoring \
            --dry-run=client -o yaml | kubectl apply -f -
        log_success "Applied SLA alert rules"
    fi
    
    log_success "Autoscaling components deployment completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying autoscaling deployment..."
    
    # Check HPA status
    log_info "Checking HPA status..."
    kubectl get hpa -n $NAMESPACE
    
    # Check Cluster Autoscaler
    log_info "Checking Cluster Autoscaler status..."
    kubectl get deployment cluster-autoscaler -n $KUBE_SYSTEM_NAMESPACE
    
    # Check if Cluster Autoscaler is running
    if kubectl get pods -n $KUBE_SYSTEM_NAMESPACE -l app=cluster-autoscaler | grep -q Running; then
        log_success "Cluster Autoscaler is running"
    else
        log_warning "Cluster Autoscaler may not be running yet"
    fi
    
    # Check Node Termination Handler
    log_info "Checking Node Termination Handler status..."
    kubectl get daemonset aws-node-termination-handler -n $KUBE_SYSTEM_NAMESPACE
    
    # Check autoscaling policy engine
    log_info "Checking Autoscaling Policy Engine status..."
    kubectl get deployment autoscaling-policy-engine -n $NAMESPACE
    
    # Show current node status
    log_info "Current node status:"
    kubectl get nodes -o wide
    
    log_success "Deployment verification completed"
}

# Show post-deployment instructions
show_post_deployment_instructions() {
    log_info "Post-deployment instructions:"
    echo ""
    echo "1. Monitor autoscaling activity:"
    echo "   kubectl logs -f deployment/cluster-autoscaler -n kube-system"
    echo ""
    echo "2. Check HPA metrics:"
    echo "   kubectl get hpa -n $NAMESPACE --watch"
    echo ""
    echo "3. View SLA monitoring dashboard:"
    echo "   Access Grafana at your configured URL"
    echo ""
    echo "4. Test autoscaling:"
    echo "   kubectl run autoscaling-validation --rm -i --tty --image=curlimages/curl -- sh"
    echo ""
    echo "5. Monitor costs:"
    echo "   Check AWS Cost Explorer for spot instance savings"
    echo ""
    echo "6. Create spot instance node groups (if using EKS):"
    echo "   Use the Terraform configuration in spot-node-groups.yaml ConfigMap"
    echo ""
    log_success "Autoscaling setup completed! 🚀"
}

# Main execution
main() {
    log_info "Starting Ainflue Production Autoscaling Deployment"
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Region: $AWS_REGION"
    log_info "Namespace: $NAMESPACE"
    echo ""
    
    check_prerequisites
    create_iam_roles
    update_k8s_configs
    deploy_autoscaling_components
    
    # Wait for components to start
    log_info "Waiting for components to start..."
    sleep 30
    
    verify_deployment
    show_post_deployment_instructions
}

# Handle script arguments
case "${1:-}" in
    --check)
        check_prerequisites
        ;;
    --iam-only)
        check_prerequisites
        create_iam_roles
        ;;
    --deploy-only)
        deploy_autoscaling_components
        ;;
    --verify)
        verify_deployment
        ;;
    *)
        main
        ;;
esac