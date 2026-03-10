---
name: paper-standardizer
description: "Use this skill whenever the user wants to standardize variables in a paper knowledge base — creating new structured columns from raw extracted text. Triggers include: 'standardize my data', 'create standardized variables', 'classify papers', 'standardize paper types', 'standardize methods', 'clean up my knowledge base', 'codebook', 'add a new variable', 'run the standardization pipeline', 'standardize this database', or any mention of converting messy raw columns into clean categorical variables in an academic paper database. Also trigger when the user uploads a raw-extracted Excel file and wants it transformed into a structured, analysis-ready dataset. This skill covers the full pipeline: designing categories, writing rule-based regex, running AI intelligence passes on unmatched papers, recording everything in a reproducible codebook, and iterating to improve coverage."
---

# Paper Standardizer — Full Pipeline

This skill standardizes raw-extracted academic paper databases into clean, analysis-ready datasets. It covers the **complete pipeline** from designing variable categories to achieving 99%+ classification coverage, and records everything in a reproducible Python codebook.

## Companion file: `standardization_codebook.py`

This skill is designed to work alongside a Python codebook file (`standardization_codebook.py`) that lives in the `3_standardized/` folder. The codebook contains all the actual implementation: regex pattern libraries, category definitions, manual overrides, and helper functions. **This SKILL.md does not include the Python code** — it documents the approach, architecture, and decisions so that Claude can build or adapt a codebook for any paper database.

When applying this skill to a new database:
1. If a codebook from a prior project exists, copy it and adapt it (see "Adapting to a New Paper Database" below)
2. If starting fresh, Claude should create a new `standardization_codebook.py` following the architecture and patterns documented here

---

## When to use this skill

Use this skill when:
- The user has a raw-extracted paper knowledge base (Excel) and wants to create standardized variables
- The user wants to add a NEW standardized variable to an existing codebook
- The user wants to improve coverage on an existing standardized variable
- The user says "standardize", "codebook", "classify papers", "clean up my database", or similar
- The user has a NEW paper database and wants to apply the same standardization procedures

---

## Architecture: The Two-Layer Approach

Every standardized variable uses the same two-layer approach:

### Layer 1: Rule-Based (codebook — `standardization_codebook.py`)
- Regex pattern matching against raw text columns
- Deterministic, reproducible, fast
- Typically achieves 85–98% coverage depending on the variable
- All rules recorded in the codebook Python file

### Layer 2: AI Intelligence (this skill)
- Claude reads each unmatched paper's metadata and classifies it using comprehension
- Handles cases where regex patterns can't capture the meaning
- Results are recorded as `MANUAL_*_OVERRIDES` dictionaries in the codebook
- Once recorded, the codebook reproduces the full result without needing AI again

**The codebook is the single source of truth.** After the AI pass, all classifications get written back into the codebook as manual overrides, so running `python standardization_codebook.py` always reproduces the complete result.

---

## Pipeline for Each Variable

When standardizing any variable, follow these steps in order:

### Step 1: Design the categories

Before writing any code, decide:
1. What categories to use (mutually exclusive? multi-valued?)
2. What raw columns to match against
3. Whether the variable applies to all papers or a subset (e.g., empirical only)

Present the proposed categories to the user for approval. Include:
- Category name
- Definition (one sentence)
- Key text signals that would trigger this category
- Whether multi-valued (semicolon-separated) or single-valued

### Step 2: Write rule-based regex patterns

For each category, write regex patterns that match its key signals in the raw text.

**Critical regex rules (learned from experience):**
- NEVER use trailing `\b` on truncated word stems. Example: `\bcase\s+stud\b` FAILS on "case study" because `\b` expects a word boundary after "stud" but "y" follows. Use `\bcase\s+stud` instead (no trailing `\b`).
- DO use leading `\b` to prevent false matches on word prefixes
- Use `\w*` or `\w+` to handle word-form variations (e.g., `\bexperiment\w*` matches "experiment", "experimental", "experiments")
- Use `(?:...|...)` for alternation groups
- Combine patterns for the same category with `|`
- Test patterns against a sample before deploying

**NaN handling rules:**
- `str(NaN).strip()` returns `"nan"` which is truthy — always check with `pd.notna(x) and str(x).strip() not in ('', 'nan', 'N/A')`
- When iterating over rows, use `row.get(col, '')` with explicit NaN checks

**Multi-column search:**
- Start with the primary column(s) for the variable
- If coverage is insufficient, expand to additional columns (abstract, key_findings, IVs, DVs, controls, etc.)
- Combine columns with a separator: `' ||| '.join(col_texts)`

### Step 3: Run the codebook and assess coverage

```python
python standardization_codebook.py
```

Check:
- Coverage percentage (target: 95%+ before AI pass)
- Distribution across categories (any category suspiciously large or small?)
- Sample unmatched papers to understand WHY they're unmatched

### Step 4: Iterate on rules

