#!/bin/bash
#
# 🎮 SCRIPT D'AJOUT DE NODES GPU AU CLUSTER EKS
# ==============================================
# Ajoute des instances GPU (g4dn.xlarge) pour les modèles IA
#
# Author: Fahed Mlaiel
# Date: 2025-10-11

set -e

CLUSTER_NAME="iacherie-cluster"
REGION="eu-central-1"
NODEGROUP_NAME="iacherie-gpu-nodes"

echo "🎮 AJOUT DE NODES GPU AU CLUSTER EKS"
echo "====================================="
echo ""
echo "📊 Configuration:"
echo "   Cluster: $CLUSTER_NAME"
echo "   Region: $REGION"
echo "   NodeGroup: $NODEGROUP_NAME"
echo "   Instance Type: g4dn.xlarge (1x NVIDIA T4 GPU, 16GB)"
echo "   Min Nodes: 1"
echo "   Max Nodes: 3"
echo "   Desired: 1"
echo ""

# Vérifier si le nodegroup existe déjà
echo "🔍 Vérification du nodegroup existant..."
if aws eks describe-nodegroup \
    --cluster-name "$CLUSTER_NAME" \
    --nodegroup-name "$NODEGROUP_NAME" \
    --region "$REGION" > /dev/null 2>&1; then
    echo "✅ NodeGroup GPU existe déjà"
    echo ""
    echo "📊 Détails du nodegroup:"
    aws eks describe-nodegroup \
        --cluster-name "$CLUSTER_NAME" \
        --nodegroup-name "$NODEGROUP_NAME" \
        --region "$REGION" \
        --query 'nodegroup.{Status:status,InstanceTypes:instanceTypes,DesiredSize:scalingConfig.desiredSize,MinSize:scalingConfig.minSize,MaxSize:scalingConfig.maxSize}' \
        --output table
    exit 0
fi

echo "🚀 Création du nodegroup GPU..."
echo ""

# Obtenir les subnets du cluster
SUBNETS=$(aws eks describe-cluster \
    --name "$CLUSTER_NAME" \
    --region "$REGION" \
    --query 'cluster.resourcesVpcConfig.subnetIds' \
    --output text | tr '\t' ',')

echo "📍 Subnets: $SUBNETS"
echo ""

# Créer le nodegroup GPU
aws eks create-nodegroup \
    --cluster-name "$CLUSTER_NAME" \
    --nodegroup-name "$NODEGROUP_NAME" \
    --region "$REGION" \
    --scaling-config minSize=1,maxSize=3,desiredSize=1 \
    --instance-types g4dn.xlarge \
    --subnets $(echo $SUBNETS | tr ',' ' ') \
    --ami-type AL2_x86_64_GPU \
    --node-role arn:aws:iam::066712929164:role/iacherie-eks-node-role \
    --labels "workload=gpu,nvidia.com/gpu=true" \
    --tags "Name=iacherie-gpu-node,Environment=production,ManagedBy=AI-Leader"

echo ""
echo "⏳ Création en cours..."
echo "   Cela peut prendre 5-10 minutes..."
echo ""

# Attendre que le nodegroup soit actif
aws eks wait nodegroup-active \
    --cluster-name "$CLUSTER_NAME" \
    --nodegroup-name "$NODEGROUP_NAME" \
    --region "$REGION"

echo "✅ NodeGroup GPU créé avec succès!"
echo ""

# Installer le device plugin NVIDIA
echo "🔌 Installation du NVIDIA Device Plugin..."
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

echo ""
echo "⏳ Attente du déploiement du device plugin (30s)..."
sleep 30

# Vérifier les nodes GPU
echo ""
echo "📊 Nodes GPU disponibles:"
kubectl get nodes -l nvidia.com/gpu=true -o custom-columns=NAME:.metadata.name,INSTANCE:.metadata.labels.node\\.kubernetes\\.io/instance-type,GPU:.status.capacity.nvidia\\.com/gpu

echo ""
echo "🎉 INSTALLATION TERMINÉE!"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Vérifier: kubectl get nodes -l nvidia.com/gpu=true"
echo "   2. Tester: kubectl apply -f k8s/ai-model-test-gpu.yaml"
echo "   3. Logs: kubectl logs -n iacherie-prod ai-model-test-gpu"
echo ""

# Afficher les coûts
echo "💰 COÛTS ESTIMÉS:"
echo "   g4dn.xlarge: ~\$0.526/heure (~\$378/mois si 24/7)"
echo "   1x NVIDIA T4 GPU (16GB GDDR6)"
echo "   4 vCPU, 16GB RAM"
echo ""
echo "💡 Conseils:"
echo "   - Utiliser AutoScaling pour économiser"
echo "   - Scale to 0 la nuit si possible"
echo "   - Monitoring GPU avec nvidia-smi"
