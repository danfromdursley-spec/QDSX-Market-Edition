

# Quantum Dark Substrate (QDS)

QDS is a **finite, GR-compatible stochastic kernel** that appears to fit both
local **H₀ variance** and **galaxy rotation curves** *without dark-matter particles*,
using only **1–2 extra parameters**.

📄 Preprint (Zenodo): **10.5281/zenodo.17769921**  
🧮 This repo contains minimal, Android-safe Python scripts that reproduce
the key variance and rotation-curve results.

> If you know a no-go theorem or standard argument that kills this kind of
> kernel, **please tell me** — I’d rather be corrected than confused. 🙂

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17771649.svg)](https://doi.org/10.5281/zenodo.17771649)

# QDSX Market Edition — Physics-Inspired Data Compression

This repo contains the **QDSX Market Edition v1** pack:

- `AAA_QDSX_MARKET_EDITION_v1.zip` — a ready-to-use folder with:
  - `qdsx_engine.py` (main compression engine)
  - `demo.txt` / `demo.txt.qdsx` (round-trip demo)
  - `QDSX_logs/` and README inside



QDSX is a small, single-file, **lossless compression engine** designed for logs, JSON, CSV and other structured data.

If you’d like me to run QDSX on one of your datasets as a **small paid pilot** (with a short written report of compression ratios and behaviour), you can contact me via GitHub or email.

---

## Quick start

```bash
git clone https://github.com/danfromdursley-spec/QDSX-Market-Edition.git
cd QDSX-Market-Edition

# run synthetic benchmark
python qdsx_engine.py

# compress a file
python qdsx_engine.py mydata.bin

# decompress
python qdsx_engine.py -d mydata.bin.qdsx

Commercial use & pilots
If you want help integrating QDSX into a production system, or you’d like a commercial license with support and SLAs, contact:
Email: danfromdursley@gmail.com

## QDSX Market Edition – Ready-to-Run Pack

If you’d like a ready-to-use version of QDSX (with the engine, demo files and a short README) you can get it here:

👉 [QDSX Market Edition on Gumroad](https://dursleydan.gumroad.com/l/apjxgw)
