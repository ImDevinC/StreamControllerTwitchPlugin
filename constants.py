"""
Constants used throughout the Twitch plugin.
"""

# Update intervals (in seconds)
VIEWER_UPDATE_INTERVAL_SECONDS = 10
AD_SCHEDULE_FETCH_INTERVAL_SECONDS = 30
AD_DISPLAY_UPDATE_INTERVAL_SECONDS = 1
CHAT_MODE_UPDATE_INTERVAL_SECONDS = 5

# Error display
ERROR_DISPLAY_DURATION_SECONDS = 3

# OAuth/Authentication
OAUTH_REDIRECT_URI = "http://localhost:3000/auth"
OAUTH_PORT = 3000

# Rate Limiting
# Twitch API standard rate limit: 800 requests per minute
# Using conservative limit to avoid hitting the cap
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 60  # seconds
