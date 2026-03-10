# Entrepreneurship Research Knowledge Base (ERKB)

A comprehensive, searchable database of **3,511 papers** published in the three leading entrepreneurship journals:

- **Entrepreneurship Theory and Practice** (ETP)
- **Journal of Business Venturing** (JBV)
- **Strategic Entrepreneurship Journal** (SEJ)

Each paper has been processed through an AI-assisted pipeline that extracts structured information — research questions, key findings, theories, methods, variables, geographic context — and standardizes it into filterable, searchable categories.

**[Live Demo →](https://amychina12.github.io/entrepreneurship-kb/)**

## Features

- **Full-text search** with BM25 relevance ranking, synonym handling, and stemming
- **Multi-dimensional filtering** by journal, year, method type, research design, theory, topic, geography, and more
- **Interactive analytics** — journal comparisons, theory × topic heatmaps, method × topic heatmaps, variable relationship explorer
- **Paper cards** with expandable details showing research questions, findings, methods, theories, and variables
- **Export** to CSV, BibTeX, or Excel
- **AI summaries** (optional, requires API key) — generate thematic summaries of filtered paper sets
- **Dark mode**, keyboard navigation, and bookmarking

## Repository Structure

```
├── index.html                      # Web app (GitHub Pages entry point)
├── data.json                       # Paper database (loaded dynamically)
├── extraction/                        # Phase 1: PDF extraction
│   ├── paper-knowledge-base-SKILL.md  # Claude skill used for extraction
│   └── paper_knowledge_base_*.xlsx    # Raw extracted data per journal
├── standardization/                # Phase 2: Standardization
│   ├── standardization_codebook.py # Master codebook (22 functions)
│   ├── knowledge_base_standardized.xlsx  # Full database with std_flag
│   ├── knowledge_base_final.xlsx   # Clean database (3,511 OK papers)
│   ├── FIELD_MAPPING.md            # Column reference with fill rates
│   └── paper-standardizer/
│       └── SKILL.md                # Standardizer skill documentation
├── app/                            # Phase 3: Web app source
│   ├── index.html                  # Development version of the app
│   ├── build_data.py               # Excel → JSON conversion
│   └── build_production.py         # Build script for deployment
└── docs/
    ├── PROCEDURE.md                # End-to-end pipeline documentation
    └── APP_FIELD_MAPPING.md        # App field mapping reference
```

## Pipeline Overview

The pipeline has three phases:

### Phase 1 — PDF Extraction
Raw journal PDFs are processed using Claude's `paper-knowledge-base` skill (included in `extraction/paper-knowledge-base-SKILL.md`) to extract 30+ structured fields per paper (title, authors, year, abstract, research questions, findings, theories, methods, variables, sample details, etc.). The skill is designed for use with [Claude Code](https://claude.com/claude-code) or Cowork mode.

### Phase 2 — Standardization
The `standardization_codebook.py` processes raw extractions through 22 standardization functions that clean, classify, and harmonize fields into analysis-ready categories. This includes:
- Regex-based classification (85–98% coverage per field)
- Quality flagging via `std_flag` (7 rules for catching duplicates, non-research content, and OCR failures)
- Title-based deduplication across journals

### Phase 3 — Web App
The final database is converted to JSON and served through a single-file React 18.2 application with BM25 search, Chart.js analytics, and D3 visualizations.

## Data Fields

Each paper record contains up to 32 fields organized into categories:

| Category | Fields |
|----------|--------|
| **Identity** | id, title, authors, year, journal, doi |
| **Content** | abstract, research questions, key findings, gaps, notes |
| **Method** | type, design, technique, sample details |
| **Theory** | discipline, theory names |
| **Topics** | level-1 domains (15), level-2 subtopics (77) |
| **Variables** | independent, dependent, mediators, moderators, controls |
| **Context** | continent, country, industry |
| **Data** | source type, named datasets |

## Deployment

The app runs entirely in the browser with no backend. Two deployment options:

**Option A — Dynamic (recommended for this repo):**
The `index.html` at the repo root loads `data.json` at runtime. To update the database, just replace `data.json`. This is how the GitHub Pages site works.

**Option B — Self-contained:**
Run `python app/build_production.py` to generate a single `deploy/index.html` (~10 MB) with all data embedded. Works offline and via `file://` protocol.

## Local Development

```bash
# Serve locally (needed for fetch-based data loading)
cd /path/to/this/repo
python -m http.server 8000
# Open http://localhost:8000
```

To rebuild from Excel data:
```bash
cd app
python build_data.py    # Generates data.json from knowledge_base_final.xlsx
python build_production.py  # Generates deploy/ with embedded + light versions
```

## Disclaimer

This database was built using an AI-assisted extraction and standardization pipeline. While every effort has been made to ensure accuracy, some papers may be missing, and extracted information (e.g., theory classifications, method coding, variable identification) may contain errors. Users are encouraged to verify critical details against the original publications.

## Author

**Wei Yu**, Assistant Professor of Entrepreneurship, National University of Singapore (NUS)

[Website](https://amychina12.github.io/weiyu/)

## License

The code in this repository (extraction scripts, standardization codebook, web app) is released under the MIT License.

The extracted data represents structured metadata about published academic papers. The original papers remain under their respective publishers' copyright.
