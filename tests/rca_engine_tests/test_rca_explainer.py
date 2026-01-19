from rca_engine.rca_explainer import RCAExplainer


def test_explainer_no_failure():
    explainer = RCAExplainer()

    summary = {
        "root_cause": None,
        "blast_radius": 0,
        "affected_services": []
    }

    result = explainer.explain(summary)

    assert result["severity"] == "none"
    assert "No failures" in result["summary"]


def test_explainer_root_only_failure():
    explainer = RCAExplainer()

    summary = {
        "incident_id": "incident-1",
        "root_cause": "service-c",
        "blast_radius": 1,
        "affected_services": ["service-c"]
    }

    result = explainer.explain(summary)

    assert result["severity"] == "low"
    assert "failed without impacting" in result["summary"]


def test_explainer_propagated_failure():
    explainer = RCAExplainer()

    summary = {
        "incident_id": "incident-2",
        "root_cause": "service-c",
        "blast_radius": 3,
        "affected_services": ["service-a", "service-b", "service-c"]
    }

    result = explainer.explain(summary)

    assert result["severity"] == "high"
    assert "propagated" in result["summary"]
    assert "service-a" in result["summary"]
