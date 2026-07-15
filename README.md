# ⏳ TimeSleuth: Forensic Timeline Analysis

TimeSleuth is a digital forensics tool that extracts, abstracts, and
visualizes system events from disk images — helping reconstruct timelines
of user activity, spot suspicious events, and detect anomalies.

## Pipeline

Disk image (.dd)
└── extract_events.py   (pytsk3 filesystem parsing)
└── raw_timeline.csv
└── abstraction.py   (maps raw actions → high-level categories)
└── abstracted_timeline.csv
└── app.py   (interactive Dash timeline UI)

## Features

- Extracts real filesystem artifacts from disk images using `pytsk3` (The Sleuth Kit)
- Abstracts raw low-level events (e.g. `file_encrypt`, `key_modify`) into
  high-level categories (File System Activity, Registry Change, Network
  Activity, etc.)
- Interactive forensic timeline visualization (Dash + Plotly)
- Event filtering by type, time-range slider, and optional DBSCAN-based
  clustering of nearby events
- Per-event inspection panel with a basic threat-level heuristic

## Tech stack

- Python 3.10+
- `pytsk3` — filesystem/disk image parsing (The Sleuth Kit bindings)
- `pandas` — data handling
- `plotly` / `dash` — interactive visualization and UI
- `scikit-learn` — DBSCAN event clustering

## Project structure

TimeSleuth/
├── app/
│   ├── init.py
│   ├── app.py             # Dash app: layout, callbacks, visualization
│   └── callbacks.py        # (reserved for callback separation as the app grows)
├── data/
│   ├── raw_timeline.csv       # sample raw event data
│   └── abstracted_timeline.csv # sample abstracted event data
├── docs/
│   └── report.md            # forensic findings write-up template
├── scripts/
│   ├── init.py
│   ├── extract_events.py     # pytsk3-based disk image extraction
│   ├── abstraction.py          # raw -> high-level event mapping
│   ├── clustering.py            # DBSCAN event clustering
│   └── utils.py                  # CSV writing / timestamp helpers
├── .gitignore
├── requirements.txt
└── README.md

## Setup

```bash
git clone https://github.com/Snitch-1302/Time-Sleuth.git
cd Time-Sleuth
pip install -r requirements.txt
```

## Running the app (with the included sample data)

The repo ships with sample `raw_timeline.csv` and `abstracted_timeline.csv`
files depicting a synthetic ransomware-infection scenario, so you can run
the visualization immediately without needing a real disk image:

```bash
python app/app.py
```

Open the local URL Dash prints (typically `http://127.0.0.1:8050`).

## Running the full pipeline on a real disk image

To extract events from an actual disk image instead of the sample data:

1. Obtain a forensic disk image — e.g. the public **m57-jean** training
   image commonly used in DFIR courses (not included in this repo due to
   file size)
2. Place it at `data/m57-jean.dd` (or update `IMAGE_PATH` in
   `scripts/extract_events.py`)
3. Run the pipeline:
```bash
   cd scripts
   python extract_events.py      # produces data/raw_timeline.csv
   python abstraction.py          # produces data/abstracted_timeline.csv
```
4. Launch the app as above

## Known limitations

- The bundled sample CSVs are a synthetic demo scenario (a fictional
  ransomware infection), not the literal output of running
  `extract_events.py` against a real disk image — the extraction pipeline
  itself is functional, but the shipped data is illustrative.
- `normalize_timestamp()` currently just stringifies the raw Unix
  timestamp from `pytsk3` rather than converting it to a readable
  datetime — worth improving if extracting from a real image.
- The threat-level indicator in the click-inspection panel uses a small
  hardcoded list of "high-risk" event names as a heuristic, not a real
  threat-intelligence-backed classification.

## Full write-up

The reasoning behind the pipeline design and what I learned building it:
[Hashnode article link]

