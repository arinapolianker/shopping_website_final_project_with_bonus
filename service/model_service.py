import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, recall_score, f1_score


MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "optimal_rf_model.joblib"


def train_and_save_model():
    df = pd.read_csv("resources/csv/user_churn_data.csv")
    X = df.drop('churned', axis=1)
    y = df['churned']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    param_grid = {
        'n_estimators': [20, 65, 100, 158, 200],
        'max_features': [2, 5, 8, 11, 15],
        'bootstrap': [True, False],
        'oob_score': [True, False]
    }

    rf_model = RandomForestClassifier()
    rf_grid_search = GridSearchCV(rf_model, param_grid)
    rf_grid_search.fit(X_train, y_train)

    optimal_rf_model = RandomForestClassifier(max_features=5, n_estimators=20, bootstrap=True, oob_score=True)
    optimal_rf_model.fit(X_train, y_train)
    y_pred = optimal_rf_model.predict(X_test)
    model = optimal_rf_model
    model.fit(X, y)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return model, y_test, y_pred


def get_or_train_model():
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        df = pd.read_csv("resources/csv/user_churn_data.csv")
        X = df.drop("churned", axis=1)
        y = df["churned"]

        _, X_test, _, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        y_pred = model.predict(X_test)
        return model, y_test, y_pred
    else:
        return train_and_save_model()


def predict_user_churn(user_features: dict) -> int:
    model, _, _ = get_or_train_model()
    df = pd.read_csv("resources/csv/user_churn_data.csv")
    required_features = df.drop('churned', axis=1).columns

    for feature in required_features:
        if feature not in user_features:
            user_features[feature] = 0

    features_df = pd.DataFrame([user_features])[required_features]
    prediction = model.predict(features_df)
    return int(prediction[0])


def get_performance_metrics():
    model, y_test, y_pred = get_or_train_model()

    performance_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True)
    }

    return performance_metrics
