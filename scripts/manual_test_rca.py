"""
Temporary manual test for RCAService.
This file is NOT committed.
"""

from api.service import RCAService

# ----------------------------
# 1️⃣ Fake raw spans (simulate Jaeger output)
# ----------------------------
raw_spans = [
    {
        "trace_id": "trace-1",
        "span_id": "span-c",
        "attributes": {
            "service.name": "service-c",
            "rca.error": True,
            "rca.error.kind": "root",
            "rca.incident_id": "incident-123",
        },
        "start_time": 1.0,
        "end_time": 1.1,
    },
    {
        "trace_id": "trace-1",
        "span_id": "span-b",
        "attributes": {
            "service.name": "service-b",
            "rca.error": True,
            "rca.error.kind": "propagated",
            "rca.incident_id": "incident-123",
            "rca.dependency.target": "service-c",
        },
        "start_time": 1.2,
        "end_time": 1.3,
    },
    {
        "trace_id": "trace-1",
        "span_id": "span-a",
        "attributes": {
            "service.name": "service-a",
            "rca.error": True,
            "rca.error.kind": "propagated",
            "rca.incident_id": "incident-123",
            "rca.dependency.target": "service-b",
        },
        "start_time": 1.4,
        "end_time": 1.5,
    },
]

# ----------------------------
# 2️⃣ Run RCA pipeline
# ----------------------------
service = RCAService()
result = service.analyze_trace(raw_spans)

# ----------------------------
# 3️⃣ Print result
# ----------------------------
from pprint import pprint
pprint(result)
