# 🌐 Triton API Usage Guide

Complete guide to using the Triton Inference Server REST API with code examples in Python and cURL.

---

## Table of Contents

- [Overview](#overview)
- [Server Management](#server-management)
- [Model Management](#model-management)
- [Inference Requests](#inference-requests)
- [Python Client Examples](#python-client-examples)
- [Batch Inference](#batch-inference)
- [Error Handling](#error-handling)

---

## Overview

Triton Inference Server exposes HTTP/REST and gRPC APIs on:
- **HTTP**: `http://localhost:8000` (REST API)
- **gRPC**: `localhost:8001` (gRPC API)
- **Metrics**: `http://localhost:8002/metrics` (Prometheus format)

This guide focuses on the **HTTP/REST API**.

---

## Server Management

### Check Server Health

**Liveness** (server is running):
```bash
curl http://localhost:8000/v2/health/live
```

**Readiness** (server is ready to infer):
```bash
curl http://localhost:8000/v2/health/ready
```

**Expected Response:**
```
200 OK
```

### Get Server Metadata

```bash
curl http://localhost:8000/v2
```

**Response:**
```json
{
  "name": "triton",
  "version": "2.38.0",
  "extensions": ["classification", "sequence", "model_repository", ...]
}
```

---

## Model Management

### List All Models

```bash
curl -X POST http://localhost:8000/v2/repository/index
```

**Response:**
```json
[
  {"name": "linear_regression_model", "version": "1", "state": "READY"},
  {"name": "resnet_model", "version": "1", "state": "READY"},
  {"name": "sentiment", "version": "1", "state": "READY"}
]
```

### Get Model Metadata

```bash
curl http://localhost:8000/v2/models/resnet_model
```

**Response:**
```json
{
  "name": "resnet_model",
  "versions": ["1"],
  "platform": "pytorch_libtorch",
  "inputs": [
    {
      "name": "input__0",
      "datatype": "FP32",
      "shape": [-1, 3, 224, 224]
    }
  ],
  "outputs": [
    {
      "name": "output__0",
      "datatype": "FP32",
      "shape": [-1, 1000]
    }
  ]
}
```

### Get Model Configuration

```bash
curl http://localhost:8000/v2/models/resnet_model/config
```

**Response:**
```json
{
  "name": "resnet_model",
  "backend": "pytorch",
  "max_batch_size": 32,
  "input": [...],
  "output": [...],
  "instance_group": [{"kind": "KIND_GPU", "count": 1}],
  "dynamic_batching": {...}
}
```

### Model Control

**Load Model:**
```bash
curl -X POST http://localhost:8000/v2/repository/models/resnet_model/load
```

**Unload Model:**
```bash
curl -X POST http://localhost:8000/v2/repository/models/resnet_model/unload
```

---

## Inference Requests

### Request Format

```json
{
  "inputs": [
    {
      "name": "input_name",
      "shape": [batch_size, ...],
      "datatype": "FP32",
      "data": [...]
    }
  ],
  "outputs": [
    {
      "name": "output_name"
    }
  ]
}
```

### Example 1: Linear Regression

**cURL:**
```bash
curl -X POST http://localhost:8000/v2/models/linear_regression_model/infer \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [{
      "name": "input__0",
      "shape": [1, 1],
      "datatype": "FP32",
      "data": [5.0]
    }]
  }'
```

**Response:**
```json
{
  "model_name": "linear_regression_model",
  "model_version": "1",
  "outputs": [
    {
      "name": "output__0",
      "datatype": "FP32",
      "shape": [1, 1],
      "data": [13.0]
    }
  ]
}
```

### Example 2: Sentiment Analysis

**cURL:**
```bash
curl -X POST http://localhost:8000/v2/models/sentiment/infer \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [{
      "name": "text",
      "shape": [1, 1],
      "datatype": "BYTES",
      "data": ["This product is amazing!"]
    }]
  }'
```

**Response:**
```json
{
  "outputs": [
    {
      "name": "label",
      "datatype": "BYTES",
      "shape": [1, 1],
      "data": ["5 stars"]
    },
    {
      "name": "score",
      "datatype": "FP32",
      "shape": [1, 1],
      "data": [0.8433]
    }
  ]
}
```

---

## Python Client Examples

### Install Client Library

```bash
pip install tritonclient[http]
```

### Example 1: Simple Inference

```python
import tritonclient.http as httpclient
import numpy as np

# Create client
client = httpclient.InferenceServerClient(url="localhost:8000")

# Check server health
if not client.is_server_ready():
    raise Exception("Server not ready")

# Prepare input
input_data = np.array([[5.0]], dtype=np.float32)
inputs = [httpclient.InferInput("input__0", input_data.shape, "FP32")]
inputs[0].set_data_from_numpy(input_data)

# Run inference
result = client.infer(model_name="linear_regression_model", inputs=inputs)

# Get output
output = result.as_numpy("output__0")
print(f"Input: {input_data[0][0]}")
print(f"Output: {output[0][0]}")
# Output: Input: 5.0, Output: 13.0
```

### Example 2: Sentiment Analysis

```python
import tritonclient.http as httpclient
import numpy as np

# Create client
client = httpclient.InferenceServerClient(url="localhost:8000")

# Prepare text input
text = "This movie was absolutely fantastic!"
text_bytes = np.array([[text.encode('utf-8')]], dtype=object)

# Create input tensor
inputs = [httpclient.InferInput("text", text_bytes.shape, "BYTES")]
inputs[0].set_data_from_numpy(text_bytes)

# Request specific outputs
outputs = [
    httpclient.InferRequestedOutput("label"),
    httpclient.InferRequestedOutput("score")
]

# Run inference
result = client.infer(model_name="sentiment", inputs=inputs, outputs=outputs)

# Parse results
label = result.as_numpy("label")[0][0].decode('utf-8')
score = result.as_numpy("score")[0][0]

print(f"Text: {text}")
print(f"Sentiment: {label}")
print(f"Confidence: {score:.2%}")
# Output: Sentiment: 5 stars, Confidence: 84.33%
```

### Example 3: Image Classification (ResNet Ensemble)

```python
import tritonclient.http as httpclient
from PIL import Image
import numpy as np

# Load image
image_path = "cat.jpg"
image = Image.open(image_path).convert("RGB")
image_array = np.array(image, dtype=np.uint8)

# Create client
client = httpclient.InferenceServerClient(url="localhost:8000")

# Prepare input
inputs = [httpclient.InferInput("input_image", image_array.shape, "UINT8")]
inputs[0].set_data_from_numpy(image_array)

# Request outputs
outputs = [
    httpclient.InferRequestedOutput("class_label"),
    httpclient.InferRequestedOutput("confidence")
]

# Run inference
result = client.infer(model_name="resnet_ensemble", inputs=inputs, outputs=outputs)

# Parse results
class_label = result.as_numpy("class_label")[0][0].decode('utf-8')
confidence = result.as_numpy("confidence")[0][0]

print(f"Prediction: {class_label}")
print(f"Confidence: {confidence:.2%}")
# Output: Prediction: tabby cat, Confidence: 78.45%
```

### Example 4: Batch Inference

```python
import tritonclient.http as httpclient
import numpy as np

# Create batch of inputs
batch_size = 4
input_batch = np.array([[1.0], [2.0], [3.0], [4.0]], dtype=np.float32)

# Create client and inputs
client = httpclient.InferenceServerClient(url="localhost:8000")
inputs = [httpclient.InferInput("input__0", input_batch.shape, "FP32")]
inputs[0].set_data_from_numpy(input_batch)

# Run batch inference
result = client.infer(model_name="linear_regression_model", inputs=inputs)

# Get batch outputs
outputs = result.as_numpy("output__0")

for i, (inp, out) in enumerate(zip(input_batch, outputs)):
    print(f"Sample {i+1}: Input={inp[0]:.1f}, Output={out[0]:.2f}")

# Output:
# Sample 1: Input=1.0, Output=3.00
# Sample 2: Input=2.0, Output=5.50
# Sample 3: Input=3.0, Output=8.00
# Sample 4: Input=4.0, Output=10.50
```

---

## Batch Inference

### Single Request with Multiple Samples

```python
import tritonclient.http as httpclient
import numpy as np

# Batch of 3 texts
texts = [
    "I love this product!",
    "This is terrible.",
    "It's okay, nothing special."
]

# Convert to numpy array
text_bytes = np.array([[t.encode('utf-8')] for t in texts], dtype=object)

# Create input
client = httpclient.InferenceServerClient(url="localhost:8000")
inputs = [httpclient.InferInput("text", text_bytes.shape, "BYTES")]
inputs[0].set_data_from_numpy(text_bytes)

# Run batch inference
result = client.infer(model_name="sentiment", inputs=inputs)

# Get batch results
labels = result.as_numpy("label")
scores = result.as_numpy("score")

for text, label, score in zip(texts, labels, scores):
    print(f"Text: {text}")
    print(f"  → {label[0].decode()}: {score[0]:.2%}\n")
```

**Output:**
```
Text: I love this product!
  → 5 stars: 92.45%

Text: This is terrible.
  → 1 star: 88.32%

Text: It's okay, nothing special.
  → 3 stars: 71.23%
```

---

## Error Handling

### Python Error Handling

```python
import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException

def safe_inference(model_name, inputs):
    try:
        client = httpclient.InferenceServerClient(url="localhost:8000")
        
        # Check server ready
        if not client.is_server_ready():
            return None, "Server not ready"
        
        # Check model exists
        if not client.is_model_ready(model_name):
            return None, f"Model {model_name} not ready"
        
        # Run inference
        result = client.infer(model_name=model_name, inputs=inputs)
        return result, None
        
    except InferenceServerException as e:
        return None, f"Inference error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

# Usage
result, error = safe_inference("sentiment", inputs)
if error:
    print(f"Error: {error}")
else:
    # Process result
    pass
```

### Common Error Responses

**Model Not Found (404):**
```json
{
  "error": "Request for unknown model: 'nonexistent_model' is not found"
}
```

**Invalid Input Shape (400):**
```json
{
  "error": "input byte size mismatch for input 'input__0' for model 'resnet_model'"
}
```

**Server Not Ready (503):**
```json
{
  "error": "Server not ready"
}
```

---

## Advanced Features

### Async Inference

```python
import tritonclient.http as httpclient
import time

client = httpclient.InferenceServerClient(url="localhost:8000")

# Start async request
async_request = client.async_infer(
    model_name="linear_regression_model",
    inputs=inputs,
    request_id="my_request_123"
)

# Do other work...
time.sleep(0.1)

# Get result when ready
result = client.get_async_result(request_id="my_request_123")
```

### Model Statistics

```bash
curl http://localhost:8000/v2/models/resnet_model/stats
```

**Response:**
```json
{
  "model_stats": [
    {
      "name": "resnet_model",
      "version": "1",
      "last_inference": 1234567890,
      "inference_count": 1523,
      "execution_count": 1523,
      "inference_stats": {
        "success": {"count": 1520, "ns": 15234567890},
        "fail": {"count": 3, "ns": 0}
      },
      "batch_stats": [...]
    }
  ]
}
```

### Server Metrics (Prometheus)

```bash
curl http://localhost:8002/metrics
```

**Key Metrics:**
- `nv_inference_request_success`: Total successful requests
- `nv_inference_request_failure`: Total failed requests
- `nv_inference_request_duration_us`: Request duration
- `nv_gpu_utilization`: GPU utilization percentage
- `nv_gpu_memory_total_bytes`: Total GPU memory

---

## Complete Python Client Class

```python
import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException
import numpy as np
from typing import Dict, Any, Optional

class TritonClient:
    """Convenient wrapper for Triton HTTP client"""
    
    def __init__(self, url: str = "localhost:8000"):
        self.url = url
        self.client = httpclient.InferenceServerClient(url=url)
    
    def is_ready(self) -> bool:
        """Check if server is ready"""
        try:
            return self.client.is_server_ready()
        except:
            return False
    
    def list_models(self) -> list:
        """List all available models"""
        return self.client.get_model_repository_index()
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model metadata"""
        return self.client.get_model_metadata(model_name)
    
    def infer(self, model_name: str, inputs: Dict[str, np.ndarray]) -> Optional[Dict[str, np.ndarray]]:
        """
        Run inference on model
        
        Args:
            model_name: Name of model
            inputs: Dictionary of {input_name: numpy_array}
        
        Returns:
            Dictionary of {output_name: numpy_array} or None on error
        """
        try:
            # Prepare inputs
            triton_inputs = []
            for name, data in inputs.items():
                inp = httpclient.InferInput(name, data.shape, self._numpy_to_triton_dtype(data.dtype))
                inp.set_data_from_numpy(data)
                triton_inputs.append(inp)
            
            # Run inference
            result = self.client.infer(model_name=model_name, inputs=triton_inputs)
            
            # Extract outputs
            outputs = {}
            for output in result.get_response()['outputs']:
                outputs[output['name']] = result.as_numpy(output['name'])
            
            return outputs
            
        except InferenceServerException as e:
            print(f"Inference error: {e}")
            return None
    
    @staticmethod
    def _numpy_to_triton_dtype(np_dtype):
        """Convert numpy dtype to Triton datatype string"""
        if np_dtype == np.float32:
            return "FP32"
        elif np_dtype == np.int64:
            return "INT64"
        elif np_dtype == np.uint8:
            return "UINT8"
        elif np_dtype == np.object_:
            return "BYTES"
        else:
            raise ValueError(f"Unsupported dtype: {np_dtype}")

# Usage
client = TritonClient()

if client.is_ready():
    result = client.infer("linear_regression_model", {"input__0": np.array([[5.0]], dtype=np.float32)})
    print(result)
```

---

## Summary

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Server health | `/v2/health/ready` | GET |
| List models | `/v2/repository/index` | POST |
| Model metadata | `/v2/models/{model}` | GET |
| Inference | `/v2/models/{model}/infer` | POST |
| Load model | `/v2/repository/models/{model}/load` | POST |
| Unload model | `/v2/repository/models/{model}/unload` | POST |
| Model stats | `/v2/models/{model}/stats` | GET |
| Server metrics | `/metrics` | GET (port 8002) |

---

## Next Steps

- **[Troubleshooting Guide](TROUBLESHOOTING.md)**
- **[Model Setup](MODEL_SETUP.md)**
- **[Triton Logging Guide](TRITON_LOGGING_GUIDE.md)**
- **[Example Notebooks](../notebooks/README.md)**
