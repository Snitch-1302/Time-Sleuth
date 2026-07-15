import pytsk3
import pandas as pd

# Works whether this file is run directly (python extract_events.py from
# inside scripts/) or as a package module (python -m scripts.extract_events
# from the repo root) -- scripts/ has an __init__.py, so it's a real
# package, and a bare `from utils import ...` only resolves in the first
# case.
try:
    from scripts.utils import write_csv, normalize_timestamp
except ImportError:
    from utils import write_csv, normalize_timestamp

IMAGE_PATH = "data/m57-jean.dd"
OUTPUT_PATH = "data/raw_timeline.csv"


def extract_filesystem_events(image_path):
    img = pytsk3.Img_Info(image_path)
    fs = pytsk3.FS_Info(img)
    directory = fs.open_dir("/")
    events = []
    for entry in directory:
        if not hasattr(entry.info, "meta") or entry.info.meta is None:
            continue
        name = entry.info.name.name.decode("utf-8", "ignore")
        if name in [".", ".."]:
            continue
        mtime = entry.info.meta.mtime
        if mtime != 0:
            events.append({
                "timestamp": normalize_timestamp(mtime),
                "source": "filesystem",
                "action": "file_entry",
                "artifact": name,
                "details": f"Filesystem event on {name} (action=file_entry)"
            })
    return events


if __name__ == "__main__":
    events = extract_filesystem_events(IMAGE_PATH)
    write_csv(events, OUTPUT_PATH)
    print(f"[+] Extracted {len(events)} events to {OUTPUT_PATH}")
