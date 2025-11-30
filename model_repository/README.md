# Model Repository

This directory contains all models deployed on the Triton Inference Server. Each model follows the Triton model repository structure.

## 📁 Directory Structure

```
model_repository/
├── <model_name>/
│   ├── config.pbtxt          # Triton configuration
│   ├── 1/                    # Version 1
│   │   ├── model.pt          # PyTorch model (for PyTorch backend)
│   │   └── model.py          # Python model (for Python backend)
│   └── <version_n>/          # Additional versions
```

## 🎯 Available Models

### 1. **Linear Regression Model** (`linear_regression_model`)
- **Type**: PyTorch TorchScript
- **Backend**: PyTorch
- **Purpose**: Simple linear regression example
- **Input**: `input__0` (FP32, [-1, 1])
- **Output**: `output__0` (FP32, [-1, 1])
- **File**: `linear_regression_model/1/model.pt`
- **Size**: ~4 KB

**Example Use Case**: Predicting continuous values from single input feature.

---

### 2. **ResNet50 Model** (`resnet_model`)
- **Type**: PyTorch TorchScript
- **Backend**: PyTorch
- **Purpose**: Image classification using pretrained ResNet50
- **Input**: `input__0` (FP32, [-1, 3, 224, 224])
- **Output**: `output__0` (FP32, [-1, 1000])
- **File**: `resnet_model/1/model.pt`
- **Size**: ~99 MB
- **Pretrained**: ImageNet (1000 classes)

**Example Use Case**: Image classification with 1000 ImageNet categories.

---

### 3. **ResNet Preprocessor** (`resnet_preprocessor`)
- **Type**: Python Backend
- **Purpose**: Preprocess images for ResNet50
- **Input**: `input_image` (UINT8, [-1, -1, -1, 3])
- **Output**: `preprocessed_image` (FP32, [-1, 3, 224, 224])
- **File**: `resnet_preprocessor/1/model.py`
- **Operations**:
  - Resize to 224×224
  - Normalize with ImageNet mean/std
  - Convert HWC → CHW format

---

### 4. **ResNet Postprocessor** (`resnet_postprocessor`)
- **Type**: Python Backend
- **Purpose**: Convert ResNet logits to class labels
- **Input**: `logits` (FP32, [-1, 1000])
- **Output**: 
  - `class_label` (STRING, [-1, 1])
  - `confidence` (FP32, [-1, 1])
- **File**: `resnet_postprocessor/1/model.py`
- **Dependencies**: `imagenet_labels.json`

---

### 5. **ResNet Ensemble** (`resnet_ensemble`)
- **Type**: Ensemble Pipeline
- **Purpose**: Complete image classification pipeline
- **Input**: `input_image` (UINT8, [-1, -1, -1, 3])
- **Output**:
  - `class_label` (STRING, [-1, 1])
  - `confidence` (FP32, [-1, 1])
- **Pipeline**: Preprocessor → ResNet50 → Postprocessor
- **File**: `resnet_ensemble/config.pbtxt` (no model file)

**Example Use Case**: End-to-end image classification with single API call.

---

### 6. **BERT Classifier** (`torch_classifier`)
- **Type**: PyTorch TorchScript
- **Backend**: PyTorch
- **Purpose**: Text classification using BERT
- **Input**: 
  - `input_ids` (INT64, [-1, 128])
  - `attention_mask` (INT64, [-1, 128])
- **Output**: `output__0` (FP32, [-1, 2])
- **File**: `torch_classifier/1/model.pt`
- **Size**: ~256 MB
- **Pretrained**: DistilBERT SST-2

---

### 7. **Text Preprocessor** (`text_preprocessor`)
- **Type**: Python Backend
- **Purpose**: Tokenize text for BERT
- **Input**: `text` (STRING, [-1, 1])
- **Output**:
  - `input_ids` (INT64, [-1, 128])
  - `attention_mask` (INT64, [-1, 128])
- **File**: `text_preprocessor/1/model.py`
- **Dependencies**: Hugging Face Transformers

---

### 8. **Text Postprocessor** (`text_postprocessor`)
- **Type**: Python Backend
- **Purpose**: Convert BERT logits to sentiment labels
- **Input**: `logits` (FP32, [-1, 2])
- **Output**: 
  - `sentiment` (STRING, [-1, 1])
  - `confidence` (FP32, [-1, 1])
- **File**: `text_postprocessor/1/model.py`

---

### 9. **Text Ensemble** (`text_ensemble`)
- **Type**: Ensemble Pipeline
- **Purpose**: Complete sentiment analysis pipeline
- **Input**: `text` (STRING, [-1, 1])
- **Output**:
  - `sentiment` (STRING, [-1, 1])
  - `confidence` (FP32, [-1, 1])
- **Pipeline**: Text Preprocessor → BERT → Text Postprocessor
- **File**: `text_ensemble/config.pbtxt`

**Example Use Case**: End-to-end sentiment analysis with single API call.

---

### 10. **Sentiment Model** (`sentiment`)
- **Type**: Python Backend
- **Purpose**: Direct sentiment analysis using Transformers pipeline
- **Input**: `text` (STRING, [-1, 1])
- **Output**:
  - `label` (STRING, [-1, 1])
  - `score` (FP32, [-1, 1])
- **File**: `sentiment/1/model.py`
- **Model**: `nlptown/bert-base-multilingual-uncased-sentiment`
- **Classes**: 1-5 stars rating

**Example Use Case**: 5-star sentiment classification for reviews.

---

## 🔧 Configuration Files

Each model has a `config.pbtxt` file that defines:
- **name**: Model identifier
- **backend**: PyTorch, Python, or Ensemble
- **max_batch_size**: Maximum batch size (0 for non-batching)
- **input**: Input tensor specifications
- **output**: Output tensor specifications
- **instance_group**: GPU/CPU placement
- **dynamic_batching**: Batching configuration

### Example `config.pbtxt`:
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
```

## 📦 Model Versioning

Triton supports multiple model versions:
- Each version is in a numbered directory (1, 2, 3, ...)
- Triton serves the latest version by default
- You can specify which version to use via API

## 🚀 Adding New Models

1. Create model directory: `mkdir -p model_repository/<model_name>/1`
2. Add model file: `model.pt` (PyTorch) or `model.py` (Python)
3. Create `config.pbtxt` with proper specifications
4. Restart Triton or use model control API

## 📚 References

- [Triton Model Repository Documentation](https://github.com/triton-inference-server/server/blob/main/docs/user_guide/model_repository.md)
- [Triton Model Configuration](https://github.com/triton-inference-server/server/blob/main/docs/user_guide/model_configuration.md)
- [Ensemble Models](https://github.com/triton-inference-server/server/blob/main/docs/user_guide/architecture.md#ensemble-models)
