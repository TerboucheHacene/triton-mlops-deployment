#!/usr/bin/env python3
"""
Train Simple Models for Triton Deployment
==========================================
This script trains simple machine learning models for demonstration purposes.
These models can be deployed on Triton Inference Server.
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
MODEL_REPO = REPO_ROOT / "model_repository"

print("=" * 60)
print("Simple Model Training Script")
print("=" * 60)
print(f"Repository root: {REPO_ROOT}")
print(f"Model repository: {MODEL_REPO}")
print()


# ============================================
# Linear Regression Model
# ============================================

class LinearRegressionModel(nn.Module):
    """Simple linear regression: y = mx + b"""
    def __init__(self, input_dim=1, output_dim=1):
        super(LinearRegressionModel, self).__init__()
        self.linear = nn.Linear(input_dim, output_dim)
    
    def forward(self, x):
        return self.linear(x)


def train_linear_regression():
    """Train a simple linear regression model"""
    print("\n" + "=" * 60)
    print("Training Linear Regression Model")
    print("=" * 60)
    
    # Generate synthetic data: y = 2.5x + 0.5 + noise
    torch.manual_seed(42)
    X_train = torch.randn(100, 1) * 10
    y_train = 2.5 * X_train + 0.5 + torch.randn(100, 1) * 0.5
    
    # Create model
    model = LinearRegressionModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    
    # Training loop
    epochs = 1000
    for epoch in range(epochs):
        # Forward pass
        predictions = model(X_train)
        loss = criterion(predictions, y_train)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 100 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    
    # Display learned parameters
    weight = model.linear.weight.item()
    bias = model.linear.bias.item()
    print(f"\nLearned parameters:")
    print(f"  Weight (m): {weight:.4f} (target: 2.5000)")
    print(f"  Bias (b): {bias:.4f} (target: 0.5000)")
    
    # Save as TorchScript
    model.eval()
    scripted_model = torch.jit.script(model)
    
    save_path = MODEL_REPO / "linear_regression_model" / "1" / "model.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    scripted_model.save(str(save_path))
    
    print(f"\n✓ Model saved to: {save_path}")
    print(f"  File size: {save_path.stat().st_size / 1024:.2f} KB")
    
    # Test inference
    test_input = torch.tensor([[5.0]])
    with torch.no_grad():
        prediction = model(test_input)
        expected = 2.5 * 5.0 + 0.5
        print(f"\nTest inference:")
        print(f"  Input: {test_input.item():.2f}")
        print(f"  Prediction: {prediction.item():.4f}")
        print(f"  Expected: {expected:.4f}")


# ============================================
# Multi-Layer Perceptron for Classification
# ============================================

class MLPClassifier(nn.Module):
    """Simple MLP for binary classification"""
    def __init__(self, input_dim=2, hidden_dim=10, output_dim=2):
        super(MLPClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


def train_mlp_classifier():
    """Train a simple MLP classifier for XOR problem"""
    print("\n" + "=" * 60)
    print("Training MLP Classifier (XOR Problem)")
    print("=" * 60)
    
    # XOR dataset
    X_train = torch.tensor([
        [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]
    ])
    y_train = torch.tensor([0, 1, 1, 0], dtype=torch.long)
    
    # Expand dataset with noise
    torch.manual_seed(42)
    X_expanded = []
    y_expanded = []
    for x, y in zip(X_train, y_train):
        for _ in range(50):
            noise = torch.randn(2) * 0.1
            X_expanded.append(x + noise)
            y_expanded.append(y)
    
    X_train = torch.stack(X_expanded)
    y_train = torch.tensor(y_expanded, dtype=torch.long)
    
    # Create model
    model = MLPClassifier(input_dim=2, hidden_dim=10, output_dim=2)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Training loop
    epochs = 500
    for epoch in range(epochs):
        # Forward pass
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 100 == 0:
            # Calculate accuracy
            _, predicted = torch.max(outputs.data, 1)
            accuracy = (predicted == y_train).sum().item() / len(y_train)
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}, Accuracy: {accuracy:.2%}")
    
    # Save as TorchScript
    model.eval()
    scripted_model = torch.jit.script(model)
    
    save_path = MODEL_REPO / "mlp_classifier" / "1" / "model.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    scripted_model.save(str(save_path))
    
    print(f"\n✓ Model saved to: {save_path}")
    print(f"  File size: {save_path.stat().st_size / 1024:.2f} KB")
    
    # Test inference
    test_inputs = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    with torch.no_grad():
        outputs = model(test_inputs)
        _, predictions = torch.max(outputs, 1)
        
        print("\nTest inference (XOR truth table):")
        for i, (x, pred) in enumerate(zip(test_inputs, predictions)):
            print(f"  Input: [{x[0]:.0f}, {x[1]:.0f}] → Prediction: {pred.item()}")


# ============================================
# Simple CNN for Image Classification
# ============================================

class SimpleCNN(nn.Module):
    """Simple CNN for MNIST-like data"""
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 32 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def create_simple_cnn():
    """Create a simple CNN model (without training, just architecture)"""
    print("\n" + "=" * 60)
    print("Creating Simple CNN Model")
    print("=" * 60)
    print("Note: This creates the architecture only, not trained.")
    
    # Create model
    model = SimpleCNN()
    model.eval()
    
    # Save as TorchScript
    example_input = torch.randn(1, 1, 28, 28)
    traced_model = torch.jit.trace(model, example_input)
    
    save_path = MODEL_REPO / "simple_cnn" / "1" / "model.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    traced_model.save(str(save_path))
    
    print(f"\n✓ Model saved to: {save_path}")
    print(f"  File size: {save_path.stat().st_size / 1024:.2f} KB")
    print(f"  Input shape: (batch, 1, 28, 28)")
    print(f"  Output shape: (batch, 10)")


# ============================================
# Main Menu
# ============================================

def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("Available Models to Train:")
    print("=" * 60)
    print("1. Linear Regression (y = mx + b)")
    print("2. MLP Classifier (XOR problem)")
    print("3. Simple CNN (architecture only)")
    print("4. All models")
    print()
    
    choice = input("Select option (1-4, or 'q' to quit): ").strip()
    
    if choice == '1':
        train_linear_regression()
    elif choice == '2':
        train_mlp_classifier()
    elif choice == '3':
        create_simple_cnn()
    elif choice == '4':
        train_linear_regression()
        train_mlp_classifier()
        create_simple_cnn()
    elif choice.lower() == 'q':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid option")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Training Complete!")
    print("=" * 60)
    print(f"Models are saved in: {MODEL_REPO}")
    print("\nNext steps:")
    print("1. Start Triton server: cd configs && docker-compose up -d")
    print("2. Check models loaded: curl -X POST http://localhost:8000/v2/repository/index")
    print("3. Run inference from your notebook or client")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
