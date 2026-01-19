from rca_engine.incident_narrator import IncidentNarrator


def test_no_incident():
    narrator = IncidentNarrator()

    summary = {
        "root_cause": None,
        "blast_radius": 0,
        "affected_services": []
    }

    result = narrator.generate(summary, [])

    assert result["impact"] == "none"
    assert "no failures" in result["narrative"].lower()


def test_simple_incident():
    narrator = IncidentNarrator()

    summary = {
        "root_cause": "service-c",
        "blast_radius": 3,
        "affected_services": ["service-a", "service-b", "service-c"]
    }

    timeline = [
        {"service": "service-c", "role": "root_cause", "offset_ms": 0},
        {"service": "service-b", "role": "propagated_failure", "offset_ms": 120},
        {"service": "service-a", "role": "propagated_failure", "offset_ms": 300},
    ]

    result = narrator.generate(summary, timeline)

    assert result["impact"] == "high"
    assert "service-c" in result["narrative"]
    assert "propagated" in result["narrative"]
