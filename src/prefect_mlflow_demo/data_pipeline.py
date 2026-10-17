import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
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

@task(name="Cargar Datos Raw", retries=2, retry_delay_seconds=5)
def extract_data_2() -> pd.DataFrame:
    """
    Extrae el conjunto de datos inicial.
    Retries configurados por si falla la conexión de red o fuente de datos.
    """
    datos = pd.read_csv("datos/train.csv", sep=";")
    df = datos
    # Renombrar columnas para consistencia
    return df


@task(name="Preprocesar y Dividir Datos")
def transform_data_2(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Preprocesa el DataFrame de fraude y lo divide en conjuntos de entrenamiento y prueba.
    - Usa 'ID' como índice (no predictor).
    - La variable objetivo es 'Fraude'.
    - Aplica OneHotEncoder a variables categóricas.
    """
    # Usar ID como índice
    df = df.set_index("ID")

    # Separar variables predictoras y objetivo
    X = df.drop(columns=["Fraude"]).copy()
    y = df["Fraude"].copy()
    

    # Identificar columnas categóricas
    cat_cols = X.select_dtypes(include=["object"]).columns

    # OneHotEncoder: convierte categóricas en variables binarias
    encoder = OneHotEncoder(drop="first", sparse_output=False)
    X_encoded = encoder.fit_transform(X[cat_cols])

    # Crear DataFrame con columnas codificadas
    encoded_df = pd.DataFrame(
        X_encoded,
        columns=encoder.get_feature_names_out(cat_cols),
        index=X.index
    )

    # Reemplazar categóricas originales por las codificadas
    X = pd.concat([X.drop(columns=cat_cols), encoded_df], axis=1)

    # División estratificada para balancear clases
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    return X_train, X_test, y_train, y_test
