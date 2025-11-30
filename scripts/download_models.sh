#!/bin/bash

# ============================================
# Download Pretrained Models for Triton Server
# ============================================
# This script downloads the required pretrained models
# and places them in the correct model_repository structure

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_REPO="$REPO_ROOT/model_repository"

echo "=========================================="
echo "Model Download Script"
echo "=========================================="
echo "Repository root: $REPO_ROOT"
echo "Model repository: $MODEL_REPO"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# Helper Functions
# ============================================

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python3 found${NC}"
}

check_dependencies() {
    echo "Checking Python dependencies..."
    python3 -c "import torch; import transformers" 2>/dev/null || {
        echo -e "${YELLOW}Warning: PyTorch or Transformers not found${NC}"
        echo "Installing dependencies..."
        pip install torch torchvision transformers
    }
    echo -e "${GREEN}✓ Dependencies OK${NC}"
}

# ============================================
# Download ResNet50 Model
# ============================================

download_resnet50() {
    echo ""
    echo "=========================================="
    echo "Downloading ResNet50 Model"
    echo "=========================================="
    
    MODEL_DIR="$MODEL_REPO/resnet_model/1"
    MODEL_FILE="$MODEL_DIR/model.pt"
    
    if [ -f "$MODEL_FILE" ]; then
        echo -e "${YELLOW}ResNet50 model already exists at $MODEL_FILE${NC}"
        read -p "Do you want to re-download? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping ResNet50 download"
            return
        fi
    fi
    
    echo "Downloading ResNet50 from PyTorch Hub..."
    python3 << EOF
import torch
import torchvision.models as models

# Download ResNet50 pretrained model
model = models.resnet50(pretrained=True)
model.eval()

# Save as TorchScript
scripted_model = torch.jit.script(model)
scripted_model.save("$MODEL_FILE")

print("✓ ResNet50 model saved to: $MODEL_FILE")
print(f"  Size: {torch.jit.get_cpp_stacktraces_enabled()}")
EOF
    
    echo -e "${GREEN}✓ ResNet50 download complete${NC}"
    ls -lh "$MODEL_FILE"
}

# ============================================
# Download BERT Classifier Model
# ============================================

download_bert_classifier() {
    echo ""
    echo "=========================================="
    echo "Downloading BERT Classifier Model"
    echo "=========================================="
    
    MODEL_DIR="$MODEL_REPO/torch_classifier/1"
    MODEL_FILE="$MODEL_DIR/model.pt"
    
    if [ -f "$MODEL_FILE" ]; then
        echo -e "${YELLOW}BERT classifier already exists at $MODEL_FILE${NC}"
        read -p "Do you want to re-download? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping BERT classifier download"
            return
        fi
    fi
    
    echo "Downloading BERT model from Hugging Face..."
    python3 << EOF
import torch
from transformers import AutoModelForSequenceClassification

# Download BERT base model fine-tuned for sentiment analysis
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# Save as TorchScript
dummy_input = torch.randint(0, 30000, (1, 128))
attention_mask = torch.ones((1, 128), dtype=torch.long)

traced_model = torch.jit.trace(model, (dummy_input, attention_mask))
traced_model.save("$MODEL_FILE")

print("✓ BERT classifier saved to: $MODEL_FILE")
EOF
    
    echo -e "${GREEN}✓ BERT classifier download complete${NC}"
    ls -lh "$MODEL_FILE"
}

# ============================================
# Create Placeholder for Linear Regression
# ============================================

create_linear_regression() {
    echo ""
    echo "=========================================="
    echo "Creating Linear Regression Model"
    echo "=========================================="
    
    MODEL_DIR="$MODEL_REPO/linear_regression_model/1"
    MODEL_FILE="$MODEL_DIR/model.pt"
    
    if [ -f "$MODEL_FILE" ]; then
        echo -e "${GREEN}✓ Linear regression model already exists${NC}"
        return
    fi
    
    echo "Creating simple linear regression model..."
    python3 << EOF
import torch
import torch.nn as nn

# Create a simple linear regression model
class LinearRegression(nn.Module):
    def __init__(self):
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(1, 1)
        # Set some example weights
        self.linear.weight.data.fill_(2.5)
        self.linear.bias.data.fill_(0.5)
    
    def forward(self, x):
        return self.linear(x)

model = LinearRegression()
model.eval()

# Save as TorchScript
scripted_model = torch.jit.script(model)
scripted_model.save("$MODEL_FILE")

print("✓ Linear regression model created at: $MODEL_FILE")
EOF
    
    echo -e "${GREEN}✓ Linear regression model created${NC}"
    ls -lh "$MODEL_FILE"
}

# ============================================
# Main Execution
# ============================================

main() {
    echo ""
    check_python
    check_dependencies
    
    echo ""
    echo "=========================================="
    echo "Available Models to Download:"
    echo "=========================================="
    echo "1. ResNet50 (Image Classification) - ~99MB"
    echo "2. BERT Classifier (Text Classification) - ~256MB"
    echo "3. Linear Regression (Simple Example) - ~4KB"
    echo "4. All models"
    echo ""
    
    read -p "Select option (1-4, or 'q' to quit): " choice
    
    case $choice in
        1)
            download_resnet50
            ;;
        2)
            download_bert_classifier
            ;;
        3)
            create_linear_regression
            ;;
        4)
            create_linear_regression
            download_resnet50
            download_bert_classifier
            ;;
        q|Q)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Download Complete!${NC}"
    echo "=========================================="
    echo "Models are ready in: $MODEL_REPO"
    echo ""
    echo "Next steps:"
    echo "1. Start Triton server: cd configs && docker-compose up -d"
    echo "2. Check models loaded: curl -X POST http://localhost:8000/v2/repository/index"
    echo "3. Run example notebook: jupyter notebook notebooks/client.ipynb"
}

# Run main function
main
