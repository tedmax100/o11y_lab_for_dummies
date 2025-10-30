FROM golang:1.25-alpine AS builder

# 安装 git (go mod download 需要)
RUN apk add --no-cache git

WORKDIR /app

# 复制所有文件
COPY . .

# 清理并重新下载依赖
RUN go mod tidy && go mod download

# 构建
RUN CGO_ENABLED=0 GOOS=linux go build -o service-b .

# 运行阶段
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/service-b .

EXPOSE 8002

CMD ["./service-b"]
