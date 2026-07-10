# Changelog

All notable changes to RaPDTool are documented here.

## [2.3.0] — 2026-07-10

### Added
- **Screen mode** (`-m screen`) — FOCUS + `mash screen` (containment) to identify the
  reference genomes present in a metagenome **without binning**. Reports each detected
  genome (species/taxID via esearch) with its identity and shared-hashes, for hits at or
  above `--screen-identity` (default 0.95). Full and profile modes are unchanged.

## [2.2.0] — 2026-07-07

Major robustness, usability and packaging overhaul.

### Added
- **Conda distribution** — `conda install -c kjestradag rapdtool` installs a small
  launcher (plus Apptainer) that downloads and caches the prebuilt image and the
  reference databases on first use; no bioinformatics tools are installed on the host.
- **Two run modes** via `-m/--mode {full,profile}`. `profile` runs FOCUS + Krona for
  single-genome assemblies (where binning does not apply) and, when a mash database is
  supplied, also classifies the **whole assembly as a single bin** (Mash classification
  table without binning/completeness columns).
- **Per-species FASTA output** — new `rapdtool_split_bins.py` writes one FASTA per
  identified species (`<Species>__<bin>.fna`). Runs automatically in full mode
  (disable with `--no-split-bins`); also usable standalone.
- **External FOCUS database** via `--focus-db` / `$RTFOCUSDB` (k-mer `db/k6`, no longer
  bundled in the image).
- **Parallelism** — `-t/--threads` (default: all cores) passed to FOCUS, Metabat2,
  miComplete and Mash.
- **Metabat coverage** — `-a/--coverage` to pass a depth/coverage file to Metabat2.
- **`--force`** to overwrite existing results for the same input.
- Convenience host launcher `rapdtool.sh` (auto-discovers the SIF and auto-binds the
  input/database/output directories) with helper `apptainer_bind.sh`.
- Documented, reproducible `Singularity.def`; `CHANGELOG.md`.

### Changed
- **External mash database** via `-d/--database` / `$RTMASHDB` — removed the hard-coded
  database path.
- Migrated from `os.system` string calls to `subprocess` with argument lists (no shell
  quoting/injection issues).
- Accepts **any FASTA extension** (`.fasta/.fa/.fna/.fas/…`, optionally `.gz`) with a
  quick format check.
- Rewrote the orchestrator around a `Pipeline` class; grouped path state; replaced
  `os.system('cp/mv/rm/mkdir')` with `shutil`/`os.makedirs`.
- Container entrypoint now forwards all arguments (`exec rapdtool.py "$@"`).
- Hardened `rapdtool_results.pl` so it no longer aborts when mash/miComplete inputs are
  absent (profile mode).
- **Slimmed the image ~70%** (1.60 GB → 0.48 GB): removed the conda package cache, the
  Miniconda installer, C headers/manpages, static libraries, package test suites,
  HMMER easel sources, docs/locales, pip and unused stdlib, and tkinter/tcl-tk
  (matplotlib forced headless via `MPLBACKEND=Agg`). The mash and FOCUS databases are
  no longer bundled.

### Fixed
- Pipeline now **aborts on any tool failure** with a clear message and log, instead of
  continuing and producing partial/garbage output.
- Fixed undefined `message` reference in error paths.
- `apptainer_bind.sh` no longer crashes under `set -u` when `$RTMASHDB`/`$RTFOCUSDB` are
  unset.
- `rapdtool.sh` now discovers versioned `rapdtool*.sif` instead of failing on a missing
  `rapdtool.sif`.

## [2.1.0] — earlier

- FOCUS / Metabat2 / Binning_refiner / miComplete / Mash pipeline with report merge and
  Krona visualization, distributed as an Apptainer image.
