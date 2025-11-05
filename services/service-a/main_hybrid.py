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

# ============================================================
# OpenTelemetry - 混合模式导入必要的组件
# TracerProvider/MeterProvider 由 opentelemetry-instrument 自动创建
# 但 LoggerProvider 需要手动配置才能发送日志到 OTLP
# ============================================================
from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# 配置结构化日志
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-a-hybrid", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}'
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

# ============================================================
# 混合模式日志配置
# TracerProvider、MeterProvider 由 opentelemetry-instrument 自动创建
# 但 Python 的 LoggerProvider 需要手动配置 OTLP exporter
# ============================================================

# 获取 resource（从环境变量）
resource = Resource.create({
    SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "service-a-hybrid")
})

# 配置 Logger Provider 用于发送日志到 OTLP
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# 添加 OTLP Log Exporter
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True
        )
    )
)

# 添加 LoggingHandler 将 Python logging 连接到 OpenTelemetry
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

# ============================================================
# 使用 lifespan context manager 处理启动和关闭事件
# 这是 FastAPI 推荐的新方式，替代 @app.on_event
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：初始化数据库、日志配置等
    - 关闭时：清理资源（如果需要）
    """
    # Startup
    logger.info("Service A (Hybrid Mode) starting up...")
    logger.info("Auto instrumentation: FastAPI, httpx, psycopg2")
    logger.info("Custom instrumentation: Business spans, metrics, attributes")
    init_db()
    logger.info("Service A startup complete")

    yield  # 应用运行期间

    # Shutdown (可选)
    logger.info("Service A shutting down...")

# ============================================================
# 创建 FastAPI app with lifespan
# 注意：不再手动调用 FastAPIInstrumentor.instrument_app()
# 这将由 opentelemetry-instrument 自动处理
# ============================================================
app = FastAPI(
    title="Service A (Hybrid Instrumentation)",
    version="2.0.0",
    lifespan=lifespan
)

# ============================================================
# 获取 tracer 和 meter - 用于自定义埋点
# ============================================================
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# ============================================================
# 自定义 metrics - 业务指标
# ============================================================
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
# 数据库连接
# 注意：psycopg2 将由 opentelemetry-instrument 自动埋点
# ============================================================
def get_db_connection():
    """获取数据库连接"""
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
    """初始化数据库表"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 创建请求日志表
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
    """健康检查"""
    logger.info("Health check called")
    return {"status": "healthy", "service": "service-a-hybrid", "instrumentation": "hybrid"}

@app.get("/process")
async def process():
    """
    主要的业务处理端点

    自动埋点（由 opentelemetry-instrument 处理）：
    - FastAPI 框架层面的 HTTP 请求/响应
    - httpx 的 HTTP client 调用
    - psycopg2 的数据库查询

    手动埋点（代码控制）：
    - 业务逻辑的自定义 span
    - 自定义 attributes
    - 业务 metrics
    """
    start_time = time.time()
    logger.info("Starting process request in Service A (Hybrid)")

    # 增加自定义计数器
    process_counter.add(1, {"endpoint": "/process", "instrumentation": "hybrid"})

    # ============================================================
    # 创建自定义业务 span
    # 框架层面的 span 由 auto instrumentation 自动创建
    # ============================================================
    with tracer.start_as_current_span("service_a.business_logic") as span:
        # 获取当前 trace_id 用于关联
        trace_id = format(span.get_span_context().trace_id, '032x')
        span.set_attribute("trace_id", trace_id)
        span.set_attribute("service.operation", "process")
        span.set_attribute("instrumentation.type", "hybrid")

        try:
            # ============================================================
            # 1. 查询数据库
            # psycopg2 的查询会被自动埋点，我们只需添加业务 span
            # ============================================================
            logger.info("Querying database")
            db_start = time.time()

            with tracer.start_as_current_span("service_a.database_business_logic") as db_span:
                db_span.set_attribute("db.operation", "insert_and_query")

                conn = get_db_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor)

                # 插入请求记录
                cur.execute(
                    "INSERT INTO request_logs (trace_id, endpoint, status, instrumentation_type) VALUES (%s, %s, %s, %s) RETURNING id",
                    (trace_id, "/process", "started", "hybrid")
                )
                log_id = cur.fetchone()['id']
                db_span.set_attribute("db.log_id", log_id)

                # 查询最近的请求
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
            # 2. 调用第三方 API
            # httpx 会被自动埋点，我们添加业务逻辑 span
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

            # ============================================================
            # 3. 并行调用 Service D 和 Service B
            # httpx 自动埋点，业务逻辑自定义
            # ============================================================
            logger.info("Calling Service D and Service B")
            external_call_counter.add(2, {"target": "downstream_services", "instrumentation": "hybrid"})

            async with httpx.AsyncClient() as client:
                # 调用 Service D
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

                # 调用 Service B
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

            # ============================================================
            # 4. 更新数据库状态
            # ============================================================
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
    """获取统计信息"""
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
    """获取服务信息"""
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
