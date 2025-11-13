"""
Service A - 混合 Instrumentation 示例
展示如何结合 Auto Instrumentation 和 Programmatic Instrumentation

使用方式：
1. 自动埋点由 opentelemetry-instrument 处理（FastAPI、httpx、psycopg2）
2. 自定义 span、metrics 由代码控制
3. 启动命令：opentelemetry-instrument python main.py
"""
import os
import logging
import time
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor


from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME


logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-a-hybrid", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}',
    handlers=[
        logging.StreamHandler()  # export log to console
    ]
)
logger = logging.getLogger(__name__)


SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8002")
SERVICE_D_URL = os.getenv("SERVICE_D_URL", "http://service-d:8004")
THIRD_PARTY_API = os.getenv("THIRD_PARTY_API", "https://api.github.com/zen")
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "o11ylab")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# ============================================================
# 混合模式 Logger 配置
# TracerProvider、MeterProvider 由 opentelemetry-instrument 自動建立
# 但 Python 的 LoggerProvider 需要手動設定 OTLP exporter
# ============================================================

resource = Resource.create({
    SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "service-a-hybrid")
})

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True
        )
    )
)

# 添加 LoggingHandler 將 Python logging 連接到 OpenTelemetry
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    LifeCycle manager for FastAPI app
    """
    # Startup
    logger.info("Service A (Hybrid Mode) starting up...")
    logger.info("Auto instrumentation: FastAPI, httpx, psycopg2")
    logger.info("Custom instrumentation: Business spans, metrics, attributes")
    init_db()
    logger.info("Service A startup complete")

    yield 

    # Shutdown 
    logger.info("Service A shutting down...")

app = FastAPI(
    title="Service A (Hybrid Instrumentation)",
    version="2.0.0",
    lifespan=lifespan
)

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


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

# ============================================================
# 注意：psycopg2 將由 opentelemetry-instrument 自動監測埋點
# ============================================================
def get_db_connection():
    """Get a new database connection"""
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
                duration_ms INTEGER,
                instrumentation_type VARCHAR(50)
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health check called")
    return {"status": "healthy", "service": "service-a-hybrid", "instrumentation": "hybrid"}

@app.get("/process")
async def process():
    """
    Main processing endpoint demonstrating hybrid instrumentation.

    Auto Instrument（由 opentelemetry-instrument 處理）：
    - FastAPI 框架 HTTP Req/Res
    - httpx 的 HTTP client interactions
    - psycopg2 database queries

    Manual Instrument（程式碼中自定義）：
    - Business logic spans
    - Customize attributes
    - Business metrics
    """
    start_time = time.time()
    logger.info("Starting process request in Service A (Hybrid)")

    process_counter.add(1, {"endpoint": "/process", "instrumentation": "hybrid"})

    with tracer.start_as_current_span("service_a.business_logic") as span:
        # Get trace ID for logging and attributes
        trace_id = format(span.get_span_context().trace_id, '032x')
        span.set_attribute("trace_id", trace_id)
        span.set_attribute("service.operation", "process")
        span.set_attribute("instrumentation.type", "hybrid")

        try:
            logger.info("Querying database")
            db_start = time.time()

            with tracer.start_as_current_span("service_a.database_business_logic") as db_span:
                db_span.set_attribute("db.operation", "insert_and_query")

                conn = get_db_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor)

                cur.execute(
                    "INSERT INTO request_logs (trace_id, endpoint, status, instrumentation_type) VALUES (%s, %s, %s, %s) RETURNING id",
                    (trace_id, "/process", "started", "hybrid")
                )
                log_id = cur.fetchone()['id']
                db_span.set_attribute("db.log_id", log_id)

                cur.execute(
                    "SELECT COUNT(*) as total FROM request_logs WHERE timestamp > NOW() - INTERVAL '1 hour'"
                )
                recent_requests = cur.fetchone()['total']
                db_span.set_attribute("db.recent_requests", recent_requests)

                conn.commit()
                cur.close()
                conn.close()

            db_duration = time.time() - db_start
            db_query_duration.record(db_duration, {"operation": "insert_and_query", "instrumentation": "hybrid"})
            logger.info(f"Database query completed in {db_duration:.3f}s, log_id={log_id}")

            # ============================================================
            # 2. Invoke third-party API
            # httpx will be auto-instrumented, we add business span and attributes
            # ============================================================
            logger.info(f"Calling third-party API: {THIRD_PARTY_API}")
            external_call_counter.add(1, {"target": "third_party_api", "instrumentation": "hybrid"})

            with tracer.start_as_current_span("service_a.external_api_business") as api_span:
                api_span.set_attribute("external.api.url", THIRD_PARTY_API)

                async with httpx.AsyncClient() as client:
                    try:
                        third_party_response = await client.get(THIRD_PARTY_API, timeout=5.0)
                        third_party_data = third_party_response.text
                        api_span.set_attribute("external.api.status", "success")
                        logger.info(f"Third-party API response: {third_party_data[:50]}...")
                    except Exception as e:
                        logger.warning(f"Third-party API call failed: {str(e)}")
                        third_party_data = "unavailable"
                        api_span.set_attribute("external.api.status", "failed")


            logger.info("Calling Service D and Service B")
            external_call_counter.add(2, {"target": "downstream_services", "instrumentation": "hybrid"})

            async with httpx.AsyncClient() as client:
                with tracer.start_as_current_span("service_a.call_service_d_business") as d_span:
                    d_span.set_attribute("service.target", "service-d")
                    try:
                        service_d_response = await client.get(
                            f"{SERVICE_D_URL}/compute",
                            params={"value": random.randint(1, 100)},
                            timeout=10.0
                        )
                        service_d_data = service_d_response.json()
                        d_span.set_attribute("service.d.status", "success")
                        logger.info(f"Service D response: {service_d_data}")
                    except Exception as e:
                        logger.error(f"Failed to call Service D: {str(e)}")
                        service_d_data = {"error": str(e)}
                        d_span.set_attribute("service.d.status", "failed")

                with tracer.start_as_current_span("service_a.call_service_b_business") as b_span:
                    b_span.set_attribute("service.target", "service-b")
                    try:
                        service_b_response = await client.post(
                            f"{SERVICE_B_URL}/enqueue",
                            json={"message": "Process request", "trace_id": trace_id},
                            timeout=10.0
                        )
                        service_b_data = service_b_response.json()
                        b_span.set_attribute("service.b.status", "success")
                        logger.info(f"Service B response: {service_b_data}")
                    except Exception as e:
                        logger.error(f"Failed to call Service B: {str(e)}")
                        service_b_data = {"error": str(e)}
                        b_span.set_attribute("service.b.status", "failed")

            with tracer.start_as_current_span("service_a.update_status"):
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
                "service": "service-a-hybrid",
                "instrumentation": "hybrid (auto + programmatic)",
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
    """Get service statistics from the last hour"""
    logger.info("Getting statistics")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                COUNT(*) as total_requests,
                AVG(duration_ms) as avg_duration_ms,
                MAX(duration_ms) as max_duration_ms,
                COUNT(*) FILTER (WHERE instrumentation_type = 'hybrid') as hybrid_requests
            FROM request_logs
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        stats = cur.fetchone()

        cur.close()
        conn.close()

        return {
            "service": "service-a-hybrid",
            "stats": dict(stats) if stats else {}
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def info():
    """Get service information and instrumentation details"""
    return {
        "service": "service-a-hybrid",
        "version": "2.0.0",
        "instrumentation": {
            "type": "hybrid",
            "auto": [
                "FastAPI (HTTP framework)",
                "httpx (HTTP client)",
                "psycopg2 (PostgreSQL)"
            ],
            "programmatic": [
                "Business logic spans",
                "Custom attributes",
                "Business metrics"
            ]
        },
        "usage": "Started with: opentelemetry-instrument python main.py"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
