# Servicios: MLflow y Prefect

Esta carpeta levanta **MLflow** (tracking y UI de experimentos) y **Prefect** (orquestación de flows y su UI) para este proyecto. El paquete y sus dependencias se definen en `../pyproject.toml`.

Hay dos formas de levantarlos. Usa una de las dos, no ambas a la vez (comparten puertos).

| Opción | Cuándo usarla |
|---|---|
| **A. Docker Compose** | Lo más sencillo si Docker Desktop funciona. Todo se ejecuta en contenedores. |
| **B. Sin Docker** | Si no hay Docker o no quieres usarlo. Se instalan MLflow y Prefect en un entorno de Python. |

## Estructura

```
services/
├── docker-compose.yml   # opción A: MLflow y Prefect en contenedores
├── requirements.txt     # instala el proyecto y sus dependencias desde pyproject.toml
├── mlflow_store/        # base SQLite y artefactos locales de MLflow; conserva los resultados
├── CLAUDE.md            # guía para asistentes de IA que trabajen en esta carpeta
└── README.md
```

## Versiones

| Componente | Versión | Dónde se fija |
|---|---|---|
| MLflow | 3.17.0 | `docker-compose.yml` y `../pyproject.toml` |
| Prefect | 3.8.8 | `docker-compose.yml` y `../pyproject.toml` |

## Puertos y UIs

| Puerto | Servicio | Interfaz en el navegador | API |
|---|---|---|---|
| 5000 | MLflow | http://localhost:5000 | http://localhost:5000/health |
| 4200 | Prefect | http://localhost:4200 | http://localhost:4200/api/health |

Si cambias un puerto, actualiza esta tabla, `docker-compose.yml` y las variables de los flows.

## Opción A: Docker Compose

Requisito: Docker Desktop abierto.

```powershell
cd services
docker compose up -d     # arranca MLflow y Prefect
docker compose down      # los para; los datos se conservan
```

Los datos se guardan en `mlflow_store/` (MLflow) y en el volumen `prefect_data` (Prefect). `docker compose down -v` borra el volumen de Prefect: no lo uses si quieres conservar sus runs.

## Opción B: sin Docker

Requisito: Python 3.12. Desde `services/`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow_store/mlflow.db --artifacts-destination mlflow_store/artifacts --serve-artifacts
```

En otra terminal, en `services/` con el mismo entorno activado:

```powershell
prefect server start --host 127.0.0.1 --port 4200
```

Deja las dos terminales abiertas mientras uses los servicios.

Esta opción usa la misma base de datos de MLflow (`mlflow_store/mlflow.db`) que la opción A, así que los runs se ven en ambas. Conserva la base y los artefactos existentes. La base de Prefect queda en `~/.prefect` del usuario, no en el proyecto.

## Comprobar en el navegador

1. Levanta los servicios con la opción A o B.
2. Abre http://localhost:5000: debe cargar la UI de MLflow.
3. Abre http://localhost:4200: debe cargar la UI de Prefect.

Para registrar una ejecución inmediatamente y verla en el dashboard de Prefect, primero instala el proyecto (`pip install -e .` desde la raíz o `pip install -r requirements.txt` desde `services/`) y luego, desde la raíz, ejecuta:

```powershell
$env:PREFECT_API_URL = "http://localhost:4200/api"
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
python -m prefect_mlflow_demo.main_flow
```

El run aparece en el dashboard de Prefect (http://localhost:4200/v2/dashboard?rangeType=span&seconds=-86400) y en http://localhost:4200/runs. El experimento y las métricas aparecen en MLflow en http://localhost:5000.

El flujo configura `http://localhost:4200/api` como servidor de Prefect por defecto; la variable anterior se puede omitir si usas ese servidor local. Si quieres que se cree el deployment y quede un proceso escuchando las ejecuciones programadas, desde la raíz ejecuta:

```powershell
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
python -m prefect_mlflow_demo.deploy
```

`deploy.py` registra el deployment `iris-mlflow-deployment` y lo programa cada hora. Mantén esa terminal abierta para que el proceso atienda las ejecuciones; el run inicial se puede crear con el comando `main_flow.py` anterior.

## Solución de problemas

- **`Cannot connect to the Docker daemon` o `dockerDesktopLinuxEngine`:** Docker Desktop no está abierto. Ábrelo y espera a que esté en marcha.
- **El puerto 5000 o 4200 ya está en uso:** otro programa lo ocupa, o tienes las dos opciones levantadas a la vez. Para una de ellas antes de arrancar la otra.
- **La UI de Prefect no muestra runs:** verifica que el servidor esté levantado en `http://localhost:4200/api/health`, instala el proyecto y ejecuta el flujo (`python -m prefect_mlflow_demo.main_flow`) o el deployment (`python -m prefect_mlflow_demo.deploy`).
- **La UI de MLflow no muestra experimentos:** comprueba que MLflow esté activo en `http://localhost:5000` y que el flow use `MLFLOW_TRACKING_URI=http://localhost:5000` (es el valor por defecto).