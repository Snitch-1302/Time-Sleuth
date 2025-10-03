import pandas as pd
from sklearn.cluster import DBSCAN

def cluster_events(df, eps_seconds=120, min_samples=2):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["ts_unix"] = df["timestamp"].astype("int64") // 1_000_000_000

    clustering = DBSCAN(eps=eps_seconds, min_samples=min_samples).fit(df[["ts_unix"]])
    df["cluster"] = clustering.labels_
    return df
