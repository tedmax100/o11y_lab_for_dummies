"""
Service D - 计算服务
使用 Flask 框架展示 OpenTelemetry 自动埋点
"""
import os
import logging
import random
import time
from flask import Flask, request, jsonify
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
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
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-d", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}'
)
logger = logging.getLogger(__name__)

# 环境变量配置
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")

# 配置 OpenTelemetry Resource
resource = Resource(attributes={
    SERVICE_NAME: "service-d",
    SERVICE_VERSION: "1.0.0",
    "service.namespace": "o11y-lab",
    "deployment.environment": "lab",
    "service.framework": "flask"
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

# 创建 Flask app
app = Flask(__name__)

# 自动埋点 Flask
FlaskInstrumentor().instrument_app(app)

# 获取 tracer 和 meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# 自定义 metrics
compute_counter = meter.create_counter(
    name="service_d_compute_total",
    description="Total number of compute operations",
    unit="1"
)

compute_duration = meter.create_histogram(
    name="service_d_compute_duration_seconds",
    description="Duration of compute operations",
    unit="s"
)

computation_value = meter.create_histogram(
    name="service_d_computation_value",
    description="Computed values distribution",
    unit="1"
)

def fibonacci(n):
    """计算斐波那契数列（模拟计算密集型任务）"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def prime_factors(n):
    """计算质因数分解"""
    factors = []
    d = 2
    while d * d <= n:
        while (n % d) == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    logger.info("Health check called")
    return jsonify({"status": "healthy", "service": "service-d"})

@app.route('/compute', methods=['GET'])
def compute():
    """
    执行计算操作
    接收一个数值参数，执行多种计算
    """
    start_time = time.time()
    value = request.args.get('value', default=10, type=int)

    logger.info(f"Starting computation with value={value}")

    # 增加计数器
    compute_counter.add(1, {"operation": "compute"})

    with tracer.start_as_current_span("service_d.compute") as span:
        trace_id = format(span.get_span_context().trace_id, '032x')
        span.set_attribute("compute.input_value", value)
        span.set_attribute("trace_id", trace_id)

        try:
            # 1. 斐波那契计算
            with tracer.start_as_current_span("service_d.fibonacci") as fib_span:
                fib_input = min(value, 20)  # 限制最大值避免太慢
                logger.info(f"Computing fibonacci({fib_input})")
                fib_result = fibonacci(fib_input)
                fib_span.set_attribute("fibonacci.input", fib_input)
                fib_span.set_attribute("fibonacci.result", fib_result)
                logger.info(f"Fibonacci result: {fib_result}")

            # 2. 质因数分解
            with tracer.start_as_current_span("service_d.prime_factors") as prime_span:
                prime_input = max(value, 2)
                logger.info(f"Computing prime factors of {prime_input}")
                factors = prime_factors(prime_input)
                prime_span.set_attribute("prime.input", prime_input)
                prime_span.set_attribute("prime.factors_count", len(factors))
                logger.info(f"Prime factors: {factors}")

            # 3. 随机延迟模拟
            with tracer.start_as_current_span("service_d.simulate_processing"):
                delay = random.uniform(0.1, 0.5)
                logger.info(f"Simulating processing delay: {delay:.3f}s")
                time.sleep(delay)

            # 4. 统计计算
            with tracer.start_as_current_span("service_d.statistics"):
                numbers = [random.randint(1, 100) for _ in range(10)]
                stats = {
                    "mean": sum(numbers) / len(numbers),
                    "max": max(numbers),
                    "min": min(numbers),
                    "sum": sum(numbers)
                }
                logger.info(f"Statistics computed: {stats}")

            duration = time.time() - start_time
            compute_duration.record(duration, {"operation": "compute"})
            computation_value.record(value, {"operation": "input"})

            result = {
                "status": "success",
                "service": "service-d",
                "trace_id": trace_id,
                "input_value": value,
                "results": {
                    "fibonacci": {
                        "input": fib_input,
                        "result": fib_result
                    },
                    "prime_factors": {
                        "input": prime_input,
                        "factors": factors
                    },
                    "statistics": stats
                },
                "duration_seconds": round(duration, 3)
            }

            span.set_attribute("response.status", "success")
            span.set_attribute("compute.duration_seconds", duration)
            logger.info(f"Computation completed in {duration:.3f}s")

            return jsonify(result)

        except Exception as e:
            logger.error(f"Error during computation: {str(e)}", exc_info=True)
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            return jsonify({
                "status": "error",
                "service": "service-d",
                "error": str(e)
            }), 500

@app.route('/info', methods=['GET'])
def info():
    """获取服务信息"""
    logger.info("Info endpoint called")
    return jsonify({
        "service": "service-d",
        "version": "1.0.0",
        "framework": "flask",
        "instrumentation": "OpenTelemetry Auto",
        "capabilities": [
            "fibonacci computation",
            "prime factorization",
            "statistical analysis"
        ]
    })

if __name__ == '__main__':
    logger.info("Starting Service D")
    app.run(host='0.0.0.0', port=8004, debug=False)
