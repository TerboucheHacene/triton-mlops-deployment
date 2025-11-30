# Configs Directory

Configuration files for Triton Inference Server and monitoring stack.

## 📁 Structure

```
configs/
├── docker-compose.yaml          # Main orchestration file
├── prometheus.yml               # Prometheus scraping config
└── grafana/
    ├── dashboards/
    │   ├── dashboard.yml        # Dashboard provider config
    │   └── triton-dashboard.json # Pre-built Triton dashboard
    └── datasources/
        └── prometheus.yml       # Prometheus datasource config
```

## 🚀 Quick Start

```bash
# Start all services (Triton + Prometheus + Grafana)
docker-compose up -d

# Or use the setup script from repository root
./scripts/setup_monitoring.sh
```

## 📊 Services

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Triton HTTP | 8000 | Inference requests | http://localhost:8000 |
| Triton gRPC | 8001 | gRPC inference | localhost:8001 |
| Triton Metrics | 8002 | Prometheus metrics | http://localhost:8002/metrics |
| Prometheus | 9090 | Metrics storage | http://localhost:9090 |
| Grafana | 3000 | Dashboards | http://localhost:3000 |

## 🔑 Credentials

**Grafana:**
- Username: `admin`
- Password: `admin`

## 📖 Documentation

See [MONITORING.md](../docs/MONITORING.md) for complete setup and usage guide.

## 🛠️ Useful Commands

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart [service_name]

# Stop all services
docker-compose down

# Stop and remove data volumes
docker-compose down -v
```

## 🔧 Configuration Details

### Prometheus

- **Scrape interval**: 15 seconds
- **Retention**: 15 days (default)
- **Storage**: Docker volume `prometheus_data`

### Grafana

- **Auto-provisioning**: Enabled (datasources + dashboards)
- **Dashboard**: Auto-loaded from `grafana/dashboards/triton-dashboard.json`
- **Storage**: Docker volume `grafana_data`

### Triton

- **Model repository**: `../model_repository` (mounted as `/models`)
- **Shared memory**: 1GB
- **GPU**: All available GPUs
- **Restart policy**: `unless-stopped`

## 🌐 Networking

All services run in a shared Docker network: `triton-network`

This allows:
- Prometheus to scrape Triton at `triton:8002`
- Grafana to query Prometheus at `prometheus:9090`
- Services to communicate by container name

## 📦 Volumes

- `prometheus_data`: Stores time-series metrics data
- `grafana_data`: Stores dashboards, users, settings

**Persist data**: Volumes survive `docker-compose down`  
**Clean restart**: Use `docker-compose down -v` to remove volumes
