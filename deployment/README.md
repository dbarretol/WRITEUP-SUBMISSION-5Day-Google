# Cloud Run Deployment

This directory contains the configuration to deploy the Multi-Agent Academic Research System to **Google Cloud Run**.

## Prerequisites

1.  **Google Cloud Project**: Active GCP project with billing enabled.

```bash
# Useful commands
gcloud projects list             # List all projects
gcloud config get-value project  # Get current project
gcloud config set project YOUR_PROJECT_ID  # Set current project
```

2.  **Google Cloud SDK**: `gcloud` CLI installed and authenticated.
3.  **APIs Enabled**:
    *   Cloud Run API
    *   Cloud Build API
    *   Vertex AI API
    *   Artifact Registry (or Container Registry) API

## ⚠️ Critical IAM Permissions

Your Cloud Run service uses a "Service Account" to run (by default, the **Compute Engine default service account**).

**This account needs permissions to call Vertex AI models (Gemini).** Without this, the application will crash when attempting to generate content.

**If you see "403 Forbidden" or "Permission Denied" errors in the logs:**

1.  Go to the **Cloud Run** console > Select your service.
2.  Check the **Security** tab to identify the Service Account email.
3.  Go to **IAM & Admin**.
4.  Find that email and grant it the **Vertex AI User** role (`roles/aiplatform.user`).

Also, you will need:

* Cloud Build Editor - to submit builds
* Cloud Run Admin - to deploy services
* Service Account User - to deploy as a service account
* Storage Admin - for the build artifacts bucket

> **IMPORTANT**: Review the [Pre-Flight Checklist](PRE-FLIGHT-CHECKLIST.md) before running the deployment script to prevent common build failures.

## How to Deploy

Run the deployment script from the **project root directory**.

### Windows (PowerShell)

```powershell
.\deployment\deploy.ps1 -ProjectId "your-project-id"
```

### Linux / macOS (Bash)

First, ensure the script is executable:
```bash
chmod +x deployment/deploy.sh
```

Then run it:
```bash
./deployment/deploy.sh -p "your-project-id"
```

### Script Parameters
*   `-ProjectId` / `-p`: Your Google Cloud Project ID (**Required**).
*   `-Region` / `-r`: GCP Region (Optional, default: `us-central1`).
*   `-ServiceName` / `-s`: Name of the Cloud Run service (Optional, default: `aida-research-agent`).

## Files Description

*   **`cloudbuild.yaml`**: Configuration for Cloud Build. It instructs Google Cloud how to build the Docker container using `deployment/Dockerfile`.
*   **`.dockerignore`**: **Crucial file.** Ensures local virtual environments (`.venv`), API keys, and temporary files are not uploaded to the build server.
*   **`Dockerfile`**: Defines the container image. It uses a secure Python 3.10 slim image, installs `uv` for fast dependency management, creates a non-root user, and runs the Streamlit app.
*   **`deploy.ps1`**: PowerShell automation script for Windows users.
*   **`deploy.sh`**: Bash automation script for Linux/Mac users.

## Manual Deployment Steps

If you prefer to run commands manually without the scripts:

1.  **Build the Container Image**:
    ```bash
    # Replace YOUR_PROJECT_ID
    gcloud builds submit --config deployment/cloudbuild.yaml \
        --substitutions=_IMAGE_NAME=gcr.io/YOUR_PROJECT_ID/aida-research-agent .
    ```

2.  **Deploy to Cloud Run**:
    ```bash
    gcloud run deploy aida-research-agent \
        --image gcr.io/YOUR_PROJECT_ID/aida-research-agent \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1" \
        --port 8080
    ```

## Troubleshooting

### Media File Storage Errors (404 on /media/...)
You may see warnings in Cloud Run logs like:
`MediaFileStorageError: Bad filename ... (No media file with id ...)`

*   **Cause**: Streamlit stores generated files in memory. Cloud Run is "serverless" and may restart containers or scale to zero when idle. When a container restarts, in-memory files are lost.
*   **Impact**: Non-critical. If a user tries to download a file after a container restart, they may need to regenerate the proposal.

### Permission Errors (`/home/appuser`)
If you see `PermissionError: [Errno 13] Permission denied: '/home/appuser'`, ensure you are using the latest `Dockerfile` provided in this repo. It specifically handles permissions by:
1.  Creating a user `appuser`.
2.  Setting `STREAMLIT_CONFIG_DIR` to `/tmp`.
3.  Running `chown -R appuser:appuser` on the application directory.

### Build Fails on "Uploading..."
If `gcloud builds submit` takes a very long time or fails during the upload step:
*   **Check `.dockerignore`**: Ensure you have a `.dockerignore` file in the root directory.
*   **Verify Content**: Make sure `.venv`, `venv`, or `.git` are listed in `.dockerignore`. Uploading a local virtual environment is the #1 cause of build timeouts.