# Paper Knowledge Base: End-to-End Procedure

From raw PDFs to a clean, analysis-ready database for web app development.

---

## Overview

This document describes the complete workflow for building a standardized academic paper knowledge base. The process has three major phases:

1. **Phase 1 — PDF Extraction**: Use the `paper-knowledge-base` skill to extract structured metadata from raw PDF papers into Excel files.
2. **Phase 2 — Standardization**: Use the `paper-standardizer` skill (with `standardization_codebook.py`) to clean, classify, and standardize raw extracted columns into analysis-ready variables.
3. **Phase 3 — Filtering & Export**: Filter out problematic entries and export the final clean database for web app development.

The output is a single Excel file with one row per paper and ~50 standardized columns covering paper type, method, theory, geography, topics, data sources, and all key text fields.

---

## Folder Structure

```
Knowledge Base Project/
├── 1_raw_pdfs/
│   ├── JournalA/          # One subfolder per journal
│   │   ├── 2020 - Title - Author.pdf
│   │   └── ...
│   ├── JournalB/
│   └── ...
├── 2_raw_extracted/
│   ├── paper_knowledge_base_JournalA.xlsx
│   ├── paper_knowledge_base_JournalB.xlsx
│   └── ...
├── 3_standardized/
│   ├── standardization_codebook.py      # The master codebook (single source of truth)
│   ├── knowledge_base_standardized.xlsx  # Full database (all papers, all columns)
│   ├── knowledge_base_final.xlsx         # Clean database (problematic entries removed)
│   ├── FIELD_MAPPING.md                  # Column reference with fill rates and descriptions
│   ├── PROCEDURE.md                      # This document
│   └── paper-standardizer/
│       └── SKILL.md                      # The standardizer skill documentation
└── olddata.json                          # (Optional) legacy data for migration
```

---

## Phase 1: PDF Extraction

### Goal
Extract structured metadata from every PDF paper into an Excel knowledge base, using Claude's reading comprehension (not regex heuristics).

### Prerequisites
- Academic papers organized as PDFs in `1_raw_pdfs/`, ideally one subfolder per journal
- PDF filenames should follow the convention: `YEAR - Title - Authors.pdf`

### Skill used
`paper-knowledge-base` — a Cowork skill that reads each PDF in Claude's context window and extracts 23 structured fields per paper.

### Fields extracted per paper (23 columns)

| Field | Description |
|-------|-------------|
| `paper_id` | Sequential numeric ID |
| `authors` | Author names, semicolon-separated |
| `year` | Publication year |
| `title` | Full paper title |
| `journal` | Journal name |
| `paper_type` | Free-text paper type (e.g., "Empirical-quantitative study") |
| `topic_tags` | Comma-separated topic keywords |
| `abstract` | AI-generated paper summary |
| `research_gaps_previous_lit` | Research gaps the paper addresses |
| `research_question` | The paper's research question(s) |
| `theoretical_lens` | Theories, frameworks, or perspectives used |
| `independent_variables` | Key IVs or constructs explored |
| `dependent_variables` | DVs or outcome constructs |
| `mediators` | Mediating variables |
| `moderators` | Moderating variables |
| `control_variables` | Control variables |
| `sample` | Sample description (who, how many, where) |
| `data_source` | Data source description |
| `country_context` | Country or region studied |
| `method` | Research method description |
| `key_findings` | Key findings with hypothesis support/rejection |
| `future_directions` | Future research directions |
| `connections_and_notes` | Cross-references and extraction notes |

### How extraction works

1. Claude uses Python (pymupdf/fitz) to extract raw text from each PDF.
2. The text is loaded into Claude's context window — Claude reads and comprehends the paper.
3. Claude fills in all 23 fields based on comprehension (not regex parsing).
4. Results are saved incrementally to an Excel file after every 5–10 papers.
5. For large folders (hundreds of papers), Claude processes them one at a time with checkpoint saves. Sessions can be resumed by loading the existing Excel and continuing from the last processed paper.

