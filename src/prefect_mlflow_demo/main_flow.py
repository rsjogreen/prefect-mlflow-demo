import os
import sys

# Agregar 'src' al path dinámicamente para soportar la ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("PREFECT_API_URL", "http://localhost:4200/api")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import mlflow
from prefect import flow, get_run_logger

# Se elimina el punto (.) para usar la importación absoluta desde el paquete
from prefect_mlflow_demo.data_pipeline import extract_data, transform_data
from prefect_mlflow_demo.model_pipeline import train_and_log_model


@flow(name="Pipeline Principal de ML (Iris)")
def main_ml_pipeline(n_estimators: int = 80, max_depth: int = 5):
    """
    Flujo principal que coordina la extracción de datos, 
    transformación y entrenamiento del modelo con logueo en MLflow.
    """
    logger = get_run_logger()
    
    # Configurar la URI del servidor de MLflow
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    logger.info(f"MLflow Tracking URI configurada en: {mlflow_uri}")

    # 1. Pipeline de Datos
    raw_df = extract_data()
    X_train, X_test, y_train, y_test = transform_data(raw_df)

    # 2. Pipeline de Modelo
    metrics = train_and_log_model(
        X_train=X_train, 
        X_test=X_test, 
        y_train=y_train, 
        y_test=y_test,
        n_estimators=n_estimators,
        max_depth=max_depth
    )

    logger.info(f"Flujo completado. Resultados finales: {metrics}")


def main() -> None:
    main_ml_pipeline()


if __name__ == "__main__":
    main()