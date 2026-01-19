from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

import os
import random
import time
import uuid
import requests
from fastapi import FastAPI, HTTPException

# -------------------------------
# OpenTelemetry setup
# -------------------------------
provider = TracerProvider()
trace.set_tracer_provider(provider)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

RequestsInstrumentor().instrument()

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# -------------------------------
# Configuration
# -------------------------------
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8000")
FAIL_RATE = float(os.getenv("FAIL_RATE", "0.0"))
LATENCY_MS = int(os.getenv("LATENCY_MS", "0"))

# -------------------------------
# Routes
# -------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "service-a"}

@app.post("/process")
def process():
    tracer = trace.get_tracer(__name__)
    incident_id = f"incident-{uuid.uuid4().hex[:8]}"

    with tracer.start_as_current_span("service-a.process") as span:
        # RCA normalization
        span.set_attribute("rca.node", True)
        span.set_attribute("rca.service", "service-a")
        span.set_attribute("rca.role", "entrypoint")
        span.set_attribute("rca.incident_id", incident_id)

        # Latency
        if LATENCY_MS > 0:
            sleep = random.uniform(0, LATENCY_MS) / 1000
            time.sleep(sleep)

        # Local failure
        if random.random() < FAIL_RATE:
            span.set_attribute("rca.error", True)
            span.set_attribute("rca.error.kind", "root")

            raise HTTPException(
                status_code=500,
                detail=f"Service-A simulated failure | {incident_id}"
            )

        # Downstream call
        try:
            response = requests.post(f"{SERVICE_B_URL}/process", timeout=2)
            response.raise_for_status()

        except Exception:
            span.set_attribute("rca.error", True)
            span.set_attribute("rca.error.kind", "propagated")

            raise HTTPException(
                status_code=502,
                detail=f"Service-A failed calling service-b | {incident_id}"
            )

        # Success
        span.set_attribute("rca.error", False)
        span.set_attribute("rca.error.kind", "none")

        return {
            "service": "service-a",
            "downstream": response.json(),
            "status": "success"
        }
