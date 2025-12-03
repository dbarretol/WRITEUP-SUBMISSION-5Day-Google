# Pre-Flight Checklist

Before running the deployment script (`deployment/deploy.ps1` or `deployment/deploy.sh`), perform this **6-point Pre-Flight Checklist**.

If any of these checks fail, the deployment script will likely error out, or the deployed application will crash on startup.

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
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com
    ```

### 3. Verification: Service Account Permissions (Vertex AI)
Your application is configured to use Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=true`). The default Cloud Run service account needs permission to call Gemini models.

*   **Context:** Cloud Run uses the Compute Engine default service account by default (looks like `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`).
*   **Fix/Grant:** Run this to grant the necessary role:
    ```bash
    # Replace with your Project ID and Project Number
    # You can find the project number via: gcloud projects describe YOUR_PROJECT_ID
    
    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
        --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
        --role="roles/aiplatform.user"
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

*   **Check:** (Note the `-f` flag because your Dockerfile is in a subfolder)
    ```bash
    docker build . -f deployment/Dockerfile -t test-build
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
| **IAM Role** | Grant `roles/aiplatform.user` | ✅ |
| **Lockfile** | `uv sync` (File `uv.lock` exists) | ✅ |
| **Ignore File** | File `.dockerignore` exists | ✅ |

Once these are green, you are safe to run:

**PowerShell:**
```powershell
.\deployment\deploy.ps1 -ProjectId "your-project-id"
```

**Bash:**
```bash
./deployment/deploy.sh -p "your-project-id"
```