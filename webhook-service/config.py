import os

# Shared secret for webhook authentication
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "dev-secret-change-me")

# Max allowed age for incoming events (in seconds)
MAX_AGE_SECONDS = 300  # 5 minutes