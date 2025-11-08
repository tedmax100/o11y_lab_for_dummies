"""
Service A - 核心业务服务
展示 OpenTelemetry 自动埋点功能
- 数据库操作 (PostgreSQL)
- HTTP 调用 (Service D, Service B)
- 第三方 API 调用
"""
import os
import logging
import time
import random
from fastapi import FastAPI, HTTPException
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

# 配置结构化日志
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-a", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}'
)
logger = logging.getLogger(__name__)

# 环境变量配置
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8002")
SERVICE_D_URL = os.getenv("SERVICE_D_URL", "http://service-d:8004")
THIRD_PARTY_API = os.getenv("THIRD_PARTY_API", "https://api.github.com/zen")
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "o11ylab")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# 配置 OpenTelemetry Resource
resource = Resource(attributes={
    SERVICE_NAME: "service-a",
    SERVICE_VERSION: "1.0.0",
    "service.namespace": "o11y-lab",
    "deployment.environment": "lab"
})

# 配置 Tracer Provider
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(trace_provider)

# 配置 Meter Provider
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# 配置 Logger Provider for OTLP log export
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True))
)

# 添加 OTLP logging handler
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

# 自动埋点日志（添加 trace context）
LoggingInstrumentor().instrument(set_logging_format=True)

# 自动埋点 psycopg2 (PostgreSQL)
Psycopg2Instrumentor().instrument()

# 创建 FastAPI app
app = FastAPI(title="Service A", version="1.0.0")

# 自动埋点 FastAPI
FastAPIInstrumentor.instrument_app(app)

# 自动埋点 HTTPX
HTTPXClientInstrumentor().instrument()

# 获取 tracer 和 meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# 自定义 metrics
process_counter = meter.create_counter(
    name="service_a_process_total",
    description="Total number of process requests",
    unit="1"
)

db_query_duration = meter.create_histogram(
    name="service_a_db_query_duration_seconds",
    description="Duration of database queries",
    unit="s"
)

external_call_counter = meter.create_counter(
    name="service_a_external_calls_total",
    description="Total number of external service calls",
    unit="1"
)

def get_db_connection():
    """Tty to connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def init_db():
    """Initialize the database schema"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id SERIAL PRIMARY KEY,
                trace_id VARCHAR(32),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                endpoint VARCHAR(255),
                status VARCHAR(50),
                duration_ms INTEGER
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Service A starting up...")
    init_db()
    logger.info("Service A startup complete")

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health check called")
    return {"status": "healthy", "service": "service-a"}

@app.get("/process")
async def process():
    """
    Main processing endpoint
    Invokes database operations, third-party API, Service D and Service B
    """
    start_time = time.time()
    logger.info("Starting process request in Service A")

    process_counter.add(1, {"endpoint": "/process"})

    with tracer.start_as_current_span("service_a.process") as span:
        # Get current trace ID to correlate logs and traces
        trace_id = format(span.get_span_context().trace_id, '032x')
        span.set_attribute("trace_id", trace_id)
        span.set_attribute("service.operation", "process")

        try:
            logger.info("Querying database")
            db_start = time.time()

            with tracer.start_as_current_span("service_a.database_query"):
                conn = get_db_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor)

                cur.execute(
                    "INSERT INTO request_logs (trace_id, endpoint, status) VALUES (%s, %s, %s) RETURNING id",
                    (trace_id, "/process", "started")
                )
                log_id = cur.fetchone()['id']

                cur.execute(
                    "SELECT COUNT(*) as total FROM request_logs WHERE timestamp > NOW() - INTERVAL '1 hour'"
                )
                recent_requests = cur.fetchone()['total']

                conn.commit()
                cur.close()
                conn.close()

            db_duration = time.time() - db_start
            db_query_duration.record(db_duration, {"operation": "insert_and_query"})
            logger.info(f"Database query completed in {db_duration:.3f}s, log_id={log_id}, recent_requests={recent_requests}")

            # 2. Invoke third-party API
            logger.info(f"Calling third-party API: {THIRD_PARTY_API}")
            external_call_counter.add(1, {"target": "third_party_api"})

            with tracer.start_as_current_span("service_a.call_third_party_api"):
                async with httpx.AsyncClient() as client:
                    try:
                        third_party_response = await client.get(THIRD_PARTY_API, timeout=5.0)
                        third_party_data = third_party_response.text
                        logger.info(f"Third-party API response: {third_party_data[:50]}...")
                    except Exception as e:
                        logger.warning(f"Third-party API call failed: {str(e)}")
                        third_party_data = "unavailable"

            # 3. invoke Service D and Service B
            logger.info("Calling Service D and Service B")
            external_call_counter.add(1, {"target": "service_d"})
            external_call_counter.add(1, {"target": "service_b"})

            async with httpx.AsyncClient() as client:
                with tracer.start_as_current_span("service_a.call_service_d"):
                    try:
                        service_d_response = await client.get(
                            f"{SERVICE_D_URL}/compute",
                            params={"value": random.randint(1, 100)},
                            timeout=10.0
                        )
                        service_d_data = service_d_response.json()
                        logger.info(f"Service D response: {service_d_data}")
                    except Exception as e:
                        logger.error(f"Failed to call Service D: {str(e)}")
                        service_d_data = {"error": str(e)}

                with tracer.start_as_current_span("service_a.call_service_b"):
                    try:
                        service_b_response = await client.post(
                            f"{SERVICE_B_URL}/enqueue",
                            json={"message": "Process request", "trace_id": trace_id},
                            timeout=10.0
                        )
                        service_b_data = service_b_response.json()
                        logger.info(f"Service B response: {service_b_data}")
                    except Exception as e:
                        logger.error(f"Failed to call Service B: {str(e)}")
                        service_b_data = {"error": str(e)}

            with tracer.start_as_current_span("service_a.update_database"):
                conn = get_db_connection()
                cur = conn.cursor()
                duration_ms = int((time.time() - start_time) * 1000)
                cur.execute(
                    "UPDATE request_logs SET status = %s, duration_ms = %s WHERE id = %s",
                    ("completed", duration_ms, log_id)
                )
                conn.commit()
                cur.close()
                conn.close()

            total_duration = time.time() - start_time
            logger.info(f"Process request completed in {total_duration:.3f}s")

            span.set_attribute("response.status", "success")
            span.set_attribute("request.duration_ms", duration_ms)
            span.set_attribute("database.log_id", log_id)

            return {
                "status": "success",
                "service": "service-a",
                "trace_id": trace_id,
                "duration_ms": duration_ms,
                "data": {
                    "log_id": log_id,
                    "recent_requests": recent_requests,
                    "third_party": third_party_data[:100],
                    "service_d": service_d_data,
                    "service_b": service_b_data
                }
            }

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get service statistics from the database"""
    logger.info("Getting statistics")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                COUNT(*) as total_requests,
                AVG(duration_ms) as avg_duration_ms,
                MAX(duration_ms) as max_duration_ms
            FROM request_logs
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        stats = cur.fetchone()

        cur.close()
        conn.close()

        return {
            "service": "service-a",
            "stats": dict(stats) if stats else {}
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
