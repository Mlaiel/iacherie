"""ETCD Backup and Restoration Manager
===================================

Automated ETCD backup with restoration testing
for the Ainflue platform Kubernetes cluster.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BackupProvider(Enum):
    """Backup storage providers"""
    AWS_S3 = "aws-s3"
    GCP_GCS = "gcp-gcs"
    AZURE_BLOB = "azure-blob"
    MINIO = "minio"


class BackupFrequency(Enum):
    """Backup frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class ETCDBackupConfig:
    """ETCD backup configuration"""
    provider: BackupProvider = BackupProvider.AWS_S3
    frequency: BackupFrequency = BackupFrequency.DAILY
    retention_days: int = 30
    bucket_name: str = "ia-influencer-etcd-backups"
    namespace: str = "kube-system"
    encryption_enabled: bool = True
    compression_enabled: bool = True


class ETCDBackupManager:
    """Manages ETCD backup and restoration operations"""
    
    def __init__(self, config: ETCDBackupConfig):
        self.config = config
    
    def create_backup_service_account(self) -> List[Dict[str, Any]]:
        """Create service account for ETCD backup operations"""
        return [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "etcd-backup",
                    "namespace": self.config.namespace,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                }
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "etcd-backup-role",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "nodes"],
                        "verbs": ["get", "list"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["secrets", "configmaps"],
                        "verbs": ["get", "list", "create", "update", "patch"]
                    },
                    {
                        "apiGroups": ["batch"],
                        "resources": ["jobs", "cronjobs"],
                        "verbs": ["get", "list", "create", "update", "patch", "delete"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": "etcd-backup-binding",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "etcd-backup",
                        "namespace": self.config.namespace
                    }
                ],
                "roleRef": {
                    "kind": "ClusterRole",
                    "name": "etcd-backup-role",
                    "apiGroup": "rbac.authorization.k8s.io"
                }
            }
        ]
    
    def create_backup_secret(self) -> Dict[str, Any]:
        """Create secret for backup storage credentials"""
        if self.config.provider == BackupProvider.AWS_S3:
            return {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "etcd-backup-credentials",
                    "namespace": self.config.namespace,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                },
                "type": "Opaque",
                "stringData": {
                    "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
                    "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
                    "AWS_DEFAULT_REGION": "${AWS_DEFAULT_REGION}"
                }
            }
        elif self.config.provider == BackupProvider.GCP_GCS:
            return {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "etcd-backup-credentials",
                    "namespace": self.config.namespace,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                },
                "type": "Opaque",
                "stringData": {
                    "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}"
                }
            }
        elif self.config.provider == BackupProvider.AZURE_BLOB:
            return {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "etcd-backup-credentials",
                    "namespace": self.config.namespace,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "etcd-backup"
                    }
                },
                "type": "Opaque",
                "stringData": {
                    "AZURE_STORAGE_ACCOUNT": "${AZURE_STORAGE_ACCOUNT}",
                    "AZURE_STORAGE_KEY": "${AZURE_STORAGE_KEY}"
                }
            }
        
        return {}
    
    def create_backup_configmap(self) -> Dict[str, Any]:
        """Create ConfigMap with backup scripts"""
        backup_script = self._generate_backup_script()
        restore_script = self._generate_restore_script()
        test_script = self._generate_test_script()
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "etcd-backup-scripts",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "etcd-backup"
                }
            },
            "data": {
                "backup.sh": backup_script,
                "restore.sh": restore_script,
                "test-restore.sh": test_script,
                "config.yaml": yaml.dump({
                    "backup": {
                        "provider": self.config.provider.value,
                        "bucket": self.config.bucket_name,
                        "retention_days": self.config.retention_days,
                        "encryption": self.config.encryption_enabled,
                        "compression": self.config.compression_enabled
                    }
                }, default_flow_style=False)
            }
        }
    
    def _generate_backup_script(self) -> str:
        """Generate ETCD backup script"""
        return """#!/bin/bash
set -euo pipefail

# Configuration
ETCD_ENDPOINTS=${ETCD_ENDPOINTS:-"https://127.0.0.1:2379"}
ETCD_CACERT=${ETCD_CACERT:-"/etc/kubernetes/pki/etcd/ca.crt"}
ETCD_CERT=${ETCD_CERT:-"/etc/kubernetes/pki/etcd/server.crt"}
ETCD_KEY=${ETCD_KEY:-"/etc/kubernetes/pki/etcd/server.key"}
BACKUP_DIR=${BACKUP_DIR:-"/backup"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="etcd-backup-${TIMESTAMP}"

echo "Starting ETCD backup at $(date)"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create ETCD snapshot
echo "Creating ETCD snapshot..."
ETCDCTL_API=3 etcdctl snapshot save "${BACKUP_DIR}/${BACKUP_NAME}.db" \\
    --endpoints="${ETCD_ENDPOINTS}" \\
    --cacert="${ETCD_CACERT}" \\
    --cert="${ETCD_CERT}" \\
    --key="${ETCD_KEY}"

# Verify snapshot
echo "Verifying snapshot..."
ETCDCTL_API=3 etcdctl snapshot status "${BACKUP_DIR}/${BACKUP_NAME}.db" \\
    --write-out=table

# Compress if enabled
if [ "${COMPRESSION_ENABLED:-true}" = "true" ]; then
    echo "Compressing backup..."
    gzip "${BACKUP_DIR}/${BACKUP_NAME}.db"
    BACKUP_FILE="${BACKUP_NAME}.db.gz"
else
    BACKUP_FILE="${BACKUP_NAME}.db"
fi

# Upload to storage
echo "Uploading backup to storage..."
case "${BACKUP_PROVIDER}" in
    "aws-s3")
        aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${BUCKET_NAME}/etcd-backups/${BACKUP_FILE}"
        ;;
    "gcp-gcs")
        gsutil cp "${BACKUP_DIR}/${BACKUP_FILE}" "gs://${BUCKET_NAME}/etcd-backups/${BACKUP_FILE}"
        ;;
    "azure-blob")
        az storage blob upload --file "${BACKUP_DIR}/${BACKUP_FILE}" \\
            --container-name etcd-backups --name "${BACKUP_FILE}" \\
            --account-name "${AZURE_STORAGE_ACCOUNT}"
        ;;
esac

# Cleanup old backups
echo "Cleaning up old backups..."
case "${BACKUP_PROVIDER}" in
    "aws-s3")
        aws s3api list-objects-v2 --bucket "${BUCKET_NAME}" --prefix "etcd-backups/" \\
            --query "Contents[?LastModified<'$(date -d "${RETENTION_DAYS} days ago" --iso-8601)'].Key" \\
            --output text | xargs -r -I {} aws s3 rm "s3://${BUCKET_NAME}/{}"
        ;;
    "gcp-gcs")
        gsutil -m rm "gs://${BUCKET_NAME}/etcd-backups/$(gsutil ls -l gs://${BUCKET_NAME}/etcd-backups/ | awk '$1 < "'$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%dT%H:%M:%S)'" {print $3}')"
        ;;
esac

# Store backup metadata
cat > "${BACKUP_DIR}/metadata.json" << EOF
{
    "timestamp": "${TIMESTAMP}",
    "backup_file": "${BACKUP_FILE}",
    "cluster_version": "$(kubectl version --short | grep Server)",
    "node_count": "$(kubectl get nodes --no-headers | wc -l)",
    "namespace_count": "$(kubectl get namespaces --no-headers | wc -l)"
}
EOF

echo "ETCD backup completed successfully at $(date)"
"""
    
    def _generate_restore_script(self) -> str:
        """Generate ETCD restore script"""
        return """#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_FILE=${1:-""}
ETCD_DATA_DIR=${ETCD_DATA_DIR:-"/var/lib/etcd"}
ETCD_NAME=${ETCD_NAME:-"default"}
ETCD_INITIAL_CLUSTER=${ETCD_INITIAL_CLUSTER:-"default=https://127.0.0.1:2380"}
ETCD_INITIAL_ADVERTISE_PEER_URLS=${ETCD_INITIAL_ADVERTISE_PEER_URLS:-"https://127.0.0.1:2380"}

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

echo "Starting ETCD restore from ${BACKUP_FILE} at $(date)"

# Stop ETCD (this would typically be done by the orchestrator)
echo "WARNING: This script is for reference. ETCD restoration requires cluster coordination."

# Download backup if needed
if [[ "${BACKUP_FILE}" == s3://* ]] || [[ "${BACKUP_FILE}" == gs://* ]]; then
    echo "Downloading backup file..."
    LOCAL_BACKUP="/tmp/$(basename ${BACKUP_FILE})"
    case "${BACKUP_FILE}" in
        s3://*)
            aws s3 cp "${BACKUP_FILE}" "${LOCAL_BACKUP}"
            ;;
        gs://*)
            gsutil cp "${BACKUP_FILE}" "${LOCAL_BACKUP}"
            ;;
    esac
    BACKUP_FILE="${LOCAL_BACKUP}"
fi

# Decompress if needed
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    echo "Decompressing backup..."
    gunzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# Verify backup before restore
echo "Verifying backup integrity..."
ETCDCTL_API=3 etcdctl snapshot status "${BACKUP_FILE}" --write-out=table

# Backup current data directory
if [ -d "${ETCD_DATA_DIR}" ]; then
    echo "Backing up current ETCD data directory..."
    mv "${ETCD_DATA_DIR}" "${ETCD_DATA_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Restore from snapshot
echo "Restoring ETCD from snapshot..."
ETCDCTL_API=3 etcdctl snapshot restore "${BACKUP_FILE}" \\
    --name="${ETCD_NAME}" \\
    --initial-cluster="${ETCD_INITIAL_CLUSTER}" \\
    --initial-cluster-token=etcd-cluster-1 \\
    --initial-advertise-peer-urls="${ETCD_INITIAL_ADVERTISE_PEER_URLS}" \\
    --data-dir="${ETCD_DATA_DIR}"

echo "ETCD restore completed. Please restart the ETCD cluster."
echo "Restore completed at $(date)"
"""
    
    def _generate_test_script(self) -> str:
        """Generate restoration test script"""
        return """#!/bin/bash
set -euo pipefail

echo "Starting ETCD backup restoration test at $(date)"

# Configuration
TEST_NAMESPACE="etcd-restore-test"
TEST_BACKUP_DIR="/tmp/etcd-test"
LATEST_BACKUP=""

# Find latest backup
case "${BACKUP_PROVIDER}" in
    "aws-s3")
        LATEST_BACKUP=$(aws s3 ls "s3://${BUCKET_NAME}/etcd-backups/" | sort | tail -n 1 | awk '{print $4}')
        ;;
    "gcp-gcs")
        LATEST_BACKUP=$(gsutil ls "gs://${BUCKET_NAME}/etcd-backups/" | sort | tail -n 1 | xargs basename)
        ;;
esac

if [ -z "${LATEST_BACKUP}" ]; then
    echo "No backup found for testing"
    exit 1
fi

echo "Testing backup: ${LATEST_BACKUP}"

# Download and verify backup
mkdir -p "${TEST_BACKUP_DIR}"
case "${BACKUP_PROVIDER}" in
    "aws-s3")
        aws s3 cp "s3://${BUCKET_NAME}/etcd-backups/${LATEST_BACKUP}" "${TEST_BACKUP_DIR}/${LATEST_BACKUP}"
        ;;
    "gcp-gcs")
        gsutil cp "gs://${BUCKET_NAME}/etcd-backups/${LATEST_BACKUP}" "${TEST_BACKUP_DIR}/${LATEST_BACKUP}"
        ;;
esac

# Decompress if needed
BACKUP_FILE="${TEST_BACKUP_DIR}/${LATEST_BACKUP}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    gunzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# Verify backup integrity
echo "Verifying backup integrity..."
ETCDCTL_API=3 etcdctl snapshot status "${BACKUP_FILE}" --write-out=table

if [ $? -eq 0 ]; then
    echo "✅ Backup verification PASSED"
else
    echo "❌ Backup verification FAILED"
    exit 1
fi

# Test restoration (dry run)
echo "Testing restoration process..."
TEST_DATA_DIR="${TEST_BACKUP_DIR}/etcd-data"
ETCDCTL_API=3 etcdctl snapshot restore "${BACKUP_FILE}" \\
    --name=test \\
    --initial-cluster=test=https://127.0.0.1:2380 \\
    --initial-cluster-token=test-cluster \\
    --initial-advertise-peer-urls=https://127.0.0.1:2380 \\
    --data-dir="${TEST_DATA_DIR}"

if [ $? -eq 0 ] && [ -d "${TEST_DATA_DIR}" ]; then
    echo "✅ Restoration test PASSED"
    rm -rf "${TEST_DATA_DIR}"
else
    echo "❌ Restoration test FAILED"
    exit 1
fi

# Create test report
cat > "${TEST_BACKUP_DIR}/test-report.json" << EOF
{
    "test_timestamp": "$(date --iso-8601)",
    "backup_file": "${LATEST_BACKUP}",
    "backup_size_bytes": $(stat -c%s "${BACKUP_FILE}"),
    "verification_status": "PASSED",
    "restoration_test_status": "PASSED",
    "test_duration_seconds": ${SECONDS}
}
EOF

# Upload test report
case "${BACKUP_PROVIDER}" in
    "aws-s3")
        aws s3 cp "${TEST_BACKUP_DIR}/test-report.json" "s3://${BUCKET_NAME}/etcd-test-reports/test-report-$(date +%Y%m%d_%H%M%S).json"
        ;;
    "gcp-gcs")
        gsutil cp "${TEST_BACKUP_DIR}/test-report.json" "gs://${BUCKET_NAME}/etcd-test-reports/test-report-$(date +%Y%m%d_%H%M%S).json"
        ;;
esac

# Cleanup
rm -rf "${TEST_BACKUP_DIR}"

echo "✅ ETCD backup restoration test completed successfully at $(date)"
"""
    
    def create_backup_cronjob(self) -> Dict[str, Any]:
        """Create CronJob for automated ETCD backups"""
        schedule_map = {
            BackupFrequency.HOURLY: "0 * * * *",
            BackupFrequency.DAILY: "0 2 * * *",  # 2 AM daily
            BackupFrequency.WEEKLY: "0 2 * * 0"  # 2 AM on Sunday
        }
        
        return {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": "etcd-backup",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "etcd-backup"
                }
            },
            "spec": {
                "schedule": schedule_map[self.config.frequency],
                "concurrencyPolicy": "Forbid",
                "failedJobsHistoryLimit": 3,
                "successfulJobsHistoryLimit": 5,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "metadata": {
                                "labels": {
                                    "app.kubernetes.io/name": "ia-influencer",
                                    "app.kubernetes.io/component": "etcd-backup"
                                }
                            },
                            "spec": {
                                "serviceAccountName": "etcd-backup",
                                "hostNetwork": True,
                                "restartPolicy": "OnFailure",
                                "containers": [
                                    {
                                        "name": "etcd-backup",
                                        "image": "quay.io/coreos/etcd:v3.5.9",
                                        "command": ["/bin/sh"],
                                        "args": ["/scripts/backup.sh"],
                                        "env": [
                                            {
                                                "name": "BACKUP_PROVIDER",
                                                "value": self.config.provider.value
                                            },
                                            {
                                                "name": "BUCKET_NAME",
                                                "value": self.config.bucket_name
                                            },
                                            {
                                                "name": "RETENTION_DAYS",
                                                "value": str(self.config.retention_days)
                                            },
                                            {
                                                "name": "COMPRESSION_ENABLED",
                                                "value": str(self.config.compression_enabled).lower()
                                            }
                                        ],
                                        "envFrom": [
                                            {
                                                "secretRef": {
                                                    "name": "etcd-backup-credentials"
                                                }
                                            }
                                        ],
                                        "volumeMounts": [
                                            {
                                                "name": "etcd-certs",
                                                "mountPath": "/etc/kubernetes/pki/etcd",
                                                "readOnly": True
                                            },
                                            {
                                                "name": "backup-scripts",
                                                "mountPath": "/scripts"
                                            },
                                            {
                                                "name": "backup-storage",
                                                "mountPath": "/backup"
                                            }
                                        ],
                                        "resources": {
                                            "requests": {
                                                "cpu": "100m",
                                                "memory": "256Mi"
                                            },
                                            "limits": {
                                                "cpu": "500m",
                                                "memory": "1Gi"
                                            }
                                        }
                                    }
                                ],
                                "volumes": [
                                    {
                                        "name": "etcd-certs",
                                        "hostPath": {
                                            "path": "/etc/kubernetes/pki/etcd",
                                            "type": "DirectoryOrCreate"
                                        }
                                    },
                                    {
                                        "name": "backup-scripts",
                                        "configMap": {
                                            "name": "etcd-backup-scripts",
                                            "defaultMode": 0o755
                                        }
                                    },
                                    {
                                        "name": "backup-storage",
                                        "emptyDir": {}
                                    }
                                ],
                                "nodeSelector": {
                                    "node-role.kubernetes.io/control-plane": ""
                                },
                                "tolerations": [
                                    {
                                        "key": "node-role.kubernetes.io/control-plane",
                                        "operator": "Exists",
                                        "effect": "NoSchedule"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    
    def create_restore_test_cronjob(self) -> Dict[str, Any]:
        """Create CronJob for testing backup restoration"""
        return {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": "etcd-restore-test",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "etcd-backup-test"
                }
            },
            "spec": {
                "schedule": "0 4 * * 1",  # 4 AM on Monday (weekly test)
                "concurrencyPolicy": "Forbid",
                "failedJobsHistoryLimit": 3,
                "successfulJobsHistoryLimit": 5,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "metadata": {
                                "labels": {
                                    "app.kubernetes.io/name": "ia-influencer",
                                    "app.kubernetes.io/component": "etcd-backup-test"
                                }
                            },
                            "spec": {
                                "serviceAccountName": "etcd-backup",
                                "restartPolicy": "OnFailure",
                                "containers": [
                                    {
                                        "name": "etcd-restore-test",
                                        "image": "quay.io/coreos/etcd:v3.5.9",
                                        "command": ["/bin/sh"],
                                        "args": ["/scripts/test-restore.sh"],
                                        "env": [
                                            {
                                                "name": "BACKUP_PROVIDER",
                                                "value": self.config.provider.value
                                            },
                                            {
                                                "name": "BUCKET_NAME",
                                                "value": self.config.bucket_name
                                            }
                                        ],
                                        "envFrom": [
                                            {
                                                "secretRef": {
                                                    "name": "etcd-backup-credentials"
                                                }
                                            }
                                        ],
                                        "volumeMounts": [
                                            {
                                                "name": "backup-scripts",
                                                "mountPath": "/scripts"
                                            }
                                        ],
                                        "resources": {
                                            "requests": {
                                                "cpu": "100m",
                                                "memory": "256Mi"
                                            },
                                            "limits": {
                                                "cpu": "500m",
                                                "memory": "1Gi"
                                            }
                                        }
                                    }
                                ],
                                "volumes": [
                                    {
                                        "name": "backup-scripts",
                                        "configMap": {
                                            "name": "etcd-backup-scripts",
                                            "defaultMode": 0o755
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all ETCD backup manifests"""
        manifests = {}
        
        # Service account and RBAC
        rbac_resources = self.create_backup_service_account()
        for i, resource in enumerate(rbac_resources):
            manifests[f"etcd-backup-rbac-{i+1}"] = yaml.dump(resource, default_flow_style=False)
        
        # Credentials secret
        secret = self.create_backup_secret()
        if secret:
            manifests["etcd-backup-secret"] = yaml.dump(secret, default_flow_style=False)
        
        # ConfigMap with scripts
        configmap = self.create_backup_configmap()
        manifests["etcd-backup-configmap"] = yaml.dump(configmap, default_flow_style=False)
        
        # Backup CronJob
        backup_cronjob = self.create_backup_cronjob()
        manifests["etcd-backup-cronjob"] = yaml.dump(backup_cronjob, default_flow_style=False)
        
        # Restore test CronJob
        test_cronjob = self.create_restore_test_cronjob()
        manifests["etcd-restore-test-cronjob"] = yaml.dump(test_cronjob, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir: str = "./k8s-manifests/etcd-backup"):
        """Save all ETCD backup manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"ETCD backup manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['ETCDBackupManager', 'ETCDBackupConfig', 'BackupProvider', 'BackupFrequency']