Common reasons for low coverage and fixes:
- **Trailing `\b` on stems** → remove trailing `\b` (this was the #1 bug, improving technique from 34% to 65%)
- **Missing synonyms** → add more pattern alternatives
- **Column doesn't contain the info** → expand to search additional columns
- **Design-based inference** → if design implies technique (e.g., qualitative design → Qualitative Coding)

Repeat Steps 3-4 until rule-based coverage plateaus (typically 85–98%).

### Step 5: AI Intelligence Pass on remaining unmatched papers

For papers that rule-based matching can't handle:

1. **Identify unmatched papers** — filter to papers where the variable is still empty
2. **Load metadata** — for each paper, gather ALL available text: title, method, data_source, sample, abstract, key_findings, IVs, DVs, controls, connections_and_notes
3. **Classify in batches** — process ~120 papers per batch using parallel subagents for speed
4. **Record as Python dict** — each batch produces `{(paper_id, title_prefix_40chars): 'Category Value', ...}`
5. **Apply and verify** — apply classifications to the Excel, check coverage

**CRITICAL: You (Claude) must read each paper's metadata yourself and make the classification decision. Do NOT write a regex script. The whole point of the AI pass is comprehension for cases where patterns fail.**

**Batching strategy for large sets (>100 papers):**
- Split into 3 parallel batches
- Use subagents (Agent tool) to process batches concurrently
- Each subagent receives the category definitions, classification guidelines, and its batch of papers
- Merge results after all batches complete

### Step 6: Integrate AI classifications into the codebook

This is critical — don't skip it! The AI classifications must go into the codebook as `MANUAL_*_OVERRIDES` so the codebook is fully reproducible.

```python
# In the codebook, add a dictionary like:
MANUAL_VARIABLE_OVERRIDES = {
    (paper_id, 'Title prefix (first 40 ch'): 'Category Value',
    ...
}
```

Then add application logic in the codebook's loop:
```python
if not matched:
    pid = int(row.get('paper_id', -1))
    title = str(row.get('title', ''))[:40]
    for (oid, tstart), val in MANUAL_VARIABLE_OVERRIDES.items():
        if pid == oid and title.startswith(tstart):
            # Apply the override
            break
```

**Key detail:** Use `(paper_id, title_prefix[:40])` tuple keys because paper_ids can duplicate across journals (33 duplicates found in ETP/JBV/SEJ).

### Step 7: Final verification

Run the codebook from scratch and verify:
- Coverage ≥ 99%
- Distribution looks reasonable (no category is suspiciously over/under-represented)
- A random sample of classifications is correct
- All columns are present in the output

---

## Currently Standardized Variables

This section documents each variable that has been finalized. Update it as new variables are added.

### Pre-pipeline: `raw_data_fixes()`

| Property | Value |
|----------|-------|
| Source | Original PDFs in `1_raw_pdfs/` |
| Applies to | 19 specific papers with extraction failures |
| Runs | First in PIPELINE, before all standardization functions |

**Purpose:** Patches raw data for papers whose original PDF extraction produced empty or garbled fields. This runs before any standardization function so all downstream `std_*` variables benefit from the corrected raw data.

**Three groups of fixes:**

1. **JBV pids 111–120 (10 papers):** OCR/extraction failures. Re-extracted from original PDFs. Only JBV rows patched (ETP/SEJ rows for same pids are fine). Papers by Bantel (1998), Baron (1999, 2004), Basu et al. (2011, 2015), Bates (1995, 1997, 1998, 2002, 2005).

2. **ETP pids 1491, 1492, 1493, 1765, 1767, 1768 (6 papers):** Extraction failures. Re-extracted from original PDFs. Includes paper_type corrections: pid 1493 (Schildt et al. 2006 co-citation analysis) → Review, pid 1768 (Windeshausen & Joyce 1977 franchising overview) → Review.

3. **ETP pids 504, 718, 719 (3 papers):** Teaching cases misclassified as "Empirical-qualitative" in raw extraction. Paper_type corrected to "Editorial". JBV rows unaffected (different papers with same pids).

**Key implementation detail:** Uses `journal_filter` parameter to apply fixes only to the correct journal's rows when paper_ids are shared across journals. List fields (IVs, DVs, mediators, moderators, controls) are converted from Python lists to semicolon-separated strings.

### Variable 0: `std_year`

| Property | Value |
|----------|-------|
| Source column | `year` |
| Applies to | All papers |
| Multi-valued | No (single integer per paper) |
| Coverage | 100% (3,821/3,821) |

**Approach:** Converts mixed-type raw `year` column (integers, NaN, 0, strings like "Unknown" and "DUPLICATE") to clean integers. 17 manual corrections applied via YEAR_CORRECTIONS lookup dict. Years confirmed through web search, PDF metadata, and DUPLICATE title parsing. Uses `Int64` nullable integer dtype.

**Key decisions:**
- OCR-failed paper (pid=729, Kelley & Rice) year confirmed as 2001 via PDF creation date metadata
- DUPLICATE entries inherit years from original paper titles (which embed the year)
- Range: 1968–2025

### Variable 0b: `std_journal`

| Property | Value |
|----------|-------|
| Source column | `journal`, `pdf_filename` |
| Applies to | All papers |
| Multi-valued | No (single category per paper) |
| Coverage | 100% (3,821/3,821) |

**Categories (4):** ETP (1,850), JBV (1,516), SEJ (453), Other (2)

**Approach:** Three-layer resolution: (1) PDF folder lookup as ground truth (3,349 papers); (2) raw journal text mapping for 7 name variants (468 papers); (3) manual overrides + DUPLICATE inheritance for edge cases. "American Journal of Small Business" (221 papers) maps to ETP as its predecessor journal.

**Key decisions:**
- AJSB → ETP (predecessor journal, renamed 1988)
- DUPLICATE entries inherit journal from original paper
- Papers with incorrect journal names from extraction use PDF folder as ground truth
- Only 2 genuinely non-target papers remain as "Other" (JSBM, SBE)

### Variable 0c: `std_abstract`

| Property | Value |
|----------|-------|
| Source column | `abstract` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 99.1% (3,785/3,821) |

**Approach:** Copy clean AI-generated summaries as-is. Recover DUPLICATE entries by pulling abstracts from original papers. Set remaining to NaN (editorial board listings, OCR failures, missing files). Pre-pipeline `raw_data_fixes()` patches 19 papers with extraction failures before this function runs.

**Key decisions:**
- Abstracts are AI-generated summaries, not original paper abstracts
- DUPLICATE resolution uses regex to extract original paper_id from abstract/title text
- 1 manual override for pid=528 (title-only DUPLICATE reference with no paper number in abstract)
- False positive guard: "editorial board" in text only triggers if it starts the abstract (not mentioned in passing)

### Variable 0d: `std_rq`

| Property | Value |
|----------|-------|
| Source column | `research_question` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 96.6% (3,691/3,821) |

**Approach:** Same cleanup pattern as `std_abstract`. Copy clean entries as-is. Recover DUPLICATE and "See paper X" entries from originals. Set remaining to NaN (editorials, OCR failures, non-research).

**Key decisions:**
- Research questions are AI-extracted, not original paper text
- "See paper X" cross-references (pid=726→725, pid=760→759) treated as recoverable like DUPLICATEs
- 147 empty entries are 83% Editorials/Other — legitimate gaps, not extraction failures

### Variable 0e: `std_findings`

| Property | Value |
|----------|-------|
| Source column | `key_findings` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 97.8% (3,736/3,821) |

**Approach:** Substantive cleanup beyond simple recovery. Three regex transformations strip redundant "Finding" occurrences while preserving meaningful hypothesis/proposition labels (H1:, H2:, P1:, etc.). Same DUPLICATE recovery pattern as `std_abstract` and `std_rq`.

**Cleanup rules:**
- `H1a/Finding:` → `H1a:` (hybrid labels — preserve hypothesis ID, strip redundant "Finding")
- `Finding N:` → remove (numbered findings like "Finding 1:", "Finding 2:" are redundant since the column IS findings)
- Standalone `Finding:` → remove (generic prefix adds no information)
- Double spaces collapsed; leading semicolons stripped

**Key decisions:**
- H1:/H2:/P1:/P2: prefixes are KEPT — they carry useful hypothesis/proposition information
- "Finding:" and "Finding N:" are REMOVED — they're redundant labels (the column is already findings)
- Same 3 DUPLICATE manual overrides as std_rq: pid=528→527, pid=726→725, pid=760→759
- 93 empty entries are almost entirely Editorials/Other — legitimate gaps

### Variable 0f: `std_gaps`

| Property | Value |
|----------|-------|
| Source column | `research_gaps_previous_lit` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 95.3% (3,641/3,821) |

**Approach:** Simple cleanup/recovery pass — no formatting issues in raw text (unlike `std_findings`). Copy clean entries as-is. Recover DUPLICATE and "See paper X" entries (same pattern as `std_abstract`, `std_rq`, `std_findings`). Set remaining to NaN.

**Key decisions:**
- Raw text is clean prose — no regex cleanup needed (unlike `std_findings` which had "Finding:" prefixes)
- Same 3 DUPLICATE manual overrides as std_rq/std_findings: pid=528→527, pid=726→725, pid=760→759
- 196 empty entries are predominantly Editorials/Other and N/A teaching cases — legitimate gaps where no prior-literature discussion exists

### Variable 0g: `std_future`

| Property | Value |
|----------|-------|
| Source column | `future_directions` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 94.5% (3,610/3,821) |

**Approach:** Same cleanup/recovery pattern as `std_gaps`. Copy clean entries as-is. Recover DUPLICATE and "See paper X" entries from originals. Set remaining to NaN.

**Key decisions:**
- Raw text is clean prose — no regex cleanup needed
- Same 3 DUPLICATE manual overrides: pid=528→527, pid=726→725, pid=760→759
- 211 empty entries are predominantly Editorials/Other — legitimate gaps where no future directions were discussed

### Variable 0h: `std_notes`

| Property | Value |
|----------|-------|
| Source column | `connections_and_notes` |
| Applies to | All papers |
| Multi-valued | No (single text per paper) |
| Coverage | 98.5% (3,764/3,821) |

**Approach:** Same cleanup/recovery pattern as `std_gaps` and `std_future`. Copy clean entries as-is. Recover DUPLICATE and "See paper X" entries from originals. Set remaining to NaN.

**Key decisions:**
- Raw text is clean prose — no regex cleanup needed
- Same 3 DUPLICATE manual overrides: pid=528→527, pid=726→725, pid=760→759
- 74 empty entries are predominantly NON-RESEARCH and OCR failures

### Variable 0i: `std_sample_description`

| Property | Value |
|----------|-------|
| Source column | `sample` |
| Applies to | All papers (but non-empirical papers are legitimately N/A) |
| Multi-valued | No (single text per paper) |
| Coverage | 78.7% (3,009/3,821) |

**Approach:** Same cleanup/recovery pattern. Copy clean entries as-is. Recover DUPLICATE and "See paper X" entries from originals. Set remaining to NaN.

**Key decisions:**
- Lower coverage (78.5%) is expected — 444 N/A entries from conceptual, editorial, formal model papers with no empirical sample
- Same 3 DUPLICATE manual overrides: pid=528→527, pid=726→725, pid=760→759
- 822 empty entries are predominantly non-empirical papers

### Variables 0j–0n: `std_iv`, `std_dv`, `std_mediators`, `std_moderators`, `std_controls`

| Variable | Source column | Coverage |
|----------|-------------|----------|
| `std_iv` | `independent_variables` | 75.7% (2,893/3,821) |
| `std_dv` | `dependent_variables` | 76.4% (2,918/3,821) |
| `std_mediators` | `mediators` | 21.6% (824/3,821) |
| `std_moderators` | `moderators` | 44.9% (1,715/3,821) |
| `std_controls` | `control_variables` | 47.3% (1,809/3,821) |

**Approach:** All five use the shared `_text_cleanup()` helper function — same cleanup/recovery pattern as all other text variables. Copy clean entries as-is, recover DUPLICATEs from originals, set rest to NaN. Same 3 manual DUPLICATE overrides for all.

**Key decisions:**
- Lower coverage rates are expected — these variables apply primarily to empirical-quantitative papers
- `std_mediators` at 21.5% is correct — most papers do not test mediation
- `std_controls` at 47.0% — only relevant for regression-type analyses
- Refactored into shared helper to eliminate code duplication across 5 nearly identical functions

### Variable 1: `std_paper_type`

| Property | Value |
|----------|-------|
| Source column | `paper_type` |
| Applies to | All papers |
| Multi-valued | No (single category per paper) |
| Coverage | 100% (3,821/3,821) |

**Categories (8):**

| Category | Definition |
|----------|-----------|
| Empirical-Quantitative | Surveys, archival, experiments, meta-analyses, scale development, QCA, etc. |
| Empirical-Qualitative | Case studies, grounded theory, ethnography, process studies, etc. |
| Empirical-Mixed | Explicitly mixed-methods designs |
| Conceptual | Theory building, frameworks, propositions, typologies |
| Review | Literature reviews, systematic reviews, bibliometrics |
| Editorial | Editorials, commentaries, SI intros, practitioner pieces, teaching cases |
| Formal Model | Mathematical/analytical/computational models (no empirical testing) |
| Other | Duplicates, OCR failures, retractions, non-research admin |

**Key decisions:**
- Meta-Analysis → Empirical-Quantitative (it IS quantitative empirical work)
- QCA → Empirical-Quantitative (set-theoretic, systematic, not interpretive)
- Formal Model separated from Conceptual (methodologically distinct)
- Teaching Cases → Editorial (not empirical research)
- 105 papers required manual overrides (ambiguous paper_type text)

### Variable 2: `std_method_design`

| Property | Value |
|----------|-------|
| Source columns | `method`, `data_source`, `sample`, `title` |
| Applies to | Empirical papers only (2,579 papers) |
| Multi-valued | Yes (semicolon-separated) |
| Coverage | 99.9% (2,577/2,579) |

**Categories (21):**

| Category | Key signals |
|----------|------------|
| Survey | "survey", "questionnaire", "Likert", "response rate", "self-report" |
| Experiment-Lab | "laboratory", "lab experiment", "student subjects", "behavioral game" |
| Experiment-Field | "field experiment", "RCT", "randomized", "random assignment to treatment" |
| Conjoint/Vignette | "vignette", "conjoint", "factorial design", "between-subjects", "2x2" |
| Quasi/Natural Experiment | "quasi-experiment", "natural experiment", "difference-in-differences" |
| Panel/Longitudinal | "panel", "longitudinal", "multi-year", "time-lag", year ranges |
| Cross-Sectional | "cross-sectional" (must be EXPLICIT, never assigned as residual) |
| Archival | "archival", "secondary data", named databases, "SEC filings", "patent data" |
| Case Study | "case study", "single case", "multiple case" |
| Interview/Fieldwork | "interview", "focus group", "ethnography", "participant observation" |
| Grounded Theory | "grounded theory", "Gioia", "open coding", "theoretical sampling" |
| Meta-Analysis | "meta-analysis", "meta-regression", "effect size pooling" |
| Content/Text Analysis | "content analysis", "NLP", "LIWC", "topic model", "sentiment" |
| QCA | "QCA", "fsQCA", "fuzzy-set" |
| Event Study | "event study", "cumulative abnormal return" |
| Simulation | "simulation study", "Monte Carlo", "agent-based model" |
| Scale Development | "scale development", "scale validation", "psychometric" |
| Diary/ESM | "diary", "experience sampling", "ESM", "day-level" |
| Bibliometric | "bibliometric", "citation analysis" |
| Delphi | "Delphi" |
| Action Research | "action research" |

**Key decisions:**
- Cross-Sectional is NOT a residual — only assigned when explicitly stated
- Papers can have multiple designs (e.g., Survey + Panel/Longitudinal)
- 78 papers required manual design overrides (35 original + 43 AI pass)

### Variable 3: `std_method_technique`

| Property | Value |
|----------|-------|
| Source columns | `method`, `data_source`, `sample`, `title`, `key_findings`, `abstract`, `independent_variables`, `dependent_variables`, `control_variables`, `connections_and_notes` |
| Applies to | Empirical papers only (2,579 papers) |
| Multi-valued | Yes (semicolon-separated) |
| Coverage | 99.9% (2,576/2,579) |

**Categories (24):**

| Category | Key signals |
|----------|------------|
| OLS/Linear Regression | "OLS", "linear regression", "hierarchical regression", "moderated regression" |
| Logistic/Limited DV | "logistic", "logit", "probit", "tobit", "negative binomial", "Poisson" |
| SEM/Path Analysis | "SEM", "structural equation", "path analysis", "PLS", "LISREL" |
| HLM/Multilevel | "HLM", "multilevel", "cross-level", "nested model" |
| Panel/Fixed Effects | "fixed effects", "random effects", "Hausman", "GMM" |
| Survival/Event History | "hazard", "survival analysis", "Cox", "Kaplan-Meier" |
| ANOVA/t-test | "ANOVA", "MANOVA", "t-test", "mean comparison" |
| Factor Analysis | "factor analysis", "CFA", "EFA", "PCA" |
| IV/Endogeneity Correction | "instrumental variable", "2SLS", "Heckman" |
| DiD/Matching | "difference-in-differences", "propensity score", "matching method" |
| QCA | "QCA", "fsQCA", "necessary condition" |
| Meta-Analytic Technique | "meta-analysis", "effect size", "HOMA" |
| Conjoint Analysis | "conjoint analysis", "part-worth", "utility score" |
| Event Study Technique | "event study", "cumulative abnormal return", "CAR" |
| Qualitative Coding | "grounded theory", "thematic analysis", "NVivo", "inductive analysis" |
| Descriptive/Exploratory | "descriptive", "chi-square", "cross-tabulation", "frequency analysis" |
| Network Analysis | "network analysis", "social network", "QAP", "ERGM" |
| Cluster/Latent Class | "cluster analysis", "latent class", "latent profile", "k-means" |
| Machine Learning/NLP | "machine learning", "random forest", "topic model", "LDA" |
| Bayesian | "Bayesian", "MCMC", "posterior" |
| Correlation | "correlation analysis", "Pearson", "Spearman" |
| Simulation Technique | "simulation", "Monte Carlo", "agent-based", "bootstrap" |
| Decomposition | "decomposition", "shift-share", "Blinder-Oaxaca" |
| Time Series | "time series", "VAR", "ARIMA", "cointegration", "Granger" |

**Key decisions:**
- Technique searches ALL useful columns (not just method/data_source/sample) because technique info often appears in findings or abstract
- Design-based inference: if no technique matches but paper is Empirical-Qualitative → assign Qualitative Coding; if Empirical-Mixed with qualitative designs → also assign Qualitative Coding
- "Hierarchical regression" = OLS/Linear Regression (it's a variant), NOT HLM
- "Mixed-effects" = HLM/Multilevel
- Generic "regression" without qualifier → OLS/Linear Regression
- 362 papers required manual technique overrides (all from AI intelligence pass)

### Variable 4: `std_country` / `std_region` / `std_continent`

| Property | Value |
|----------|-------|
| Source column | `country_context` |
| Applies to | All papers (but many are legitimately N/A) |
| Multi-valued | Yes (semicolon-separated; multi-country studies list all countries) |
| Coverage | 81.2% (3,104/3,821) — remaining 18.8% are genuinely N/A entries |

**std_country — 93 unique values (92 specific countries + "Multi-Country/Global"):**

Extracted using a 130-country reference table (COUNTRY_GEO) plus ~90 alias patterns covering demonyms (e.g., "Swiss" → Switzerland), US states (e.g., "Texas" → United States), Canadian provinces, UK constituents, and major city names (e.g., "Silicon Valley" → United States). Papers that explicitly study multiple countries, international samples, or global contexts without listing specific individual countries are assigned "Multi-Country/Global" (521 papers).

**std_region — 12 categories (UN geoscheme):**

| Region | Includes |
|--------|----------|
| Northern America | United States, Canada |
| Western Europe | Germany, France, Netherlands, Belgium, Switzerland, Austria, Luxembourg |
| Northern Europe | United Kingdom, Sweden, Finland, Norway, Denmark, Ireland, Iceland, Lithuania, Latvia, Estonia |
| Southern Europe | Italy, Spain, Portugal, Greece, Turkey, Croatia, Slovenia, Serbia, Cyprus, Malta, North Macedonia, Bosnia, Montenegro, Albania, Kosovo |
| Eastern Europe | Russia, Poland, Czech Republic, Hungary, Romania, Ukraine, Bulgaria, Slovakia, Belarus, Moldova |
| East Asia | China, Japan, South Korea, Taiwan, Hong Kong, Mongolia |
| South Asia | India, Pakistan, Bangladesh, Sri Lanka, Nepal |
| Southeast Asia | Singapore, Malaysia, Indonesia, Thailand, Vietnam, Philippines, Myanmar, Cambodia, Laos |
| Middle East & North Africa | Israel, UAE, Saudi Arabia, Iran, Egypt, Jordan, Lebanon, Qatar, Kuwait, Bahrain, Oman, Morocco, Tunisia, Algeria, Libya, Iraq, Palestine, Syria, Yemen |
| Sub-Saharan Africa | South Africa, Nigeria, Kenya, Ghana, Ethiopia, Tanzania, Uganda, Rwanda, Mozambique, Cameroon, Senegal, Zambia, Zimbabwe, Botswana, Namibia, Malawi, Ivory Coast, Congo DRC, Burkina Faso |
| Latin America & Caribbean | Brazil, Mexico, Chile, Colombia, Argentina, Peru, Ecuador, Costa Rica, Jamaica, Trinidad, Uruguay, Venezuela, Panama, El Salvador, Guatemala, Honduras, Nicaragua, Bolivia, Paraguay, Dominican Republic, Cuba, Puerto Rico, Barbados |
| Oceania | Australia, New Zealand, Fiji, Papua New Guinea, Samoa, Tonga |

**std_continent — 6 categories:**

| Continent | Derived from regions |
|-----------|---------------------|
| North America | Northern America |
| Europe | Western + Northern + Southern + Eastern Europe |
| Asia | East + South + Southeast Asia, Middle East & North Africa |
| South America | Latin America & Caribbean |
| Africa | Sub-Saharan Africa, Middle East & North Africa (African countries) |
| Oceania | Oceania |

**Key decisions:**
- Multi-country studies list ALL specific countries when identifiable; when only generic multi-country signals exist (e.g., "Global", "International", "42 countries"), assign "Multi-Country/Global"
- "Multi-Country/Global" papers get inferred continent(s) where possible (e.g., "European countries" → Europe) but no specific region
- Multi-country detection takes priority over N/A detection — e.g., "N/A (global literature review)" is classified as Multi-Country/Global, not left empty
- "Likely United States" entries were mostly handled by alias matching; 4 remaining "likely US" papers verified manually via MANUAL_COUNTRY_OVERRIDES
- N/A-type entries (conceptual papers with no country, editorials, "Not specified", "General", "Not applicable") receive empty values
- COUNTRY_ALIASES handles demonyms, sub-national entities, and common informal names
- Region/continent are automatically derived from the country lookup — no separate classification step

---

### Variable 5: `std_theory_L1_discipline` / `std_theory_L2_name`

| Property | Value |
|----------|-------|
| Source column | `theoretical_lens` |
| Applies to | All papers (but editorials/other often have no formal theory) |
| Multi-valued | Yes (semicolon-separated; papers can use multiple theories) |
| Coverage | 88.9% (3,395/3,821) — remaining 11.1% are mostly editorials, "Other", and applied/practitioner papers |

**std_theory_L2_name — 166 canonical theory names:**

Extracted using a curated THEORY_CATALOG of ~160 canonical theories with ~300+ regex alias patterns. A `_clean_theory_text()` function strips parenthetical citations (e.g., "Resource-based view (Barney, 1991)" → "Resource-based view") before matching. Each raw theory string is matched to at most one canonical L2 name using a first-match-wins strategy. Top 10: Institutional Theory (316), Resource-Based View (271), Agency Theory (253), Social Network Theory (165), Human Capital Theory (158), Signaling Theory (133), Strategic Management (118), Social Capital Theory (111), Cognitive Psychology (102), Research Methodology (88).

**std_theory_L1_discipline — 9 broad disciplinary categories:**

| Discipline | Description | Example L2 theories |
|------------|-------------|---------------------|
| Economics | Classical/behavioral economics | Agency Theory, Transaction Cost Economics, Game Theory, Labor Economics |
| Psychology | Cognitive, motivational, affective | Cognitive Psychology, Self-Efficacy Theory, Affect Theory, Personality Psychology |
| Sociology | Social structures, networks, culture | Social Network Theory, Social Capital Theory, Feminist Theory, Cultural Theory |
| Management / Strategy | Firm-level strategic frameworks | Resource-Based View, Dynamic Capabilities, Competitive Strategy, Upper Echelons Theory |
| Organizational Theory | Org-level behavior and structure | Organizational Learning, Organizational Ecology, Contingency Theory, Process Theory |
| Entrepreneurship-Specific | Theories unique to entrepreneurship | Effectuation Theory, Opportunity Theory, Entrepreneurial Orientation, Corporate Entrepreneurship |
| Finance | Financial markets, valuation, investment | Venture Capital Theory, Capital Structure Theory, Behavioral Finance, IPO Theory |
| Institutional Theory | Institutions, legitimacy, isomorphism | Institutional Theory, Institutional Entrepreneurship, Legitimacy Theory, Institutional Economics |
| Methodology / Philosophy | Research methods, epistemology | Research Methodology, Philosophy of Science, Grounded Theory |

L1 is derived from the L2-to-L1 mapping in the THEORY_CATALOG. Each L2 theory belongs to exactly one L1 discipline, but a paper can span multiple disciplines if it uses theories from different traditions.

**Approach:** Two-pass — rule-based regex matching against THEORY_CATALOG (Pass 1, 80.2% paper-level coverage), then AI intelligence pass classifying 335 additional papers from 442 unmatched substantive entries as MANUAL_THEORY_OVERRIDES (Pass 2, pushing to 88.9%). The remaining 426 uncovered papers include 284 editorials/other and 142 substantive papers using applied/practitioner frameworks (financial management, tax law, HRM, technology adoption) that do not map to formal theories.

---

### Variable 6: `std_dsType` / `std_dsNamed`

| Property | Value |
|----------|-------|
| Source columns | `data_source` (primary), `method` (fallback for dsType), `sample` (for dsNamed) |
| Applies to | All papers (but non-empirical papers are legitimately N/A) |
| Multi-valued | Yes (semicolon-separated; papers can have multiple data source types and named datasets) |
| Coverage | std_dsType: 80.2% overall (3,066/3,821), 99.8% empirical (2,557/2,561); std_dsNamed: 24.3% overall (929/3,821), 33.4% empirical (862/2,579), 38.1% Empirical-Quantitative |

**std_dsType — 9 data source type categories:**

| Category | Definition | Key signals |
|----------|-----------|-------------|
| Archival/Database | Secondary data from existing records | "archival", "secondary data", named databases, "SEC filings", "firm-level data" |
| Survey/Questionnaire | Primary data via structured instruments | "survey", "questionnaire", "Likert", "response rate", "self-report" |
| Interview | Primary data via conversations | "interview", "focus group", "informants", "semi-structured" |
| Government/Administrative | Official government or administrative records | "census", "tax records", "government data", national statistics agencies |
| Case Study | In-depth study of specific cases | "case study", "single case", "multiple case", "in-depth investigation" |
| Experiment | Controlled experimental data | "experiment", "treatment group", "control group", "manipulation" |
| Ethnographic/Observational | Field observation or participatory research | "ethnograph", "participant observation", "field notes", "observational" |
| Online/Digital Data | Web-scraped or digital platform data | "crowdfunding", "social media", "web scraping", "online platform", "digital trace" |
| Simulation/Formal | Computer-generated or formal model data | "simulation", "Monte Carlo", "agent-based", "computational model" |

**Key decisions:**
- No "Mixed Primary" category needed — multi-valued format handles this naturally (e.g., "Survey/Questionnaire; Interview")
- Government/Administrative separated from Archival/Database because government statistics are a distinctive data tradition in entrepreneurship research
- Ethnographic/Observational separated from Interview because ethnography involves sustained field presence beyond just interviews
- Named dataset inference rule: if a named dataset is detected (e.g., Compustat, GEM) but no dsType pattern matched, auto-assign "Archival/Database"
- Method column fallback: if data_source text alone doesn't match any pattern, check method column as well
- 31 papers required manual overrides (corrected title[:40] keys essential)

**std_dsNamed — 313 unique canonical dataset names:**

Extracted using three layers: (1) NAMED_DATASET_CATALOG of ~195 canonical datasets with ~450+ alias regex patterns; (2) ~130 manual AI-identified overrides for papers with named datasets described in natural language; (3) all aliases normalize to a single canonical name (e.g., "PSED" and "Panel Study of Entrepreneurial Dynamics" → "PSED"; "CFPS" and "China Family Panel Studies" → "CFPS"). Top 10: Patent Data (60), IPO Prospectuses/Data (56), VentureXpert (48), Compustat (44), GEM (44), Kickstarter (41), World Bank (39), VC Database (37), PSED (36), SEC/EDGAR (34).

**Approach:** Three-layer extraction with manual overrides. DS_TYPE_PATTERNS dict contains ~150 regex patterns across 9 categories, compiled into a single regex per category. Named datasets are extracted from concatenated text of data_source + method + sample columns using both regex catalog and manual AI overrides (MANUAL_DS_NAMED_OVERRIDES dict with ~130 entries from two AI intelligence passes). The inference rule (named dataset found → Archival/Database if no other dsType matched) catches papers whose data_source mentions specific databases without generic archival keywords. 31 manual dsType overrides handle edge cases where neither regex nor inference could classify.

---

### Variable 7: `std_tpL1` / `std_tpL2`

| Property | Value |
|----------|-------|
| Source columns | `topic_tags` (primary) |
| Applies to | All papers (meta-scholarship papers are legitimately N/A) |
| Multi-valued | Yes (semicolon-separated; papers can belong to multiple topic domains) |
| Coverage | std_tpL1: 93.1% (3,558/3,821); std_tpL2: 93.1% (3,558/3,821) |

**std_tpL1 — 15 broad topic domains:**

| L1 Category | Description |
|-------------|-------------|
| Entrepreneurial Finance | VC, crowdfunding, IPO, angel investing, PE, microfinance, capital structure |
| Family Business | Family firms, succession, SEW, governance, familiness |
| Corporate Entrepreneurship | CE, CVC, intrapreneurship, strategic entrepreneurship, NPD |
| Social Entrepreneurship | Social enterprise, hybrid orgs, sustainability, poverty alleviation |
| International Entrepreneurship | Internationalization, born globals, emerging markets, cross-cultural |
| Innovation & Technology | R&D, patents, IP, tech transfer, biotech, academic entrepreneurship |
| Entrepreneurial Cognition & Psychology | Cognition, emotions, biases, passion, self-efficacy, well-being, identity |
| Entrepreneurial Process | Opportunity recognition/creation, venture creation, effectuation, bricolage |
| Strategy & Performance | EO, firm performance/growth, competitive advantage, business models |
| Networks & Social Capital | Social capital, networks, trust, alliances, embeddedness |
| Small Business & SMEs | Small business management, franchising, SME performance |
| Gender & Diversity | Women entrepreneurship, gender differences, minority/immigrant entrepreneurship |
| Institutions & Context | Institutional theory, culture, informal economy, institutional voids |
| Human Capital & Teams | Human capital, teams, founder characteristics, HRM, leadership |
| Policy & Economic Development | Entrepreneurship policy, self-employment, ecosystems, economic development |

**std_tpL2 — 77 subtopic categories** within the 15 L1 domains. Each L2 maps to exactly one L1 parent. Examples: "Venture Capital" → Entrepreneurial Finance; "Succession" → Family Business; "Born Globals" → International Entrepreneurship.

**Approach:** Regex-based classification of individual tags from `topic_tags`. Tags are split by comma/semicolon delimiters, lowercased, and matched against a TOPIC_TAXONOMY dict of 15 L1 × 77 L2 with ~300+ keyword regex patterns. Meta-scholarship tags (research methodology, editorials, field development) are explicitly skipped. The 6.9% unclassified papers are almost entirely meta-scholarship.

**Key decisions:**
- Multi-valued L1: papers can belong to multiple domains (e.g., a VC paper about family firms gets both "Entrepreneurial Finance" and "Family Business")
- Meta-scholarship excluded: editorials, research methodology, field development papers are intentionally unclassified
- Country names excluded from topic matching (already captured in std_country)
- Dataset names excluded from topic matching (already captured in std_dsNamed)
- Theory names excluded from topic matching (already captured in std_theory_L2_name)

### Variable 0p: `std_flag`

| Property | Value |
|----------|-------|
| Source column | `title`, `abstract`, `paper_type`, `journal` (raw), `std_paper_type`, `std_journal` |
| Applies to | All papers |
| Multi-valued | No (single flag per paper) |
| Coverage | 100% (3,821/3,821) |

**Values (5):**

| Flag | Count | Description |
|------|-------|-------------|
| OK | 3,511 (91.9%) | Clean paper — include in web app |
| DUPLICATE | 238 (6.2%) | Duplicate entry of another paper (68 keyword-based + 170 title-based) |
| NON_RESEARCH | 57 (1.5%) | Administrative content, wrong-journal papers, or out-of-scope entries |
| OCR_FAILED | 12 (0.3%) | Extraction/OCR failure with insufficient content |
| RETRACTED | 3 (0.1%) | Retracted papers, corrigenda, or errata |

**Approach:** Seven-rule cascade in two passes. Rules 1–6 run per-paper (first match wins), checking title, abstract, raw paper_type, raw journal, std_journal, and std_paper_type for keywords. Rule 7 is a second pass that detects remaining duplicates by exact title match among OK-flagged papers, keeping the copy with the most filled std_ fields. Runs last in the pipeline (after all std_ variables are populated) so it can check std_ columns for content quality and title-based dedup.

**Rules:**
1. DUPLICATE — title/abstract starts with "DUPLICATE", or raw journal/paper_type is "DUPLICATE"
2. RETRACTED — title/type contains "retract", "corrigendum", "erratum"
3. OCR_FAILED — title/type contains OCR failure keywords
4. NON_RESEARCH — title/type contains admin keywords (editorial board, TOC, etc.)
5. NON_RESEARCH — std_journal is "Other" (wrong journal, out of scope)
6. OCR_FAILED — std_paper_type is "Other" with no substantive content (<10 chars in RQ/findings, <20 in abstract)
7. DUPLICATE — title-based dedup: among OK papers, flag lower-quality copies of same-title papers

**Key decisions:**
- Uses `'OK'` (not empty string) for clean papers — avoids NaN when Excel serializes empty strings
- Substantive editorials, commentaries, teaching cases are NOT flagged — they are legitimate scholarly content
- DUPLICATE papers with recovered std_ fields are still flagged (recovery was for analytical convenience)
- Title-based dedup (Rule 7) catches duplicates the extractor created without flagging them
- Papers from out-of-scope journals (e.g., JSBM, SBE) are flagged NON_RESEARCH via Rule 5

---

## Adapting to a New Paper Database

When the user has a new/different paper database, the codebook has **reusable** and **database-specific** components:

### What is REUSABLE (keep as-is)
These components encode domain knowledge and will work on any entrepreneurship paper database:
- **Category definitions** — the 8 paper types, 21 method designs, 24 techniques, 9 data source types, 15 topic L1 domains, 77 topic L2 subtopics, 9 theory disciplines, 166 canonical theory names
- **Regex pattern libraries** — `PAPER_TYPE_RULES`, `DESIGN_PATTERNS`, `TECHNIQUE_PATTERNS`, `DS_TYPE_PATTERNS`, `NAMED_DATASET_CATALOG`, `THEORY_CATALOG`, `TOPIC_TAXONOMY`, `COUNTRY_GEO`, `COUNTRY_ALIASES`
- **Helper functions** — `_text_cleanup()`, `_clean_theory_text()`, `_extract_country_from_text()`, `_list_to_str()`
- **Architecture** — the two-layer approach (rules + manual overrides), the PIPELINE execution order, the `std_flag` cascade logic
- **NaN handling patterns** — `pd.notna(x) and str(x).strip() not in ('', 'nan', 'N/A')`

### What is DATABASE-SPECIFIC (must be cleared/rewritten)
These components are specific to the current ETP/JBV/SEJ database:
- **`raw_data_fixes()`** — contains fixes for 19 specific papers. **Clear entirely** for a new database (set to `def raw_data_fixes(df): return df`). Re-populate only if you discover extraction failures in the new database
- **All `MANUAL_*_OVERRIDES` dicts** — `PASS2_OVERRIDES`, `MANUAL_DESIGN_OVERRIDES`, `MANUAL_TECHNIQUE_OVERRIDES`, `MANUAL_COUNTRY_OVERRIDES`, `MANUAL_THEORY_OVERRIDES`, `MANUAL_DS_TYPE_OVERRIDES`, `MANUAL_DS_NAMED_OVERRIDES`. **Clear all** to empty dicts `{}`. These will be repopulated during the AI intelligence pass on the new database
- **`YEAR_CORRECTIONS`** — 17 corrections specific to this database. **Clear to empty dict**
- **`JOURNAL_SPECIFIC_OVERRIDES`** — **Clear to empty dict**
- **Configuration paths** — `RAW_DIR`, `RAW_FILES`, `OUTPUT_FILE`

### Step-by-step for a new database

1. **Copy the codebook** to the new project's standardization folder
2. **Update configuration paths** — `RAW_DIR`, `RAW_FILES`, `OUTPUT_FILE`
3. **Clear all database-specific components** (see list above)
4. **Verify column names** — the codebook expects: `paper_id`, `title`, `authors`, `year`, `journal`, `paper_type`, `abstract`, `research_question`, `key_findings`, `research_gaps_previous_lit`, `future_directions`, `connections_and_notes`, `sample`, `data_source`, `method`, `country_context`, `theoretical_lens`, `independent_variables`, `dependent_variables`, `mediators`, `moderators`, `control_variables`, `topic_tags`, `pdf_filename`. If the new database uses different column names, add mapping logic in `load_raw_data()`
5. **Run the codebook** — `python standardization_codebook.py`
6. **Check coverage** for each variable — the rule-based layer should handle 85–98% of papers
7. **Run AI intelligence passes** on unmatched papers for each variable (Step 5 in Pipeline section)
8. **Record new manual overrides** in the codebook for the new database's papers
9. **Investigate data quality** — check for OCR failures, duplicates, and extraction errors. Add fixes to `raw_data_fixes()` as needed
10. **Re-run and verify** — final pipeline run should achieve 99%+ coverage on all categorical variables

### If you need different categories
1. Modify the category definitions and regex patterns in the codebook
2. Update this skill document's category tables
3. The two-layer architecture (rules + AI overrides) remains the same

---

## Adding a New Variable

When the user wants to standardize a new variable:

1. **Add a new function** in the codebook following the existing pattern:
   ```python
   def std_new_variable(df):
       """
       Variables: new_variable_name
       Source column(s): ...
       Date finalized: YYYY-MM-DD
       Decision rationale: ...
       """
       # Rules, overrides, matching logic
       return df
   ```

2. **Add the function to PIPELINE**:
   ```python
   PIPELINE = [
       raw_data_fixes,  # ← patches raw data for 19 papers with extraction failures
       std_year,
       std_journal,
       std_abstract,
       std_rq,
       std_findings,
       std_gaps,
       std_future,
       std_notes,
       std_sample_description,
       std_iv,
       std_dv,
       std_mediators,
       std_moderators,
       std_controls,
       std_paper_type,
       std_method_design_and_technique,
       std_country_region_continent,
       std_theory_L1_L2,
       std_data_source_type_and_named,
       std_topic_L1_L2,
       std_new_variable,  # ← add BEFORE std_flag
       std_flag,          # ← std_flag must ALWAYS be last (uses std_ columns for content checks)
   ]
   ```

3. **Update this skill document** — add the new variable to the "Currently Standardized Variables" section above

4. **Follow Steps 1–7** from the Pipeline section to develop, iterate, and finalize the variable

---

## AI Intelligence Classification Guidelines

These guidelines apply when classifying any variable using Claude's comprehension (the AI pass):

### General principles
- Read ALL available metadata for each paper, not just the primary column
- When in doubt, err on leaving empty rather than guessing
- Multi-valued categories use semicolons: `"Category A; Category B"`
- Sort categories alphabetically within each cell for consistency
- Do not overwrite existing classifications — only fill in empty cells
- Process in batches of ~120 papers; use parallel subagents for sets > 100

### For std_method_design specifically
- Look at what TYPE of study was conducted, not what analysis was run
- "Regression analysis" alone doesn't tell you the design — check data_source
- Named database → likely Archival
- Interviews/questionnaires as primary data → Survey or Interview/Fieldwork
- "Experimental design" without specifics → default to Conjoint/Vignette
- Do NOT assign Cross-Sectional as residual

### For std_country / std_region / std_continent specifically
- Uses a top-down lookup approach (COUNTRY_GEO table + COUNTRY_ALIASES), NOT regex pattern matching
- Multi-country studies get all specific countries listed, each separated by semicolons
- When no specific countries can be extracted but multi-country signals exist → "Multi-Country/Global"
- Regions and continents are derived automatically from the country — never assign region/continent independently
- "Likely [Country]" or "Inferred [Country]" entries: if a country name appears in the text, extract it; if not, use MANUAL_COUNTRY_OVERRIDES after verification
- Entries with only generic N/A terms ("Not specified", "General", "Not applicable") and no multi-country signal → leave empty
- Do NOT classify conceptual, editorial, or review papers unless they explicitly study a country or are explicitly multi-country/global

### For std_theory_L1_discipline / std_theory_L2_name specifically
- Prefer EXISTING L2 canonical names from the 166-entry catalog — only propose new ones if truly needed
- Be generous in mapping: "innovation efficiency theory" → Innovation Theory; "organizational change theory" → Organizational Learning
- If theoretical_lens says "N/A", "atheoretical", "practitioner-oriented", or "teaching case" → leave EMPTY unless the paper is clearly about a recognized entrepreneurship framework
- Applied/vocational frameworks (tax planning, financial ratios, cash management) are NOT formal theories — leave empty
- Papers can have MULTIPLE L2 theories (semicolon-separated); assign all that clearly apply
- L1 is derived from L2 — ensure consistency with the L2-to-L1 mapping in THEORY_CATALOG
- Strip parenthetical citations before matching (the codebook does this automatically)

### For std_dsType / std_dsNamed specifically
- Classify the TYPE of data source, not the method of analysis — "regression on archival data" → Archival/Database
- If a named dataset is mentioned but no dsType matched → infer Archival/Database
- Government statistical agencies (e.g., Statistics Sweden, US Census Bureau, BLS) → Government/Administrative
- Crowdfunding platforms (Kickstarter, Indiegogo) → Online/Digital Data
- Papers can have multiple dsTypes — a mixed-methods paper using interviews AND survey data gets "Interview; Survey/Questionnaire"
- For std_dsNamed, always normalize to canonical names — check NAMED_DATASET_CATALOG for existing entries before adding new ones
- Only extract named datasets when the paper actually USES the dataset as data, not just cites it in the literature review

### For std_method_technique specifically
- Look at what ANALYTICAL METHOD was used
- Generic "regression" → OLS/Linear Regression
- "Hierarchical regression" → OLS/Linear Regression (NOT HLM)
- "Multilevel modeling" → HLM/Multilevel
- If technique is only hinted at in findings/abstract but not method column, still classify
- If design is qualitative and no technique stated → Qualitative Coding

---

## Lessons Learned

Key issues encountered during standardization (reference for future work):

1. **Trailing `\b` on truncated stems is the #1 regex bug.** Example: `\bcase\s+stud\b` fails on "case study". Always remove trailing `\b` when the pattern ends mid-word. This single fix improved technique coverage from 34% to 65%.

2. **NaN handling requires explicit checks.** `str(NaN).strip()` returns `"nan"` which evaluates as truthy. Always use: `pd.notna(x) and str(x).strip() not in ('', 'nan', 'N/A')`

3. **Paper IDs can duplicate across journals.** Use `(paper_id, title[:40])` tuple keys for manual overrides.

4. **Technique info is scattered across many columns.** The `method` column alone yields ~65% coverage; adding key_findings, abstract, IVs, DVs, controls, and connections_and_notes pushes rule-based coverage to ~86%.

5. **Design-based inference helps technique coverage.** Qualitative papers almost always use Qualitative Coding even if not stated explicitly.

6. **Apostrophes in titles break Python string literals.** When generating override dictionaries from AI batch results, escape or use double quotes for titles containing apostrophes.

7. **Title prefix matching must be ≤ 40 characters.** The codebook uses `title[:40]` — ensure override keys don't exceed this length.

8. **Country extraction benefits from aliases over regex.** Direct country name matching plus a curated alias list (demonyms, state names, city names) achieved ~95% coverage of extractable entries without needing an AI pass. The top-down lookup approach (known country list → match against text) is more reliable than bottom-up extraction (parse text → infer country).

9. **Many papers legitimately have no country.** ~33% of papers in the database are conceptual, editorial, or don't specify a country. These should remain empty, not be force-classified.

10. **Theory text requires citation stripping before matching.** Raw `theoretical_lens` entries frequently contain parenthetical citations (e.g., "Resource-based view (Barney, 1991)"). A `_clean_theory_text()` preprocessing step that strips these patterns improved rule-based matching significantly.

11. **Applied/practitioner frameworks resist theory classification.** Older small-business papers (1970s–1990s) often use applied frameworks (financial ratios, tax planning, cash management, HRM practices) that are not formal theories. These are best left unclassified rather than force-fitted into the L1/L2 scheme.

12. **Two-level theory taxonomy (L1 discipline + L2 canonical name) balances breadth and specificity.** The 9 L1 categories enable cross-disciplinary analysis while 166 L2 names preserve theoretical precision. The L2-to-L1 mapping is fixed in the THEORY_CATALOG to ensure consistency.

13. **Named dataset inference is a powerful coverage booster.** Many papers mention specific databases (e.g., "Compustat", "GEM") without using generic archival keywords. The rule "if named dataset detected but no dsType matched → Archival/Database" caught dozens of papers that would otherwise be unmatched.

14. **Plural regex gotcha: `\bsurvey\b` doesn't match "surveys".** The word boundary `\b` at the end prevents matching when the word continues. Fix: use `\bsurveys?\b` (optional 's') or `\bsurvey\w*` (any suffix). This applies to all pattern-based matching.

15. **Manual override title prefixes must be exact.** When building MANUAL_*_OVERRIDES, the title[:40] key must match the actual title in the dataframe exactly. Guessing or paraphrasing titles causes overrides to silently fail. Always query the dataframe for exact title[:40] values before writing overrides.
