package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"os"
	"time"

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

var (
	tracer         trace.Tracer
	meter          metric.Meter
	logger         *slog.Logger
	kafkaWriter    *kafka.Writer
	messageCounter metric.Int64Counter
	kafkaDuration  metric.Float64Histogram
)

// StructuredLog
type StructuredLog struct {
	Time    string `json:"time"`
	Level   string `json:"level"`
	Service string `json:"service"`
	TraceID string `json:"trace_id"`
	SpanID  string `json:"span_id"`
	Message string `json:"message"`
}

// logStructured
func logStructured(ctx context.Context, level, message string) {
	spanCtx := trace.SpanContextFromContext(ctx)

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

// initTracer
func initTracer() (*sdktrace.TracerProvider, error) {
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

	exporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create trace exporter: %w", err)
	}

	resource, err := sdkresource.Merge(
		sdkresource.Default(),
		sdkresource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("service-b"),
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

// initMeter
func initMeter() (*sdkmetric.MeterProvider, error) {
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

	exporter, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create metric exporter: %w", err)
	}

	resource, err := sdkresource.Merge(
		sdkresource.Default(),
		sdkresource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("service-b"),
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

// initLogger
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
			semconv.ServiceName("service-b"),
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
	logger = otelslog.NewLogger("service-b", otelslog.WithLoggerProvider(lp))
	slog.SetDefault(logger)

	return lp, nil
}

// initKafka
func initKafka() {
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	if kafkaBroker == "" {
		kafkaBroker = "kafka:9092"
	}

	kafkaWriter = &kafka.Writer{
		Addr:         kafka.TCP(kafkaBroker),
		Topic:        "o11y-lab-events",
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 10 * time.Millisecond,
	}

	log.Printf("Kafka writer initialized for broker: %s", kafkaBroker)
}

// EnqueueRequest
type EnqueueRequest struct {
	Message string `json:"message" binding:"required"`
	TraceID string `json:"trace_id"`
}

// healthHandler
func healthHandler(c *gin.Context) {
	ctx := c.Request.Context()
	logStructured(ctx, "INFO", "Health check called")

	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"service": "service-b",
	})
}

// enqueueHandler
func enqueueHandler(c *gin.Context) {
	ctx := c.Request.Context()

	ctx, span := tracer.Start(ctx, "service_b.enqueue",
		trace.WithSpanKind(trace.SpanKindServer),
	)
	defer span.End()

	logStructured(ctx, "INFO", "Received enqueue request")

	var req EnqueueRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		logStructured(ctx, "ERROR", fmt.Sprintf("Failed to parse request: %v", err))
		span.SetStatus(codes.Error, "Invalid request")
		span.RecordError(err)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	span.SetAttributes(
		attribute.String("message.content", req.Message),
		attribute.String("message.trace_id", req.TraceID),
	)

	messageCounter.Add(ctx, 1, metric.WithAttributes(
		attribute.String("operation", "enqueue"),
	))

	kafkaStart := time.Now()
	_, kafkaSpan := tracer.Start(ctx, "service_b.kafka_publish",
		trace.WithSpanKind(trace.SpanKindProducer),
	)

	messageData := map[string]interface{}{
		"message":   req.Message,
		"trace_id":  req.TraceID,
		"timestamp": time.Now().Unix(),
		"source":    "service-b",
	}

	messageJSON, err := json.Marshal(messageData)
	if err != nil {
		logStructured(ctx, "ERROR", fmt.Sprintf("Failed to marshal message: %v", err))
		kafkaSpan.SetStatus(codes.Error, "Failed to marshal message")
		kafkaSpan.RecordError(err)
		kafkaSpan.End()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal message"})
		return
	}

	kafkaMsg := kafka.Message{
		Key:   []byte(req.TraceID),
		Value: messageJSON,
		Headers: []kafka.Header{
			{Key: "trace_id", Value: []byte(req.TraceID)},
			{Key: "source", Value: []byte("service-b")},
		},
	}

	// Inject trace context into Kafka message headers
	carrier := &kafkaHeaderCarrier{headers: &kafkaMsg.Headers}
	otel.GetTextMapPropagator().Inject(ctx, carrier)

	logStructured(ctx, "INFO", fmt.Sprintf("Publishing message to Kafka: %s", req.Message))

	err = kafkaWriter.WriteMessages(ctx, kafkaMsg)
	kafkaDurationSeconds := time.Since(kafkaStart).Seconds()

	if err != nil {
		logStructured(ctx, "ERROR", fmt.Sprintf("Failed to write to Kafka: %v", err))
		kafkaSpan.SetStatus(codes.Error, "Failed to write to Kafka")
		kafkaSpan.RecordError(err)
		kafkaSpan.SetAttributes(
			attribute.String("kafka.topic", "o11y-lab-events"),
			attribute.Bool("kafka.success", false),
		)
		kafkaSpan.End()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to enqueue message"})
		return
	}

	kafkaSpan.SetStatus(codes.Ok, "Message published successfully")
	kafkaSpan.SetAttributes(
		attribute.String("kafka.topic", "o11y-lab-events"),
		attribute.Bool("kafka.success", true),
		attribute.Int("kafka.message_size", len(messageJSON)),
	)
	kafkaSpan.End()

	kafkaDuration.Record(ctx, kafkaDurationSeconds, metric.WithAttributes(
		attribute.String("operation", "publish"),
		attribute.String("topic", "o11y-lab-events"),
	))

	logStructured(ctx, "INFO", fmt.Sprintf("Message published to Kafka successfully, duration: %.3fs", kafkaDurationSeconds))
	span.SetStatus(codes.Ok, "Message enqueued successfully")

	c.JSON(http.StatusOK, gin.H{
		"status":   "success",
		"service":  "service-b",
		"message":  "Message enqueued to Kafka",
		"trace_id": req.TraceID,
	})
}

