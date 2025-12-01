# 📋 Triton Server Logging with Loki & Grafana

Complete guide for viewing and analyzing Triton Inference Server logs in Grafana using Loki.

---

## 🏗️ Architecture

```
┌─────────────────┐
│ Triton Server   │
│ (Container Logs)│
└────────┬────────┘
         │ stdout/stderr
         ▼
┌─────────────────┐
│    Promtail     │ ◄─── Scrapes Docker logs
│ (Log Collector) │
└────────┬────────┘
         │ Push logs
         ▼
┌─────────────────┐
│      Loki       │ ◄─── Stores & indexes logs
│ (Log Storage)   │
└────────┬────────┘
         │ Query logs
         ▼
┌─────────────────┐
│    Grafana      │ ◄─── Visualize logs + metrics
│ (Visualization) │
└─────────────────┘
```

---

## 🚀 Quick Start

### 1. Start All Services

```bash
cd configs/
docker-compose up -d
```

This starts:
- **Triton Server** (ports 8000, 8001, 8002)
- **Prometheus** (port 9090) - Metrics
- **Loki** (port 3100) - Log storage
- **Promtail** (port 9080) - Log collector
- **Grafana** (port 3000) - Visualization

### 2. Access Grafana

Open http://localhost:3000
- **Username**: `admin`
- **Password**: `admin`

### 3. View Logs Dashboard

Navigate to: **Dashboards** → **Triton Inference Server Logs**

---

## 📊 Dashboard Panels

### 1. **Triton Server Logs - All Levels**
- Shows all logs from Triton container
- Real-time streaming
- Filterable by search

### 2. **Error Logs Only**
- Filters for ERROR and FATAL messages
- Red highlight for quick identification
- Shows full log context

### 3. **Warning Logs**
- Shows WARN level messages
- Helps identify potential issues

### 4. **Error Count (Last 5m)**
- Stat panel showing error count
- Color-coded:
  - Green: 0 errors
  - Yellow: 1-9 errors
  - Red: 10+ errors

### 5. **Warning Count (Last 5m)**
- Stat panel for warnings
- Threshold-based coloring

### 6. **Log Levels Distribution**
- Bar chart showing log volume by level
- Helps understand log patterns

### 7. **Model-Specific Logs**
- Filters logs mentioning models
- Useful for debugging model issues

### 8. **Log Rate by Level**
- Time series showing logs/second
- Tracks logging activity over time

---

## 🔍 Querying Logs (LogQL)

### Basic Queries

**All Triton logs:**
```logql
{container="triton_server"}
```

**Error logs only:**
```logql
{container="triton_server"} |~ "ERROR|FATAL"
```

**Warning logs:**
```logql
{container="triton_server"} |~ "WARN"
```

**Logs containing specific model:**
```logql
{container="triton_server"} |~ "resnet_model"
```

**Logs with specific text:**
```logql
{container="triton_server"} |= "batch"
```

### Advanced Queries

**Count errors in last hour:**
```logql
sum(count_over_time({container="triton_server"} |~ "ERROR" [1h]))
```

**Logs between timestamps:**
```logql
{container="triton_server"} | json | timestamp > "2025-12-01 10:00:00"
```

**Exclude INFO logs:**
```logql
{container="triton_server"} != "INFO"
```

**Pattern extraction:**
```logql
{container="triton_server"} | regexp "model='(?P<model_name>\\w+)'"
```

---

## ⚙️ Configuration Files

### Loki Config (`loki-config.yaml`)
- **Retention**: Logs kept for 7 days (168h)
- **Storage**: Local filesystem at `/tmp/loki`
- **Indexing**: TSDB schema with 24h periods
- **Compaction**: Runs every 10 minutes

### Promtail Config (`promtail-config.yaml`)
- **Target**: Scrapes all Docker containers
- **Special handling** for `triton_server` container
- **Label extraction**: 
  - `container` - Container name
  - `level` - Log level (INFO/WARN/ERROR)
  - `service` - Service name
  - `model_name` - Extracted from logs

### Docker Compose Updates
- Added `loki` service (port 3100)
- Added `promtail` service with Docker socket access
- Updated `grafana` to depend on Loki
- Added `loki_data` volume for persistence

---

## 🎯 Common Use Cases

### 1. Debugging Model Loading Issues
**Query:**
```logql
{container="triton_server"} |~ "model" |~ "ERROR|WARN"
```

### 2. Tracking Request Failures
**Query:**
```logql
{container="triton_server"} |~ "request|inference" |~ "fail|error"
```

### 3. Monitoring Startup Sequence
**Query:**
```logql
{container="triton_server"} |~ "Starting|Loading|Ready"
```

