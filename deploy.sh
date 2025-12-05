#!/bin/bash

# ================================
# CONFIGURATION (EDIT IF NEEDED)
# ================================
RESOURCE_GROUP="doc-processing"
ACR_NAME="docprocessingarc"
SERVICES=("upload-service" "ml-processing-service" "results-service" "auth-service" "admin-service")

# Azure Container App names match folder names:
# upload-service → upload-service
# ... etc

# Use current Git commit hash for unique image tags
GIT_SHA=$(git rev-parse --short HEAD)

echo "Using image tag: $GIT_SHA"
echo "Logging into Azure..."

az login
if [ $? -ne 0 ]; then
    echo "Azure login failed"
    exit 1
fi

echo "Logging into ACR: $ACR_NAME..."
az acr login --name $ACR_NAME
if [ $? -ne 0 ]; then
    echo "ACR login failed"
    exit 1
fi

echo "Starting build + push for all services..."
echo "------------------------------------------"

for SERVICE in "${SERVICES[@]}"; do
    IMAGE="$ACR_NAME.azurecr.io/$SERVICE:$GIT_SHA"
    SERVICE_PATH="./services/$SERVICE"

    echo ""
    echo "=========================================="
    echo "Building: $SERVICE"
    echo "Dockerfile path: $SERVICE_PATH"
    echo "Tag: $IMAGE"
    echo "=========================================="

    docker build -t $IMAGE $SERVICE_PATH
    if [ $? -ne 0 ]; then
        echo "Build failed for $SERVICE"
        exit 1
    fi

    echo "Pushing image..."
    docker push $IMAGE
    if [ $? -ne 0 ]; then
        echo "Push failed for $SERVICE"
        exit 1
    fi

done

echo ""
echo "All images pushed!"
echo "Updating Azure Container Apps..."
echo "------------------------------------------"

for SERVICE in "${SERVICES[@]}"; do
    IMAGE="$ACR_NAME.azurecr.io/$SERVICE:$GIT_SHA"

    echo ""
    echo "Updating container app: $SERVICE"
    echo "Using image: $IMAGE"

    az containerapp update \
        --name $SERVICE \
        --resource-group $RESOURCE_GROUP \
        --image $IMAGE

    if [ $? -ne 0 ]; then
        echo "Failed to update $SERVICE"
        exit 1
    fi
done

echo ""
echo "=============================================="
echo "🚀 Deployment complete!"
echo "All services are updated to image tag: $GIT_SHA"
echo "=============================================="