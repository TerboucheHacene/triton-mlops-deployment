# Contributing to Model Deployment

Thank you for considering contributing to this project! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## How to Contribute

### Types of Contributions

We welcome:
- 🐛 **Bug fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🧪 **Test cases**
- 🎨 **Code refactoring**
- 🔧 **Configuration improvements**

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/model_deployment.git
cd model_deployment
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 4. Download Models

```bash
./scripts/download_models.sh
```

### 5. Start Triton Server

```bash
cd configs && docker-compose up -d
```

### 6. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## Coding Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** where possible
- Write **docstrings** for all functions/classes
- Maximum line length: **120 characters**

```python
def preprocess_image(image: np.ndarray, size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
    """
    Preprocess image for ResNet model.
    
    Args:
        image: Input image as numpy array (H, W, C)
        size: Target size for resizing
    
    Returns:
        Preprocessed image tensor (C, H, W)
    """
    # Implementation here
    pass
```

### Formatting Tools

```bash
# Install formatters
pip install black isort flake8

# Format code
black .
isort .

# Check linting
flake8 .
```

### Configuration Files

- Use **protobuf** format for Triton configs (`config.pbtxt`)
- Use **YAML** for Docker configs
- Use **JSON** for data files

---

## Commit Messages

Follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(model): add support for ONNX models

Add ONNX backend support for deploying ONNX models on Triton.
Includes configuration examples and documentation.

Closes #123
```

```bash
fix(client): handle connection timeout gracefully

Added retry logic and better error messages when Triton
server is not reachable.
```

```bash
docs(readme): update quick start guide

Simplified installation steps and added troubleshooting
section for common Docker issues.
```

---

## Pull Request Process

### 1. Ensure Quality

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with `main`

### 2. Run Tests

```bash
# Run unit tests (when available)
pytest tests/

# Test models manually
python src/test.py

# Check Triton server
curl http://localhost:8000/v2/health/ready
```

### 3. Update Documentation

If you changed:
- **Models**: Update `model_repository/README.md`
- **API**: Update `docs/API_GUIDE.md`
- **Setup**: Update `docs/MODEL_SETUP.md` or main `README.md`
- **Configuration**: Update relevant docs

### 4. Create Pull Request

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to GitHub and create a Pull Request

3. Fill out the PR template with:
   - **Description** of changes
   - **Related issues** (e.g., "Closes #123")
   - **Testing done**
   - **Screenshots** (if UI changes)

### 5. Code Review

- Address review comments promptly
- Keep discussions focused and respectful
- Update PR based on feedback

### 6. Merge

Once approved:
- Squash commits if needed
- Maintainer will merge the PR

---

## Reporting Bugs

### Before Reporting

1. **Search existing issues**: Check if already reported
2. **Check documentation**: Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **Test with latest version**: Update to latest code

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Start Triton server: `docker-compose up`
2. Run client: `python src/test.py`
3. See error: ...

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10]
- Docker version: [e.g., 20.10.21]
- Triton version: [e.g., 23.08]
- GPU: [e.g., NVIDIA RTX 3080]

**Logs**
```
Paste relevant logs here
```

**Additional context**
Any other information that might help.
```

---

## Suggesting Enhancements

### Enhancement Template

```markdown
**Feature description**
Clear description of the proposed feature.

**Motivation**
Why is this feature needed? What problem does it solve?

**Proposed solution**
How would you implement this feature?

**Alternatives considered**
What other approaches did you consider?

**Additional context**
Any mockups, diagrams, or examples.
```

---

## Adding New Models

### Steps to Add a Model

1. **Create model directory:**
   ```bash
   mkdir -p model_repository/my_new_model/1
   ```

2. **Add model file:**
   - PyTorch: `model.pt` (TorchScript)
   - Python: `model.py`

3. **Create config.pbtxt:**
   ```protobuf
   name: "my_new_model"
   backend: "pytorch"  # or "python"
   max_batch_size: 16
   
   input [
     {
       name: "input__0"
       data_type: TYPE_FP32
       dims: [-1, 10]
     }
   ]
   
   output [
     {
       name: "output__0"
       data_type: TYPE_FP32
       dims: [-1, 1]
     }
   ]
   ```

4. **Update documentation:**
   - Add to `model_repository/README.md`
   - Add usage example to `docs/API_GUIDE.md`

5. **Test thoroughly:**
   ```python
   # Test loading
   curl http://localhost:8000/v2/models/my_new_model
   
   # Test inference
   python -c "
   import tritonclient.http as httpclient
   import numpy as np
   
   client = httpclient.InferenceServerClient('localhost:8000')
   inputs = [httpclient.InferInput('input__0', [1, 10], 'FP32')]
   inputs[0].set_data_from_numpy(np.random.rand(1, 10).astype(np.float32))
   
   result = client.infer('my_new_model', inputs=inputs)
   print(result.as_numpy('output__0'))
   "
   ```

6. **Submit PR** with model configuration and documentation

---

## Development Tools

### Recommended IDE Setup

**VS Code Extensions:**
- Python
- Docker
- YAML
- Markdown All in One
- GitLens

**VS Code Settings:**
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [120]
}
```

---

## Testing

### Manual Testing Checklist

- [ ] Server starts without errors
- [ ] All models load successfully
- [ ] Inference requests return expected results
- [ ] Error cases handled gracefully
- [ ] Documentation is accurate
- [ ] Examples run successfully

### Automated Tests (Coming Soon)

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Model tests
pytest tests/models/
```

---

## Questions?

- **Issues**: [GitHub Issues](https://github.com/yourusername/model_deployment/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/model_deployment/discussions)

---

Thank you for contributing! 🙏
