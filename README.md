# Prefect + MLflow Demo

Pipeline de clasificación Iris: Prefect coordina la carga, transformación y entrenamiento del modelo, mientras MLflow registra sus métricas y artefactos.

## Estructura

```text
src/prefect_mlflow_demo/  Código del paquete y del flujo
services/                 Docker Compose, guía de servicios y datos locales de MLflow
pyproject.toml             Dependencias, metadatos del paquete y comandos
```

## Iniciar servicios y ejecutar el flujo

Requiere Python 3.12 y Docker Desktop. Desde la raíz del repositorio:

```powershell
docker compose -f .\services\docker-compose.yml up -d
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
$env:PREFECT_API_URL = "http://localhost:4200/api"
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
python -m prefect_mlflow_demo.main_flow
```

El run aparece en el [dashboard de Prefect](http://localhost:4200/v2/dashboard?rangeType=span&seconds=-86400), y las métricas y el modelo quedan registrados en MLflow (`http://localhost:5000`). Para registrar el deployment y atender las ejecuciones programadas, usa `python -m prefect_mlflow_demo.deploy` en una terminal que permanezca abierta.

También se pueden ejecutar los servicios sin Docker. Consulta [la guía de servicios](services/README.md) para ambas opciones, solución de problemas y comandos detallados.
