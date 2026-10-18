# Pipeline de clasificación de fraude con Prefect y MLflow

Este proyecto entrena y evalúa modelos de clasificación para detectar transacciones fraudulentas usando los datos de `datos/train.csv`. **Prefect** organiza las etapas del pipeline y registra sus ejecuciones; **MLflow** registra los parámetros, las métricas y los modelos entrenados para facilitar su seguimiento y comparación.

## Qué hace el experimento

El flujo principal, **Pipeline Principal de ML Fraude**, realiza estos pasos:

1. Lee `datos/train.csv` como un CSV separado por punto y coma. El archivo `datos/test.csv` está en el repositorio, pero actualmente el flujo no lo utiliza.
2. Usa `Fraude` como variable objetivo y excluye `ID` de las variables predictoras.
3. Convierte las variables categóricas a columnas numéricas con `OneHotEncoder` y divide los datos en conjuntos de entrenamiento (80 %) y prueba (20 %), con división estratificada y semilla 42.
4. Entrena un `RandomForestClassifier` con los parámetros indicados y evalúa las predicciones con *accuracy*, F1 ponderado y ROC AUC.
5. Registra parámetros, métricas y el modelo en el experimento `Clasificacion_fraude_random_forest` de MLflow. El modelo registrado se llama `Fraude_RandomForestModel`.
6. Ejecuta una búsqueda de hiperparámetros sobre 12 combinaciones:
   - `n_estimators`: 100, 300 y 500.
   - `max_depth`: 5, 15, 35 y `None`.

Al ejecutar el flujo directamente, primero se realiza un entrenamiento base con 300 árboles y profundidad máxima 15; luego se evalúan las 12 combinaciones de la búsqueda. Cada entrenamiento se registra como una ejecución de MLflow.

El deployment definido en `deploy.py` usa 100 árboles y profundidad máxima 5, y programa el flujo cada hora (`0 * * * *`). El proceso que sirve el deployment debe permanecer activo para atender las ejecuciones programadas.

## Estructura

```text
.
├── datos/
│   ├── train.csv                  # Datos usados actualmente por el pipeline
│   └── test.csv                   # Presente, pero no usado por el flujo actual
├── pyproject.toml                 # Dependencias, configuración del paquete y comandos
├── src/
│   └── prefect_mlflow_demo/
│       ├── main_flow.py           # Flujo Prefect y configuración de conexiones
│       ├── data_pipeline.py       # Carga, codificación y división de datos
│       ├── model_pipeline.py      # Entrenamiento, evaluación y registro en MLflow
│       └── deploy.py              # Deployment Prefect con programación horaria
└── services/
    ├── docker-compose.yml         # Servidores locales de Prefect y MLflow
    ├── requirements.txt           # Instalación del proyecto para la opción sin Docker
    ├── README.md                  # Instrucciones detalladas y solución de problemas
    └── mlflow_store/              # Base de datos y artefactos locales de MLflow
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
