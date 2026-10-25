#!/bin/bash
set -e

# ==============================================================================
# Finlytics AI - AWS ECR & Kubernetes (EKS) Automated Deployment Script
# ==============================================================================

# Configurations (customize or set via environment)
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")}"
CLUSTER_NAME="${CLUSTER_NAME:-finlytics-cluster}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "❌ Error: AWS CLI is not configured or AWS_ACCOUNT_ID is not set."
    echo "Please run: aws configure"
    exit 1
fi

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo "======================================================"
echo "🚀 Target AWS Account:  $AWS_ACCOUNT_ID"
echo "🌐 Target AWS Region:   $AWS_REGION"
echo "📦 ECR Registry:        $ECR_REGISTRY"
echo "☸️  EKS Cluster:        $CLUSTER_NAME"
echo "🏷️  Image Tag:          $IMAGE_TAG"
echo "======================================================"

# Step 1: Login to Amazon ECR
echo "🔑 Logging in to Amazon ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Step 2: Ensure ECR Repositories exist
REPOS=("finlytics-backend" "finlytics-frontend" "finlytics-wisprflow")
for REPO in "${REPOS[@]}"; do
    if ! aws ecr describe-repositories --repository-names "$REPO" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "Creating ECR repository: $REPO..."
        aws ecr create-repository --repository-name "$REPO" --region "$AWS_REGION"
    else
        echo "✅ ECR repository exists: $REPO"
    fi
done

# Step 3: Build & Push Docker Images (multi-platform linux/amd64 for AWS EKS)
echo "🔨 Building and pushing Backend..."
docker build --platform linux/amd64 -t "${ECR_REGISTRY}/finlytics-backend:${IMAGE_TAG}" ./backend
docker push "${ECR_REGISTRY}/finlytics-backend:${IMAGE_TAG}"

echo "🔨 Building and pushing Frontend..."
docker build --platform linux/amd64 -t "${ECR_REGISTRY}/finlytics-frontend:${IMAGE_TAG}" ./frontend
docker push "${ECR_REGISTRY}/finlytics-frontend:${IMAGE_TAG}"

echo "🔨 Building and pushing Wisprflow..."
docker build --platform linux/amd64 -t "${ECR_REGISTRY}/finlytics-wisprflow:${IMAGE_TAG}" ./wisprflow
docker push "${ECR_REGISTRY}/finlytics-wisprflow:${IMAGE_TAG}"

# Step 4: Update K8s manifests with the ECR image paths
echo "☸️  Preparing Kubernetes manifests..."
sed -i.bak "s|image: finlytics-backend:latest|image: ${ECR_REGISTRY}/finlytics-backend:${IMAGE_TAG}|g" k8s/backend.yaml && rm -f k8s/backend.yaml.bak
sed -i.bak "s|image: finlytics-frontend:latest|image: ${ECR_REGISTRY}/finlytics-frontend:${IMAGE_TAG}|g" k8s/frontend.yaml && rm -f k8s/frontend.yaml.bak
sed -i.bak "s|image: finlytics-wisprflow:latest|image: ${ECR_REGISTRY}/finlytics-wisprflow:${IMAGE_TAG}|g" k8s/wisprflow.yaml && rm -f k8s/wisprflow.yaml.bak

# Step 5: Check kubeconfig connectivity
echo "🔍 Checking cluster connectivity..."
if kubectl cluster-info >/dev/null 2>&1; then
    echo "Applying Namespace & Configs..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    
    # Prompt for secret if not exists
    if ! kubectl get secret finlytics-secrets -n finlytics >/dev/null 2>&1; then
        if [ -n "$GEMINI_API_KEY" ]; then
            kubectl create secret generic finlytics-secrets \
                --namespace finlytics \
                --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY"
            echo "✅ Created finlytics-secrets from environment."
        else
            echo "⚠️ Warning: finlytics-secrets does not exist in namespace 'finlytics'."
            echo "Create it using: kubectl create secret generic finlytics-secrets -n finlytics --from-literal=GEMINI_API_KEY='<YOUR_KEY>'"
        fi
    fi

    echo "Deploying microservices..."
    kubectl apply -f k8s/wisprflow.yaml
    kubectl apply -f k8s/backend.yaml
    kubectl apply -f k8s/frontend.yaml
    kubectl apply -f k8s/ingress.yaml

    echo "🎉 Deployment initiated! Checking rollouts:"
    kubectl rollout status deployment/backend-deployment -n finlytics --timeout=120s || true
    kubectl rollout status deployment/frontend-deployment -n finlytics --timeout=120s || true
    kubectl rollout status deployment/wisprflow-deployment -n finlytics --timeout=120s || true

    echo "======================================================"
    echo "Ingress details:"
    kubectl get ingress finlytics-ingress -n finlytics
    echo "======================================================"
else
    echo "⚠️ Warning: No active Kubernetes context found. Manifests have been updated with ECR paths in ./k8s/"
    echo "When your EKS cluster is ready, connect and run: kubectl apply -f k8s/"
fi

