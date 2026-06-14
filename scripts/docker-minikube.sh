echo -e "Starting deployment...$"

echo -e "Building Docker image in Minikube..."
eval $(minikube docker-env)
docker build -t aura-app:v1 .

echo "Creating pod..."

kubectl delete pod aura-app --ignore-not-found=true
kubectl delete service aura-service --ignore-not-found=true

kubectl apply -f minikubectl-env.yaml

echo "Waiting for pod to be ready..."
kubectl wait --for=condition=ready pod/aura-app --timeout=60s

echo "Creating service..."
kubectl expose pod aura-app --name=aura-service --type=NodePort --port=5005

# Get the URL
echo "Deployment complete!"
echo "Your app is running at:"
minikube service aura-service --url

# Open in browser
minikube service aura-service
