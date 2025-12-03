# QDSX Market Edition — Physics-Inspired Data Compression

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17771649.svg)](https://doi.org/10.5281/zenodo.17771649)

QDSX is a small, single-file, **lossless compression engine** designed for logs, JSON, CSV and other structured data.  
The algorithms were **inspired by the Quantum Dark Substrate (QDS)** work, but this repo is **purely practical software** – no physics background required.

---

## What’s in this repo?

This repo contains the **QDSX Market Edition v1** pack:

- `AAA_QDSX_MARKET_EDITION_v1.zip` — ready-to-use folder with:
  - `qdsx_engine.py` — main compression engine
  - `demo.txt` and `demo.txt.qdsx` — round-trip demo
  - `QDSX_logs/` and its own README inside

Key properties:

- Single-file engine, easy to drop into existing projects
- Lossless compression with human-readable logs
- Designed for **structured data** (logs / JSON / CSV) rather than media

---

## Requirements

- **Python**: 3.8 or newer  
- **Dependencies**: standard library only (no external packages needed)

Runs fine on:

- Linux / macOS / Windows
- Termux on Android
- Pydroid3 on Android

---

## Quick start

### 1. Clone and unpack

```bash
git clone https://github.com/danfromdursley-spec/QDSX-Market-Edition.git
cd QDSX-Market-Edition

unzip AAA_QDSX_MARKET_EDITION_v1.zip
cd AAA_QDSX_MARKET_EDITION_v1