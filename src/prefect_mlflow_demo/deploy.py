import os

# Conectar explícitamente al servidor de Prefect y silenciar logs de Git
os.environ.setdefault("PREFECT_API_URL", "http://localhost:4200/api")
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# Importar el flujo principal
from .main_flow import main_ml_pipeline


def main() -> None:
    # Servir el flujo en el servidor de Prefect
    # Esto registra el Deployment en la UI y deja un worker escuchando ejecuciones
    main_ml_pipeline.serve(
        name="iris-mlflow-deployment",
        tags=["machine-learning", "iris", "mlflow"],
        parameters={"n_estimators": 100, "max_depth": 5},
        cron="0 * * * *",  # Opcional: Programa la ejecución cada hora
    )


if __name__ == "__main__":
    main()