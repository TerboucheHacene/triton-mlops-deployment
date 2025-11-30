# 📦 Model Setup Guide

This guide explains how to download, configure, and deploy models for Triton Inference Server.

---

## Table of Contents

- [Overview](#overview)
- [Model Download Options](#model-download-options)
- [Manual Model Setup](#manual-model-setup)
- [Model Configuration](#model-configuration)
- [Verifying Models](#verifying-models)
- [Troubleshooting](#troubleshooting)

---

## Overview

Models are **not included** in this repository because they are too large for Git (355+ MB total). You must download or train them separately.

**Why models aren't in Git:**
- ResNet50: ~99 MB
- BERT Classifier: ~256 MB  
- Total model size: > 300 MB

**Solution**: Use our automated scripts or manual download.

---

## Model Download Options

### Option 1: Automated Download Script (Recommended)

```bash
cd model_deployment
./scripts/download_models.sh
```

**Interactive Menu:**
```
1. ResNet50 (Image Classification) - ~99MB
2. BERT Classifier (Text Classification) - ~256MB
3. Linear Regression (Simple Example) - ~4KB
4. All models
```

**What it does:**
- Downloads pretrained models from PyTorch Hub / Hugging Face
- Saves models in correct `model_repository/` structure
- Converts models to TorchScript format
- Verifies model files

**Requirements:**
- Python 3.8+
- PyTorch
- Transformers library

---

### Option 2: Train Simple Models

```bash
python scripts/train_simple_models.py
```

**Available Models:**
1. **Linear Regression**: Trains on synthetic data (y = 2.5x + 0.5)
2. **MLP Classifier**: Trains on XOR problem
3. **Simple CNN**: Creates architecture (no training)

**Output:**
- Models saved in `model_repository/<model_name>/1/model.pt`
- Training logs and metrics
- Test predictions

---

### Option 3: Manual Download

If scripts fail, download manually:

#### ResNet50

```python
import torch
import torchvision.models as models

# Download pretrained ResNet50
model = models.resnet50(pretrained=True)
model.eval()

# Convert to TorchScript
scripted_model = torch.jit.script(model)

# Save
save_path = "model_repository/resnet_model/1/model.pt"
scripted_model.save(save_path)
print(f"Saved: {save_path}")
```

#### BERT Classifier

```python
import torch
from transformers import AutoModelForSequenceClassification

# Download DistilBERT model
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# Convert to TorchScript
dummy_input = torch.randint(0, 30000, (1, 128))
attention_mask = torch.ones((1, 128), dtype=torch.long)
traced_model = torch.jit.trace(model, (dummy_input, attention_mask))

# Save
save_path = "model_repository/torch_classifier/1/model.pt"
traced_model.save(save_path)
print(f"Saved: {save_path}")
```

#### Linear Regression

```python
import torch
import torch.nn as nn

class LinearRegression(nn.Module):
    def __init__(self):
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(1, 1)
        self.linear.weight.data.fill_(2.5)
        self.linear.bias.data.fill_(0.5)
    
    def forward(self, x):
        return self.linear(x)

model = LinearRegression()
model.eval()

scripted_model = torch.jit.script(model)
save_path = "model_repository/linear_regression_model/1/model.pt"
scripted_model.save(save_path)
print(f"Saved: {save_path}")
```

---

## Manual Model Setup

### Step 1: Create Directory Structure

```bash
cd model_deployment

# Create model directories
mkdir -p model_repository/resnet_model/1
mkdir -p model_repository/torch_classifier/1
mkdir -p model_repository/linear_regression_model/1
```

### Step 2: Place Model Files

```
model_repository/
├── resnet_model/
│   ├── config.pbtxt          # Already provided
│   └── 1/
│       └── model.pt          # ← Place ResNet50 here
├── torch_classifier/
│   ├── config.pbtxt
│   └── 1/
│       └── model.pt          # ← Place BERT here
└── linear_regression_model/
    ├── config.pbtxt
    └── 1/
        └── model.pt          # ← Place linear model here
```

### Step 3: Verify File Sizes

```bash
ls -lh model_repository/*/1/model.pt
```

**Expected Output:**
```
-rw-r--r-- 1 user user   4K  model_repository/linear_regression_model/1/model.pt
-rw-r--r-- 1 user user  99M  model_repository/resnet_model/1/model.pt
-rw-r--r-- 1 user user 256M  model_repository/torch_classifier/1/model.pt
```

---

## Model Configuration

Each model requires a `config.pbtxt` file. These are already provided in the repository.

### Example: ResNet50 Config

```protobuf
name: "resnet_model"
backend: "pytorch"
max_batch_size: 32

input [
  {
    name: "input__0"
    data_type: TYPE_FP32
    dims: [-1, 3, 224, 224]
  }
]

output [
  {
    name: "output__0"
    data_type: TYPE_FP32
    dims: [-1, 1000]
  }
]

instance_group [
  {
    kind: KIND_GPU
    count: 1
  }
]

dynamic_batching {
  preferred_batch_size: [1, 8, 16]
  max_queue_delay_microseconds: 100
}
```

**Key Settings:**
- `backend: "pytorch"`: Use PyTorch backend
- `max_batch_size: 32`: Maximum batch size
- `dims: [-1, ...]`: Dynamic batching (-1 = variable batch)
- `KIND_GPU`: Use GPU for inference

---

## Verifying Models

### 1. Check File Existence

```bash
# Check all model files
find model_repository -name "model.pt" -o -name "model.py"
```

### 2. Test Model Loading (Optional)

```python
import torch

# Test ResNet50
model = torch.jit.load("model_repository/resnet_model/1/model.pt")
print(f"✓ ResNet50 loaded successfully")

# Test BERT
model = torch.jit.load("model_repository/torch_classifier/1/model.pt")
print(f"✓ BERT classifier loaded successfully")

# Test Linear Regression
model = torch.jit.load("model_repository/linear_regression_model/1/model.pt")
print(f"✓ Linear regression loaded successfully")
```

### 3. Start Triton and Check

```bash
# Start Triton
cd configs && docker-compose up -d

# Wait 30 seconds for models to load
sleep 30

# Check model status
curl -X POST http://localhost:8000/v2/repository/index
```

**Expected Output:**
```json
[
  {"name": "linear_regression_model", "version": "1", "state": "READY"},
  {"name": "resnet_model", "version": "1", "state": "READY"},
  {"name": "torch_classifier", "version": "1", "state": "READY"},
  ...
]
```

---

## Troubleshooting

### Models Not Loading

**Check 1: File Paths**
```bash
# Verify structure
tree model_repository/resnet_model/
# Expected:
# resnet_model/
# ├── config.pbtxt
# └── 1/
#     └── model.pt
```

**Check 2: File Permissions**
```bash
chmod 644 model_repository/*/1/model.pt
```

**Check 3: Triton Logs**
```bash
docker logs triton-server | grep -i error
```

### Download Script Fails

**Error: `ModuleNotFoundError: No module named 'torch'`**

**Solution:**
```bash
pip install torch torchvision transformers
```

**Error: `CUDA out of memory`**

**Solution:** Download CPU versions:
```python
# For ResNet50
model = models.resnet50(pretrained=True).cpu()

# For BERT
model = AutoModelForSequenceClassification.from_pretrained(model_name).cpu()
```

### Model File Corrupted

**Symptom:** Triton fails to load model

**Solution:** Re-download:
```bash
rm model_repository/resnet_model/1/model.pt
./scripts/download_models.sh
# Select option 1 (ResNet50)
```

### Disk Space Issues

**Check available space:**
```bash
df -h .
```

**Cleanup:**
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove Jupyter checkpoints
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
```

---

## Alternative: Use Pre-trained Models from Cloud

If download scripts fail, manually download from:

### ResNet50
- **Source**: [PyTorch Hub](https://pytorch.org/vision/stable/models.html#torchvision.models.resnet50)
- **Command**: Already handled by script

### BERT Classifier
- **Source**: [Hugging Face](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)
- **Manual Download**:
  ```bash
  git lfs install
  git clone https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english
  ```
  Then convert to TorchScript using script above.

---

## Model Updates

To update a model:

1. **Create new version directory:**
   ```bash
   mkdir model_repository/resnet_model/2
   ```

2. **Place new model file:**
   ```bash
   cp new_model.pt model_repository/resnet_model/2/model.pt
   ```

3. **Reload Triton:**
   ```bash
   curl -X POST http://localhost:8000/v2/repository/models/resnet_model/load
   ```

Triton will automatically serve the latest version (2).

---

## Summary Checklist

- [ ] Downloaded all required models
- [ ] Verified file sizes (ResNet50: ~99MB, BERT: ~256MB)
- [ ] Checked directory structure
- [ ] Tested model loading with Python
- [ ] Started Triton server
- [ ] Verified models show "READY" status
- [ ] Tested inference with sample request

---

## Next Steps

- **[Start Triton Server](../README.md#-quick-start)**
- **[Run Example Notebook](../notebooks/README.md)**
- **[API Usage Guide](API_GUIDE.md)**
- **[Troubleshooting](TROUBLESHOOTING.md)**
