[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17771649.svg)](https://doi.org/10.5281/zenodo.17771649)

# QDSX Market Edition — Physics-Inspired Data Compression
# QDSX Market Edition — Physics-Inspired Data Compression

This repo contains the **QDSX Market Edition v1** pack:

- `AAA_QDSX_MARKET_EDITION_v1.zip` — a ready-to-use folder with:
  - `qdsx_engine.py` (main compression engine)
  - `demo.txt` / `demo.txt.qdsx` (round-trip demo)
  - `QDSX_logs/` and README inside

QDSX is a small, single-file, **lossless compression engine** designed for
logs, JSON, CSV and other structured data.

If you’d like me to run QDSX on one of your datasets as a **small paid
pilot** (with a short written report of compression ratios and behaviour),
you can contact me via GitHub or email.


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


## Citation

If you use QDSX in research or a project, please cite:

> Williams, D. (2025). *QDSX Market Edition* (v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.17771649
