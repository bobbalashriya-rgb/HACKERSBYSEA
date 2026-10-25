# Finlytics AI - AWS EKS & Docker Deployment Guide

This guide provides step-by-step instructions for containerizing the Finlytics AI multi-service project (`frontend`, `backend`, `wisprflow`) using **Docker**, pushing images to **Amazon ECR (Elastic Container Registry)**, and orchestrating them on **Amazon EKS (Elastic Kubernetes Service)**.

---

## 🏛️ Architecture Overview

```
                      Internet Traffic (Port 80/443)
                                  │
                                  ▼
                    [ AWS Application Load Balancer ]
                                  │
              ┌───────────────────┴───────────────────┐
              │ Ingress Route /api/*                  │ Ingress Route /*
              ▼                                       ▼
     [ backend-service ]                     [ frontend-service ]
     (FastAPI | Port 8000)                   (Nginx SPA | Port 80)
              │
              │ Internal DNS ClusterIP
              ▼
    [ wisprflow-service ]
    (FastAPI | Port 8002)
```

---

## 📋 Prerequisites

Ensure you have the following installed on your machine:
* **AWS CLI v2** configured with proper IAM permissions: `aws configure`
* **Docker** running locally: `docker --version`
* **kubectl** (Kubernetes CLI): `kubectl version --client`
* **eksctl** (CLI for managing EKS clusters): `eksctl version`

---

## 🧪 Local Testing with Docker Compose (Optional)

Before deploying to AWS, test all 3 containers locally:

```bash
# 1. Provide your Gemini key in .env or shell
export GEMINI_API_KEY="your_actual_key_here"

# 2. Build and launch all containers
docker compose up --build

# 3. Access in browser:
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
# Wisprflow: http://localhost:8002
```

---

## 🚀 Step 1: Create Amazon ECR Repositories

Log in to Amazon ECR and create the 3 microservice repositories:

```bash
# Set your AWS Region and retrieve your Account ID
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Create ECR Repositories
aws ecr create-repository --repository-name finlytics-backend --region $AWS_REGION || true
aws ecr create-repository --repository-name finlytics-frontend --region $AWS_REGION || true
aws ecr create-repository --repository-name finlytics-wisprflow --region $AWS_REGION || true
```

---

## 🔨 Step 2: Build & Push Multi-Platform Docker Images

Build for `linux/amd64` architecture (the standard architecture for AWS EKS worker nodes):

```bash
# 1. Build and push Backend
docker build --platform linux/amd64 -t $ECR_REGISTRY/finlytics-backend:latest ./backend
docker push $ECR_REGISTRY/finlytics-backend:latest

# 2. Build and push Frontend
docker build --platform linux/amd64 -t $ECR_REGISTRY/finlytics-frontend:latest ./frontend
docker push $ECR_REGISTRY/finlytics-frontend:latest

# 3. Build and push Wisprflow
docker build --platform linux/amd64 -t $ECR_REGISTRY/finlytics-wisprflow:latest ./wisprflow
docker push $ECR_REGISTRY/finlytics-wisprflow:latest
```

---

## ☸️ Step 3: Provision Amazon EKS Cluster

If you do not already have an active EKS cluster, create one using `eksctl`:

```bash
eksctl create cluster \
  --name finlytics-cluster \
  --region $AWS_REGION \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

Once provisioned, verify connectivity:
```bash
kubectl get nodes
```

---

## 🔐 Step 4: Configure Kubernetes Secrets & Namespace

Create the dedicated `finlytics` namespace and inject your Gemini API key securely:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Apply configmap
kubectl apply -f k8s/configmap.yaml

# 3. Create Secret for Gemini API key
kubectl create secret generic finlytics-secrets \
  --namespace finlytics \
  --from-literal=GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
```

---

## 📦 Step 5: Update Manifest Image Paths & Deploy

Update the image field in `k8s/backend.yaml`, `k8s/frontend.yaml`, and `k8s/wisprflow.yaml` to reference your AWS ECR Registry:

```bash
sed -i.bak "s|finlytics-backend:latest|${ECR_REGISTRY}/finlytics-backend:latest|g" k8s/backend.yaml
sed -i.bak "s|finlytics-frontend:latest|${ECR_REGISTRY}/finlytics-frontend:latest|g" k8s/frontend.yaml
sed -i.bak "s|finlytics-wisprflow:latest|${ECR_REGISTRY}/finlytics-wisprflow:latest|g" k8s/wisprflow.yaml
rm -f k8s/*.bak
```

Deploy the microservices:
```bash
kubectl apply -f k8s/wisprflow.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

Check rollout status:
```bash
kubectl get pods -n finlytics
kubectl rollout status deployment/backend-deployment -n finlytics
kubectl rollout status deployment/frontend-deployment -n finlytics
kubectl rollout status deployment/wisprflow-deployment -n finlytics
```

---

## 🌐 Step 6: Expose App via Ingress / Load Balancer

### Option A: AWS Load Balancer Controller (Recommended for AWS)
If your EKS cluster has the **AWS Load Balancer Controller** installed:
```bash
kubectl apply -f k8s/ingress.yaml
kubectl get ingress finlytics-ingress -n finlytics
```
An AWS Application Load Balancer (ALB) will automatically be provisioned. Once the `ADDRESS` appears (usually 2-3 minutes), navigate to the ALB DNS name in your browser.

### Option B: Quick Public Exposure via LoadBalancer Service
If you prefer not to install an Ingress controller, you can convert `frontend-service` to type `LoadBalancer`:
```bash
kubectl patch svc frontend-service -n finlytics -p '{"spec": {"type": "LoadBalancer"}}'
kubectl get svc frontend-service -n finlytics
```

---

## ⚡ One-Click Automated Script

You can run the included automation script:
```bash
export GEMINI_API_KEY="your_key"
export AWS_REGION="us-east-1"
./scripts/deploy-aws.sh
```

---

## 🔍 Troubleshooting & Logs

* **Check Pod Status**: `kubectl get pods -n finlytics`
* **View Backend Logs**: `kubectl logs -l app=finlytics-backend -n finlytics -f`
* **View Frontend Logs**: `kubectl logs -l app=finlytics-frontend -n finlytics -f`
* **Check Service Endpoints**: `kubectl get svc -n finlytics`
* **Describe Failing Pod**: `kubectl describe pod <POD_NAME> -n finlytics`

