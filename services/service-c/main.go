package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"log"

	"github.com/gin-gonic/gin"
	"github.com/segmentio/kafka-go"
	"go.opentelemetry.io/contrib/bridges/otelslog"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/propagation"
	sdklog "go.opentelemetry.io/otel/sdk/log"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	sdkresource "go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.37.0"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// 全局变量
var (
	tracer             trace.Tracer
	meter              metric.Meter
	logger             *slog.Logger
	kafkaReader        *kafka.Reader
	processedCounter   metric.Int64Counter
	processingDuration metric.Float64Histogram
	messagesReceived   int64
	messagesProcessed  int64
	mu                 sync.RWMutex
)

// StructuredLog 结构化日志格式
type StructuredLog struct {
	Time    string `json:"time"`
	Level   string `json:"level"`
	Service string `json:"service"`
	TraceID string `json:"trace_id"`
	SpanID  string `json:"span_id"`
	Message string `json:"message"`
}

// MessagePayload Kafka 消息载荷
type MessagePayload struct {
	Message   string `json:"message"`
	TraceID   string `json:"trace_id"`
	Timestamp int64  `json:"timestamp"`
	Source    string `json:"source"`
}

// logStructured 输出结构化日志（使用 OpenTelemetry）
func logStructured(ctx context.Context, level, message string) {
	spanCtx := trace.SpanContextFromContext(ctx)

	// 使用 slog 记录日志，trace context 会自动注入
	switch level {
	case "INFO":
		logger.InfoContext(ctx, message,
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)
	case "ERROR":
		logger.ErrorContext(ctx, message,
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)
	case "WARN":
		logger.WarnContext(ctx, message,
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)
	default:
		logger.InfoContext(ctx, message,
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)
	}
}

// initTracer 初始化 Tracer
func initTracer() (*sdktrace.TracerProvider, error) {
	collectorEndpoint := os.Getenv("OTEL_COLLECTOR_ENDPOINT")
	if collectorEndpoint == "" {
		collectorEndpoint = "otel-collector:4317"
	}

	ctx := context.Background()

	conn, err := grpc.DialContext(ctx, collectorEndpoint,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC connection: %w", err)
	}

	exporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create trace exporter: %w", err)
	}

	resource, err := sdkresource.Merge(
		sdkresource.Default(),
		sdkresource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("service-c"),
			semconv.ServiceVersion("1.0.0"),
			attribute.String("service.namespace", "o11y-lab"),
			attribute.String("deployment.environment", "lab"),
			attribute.String("service.language", "go"),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(resource),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	return tp, nil
}

// initMeter 初始化 Meter
func initMeter() (*sdkmetric.MeterProvider, error) {
	collectorEndpoint := os.Getenv("OTEL_COLLECTOR_ENDPOINT")
	if collectorEndpoint == "" {
		collectorEndpoint = "otel-collector:4317"
	}

	ctx := context.Background()

	conn, err := grpc.DialContext(ctx, collectorEndpoint,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC connection: %w", err)
	}

	exporter, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create metric exporter: %w", err)
	}

	resource, err := sdkresource.Merge(
		sdkresource.Default(),
		sdkresource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("service-c"),
			semconv.ServiceVersion("1.0.0"),
			attribute.String("service.namespace", "o11y-lab"),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	mp := sdkmetric.NewMeterProvider(
		sdkmetric.WithResource(resource),
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(exporter, sdkmetric.WithInterval(10*time.Second))),
	)

	otel.SetMeterProvider(mp)

	return mp, nil
}