// infoHandler
func infoHandler(c *gin.Context) {
	ctx := c.Request.Context()
	logStructured(ctx, "INFO", "Info endpoint called")

	c.JSON(http.StatusOK, gin.H{
		"service":         "service-b",
		"version":         "1.0.0",
		"language":        "go",
		"framework":       "gin",
		"instrumentation": "OpenTelemetry Manual",
		"capabilities": []string{
			"kafka message queuing",
			"manual instrumentation",
			"structured logging",
		},
	})
}

// kafkaHeaderCarrier to implement TextMapCarrier for Kafka headers
type kafkaHeaderCarrier struct {
	headers *[]kafka.Header
}

func (c *kafkaHeaderCarrier) Get(key string) string {
	for _, h := range *c.headers {
		if h.Key == key {
			return string(h.Value)
		}
	}
	return ""
}

func (c *kafkaHeaderCarrier) Set(key string, value string) {
	*c.headers = append(*c.headers, kafka.Header{
		Key:   key,
		Value: []byte(value),
	})
}

func (c *kafkaHeaderCarrier) Keys() []string {
	keys := make([]string, len(*c.headers))
	for i, h := range *c.headers {
		keys[i] = h.Key
	}
	return keys
}

func main() {
	log.Println("Starting Service B...")

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

	tracer = otel.Tracer("service-b")
	meter = otel.Meter("service-b")

	messageCounter, err = meter.Int64Counter(
		"service_b_messages_total",
		metric.WithDescription("Total number of messages processed"),
		metric.WithUnit("1"),
	)
	if err != nil {
		log.Fatalf("Failed to create message counter: %v", err)
	}

	kafkaDuration, err = meter.Float64Histogram(
		"service_b_kafka_duration_seconds",
		metric.WithDescription("Duration of Kafka operations"),
		metric.WithUnit("s"),
	)
	if err != nil {
		log.Fatalf("Failed to create kafka duration histogram: %v", err)
	}

	initKafka()
	defer kafkaWriter.Close()

	r := gin.New()

	r.Use(gin.Recovery())

	r.Use(otelgin.Middleware("service-b"))

	r.Use(func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery

		c.Next()

		ctx := c.Request.Context()
		spanCtx := trace.SpanContextFromContext(ctx)

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

	r.GET("/health", healthHandler)
	r.POST("/enqueue", enqueueHandler)
	r.GET("/info", infoHandler)

	log.Println("Service B listening on :8002")
	if err := r.Run(":8002"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
