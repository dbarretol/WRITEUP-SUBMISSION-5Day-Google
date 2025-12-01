"""Academic_Research: Research advice, related literature finding, research area proposals, web knowledge access."""

## FOR VERTEX USE
import os

import google.auth
from dotenv import load_dotenv

load_dotenv()

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ["GOOGLE_CLOUD_LOCATION"] ="us-central1" #"global"
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

print(f"[INFO] Configured for Vertex AI. Project: {project_id}, Region: {os.environ['GOOGLE_CLOUD_LOCATION']}")

## FOR GEMINI USE
""" import os
from dotenv import load_dotenv

# 1. Load the .env file from the root directory
load_dotenv('../.env')

# 2. Explicitly tell the library NOT to use Vertex AI.
# This forces it to look for 'GOOGLE_API_KEY' instead.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Optional: Verify the key is loaded (for debugging only, remove in production)
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY not found in environment variables.") """