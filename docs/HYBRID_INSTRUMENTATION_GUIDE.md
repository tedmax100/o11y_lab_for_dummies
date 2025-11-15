# OpenTelemetry Python Hybrid Instrumentation Configuration Guide

## What is Hybrid Mode?

Hybrid mode combines **Auto Instrumentation** and **Manual Instrumentation**:

- **Auto Instrumentation**: Launched using the `opentelemetry-instrument` command, automatically adds telemetry to frameworks and libraries
- **Manual Instrumentation**: Manually creates spans, metrics, and configures providers in code

## Service-A Hybrid Mode Architecture

### 1. Auto Instrumentation Responsibilities (via opentelemetry-instrument)

```bash
CMD ["opentelemetry-instrument", "python", "main.py"]
```

**Auto-instrumented Components**:
- ✅ **TracerProvider**: Automatically created and configured
- ✅ **MeterProvider**: Automatically created and configured
- ✅ **FastAPI**: HTTP request/response automatic tracing
- ✅ **httpx**: HTTP client calls automatic tracing
- ✅ **psycopg2**: Database queries automatic tracing

### 2. Manual Instrumentation Responsibilities (manual configuration in code)

```python
# Manually configured components
- LoggerProvider: Requires manual creation and configuration
- Custom business spans
- Custom metrics
- Custom attributes
```

---

## Key Configuration Decisions

### ❌ Don't Enable Auto and Manual Logging Configuration Simultaneously

**Problematic Environment Variable**:
```bash
# ❌ Wrong: Will cause conflicts
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

**Why does it conflict?**
- When set to `true`, `opentelemetry-instrument` automatically attaches OTLP handler to the root logger
- But your code also manually creates a LoggerProvider and adds a LoggingHandler
- Result: Two handlers compete for control, causing logs to fail to send correctly

**✅ Correct Approach**:
```bash
# Comment out or remove this environment variable
# OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

Then fully control logging configuration manually in code.

---

## Complete Environment Variable Configuration

### Configuration in docker-compose.yaml

```yaml
services:
  service-a:
    environment:
      # ============ Application Configuration ============
      - SERVICE_B_URL=http://service-b:8002
      - DB_HOST=postgres

      # ============ OpenTelemetry Basic Configuration ============
      - OTEL_SERVICE_NAME=service-a-hybrid
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_EXPORTER_OTLP_INSECURE=true

      # ============ Signal Configuration ============
      - OTEL_TRACES_EXPORTER=otlp    # ✅ Auto instrumentation handles
      - OTEL_METRICS_EXPORTER=otlp   # ✅ Auto instrumentation handles
      - OTEL_LOGS_EXPORTER=otlp      # ✅ Tells SDK to use OTLP, but doesn't auto-configure

      # ============ Important: Don't Enable Auto Logging Configuration ============
      # ❌ Comment out to avoid conflicts
      # - OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

      # ============ Resource Attributes ============
      - OTEL_RESOURCE_ATTRIBUTES=service.namespace=o11y-lab,deployment.environment=lab,instrumentation.type=hybrid
```

---

## Correct Configuration Pattern in Code

### 1. Logging Configuration (Fully Manual)

```python
import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# Step 1: Configure basic logging (output to console)
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-a-hybrid", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}',
    handlers=[
        logging.StreamHandler()  # Ensure logs output to console
    ]
)

# Step 2: Create LoggerProvider
resource = Resource.create({
    SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "service-a-hybrid")
})
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# Step 3: Add OTLP Exporter
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            insecure=True
        )
    )
)

# Step 4: Attach LoggingHandler to root logger
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
```

### 2. Traces and Metrics (Using Auto-Created Providers)

```python
from opentelemetry import trace, metrics

# Get providers automatically created by opentelemetry-instrument
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create custom metrics
process_counter = meter.create_counter(
    name="service_a_process_total",
    description="Total number of process requests",
    unit="1"
)

# Create custom spans
with tracer.start_as_current_span("my_business_logic") as span:
    span.set_attribute("custom.attribute", "value")
    # Your business logic
```

---

## Why This Design?

### Advantages of Auto Instrumentation
1. **Zero Code Changes**: Automatically adds instrumentation for frameworks (FastAPI, httpx, psycopg2)
2. **Standardization**: Uses OpenTelemetry standard semantic conventions
3. **Easy Maintenance**: Automatically gets new features when frameworks are updated

