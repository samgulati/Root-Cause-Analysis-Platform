import requests
from typing import Dict, List


class JaegerClient:
    """
    Fetches traces from Jaeger Query API.
    """

    def __init__(self, base_url: str = "http://localhost:16686"):
        self.base_url = base_url

    def get_trace(self, trace_id: str) -> List[Dict]:
        """
        Fetch a trace by trace_id from Jaeger.
        """
        url = f"{self.base_url}/api/traces/{trace_id}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return data["data"][0]["spans"]
