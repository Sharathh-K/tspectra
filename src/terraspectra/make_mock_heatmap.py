"""Create the Week 2 mock JSON response. No model or dataset is used here."""
import json
import math
from terraspectra.data import ROOT


def make_mock_heatmap():
    west, south, east, north = 77.591, 13.152, 77.599, 13.158
    columns, rows = 10, 8
    width, height = (east - west) / columns, (north - south) / rows
    cells = []
    for row in range(rows):
        for column in range(columns):
            # Two invented smooth hotspots make an understandable UI example.
            score = min(0.98, 0.12 + 0.80 * math.exp(-((column-7)**2+(row-5)**2)/6)
                        + 0.35 * math.exp(-((column-2)**2+(row-2)**2)/3))
            cells.append({"id": f"cell-{row}-{column}", "row": row, "column": column,
                          "bounds": [west+column*width, south+row*height,
                                     west+(column+1)*width, south+(row+1)*height],
                          "score": round(score, 3)})
    data = {"schema_version": 1, "is_mock": True,
            "source": "Synthetic demonstration; not model predictions or measured disease.",
            "score_meaning": "Invented display score from 0 to 1, not an infection probability.",
            "crs": "EPSG:4326", "bounds": [west, south, east, north],
            "rows": rows, "columns": columns, "cells": cells}
    path = ROOT / "frontend/public/mock-heatmap.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {len(cells)} synthetic cells to {path}")
    return data


if __name__ == "__main__":
    make_mock_heatmap()
