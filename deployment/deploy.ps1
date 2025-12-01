# Deployment Script for Google Cloud Run
# Usage: .\deployment\deploy.ps1 -ProjectId "your-project-id"

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$Region = "us-central1",
    
    [string]$ServiceName = "aida-research-agent"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Deployment to Google Cloud Run..." -ForegroundColor Cyan

# 1. Configure Project
Write-Host "1️⃣  Configuring Google Cloud Project: $ProjectId"
gcloud config set project $ProjectId

# 2. Build Container Image
# Note: Using gcr.io for simplicity. For production, consider Artifact Registry (us-central1-docker.pkg.dev)
$ImageName = "gcr.io/$ProjectId/$ServiceName"
Write-Host "2️⃣  Building Container Image: $ImageName"
# Submit build from root directory
gcloud builds submit --config deployment/cloudbuild.yaml --substitutions=_IMAGE_NAME=$ImageName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Build failed."
    exit 1
}

# 3. Deploy to Cloud Run
Write-Host "3️⃣  Deploying to Cloud Run..."
gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=true" `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$ProjectId" `
    --set-env-vars="GOOGLE_CLOUD_LOCATION=$Region" `
    --port 8080

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment Successful!" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Ensure your Cloud Run Service Account has 'Vertex AI User' role."
}
else {
    Write-Error "❌ Deployment failed."
    exit 1
}