# 🚀 Triton Inference Server - MLOps Model Deployment

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Triton](https://img.shields.io/badge/NVIDIA-Triton-green.svg)](https://github.com/triton-inference-server/server)

A production-ready MLOps project demonstrating how to deploy PyTorch and Python-based machine learning models using **NVIDIA Triton Inference Server**. This repository showcases model serving, ensemble pipelines, preprocessing/postprocessing, and client integration.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Models](#-models)
- [Project Structure](#-project-structure)
- [Setup Guide](#-setup-guide)
- [Usage](#-usage)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **🎯 Multi-Model Deployment**: Deploy PyTorch, TorchScript, and Python backend models
- **🔗 Ensemble Pipelines**: Chain models for end-to-end inference (preprocessing → inference → postprocessing)
- **⚡ Dynamic Batching**: Automatic request batching for improved throughput
- **🐳 Docker Support**: Containerized deployment with Docker Compose
- **📊 Multiple Backends**: PyTorch, Python, and Ensemble model support
- **🧪 Complete Examples**: Jupyter notebooks for training and client testing
- **📝 Comprehensive Logging**: Detailed logging and monitoring guide
- **🔄 Model Versioning**: Support for multiple model versions
- **🌐 REST API**: HTTP/REST interface for easy integration
- **📦 Production Ready**: Includes error handling, validation, and best practices

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│ (HTTP/REST) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   NVIDIA Triton Inference Server    │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   PyTorch    │  │   Python    │ │
│  │   Backend    │  │   Backend   │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                 │        │
│  ┌──────▼─────────────────▼──────┐ │
│  │     Ensemble Pipelines        │ │
│  │  • Image Classification       │ │
│  │  • Sentiment Analysis         │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Model Pipeline Example (ResNet Ensemble):

```
Input Image (numpy array)
    │
    ▼
[Preprocessor] → Resize, Normalize, Transform
    │
    ▼
[ResNet50 Model] → 1000 ImageNet logits
    │
    ▼
[Postprocessor] → Class label + Confidence
    │
    ▼
Output: {"class": "bucket", "confidence": 0.85}
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 1.29+
- **Python**: 3.8+ (for training and client)
- **NVIDIA GPU** (recommended) with CUDA support

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/model_deployment.git
cd model_deployment
```

### 2️⃣ Download Models

Models are not included in the repository (too large for Git). Download them using:

```bash
# Option 1: Download pretrained models
./scripts/download_models.sh

# Option 2: Train simple models locally
python scripts/train_simple_models.py
```

**Note**: ResNet50 (~99MB) and BERT classifier (~256MB) will be downloaded from PyTorch Hub and Hugging Face.

### 3️⃣ Start Triton Server

```bash
cd configs
docker-compose up -d
```

### 4️⃣ Verify Deployment

```bash
# Check server health
curl http://localhost:8000/v2/health/ready

# List loaded models
curl -X POST http://localhost:8000/v2/repository/index
```

### 5️⃣ Run Example Notebook

```bash
pip install jupyter tritonclient[http] numpy pillow
jupyter notebook notebooks/client.ipynb
```

---

## 🎯 Models

| Model Name | Type | Purpose | Input | Output | Size |
|------------|------|---------|-------|--------|------|
| `linear_regression_model` | PyTorch | Simple regression | (batch, 1) | (batch, 1) | 4 KB |
| `resnet_model` | PyTorch | Image classification | (batch, 3, 224, 224) | (batch, 1000) | 99 MB |
| `resnet_ensemble` | Ensemble | End-to-end image pipeline | RGB image | label + confidence | - |
| `torch_classifier` | PyTorch | BERT text classification | tokenized text | (batch, 2) | 256 MB |
| `text_ensemble` | Ensemble | End-to-end sentiment | raw text | sentiment + confidence | - |
| `sentiment` | Python | 5-star sentiment rating | raw text | label + score | - |

**Ensemble Models** (recommended for production):
- **`resnet_ensemble`**: Preprocessing → ResNet50 → Postprocessing
- **`text_ensemble`**: Tokenization → BERT → Label Mapping

See [`model_repository/README.md`](model_repository/README.md) for detailed model specifications.

---

## 📁 Project Structure

```
model_deployment/
├── configs/
│   └── docker-compose.yaml       # Docker Compose configuration
├── docs/
│   ├── TRITON_LOGGING_GUIDE.md   # Comprehensive logging guide
│   ├── MODEL_SETUP.md            # Model download and setup
│   ├── API_GUIDE.md              # API usage examples
│   └── TROUBLESHOOTING.md        # Common issues and fixes
├── model_repository/
│   ├── README.md                 # Model documentation
│   ├── linear_regression_model/  # Simple linear regression
│   ├── resnet_model/             # ResNet50 PyTorch model
│   ├── resnet_preprocessor/      # Image preprocessing
│   ├── resnet_postprocessor/     # Classification postprocessing
│   ├── resnet_ensemble/          # Complete image pipeline
│   ├── torch_classifier/         # BERT text classifier
│   ├── text_preprocessor/        # Text tokenization
│   ├── text_postprocessor/       # Sentiment label mapping
│   ├── text_ensemble/            # Complete text pipeline
│   └── sentiment/                # 5-star sentiment model
├── notebooks/
│   ├── README.md                 # Notebook documentation
│   ├── train.ipynb               # Model training examples
│   └── client.ipynb              # Triton client examples
├── scripts/
│   ├── download_models.sh        # Download pretrained models
│   └── train_simple_models.py    # Train simple demo models
├── src/
│   └── test.py                   # Client test scripts
├── tests/
│   └── .gitkeep                  # Unit tests (to be added)
├── .dockerignore                 # Docker build exclusions
├── .gitignore                    # Git exclusions
├── Dockerfile                    # Triton server image
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## 🛠️ Setup Guide

### Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download models
./scripts/download_models.sh

# 4. Start Triton server
cd configs && docker-compose up -d

# 5. Run tests
python src/test.py
```

### Docker Configuration

The `configs/docker-compose.yaml` includes:
- **Shared Memory**: 1GB for Python backend models
- **GPU Support**: NVIDIA runtime for GPU acceleration
- **Port Mappings**:
  - `8000`: HTTP REST API
  - `8001`: gRPC API
  - `8002`: Metrics endpoint
- **Volume Mount**: Links local `model_repository/` to container

**Important**: Ensure models are downloaded before starting Docker.

---

## 📖 Usage

### HTTP REST API

#### Check Server Health

```bash
curl http://localhost:8000/v2/health/live
curl http://localhost:8000/v2/health/ready
```

#### List Models

```bash
curl -X POST http://localhost:8000/v2/repository/index
```

#### Inference Example (Linear Regression)

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

#### Inference Example (ResNet Ensemble)

```python
import tritonclient.http as httpclient
from PIL import Image
import numpy as np

# Load and prepare image
image = Image.open("cat.jpg").convert("RGB")
image_array = np.array(image)

# Create Triton client
client = httpclient.InferenceServerClient(url="localhost:8000")

# Prepare input
input_data = httpclient.InferInput("input_image", image_array.shape, "UINT8")
input_data.set_data_from_numpy(image_array)

# Run inference
result = client.infer("resnet_ensemble", inputs=[input_data])

# Get outputs
label = result.as_numpy("class_label")[0].decode()
confidence = result.as_numpy("confidence")[0]

print(f"Prediction: {label} ({confidence:.2%})")
```

See [`docs/API_GUIDE.md`](docs/API_GUIDE.md) for more examples.

---

## 📚 Documentation

- **[Triton Logging Guide](docs/TRITON_LOGGING_GUIDE.md)**: Complete guide to viewing and debugging logs
- **[Model Setup](docs/MODEL_SETUP.md)**: Detailed model download and configuration
- **[API Guide](docs/API_GUIDE.md)**: REST API usage and code examples
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Model Repository](model_repository/README.md)**: Model specifications
- **[Notebooks](notebooks/README.md)**: Jupyter notebook documentation

---

## 🐛 Troubleshooting

### Common Issues

**1. Models Not Loading**
```bash
# Check model files exist
ls -lh model_repository/*/1/model.*

# Check Triton logs
docker logs triton-server

# Verify config files
cat model_repository/resnet_model/config.pbtxt
```

**2. Shared Memory Error (Python Backend)**
```
Error: Shared memory region creation failed
```
**Solution**: Increase `shm_size` in `docker-compose.yaml` to `'2gb'`

**3. Connection Refused**
```bash
# Check if Triton is running
docker ps | grep triton

# Wait for models to load (can take 30-60 seconds)
docker logs -f triton-server
```

See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for more solutions.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NVIDIA Triton Inference Server**: https://github.com/triton-inference-server/server
- **PyTorch**: https://pytorch.org/
- **Hugging Face Transformers**: https://huggingface.co/transformers/

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/model_deployment/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/model_deployment/discussions)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

---

**Built with ❤️ for the MLOps community**