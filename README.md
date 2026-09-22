# AI Paper Research & Operations Engineering

[![Typesetting: Tectonic](https://img.shields.io/badge/typesetting-Tectonic-blue.svg)](https://tectonic-typesetting.github.io/)
[![Workspace: TPO--VERSE](https://img.shields.io/badge/research-TPO--VERSE-indigo.svg)](TPO-VERSE/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](#)

Welcome to the **AI Paper Research & Operations Engineering** repository (ETDE Paragon / ParaTech Platform R&D). This monorepo houses foundational research papers, operational roadmaps, mathematical formulations, and engineering architectures developed for enterprise-scale commerce, spatial intelligence, and logistics in Indonesia.

---

## 🧭 Repository Architecture

All core research workstreams reside within the [`TPO-VERSE`](TPO-VERSE/) workspace:

```text
ai-paper-research/
├── README.md                                 # Root repository documentation (this file)
└── TPO-VERSE/                                # Research papers and operational frameworks
    ├── .vscode/                              # Pre-configured IDE settings for Tectonic & SyncTeX
    ├── README.md                             # Sub-workspace documentation
    │
    ├── Customer_OD/                          # ⬡ Spatial Indexing & Geospatial Analytics
    │   ├── brief.md                          # Strategic brief & Snowflake data architecture
    │   ├── plan.md                           # Research paper execution plan
    │   ├── generate_figures.py               # Deterministic TikZ figure generator
    │   ├── figures/                          # Generated TikZ LaTeX diagrams
    │   ├── h3_market_analysis.tex            # LaTeX source paper
    │   └── h3_market_analysis.pdf            # Compiled research paper
    │
    ├── ParaExpress/                          # ⚡ Ultra-Fast Omnichannel Fulfillment (<60m)
    │   ├── ROADMAP.md                        # Effort–impact technical strategy & workstream ranking
    │   ├── PHASE0.md                         # Months 0–4 execution plan (Foundations & digital twin)
    │   ├── paraexpress.tex                   # LaTeX technical report (Vol. 1 No. 1)
    │   └── paraexpress.pdf                   # Compiled technical report
    │
    ├── TPO-Gravity-Model/                    # 🪐 Market-Responsive Gravitational Architecture
    │   ├── tpo_gravity_model.tex             # LaTeX source paper
    │   └── tpo_gravity_model.pdf             # Compiled research paper
    │
    ├── Tech-Social-Dynamics/                 # ⚛️ Computing Epochs & Human Organization
    │   ├── organizational-evolution-ai-quantum-era.md # Ideation & architectural notes
    │   ├── org_evolution_computing_epochs.tex# LaTeX source paper (The Feynman Quantum Org)
    │   └── org_evolution_computing_epochs.pdf# Compiled research paper
    │
    └── VRPTW-TERRA/                          # 🚚 Heterogeneous Hybrid Routing Framework
        ├── brief.md                          # Technical brief (Megacity vs. Archipelagic routing)
        ├── vrptw_terra.tex                   # LaTeX source paper (VROOM / OSM / H3 adaptation)
        └── vrptw_terra.pdf                   # Compiled research paper
```

---

## 🔬 Research Pillars & Papers

### 1. [TPO Gravity Model](TPO-VERSE/TPO-Gravity-Model/)
* **Title**: *Engineering Market Gravity: A Gravitational Architecture for Market-Responsive Enterprise Systems*
* **Paper**: [`tpo_gravity_model.tex`](TPO-VERSE/TPO-Gravity-Model/tpo_gravity_model.tex) · [Compiled PDF](TPO-VERSE/TPO-Gravity-Model/tpo_gravity_model.pdf)
* **Summary**: Reconceptualizes enterprise architecture from traditional fragmented internal silos (sales, logistics, finance) into a unified, market-responsive gravitational model structured around four operational pillars:
  - **Consumer** (*Gravity Well*): The primary demand sink pulling value through the ecosystem.
  - **Community** (*Gravity Field*): Organic social influence and distributed brand presence.
  - **Customer** (*Gravity Bridge*): Retailers, distributors, and omnichannel touchpoints.
  - **Supply Chain** (*Gravity Engine*): Manufacturing, warehousing, and dynamic fulfillment.
  - **Gravity Core**: Shared governance base providing legal, financial, and HR technology cohesion.

---

### 2. [ParaExpress](TPO-VERSE/ParaExpress/)
* **Title**: *Ultra-Fast Omnichannel Fulfillment: Architecture, Economics, and Execution Strategy*
* **Paper**: [`paraexpress.tex`](TPO-VERSE/ParaExpress/paraexpress.tex) · [Compiled PDF](TPO-VERSE/ParaExpress/paraexpress.pdf)
* **Roadmap & Strategy**: [`ROADMAP.md`](TPO-VERSE/ParaExpress/ROADMAP.md)
* **Foundational Plan**: [`PHASE0.md`](TPO-VERSE/ParaExpress/PHASE0.md)
* **Key Insights**:
  - **Quadratic Leverage on In-Node Time ($t_{\text{node}}$)**: Cutting in-node time from 15 to 8 minutes reduces SLA-mandated fulfillment node count by ~25%.
  - **Courier Pre-Matching**: Dispatching 3PL couriers at pick-start rather than pack-end compresses the handover window and recovers critical node margin.
  - **Two-Tier Digital Twin**: Separating closed-form analytical approximations (Phase 0–1) from discrete-event simulation kernels (Phase 2).
  - **Asset-Light Coverage**: Activating consignment retail doors as fulfillment points before deploying dedicated dark stores.

---

### 3. [Customer OD & H3 Spatial Analytics](TPO-VERSE/Customer_OD/)
* **Title**: *H3 Spatial Indexing & Geospatial Analytics for Indonesian Retail and Supply Chain*
* **Paper**: [`h3_market_analysis.tex`](TPO-VERSE/Customer_OD/h3_market_analysis.tex) · [Compiled PDF](TPO-VERSE/Customer_OD/h3_market_analysis.pdf)
* **Strategic Brief**: [`brief.md`](TPO-VERSE/Customer_OD/brief.md) · **Plan**: [`plan.md`](TPO-VERSE/Customer_OD/plan.md)
* **Visualization Generator**: [`generate_figures.py`](TPO-VERSE/Customer_OD/generate_figures.py)
* **Key Innovations**:
  - **Mitigating MAUP**: Eliminates the Modifiable Areal Unit Problem inherent in wildly unequal Indonesian administrative boundaries (*Kota*, *Kecamatan*, *Kelurahan*).
  - **Uniform Hexagonal Tessellation**: Uses Uber H3 Resolution 8 (~0.73 km²) across the archipelago for apples-to-apples performance comparisons.
  - **Cross-Border Catchment**: Overcomes artificial municipal boundaries between West Jakarta and Tangerang using continuous $k$-Ring neighbor queries.
  - **Snowflake-Native H3 Spine**: Standardizes spatial joins into native string operations inside cloud data warehouses.

---

### 4. [VRPTW-TERRA](TPO-VERSE/VRPTW-TERRA/)
* **Title**: *A Heterogeneous Hybrid Routing Framework: Adapting Spatial Indexing (Uber H3) and Open-Source Optimization (VROOM/OSM) across Asymmetric Indonesian Topographies*
* **Paper**: [`vrptw_terra.tex`](TPO-VERSE/VRPTW-TERRA/vrptw_terra.tex) · [Compiled PDF](TPO-VERSE/VRPTW-TERRA/vrptw_terra.pdf)
* **Brief**: [`brief.md`](TPO-VERSE/VRPTW-TERRA/brief.md)
* **Key Innovations**:
  - **Context-Aware Parameterization Layer**: Dynamically tunes routing behavior between two distinct archetypes:
    - *Archetype A (Megacity — Jakarta)*: High H3 resolution (res 8–9), heavy time-dependent traffic multipliers ($\mu_{\text{traffic}}$), motorbike lane splits, and soft time windows with tardiness penalties.
    - *Archetype B (Archipelagic Hub — Ambon)*: Low H3 resolution (res 6–7), ferry route graph links, maritime transit penalties ($\delta_{\text{maritime}}$), and hard cutoffs dictated by daylight hours and vessel departure schedules.
  - **Regional Complexity Factor ($\Omega_{\text{region}}$)**: Corrects distance-to-effort distortion between continental and archipelagic routes.

---

### 5. [Tech × Social Dynamics](TPO-VERSE/Tech-Social-Dynamics/)
* **Title**: *The Feynman Quantum Organization: How Computing Epochs Reshape Human Organization*
* **Paper**: [`org_evolution_computing_epochs.tex`](TPO-VERSE/Tech-Social-Dynamics/org_evolution_computing_epochs.tex) · [Compiled PDF](TPO-VERSE/Tech-Social-Dynamics/org_evolution_computing_epochs.pdf)
* **Ideation Notes**: [`organizational-evolution-ai-quantum-era.md`](TPO-VERSE/Tech-Social-Dynamics/organizational-evolution-ai-quantum-era.md)
* **Summary**: Grounded in Richard Feynman's 1981 foundational paper on simulating physics with computers, this research models how human organizations evolve across three distinct computing epochs:
  1. *Classical & Analytical*: Hierarchical, deterministic structures matching sequential computing.
  2. *Generative & Agentic*: Probabilistic, adaptive networks matching LLM and multi-agent coordination.
  3. *Quantum & Entangled*: Non-local, superposed organizational topologies where authority and coordination boundaries become fluid and dynamic.

---

## 🛠️ Build & Typesetting Environment

All papers in this repository are compiled using [**Tectonic**](https://tectonic-typesetting.github.io/), an open-source, self-contained modern TeX engine that automatically downloads required TeX packages on-demand.

### Antigravity IDE / VS Code Integration

The repository includes workspace settings in [`TPO-VERSE/.vscode/settings.json`](TPO-VERSE/.vscode/settings.json):

* **Auto-Compilation on Save**: Saving any `.tex` file (`Cmd+S` / `Ctrl+S`) triggers Tectonic compilation automatically.
* **SyncTeX Two-Way Synchronization**:
  - **Source to PDF**: Jump directly to the compiled paragraph in the PDF viewer.
  - **PDF to Source**: `Cmd + Click` (macOS) or `Ctrl + Click` (Windows/Linux) anywhere on the PDF viewer to navigate to the exact LaTeX line.
* **Automatic Workspace Cleanup**: Automatically scrubs auxiliary files (`.aux`, `.bbl`, `.log`, `.xdv`, `.out`, etc.) upon build completion to keep git trees clean.

### Manual CLI Compilation

To compile any paper manually from the terminal:

```bash
# Compile TPO Gravity Model
cd TPO-VERSE/TPO-Gravity-Model
tectonic --synctex tpo_gravity_model.tex

# Compile ParaExpress Technical Report
cd ../ParaExpress
tectonic --synctex paraexpress.tex

# Compile Customer OD H3 Paper
cd ../Customer_OD
python3 generate_figures.py  # regenerate TikZ figures if needed
tectonic --synctex h3_market_analysis.tex

# Compile VRPTW-TERRA Paper
cd ../VRPTW-TERRA
tectonic --synctex vrptw_terra.tex

# Compile Tech-Social-Dynamics Paper
cd ../Tech-Social-Dynamics
tectonic --synctex org_evolution_computing_epochs.tex
```

---

## 📊 Figure Generation

Geospatial diagrams and TikZ figures in [`TPO-VERSE/Customer_OD/`](TPO-VERSE/Customer_OD/) are generated via:

```bash
cd TPO-VERSE/Customer_OD
python3 generate_figures.py
```

* Zero external heavy dependencies: Uses a deterministic Linear Congruential Generator (LCG) to output identical mathematical plots across platforms without needing `numpy` or `matplotlib`.
* Output diagrams are written to [`TPO-VERSE/Customer_OD/figures/`](TPO-VERSE/Customer_OD/figures/).

---

## 🤝 Contribution & Git Workflow

* **Commit Conventions**: Follow conventional commits:
  - `feat:` New research models, algorithms, or figure generators.
  - `docs:` Updates to papers, LaTeX documentation, and markdown briefs.
  - `refactor:` Restructuring LaTeX floats, TikZ adjustments, or code cleanup.
* **Remote Access**: Pushes are authenticated via SSH (`git@github.com:arifindobson/ai-paper-research.git`). Ensure your SSH key is authorized in your GitHub settings before pushing to `origin/main`.
