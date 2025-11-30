# 🔧 Troubleshooting Guide

Common issues and solutions when deploying models with Triton Inference Server.

---

## Table of Contents

- [Server Issues](#server-issues)
- [Model Loading Problems](#model-loading-problems)
- [Inference Errors](#inference-errors)
- [Docker Issues](#docker-issues)
- [Performance Problems](#performance-problems)
- [Python Backend Issues](#python-backend-issues)
- [Client Connection Issues](#client-connection-issues)

---

## Server Issues

### Server Won't Start

**Symptom:**
```bash
docker-compose up -d
# Container exits immediately
```

**Diagnosis:**
```bash
docker logs triton-server
```

**Common Causes:**

#### 1. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yaml
ports:
  - "8080:8000"  # Use 8080 instead
```

#### 2. Model Repository Not Found

**Error:**
```
failed to load model 'resnet_model': model repository path does not exist
```

**Solution:**
```bash
# Check volume mount in docker-compose.yaml
volumes:
  - ../model_repository:/models

# Verify path exists
ls -la model_repository/
```

#### 3. GPU Not Available

**Error:**
```
failed to get CUDA device count: no CUDA-capable device is detected
```

**Solution:**
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# If fails, install nvidia-container-toolkit
# Ubuntu/Debian:
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Alternative: Use CPU-only mode
# In config.pbtxt, change:
instance_group [
  {
    kind: KIND_CPU
    count: 1
  }
]
```

---

## Model Loading Problems

### Model Not Showing as READY

**Diagnosis:**
```bash
# Check model status
curl -X POST http://localhost:8000/v2/repository/index

# Check specific model
curl http://localhost:8000/v2/models/resnet_model

# Check logs
docker logs triton-server | grep resnet_model
```

#### Error 1: Config File Not Found

**Error:**
```
failed to load 'resnet_model': config file not found
```

**Solution:**
```bash
# Verify config.pbtxt exists at model root
ls model_repository/resnet_model/config.pbtxt

# Correct structure:
model_repository/
└── resnet_model/
    ├── config.pbtxt    # ← Must be here
    └── 1/
        └── model.pt

# Wrong structure (DON'T DO THIS):
model_repository/
└── resnet_model/
    └── 1/
        ├── config.pbtxt  # ← WRONG location
        └── model.pt
```

#### Error 2: Model File Not Found

**Error:**
```
failed to load 'resnet_model': version 1 directory does not exist or is not readable
```

**Solution:**
```bash
# Check model file exists
ls -lh model_repository/resnet_model/1/model.pt

# If missing, download models
./scripts/download_models.sh

# Check file permissions
chmod 644 model_repository/resnet_model/1/model.pt
```

#### Error 3: Invalid TorchScript Model

**Error:**
```
failed to load model 'resnet_model': failed to load model from file
```

**Solution:**
```python
# Re-export model to TorchScript
import torch
import torchvision.models as models

model = models.resnet50(pretrained=True)
model.eval()

# Use torch.jit.script for nn.Module
scripted = torch.jit.script(model)
scripted.save("model_repository/resnet_model/1/model.pt")
```

#### Error 4: Input/Output Mismatch

**Error:**
```
configuration specifies 3 inputs but model provides 1 inputs
```

**Solution:**
```bash
# Check model's actual inputs/outputs
python3 << EOF
import torch
model = torch.jit.load("model_repository/resnet_model/1/model.pt")
print(model.graph)
EOF

# Update config.pbtxt to match actual model signature
```

---

## Inference Errors

### Invalid Input Shape

**Error:**
```
input byte size mismatch for input 'input__0'
```

**Diagnosis:**
```python
# Check model's expected input shape
curl http://localhost:8000/v2/models/resnet_model | jq '.inputs'

# Output:
# {
#   "name": "input__0",
#   "datatype": "FP32",
#   "shape": [-1, 3, 224, 224]
# }
```

**Solution:**
```python
import numpy as np
import tritonclient.http as httpclient

# Correct: Match expected shape
input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)

# Wrong shapes:
# input_data = np.random.rand(224, 224, 3).astype(np.float32)  # ❌ Wrong order
# input_data = np.random.rand(1, 256, 256, 3).astype(np.float32)  # ❌ Wrong size
```

### Type Mismatch Error

**Error:**
```
invalid datatype BYTES for input 'input__0', expected TYPE_FP32
```

**Solution:**
```python
# Check expected datatype
curl http://localhost:8000/v2/models/linear_regression_model | jq '.inputs[0].datatype'

# Ensure numpy array has correct dtype
input_data = np.array([[5.0]], dtype=np.float32)  # ✓ Correct

# Wrong:
# input_data = np.array([[5.0]], dtype=np.float64)  # ❌ Wrong dtype
# input_data = np.array([[5]], dtype=np.int32)  # ❌ Wrong dtype
```

### Model Not Ready

**Error:**
```
model 'resnet_model' is not ready
```

**Solution:**
```bash
# Wait for model to load (can take 30-60 seconds)
watch -n 1 'curl -s -X POST http://localhost:8000/v2/repository/index | jq'

# Or check logs
docker logs -f triton-server

# Force model reload
curl -X POST http://localhost:8000/v2/repository/models/resnet_model/unload
curl -X POST http://localhost:8000/v2/repository/models/resnet_model/load
```

---

## Docker Issues

### Shared Memory Error (Python Backend)

**Error:**
```
Shared memory region creation failed: unable to create shared memory region
```

**Explanation:** Python backend models require significant shared memory for inter-process communication.

**Solution:**
```yaml
# Edit configs/docker-compose.yaml
services:
  triton:
    shm_size: '2gb'  # Increase from default 64mb
```

**Or use Docker CLI:**
```bash
docker run --shm-size=2gb nvcr.io/nvidia/tritonserver:23.08-py3 ...
```

### Container Keeps Restarting

**Diagnosis:**
```bash
docker ps -a  # Check exit code
docker logs triton-server
```

**Common Exit Codes:**
- **Exit 137**: Out of memory (OOM killed)
- **Exit 1**: Configuration error
- **Exit 139**: Segmentation fault

**Solutions:**

**For Exit 137 (OOM):**
```yaml
# Increase memory limit
services:
  triton:
    mem_limit: 8g
    shm_size: '2gb'
```

**For Exit 1:**
```bash
# Check logs for configuration errors
docker logs triton-server | grep -i error
```

### Permission Denied Errors

**Error:**
```
failed to open model repository: permission denied
```

**Solution:**
```bash
# Fix permissions
chmod -R 755 model_repository/
chown -R $USER:$USER model_repository/

# Or run container with your UID
docker run --user $(id -u):$(id -g) ...
```

---

## Performance Problems

### Slow Inference Times

**Diagnosis:**
```python
import time
import tritonclient.http as httpclient

client = httpclient.InferenceServerClient("localhost:8000")

start = time.time()
result = client.infer("resnet_model", inputs=inputs)
print(f"Inference time: {(time.time() - start)*1000:.2f} ms")
```

**Solutions:**

#### 1. Enable Dynamic Batching

```protobuf
# In config.pbtxt
dynamic_batching {
  preferred_batch_size: [1, 4, 8, 16]
  max_queue_delay_microseconds: 100
}
```

#### 2. Use GPU Instead of CPU

```protobuf
instance_group [
  {
    kind: KIND_GPU
    count: 1
    gpus: [0]
  }
]
```

#### 3. Increase Model Instances

```protobuf
instance_group [
  {
    kind: KIND_GPU
    count: 2  # Run 2 instances in parallel
  }
]
```

### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
docker stats triton-server

# Check GPU memory
docker exec triton-server nvidia-smi
```

**Solutions:**

**Limit instance count:**
```protobuf
instance_group [
  {
    count: 1  # Reduce from 2
  }
]
```

**Unload unused models:**
```bash
curl -X POST http://localhost:8000/v2/repository/models/unused_model/unload
```

---

## Python Backend Issues

### ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution:**
```bash
# Create requirements.txt in model directory
echo "transformers==4.30.0" > model_repository/sentiment/1/requirements.txt

# Restart Triton to install dependencies
docker-compose restart
```

### Import Errors in model.py

**Error:**
```
ImportError: cannot import name 'pb_utils' from partially initialized module
```

**Solution:**
```python
# In model.py, import triton_python_backend_utils FIRST
import triton_python_backend_utils as pb_utils
import numpy as np
# ... other imports
```

### Execution Timeout

**Error:**
```
model 'sentiment' execution timed out after 30 seconds
```

**Solution:**
```python
# Optimize model.execute() method
# Move expensive operations to initialize()

class TritonPythonModel:
    def initialize(self, args):
        # Load heavy models here (once)
        self.model = load_heavy_model()
    
    def execute(self, requests):
        # Keep this fast (called for every request)
        pass
```

---

## Client Connection Issues

### Connection Refused

**Error:**
```python
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solutions:**

**1. Check Triton is running:**
```bash
docker ps | grep triton
```

**2. Verify port mapping:**
```bash
docker port triton-server
# Should show: 8000/tcp -> 0.0.0.0:8000
```

**3. Check firewall:**
```bash
sudo ufw status
sudo ufw allow 8000/tcp
```

### Timeout Errors

**Error:**
```
InferenceServerException: Deadline Exceeded
```

**Solution:**
```python
# Increase timeout
client = httpclient.InferenceServerClient(
    url="localhost:8000",
    connection_timeout=60.0,  # seconds
    network_timeout=120.0
)
```

---

## Advanced Debugging

### Enable Verbose Logging

```bash
# Edit docker-compose.yaml
command: tritonserver --model-repository=/models --log-verbose=1 --log-info=1
```

**Or:**
```bash
docker run --gpus all --rm -p8000:8000 -p8001:8001 -p8002:8002 \
  -v$(pwd)/model_repository:/models \
  nvcr.io/nvidia/tritonserver:23.08-py3 \
  tritonserver --model-repository=/models --log-verbose=1
```

### Check Model-Specific Logs

```bash
docker logs triton-server 2>&1 | grep "resnet_model"
```

### Test Model Directly

```python
# Test PyTorch model outside Triton
import torch
model = torch.jit.load("model_repository/resnet_model/1/model.pt")
model.eval()

test_input = torch.randn(1, 3, 224, 224)
output = model(test_input)
print(f"Output shape: {output.shape}")
```

---

## Diagnostic Checklist

When facing issues, check:

- [ ] Triton container is running: `docker ps`
- [ ] Server is ready: `curl http://localhost:8000/v2/health/ready`
- [ ] Models are loaded: `curl -X POST http://localhost:8000/v2/repository/index`
- [ ] Model files exist: `ls model_repository/*/1/model.*`
- [ ] Config files exist: `ls model_repository/*/config.pbtxt`
- [ ] Logs show no errors: `docker logs triton-server | grep -i error`
- [ ] Sufficient memory: `docker stats triton-server`
- [ ] GPU available (if using): `docker exec triton-server nvidia-smi`
- [ ] Ports not blocked: `telnet localhost 8000`
- [ ] Client library installed: `pip show tritonclient`

---

## Getting Help

If issues persist:

1. **Check Logs**: `docker logs triton-server > triton.log`
2. **Search GitHub Issues**: [Triton Server Issues](https://github.com/triton-inference-server/server/issues)
3. **NVIDIA Forums**: [NVIDIA Developer Forums](https://forums.developer.nvidia.com/c/ai/triton-inference-server/322)
4. **Project Issues**: [Open an issue](https://github.com/yourusername/model_deployment/issues)

Include:
- Triton version: `docker exec triton-server tritonserver --version`
- Docker version: `docker --version`
- GPU info: `nvidia-smi`
- Full logs: `docker logs triton-server`
- Model config: `cat model_repository/model_name/config.pbtxt`

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Server won't start | `docker logs triton-server` |
| Model not loading | Check `config.pbtxt` location and model file exists |
| Shared memory error | Add `shm_size: '2gb'` to docker-compose |
| Connection refused | Check `docker ps` and port mappings |
| Slow inference | Enable dynamic batching in config.pbtxt |
| Import errors | Add `requirements.txt` to model directory |
| Shape mismatch | Check model metadata: `/v2/models/{model}` |
| Timeout | Increase client timeout or optimize model |

---

## Next Steps

- **[Triton Logging Guide](TRITON_LOGGING_GUIDE.md)** - Comprehensive logging reference
- **[API Guide](API_GUIDE.md)** - API usage examples
- **[Model Setup](MODEL_SETUP.md)** - Model download and configuration
- **[Main README](../README.md)** - Project overview
