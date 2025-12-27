# MLflow Experiment Tracking Guide

## Market Anomaly Detection Engine

**MLflow Version:** 2.9.2

---

## 🎯 What is MLflow?

MLflow is an open-source platform for managing the ML lifecycle, including:

- **Tracking**: Log parameters, metrics, code versions, and artifacts
- **Models**: Package and deploy models from any ML library
- **Registry**: Centralized model store with versioning
- **Projects**: Reproducible runs with dependencies

---

## 🚀 Quick Start

### 1. Start MLflow UI

```bash
# Start MLflow tracking server
mlflow ui --port 5000

# Access at: http://localhost:5000
```

### 2. Basic Usage

```python
from src.utils.mlflow_tracker import MLflowTracker

# Initialize tracker
tracker = MLflowTracker("statistical_baseline")

# Start run
with tracker.start_run("zscore_detector"):
    # Log parameters
    tracker.log_params({
        "threshold": 3.0,
        "window": 30,
        "method": "zscore"
    })
    
    # Train model
    model = train_model()
    
    # Log metrics
    tracker.log_metrics({
        "precision": 0.65,
        "recall": 0.72,
        "f1_score": 0.68
    })
    
    # Log model
    tracker.log_model(model, "isolation_forest")
```

---

## 📊 What We'll Track

### Week 1: Statistical Baseline

**Experiment:** `statistical_methods`

**Parameters:**

- `volume_threshold`: 3.0
- `price_change_threshold`: 10.0
- `window_size`: 30
- `method`: "zscore" / "volatility" / "correlation"

**Metrics:**

- `precision`, `recall`, `f1_score`
- `false_positive_rate`
- `detection_latency_ms`

**Artifacts:**

- Feature importance plots
- Confusion matrix
- Sample detections CSV

### Week 2: ML Models

**Experiments:**

1. `isolation_forest`
2. `autoencoder`
3. `lstm_detector`
4. `ensemble`

**Parameters (Isolation Forest):**

- `contamination`: 0.05
- `n_estimators`: 100
- `max_samples`: 256
- `random_state`: 42

**Parameters (Autoencoder):**

- `encoding_dim`: 32
- `learning_rate`: 0.001
- `batch_size`: 256
- `epochs`: 100

**Parameters (LSTM):**

- `units`: 64
- `seq_length`: 30
- `dropout`: 0.2
- `learning_rate`: 0.001

**Metrics:**

- Model-specific performance
- Training time
- Inference latency
- Memory usage

**Artifacts:**

- Trained models (.pkl, .h5)
- Training curves
- SHAP importance plots
- Sample predictions

### Week 3: Backtesting

**Experiment:** `historical_backtesting`

**Parameters:**

- `test_stocks`: ["GOTO.JK", "BUMI.JK", ...]
- `date_range`: "2023-01-01 to 2024-12-31"
- `models`: ["statistical", "iso_forest", "ensemble"]

**Metrics:**

- `detection_rate`: % of cases detected
- `avg_early_warning_days`: How many days before event
- `backtest_accuracy`

**Artifacts:**

- Case study reports
- Timeline visualizations
- Performance comparison tables

---

## 🎨 MLflow UI Overview

### Experiments View

```
market-anomaly-detection/
├── statistical_methods/
│   ├── zscore_detector (Run 1)
│   ├── volatility_detector (Run 2)
│   └── correlation_detector (Run 3)
├── isolation_forest/
│   ├── contamination_0.03 (Run 1)
│   ├── contamination_0.05 (Run 2)
│   └── contamination_0.10 (Run 3)
└── ensemble/
    └── final_model (Run 1)
```

### Run Comparison

- Compare parameters side-by-side
- Plot metrics across runs
- Identify best performing configurations

### Model Registry

```
Models/
├── IsolationForestDetector v1 (Production)
├── IsolationForestDetector v2 (Staging)
├── AutoencoderDetector v1 (Staging)
└── EnsembleDetector v1 (None)
```

---

## 💡 Best Practices

### 1. Naming Conventions

**Experiments:**

- Use descriptive names: `statistical_baseline`, `isolation_forest_tuning`
- Group related runs under same experiment

**Runs:**

- Include key parameters: `zscore_threshold_3.0_window_30`
- Add timestamps if needed: `ensemble_2024-12-27_final`

### 2. What to Log

**Always log:**

- ✅ All hyperparameters used
- ✅ Final performance metrics (precision, recall, F1)
- ✅ Training/inference time
- ✅ Model artifacts

**Good to log:**

- ✅ Intermediate metrics (per epoch)
- ✅ Feature importance
- ✅ Sample predictions
- ✅ Data quality stats

**Don't log:**

- ❌ Large raw datasets (use references instead)
- ❌ Redundant parameters
- ❌ Temporary debug info

### 3. Tagging Strategy

**Use tags for:**

- `developer`: "Your Name"
- `model_type`: "isolation_forest"
- `dataset`: "IDX_2023_2024"
- `status`: "baseline" / "tuning" / "final"
- `purpose`: "experiment" / "production"

### 4. Model Versioning

```python
# Register model to registry
tracker.log_model(
    model,
    "model",
    registered_model_name="AnomalyDetector"
)

# Later: Load specific version
model = mlflow.sklearn.load_model("models:/AnomalyDetector/1")
```

---

## 📈 Portfolio Value

### What Recruiters Will See

1. **MLflow UI Screenshots** showing:
   - Multiple experiment runs
   - Systematic hyperparameter tuning
   - Model performance progression
   - Professional experiment tracking

2. **Evidence of Scientific Rigor:**
   - Controlled experiments (change one variable at a time)
   - Reproducible results (logged parameters + random seeds)
   - Systematic improvement (metrics trending upward)

3. **Production Mindset:**
   - Model registry usage
   - Version control for models
   - Artifact management

### Interview Talking Points

> *"I used MLflow to track over 50+ experiment runs during model development. This allowed me to systematically tune hyperparameters, compare different architectures (Isolation Forest vs Autoencoder vs LSTM), and maintain full reproducibility. I registered the best performing ensemble model (F1=0.75) to production staging."*

---

## 🔧 Common Commands

```bash
# Start UI
mlflow ui --port 5000

# Start with backend store (PostgreSQL)
mlflow server \
    --backend-store-uri postgresql://user:pass@localhost/mlflow \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000

# Search runs via CLI
mlflow runs search --experiment-id 0

# List experiments
mlflow experiments search

# Delete run
mlflow runs delete --run-id <run_id>
```

---

## 🎯 Integration with Our System

### Training Script Pattern

```python
from src.utils.mlflow_tracker import MLflowTracker

def train_isolation_forest(params):
    tracker = MLflowTracker("isolation_forest")
    
    with tracker.start_run(f"contamination_{params['contamination']}"):
        # Log parameters
        tracker.log_params(params)
        tracker.set_tags({
            "model_type": "isolation_forest",
            "dataset": "IDX_2023_2024"
        })
        
        # Train
        model = IsolationForest(**params)
        model.fit(X_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        metrics = calculate_metrics(y_test, y_pred)
        
        # Log results
        tracker.log_metrics(metrics)
        tracker.log_confusion_matrix(y_test, y_pred)
        tracker.log_model(model, "model", registered_model_name="IsolationForestDetector")
        
        return model, metrics
```

---

**Next:** Install MLflow and start tracking your first experiment! 🚀

```bash
pip install mlflow==2.9.2
mlflow ui --port 5000
```
