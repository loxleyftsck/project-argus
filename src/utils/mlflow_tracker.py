"""MLflow experiment tracking utilities for Market Anomaly Detection Engine.

Provides wrapper functions for logging experiments, metrics, parameters, and models
with MLflow. Enables comprehensive experiment tracking and model versioning.
"""

import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from typing import Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd
import numpy as np

from src.utils.logger import setup_logger
from src.utils.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_ARTIFACT_LOCATION
)

logger = setup_logger(__name__)


class MLflowTracker:
    """MLflow experiment tracking wrapper.
    
    Simplifies experiment logging for market anomaly detection models.
    Tracks parameters, metrics, artifacts, and models with automatic experiment management.
    
    Examples:
        >>> tracker = MLflowTracker("statistical_baseline")
        >>> with tracker.start_run("zscore_detector"):
        ...     tracker.log_params({"threshold": 3.0, "window": 30})
        ...     tracker.log_metrics({"precision": 0.65, "recall": 0.72})
        ...     tracker.log_model(model, "isolation_forest")
    """
    
    def __init__(self, experiment_name: Optional[str] = None):
        """Initialize MLflow tracker.
        
        Args:
            experiment_name: Name of experiment (default: from config)
        """
        self.experiment_name = experiment_name or MLFLOW_EXPERIMENT_NAME
        
        # Set tracking URI
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        # Create or get experiment
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(
                    self.experiment_name,
                    artifact_location=MLFLOW_ARTIFACT_LOCATION
                )
                logger.info(f"Created MLflow experiment: {self.experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing MLflow experiment: {self.experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(self.experiment_name)
            
        except Exception as e:
            logger.error(f"Error setting up MLflow experiment: {e}")
            raise
    
    def start_run(self, run_name: Optional[str] = None, nested: bool = False):
        """Start MLflow run context manager.
        
        Args:
            run_name: Name for this run
            nested: Whether this is a nested run
        
        Returns:
            MLflow active run context
        
        Examples:
            >>> tracker = MLflowTracker()
            >>> with tracker.start_run("model_training"):
            ...     # Log parameters and metrics
            ...     pass
        """
        return mlflow.start_run(run_name=run_name, nested=nested)
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to active run.
        
        Args:
            params: Dictionary of parameter names and values
        """
        try:
            mlflow.log_params(params)
            logger.debug(f"Logged {len(params)} parameters to MLflow")
        except Exception as e:
            logger.error(f"Error logging parameters: {e}")
    
    def log_param(self, key: str, value: Any) -> None:
        """Log single parameter.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        try:
            mlflow.log_param(key, value)
        except Exception as e:
            logger.error(f"Error logging parameter {key}: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log metrics to active run.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number for time-series metrics
        """
        try:
            mlflow.log_metrics(metrics, step=step)
            logger.debug(f"Logged {len(metrics)} metrics to MLflow")
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
    
    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """Log single metric.
        
        Args:
            key: Metric name
            value: Metric value
            step: Optional step number
        """
        try:
            mlflow.log_metric(key, value, step=step)
        except Exception as e:
            logger.error(f"Error logging metric {key}: {e}")
    
    def log_model(
        self,
        model: Any,
        artifact_path: str,
        registered_model_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log model to MLflow.
        
        Args:
            model: Trained model object
            artifact_path: Path within run to save model
            registered_model_name: Name for model registry (optional)
            **kwargs: Additional arguments for model logging
        """
        try:
            # Detect model type and use appropriate logging
            model_type = type(model).__name__
            
            if "sklearn" in str(type(model).__module__):
                mlflow.sklearn.log_model(
                    model,
                    artifact_path,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            elif "tensorflow" in str(type(model).__module__) or "keras" in str(type(model).__module__):
                mlflow.tensorflow.log_model(
                    model,
                    artifact_path,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            else:
                # Fallback to generic Python model
                mlflow.pyfunc.log_model(
                    artifact_path,
                    python_model=model,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            
            logger.info(f"Logged {model_type} model to MLflow: {artifact_path}")
            
        except Exception as e:
            logger.error(f"Error logging model: {e}")
    
    def log_artifact(self, local_path: Union[str, Path], artifact_path: Optional[str] = None) -> None:
        """Log artifact file or directory.
        
        Args:
            local_path: Path to file or directory to log
            artifact_path: Path within run to save artifact
        """
        try:
            mlflow.log_artifact(str(local_path), artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.error(f"Error logging artifact: {e}")
    
    def log_dict(self, dictionary: Dict, filename: str) -> None:
        """Log dictionary as JSON artifact.
        
        Args:
            dictionary: Dictionary to log
            filename: Artifact filename
        """
        try:
            mlflow.log_dict(dictionary, filename)
            logger.debug(f"Logged dictionary as {filename}")
        except Exception as e:
            logger.error(f"Error logging dictionary: {e}")
    
    def log_figure(self, figure, artifact_file: str) -> None:
        """Log matplotlib/plotly figure.
        
        Args:
            figure: Matplotlib or Plotly figure object
            artifact_file: Filename for saved figure
        """
        try:
            mlflow.log_figure(figure, artifact_file)
            logger.debug(f"Logged figure: {artifact_file}")
        except Exception as e:
            logger.error(f"Error logging figure: {e}")
    
    def log_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: Optional[list] = None
    ) -> None:
        """Log confusion matrix as artifact.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Class labels (optional)
        """
        try:
            from sklearn.metrics import confusion_matrix
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            ax.set_title('Confusion Matrix')
            
            if labels:
                ax.set_xticklabels(labels)
                ax.set_yticklabels(labels)
            
            # Log figure
            mlflow.log_figure(fig, "confusion_matrix.png")
            
            # Also log as dict
            mlflow.log_dict({
                "confusion_matrix": cm.tolist(),
                "labels": labels if labels else []
            }, "confusion_matrix.json")
            
            plt.close(fig)
            logger.info("Logged confusion matrix")
            
        except Exception as e:
            logger.error(f"Error logging confusion matrix: {e}")
    
    def log_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        target_names: Optional[list] = None
    ) -> None:
        """Log classification report as artifact.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            target_names: Class names (optional)
        """
        try:
            from sklearn.metrics import classification_report
            
            report = classification_report(
                y_true,
                y_pred,
                target_names=target_names,
                output_dict=True
            )
            
            mlflow.log_dict(report, "classification_report.json")
            
            # Also log key metrics
            if 'accuracy' in report:
                mlflow.log_metric("accuracy", report['accuracy'])
            if 'weighted avg' in report:
                mlflow.log_metric("precision_weighted", report['weighted avg']['precision'])
                mlflow.log_metric("recall_weighted", report['weighted avg']['recall'])
                mlflow.log_metric("f1_weighted", report['weighted avg']['f1-score'])
            
            logger.info("Logged classification report")
            
        except Exception as e:
            logger.error(f"Error logging classification report: {e}")
    
    def set_tag(self, key: str, value: str) -> None:
        """Set tag for active run.
        
        Args:
            key: Tag key
            value: Tag value
        """
        try:
            mlflow.set_tag(key, value)
        except Exception as e:
            logger.error(f"Error setting tag {key}: {e}")
    
    def set_tags(self, tags: Dict[str, str]) -> None:
        """Set multiple tags for active run.
        
        Args:
            tags: Dictionary of tag keys and values
        """
        try:
            mlflow.set_tags(tags)
            logger.debug(f"Set {len(tags)} tags")
        except Exception as e:
            logger.error(f"Error setting tags: {e}")


# Convenience function for quick experiment logging
def log_experiment(
    run_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    model: Optional[Any] = None,
    artifacts: Optional[Dict[str, Union[str, Path]]] = None,
    tags: Optional[Dict[str, str]] = None
) -> None:
    """Quick experiment logging function.
    
    Args:
        run_name: Name for this run
        params: Parameters to log
        metrics: Metrics to log
        model: Model to log (optional)
        artifacts: Dictionary of artifact names and paths (optional)
        tags: Tags to set (optional)
    
    Examples:
        >>> log_experiment(
        ...     "baseline_model",
        ...     params={"threshold": 3.0},
        ...     metrics={"f1_score": 0.72},
        ...     model=trained_model,
        ...     tags={"model_type": "isolation_forest"}
        ... )
    """
    tracker = MLflowTracker()
    
    with tracker.start_run(run_name):
        # Log parameters
        tracker.log_params(params)
        
        # Log metrics
        tracker.log_metrics(metrics)
        
        # Log model if provided
        if model is not None:
            tracker.log_model(model, "model")
        
        # Log artifacts if provided
        if artifacts:
            for name, path in artifacts.items():
                tracker.log_artifact(path, name)
        
        # Set tags if provided
        if tags:
            tracker.set_tags(tags)
        
        logger.info(f"Logged experiment: {run_name}")
