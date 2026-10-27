# My progress

- [x] Phase 00 / 01 Dev Environment: Git, Python 3.12 (uv), Node.js 24, Rust 1.99, PyTorch (CPU)
- [x] Phase 00 / 02 Git & Collaboration
- Experiment branch: sinab ko'rish uchun alohida branch, main buzilmaydi
- [x] Phase 00 / 03 GPU Setup & Cloud

## GPU benchmark (GeForce GT 1030, 2 GB VRAM, driver 582.78, torch 2.14.1+cu126)

| Matrix | CPU | GPU | Speedup |
|--------|-----|-----|---------|
| 5000x5000, run 2 | 0.514s | 0.322s | 1.6x |
| 4000x4000 (gpu_check.py) | 0.331s | 0.189s | 2x |

Max model in fp16: 2.1 GB - ~0.5 GB used by Windows - ~0.3 GB margin = ~1.3 GB / 2 bytes = ~650M parameters.
- [ ] Phase 00 / 04 APIs & Keys: SDK installed, 401 error studied; real API call waits for a key
- [x] Phase 00 / 05 Jupyter Notebooks: `jupyter_ex1_timeit.ipynb`, `jupyter_ex2_csv_plot.ipynb` (kernel: `ai-course`)
- [x] Phase 00 / 06 Python Environments: env_setup.sh passed, isolated numpy 1.26 vs 2.5, `pyproject_ex3.toml`, global install demo
- [ ] Phase 00 / 07 Docker for AI: Docker Desktop + hello-world + GPU in container done; image build skipped (WSL crashes locally, Codespace disk too small) - return later
