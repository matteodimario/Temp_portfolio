# ICU Mortality Prediction

A machine learning pipeline to predict patient mortality from ICU time-series data.

## What it does

- Extracts feature vectors from patient measurements (static + time-series)
- Imputes missing values with population means
- Trains logistic regression and kernel ridge regression classifiers
- Evaluates with ROC curves, AUC, accuracy, precision, recall
- Uses stratified k-fold cross-validation

## Files

- `project1.py` — main pipeline (feature extraction, imputation, training, evaluation)
- `helper.py` — utility functions
- `config.yaml` — feature and seed configuration
- `data/` — patient datasets

## Run

```bash
python project1.py
```

## Key concepts

- Feature engineering from medical time-series
- Missing value imputation
- Logistic regression and kernel methods
- Cross-validation and ROC analysis
