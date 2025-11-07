# 截图添加指南

本指南将帮助你为教程添加实际的截图，以替换当前的占位符图片。

## 需要的截图清单

### 1. Grafana 主页 (grafana-home.png)

**何时截图**: 完成 "访问 Grafana 平台" 步骤后

**操作步骤**:
1. 启动所有服务: `docker compose up -d`
2. 访问 http://localhost:3000
3. 使用 admin/admin 登录
4. 在主页截图，包含左侧菜单栏和主面板

**截图要点**:
- 显示完整的 Grafana 界面
- 确保左侧菜单清晰可见
- 包含顶部导航栏

---

### 2. 数据源配置 (grafana-datasources.png)

**何时截图**: 在 Grafana 主页登录后

**操作步骤**:
1. 点击左侧齿轮图标 (Configuration)
2. 选择 "Data sources"
3. 截图显示已配置的数据源列表

**截图要点**:
- 显示 Prometheus、Loki、Tempo 三个数据源
- 每个数据源应显示为 "working" 状态
- 包含数据源类型和名称

---

### 3. Dashboard 列表 (grafana-dashboards.png)

**何时截图**: 查看预配置的 Dashboard

**操作步骤**:
1. 点击左侧 Dashboard 图标
2. 显示所有可用的 Dashboard
3. 截图

**截图要点**:
- 显示预配置的 Dashboard 列表
- 包含 Dashboard 名称和标签

---

### 4. K6 流量图表 (k6-traffic.png)

**何时截图**: K6 测试运行期间

**操作步骤**:
1. 运行 K6 测试:
   ```bash
   k6 run k6/load-test.js
   ```
2. 在 Grafana Explore 中:
   - 选择 Prometheus 数据源
   - 查询: `rate(http_requests_total[1m])`
   - 点击 "Run query"
3. 等待数据显示后截图

**截图要点**:
- 显示请求速率的时间序列图表
- 图表应显示明显的流量增长
- 包含查询语句和时间范围选择器

---

### 5. Pumba 延迟效果 (pumba-delay.png)

**何时截图**: 注入延迟并观察影响

**操作步骤**:
1. 启动 K6 持续流量:
   ```bash
   k6 run --duration 5m k6/load-test.js &
   ```
2. 注入延迟:
   ```bash
   pumba netem --duration 2m delay --time 500 o11y_lab_for_dummies-service-a-1
   ```
3. 在 Grafana 中查询 P95 延迟:
   ```promql
   histogram_quantile(0.95,
     rate(http_server_duration_milliseconds_bucket[1m])
   )
   ```
4. 截图显示延迟注入前后的变化

**截图要点**:
- 图表应显示明显的延迟增加（从 ~100ms 到 ~600ms）
- 包含时间范围，显示注入前后的对比
- 标注出延迟注入的时间点

---

### 6. 自动埋点 Trace (auto-trace.png)

**何时截图**: 查看自动生成的 Trace

**操作步骤**:
1. 触发请求:
   ```bash
   curl http://localhost:8080/api/process
   ```
2. 在 Grafana Explore 中:
   - 选择 Tempo 数据源
   - 选择 Service: service-a
   - 点击 "Run query"
3. 点击任意 trace 查看详情
4. 截图显示 span 树状结构

**截图要点**:
- 显示完整的 trace waterfall 视图
- 清晰显示自动生成的 spans（HTTP、数据库等）
- 包含 span 的时间和属性信息

---

### 7. 手动埋点 Trace (manual-trace.png)

**何时截图**: 查看包含手动埋点的 Trace

**操作步骤**:
1. 触发请求到 service-d
2. 在 Tempo 中搜索 service-d 的 traces
3. 找到包含自定义 span 的 trace（如 "business_logic"）
4. 截图显示自定义的 span 和属性

**截图要点**:
- 显示自定义的 span 名称（如 business_logic）
- 展开 span 显示自定义属性（user.id, request.size 等）
- 显示 span events（如 "Processing started"）

---

### 8. 关联 Dashboard (correlated-dashboard.png)

