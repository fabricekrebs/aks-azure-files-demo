# Azure Files Demo for AKS

Simple demo application showing Azure Files integration with AKS using persistent volumes.

## What it does

- Demonstrates Azure Files with Kubernetes persistent storage
- Creates sample data continuously for backup testing
- Provides web interface to monitor file operations
- Shows data persistence across pod restarts

## Deploy

```bash
# Clone and deploy
git clone https://github.com/fabricekrebs/aks-azure-files-demo.git
cd aks-azure-files-demo
kubectl apply -k k8s/

# Check status
kubectl get pods -n azure-files-demo
```

## Access

**Port forward:**
```bash
kubectl port-forward -n azure-files-demo service/azure-files-demo-service 8080:80
# Open http://localhost:8080
```

**Ingress (optional):**
```bash
# Edit k8s/ingress.yaml with your domain, then access via ingress
```

## Data Structure

The app creates files in `/data/` with this structure:
```
/data/
├── logs/           # Application and metrics logs
├── uploads/        # Simulated user files
└── backup-test/    # Test files for backup scenarios
```

## Testing

**Verify persistence:**
```bash
# Count files, restart pod, count again (should be same)
kubectl exec -n azure-files-demo deployment/azure-files-demo -- find /data -type f | wc -l
kubectl rollout restart -n azure-files-demo deployment/azure-files-demo
kubectl exec -n azure-files-demo deployment/azure-files-demo -- find /data -type f | wc -l
```

**Backup testing:**
```bash
# Create backup
kubectl exec -n azure-files-demo deployment/azure-files-demo -- tar -czf /tmp/backup.tar.gz /data
```

## Monitoring

```bash
# Check storage
kubectl get pvc -n azure-files-demo
kubectl exec -n azure-files-demo deployment/azure-files-demo -- df -h /data

# View logs
kubectl logs -n azure-files-demo deployment/azure-files-demo
kubectl exec -n azure-files-demo deployment/azure-files-demo -- tail -f /data/activity.log
```

## Cleanup

```bash
kubectl delete -k k8s/
```

## GitOps

Point your GitOps tool (ArgoCD/Flux) to this repository with path: `k8s/`
