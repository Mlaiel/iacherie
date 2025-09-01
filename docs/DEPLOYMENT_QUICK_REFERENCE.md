# 🚀 Deployment Quick Reference

## Manual Deployment Triggers

### Standard Production Deployment
```bash
gh workflow run production-deployment.yml \
  -f environment=production \
  -f deployment_type=blue-green \
  -f skip_approval=false
```

### Canary Deployment
```bash
gh workflow run production-deployment.yml \
  -f environment=production \
  -f deployment_type=canary \
  -f skip_approval=false
```

### Emergency Deployment
```bash
gh workflow run emergency-deployment.yml \
  -f emergency_type=critical-bugfix \
  -f severity=critical \
  -f image_tag=v1.2.3-hotfix \
  -f description="Fix critical payment processing bug" \
  -f approver=lead-engineer
```

### Scheduled Maintenance Deployment
```bash
gh workflow run deployment-scheduling.yml \
  -f deployment_type=maintenance-window \
  -f maintenance_duration=60 \
  -f deployment_strategy=blue-green \
  -f environment=production
```

## Health Monitoring Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | > 2% | Auto-rollback |
| Response Time P95 | > 2s | Auto-rollback |
| CPU Usage | > 80% | Auto-rollback |
| Memory Usage | > 85% | Auto-rollback |
| User Complaints | > 10/10min | Auto-rollback |
| Revenue Impact | > 1% | Auto-rollback |

## Deployment Status Checks

```bash
# Check deployment status
kubectl get deployments -n ainflue-production

# Check service health
curl https://api.ainflue.com/health

# View deployment logs
kubectl logs -n ainflue-production deployment/ainflue-api-green

# Check rollback status
kubectl get pods -n ainflue-production -l version=blue
```

## Emergency Contacts

- **DevOps**: devops@ainflue.com
- **On-Call**: +1-xxx-xxx-xxxx
- **Slack**: #deployment-alerts
- **Escalation**: cto@ainflue.com

## Quick Rollback (Manual)

```bash
# Manual rollback to blue deployment
kubectl patch service ainflue-api -n ainflue \
  -p '{"spec":{"selector":{"version":"blue"}}}'

kubectl scale deployment ainflue-api-blue -n ainflue --replicas=3
kubectl scale deployment ainflue-api-green -n ainflue --replicas=0
```

## Feature Flag Emergency Disable

```bash
# Disable feature via API (if implemented)
curl -X POST https://api.ainflue.com/api/v1/features/emergency-disable \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"feature_key": "problematic_feature", "reason": "deployment issue"}'
```