import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GoogleMapsAPI:
    """Google Maps API integration for transit and distance data."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    def get_distance_matrix(
        self,
        origin: str,
        destination: str,
        mode: str = "transit"
    ) -> Optional[Dict[str, Any]]:
        """Get distance and duration between two locations."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/distancematrix/json"
            params = {
                "origins": origin,
                "destinations": destination,
                "mode": mode,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK":
                element = data["rows"][0]["elements"][0]
                if element["status"] == "OK":
                    return {
                        "distance_km": element["distance"]["value"] / 1000,
                        "duration_minutes": element["duration"]["value"] / 60,
                        "distance_text": element["distance"]["text"],
                        "duration_text": element["duration"]["text"]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Google Maps API error: {e}")
            return None