### Necessity of Manual Instrumentation
1. **Logging Configuration**: Python's logging system needs to be manually connected to OTLP
2. **Business Logic**: Add business-specific spans and attributes
3. **Custom Metrics**: Create business-level metrics

---

## Environment Variables Reference

### Basic Configuration
| Variable | Purpose | Example |
|----------|---------|---------|
| `OTEL_SERVICE_NAME` | Service name | `service-a-hybrid` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector address | `http://otel-collector:4317` |
| `OTEL_EXPORTER_OTLP_INSECURE` | Use non-encrypted connection | `true` |

### Signal Configuration
| Variable | Purpose | Recommended Value |
|----------|---------|-------------------|
| `OTEL_TRACES_EXPORTER` | Traces exporter | `otlp` |
| `OTEL_METRICS_EXPORTER` | Metrics exporter | `otlp` |
| `OTEL_LOGS_EXPORTER` | Logs exporter | `otlp` |

### Python-Specific Configuration
| Variable | Purpose | Hybrid Mode Recommendation |
|----------|---------|---------------------------|
| `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` | Auto-configure logging | ❌ **Don't set** (manual configuration) |
| `OTEL_PYTHON_LOG_CORRELATION` | Log correlation with trace context | `true` |
| `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS` | Disable specific instrumentations | `redis,kafka` |
| `OTEL_PYTHON_EXCLUDED_URLS` | Exclude specific URLs | `healthcheck,metrics` |

---

## Diagnostic Methods

### 1. Check if Logs are Sent to OTel Collector

```bash
# View service-a logs
docker logs service-a 2>&1 | grep "service-a-hybrid"

# Check if OTel Collector receives logs
docker logs otel-collector 2>&1 | grep "service-a-hybrid"
```

### 2. Check Environment Variables

```bash
docker exec service-a env | grep OTEL
```

### 3. Verify Loki Configuration

```bash
# Check if Loki has OTLP enabled
curl http://localhost:3100/ready

# Query service-a logs
curl 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query={service_name="service-a-hybrid"}' \
  --data-urlencode 'limit=10'
```

---

## Best Practices

### ✅ Recommended Practices

1. **Clear Division of Responsibilities**:
   - Auto instrumentation handles frameworks and libraries
   - Manual instrumentation handles business logic and logging

2. **Avoid Duplicate Configuration**:
   - Don't use both `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true` and manual LoggerProvider

3. **Unified Resource**:
   - Manually created LoggerProvider should use the same resource attributes as auto instrumentation

4. **Log Format**:
   - Use structured logging (JSON)
   - Include trace_id and span_id for correlation

### ❌ Practices to Avoid

1. **Don't mix logging configuration methods**
2. **Don't forget to configure StreamHandler** (otherwise logs only go to OTLP, not visible in console)
3. **Don't recreate TracerProvider in hybrid mode** (will override auto instrumentation)

---

## Common Issues

### Q1: Why don't logs appear in Loki?
**A**: Check:
1. Whether `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` is commented out
2. Whether LoggerProvider is correctly configured in code
3. Whether Loki has OTLP reception enabled (requires `distributor.otlp_config` configuration)

### Q2: Can I use Auto Instrumentation exclusively?
**A**:
- ✅ **Traces and Metrics**: Can be fully automatic
- ❌ **Logs**: Python requires manual configuration to send to OTLP

### Q3: When do I need manual instrumentation?
**A**:
- Add business-specific spans
- Create custom metrics
- Configure log sending to OTLP
- Add custom attributes

### Q4: How to verify Auto Instrumentation is working?
**A**:
```bash
# View startup logs, should see output like:
# "Instrumenting fastapi"
# "Instrumenting httpx"
# "Instrumenting psycopg2"
docker logs service-a 2>&1 | grep -i "instrumenting"
```

---

## Reference Resources

- [OpenTelemetry Python Auto-Instrumentation](https://opentelemetry.io/docs/zero-code/python/)
- [OpenTelemetry Python Configuration](https://opentelemetry.io/docs/zero-code/python/configuration/)
- [Python SDK Documentation](https://opentelemetry-python.readthedocs.io/)
