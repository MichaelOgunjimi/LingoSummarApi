"""Resource loading and membership function definitions."""

import os

# ── Membership functions for each feature ─────────────────
mem_funcs = {
    "keyword": {
        "VL": {"start": -1, "peak": 0, "end": 0.25},
        "L": {"start": 0, "peak": 0.25, "end": 0.50},
        "M": {"start": 0.25, "peak": 0.50, "end": 0.75},
        "H": {"start": 0.50, "peak": 0.75, "end": 1.00},
        "VH": {"start": 0.75, "peak": 1.00, "end": 2.00},
    },
    "title_word": {
        "L": {"start": -1, "peak": 0, "end": 0.25},
        "M": {"start": 0, "peak": 0.25, "end": 1.00},
        "H": {"start": 0.25, "peak": 1.00, "end": 2.00},
    },
    "sentence_location": {
        "L": {"start": -1, "peak": 0, "end": 0.7},
        "H": {"start": 0, "peak": 1, "end": 2},
    },
    "sentence_length": {
        "VL": {"start": -1, "peak": 0, "end": 0.25},
        "L": {"start": 0, "peak": 0.25, "end": 0.50},
        "M": {"start": 0.25, "peak": 0.50, "end": 0.75},
        "H": {"start": 0.50, "peak": 0.75, "end": 1.00},
        "VH": {"start": 0.75, "peak": 1.00, "end": 2.00},
    },
    "proper_noun": {
        "L": {"start": -1, "peak": 0, "end": 0.50},
        "M": {"start": 0, "peak": 0.50, "end": 1.00},
        "H": {"start": 0.50, "peak": 1.00, "end": 2.00},
    },
    "cue_phrase": {
        "L": {"start": -1, "peak": 0, "end": 0.10},
        "M": {"start": 0, "peak": 0.10, "end": 1.00},
        "H": {"start": 0.10, "peak": 1.00, "end": 2.00},
    },
    "nonessential": {
        "L": {"start": -1, "peak": 0, "end": 0.05},
        "M": {"start": 0, "peak": 0.05, "end": 1.00},
        "H": {"start": 0.05, "peak": 1.00, "end": 2.00},
    },
    "numerical_data": {
        "L": {"start": -1, "peak": 0, "end": 0.50},
        "M": {"start": 0, "peak": 0.50, "end": 1.00},
        "H": {"start": 0.50, "peak": 1.00, "end": 2.00},
    },
}

# ── Output membership functions (I=Important, M=Medium, L=Low) ──
output_funcs = {
    "L": {"start": -0.5, "peak": 0, "end": 0.50},
    "M": {"start": 0, "peak": 0.50, "end": 1.00},
    "I": {"start": 0.50, "peak": 1.00, "end": 1.50},
}


def resource_loader() -> dict[str, set[str]]:
    """Load bonus_words.txt and stigma_words.txt from the resources directory."""
    resources: dict[str, set[str]] = {}
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")

    for filename in os.listdir(resources_dir):
        filepath = os.path.join(resources_dir, filename)
        if os.path.isfile(filepath):
            name = os.path.splitext(filename)[0]
            with open(filepath, encoding="utf-8") as f:
                resources[name] = set(f.read().split("\n"))

    return resources