// initLogger 初始化 Logger
func initLogger() (*sdklog.LoggerProvider, error) {
	collectorEndpoint := os.Getenv("OTEL_COLLECTOR_ENDPOINT")
	if collectorEndpoint == "" {
		collectorEndpoint = "otel-collector:4317"
	}

	ctx := context.Background()

	conn, err := grpc.NewClient(collectorEndpoint,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC connection: %w", err)
	}

	exporter, err := otlploggrpc.New(ctx, otlploggrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create log exporter: %w", err)
	}

	resource, err := sdkresource.Merge(
		sdkresource.Default(),
		sdkresource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("service-c"),
			semconv.ServiceVersion("1.0.0"),
			attribute.String("service.namespace", "o11y-lab"),
			attribute.String("deployment.environment", "lab"),
			attribute.String("service.language", "go"),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	lp := sdklog.NewLoggerProvider(
		sdklog.WithProcessor(sdklog.NewBatchProcessor(exporter)),
		sdklog.WithResource(resource),
	)

	// Create slog logger with OpenTelemetry bridge
	logger = otelslog.NewLogger("service-c", otelslog.WithLoggerProvider(lp))
	slog.SetDefault(logger)

	return lp, nil
}

// initKafkaConsumer 初始化 Kafka Consumer
func initKafkaConsumer() {
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	if kafkaBroker == "" {
		kafkaBroker = "kafka:9092"
	}

	kafkaReader = kafka.NewReader(kafka.ReaderConfig{
		Brokers:        []string{kafkaBroker},
		Topic:          "o11y-lab-events",
		GroupID:        "service-c-consumer",
		MinBytes:       10e1,
		MaxBytes:       10e6,
		CommitInterval: time.Second,
		StartOffset:    kafka.LastOffset,
	})

	log.Printf("Kafka consumer initialized for broker: %s, topic: o11y-lab-events", kafkaBroker)
}

// kafkaHeaderCarrier 实现 TextMapCarrier 接口用于 Kafka headers
type kafkaHeaderCarrier struct {
	headers []kafka.Header
}

func (c *kafkaHeaderCarrier) Get(key string) string {
	for _, h := range c.headers {
		if h.Key == key {
			return string(h.Value)
		}
	}
	return ""
}

func (c *kafkaHeaderCarrier) Set(key string, value string) {
	c.headers = append(c.headers, kafka.Header{
		Key:   key,
		Value: []byte(value),
	})
}

func (c *kafkaHeaderCarrier) Keys() []string {
	keys := make([]string, len(c.headers))
	for i, h := range c.headers {
		keys[i] = h.Key
	}
	return keys
}

// processMessage 处理单个 Kafka 消息
func processMessage(ctx context.Context, msg kafka.Message) error {
	start := time.Now()

	// 从 Kafka headers 提取 trace context
	carrier := &kafkaHeaderCarrier{headers: msg.Headers}
	ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

	// 手动创建 span，继承从 Kafka 提取的 context
	ctx, span := tracer.Start(ctx, "service_c.process_message",
		trace.WithSpanKind(trace.SpanKindConsumer),
		trace.WithAttributes(
			attribute.String("messaging.system", "kafka"),
			attribute.String("messaging.destination", "o11y-lab-events"),
			attribute.Int64("messaging.offset", msg.Offset),
			attribute.Int("messaging.partition", msg.Partition),
		),
	)
	defer span.End()

	mu.Lock()
	messagesReceived++
	mu.Unlock()

	logStructured(ctx, "INFO", fmt.Sprintf("Processing message from Kafka, offset: %d", msg.Offset))

	// 解析消息
	var payload MessagePayload
	if err := json.Unmarshal(msg.Value, &payload); err != nil {
		logStructured(ctx, "ERROR", fmt.Sprintf("Failed to unmarshal message: %v", err))
		span.SetStatus(codes.Error, "Failed to unmarshal message")
		span.RecordError(err)
		return err
	}

	span.SetAttributes(
		attribute.String("message.trace_id", payload.TraceID),
		attribute.String("message.source", payload.Source),
		attribute.String("message.content", payload.Message),
		attribute.Int64("message.timestamp", payload.Timestamp),
	)

	logStructured(ctx, "INFO", fmt.Sprintf("Message payload: %+v", payload))

	// 模拟业务处理
	ctx, processSpan := tracer.Start(ctx, "service_c.business_logic")
	logStructured(ctx, "INFO", "Starting business logic processing")

	// 模拟一些处理时间
	time.Sleep(time.Duration(100+msg.Offset%200) * time.Millisecond)

	// 模拟子操作
	ctx, subSpan := tracer.Start(ctx, "service_c.data_transformation")
	logStructured(ctx, "INFO", "Transforming message data")

	transformedData := map[string]interface{}{
		"original_message": payload.Message,
		"processed_at":     time.Now().Unix(),
		"processor":        "service-c",
		"trace_id":         payload.TraceID,
	}

	logStructured(ctx, "INFO", fmt.Sprintf("Transformed data: %+v", transformedData))
	subSpan.End()

	// 模拟另一个子操作
	ctx, validationSpan := tracer.Start(ctx, "service_c.validation")
	logStructured(ctx, "INFO", "Validating processed data")

	// 简单验证
	if len(payload.Message) > 0 {
		validationSpan.SetAttributes(attribute.Bool("validation.passed", true))
		logStructured(ctx, "INFO", "Validation passed")
	} else {
		validationSpan.SetAttributes(attribute.Bool("validation.passed", false))
		logStructured(ctx, "WARN", "Validation failed: empty message")
	}

	validationSpan.End()
	processSpan.End()

	duration := time.Since(start).Seconds()

	// 记录 metrics
	processedCounter.Add(ctx, 1, metric.WithAttributes(
		attribute.String("source", payload.Source),
		attribute.String("status", "success"),
	))

	processingDuration.Record(ctx, duration, metric.WithAttributes(
		attribute.String("operation", "process_message"),
	))

	mu.Lock()
	messagesProcessed++
	mu.Unlock()

	span.SetStatus(codes.Ok, "Message processed successfully")
	logStructured(ctx, "INFO", fmt.Sprintf("Message processed successfully in %.3fs", duration))

	return nil
}

// consumeMessages 持续消费 Kafka 消息
func consumeMessages(ctx context.Context) {
	log.Println("Starting Kafka consumer...")

	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping Kafka consumer...")
			return
		default:
			msg, err := kafkaReader.FetchMessage(ctx)
			if err != nil {
				if err == context.Canceled {
					return
				}
				log.Printf("Error fetching message: %v", err)
				time.Sleep(time.Second)
				continue
			}

			// 处理消息
			if err := processMessage(ctx, msg); err != nil {
				log.Printf("Error processing message: %v", err)
			}

			// 提交 offset
			if err := kafkaReader.CommitMessages(ctx, msg); err != nil {
				log.Printf("Error committing message: %v", err)
			}
		}
	}
}

