from fastapi import FastAPI
from api.schemas import RCARequest, RCAResponse
from api.service import RCAService
from rca_engine.otel_adapter import extract_raw_spans
from api.schemas import RCAFeedbackRequest


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="Incident RCA Platform",
    description="Automated Root Cause Analysis for Distributed Systems",
    version="1.0.0",
)

# --------------------------------------------------
# RCA Service (core engine)
# --------------------------------------------------

rca_service = RCAService()

# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

@app.post("/analyze", response_model=RCAResponse)
def analyze_trace(request: RCARequest):
    """
    Analyze a distributed trace using normalized raw spans.

    This endpoint is useful for:
    - unit tests
    - manual testing
    - synthetic traces
    """

    result = rca_service.analyze_trace(
        raw_spans=[span.model_dump() for span in request.spans]
    )

    return result


@app.post("/analyze/otel", response_model=RCAResponse)
def analyze_otel_trace(otel_payload: dict):
    """
    Analyze a REAL OpenTelemetry / Jaeger trace export.

    Steps:
    1. Extract raw spans from OTEL payload
    2. Normalize spans
    3. Build RCA graph
    4. Detect root cause
    5. Compute blast radius
    6. Build timeline
    7. Generate explanation
    """

    # Step 1: Convert OTEL → raw spans
    raw_spans = extract_raw_spans(otel_payload)

    # Step 2: Run full RCA pipeline
    result = rca_service.analyze_trace(raw_spans)

    return result

@app.post("/feedback")
def submit_feedback(feedback: RCAFeedbackRequest):
    """
    Accept human feedback to improve RCA learning.
    """

    rca_service.feedback_store.record(
        incident_id=feedback.incident_id,
        root_cause=feedback.root_cause,
        confidence=0.0,  # confidence already accounted earlier
        correct=feedback.correct,
    )

    return {
        "status": "feedback recorded",
        "incident_id": feedback.incident_id,
        "root_cause": feedback.root_cause,
        "correct": feedback.correct,
    }


@app.get("/health")
def health_check():
    """
    Health endpoint for monitoring.
    """
    return {"status": "ok"}
