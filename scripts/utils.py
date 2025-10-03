import pandas as pd

def write_csv(events, path):
    df = pd.DataFrame(events)
    df.to_csv(path, index=False)

def normalize_timestamp(ts):
    # Add normalization if needed
    return str(ts)