### Output
One Excel file per journal in `2_raw_extracted/`:
- `paper_knowledge_base_JournalA.xlsx`
- `paper_knowledge_base_JournalB.xlsx`
- etc.

### Quality expectations at this stage
- Coverage varies by field: `title` and `authors` approach 100%; `mediators` may be ~23% (most papers don't have mediators)
- Some papers will have extraction failures (OCR issues, scanned PDFs, corrupted files)
- The `paper_type` field will be inconsistent free-text (e.g., "Empirical-quantitative study", "empirical quantitative", "Conceptual/Theoretical") — this is expected and gets cleaned in Phase 2
- Duplicate entries and non-research content (editorial boards, table of contents) may be present — these get flagged in Phase 2

---

## Phase 2: Standardization

### Goal
Transform the raw extracted columns into clean, categorical, analysis-ready standardized variables with 99%+ classification coverage.

### Skill used
`paper-standardizer` — documented in `3_standardized/paper-standardizer/SKILL.md`.

### The two-layer architecture

Every standardized variable uses the same approach:

**Layer 1 — Rule-based (codebook)**: Regex pattern matching against raw text columns. Deterministic, reproducible, fast. Typically achieves 85–98% coverage. All rules recorded in `standardization_codebook.py`.

**Layer 2 — AI intelligence (Claude)**: For papers that regex can't classify, Claude reads each paper's metadata and classifies it using comprehension. Results are recorded as `MANUAL_*_OVERRIDES` dictionaries in the codebook, making the codebook fully reproducible without needing AI again.

### The codebook (`standardization_codebook.py`)

This Python file is the single source of truth. It contains:
- Configuration paths pointing to raw Excel files
- A `load_raw_data()` function that merges all journal Excel files
- A `raw_data_fixes()` function for patching extraction failures
- One function per standardized variable (e.g., `std_year()`, `std_paper_type()`)
- A `PIPELINE` list that defines execution order
- A `main()` function that runs everything and saves the output

Running `python standardization_codebook.py` reproduces the complete standardized database from raw extracted data.

### Standardization pipeline (execution order)

The pipeline runs 22 functions in sequence:

```
raw_data_fixes      → Patch extraction failures in raw data
std_year            → Clean publication year (Int64)
std_journal         → Standardize journal names (4 categories)
std_abstract        → Clean AI-generated summaries, recover duplicates
std_rq              → Clean research questions, recover duplicates
std_findings        → Clean findings, strip redundant labels, recover duplicates
std_gaps            → Clean research gaps, recover duplicates
std_future          → Clean future directions, recover duplicates
std_notes           → Clean notes/cross-references, recover duplicates
std_sample_description → Clean sample descriptions, recover duplicates
std_iv              → Clean independent variables, recover duplicates
std_dv              → Clean dependent variables, recover duplicates
std_mediators       → Clean mediating variables, recover duplicates
std_moderators      → Clean moderating variables, recover duplicates
std_controls        → Clean control variables, recover duplicates
std_paper_type      → Classify into 8 paper types (100% coverage)
std_method_design_and_technique → 21 designs + 24 techniques (empirical papers only)
std_country_region_continent → Country, UN region, continent from country_context
std_theory_L1_L2    → 9 theory disciplines + 166 canonical theory names
std_data_source_type_and_named → 9 source types + 313 named datasets
std_topic_L1_L2     → 15 topic domains + 77 subtopics from topic_tags
std_flag            → Quality flag (OK, DUPLICATE, OCR_FAILED, RETRACTED, NON_RESEARCH)
```

### How to standardize each variable (the 7-step process)

For each new variable, follow these steps in order:

**Step 1 — Design categories.** Decide what categories to use (mutually exclusive or multi-valued), what raw columns to match against, and whether the variable applies to all papers or a subset. Present proposed categories to the user for approval.

**Step 2 — Write rule-based regex patterns.** For each category, write regex patterns that match key signals in the raw text. Critical rules learned from experience: never use trailing `\b` on truncated word stems; use `\w*` for word-form variations; handle NaN explicitly with `pd.notna(x)` checks; combine multiple columns with a separator for broader matching.

**Step 3 — Run the codebook and assess coverage.** Execute `python standardization_codebook.py` and check coverage percentage, category distribution, and sample unmatched papers.

**Step 4 — Iterate on rules.** Improve regex patterns based on what's unmatched. Common fixes: remove trailing `\b` on stems, add synonym alternatives, expand to search additional columns, use design-based inference (e.g., qualitative design implies qualitative coding technique).

**Step 5 — AI intelligence pass.** For remaining unmatched papers (typically 2–15% after regex optimization), Claude reads each paper's full metadata and classifies it. Process in batches of ~120 papers using parallel subagents for speed.

**Step 6 — Integrate AI classifications into the codebook.** Record all AI classifications as `MANUAL_*_OVERRIDES` dictionaries in the codebook using `(paper_id, title[:40])` tuple keys (paper_ids can duplicate across journals). This makes the codebook fully reproducible.

**Step 7 — Final verification.** Run the codebook from scratch and verify: coverage ≥ 99%, reasonable distribution across categories, random sample of classifications is correct.

### Variables produced (51 columns total)

The standardization pipeline produces the following standardized columns:

**Text cleanup variables (12):** `std_year`, `std_journal`, `std_abstract`, `std_rq`, `std_findings`, `std_gaps`, `std_future`, `std_notes`, `std_sample_description`, `std_iv`, `std_dv`, `std_mediators`, `std_moderators`, `std_controls`

**Categorical classification variables (12):** `std_paper_type`, `std_method_design`, `std_method_technique`, `std_country`, `std_region`, `std_continent`, `std_theory_L1_discipline`, `std_theory_L2_name`, `std_dsType`, `std_dsNamed`, `std_tpL1`, `std_tpL2`

**Quality flag (1):** `std_flag`

Combined with the 24 raw columns, the total is 51 columns per paper.

### Data quality investigation

After the initial standardization pass, investigate data quality:

1. **Check `Other`-typed papers** — many are duplicates, OCR failures, or non-research content, but some are misclassified real papers.
2. **Identify extraction failures** — papers with empty/garbled key fields (abstract, research_question, key_findings). Re-extract from original PDFs where possible.
3. **Reclassify mistyped papers** — teaching cases, commentaries, and reviews sometimes get misclassified as empirical papers during extraction. Correct in `raw_data_fixes()`.
4. **Check for true duplicates** — some databases contain duplicate entries of the same paper. Flag with `std_flag = 'DUPLICATE'`.

All corrections go into `raw_data_fixes()` (for raw column patches) or `MANUAL_*_OVERRIDES` (for classification corrections), keeping the codebook as the single source of truth.

---

## Phase 3: Filtering & Export

### Goal
Produce a clean, final database with only valid research papers for web app development.

### Steps

1. **Run the full pipeline** to generate `knowledge_base_standardized.xlsx` (all papers, all columns including `std_flag`).

2. **Filter to clean papers only:**
   ```python
   df_clean = df[df['std_flag'] == 'OK'].copy()
   ```

3. **Save as `knowledge_base_final.xlsx`** in `3_standardized/`.

4. **Verify the final database:**
   - Row count matches expected (total minus flagged papers)
   - All 51 columns present
   - No unexpected NaN values in required columns (`std_year`, `std_journal`, `std_paper_type`)
   - Journal distribution looks reasonable
   - Paper type distribution looks reasonable

### What gets filtered out

| Flag | Description |
|------|-------------|
| DUPLICATE | Duplicate entries of other papers in the database |
| OCR_FAILED | Papers where PDF extraction produced garbled or empty content |
| RETRACTED | Retracted papers, corrigenda, and errata |
| NON_RESEARCH | Administrative content (editorial board listings, tables of contents, subject indexes) |

Substantive editorials, commentaries, and teaching cases are NOT filtered — they remain as legitimate scholarly content under their respective `std_paper_type` categories.

---

## Key Design Decisions

### Why a Python codebook (not Excel formulas or manual editing)?
The codebook is reproducible — running `python standardization_codebook.py` regenerates the complete standardized database from raw data. Every decision is recorded in code, not in someone's memory or a spreadsheet cell.

### Why `(paper_id, title[:40])` tuple keys?
Paper IDs are not globally unique — the same ID can appear in different journals (e.g., pid=714 exists in both ETP and JBV as different papers). The title prefix disambiguates. The 40-character limit balances uniqueness against readability.

### Why regex before AI?
Regex handles 85–98% of papers deterministically and instantly. The AI pass is reserved for the 2–15% that require reading comprehension. This keeps the pipeline fast, reproducible, and cost-efficient.

### Why record AI classifications as manual overrides?
Once Claude classifies a paper, that classification is written into the codebook as a dictionary entry. Future pipeline runs reproduce the result without needing AI, making the process deterministic and auditable.

### Why `'OK'` instead of empty string for clean papers?
Empty strings in pandas become NaN when saved to Excel and read back. Using the explicit string `'OK'` avoids this silent data loss.

### Why `std_flag` runs last in the pipeline?
`std_flag` uses content from other `std_` columns (e.g., `std_rq`, `std_findings`, `std_abstract`) to determine whether `Other`-typed papers have substantive content. It must run after all other standardization functions have populated their columns.

---

## Reusing This Pipeline for a New Database

The standardization codebook is designed to be reusable. See the "Adapting to a New Paper Database" section in `paper-standardizer/SKILL.md` for detailed instructions.

In brief:
1. Copy `standardization_codebook.py` to your new project
2. Clear all database-specific components (manual overrides, raw_data_fixes, year corrections)
3. Keep all reusable components (regex pattern libraries, category definitions, helper functions, architecture)
4. Update configuration paths
5. Run the codebook — regex rules should handle 85–98% of your new papers
6. Run AI intelligence passes on unmatched papers
7. Record new manual overrides
8. Investigate data quality and add raw_data_fixes as needed

The category definitions (8 paper types, 21 method designs, 24 techniques, 9 data source types, 15 topic domains, 77 subtopics, 9 theory disciplines, 166 theory names, 93 countries, 313 named datasets) encode domain knowledge about entrepreneurship research and should transfer well to any database in the same field.

---

## Quick Reference: File Purposes

| File | Purpose |
|------|---------|
| `standardization_codebook.py` | Single source of truth — all standardization logic, run to regenerate everything |
| `knowledge_base_standardized.xlsx` | Full database — all papers including flagged ones, all 51 columns |
| `knowledge_base_final.xlsx` | Clean database — flagged entries removed, ready for web app |
| `FIELD_MAPPING.md` | Column-by-column reference with fill rates, descriptions, and design decisions |
| `PROCEDURE.md` | This document — end-to-end workflow description |
| `paper-standardizer/SKILL.md` | Skill documentation — detailed variable-by-variable standardization guide |

---

### Post-pipeline deduplication

The `std_flag` function now includes both keyword-based detection (Rules 1–6) and title-based deduplication (Rule 7). Rule 7 catches duplicates the extractor created without flagging them — it compares exact titles among OK-flagged papers and keeps the copy with the most filled std_ fields. In the current database, keyword-based rules flag 68 duplicates and title-based dedup flags an additional 170, for a total of 238 DUPLICATE entries. Papers from out-of-scope journals (e.g., JSBM, SBE) are flagged NON_RESEARCH. After filtering to `std_flag == OK`, the final database has 3,511 papers. Paper IDs are reassigned sequentially (1 to N) to ensure uniqueness.

### Web app data export

The final database is exported to JSON for the web app using `4_app/build_data.py`, which maps 32 fields from the 51-column Excel to compact JSON field names (e.g., `std_paper_type` → `type`, `std_method_design` → `design`). A production build script (`4_app/build_production.py`) embeds the JSON data into a self-contained HTML file for deployment.

---

*Last updated: 2026-03-11*
