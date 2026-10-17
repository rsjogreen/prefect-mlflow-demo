# Importamos las librerías necesarias
from prefect import flow, task              # Prefect para definir tareas y flujos
import mlflow                               # MLflow para registrar modelos y métricas
from sklearn.datasets import load_iris      # Dataset de ejemplo (Iris)
from sklearn.linear_model import LogisticRegression  # Modelo de regresión logística

# Definimos una tarea de Prefect para entrenar el modelo
@task
def train_model():
    # Cargamos el dataset Iris (X = características, y = etiquetas)
    X, y = load_iris(return_X_y=True)
    
    # Creamos un modelo de regresión logística con un número máximo de iteraciones
    model = LogisticRegression(max_iter=200)
    
    # Entrenamos el modelo con los datos
    model.fit(X, y)
    
    # Retornamos el modelo entrenado para usarlo en otras tareas
    return model

# Definimos otra tarea de Prefect para registrar el modelo en MLflow
@task
def log_model(model):
    # Registramos el modelo entrenado en MLflow bajo el nombre "iris-logreg"
    mlflow.sklearn.log_model(model, "iris-logreg")

# Definimos el flujo principal de Prefect
@flow
def main_flow():
    # Ejecutamos la tarea de entrenamiento
    model = train_model()
    
    # Ejecutamos la tarea de registro en MLflow
    log_model(model)

# Punto de entrada del script
if __name__ == "__main__":
    # Llamamos al flujo principal
    main_flow()
