# Jupyter Notebooks

This directory contains Jupyter notebooks for training models and testing Triton Inference Server.

## 📓 Available Notebooks

### 1. **`train.ipynb`** - Model Training

**Purpose**: Train and export models for Triton deployment.

**Contents**:
- Linear regression model training
- PyTorch model export to TorchScript
- Model saving in correct directory structure

**Prerequisites**:
```bash
pip install torch torchvision numpy matplotlib
```

**Usage**:
```bash
jupyter notebook notebooks/train.ipynb
```

**Outputs**:
- `model_repository/linear_regression_model/1/model.pt`
- Training visualization plots
- Model performance metrics

---

### 2. **`client.ipynb`** - Triton Client Testing

**Purpose**: Test Triton Inference Server with various models.

**Contents**:
- Triton server health checks
- Model repository inspection
- Inference requests for all models:
  - Linear regression
  - ResNet50 image classification
  - BERT sentiment analysis
  - Ensemble pipelines
- Response parsing and visualization

**Prerequisites**:
```bash
# Install Triton client
pip install tritonclient[http] numpy pillow

# Start Triton server
cd configs && docker-compose up -d
```

**Usage**:
```bash
# Wait for Triton to load models (~30 seconds)
sleep 30

# Open notebook
jupyter notebook notebooks/client.ipynb
```

**Key Features**:
- ✅ Server health and readiness checks
- ✅ List all loaded models
- ✅ Single and batch inference examples
- ✅ Image and text processing examples
- ✅ Performance timing measurements

---

## 🚀 Quick Start

### Setup Environment

```bash
# Install Jupyter
pip install jupyter ipykernel

# Create kernel (if using virtual environment)
python -m ipykernel install --user --name=deployment --display-name "Python (deployment)"

# Install dependencies
pip install -r requirements.txt
```

### Launch Jupyter

```bash
# From repository root
jupyter notebook notebooks/
```

### Start Triton Server (Required for client.ipynb)

```bash
# Navigate to configs directory
cd configs

# Start Triton with Docker Compose
docker-compose up -d

# Wait for models to load
docker logs -f triton-server

# When you see "Started GRPCInferenceService", press Ctrl+C
```

---

## 📊 Expected Outputs

### train.ipynb
- Linear regression convergence plot
- Model weights and bias values
- Test predictions vs. actual values
- Saved model file (~4 KB)

### client.ipynb
- Server status: **READY**
- Number of models: **10**
- Sample predictions:
  - Linear regression: `f(5.0) ≈ 13.0`
  - Image classification: `"bucket"` with 85% confidence
  - Sentiment: `"5 stars"` with 84% confidence

---

## 🔧 Troubleshooting

### Notebook Kernel Not Found
```bash
python -m ipykernel install --user --name=deployment
```

### Triton Connection Error
```bash
# Check if Triton is running
docker ps | grep triton

# Check Triton logs
docker logs triton-server

# Restart Triton
cd configs && docker-compose restart
```

### Import Errors
```bash
# Install all requirements
pip install -r requirements.txt

# Verify installations
python -c "import tritonclient.http as httpclient; print('✓ Triton client OK')"
python -c "import torch; print('✓ PyTorch OK')"
```

### Model Not Found
```bash
# Check model repository
curl -X POST http://localhost:8000/v2/repository/index

# Reload models
curl -X POST http://localhost:8000/v2/repository/index
```

---

## 📁 Notebook Structure

```
notebooks/
├── README.md           # This file
├── train.ipynb         # Model training notebook
├── client.ipynb        # Triton client testing notebook
└── .gitkeep           # Keep directory in git
```

---

## 🎯 Best Practices

1. **Clear Outputs Before Committing**:
   ```bash
   jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
   ```

2. **Use Markdown Cells**: Document your code with markdown explanations

3. **Save Regularly**: Notebooks auto-save, but use `Cmd/Ctrl+S` frequently

4. **Restart Kernel**: Use "Kernel → Restart & Run All" to verify reproducibility

5. **Virtual Environment**: Always work in a virtual environment

---

## 📚 Additional Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Triton Client API](https://github.com/triton-inference-server/client)
- [PyTorch TorchScript](https://pytorch.org/docs/stable/jit.html)
- [Triton Python Backend](https://github.com/triton-inference-server/python_backend)

---

## 💡 Tips

- **Performance**: Use batch inference for better throughput
- **Memory**: Close unused notebooks to free RAM
- **Debugging**: Use `%%time` magic to profile cells
- **Visualization**: Use matplotlib/seaborn for plots
- **Version Control**: Clear outputs before committing to git
