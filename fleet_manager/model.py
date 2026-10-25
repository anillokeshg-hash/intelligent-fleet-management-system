"""AI model that predicts the maintenance risk of a vehicle."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

FEATURES = ["km_since_service", "engine_temp", "tyre_pressure", "battery_voltage", "fuel_efficiency"]


def make_training_data(n=4000, seed=1):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "km_since_service": rng.uniform(0, 16000, n),
        "engine_temp": rng.normal(92, 10, n),
        "tyre_pressure": rng.normal(31, 3, n),
        "battery_voltage": rng.normal(12.2, 0.5, n),
        "fuel_efficiency": rng.normal(10, 3, n),
    })
    # risk score: higher means the vehicle is more likely to need maintenance
    score = (
        (df["km_since_service"] / 10000)
        + np.clip((df["engine_temp"] - 95) / 10, 0, None)
        + np.clip((29 - df["tyre_pressure"]) / 3, 0, None)
        + np.clip((11.9 - df["battery_voltage"]) / 0.5, 0, None)
        + np.clip((7 - df["fuel_efficiency"]) / 3, 0, None)
        + rng.normal(0, 0.15, n)
    )
    df["needs_maintenance"] = (score > 1.0).astype(int)
    return df


def train_model(verbose=True):
    df = make_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], df["needs_maintenance"], test_size=0.2, random_state=1,
        stratify=df["needs_maintenance"],
    )
    model = RandomForestClassifier(n_estimators=100, random_state=1)
    model.fit(X_train, y_train)
    if verbose:
        acc = accuracy_score(y_test, model.predict(X_test))
        print(f"Maintenance model accuracy: {acc:.3f}")
    return model


def maintenance_risk(model, telemetry):
    """Return the probability (0-1) that this vehicle needs maintenance."""
    X = pd.DataFrame([[telemetry[f] for f in FEATURES]], columns=FEATURES)
    return round(float(model.predict_proba(X)[0][1]), 3)


if __name__ == "__main__":
    train_model()
