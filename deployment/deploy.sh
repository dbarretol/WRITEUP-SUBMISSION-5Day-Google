#!/bin/bash

# Deployment Script for Google Cloud Run
# Usage: ./deployment/deploy.sh -p "your-project-id"

# Exit on error
set -e

# Default values
REGION="us-central1"
SERVICE_NAME="aida-research-agent"

# Function to show usage
usage() {
    echo "Usage: $0 -p <project-id> [-r <region>] [-s <service-name>]"
    exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--project-id) PROJECT_ID="$2"; shift ;;
        -r|--region) REGION="$2"; shift ;;
        -s|--service-name) SERVICE_NAME="$2"; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown parameter: $1"; usage ;;
    esac
    shift
done

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required."
    usage
fi

echo -e "\033[0;36m🚀 Starting Deployment to Google Cloud Run...\033[0m"

# 1. Configure Project
echo -e "\n\033[1;33m1️⃣  Configuring Google Cloud Project: $PROJECT_ID\033[0m"
gcloud config set project "$PROJECT_ID"

# 2. Build Container Image
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
echo -e "\n\033[1;33m2️⃣  Building Container Image: $IMAGE_NAME\033[0m"
gcloud builds submit --config deployment/cloudbuild.yaml --substitutions=_IMAGE_NAME="$IMAGE_NAME" .

# 3. Deploy to Cloud Run
echo -e "\n\033[1;33m3️⃣  Deploying to Cloud Run...\033[0m"
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=true" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars="GOOGLE_CLOUD_LOCATION=$REGION" \
    --port 8080

echo -e "\n\033[0;32m✅ Deployment Successful!\033[0m"
echo "⚠️  IMPORTANT: Ensure your Cloud Run Service Account has 'Vertex AI User' role."