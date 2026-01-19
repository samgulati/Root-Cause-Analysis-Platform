# Incident RCA Platform

A production-grade root cause analysis (RCA) system that converts distributed traces
(OpenTelemetry / Jaeger) into causal graphs, blast radius metrics, timelines,
and human-readable incident explanations.

## Why This Exists
Traditional observability tools show *what* failed, but not *why*.
This system automatically reconstructs failure propagation paths
across microservices and identifies the true root cause.

## Architecture
OpenTelemetry Traces
        ↓
Trace Normalizer
        ↓
RCA Graph Builder
        ↓
Blast Radius Analyzer
        ↓
Timeline Reconstruction
        ↓
Explanation Engine
        ↓
Canonical RCA Report (JSON)

## Key Features
- Root cause detection (local vs propagated failures)
- Dependency-aware blast radius calculation
- Failure timeline reconstruction
- Canonical, versioned RCA output schema
- Defensive handling of partial or malformed traces
- Fully unit-tested graph algorithms

## Tech Stack
- Python 3
- OpenTelemetry
- Jaeger
- Pytest
- Graph traversal algorithms (BFS)

## Example Output
```json
{
  "incident_id": "incident-999",
  "root_cause": "service-c",
  "blast_radius": 3,
  "severity": "high",
  "affected_services": ["service-a", "service-b", "service-c"]
}
