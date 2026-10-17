import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from prefect import task, get_run_logger


@task(name="Entrenar y Registrar Modelo en MLflow")
def train_and_log_model(X_train, X_test, y_train, y_test, n_estimators: int, max_depth: int):
    """
    Entrena un RandomForestClassifier y registra hiperparámetros,
    métricas y artefactos directamente en el servidor de MLflow.
    """
    logger = get_run_logger()
    logger.info(f"Iniciando entrenamiento: n_estimators={n_estimators}, max_depth={max_depth}")

    # Iniciar experimento en MLflow
    mlflow.set_experiment("Clasificacion_fraude_random_forest")

    with mlflow.start_run(run_name=f"RF_depth_{max_depth}_trees_{n_estimators}"):
        # 1. Definir y entrenar el modelo
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )
        model.fit(X_train, y_train)

        # 2. Predecir y evaluar
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

        # 3. Registrar hiperparámetros en MLflow
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "model_type": "RandomForestClassifier"
        })

        # 4. Registrar métricas en MLflow
        mlflow.log_metrics({
            "accuracy": acc,
            "f1_score": f1,
            "roc_auc": auc
        })

        # 5. Guardar el modelo en el Registry de MLflow
        mlflow.sklearn.log_model(
            sk_model=model,
            name="fraude_rf_model",
            registered_model_name="Fraude_RandomForestModel",
            pyfunc_predict_fn="predict",
            # Permite a skops aceptar las estructuras de árbol nativas de scikit-learn
            skops_trusted_types=["sklearn.tree._tree.Tree"]
        )

        logger.info(f"Modelo registrado exitosamente con Accuracy: {acc:.4f}")
        return {"accuracy": acc, "f1": f1, "roc_auc": auc}