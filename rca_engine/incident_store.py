from typing import Dict, List
import hashlib
import json


class IncidentStore:
    """
    Stores and retrieves historical RCA incidents.
    """

    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def _fingerprint(self, incident: Dict) -> str:
        """
        Create a stable fingerprint for an incident.
        """
        normalized = {
            "root_cause": incident.get("root_cause"),
            "affected_services": sorted(incident.get("affected_services", [])),
            "blast_radius": incident.get("blast_radius"),
        }

        payload = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def save(self, incident: Dict):
        fingerprint = self._fingerprint(incident)

        if fingerprint not in self._store:
            self._store[fingerprint] = {
                "count": 0,
                "incident": incident,
            }

        self._store[fingerprint]["count"] += 1

    def similar_incidents(self, incident: Dict) -> List[Dict]:
        fingerprint = self._fingerprint(incident)

        if fingerprint in self._store:
            return [self._store[fingerprint]]

        return []