// healthHandler 健康检查
func healthHandler(c *gin.Context) {
	ctx := c.Request.Context()
	logStructured(ctx, "INFO", "Health check called")

	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"service": "service-c",
	})
}

// statsHandler 获取统计信息
func statsHandler(c *gin.Context) {
	ctx := c.Request.Context()
	logStructured(ctx, "INFO", "Stats endpoint called")

	mu.RLock()
	received := messagesReceived
	processed := messagesProcessed
	mu.RUnlock()

	c.JSON(http.StatusOK, gin.H{
		"service":            "service-c",
		"messages_received":  received,
		"messages_processed": processed,
		"consumer_group":     "service-c-consumer",
		"topic":              "o11y-lab-events",
	})
}

// infoHandler 获取服务信息
func infoHandler(c *gin.Context) {
	ctx := c.Request.Context()
	logStructured(ctx, "INFO", "Info endpoint called")

	c.JSON(http.StatusOK, gin.H{
		"service":         "service-c",
		"version":         "1.0.0",
		"language":        "go",
		"framework":       "gin",
		"instrumentation": "OpenTelemetry Manual",
		"capabilities": []string{
			"kafka message consumption",
			"manual instrumentation",
			"structured logging",
			"context propagation",
		},
	})
}

func main() {
	log.Println("Starting Service C...")

	// 初始化 OpenTelemetry
	tp, err := initTracer()
	if err != nil {
		log.Fatalf("Failed to initialize tracer: %v", err)
	}
	defer func() {
		if err := tp.Shutdown(context.Background()); err != nil {
			log.Printf("Error shutting down tracer provider: %v", err)
		}
	}()

	mp, err := initMeter()
	if err != nil {
		log.Fatalf("Failed to initialize meter: %v", err)
	}
	defer func() {
		if err := mp.Shutdown(context.Background()); err != nil {
			log.Printf("Error shutting down meter provider: %v", err)
		}
	}()

	lp, err := initLogger()
	if err != nil {
		log.Fatalf("Failed to initialize logger: %v", err)
	}
	defer func() {
		if err := lp.Shutdown(context.Background()); err != nil {
			log.Printf("Error shutting down logger provider: %v", err)
		}
	}()

	// 创建 tracer 和 meter
	tracer = otel.Tracer("service-c")
	meter = otel.Meter("service-c")

	// 创建自定义 metrics
	processedCounter, err = meter.Int64Counter(
		"service_c_messages_processed_total",
		metric.WithDescription("Total number of messages processed"),
		metric.WithUnit("1"),
	)
	if err != nil {
		log.Fatalf("Failed to create processed counter: %v", err)
	}

	processingDuration, err = meter.Float64Histogram(
		"service_c_processing_duration_seconds",
		metric.WithDescription("Duration of message processing"),
		metric.WithUnit("s"),
	)
	if err != nil {
		log.Fatalf("Failed to create processing duration histogram: %v", err)
	}

	// 初始化 Kafka Consumer
	initKafkaConsumer()
	defer kafkaReader.Close()

	// 创建 context 用于优雅关闭
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// 启动 Kafka 消费者
	go consumeMessages(ctx)

	// 创建 Gin router (使用 New 而非 Default，避免非结构化日志)
	r := gin.New()

	// 添加 Recovery 中间件
	r.Use(gin.Recovery())

	// 添加 OpenTelemetry 中间件
	r.Use(otelgin.Middleware("service-c"))

	// 添加自定义的 JSON 格式日志中间件
	r.Use(func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery

		c.Next()

		// 获取 trace context
		ctx := c.Request.Context()
		spanCtx := trace.SpanContextFromContext(ctx)

		// 使用 slog 记录 JSON 格式的访问日志
		logger.InfoContext(ctx, "HTTP request",
			slog.String("method", c.Request.Method),
			slog.String("path", path),
			slog.String("query", raw),
			slog.Int("status", c.Writer.Status()),
			slog.Duration("latency", time.Since(start)),
			slog.String("client_ip", c.ClientIP()),
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)
	})

	// 注册路由
	r.GET("/health", healthHandler)
	r.GET("/stats", statsHandler)
	r.GET("/info", infoHandler)

	// 优雅关闭
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
		<-sigChan
		log.Println("Shutting down gracefully...")
		cancel()
	}()

	// 启动 HTTP 服务
	log.Println("Service C listening on :8003")
	if err := r.Run(":8003"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
