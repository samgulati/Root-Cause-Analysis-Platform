from typing import Dict, List, Any


def _flatten_attributes(attrs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Converts OTEL attribute list into a flat dict.

    Example:
    [
      {"key": "rca.error", "value": {"boolValue": true}}
    ]
    →
    {"rca.error": True}
    """
    flattened = {}

    for attr in attrs:
        key = attr.get("key")
        value_obj = attr.get("value", {})

        # OTEL encodes values by type
        if "stringValue" in value_obj:
            flattened[key] = value_obj["stringValue"]
        elif "boolValue" in value_obj:
            flattened[key] = value_obj["boolValue"]
        elif "intValue" in value_obj:
            flattened[key] = int(value_obj["intValue"])
        elif "doubleValue" in value_obj:
            flattened[key] = float(value_obj["doubleValue"])

    return flattened


def extract_raw_spans(otel_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converts an OTEL / Jaeger trace export payload
    into RCA-compatible raw spans.

    Output format matches what `trace_normalizer.normalize_span`
    expects.
    """

    raw_spans: List[Dict[str, Any]] = []

    resource_spans = otel_payload.get("resourceSpans", [])

    for resource_span in resource_spans:
        # -----------------------------
        # Resource attributes (service name lives here)
        # -----------------------------
        resource_attrs = _flatten_attributes(
            resource_span.get("resource", {}).get("attributes", [])
        )

        service_name = resource_attrs.get("service.name", "unknown")

        scope_spans = resource_span.get("scopeSpans", [])

        for scope in scope_spans:
            spans = scope.get("spans", [])

            for span in spans:
                span_attrs = _flatten_attributes(span.get("attributes", []))

                # -----------------------------
                # Span status (ERROR / OK)
                # -----------------------------
                status = span.get("status", {})
                status_code = status.get("code")

                raw_span = {
                    # ---- Identity ----
                    "trace_id": span.get("traceId"),
                    "span_id": span.get("spanId"),
                    "parent_span_id": span.get("parentSpanId"),

                    # ---- Operation ----
                    "name": span.get("name", "unknown"),

                    # ---- Attributes ----
                    "attributes": span_attrs,

                    # ---- Resource attributes ----
                    "resource": {
                        "attributes": {
                            "service.name": service_name
                        }
                    },

                    # ---- Status ----
                    "status": {
                        "code": status_code
                    },

                    # ---- Timing (ns → seconds) ----
                    "start_time": span.get("startTimeUnixNano", 0) / 1e9,
                    "end_time": span.get("endTimeUnixNano", 0) / 1e9,
                }

                raw_spans.append(raw_span)

    return raw_spans
