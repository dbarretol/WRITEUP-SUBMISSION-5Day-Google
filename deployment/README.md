# Cloud Run Deployment

This directory contains the configuration to deploy the Multi-Agent Academic Research System to **Google Cloud Run**.

## Prerequisites

1.  **Google Cloud Project**: Active GCP project with billing enabled.

```sh
# Useful commands
gcloud projects list    #List all the projects
gcloud config get-value project #Get the current project
gcloud config set project YOUR_PROJECT_ID #Set the current project
```

2.  **Google Cloud SDK**: `gcloud` CLI installed and authenticated.
3.  **APIs Enabled**:
    *   Cloud Run API
    *   Cloud Build API
    *   Vertex AI API
    *   Cloud Storage API

## ⚠️ Critical IAM Permissions

Your Cloud Run service uses a "Service Account" to run (usually the default Compute Engine account). **This account needs permissions to call Vertex AI.**

After deployment, if you see "403 Forbidden" or "Permission Denied" errors in the logs:

1.  Go to **Cloud Run** console > Select your service.
2.  Check the **Security** tab to see which Service Account is being used.
3.  Go to **IAM & Admin**.
4.  Grant that Service Account the **Vertex AI User** role.

Also, you will need:

* Cloud Build Editor - to submit builds
* Cloud Run Admin - to deploy services
* Service Account User - to deploy as a service account
* Storage Admin - for the build artifacts bucket

> IMPORTANT!: Check the [pre-flight checklist](PRE-FLIGHT-CHECKLIST.md) before running the deployment script.

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

### Parameters:
*   `-ProjectId` / `-p`: Your Google Cloud Project ID (Required).
*   `-Region` / `-r`: (Optional) GCP Region (default: `us-central1`).
*   `-ServiceName` / `-s`: (Optional) Name of the Cloud Run service (default: `aida-research-agent`).

## Files

*   **`.dockerignore`**: Crucial file. Ensures local virtual environments (`.venv`) are not copied to the container.
*   **`Dockerfile`**: Defines the container image. It uses a lightweight Python 3.10 slim image, installs `uv`, and runs the Streamlit app on port 8080.
*   **`deploy.ps1`**: PowerShell script to automate the build and deploy process.
*   **`deploy.sh`**: Bash script to automate the build and deploy process.

## Manual Deployment Steps

If you prefer to run commands manually:

1.  **Build the image**:
    ```bash
    gcloud builds submit --config deployment/cloudbuild.yaml --substitutions=_IMAGE_NAME=gcr.io/YOUR_PROJECT_ID/aida-research-agent .
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
```
MediaFileStorageError: Bad filename '...' (No media file with id '...')
```

**This is expected behavior** and not a critical error. It occurs because:
- Streamlit stores download buttons in memory
- Cloud Run can scale to zero and restart containers
- When containers restart, the in-memory media files are lost

**Impact**: Users may need to regenerate their proposal if the container restarts between generation and download. The app will continue to work normally.

### Permission Errors

If you see `PermissionError: [Errno 13] Permission denied: '/home/appuser'`, ensure you're using the latest Dockerfile which:
- Creates the appuser home directory with `-m -d /home/appuser`
- Sets `STREAMLIT_CONFIG_DIR=/tmp/.streamlit`
- Runs `chown -R appuser:appuser /app /home/appuser`

### Vertex AI Permission Errors

If you see 403 errors when calling Vertex AI:
1. Go to Cloud Run console → Select your service
2. Check the **Security** tab for the Service Account being used
3. Go to **IAM & Admin** → Grant that Service Account the **Vertex AI User** role
