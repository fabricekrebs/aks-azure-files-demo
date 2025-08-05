# Azure Files Demo for AKS

Modern Django web application demonstrating Azure Files integration with AKS using persistent volumes.

## Features

- **Django Backend**: RESTful API built with Django REST Framework
- **Modern Frontend**: Responsive web interface with JavaScript
- **Azure Files Integration**: Persistent file storage across pod restarts
- **Container Ready**: Optimized for deployment on Kubernetes
- **Health Monitoring**: Built-in health checks and monitoring
- **File Management**: Create, view, delete, and download files
- **Real-time Updates**: Dynamic file listing and content viewing

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │  Azure Files    │
│   (HTML/CSS/JS) │◄──►│   (REST API)    │◄──►│   (PVC Mount)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Build and Deploy

```bash
# Clone repository
git clone https://github.com/fabricekrebs/aks-azure-files-demo.git
cd aks-azure-files-demo

# Build the application
./build.sh

# Create namespace and deploy
kubectl create namespace azure-files-demo
kubectl apply -k k8s/ -n azure-files-demo

# Check deployment status
kubectl get pods -n azure-files-demo
kubectl logs -f deployment/azure-files-demo -n azure-files-demo
```

### Access the Application

**Port Forward (Development):**
```bash
kubectl port-forward -n azure-files-demo service/azure-files-demo-service 8080:80
# Open http://localhost:8080
```

**Ingress (Production):**
```bash
# Configure ingress in k8s/ingress.yaml with your domain
kubectl apply -f k8s/ingress.yaml -n azure-files-demo
# Access via your configured domain
```

## Development

### Local Development

```bash
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Visit http://localhost:8000 to see the application.

### Building Custom Image

```bash
# Build with custom registry
export AZURE_CONTAINER_REGISTRY="your-registry.azurecr.io"
./build.sh

# Or build manually
cd app
docker build -t azure-files-demo:latest .
```

## API Endpoints

The application provides the following REST API endpoints:

- `GET /api/health/` - Health check endpoint
- `GET /api/files/` - List all files
- `POST /api/files/` - Create a new file
- `GET /api/files/{filename}/` - Get file content
- `DELETE /api/files/{filename}/` - Delete a file

### Example API Usage

```bash
# Health check
curl http://localhost:8080/api/health/

# List files
curl http://localhost:8080/api/files/

# Create a file
curl -X POST http://localhost:8080/api/files/ \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.txt", "content": "Hello World!"}'

# Get file content
curl http://localhost:8080/api/files/test.txt/

# Delete file
curl -X DELETE http://localhost:8080/api/files/test.txt/
```

## Storage Configuration

The application uses Azure Files through a Kubernetes PersistentVolumeClaim:

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-files-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: azurefile-csi-premium
  resources:
    requests:
      storage: 10Gi
```

Files are stored in `/data` inside the container, which is mounted from the Azure Files share.

## Testing

### Verify Persistence
```bash
# Create a test file
kubectl exec -n azure-files-demo deployment/azure-files-demo -- \
  curl -X POST http://localhost:8000/api/files/ \
  -H "Content-Type: application/json" \
  -d '{"filename": "persistence-test.txt", "content": "This file should persist across restarts"}'

# Count files before restart
kubectl exec -n azure-files-demo deployment/azure-files-demo -- \
  find /data -type f | wc -l

# Restart deployment
kubectl rollout restart -n azure-files-demo deployment/azure-files-demo
kubectl rollout status -n azure-files-demo deployment/azure-files-demo

# Count files after restart (should be the same)
kubectl exec -n azure-files-demo deployment/azure-files-demo -- \
  find /data -type f | wc -l
```

### Performance Testing
```bash
# Test file operations
kubectl exec -n azure-files-demo deployment/azure-files-demo -- \
  curl -s http://localhost:8000/api/health/
```

## Monitoring

### Health Checks
The application includes comprehensive health checks:
- Liveness probe: `/api/health/`
- Readiness probe: `/api/health/`
- Storage accessibility verification

### Logs
```bash
# Application logs
kubectl logs -f deployment/azure-files-demo -n azure-files-demo

# Storage information
kubectl get pvc -n azure-files-demo
kubectl describe pvc azure-files-pvc -n azure-files-demo

# Pod information
kubectl describe pod -l app=azure-files-demo -n azure-files-demo
```

## Security

### Production Considerations
- Change the Django `SECRET_KEY` in deployment
- Enable HTTPS with proper TLS certificates
- Restrict `ALLOWED_HOSTS` in Django settings
- Use Azure Key Vault for secrets management
- Enable pod security policies
- Configure network policies for traffic isolation

### Environment Variables
- `SECRET_KEY`: Django secret key (change in production)
- `DEBUG`: Set to `False` in production
- `FILES_STORAGE_PATH`: Storage path (default: `/data`)
- `POD_NAME`: Automatically set by Kubernetes
- `NODE_NAME`: Automatically set by Kubernetes

## Troubleshooting

### Common Issues

**Pod fails to start:**
```bash
kubectl describe pod -l app=azure-files-demo -n azure-files-demo
kubectl logs deployment/azure-files-demo -n azure-files-demo
```

**Storage issues:**
```bash
kubectl describe pvc azure-files-pvc -n azure-files-demo
kubectl get storageclass azurefile-csi-premium
```

**Network connectivity:**
```bash
kubectl port-forward -n azure-files-demo service/azure-files-demo-service 8080:80
curl http://localhost:8080/api/health/
```

## Cleanup

```bash
# Delete the application
kubectl delete -k k8s/ -n azure-files-demo

# Delete the namespace
kubectl delete namespace azure-files-demo

# Remove local Docker image
docker rmi azure-files-demo:latest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the changes
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
