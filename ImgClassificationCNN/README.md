# Image Classification with CNN (CIFAR-10)

A PyTorch implementation of a Convolutional Neural Network (CNN) for image classification on the CIFAR-10 dataset. Optimized for Google Colab with GPU support.

## 📦 CIFAR-10 Dataset Download

### Direct Download Links

| Source | URL |
|--------|-----|
| **Official (Toronto)** | https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz |
| **Kaggle** | https://www.kaggle.com/datasets/swaroopchil/cifar10-pngs-in-folders |
| **PyTorch Mirrors** | Auto-downloaded via torchvision |

### Quick Download (Colab/VS Code)

```bash
# Create data directory and download
!mkdir -p ./data
!wget https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz -P ./data
!tar -xzvf ./data/cifar-10-python.tar.gz -C ./data
```

**Or with curl:**
```bash
!mkdir -p ./data
!curl -o ./data/cifar-10-python.tar.gz https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz
!tar -xzvf ./data/cifar-10-python.tar.gz -C ./data
```

### PyTorch Auto-Download (Recommended)

The dataset downloads automatically on first run:
```python
import torchvision
torchvision.datasets.CIFAR10(root='./data', train=True, download=True)
```

## 🚀 Quick Start

### Installation

```bash
pip3 install numpy pillow torch torchvision
```

### For VS Code + Colab (GPU)

1. Open the notebook in VS Code
2. Connect to Google Colab runtime
3. Enable GPU: `Runtime > Change runtime type > T4 GPU`

### For Google Colab Direct

1. Upload `ImgClassificationCNN.ipynb` to Google Colab
2. Go to `Runtime > Change runtime type > Hardware accelerator > GPU`
3. Run all cells

## 📊 Dataset Details

**CIFAR-10** consists of 60,000 32x32 color images in 10 classes:

| Class | Images |
|-------|--------|
| airplane | 6,000 |
| automobile | 6,000 |
| bird | 6,000 |
| cat | 6,000 |
| deer | 6,000 |
| dog | 6,000 |
| frog | 6,000 |
| horse | 6,000 |
| ship | 6,000 |
| truck | 6,000 |

- **Training set:** 50,000 images
- **Test set:** 10,000 images
- **Image size:** 32×32 pixels
- **Channels:** 3 (RGB)
- **Download size:** ~170 MB

## 🏗️ Model Architecture

```
Input (3, 32, 32)
    ↓
Conv2d(3, 12, 5) + ReLU → (12, 28, 28)
    ↓
MaxPool2d(2, 2) → (12, 14, 14)
    ↓
Conv2d(12, 24, 5) + ReLU → (24, 10, 10)
    ↓
MaxPool2d(2, 2) → (24, 5, 5)
    ↓
Flatten → (1200)
    ↓
Linear(1200, 120) + ReLU → (120)
    ↓
Linear(120, 84) + ReLU → (84)
    ↓
Linear(84, 10) → Output
```

**Total Parameters:** ~156K

### Layer Breakdown

| Layer | Input Shape | Output Shape | Parameters |
|-------|-------------|--------------|------------|
| Conv2d | (3, 32, 32) | (12, 28, 28) | 912 |
| MaxPool | (12, 28, 28) | (12, 14, 14) | 0 |
| Conv2d | (12, 14, 14) | (24, 10, 10) | 7,224 |
| MaxPool | (24, 10, 10) | (24, 5, 5) | 0 |
| Flatten | (24, 5, 5) | (600) | 0 |
| Linear | 600 | 120 | 72,120 |
| Linear | 120 | 84 | 10,164 |
| Linear | 84 | 10 | 850 |

## ⚙️ Training Configuration

| Parameter | Value |
|-----------|-------|
| Batch Size | 32 |
| Epochs | 30 |
| Learning Rate | 0.001 |
| Optimizer | SGD (momentum=0.9) |
| Loss Function | CrossEntropyLoss |
| Data Augmentation | Normalization (0.5, 0.5, 0.5) |

## 💾 Persisting Data in Google Drive

For faster subsequent runs, save the dataset to Google Drive:

```python
from google.colab import drive
drive.mount('/content/drive')

!mkdir -p /content/drive/MyDrive/cifar10_data

# First run - downloads to Drive (slow)
datasets.CIFAR10(root='/content/drive/MyDrive/cifar10_data', train=True, download=True)
datasets.CIFAR10(root='/content/drive/MyDrive/cifar10_data', train=False, download=True)

# Future runs - loads from Drive (instant!)
train_data = datasets.CIFAR10(root='/content/drive/MyDrive/cifar10_data', train=True, download=False)
```

## 📝 Usage Examples

### Train from scratch
```python
net = NeuralNetwork().to(device)
# ... training loop ...
torch.save(net.state_dict(), 'trained_model.pth')
```

### Load saved model
```python
net = NeuralNetwork()
net.load_state_dict(torch.load('trained_model.pth'))
net = net.to(device)
```

### Evaluate
```python
net.eval()
with torch.no_grad():
    # ... evaluation code ...
```

## 🎯 Expected Performance

This basic CNN typically achieves:
- **Training accuracy:** ~70-75%
- **Test accuracy:** ~60-65%

For better results, consider:
- Deeper networks (ResNet, VGG)
- Data augmentation (random crops, flips)
- Learning rate scheduling
- Dropout regularization

## 🔧 Troubleshooting

**Download stuck/slow?**
- Use the direct wget link provided above
- Save to Google Drive for persistence

**Out of memory?**
- Reduce `batch_size` (try 16 or 8)
- Use a smaller model

**GPU not available?**
- Check: `torch.cuda.is_available()`
- In Colab: Runtime → Change runtime type → GPU

## 📁 File Structure

```
image/
├── ImgClassificationCNN.ipynb    # Main notebook
├── README-2.md                    # This file
├── data/                          # Dataset folder (auto-created)
│   └── cifar-10-batches-py/
└── trained_model.pth              # Saved model (after training)
```

## 📚 References

- [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)
- [PyTorch Documentation](https://pytorch.org/docs)
- [CNN Explainer](https://poloclub.github.io/cnn-explainer/)

---

**Note:** This notebook uses VS Code connected to Google Colab for GPU acceleration. Make sure to install the Google Colab extension in VS Code.
