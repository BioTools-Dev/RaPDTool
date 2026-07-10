<div align="center">
  <h1>RaPDTool</h1>
  <h1>${{\color{red}Ra}pid\ {\color{red}P}rofiling\ and\ {\color{red}D}econvolution\ {\color{red}Tool}}\ for\ metagenomes$</h1>
</div>

### [!WARNING]
 <div align="center">
<h1>
<span style="color:red;">
RaPDTool up-to-date version (v2.2) continues in https://github.com/kjestradag/RaPDTool
</span>
</h1>
</div>

![RaPDTool_pipeline_600ppi](https://user-images.githubusercontent.com/42699236/163837963-9394db95-a232-4b6e-92d7-d5b6bc90cdd2.png)

RaPDTool offers a simple, easy-to-use workflow for microbial-community profiling,
contig binning and "genomic-distance" exploration by chaining several
bioinformatic tools into a single pipeline:

1. **Taxonomic profile** from a metagenome assembly (or genomic assembly) with **FOCUS**.
2. **Binning** of a metagenome into individual genomes/bins with **Metabat2**, refined
   into a non-redundant set with **Binning_refiner**.
3. **Completeness / redundancy** and basic MAG statistics with **miComplete**.
4. **"Taxonomic neighborhood"** of each bin against a curated type-material **Mash** database.
5. **Interactive visualization** with **Krona**, plus per-species FASTA output.

---

## What's new in v2.2.0

- **One-line conda install** – `conda install -c kjestradag rapdtool` sets everything up;
  the tested image and databases are fetched and cached automatically on first use.
- **Robust error handling** – if any tool fails, the pipeline stops immediately with a
  clear message instead of producing partial/garbage output.
- **External databases** – the mash reference via `-d`/`$RTMASHDB` and the FOCUS k-mer
  database via `--focus-db`/`$RTFOCUSDB` (neither is bundled in the image, keeping it slim).
- **Two run modes** – `full` (default) and `profile` (for genomic assemblies where binning
  does not apply). Profile runs FOCUS + Krona and, if a mash database is supplied, also
  classifies the **whole assembly as a single bin** against it, adding a Mash
  classification table (without binning/completeness columns).
- **Parallelism** – `-t/--threads` is passed to FOCUS, Metabat2, miComplete and Mash.
- **Any FASTA extension** accepted (`.fasta`, `.fa`, `.fna`, `.fas`, …, optionally `.gz`)
  with a quick format check.
- **Metabat coverage** – pass a depth/coverage file with `-a`.
- **Per-species bins** – `rapdtool_split_bins.py` writes one FASTA per identified species
  (runs automatically in full mode; disable with `--no-split-bins`).
- Migrated from `os.system` string calls to `subprocess` with argument lists (no shell
  quoting/injection issues); general clean-up and bug fixes.

---

## Install

RaPDTool installs from conda and runs a **prebuilt, tested Apptainer image** — no
bioinformatics tools are installed on your machine:

```bash
conda install -c kjestradag rapdtool
```

This pulls in [Apptainer](https://apptainer.org/) and the `rapdtool` launcher. On the
**first run**, the image (~0.5 GB) and the reference databases are downloaded once and
cached under `~/.cache/rapdtool` (override with `$RAPDTOOL_CACHE`). Pre-fetch everything
with:

```bash
rapdtool setup      # optional: download image + databases ahead of time
rapdtool --where    # show where the image and databases are cached
```

Requirements: Linux with conda. That's it — Apptainer and the databases are handled
for you.

<details>
<summary>Advanced: build the image yourself / use your own databases</summary>

```bash
# Build the image from the recipe instead of downloading it
apptainer build --fakeroot rapdtool.sif Singularity.def
export RAPDTOOL_SIF=$PWD/rapdtool.sif

# Point at your own databases instead of the auto-downloaded ones
export RTMASHDB=/path/to/mash_db.msh       # NCBI type material or GTDB r202
export RTFOCUSDB=/path/to/focus            # a directory containing db/k6
```

Mash databases: [NCBI type-material prokaryotes](https://figshare.com/ndownloader/files/30851626)
· [GTDB r202](https://figshare.com/ndownloader/files/30863182).
</details>

---

## Usage

The `rapdtool` command forwards its arguments to the pipeline (the databases are provided
automatically):

```
rapdtool -i INPUT [-r ROOT] [-m {full,profile}] [-t THREADS] [-a COVERAGE]
         [--no-split-bins] [--force] [-c COMMENT]

  -i, --input      input FASTA assembly (.fasta/.fa/.fna/.fas, optionally .gz)   [required]
  -r, --root       output directory (default: ./rapdtool_results)
  -m, --mode       full (default) or profile (FOCUS + Krona; classifies the whole
                   assembly with Mash too)
  -t, --threads    threads for FOCUS/Metabat/miComplete/Mash (default: all cores)
  -a, --coverage   depth/coverage file passed to Metabat2 (-a)
      --no-split-bins   disable per-species FASTA output
      --force      overwrite existing results for the same input
  -c, --comment    comment recorded in the log

  -d, --database   mash .msh to use instead of the cached one   (optional override)
      --focus-db   FOCUS db directory (containing db/k6) to use  (optional override)
```

### Examples

```bash
# Full pipeline (metagenome assembly)
rapdtool -i assembly.fasta -r results

# Profile a single-genome assembly (FOCUS + whole-assembly Mash classification)
rapdtool -i genome.fna -m profile -r prof_out

# Full pipeline with 16 threads and a precomputed coverage file
rapdtool -i assembly.fa -t 16 -a depth.txt
```

---

## Output

Results are written under the `-r` directory (default `rapdtool_results`):

- `profilesfmbm/` – FOCUS profiling results
- `allresultsfmbm/` – ten closest Mash hits per bin
- `workfmbm/` – intermediate binning / distance data
- `species_bins/` – one FASTA per identified species (full mode)
- `rapdtool_confidence.tbl` / `.txt` – merged high-confidence Species/Genus report
- `rapdtool_krona.html` – interactive Krona visualization
- `log/logfmbm.txt` – full execution log

For each bin, RaPDTool reports the ten closest neighbors from the Mash comparison,
simplifying interpretation and providing a basis for finer OGRI/ANI analysis.

---

## Repository layout

```
bin/            pipeline scripts (rapdtool.py, rapdtool_split_bins.py, rapdtool_results.pl)
scripts/        rapdtool — host launcher (downloads/caches the image + databases, runs it)
conda-recipe/   conda package recipe (meta.yaml, build.sh)
docs/           figures
Singularity.def container build recipe
CHANGELOG.md    version history
```

See [CHANGELOG.md](CHANGELOG.md) for the full list of changes.

---

## Dependencies

FOCUS · Metabat2 (2.15) · Binning_refiner (1.4.3) · miComplete (1.1.1) · Mash (2.3) ·
KronaTools · entrez-direct (used only when reporting Mash hits; requires internet).

## References

- Sánchez-Reyes, A.; Fernández-López, M.G. *Mash Sketched Reference Dataset for
  Genome-Based Taxonomy and Comparative Genomics*. Preprints 2021, 2021060368.
- Ondov BD *et al.* *Mash: fast genome and metagenome distance estimation using MinHash.*
  Genome Biol. 2016;17(1):132.
- Silva GGZ *et al.* *FOCUS: an alignment-free model to identify organisms in
  metagenomes using non-negative least squares.* PeerJ. 2014;2:e425.
- Song WZ, Thomas T. *Binning_refiner.* Bioinformatics. 2017;33(12):1873-1875.
- Kang DD *et al.* *MetaBAT 2.* PeerJ. 2019;7:e7359.

## Maintainer

This distribution (v2.2.0 — refactored pipeline, external databases, slim image and
conda packaging) is maintained by **Karel Estrada** ([@kjestradag](https://github.com/kjestradag),
kjestradag@gmail.com). Issues and pull requests are welcome on the
[GitHub repository](https://github.com/kjestradag/RaPDTool).

## Acknowledgments

RaPDTool was originally developed in the group of **Dr. Ayixon Sánchez-Reyes** —
"Researchers for Mexico" Program (CONACYT), Institute of Biotechnology, UNAM.

Contact: ayixon@gmail.com · ayixon.sanchez@mail.ibt.unam.mx

We thank Ing. Roberto Peredo for his help in developing this tool.

Funded in part by project CF 2019 265222 (FORDECYT-PRONACES CONACYT-México).


--------------------------------------------------------------------------------------------------------------------------------------------------------------
<div align="justify">
<h2>RaPDTool</h2> A simple and easy-to-use tool for microbial communities profiling, contigs binning and "genomic-distance" exploration by connecting a series of bioinformatic tools in a single workflow:
</div>

### 1. Generate a taxonomic profile from massive sequencing data (the input file should be a metagenome assembly).

RaPDTool use metagenomic assemblies and call FOCUS profiler to report the organisms/abundance present in the metagenome.
<p align="justify">
*Warning: Taxonomic profiles are usually inferred from raw reads; assembled-contigs profiling is an "special case" in order to explore what part of the community could be assembled into regular genomic composites. Use at your own risk. For example, we have observed that Focus is not good at detecting contamination in the eukaryote genome and can return false positives in this case.
</p>

### 2. Deconvolve a metagenome into individual genomes or bins, and refine the set of MAGs.

<p align="justify">
If the input consist on a metagenome assembly, RaPDTool automatically call Metabat2  to aggregate individual genome bins. The bins are subsequently refined with Binning_refiner to produce a non-redundant set.
</p>

### 3. Estimate Completeness, Redundancy and MAG basic statistics with miComplete
 
<p align="justify">
In the version 2.0 of this pipeline, the refined set of bins are automatically processed with miComplete, a much faster tool than CheckM for this purpose. 
</p>

### 4. Evaluate the probable "taxonomic neighborhoods" of each resulting genome bin.

<p align="justify">
RaPDTool compare each bin against curated taxonomic mash databases like type material genome database from NCBI (NCBI_type_material.msh), the Genome Taxonomy Database (GTDBr202.msh) and a database that we built to enrich the one that comes by default with Focus, using almost entirely, the type material database. these databases are offered as representations or sketches that reduce storage space and computing time.
</p>


## Output directories and files

The output of RaPDTool produces 4 directories and 3 main files:

![rapdtool_output](https://user-images.githubusercontent.com/43998702/197233431-b97a7c1e-a94e-4b4d-812a-df6bc9305b54.png)

### Directory "log"

Contains the log file of the RaPDTool execution (logfmbm.txt).

**fmbm** is a kind of acronym that includes the main operations of the pipeline (Focus/Metabat/Binning_refiner/Mash).

***

## What about the results?

### File "rapdtools_confidence.txt"

<p align="justify">
Summarizes the best/most reliable **Mash** hits to be able to classify at the genus or species level. For the gender level it is considered a cut-off value <= 0.08 and <= 0.05 for species level.
Additionally it contains the results of the taxonomic classification with Focus, leaving only the species with a relative abundance greater than 1.
</p>

**rapdtools_confidence.tbl** contains the same data but with a prettier aesthetic

![rapdtool_result](https://user-images.githubusercontent.com/43998702/197008164-ab28e5b6-e79f-435c-a2c8-84ae590ce1a1.png)

### File "rapdtool_krona.html"

<p align="justify">
Krona charts through which you can navigate/explore the taxonomic annotation made up to the species level. Krona charts can be viewed with any modern web browser.
</p>

### Directory "profilesfmbm" 

<p align="justify">
Store the FOCUS taxonomic profile inferred from the inputs (metagenome assembly). You should see 
several files -in tabular format (csv)- reporting relative abundance from Kingdom to Species . FOCUS also ventures to infer Strains, but I would be cautious at that taxonomic level.
</p>

**Some points to note with this result:**

<p align="justify">
1-We could assume that the short-reads contain a "genomic space" more representative of the community, than that contained in the assembly; the assembly _per se_ supposes a loss of taxonomic information. Assembled contigs profiling only represents an approximation of taxonomic composition at the genomic level, so be cautious with the interpretations.
</p>

<p align="justify">
2-The native FOCUS database plays an important role in the accuracy of the profile. The initial launch of FOCUS considered 2,766 reference genomes to build a kmer frecuencies database ( _k_ = 6; _k_ = 7)  . For the implementation of RaPDTool, we have considered 14,551 genomes from the Type Material to give taxonomic certainty to the profiles, while enriching the initial database. 
</p>

> The new  _k_ = 6; _k_ = 7 kmer archives for [Update FOCUS Database will be available here](https://drive.google.com/file/d/1tuoWaNAocCv5igC7y1cm-QDdcGQhBZrQ/view?usp=drive_link)

![image](https://user-images.githubusercontent.com/42699236/170603717-eb9f8047-6bfa-4a89-85b2-0fa34c6c7e7e.png)

***

### Directory "workfmbm" 

Contains several relevant subdirectories and files:

**binmetabat** > Store Metabat2 binning results. The genome composites aggregated from the initial metagenomic assembly

**outbinningref**  > Binning_refiner results. All bins obtained with Metabat2 are "refined" with Binning_refiner to produce a set of probable MAGs

**outmicomplete** > Hugoson et al, 2020 published a paper with a fairly "generous" alternative to estimate quality of assembled microbial genomes (https://doi.org/10.1093/bioinformatics/btz664). Although the gold standard is still CheckM, miComplete is more resource friendly and offers a weighted calculation. 

The result of miComplete is a table with the quality assessment of the refined bins as shown in the image:

![rapdtool_micomplete](https://user-images.githubusercontent.com/43998702/196972846-0d9cbf2c-d5eb-4605-9c93-dee965fc0699.png)

**outmash** > **Full** Mash dist comparison for each bin produced, against the input database. Remember that these databases contain a set of genomes curated as Mash representations or sketches. This indicates that _bin1_ is compared against the ~65,336 records in the database (that's extremely fast with Mash), and the result is a table with 5 columns representing the following:


|Query_genome |  Match_in_database|   Genomic_Distance |  p_value | Shared_Hashes |
|-------------|-------------------|--------------------|----------|---------------| 
|  Bin1.fna   | GCA_Reference.fna |      0.0327655     |     0    |    471/1000   |

<p align="justify">
The genomic distance in the third column refers to the Mash distance, also defined as mutational distance. You will find more information on the interpretation of these tables in: https://doi.org/10.1186/s13059-016-0997-x. A practical interpretation of this comparison suggests that if two genomic contexts share < 0.05 distance, they are likely to be genomically coherents, and that has implications for the prokaryotic species concept.
</p>

<p align="justify">
This also means that those contexts with smaller genomic distances will potentially be the closest phylogenetic neighbors to your query; very useful if you want to explore the phylogenetic hypothesis.
</p>

Other subdirectories contain the log files of each task
***
 
### Directory "allresultsfmbm"

<p align="justify">
Contain the ten closest hits from the Mash paired comparison for each genome. This simplifies the interpretation of the results by limiting the Mash comparison to the ten closest neighbors to the query, which can be useful in phylogenetics and taxonomy. The user can take this list as the basis for a finer comparison by estimating the Overall genome relatedness index (OGRI) like ANI...
</p>

![rapdtool_mash](https://user-images.githubusercontent.com/43998702/197004779-6693da15-bd45-443f-a50d-0eff9ab7a63c.png)

<p align="justify">
As you can see, they are conveniently sorted from smallest to largest, so that it is easy to establish or rule out probable genomic coherence; and use the elements of the reference in subsequent more refined analyzes.
</p>

<p align="justify">
For example, in the previous image the bin **meta-assembly_bin_1.fna** shares a genomic distance of ~0.062 with the assembly GCF_002165255.2, that belongs to the species Acinetobacter sp. WCHA45 (proteobacteria); and ~0.07 with the assembly GCA_000430225.1 that belongs to the species _Acinetobacter_junii_. Other hits in this comparison also match elements of the _Acinetobacter_ genus. It is not difficult to hypothesize that the bin **meta-assembly_bin_1.fna** is related with the clade _Acinetobacter_ (probably at the genus level, although nothing can be said about the species yet). So, presumably **meta-assembly_bin_1.fna** can be clasified as _Acinetobacter_sp.
</p>

<p align="justify">
Potential tests could be the estimation of the Average Nucleotide Identity against these close hits and reconstructing a phylogenomic tree in order to place the query in a finer taxonomic context.
</p>
