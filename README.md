
# Quantum Dark Substrate (QDS)

QDS is a **finite, GR-compatible stochastic kernel** that appears to fit both local  
**H₀ variance** and **galaxy rotation curves** **without dark-matter particles**,  
using only **1–2 extra parameters**.

---

## Preprint & DOI

📄 **Preprint (Zenodo)**  
https://doi.org/10.5281/zenodo.17769921  

This repo contains minimal, Android-safe Python scripts that reproduce the key  
variance and rotation-curve results from the preprint.

---

## What’s in this repo?

- Simple Python scripts to:
  - generate **H₀ variance** fits vs. survey scale, and  
  - generate **galaxy rotation-curve** fits with the QDS kernel;
- Comments kept short and practical so they run cleanly on:
  - **Termux** on Android, and  
  - **Pydroid3** or a basic desktop Python install;
- No heavy dependencies: standard scientific Python only (NumPy / SciPy / Matplotlib).

---

## Quick start (Termux / desktop / Pydroid)

1. **Clone or download** this repository.
2. Make sure you have Python 3 plus the usual stack (`numpy`, `scipy`, `matplotlib`).
3. From the repo folder, run the included QDS demo scripts, for example:

   ```bash
   # H₀ variance demo
   python qds_h0_variance_demo.py

   # Galaxy rotation-curve demo
   python qds_rotation_demo.py