#!/bin/bash
# Script pour vérifier les quotas AWS disponibles

echo "🔍 Vérification des quotas AWS..."
echo ""

REGION=${1:-eu-west-1}

echo "Region: $REGION"
echo "Account ID: 066712929164"
echo ""

echo "📊 EC2 vCPU Quotas:"
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-1216C47A \
  --region $REGION \
  --query 'Quota.Value' 2>/dev/null || echo "Besoin de configurer AWS CLI"

echo ""
echo "💾 EBS Storage Quotas:"
aws service-quotas get-service-quota \
  --service-code ebs \
  --quota-code L-D18FCD1D \
  --region $REGION \
  --query 'Quota.Value' 2>/dev/null || echo "Besoin de configurer AWS CLI"

echo ""
echo "🌐 Elastic IP Quotas:"
aws ec2 describe-account-attributes \
  --attribute-names max-elastic-ips \
  --region $REGION \
  --query 'AccountAttributes[0].AttributeValues[0].AttributeValue' 2>/dev/null || echo "Besoin de configurer AWS CLI"

echo ""
echo "✅ Script terminé"