### 4. GPU-Related Issues
**Query:**
```logql
{container="triton_server"} |~ "GPU|CUDA|cuda"
```

### 5. Performance Debugging
**Query:**
```logql
{container="triton_server"} |~ "batch|queue|latency"
```

---

## 🔧 Combining Logs & Metrics

### Example: Correlate Errors with Latency Spikes

1. Open the **Triton Metrics** dashboard
2. Notice high P95 latency at 10:30 AM
3. Open **Triton Logs** dashboard
4. Set time range to 10:25-10:35 AM
5. Check error logs for root cause

### Split View Setup
1. Add a new panel
2. Set to "Logs" visualization
3. Set datasource to "Loki"
4. Add metric panel below for comparison

---

## 🚨 Alerting on Logs

### Create Alert for Error Spikes

1. Go to **Alerting** → **Alert Rules**
2. Click **New Alert Rule**
3. Set query:
   ```logql
   sum(rate({container="triton_server"} |~ "ERROR" [5m])) > 1
   ```
4. Set threshold: Alert if > 1 error/sec
5. Configure notification channel

### Example Alert Conditions
- **Critical**: > 10 errors in 1 minute
- **Warning**: > 5 warnings in 5 minutes
- **Info**: Model restart detected

---

## 📈 Performance Considerations

### Log Volume
- **Typical**: 100-500 logs/min (idle)
- **Under load**: 1,000-5,000 logs/min
- **With verbose logging**: 10,000+ logs/min

### Retention Settings
Current: **7 days** (168h)

To change retention, edit `configs/loki-config.yaml`:
```yaml
limits_config:
  retention_period: 336h  # 14 days
```

### Storage Usage
- **Typical**: ~100MB per day
- **Verbose**: ~500MB per day
- Located at: `/tmp/loki` (in container)

---

## 🐛 Troubleshooting

### Logs Not Appearing

**Check Promtail status:**
```bash
docker logs promtail
```

**Check Loki connectivity:**
```bash
curl http://localhost:3100/ready
```

**Verify Triton is logging:**
```bash
docker logs triton_server
```

### Loki Storage Full

**Check disk usage:**
```bash
docker exec loki du -sh /tmp/loki
```

**Clear old data:**
```bash
docker-compose down
docker volume rm configs_loki_data
docker-compose up -d
```

### Slow Query Performance

**Reduce time range** in Grafana (e.g., last 15m instead of 24h)

**Use specific filters** instead of broad searches:
- Good: `{container="triton_server"} |= "ERROR"`
- Slow: `{container="triton_server"} |~ ".*"`

### Missing Log Levels

Check Promtail regex patterns in `promtail-config.yaml`. Triton uses formats like:
- `I1201 10:30:45.123456` (INFO)
- `W1201 10:30:45.123456` (WARN)
- `E1201 10:30:45.123456` (ERROR)

---

## 🔐 Security Considerations

### Production Setup

1. **Change Grafana password** (default: admin/admin)
2. **Restrict Loki access** (not exposed publicly)
3. **Enable authentication** on Loki if needed
4. **Use HTTPS** for Grafana
5. **Implement log sanitization** (remove sensitive data)

### Log Sanitization

Add to `promtail-config.yaml`:
```yaml
pipeline_stages:
  - replace:
      expression: '(password|token|key)=\S+'
      replace: '$1=***REDACTED***'
```

---

## 📚 Additional Resources

- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Triton Logging Guide](./TRITON_LOGGING_GUIDE.md)

---

## 🎓 Learning LogQL

### Basic Operators
- `|=` - Contains string
- `!=` - Does not contain
- `|~` - Regex match
- `!~` - Regex not match

### Examples
```logql
# Contains "batch"
{container="triton_server"} |= "batch"

# Regex for model names
{container="triton_server"} |~ "model='[a-z_]+'"

# Exclude INFO
{container="triton_server"} != "INFO"

# Multiple filters
{container="triton_server"} |= "ERROR" |~ "resnet"
```

---

## ✅ Verification Checklist

- [ ] All services running (`docker-compose ps`)
- [ ] Loki accessible (http://localhost:3100/ready)
- [ ] Promtail collecting logs (`docker logs promtail`)
- [ ] Grafana shows Loki datasource (green)
- [ ] Logs dashboard loads
- [ ] Logs appearing in real-time
- [ ] Error counts updating
- [ ] Time range selector working

---

## 🎯 Next Steps

1. **Generate load** to see logs in action:
   ```bash
   python -m locust -f tests/locustfile_resnet.py \
     --host=http://localhost:8000 --users 10 --run-time 60s
   ```

2. **Create custom log queries** for your models

3. **Set up alerts** for critical errors

4. **Export dashboards** for version control

5. **Integrate with other services** (e.g., Alertmanager, PagerDuty)
