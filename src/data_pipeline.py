import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from prefect import task

@task(name="Cargar Datos Raw", retries=2, retry_delay_seconds=5)
def extract_data() -> pd.DataFrame:
    """
    Extrae el conjunto de datos inicial.
    Retries configurados por si falla la conexión de red o fuente de datos.
    """
    iris = load_iris(as_frame=True)
    df = iris.frame
    # Renombrar columnas para consistencia
    df.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df.columns]
    return df

@task(name="Preprocesar y Dividir Datos")
def transform_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Divide el DataFrame en conjuntos de entrenamiento y prueba.
    """
    X = df.drop(columns=["target"])
    y = df["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test