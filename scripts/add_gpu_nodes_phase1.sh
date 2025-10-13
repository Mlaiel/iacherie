#!/bin/bash

###############################################################################
# GPU NODEGROUP CREATION - PHASE 1 (2 nodes)
# Author: Fahed Mlaiel
# Description: Création de 2 noeuds GPU g4dn.2xlarge pour IA Chérie
# Configuration: 2x NVIDIA T4 (16GB VRAM chacun), total 32GB VRAM
# Cost: $1,080/mois ($0.752/heure × 2 nodes × 730 heures)
###############################################################################

set -e

echo "🚀 Creating GPU nodegroup for IA Chérie - PHASE 1"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  - Cluster: iacherie-cluster"
echo "  - Region: eu-central-1"
echo "  - Instance Type: g4dn.2xlarge"
echo "  - GPU: 2x NVIDIA T4 (16GB VRAM each)"
echo "  - Nodes: Min=2, Max=4, Desired=2"
echo "  - Total VRAM: 32GB"
echo "  - Cost: ~$1,080/month"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Variables
CLUSTER_NAME="iacherie-cluster"
REGION="eu-central-1"
NODEGROUP_NAME="iacherie-gpu-nodes-phase1"
INSTANCE_TYPE="g4dn.2xlarge"
MIN_NODES=2
MAX_NODES=4
DESIRED_NODES=2

echo "📋 Step 1/4: Creating GPU nodegroup..."
echo "========================================"

# Créer le nodegroup GPU
eksctl create nodegroup \
  --cluster=$CLUSTER_NAME \
  --region=$REGION \
  --name=$NODEGROUP_NAME \
  --node-type=$INSTANCE_TYPE \
  --nodes=$DESIRED_NODES \
  --nodes-min=$MIN_NODES \
  --nodes-max=$MAX_NODES \
  --node-ami-family=AmazonLinux2 \
  --node-volume-size=100 \
  --node-labels="workload=gpu,gpu-type=nvidia-t4,phase=1" \
  --tags="Environment=production,Project=iacherie,GPU=nvidia-t4,Phase=1" \
  --asg-access \
  --managed

echo ""
echo "✅ GPU nodegroup created successfully!"
echo ""
echo "⏳ Step 2/4: Waiting for nodes to be ready..."
echo "=============================================="

# Attendre que les noeuds soient prêts
kubectl wait --for=condition=Ready nodes -l workload=gpu --timeout=600s

echo ""
echo "✅ GPU nodes are ready!"
echo ""
echo "📋 Step 3/4: Installing NVIDIA Device Plugin..."
echo "================================================="

# Installer le plugin NVIDIA Device Plugin pour Kubernetes
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

echo ""
echo "⏳ Waiting for NVIDIA plugin to be ready..."
sleep 30

# Vérifier que le plugin est déployé
kubectl rollout status daemonset nvidia-device-plugin-daemonset -n kube-system --timeout=300s

echo ""
echo "✅ NVIDIA Device Plugin installed!"
echo ""
echo "📋 Step 4/4: Verifying GPU availability..."
echo "==========================================="

# Vérifier les noeuds GPU
echo ""
echo "📊 GPU Nodes:"
kubectl get nodes -l workload=gpu -o wide

echo ""
echo "📊 GPU Capacity:"
kubectl get nodes -l workload=gpu -o json | jq -r '.items[] | {name: .metadata.name, gpu: .status.capacity["nvidia.com/gpu"], instance: .metadata.labels["node.kubernetes.io/instance-type"]}'

echo ""
echo "📊 Node Labels:"
kubectl get nodes -l workload=gpu -o json | jq -r '.items[] | {name: .metadata.name, labels: .metadata.labels}'

echo ""
echo "✅ GPU nodegroup Phase 1 setup complete!"
echo ""
echo "=================================================="
echo "🎯 NEXT STEPS:"
echo "=================================================="
echo ""
echo "1. Test GPU with test pod:"
echo "   kubectl apply -f k8s/ai-model-test-gpu.yaml"
echo ""
echo "2. Check test results:"
echo "   kubectl logs -f ai-model-test-pod"
echo ""
echo "3. Deploy AI models with GPU:"
echo "   kubectl apply -f k8s/ai-models-deployment-phase1.yaml"
echo ""
echo "4. Monitor GPU usage:"
echo "   kubectl top nodes -l workload=gpu"
echo ""
echo "5. Check NVIDIA metrics:"
echo "   kubectl exec -it <pod-name> -- nvidia-smi"
echo ""
echo "=================================================="
echo "💰 COST TRACKING:"
echo "=================================================="
echo ""
echo "Current configuration cost:"
echo "  - 2x g4dn.2xlarge: $0.752/hour each"
echo "  - Total: $1.504/hour = $1,080/month"
echo ""
echo "To scale to Phase 2 (add 3rd GPU):"
echo "  eksctl scale nodegroup --cluster=$CLUSTER_NAME --name=$NODEGROUP_NAME --nodes=3 --nodes-min=3"
echo "  Additional cost: +$540/month"
echo ""
echo "=================================================="
echo "🎉 GPU Phase 1 ready for AI generation!"
echo "=================================================="
