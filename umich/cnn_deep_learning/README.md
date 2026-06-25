# CNN Image Classifier

A deep learning pipeline for image classification using PyTorch.

## What it does

- Loads and preprocesses image datasets
- Trains a CNN from scratch with early stopping
- Implements transfer learning with pretrained models
- Evaluates on a challenge test set
- Generates confusion matrices and training plots

## Files

- `train_cnn.py` — CNN training script
- `train_target.py` — transfer learning script
- `train_challenge.py` — challenge evaluation
- `dataset.py` — data loading and augmentation
- `utils.py` — helper functions
- `config.json` — hyperparameter configuration
- `requirements.txt` — dependencies

## Run

```bash
pip install -r requirements.txt
python train_cnn.py
```

## Key concepts

- Convolutional neural networks
- Transfer learning
- Data augmentation
- Early stopping and hyperparameter tuning