**何时截图**: 展示 Logs/Traces/Metrics 的关联

**操作步骤**:
1. 创建或打开一个包含三者的 dashboard
2. 或者在 Explore 中使用分屏显示：
   - 上方: Prometheus metrics
   - 中间: Tempo traces
   - 下方: Loki logs
3. 确保显示相同时间范围的数据
4. 截图

**截图要点**:
- 同时显示 metrics、traces、logs
- 显示它们之间的关联（通过 trace_id）
- 展示如何从一个跳转到另一个

---

## 截图工具推荐

### Linux
- **Flameshot**: `sudo apt install flameshot`
- **GNOME Screenshot**: 系统自带
- **Spectacle** (KDE): `sudo apt install spectacle`

### MacOS
- **系统截图**: Cmd + Shift + 4
- **CleanShot X**: 付费但功能强大

### Windows
- **Snipping Tool**: 系统自带
- **Greenshot**: 免费开源
- **ShareX**: 功能丰富

## 截图最佳实践

1. **分辨率**: 至少 1920x1080，保证清晰度
2. **格式**: PNG 格式，保证质量
3. **内容**:
   - 去除个人敏感信息
   - 确保界面完整，不要裁剪关键部分
   - 包含必要的上下文（如 URL、时间等）
4. **文件大小**:
   - 尽量控制在 500KB 以内
   - 可使用 `optipng` 或 `pngquant` 压缩
5. **命名**: 使用上述指定的文件名

## 添加截图到教程

### 方法 1: 添加到源文件（推荐）

1. 将截图保存到:
   ```
   codelabs/tutorials/assets/images/
   ```

2. 重新生成 HTML:
   ```bash
   cd codelabs
   ./claat export -o generated tutorials/observability-lab.md
   ```

### 方法 2: 直接添加到生成的教程

1. 将截图保存到:
   ```
   codelabs/generated/o11y-lab-tutorial/img/
   ```

2. 文件会直接显示在教程中

## 优化截图

### 压缩 PNG

```bash
# 安装 optipng
sudo apt install optipng

# 压缩单个文件
optipng -o7 image.png

# 批量压缩
find codelabs/tutorials/assets/images/ -name "*.png" -exec optipng -o7 {} \;
```

### 调整尺寸

```bash
# 安装 ImageMagick
sudo apt install imagemagick

# 调整宽度为 1200px（保持比例）
convert input.png -resize 1200x output.png

# 批量调整
for img in *.png; do
  convert "$img" -resize 1200x "resized_$img"
done
```

## 示例工作流

```bash
# 1. 截取所有需要的图片
# 2. 保存到 tutorials/assets/images/
cd codelabs

# 3. 优化图片
optipng -o7 tutorials/assets/images/*.png

# 4. 重新生成教程
./claat export -o generated tutorials/observability-lab.md

# 5. 启动服务器预览
./serve.sh

# 6. 在浏览器中检查 http://localhost:8000
```

## 故障排查

### 图片不显示

检查：
1. 文件名是否完全匹配（区分大小写）
2. 文件格式是否为 PNG
3. 路径是否正确
4. 重新生成 HTML 后是否刷新了浏览器缓存

### 图片太大

```bash
# 查看文件大小
ls -lh codelabs/tutorials/assets/images/

# 如果超过 1MB，进行压缩
pngquant --quality=65-80 image.png -o image.png
```

## 完成检查清单

- [ ] grafana-home.png - Grafana 主页
- [ ] grafana-datasources.png - 数据源配置
- [ ] grafana-dashboards.png - Dashboard 列表
- [ ] k6-traffic.png - K6 流量图表
- [ ] pumba-delay.png - 延迟注入效果
- [ ] auto-trace.png - 自动埋点 Trace
- [ ] manual-trace.png - 手动埋点 Trace
- [ ] correlated-dashboard.png - 关联 Dashboard
- [ ] 所有图片已优化压缩
- [ ] 重新生成 HTML
- [ ] 本地预览确认无误

完成后，你的教程将拥有完整的视觉指导！
