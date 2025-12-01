Before running the deployment script (`deploy.ps1` or `deploy.sh`), perform this **6-point Pre-Flight Checklist**.

If any of these check fails, the deployment script will likely error out or the deployed application will crash on startup.

### 1. Verification: Cloud SDK Installation & Login
You need the Google Cloud CLI tools installed and authenticated.

*   **Check:** Run these commands in your terminal:
    ```bash
    gcloud --version
    gcloud auth print-identity-token
    ```
*   **Fix:** If you get an error or are logged into the wrong account:
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```

### 2. Verification: Enabled APIs
Cloud Run, Cloud Build, and Vertex AI APIs must be enabled on your project.

*   **Check:**
    ```bash
    gcloud services list --enabled --filter="name:run.googleapis.com OR name:cloudbuild.googleapis.com OR name:aiplatform.googleapis.com"
    ```
    *You should see `run.googleapis.com`, `cloudbuild.googleapis.com`, and `aiplatform.googleapis.com` in the output.*

*   **Fix:**
    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com artifactregistry.googleapis.com storage.googleapis.com
    ```

### 3. Verification: Storage Bucket Existence
Your script requires a `-BucketName`. This bucket must already exist.

*   **Check:**
    ```bash
    # Replace with the bucket name you plan to use
    gcloud storage buckets describe gs://YOUR_BUCKET_NAME
    ```
*   **Fix:** If it says "Not found":
    ```bash
    gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1
    ```

### 4. Verification: `uv.lock` Sync
The `Dockerfile` copies `uv.lock` to install dependencies. If this file is missing or out of sync with `pyproject.toml`, the build will fail.

*   **Check:** Look at your file explorer. Does `uv.lock` exist?
*   **Fix:** Run this locally to generate/update it:
    ```bash
    uv sync
    ```

### 5. Verification: `.dockerignore`
This is critical for upload speed and preventing crashes.

*   **Check:** Ensure a file named `.dockerignore` exists in the root and contains `.venv` and `.gemini`.
*   **Why:** If you don't have this, `gcloud builds submit` will try to upload your massive local virtual environment to the cloud, which is slow and breaks the build.

### 6. Verification: Local Docker Build (Optional but Recommended)
If you have Docker installed locally, try building the image on your machine first. If it breaks here, it will break in the cloud.

*   **Check:**
    ```bash
    docker build . -t test-build
    ```
*   **If it passes:** You can be 99% sure the cloud build will pass.
*   **If you don't have Docker:** You can skip this and let Cloud Build handle it, but debugging is slower.

---

### Summary Checklist

| Check | Command/Action | Status |
| :--- | :--- | :--- |
| **Logged In** | `gcloud auth login` | ✅ |
| **Project Set** | `gcloud config set project <ID>` | ✅ |
| **APIs Up** | `gcloud services enable ...` | ✅ |
| **Bucket Exists** | `gcloud storage buckets create ...` | ✅ |
| **Lockfile** | `uv sync` (File `uv.lock` exists) | ✅ |
| **Ignore File** | File `.dockerignore` exists | ✅ |

Once these are green, you are safe to run:

```powershell
.\deployment\deploy.ps1 -ProjectId "..." -BucketName "..."
```