"""
Polar client configuration and initialization.
"""
from typing import Optional
from polar_sdk import Polar
from app.core.config import settings


class PolarClient:
    """Polar SDK client wrapper."""
    
    def __init__(self):
        """Initialize Polar client."""
        if not settings.POLAR_ACCESS_TOKEN:
            raise ValueError("POLAR_ACCESS_TOKEN environment variable is required")
        
        self._client = Polar(
            access_token=settings.POLAR_ACCESS_TOKEN,
            server=settings.POLAR_SERVER
        )
    
    def get_client(self) -> Polar:
        """Get the Polar client instance."""
        return self._client
    
    @property
    def webhook_secret(self) -> str:
        """Get the webhook secret."""
        if not settings.POLAR_WEBHOOK_SECRET:
            raise ValueError("POLAR_WEBHOOK_SECRET environment variable is required")
        return settings.POLAR_WEBHOOK_SECRET


# Global client instance
polar_client = PolarClient()