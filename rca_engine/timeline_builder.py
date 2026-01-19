from typing import List, Dict
from rca_engine.trace_normalizer import NormalizedSpan


class IncidentTimeline:
    """
    Builds an RCA-enriched timeline of an incident.
    """

    def build(self, spans: List[NormalizedSpan]) -> List[Dict]:
        if not spans:
            return []

        # Sort spans by start time
        ordered = sorted(
            spans,
            key=lambda s: s.start_time if s.start_time is not None else float("inf")
        )

        base_time = ordered[0].start_time or 0.0
        timeline = []

        for span in ordered:
            role = self._classify_role(span)
            explanation = self._explain_span(span, role)

            timeline.append({
                "service": span.service,
                "operation": span.operation,
                "role": role,
                "error": span.error,
                "error_kind": span.error_kind,
                "incident_id": span.incident_id,
                "offset_ms": (
                    int((span.start_time - base_time) * 1000)
                    if span.start_time is not None
                    else None
                ),
                "explanation": explanation,
            })

        return timeline

    # ------------------------
    # Role classification
    # ------------------------
    def _classify_role(self, span: NormalizedSpan) -> str:
        if span.error and span.error_kind == "root":
            return "root_cause"

        if span.error and span.error_kind == "propagated":
            return "propagated_failure"

        return "normal"

    # ------------------------
    # Human explanation
    # ------------------------
    def _explain_span(self, span: NormalizedSpan, role: str) -> str:
        if role == "root_cause":
            return (
                f"Service '{span.service}' experienced the original failure "
                f"that triggered the incident."
            )

        if role == "propagated_failure":
            parent = span.parent_service or "an upstream dependency"
            return (
                f"Service '{span.service}' failed due to issues propagated "
                f"from {parent}."
            )

        return f"Service '{span.service}' executed normally."
