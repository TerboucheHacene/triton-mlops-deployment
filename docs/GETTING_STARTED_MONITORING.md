# Getting Started with Monitoring

Quick guide to get Prometheus + Grafana monitoring up and running.

## Prerequisites

- ✅ Docker and Docker Compose installed
- ✅ Triton model repository set up
- ✅ Ports available: 3000, 8000, 8001, 8002, 9090

## 🚀 Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./scripts/setup_monitoring.sh

# Wait about 30 seconds for all services to start
# Then open Grafana: http://localhost:3000
```

## 🛠️ Option 2: Manual Setup

### Step 1: Start Services

```bash
cd configs/
docker-compose up -d
```

### Step 2: Wait for Startup

```bash
# Wait 30 seconds for services to initialize
sleep 30

# Check status
docker-compose ps
```

Expected output:
```
NAME              STATUS
grafana           Up
prometheus        Up
triton_server     Up
```

### Step 3: Verify Health

```bash
# From repository root
./scripts/check_monitoring.sh
```

Expected output:
```
✅ Triton HTTP API is UP
✅ Triton Metrics is UP
✅ Prometheus is UP
✅ Grafana is UP
✅ Prometheus can reach Triton
✅ Triton is exposing 200+ metrics
```

### Step 4: Access Grafana

1. Open: **http://localhost:3000**
2. Login:
   - Username: `admin`
   - Password: `admin`
3. (Optional) Skip or set new password
4. Go to **Dashboards** → **Triton Inference Server Metrics**

## 📊 Generate Load to See Metrics

```bash
# Run load test
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s \
  --headless

# Watch the dashboard update in real-time!
```

You should see:
- Request rate increasing
- Batch size forming (3-8 requests/batch)
- GPU utilization rising
- Latency metrics populating

## 🔍 Explore

### Prometheus UI

http://localhost:9090

Try queries:
```promql
# Request rate
rate(nv_inference_request_success[1m])

# Batch size
rate(nv_inference_request_success[1m]) / rate(nv_inference_exec_count[1m])

# GPU utilization
nv_gpu_utilization
```

### Grafana Dashboard

http://localhost:3000/d/triton-metrics

Features:
- 12 pre-configured panels
- Real-time updates (5s refresh)
- Interactive time range
- Zoom and filtering

## 🛑 Stop Services

```bash
cd configs/
docker-compose down

# Or keep data and stop
docker-compose stop
```

## 🔄 Restart Services

```bash
cd configs/
docker-compose restart

# Or restart specific service
docker-compose restart triton
```

## 📚 Next Steps

1. **Customize Dashboard**: Add your own panels in Grafana
2. **Set Up Alerts**: Configure Prometheus alerting (see [MONITORING.md](../docs/MONITORING.md))
3. **Tune Settings**: Adjust scrape intervals, retention periods
4. **Production Deploy**: Set strong passwords, enable HTTPS

## 🆘 Troubleshooting

### Prometheus shows "Target Down"

```bash
# Check Triton is running
docker ps | grep triton

# Check metrics endpoint
curl http://localhost:8002/metrics

# Check docker network
docker network ls | grep triton
```

### Grafana shows "No Data"

```bash
# Wait 30 seconds after startup
sleep 30

# Generate some load
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000

# Refresh Grafana dashboard
```

### Can't Access Grafana

```bash
# Check if container is running
docker ps | grep grafana

# Check logs
docker logs grafana

# Restart Grafana
docker restart grafana
```

## 📖 Full Documentation

See [MONITORING.md](../docs/MONITORING.md) for:
- Complete configuration guide
- Custom queries and panels
- Alert setup
- Advanced troubleshooting
- Production best practices

---

**Ready to monitor! 🚀**
