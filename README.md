# Pipeline de machine learning con Prefect y MLflow

Este proyecto implementa un pipeline de clasificación del conjunto de datos Iris. **Prefect** organiza las etapas y muestra las ejecuciones en su dashboard; **MLflow** registra los parámetros, las métricas y el modelo entrenado.

## Qué hace el pipeline

1. Carga Iris desde `scikit-learn`.
2. Separa características y etiquetas, y crea conjuntos de entrenamiento y prueba estratificados (20 % para prueba).
3. Entrena un `RandomForestClassifier`.
4. Calcula *accuracy* y F1 ponderado.
5. Registra parámetros, métricas y el modelo `IrisRandomForestModel` en MLflow, dentro del experimento `Clasificacion_Iris_Prefect`.

El flujo Prefect se llama **Pipeline Principal de ML (Iris)**. Al ejecutarlo directamente usa 80 estimadores, profundidad máxima 5 y semilla 42. El deployment usa 100 estimadores y profundidad máxima 5, y tiene una programación horaria.

## Estructura

```text
.
├── pyproject.toml                 # Dependencias, configuración del paquete y comandos
├── src/
│   └── prefect_mlflow_demo/
│       ├── main_flow.py            # Flujo Prefect y configuración de conexiones
│       ├── data_pipeline.py        # Carga, separación y preparación de datos
│       ├── model_pipeline.py       # Entrenamiento y registro en MLflow
│       └── deploy.py               # Deployment Prefect con programación horaria
└── services/
    ├── docker-compose.yml          # Servidores locales de Prefect y MLflow
    ├── requirements.txt            # Instalación del proyecto para la opción sin Docker
    ├── README.md                   # Instrucciones detalladas y solución de problemas
    └── mlflow_store/                # Base de datos y artefactos locales de MLflow
```

## Requisitos

- Python 3.12 o posterior.
- Docker Desktop para iniciar ambos servicios con Docker. También es posible iniciarlos localmente con Python, siguiendo la [guía de servicios](services/README.md).

## Instalación y ejecución con Docker

Desde PowerShell, en la raíz del repositorio:

```powershell
docker compose -f .\services\docker-compose.yml up -d
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m prefect_mlflow_demo.main_flow
```

La configuración predeterminada conecta el flujo a Prefect en `http://localhost:4200/api` y a MLflow en `http://localhost:5000`. Si necesitas cambiar los servidores, define las variables `PREFECT_API_URL` y `MLFLOW_TRACKING_URI` antes de ejecutar el flujo.

- **Prefect:** [dashboard](http://localhost:4200/v2/dashboard?rangeType=span&seconds=-86400) y [lista de runs](http://localhost:4200/runs).
- **MLflow:** [experimentos y modelos](http://localhost:5000).

Para registrar e iniciar el deployment programado, ejecuta en otra terminal, desde la raíz del repositorio:

```powershell
.\.venv\Scripts\Activate.ps1
python -m prefect_mlflow_demo.deploy
```

Deja esa terminal abierta para que el proceso del deployment pueda atender las ejecuciones. Para detener los servicios, ejecuta:

```powershell
docker compose -f .\services\docker-compose.yml down
```

Este comando conserva los datos. **No uses `docker compose down -v`** si quieres preservar la base de datos de Prefect y su historial de ejecuciones. Los datos de MLflow se guardan en `services/mlflow_store/`.

## Comandos instalables

Después de `python -m pip install -e .`, también están disponibles:

```powershell
prefect-mlflow-run
prefect-mlflow-deploy
```

Para instrucciones de instalación y ejecución sin Docker, puertos, persistencia de datos y solución de problemas, consulta [services/README.md](services/README.md).
