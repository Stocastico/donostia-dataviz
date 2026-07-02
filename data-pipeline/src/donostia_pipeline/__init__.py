"""Donostia Dataviz data pipeline.

Turns raw public sources (Donostia Open Data, INE, AEMET, ...) into the cleaned
static JSON consumed by the web app, per ``docs/DATA-CONTRACT.md``. The frontend
has no runtime dependency on this package; it only reads the emitted JSON.
"""

__all__ = ["config", "geometry", "build"]
