"""
API Gateway - 统一的请求入口
使用 OpenTelemetry 自动埋点
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"api-gateway", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}'
)
logger = logging.getLogger(__name__)

# 配置 OpenTelemetry
SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://service-a:8001")
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")

# 创建 Resource
resource = Resource(attributes={
    SERVICE_NAME: "api-gateway",
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

# 自动注入 trace context 到日志
LoggingInstrumentor().instrument(set_logging_format=True)

# 创建 FastAPI app
app = FastAPI(title="API Gateway", version="1.0.0")

# 自动埋点 FastAPI
FastAPIInstrumentor.instrument_app(app)

# 自动埋点 HTTPX client
HTTPXClientInstrumentor().instrument()

# 创建 tracer 和 meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# 创建自定义 metrics
request_counter = meter.create_counter(
    name="gateway_requests_total",
    description="Total number of requests received by gateway",
    unit="1"
)

request_duration = meter.create_histogram(
    name="gateway_request_duration_seconds",
    description="Duration of gateway requests",
    unit="s"
)

@app.get("/health")
async def health():
    """健康检查端点"""
    logger.info("Health check called")
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/api/process")
async def process_request():
    """
    处理请求的主要端点
    调用 Service A，Service A 会继续调用其他服务
    """
    logger.info("Received process request at gateway")

    # 增加请求计数
    request_counter.add(1, {"endpoint": "/api/process", "method": "GET"})

    with tracer.start_as_current_span("gateway.process_request") as span:
        span.set_attribute("endpoint", "/api/process")
        span.set_attribute("gateway.version", "1.0.0")

        try:
            # 调用 Service A
            logger.info(f"Calling Service A at {SERVICE_A_URL}/process")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SERVICE_A_URL}/process",
                    timeout=30.0
                )

                span.set_attribute("http.status_code", response.status_code)

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully received response from Service A: {result}")
                    span.set_attribute("response.status", "success")
                    return {
                        "status": "success",
                        "message": "Request processed through gateway",
                        "data": result
                    }
                else:
                    logger.error(f"Service A returned error: {response.status_code}")
                    span.set_attribute("response.status", "error")
                    span.set_attribute("error", True)
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Service A returned error: {response.text}"
                    )

        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Service A: {str(e)}", exc_info=True)
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to Service A: {str(e)}"
            )

@app.get("/api/info")
async def get_info():
    """获取网关信息"""
    logger.info("Info endpoint called")
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "instrumentation": "OpenTelemetry Auto",
        "backends": {
            "service_a": SERVICE_A_URL,
            "collector": OTEL_COLLECTOR_ENDPOINT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
