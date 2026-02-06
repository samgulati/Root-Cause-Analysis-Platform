import json
import os
from typing import Dict


class DatasetWriter:
    """
    Persists ML-ready RCA records to disk (JSONL format).
    """

    def __init__(self, path: str = "data/incidents.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def write(self, record: Dict):
        """
        Append a single incident record to the dataset.
        """

        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
