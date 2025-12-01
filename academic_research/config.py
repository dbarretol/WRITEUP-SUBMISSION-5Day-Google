"""Central configuration for the academic research module."""

import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables (force override of system variables)
load_dotenv(override=True)

# Default model configuration
DEFAULT_MODEL = "gemini-2.0-flash-lite"

# Configure retry options for API resilience
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)
