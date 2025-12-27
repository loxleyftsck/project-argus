"""MLflow Demo Script - Test Experiment Tracking

This script demonstrates MLflow integration by creating sample experiments
with different model configurations. Use this to verify MLflow setup.
"""

import sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.mlflow_tracker import MLflowTracker
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_sample_data(n_samples=1000, contamination=0.05):
    """Generate synthetic anomaly detection data.
    
    Args:
        n_samples: Number of samples
        contamination: Proportion of anomalies
    
    Returns:
        X: Feature matrix
        y: True labels (1=normal, -1=anomaly)
    """
    np.random.seed(42)
    
    # Normal data
    n_normal = int(n_samples * (1 - contamination))
    X_normal = np.random.randn(n_normal, 6) * 0.5
    
    # Anomalous data (outliers)
    n_anomaly = n_samples - n_normal
    X_anomaly = np.random.randn(n_anomaly, 6) * 3.0 + 5
    
    # Combine
    X = np.vstack([X_normal, X_anomaly])
    y = np.hstack([np.ones(n_normal), -np.ones(n_anomaly)])
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X = X[indices]
    y = y[indices]
    
    return X, y


def run_experiment(contamination, n_estimators, max_samples):
    """Run single experiment with given parameters.
    
    Args:
        contamination: Contamination parameter for Isolation Forest
        n_estimators: Number of trees
        max_samples: Number of samples per tree
    
    Returns:
        metrics: Dictionary of performance metrics
    """
    logger.info(f"Running experiment: contamination={contamination}, n_estimators={n_estimators}")
    
    # Generate data
    X_train, y_train = generate_sample_data(1000, contamination=contamination)
    X_test, y_test = generate_sample_data(300, contamination=contamination)
    
    # Train model
    model = IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        max_samples=max_samples,
        random_state=42
    )
    model.fit(X_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    # Convert to binary (1=normal, 0=anomaly) for sklearn metrics
    y_test_binary = (y_test == 1).astype(int)
    y_pred_binary = (y_pred == 1).astype(int)
    
    metrics = {
        'precision': float(precision_score(y_test_binary, y_pred_binary, zero_division=0)),
        'recall': float(recall_score(y_test_binary, y_pred_binary, zero_division=0)),
        'f1_score': float(f1_score(y_test_binary, y_pred_binary, zero_division=0)),
    }
    
    # Calculate anomaly-specific metrics
    cm = confusion_matrix(y_test_binary, y_pred_binary)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        metrics['true_positives'] = int(tp)
        metrics['false_positives'] = int(fp)
        metrics['true_negatives'] = int(tn)
        metrics['false_negatives'] = int(fn)
        metrics['false_positive_rate'] = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    
    logger.info(f"Results: F1={metrics['f1_score']:.3f}, Precision={metrics['precision']:.3f}")
    
    return model, metrics, y_test, y_pred


def main():
    """Run demo MLflow experiments."""
    
    logger.info("=" * 80)
    logger.info("MLFLOW DEMO - Testing Experiment Tracking")
    logger.info("=" * 80)
    
    # Initialize tracker
    tracker = MLflowTracker("demo_isolation_forest")
    
    # Experiment configurations
    configs = [
        {"contamination": 0.03, "n_estimators": 100, "max_samples": 256},
        {"contamination": 0.05, "n_estimators": 100, "max_samples": 256},
        {"contamination": 0.10, "n_estimators": 100, "max_samples": 256},
        {"contamination": 0.05, "n_estimators": 50, "max_samples": 256},
        {"contamination": 0.05, "n_estimators": 200, "max_samples": 256},
    ]
    
    logger.info(f"Running {len(configs)} experiments...")
    
    for i, config in enumerate(configs, 1):
        run_name = f"contamination_{config['contamination']}_trees_{config['n_estimators']}"
        
        logger.info(f"\nExperiment {i}/{len(configs)}: {run_name}")
        
        with tracker.start_run(run_name):
            # Set tags
            tracker.set_tags({
                "model_type": "isolation_forest",
                "dataset": "synthetic_demo",
                "purpose": "mlflow_demo",
                "developer": "market_anomaly_team"
            })
            
            # Log parameters
            tracker.log_params(config)
            tracker.log_param("random_state", 42)
            tracker.log_param("n_features", 6)
            
            # Run experiment
            model, metrics, y_test, y_pred = run_experiment(**config)
            
            # Log metrics
            tracker.log_metrics(metrics)
            
            # Log confusion matrix
            y_test_binary = (y_test == 1).astype(int)
            y_pred_binary = (y_pred == 1).astype(int)
            tracker.log_confusion_matrix(y_test_binary, y_pred_binary, labels=[0, 1])
            
            # Log model
            tracker.log_model(
                model,
                "model",
                registered_model_name="DemoIsolationForest"
            )
            
            logger.info(f"✓ Logged to MLflow: {run_name}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ DEMO COMPLETE!")
    logger.info("=" * 80)
    logger.info("\nStart MLflow UI to view results:")
    logger.info("  Windows: .\\start_mlflow.ps1")
    logger.info("  Linux/Mac: ./start_mlflow.sh")
    logger.info("\nThen open: http://localhost:5000")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
