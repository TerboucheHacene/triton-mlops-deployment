# Real-Time Monitoring with Prometheus & Grafana

Complete guide for setting up production-grade real-time monitoring for Triton Inference Server.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Using the Dashboard](#using-the-dashboard)
- [Custom Queries](#custom-queries)
- [Alerts (Optional)](#alerts-optional)
- [Troubleshooting](#troubleshooting)

---

## Overview

This monitoring stack provides **real-time visibility** into your Triton Inference Server's performance:

- **Prometheus**: Collects and stores metrics from Triton every 15 seconds
- **Grafana**: Visualizes metrics with interactive dashboards
- **Triton**: Exposes Prometheus-format metrics on port 8002

### Key Metrics Tracked

✅ **Request Rate** - Requests per second (success/failure)  
✅ **Batch Size** - Average requests per GPU execution  
✅ **Latency** - P50/P95 response times  
✅ **GPU Utilization** - GPU usage percentage  
✅ **GPU Memory** - Memory consumption  
✅ **Queue Time** - Batching delay  
✅ **Compute Time** - Model inference duration  
✅ **Batching Efficiency** - GPU call reduction percentage  

---

## Architecture

```
┌─────────────────┐
│  Triton Server  │  Exposes metrics on :8002/metrics
│   (port 8000)   │
└────────┬────────┘
         │
         │ scrapes every 15s
         ↓
┌─────────────────┐
│   Prometheus    │  Stores time-series data
│   (port 9090)   │
└────────┬────────┘
         │
         │ queries
         ↓
┌─────────────────┐
│    Grafana      │  Visualizes dashboards
│   (port 3000)   │
└─────────────────┘
         │
         │ view in browser
         ↓
┌─────────────────┐
│   Your Browser  │
└─────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Triton Server repository set up
- Ports 3000, 8000, 8002, 9090 available

### One-Command Setup

```bash
# Run the setup script
./scripts/setup_monitoring.sh
```

This script will:
1. Stop any existing services
2. Start Triton, Prometheus, and Grafana
3. Wait for services to be ready
4. Display access URLs and credentials

### Manual Setup

```bash
# Navigate to configs directory
cd configs/

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f grafana
```

---

## Configuration

### Prometheus Configuration

File: `configs/prometheus.yml`

```yaml
global:
  scrape_interval: 15s      # How often to collect metrics
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'triton'
    static_configs:
      - targets: ['triton:8002']  # Triton metrics endpoint
```

**Tuning:**
- Decrease `scrape_interval` to `5s` for higher resolution (more disk usage)
- Increase to `30s` or `1m` for lower resolution (less disk usage)

### Grafana Configuration

Files:
- `configs/grafana/datasources/prometheus.yml` - Connects Grafana to Prometheus
- `configs/grafana/dashboards/dashboard.yml` - Auto-loads dashboards
- `configs/grafana/dashboards/triton-dashboard.json` - Main dashboard definition

**Dashboard Auto-Loading:**
Dashboards are automatically loaded from JSON files on startup. No manual import needed!

---

## Using the Dashboard

### Access Grafana

1. Open browser: **http://localhost:3000**
2. Login:
   - Username: `admin`
   - Password: `admin`
3. Skip password change (or set a new one)
4. Navigate to **Dashboards** → **Triton Inference Server Metrics**

### Dashboard Panels

#### 1. **Request Rate** (Top Left)
- Shows successful and failed requests per second
- Green = success, Red = failures
- **Good**: Steady rate, no failures
- **Bad**: Many failures or erratic pattern

#### 2. **Average Batch Size** (Top Right)
- Shows how many requests are batched together
- **Good**: > 2.0 (batching is working)
- **Bad**: ≈ 1.0 (no batching, increase load or queue delay)

#### 3. **Request Duration P50/P95** (Middle Left)
- P50 = median response time
- P95 = 95% of requests faster than this
- **Good**: P50 < 100ms, P95 < 500ms
- **Warning**: P95 > 2000ms

#### 4. **GPU Utilization** (Middle Right - Gauge)
- Current GPU usage percentage
- **Green**: 0-50% (underutilized)
- **Yellow**: 50-80% (good)
- **Red**: 80-100% (at capacity)

#### 5. **GPU Memory Usage** (Bottom Left)
- Percentage of GPU memory used
- Watch for memory leaks (continuously increasing)

#### 6. **Queue Time** (Bottom Middle)
- Average time requests wait for batching
- Higher with longer `max_queue_delay`
- Trade-off: higher queue = more batching but higher latency

#### 7. **Statistics Panels** (Bottom)
- Total successful/failed requests
- Total GPU executions
- **Batching Efficiency** = (1 - executions/requests) × 100%
  - **Good**: > 50%
  - **Great**: > 70%

#### 8. **Compute Time** (Bottom)
- Actual inference time per model
- Helps identify slow models

#### 9. **Model Summary Table**
- Lists all models with their total requests/executions
- Sortable by any column

### Dashboard Controls

**Time Range** (top right):
- Last 15 minutes (default)
- Last 1 hour
- Last 6 hours
- Custom range

**Auto-Refresh** (top right):
- 5s (default - good for active monitoring)
- 10s, 30s, 1m (lighter load)
- Off (manual refresh)

**Zoom**: Click and drag on any graph to zoom into that time range

---

## Custom Queries

### Prometheus UI

Access: **http://localhost:9090**

Try these queries in the **Graph** tab:

#### Request Rate Per Model
```promql
rate(nv_inference_request_success{job="triton"}[1m])
```

#### Average Batch Size
```promql
rate(nv_inference_request_success{job="triton"}[1m]) / rate(nv_inference_exec_count{job="triton"}[1m])
```

#### P95 Latency (milliseconds)
```promql
histogram_quantile(0.95, rate(nv_inference_request_duration_us_bucket{job="triton"}[1m])) / 1000
```

#### GPU Memory Percentage
```promql
nv_gpu_memory_used_bytes{job="triton"} / nv_gpu_memory_total_bytes{job="triton"} * 100
```

#### Batching Efficiency
```promql
(1 - sum(nv_inference_exec_count{job="triton"}) / sum(nv_inference_request_success{job="triton"})) * 100
```

#### Requests by Model (Table)
```promql
nv_inference_request_success{job="triton"}
```

### Creating Custom Panels in Grafana

1. Click **Add panel** button
2. Select **Prometheus** as data source
3. Enter your PromQL query
4. Choose visualization:
   - **Graph** - Time series line chart
   - **Gauge** - Single current value with thresholds
   - **Stat** - Large number display
   - **Table** - Tabular data
   - **Heatmap** - Distribution over time
5. Configure display options (colors, thresholds, legends)
6. Click **Apply** to add to dashboard
7. Click **Save** (disk icon) to save dashboard

---

## Alerts (Optional)

Set up alerts to notify you of issues automatically.

### Create Alert Rules File

Create `configs/prometheus-alerts.yml`:

```yaml
groups:
  - name: triton_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(nv_inference_request_failure{job="triton"}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.model }}"
          description: "Error rate is {{ $value | humanize }} req/s"

      - alert: HighGPUUtilization
        expr: nv_gpu_utilization{job="triton"} > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU utilization very high"
          description: "GPU {{ $labels.gpu_uuid }} at {{ $value }}%"

      - alert: TritonDown
        expr: up{job="triton"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Triton Server is down"
          description: "Cannot reach Triton metrics endpoint"

      - alert: LowBatchingEfficiency
        expr: (1 - sum(nv_inference_exec_count{job="triton"}) / sum(nv_inference_request_success{job="triton"})) * 100 < 30
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "Low batching efficiency"
          description: "Only {{ $value | humanize1024 }}% batching efficiency"
```

### Update Prometheus Config

Update `configs/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Add this:
rule_files:
  - /etc/prometheus/prometheus-alerts.yml

scrape_configs:
  - job_name: 'triton'
    static_configs:
      - targets: ['triton:8002']
        labels:
          service: 'triton-inference-server'
```

### Update Docker Compose

Update `configs/docker-compose.yaml` prometheus volumes:

```yaml
prometheus:
  # ... existing config ...
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./prometheus-alerts.yml:/etc/prometheus/prometheus-alerts.yml:ro
    - prometheus_data:/prometheus
```

### Restart Prometheus

```bash
cd configs/
docker-compose restart prometheus
```

### View Alerts

- Prometheus: http://localhost:9090/alerts
- Grafana: Add an **Alert list** panel to your dashboard

---

## Troubleshooting

### Issue: "Prometheus shows target is DOWN"

**Check Triton is running:**
```bash
docker ps | grep triton_server
curl http://localhost:8002/metrics
```

**Check Docker network:**
```bash
docker network inspect configs_triton-network
```

**Check Prometheus logs:**
```bash
docker-compose -f configs/docker-compose.yaml logs prometheus
```

**Solution:**
```bash
# Restart all services
cd configs/
docker-compose restart
```

---

### Issue: "Grafana shows 'No Data'"

**Verify Prometheus datasource:**
1. In Grafana: **Configuration** → **Data Sources** → **Prometheus**
2. Click **Test** button
3. Should show "Data source is working"

**Check Prometheus has data:**
```bash
curl 'http://localhost:9090/api/v1/query?query=up{job="triton"}'
```

**Solution:**
```bash
# Check if Triton is actually sending metrics
curl http://localhost:8002/metrics | grep nv_inference

# Restart Grafana
docker-compose restart grafana
```

---

### Issue: "Dashboard not auto-loading"

**Check Grafana provisioning logs:**
```bash
docker-compose logs grafana | grep provisioning
```

**Manual import:**
1. In Grafana: **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `configs/grafana/dashboards/triton-dashboard.json`
4. Click **Import**

---

### Issue: "Can't login to Grafana"

**Default credentials:**
- Username: `admin`
- Password: `admin`

**Reset if needed:**
```bash
# Reset Grafana (deletes all custom configs)
docker-compose down
docker volume rm configs_grafana_data
docker-compose up -d grafana
```

---

### Issue: "Prometheus consuming too much disk space"

**Check disk usage:**
```bash
docker exec prometheus du -sh /prometheus
```

**Reduce retention:**

Update `configs/docker-compose.yaml` prometheus command:

```yaml
prometheus:
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=7d'  # Keep only 7 days (default: 15d)
```

**Clean up old data:**
```bash
docker-compose down
docker volume rm configs_prometheus_data
docker-compose up -d
```

---

## Workflow Examples

### Scenario 1: Performance Testing

```bash
# 1. Start monitoring
./scripts/setup_monitoring.sh

# 2. Open Grafana dashboard
# http://localhost:3000

# 3. Run load test
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 20 \
  --spawn-rate 5 \
  --run-time 120s \
  --headless

# 4. Watch metrics in real-time:
# - Request rate increasing
# - Batch size forming (should be 3-8)
# - GPU utilization rising
# - Response times stabilizing

# 5. After test, check:
# - Total requests (should be ~2400 for 120s @ 20 RPS)
# - Failure rate (should be 0%)
# - Batching efficiency (should be > 50%)
```

### Scenario 2: Tuning Batching

```bash
# 1. Run load test and observe metrics

# 2. If batch size is low (< 2):
# Edit model_repository/resnet_model/config.pbtxt
# Increase: max_queue_delay_microseconds: 200000

# 3. Restart Triton
docker-compose restart triton

# 4. Wait for models to reload (~30s)

# 5. Run load test again

# 6. Check if batch size improved in Grafana
```

### Scenario 3: Production Monitoring

```bash
# Set up monitoring with alerts
./scripts/setup_monitoring.sh

# Keep dashboard open on separate monitor
# http://localhost:3000/d/triton-metrics

# Monitor:
# - Request rate (should be steady)
# - Error rate (should be near 0)
# - GPU utilization (should be 40-80%)
# - Latency P95 (should be < 1000ms)

# Set up alerts for critical issues
# See "Alerts" section above
```

---

## Best Practices

### 1. **Dashboard Organization**

- Keep default dashboard as-is (easy reference)
- Create custom dashboards for specific needs:
  - One per model
  - One for alerting
  - One for capacity planning

### 2. **Metric Retention**

- **Development**: 1-3 days retention
- **Staging**: 7 days retention
- **Production**: 15-30 days retention

### 3. **Regular Monitoring**

- Check dashboard daily in production
- Set up alerts for critical metrics
- Review trends weekly (capacity planning)

### 4. **Performance Testing**

- Always have Grafana open during load tests
- Compare before/after config changes
- Document optimal settings

---

## Advanced: Distributed Monitoring

For production environments with multiple Triton instances:

### Multi-Target Prometheus

Update `configs/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'triton-prod'
    static_configs:
      - targets:
          - 'triton-1:8002'
          - 'triton-2:8002'
          - 'triton-3:8002'
        labels:
          environment: 'production'
```

Grafana will automatically aggregate metrics across all instances.

---

## Summary

✅ **Setup**: `./scripts/setup_monitoring.sh`  
✅ **Access**: http://localhost:3000 (admin/admin)  
✅ **Dashboard**: Triton Inference Server Metrics  
✅ **Verify**: Run load test and watch metrics update  
✅ **Customize**: Add panels, create alerts, tune retention  

---

## Next Steps

- **[Load Testing Guide](LOAD_TESTING_AND_BATCHING.md)** - Generate load to see metrics
- **[API Guide](API_GUIDE.md)** - Understand Triton endpoints
- **[Troubleshooting](TROUBLESHOOTING.md)** - Fix common issues

---

**Happy Monitoring! 📊**
