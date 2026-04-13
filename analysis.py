
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_anomalies(df, col):
    model = IsolationForest(contamination=0.05, random_state=42)

    df = df.copy()
    df["anomaly"] = model.fit_predict(df[[col]])

    return df[df["anomaly"] == -1]


def get_stats(df, col):
    mean = df[col].mean()
    std = df[col].std()

    df["z"] = (df[col] - mean) / std
    outliers = df[df["z"].abs() > 2]

    hhi = ((df[col] / df[col].sum()) ** 2).sum()

    return outliers, hhi
