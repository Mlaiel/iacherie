# Kubernetes Secrets Directory

This directory contains encrypted Kubernetes secrets for the Ainflue platform. 

## Security Notice

**⚠️ IMPORTANT: This directory is intentionally excluded from git via `.gitignore` for security reasons.**

Secret files should never be committed to version control as they contain sensitive information like:
- Database passwords
- API keys  
- JWT secrets
- Third-party service credentials
- SSL certificates

## Template Files

Template files with example values are provided in the `templates/` subdirectory. Use these as a starting point for creating your actual secret files:

1. Copy template files to this directory
2. Replace all example values with actual secrets
3. Apply to your Kubernetes cluster using `kubectl apply -f <secret-file>.yaml`

## Secret Management Best Practices

In production environments, consider using:

- **HashiCorp Vault** for centralized secret management
- **AWS Secrets Manager** for AWS-hosted applications  
- **Azure Key Vault** for Azure-hosted applications
- **Google Secret Manager** for GCP-hosted applications
- **Kubernetes External Secrets Operator** for automated secret synchronization

## Files Structure

```
k8s/secrets/
├── README.md                    # This file
├── templates/                   # Template files (safe to commit)
│   ├── api-gateway.yaml.template
│   ├── database.yaml.template
│   └── monitoring.yaml.template
├── api-gateway.yaml            # Actual secrets (gitignored)
├── database.yaml               # Actual secrets (gitignored)
└── monitoring.yaml             # Actual secrets (gitignored)
```

## Usage

```bash
# Create secrets from templates
cp templates/api-gateway.yaml.template api-gateway.yaml
cp templates/database.yaml.template database.yaml

# Edit with actual values
vim api-gateway.yaml
vim database.yaml

# Apply to cluster
kubectl apply -f api-gateway.yaml
kubectl apply -f database.yaml
```

## Encryption

All secret values should be base64 encoded before adding to the YAML files:

```bash
echo -n "your-secret-value" | base64
```

For additional security, consider using tools like:
- `sops` (Secrets OPerationS)
- `sealed-secrets`
- `age` encryption