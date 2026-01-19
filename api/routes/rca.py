from fastapi import APIRouter, HTTPException
from api.schemas import RCARequest, RCAResponse
from api.service import RCAService
from rca_engine.otel_adapter import extract_raw_spans

router = APIRouter()


@router.post("/analyze", response_model=RCAResponse)
def analyze_trace(payload: RCARequest):
    """
    Analyze a trace from either:
    - raw spans
    - OTEL payload
    """

    # Case 1: Raw spans provided
    if payload.spans:
        raw_spans = [span.model_dump() for span in payload.spans]

    # Case 2: OTEL payload provided
    elif payload.otel_payload:
        raw_spans = extract_raw_spans(payload.otel_payload)

    # Case 3: Invalid request
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'spans' or 'otel_payload' must be provided"
        )

    # Run RCA
    service = RCAService()
    return service.analyze_trace(raw_spans)
