#!/bin/bash
###############################################################################
# AUTOMATED GPU SETUP - Phase 3
# This script runs automatically once GPU node is ready
###############################################################################

set -e

echo "🚀 Starting automated GPU Phase 3 setup..."
echo ""

# Wait for GPU node to join cluster
echo "⏳ Waiting for GPU node to be Ready..."
timeout 600 bash -c 'until kubectl get nodes -l workload=gpu 2>/dev/null | grep -q Ready; do echo "  Still waiting for GPU node..."; sleep 10; done' || {
    echo "❌ Timeout waiting for GPU node"
    exit 1
}

echo "✅ GPU node detected!"
echo ""

# Show GPU node details
echo "📊 GPU Node Information:"
kubectl get nodes -l workload=gpu -o wide
echo ""

# Check GPU capacity
echo "📊 GPU Capacity:"
kubectl get nodes -l workload=gpu -o json | jq -r '.items[] | {name: .metadata.name, gpus: .status.capacity["nvidia.com/gpu"], instance: .metadata.labels["node.kubernetes.io/instance-type"]}'
echo ""

# Install NVIDIA Device Plugin if not already installed
if ! kubectl get daemonset -n kube-system nvidia-device-plugin-daemonset &>/dev/null; then
    echo "📦 Installing NVIDIA Device Plugin..."
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
    
    echo "⏳ Waiting for NVIDIA plugin to be ready..."
    sleep 30
    kubectl rollout status daemonset nvidia-device-plugin-daemonset -n kube-system --timeout=300s
    echo "✅ NVIDIA Device Plugin installed!"
else
    echo "✅ NVIDIA Device Plugin already installed"
fi

echo ""

# Verify GPUs are detected
echo "📊 Final GPU Verification:"
kubectl get nodes -l workload=gpu -o json | jq -r '.items[] | {name: .metadata.name, gpu_count: .status.capacity["nvidia.com/gpu"], gpu_allocatable: .status.allocatable["nvidia.com/gpu"]}'

echo ""
echo "🎉 GPU Phase 3 setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Deploy AI models: kubectl apply -f k8s/ai-models-deployment-phase3-fullstack.yaml"
echo "  2. Test GPUs: kubectl apply -f k8s/ai-model-test-phase3.yaml"
echo "  3. Monitor: kubectl top nodes -l workload=gpu"
echo ""
