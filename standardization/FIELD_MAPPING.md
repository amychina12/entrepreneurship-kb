# Field Mapping Reference

**Database:** Entrepreneurship Knowledge Base
**Papers:** 3,821 across ETP, JBV, SEJ (1968–2025)
**Last updated:** 2026-03-10

---

## Column Overview

| # | Column | Type | Fill Rate | Description |
|---|--------|------|-----------|-------------|
| 1 | `paper_id` | Raw | 100% | Numeric ID assigned during extraction. **Not globally unique** — 33 IDs are shared across journals. Use `(paper_id, title[:40])` for deduplication. |
| 2 | `authors` | Raw | 100% | Author names, semicolon-separated. |
| 3 | `year` | Raw | 99.8% | Publication year. Range: 1968–2025 (mixed types: integers, NaN, 0, strings). Superseded by `std_year`. |
| 4 | `title` | Raw | 99.8% | Full paper title. 3,633 unique values (some duplicates from replication/DUPLICATE entries). |
| 5 | `journal` | Raw | 99.3% | Journal name. 20 distinct values + 28 NaN. Superseded by `std_journal`. |
| 6 | `paper_type` | Raw | 100% | Free-text paper type from extraction. 431 unique values — highly inconsistent (e.g., "Empirical-qualitative", "empirical quantitative study", "Conceptual/Theoretical"). Superseded by `std_paper_type`. |
| 7 | `topic_tags` | Raw | 99.8% | Comma-separated topic keywords generated during extraction. |
| 8 | `abstract` | Raw | 99.5% | AI-generated paper summary (not original abstract). Contains placeholder text for DUPLICATEs, OCR failures, and editorials. Superseded by `std_abstract`. |
| 9 | `research_gaps_previous_lit` | Raw | 96.9% | AI-extracted description of research gaps the paper addresses. Superseded by `std_gaps`. |
| 10 | `research_question` | Raw | 97.2% | AI-extracted research question(s). Contains placeholders for DUPLICATEs, OCR failures, and non-research. Superseded by `std_rq`. |
| 11 | `theoretical_lens` | Raw | 96.7% | Theories, frameworks, or perspectives used in the paper. Superseded by `std_theory_L1_discipline` and `std_theory_L2_name`. |
| 12 | `independent_variables` | Raw | 86.2% | AI-extracted IVs or key constructs explored. Superseded by `std_iv`. |
| 13 | `dependent_variables` | Raw | 83.4% | AI-extracted DVs or outcome constructs. Superseded by `std_dv`. |
| 14 | `mediators` | Raw | 23.1% | AI-extracted mediating variables. Low fill rate because most papers don't have mediators. Superseded by `std_mediators`. |
| 15 | `moderators` | Raw | 46.0% | AI-extracted moderating variables. Superseded by `std_moderators`. |
| 16 | `control_variables` | Raw | 51.7% | AI-extracted control variables. Only relevant for empirical papers with regression-type analyses. Superseded by `std_controls`. |
| 17 | `sample` | Raw | 90.7% | AI-extracted sample description (who, how many, where). Superseded by `std_sample_description`. |
| 18 | `data_source` | Raw | 89.0% | Data source description (surveys, databases, interviews, etc.). Superseded by `std_dsType` and `std_dsNamed`. |
| 19 | `country_context` | Raw | 92.9% | Country or region studied. 1,304 unique values — free-text. Superseded by `std_country`. |
| 20 | `method` | Raw | 98.8% | Free-text method description. Primary source for `std_method_design` and `std_method_technique`. |
| 21 | `key_findings` | Raw | 98.8% | AI-extracted findings with messy formatting ("Finding 1:", "Finding:", "H1/Finding:"). Superseded by `std_findings`. |
| 22 | `future_directions` | Raw | 96.0% | AI-extracted future research directions suggested by the paper. Superseded by `std_future`. |
| 23 | `connections_and_notes` | Raw | 99.3% | AI-extracted cross-references, theoretical connections, and extraction notes. Superseded by `std_notes`. |
| 24 | `pdf_filename` | Raw | 100% | Original PDF filename (format: "YEAR - Title - Authors.pdf"). |
| 25 | `std_year` | **Standardized** | 100% | Cleaned integer publication year. Range: 1968–2025. 17 corrections applied. See details below. |
| 26 | `std_journal` | **Standardized** | 100% | Standardized journal: ETP, JBV, SEJ, or Other. See details below. |
| 27 | `std_abstract` | **Standardized** | 99.1% | Cleaned AI-generated summary. DUPLICATE entries recovered from originals. See details below. |
| 28 | `std_rq` | **Standardized** | 96.6% | Cleaned AI-extracted research question. DUPLICATE/cross-ref entries recovered from originals. See details below. |
| 29 | `std_findings` | **Standardized** | 97.8% | Cleaned AI-extracted findings. Redundant "Finding:" prefixes stripped, DUPLICATEs recovered. See details below. |
| 30 | `std_gaps` | **Standardized** | 95.3% | Cleaned AI-extracted research gaps. DUPLICATEs recovered from originals. See details below. |
| 31 | `std_future` | **Standardized** | 94.5% | Cleaned AI-extracted future research directions. DUPLICATEs recovered from originals. See details below. |
| 32 | `std_notes` | **Standardized** | 98.5% | Cleaned AI-extracted cross-references and notes. DUPLICATEs recovered from originals. See details below. |
| 33 | `std_sample_description` | **Standardized** | 78.7% | Cleaned AI-extracted sample description. DUPLICATEs recovered from originals. See details below. |
| 34 | `std_iv` | **Standardized** | 75.7% | Cleaned AI-extracted independent variables. DUPLICATEs recovered. See details below. |
| 35 | `std_dv` | **Standardized** | 76.4% | Cleaned AI-extracted dependent variables. DUPLICATEs recovered. See details below. |
| 36 | `std_mediators` | **Standardized** | 21.6% | Cleaned AI-extracted mediating variables. DUPLICATEs recovered. See details below. |
| 37 | `std_moderators` | **Standardized** | 44.9% | Cleaned AI-extracted moderating variables. DUPLICATEs recovered. See details below. |
| 38 | `std_controls` | **Standardized** | 47.3% | Cleaned AI-extracted control variables. DUPLICATEs recovered. See details below. |
| 39 | `std_paper_type` | **Standardized** | 100% | 8 mutually exclusive categories. See details below. |
| 40 | `std_method_design` | **Standardized** | 99.9%* | 21 categories, multi-valued. Empirical papers only. See details below. |
| 41 | `std_method_technique` | **Standardized** | 99.9%* | 24 categories, multi-valued. Empirical papers only. See details below. |
| 42 | `std_country` | **Standardized** | 81.2%** | Country name(s) or "Multi-Country/Global" from `country_context`. Multi-valued (semicolon-separated). 93 unique values. See details below. |
| 43 | `std_region` | **Standardized** | 81.2%** | UN geoscheme region(s) derived from `std_country`. 12 regions. See details below. |
| 44 | `std_continent` | **Standardized** | 81.2%** | Continent(s) derived from `std_country`. 6 continents. See details below. |
| 45 | `std_theory_L1_discipline` | **Standardized** | 88.9%*** | 9 broad theoretical disciplines. Multi-valued (semicolon-separated). See details below. |
| 46 | `std_theory_L2_name` | **Standardized** | 88.9%*** | 166 canonical theory names. Multi-valued (semicolon-separated). See details below. |
| 47 | `std_dsType` | **Standardized** | 80.2%**** | 9 data source type categories. Multi-valued (semicolon-separated). See details below. |
| 48 | `std_dsNamed` | **Standardized** | 24.3%**** | Named dataset(s) extracted and alias-normalized. 313 unique canonical names. Multi-valued (semicolon-separated). See details below. |
| 49 | `std_tpL1` | **Standardized** | 93.1%***** | 15 broad topic domains. Multi-valued (semicolon-separated). See details below. |
| 50 | `std_tpL2` | **Standardized** | 93.1%***** | 77 specific subtopic categories within the 15 L1 domains. Multi-valued (semicolon-separated). See details below. |
| 51 | `std_flag` | **Standardized** | 100% | Quality flag: OK (clean, 96.4%), DUPLICATE, OCR_FAILED, RETRACTED, or NON_RESEARCH. Use `std_flag == 'OK'` to filter for web app. See details below. |

*Coverage percentages for `std_method_design` and `std_method_technique` are relative to the 2,579 empirical papers they apply to, not to all 3,821 papers. Their fill rate across all papers is 67.4% because non-empirical papers (1,242) receive empty values by design.

**Coverage for `std_country`, `std_region`, and `std_continent` is 81.2% (3,104/3,821). The remaining 18.8% are legitimately N/A — conceptual papers with no country, editorials, papers with "Not specified", "General", "Not applicable", DUPLICATE entries, and papers with no `country_context` text at all.

***Coverage for `std_theory_L1_discipline` and `std_theory_L2_name` is 88.9% (3,395/3,821). The remaining 11.1% (426 papers) breaks down as: 164 Editorials, 120 Other, 86 Empirical-Quantitative, 34 Conceptual, 14 Empirical-Qualitative, 6 Review, 1 Formal Model, 1 Empirical-Mixed. Most uncovered substantive papers (142) use applied/practitioner frameworks (financial management, tax law, HRM, technology adoption) that do not map cleanly to formal theories.

*****Coverage for `std_tpL1` and `std_tpL2` is 93.1% (3,558/3,821). The remaining 6.9% (263 papers) are predominantly meta-scholarship: editorials, research methodology papers, field development articles, DUPLICATE entries, and non-research content. These do not map to substantive research topics.

****Coverage for `std_dsType` is 80.2% (3,066/3,821) across all papers. Among empirical papers specifically, coverage is 99.8% (2,557/2,561). The remaining 19.8% are legitimately N/A — editorials, conceptual papers, reviews, and formal models that have no empirical data source. For `std_dsNamed`, 24.3% (929/3,821) overall; among empirical papers, 33.4% (862/2,579) reference a named dataset. Coverage is highest for Empirical-Quantitative papers (38.1%). The remaining empirical papers use primary data collection (surveys, interviews, experiments) or non-specific archival sources with no recognizable named dataset.

---

## Standardized Variables — Detail

### `std_year` — 100% coverage (3,821/3,821)

Clean integer publication year derived from the raw `year` column. Range: 1968–2025.

The raw `year` column had 17 problematic entries: 6 NaN, 2 with year=0, 1 with year='Unknown' (OCR failure), and 8 with year='DUPLICATE' (string values). All 17 were manually corrected using web searches, PDF metadata extraction, and year information embedded in DUPLICATE title strings.

**Approach:** `pd.to_numeric(df['year'], errors='coerce')` converts the mixed-type column to numeric, then 17 manual corrections are applied via a YEAR_CORRECTIONS lookup dict keyed by `(paper_id, title[:40])`. Final column uses `Int64` nullable integer dtype.

### `std_journal` — 100% coverage (3,821/3,821)

Standardized journal assignment. 4 categories: ETP, JBV, SEJ, Other.

| Category | Count | % |
|----------|-------|---|
| ETP | 1,850 | 48.4% |
| JBV | 1,516 | 39.7% |
| SEJ | 453 | 11.9% |
| Other | 2 | 0.1% |

The raw `journal` column had 20 distinct values plus 28 NaN entries. Issues included: ETP spelling variants ("Entrepreneurship: Theory and Practice", "Entrepreneurship Theory & Practice"), the predecessor journal "American Journal of Small Business" (221 papers, renamed to ETP in 1988), 15 DUPLICATE entries with journal="DUPLICATE", 28 NaN entries, and 16 papers with incorrect journal names from extraction errors (JSBM, SBE, FBR, etc.).

**Approach:** Three-layer resolution: (1) PDF folder lookup — each paper's `pdf_filename` is matched against the ETP/JBV/SEJ folders in `1_raw_pdfs/`, providing ground truth for 3,349 papers; (2) Raw journal text mapping for papers not found in folders — 7 journal name variants mapped to the 3 core journals (468 papers); (3) 2 manual overrides for papers with no folder match and non-standard journal text, confirmed via web search. DUPLICATE entries inherit their journal from the original paper. The 2 "Other" papers are genuinely from JSBM and SBE (different papers by same authors as ETP papers).

### `std_abstract` — 99.1% coverage (3,785/3,821)

Cleaned AI-generated paper summaries. The raw `abstract` column contained 106 problematic entries (2.8%): 58 DUPLICATE placeholders, 18 NaN, 14 editorial board listings, 7 N/A placeholders, 6 OCR failures, and 3 FILE NOT FOUND entries.

**Approach:** Clean entries (3,716) are copied as-is. DUPLICATE entries (58) are resolved by extracting the original paper_id from the abstract or title text and pulling the original paper's abstract. Remaining problematic entries (47) are set to NaN — these are editorial board listings, OCR failures, missing files, and papers with no extractable content. The 47 empty entries break down as: 14 editorial board listings (Other), 13 NaN with no source content, 6 OCR failures, 5 N/A placeholders, 3 FILE NOT FOUND, and 6 other extraction gaps.

### `std_rq` — 96.6% coverage (3,691/3,821)

Cleaned AI-extracted research questions. The raw `research_question` column had 189 problematic entries: 107 NaN, 48 DUPLICATE placeholders, 18 N/A (editorials/commentaries), 15 NON-RESEARCH, 7 OCR failures, 3 FILE NOT FOUND, 2 "See paper X" cross-references, and 1 RETRACTED.

**Approach:** Same pattern as `std_abstract`. Clean entries (3,622) copied as-is. DUPLICATE and "See paper X" entries (52) recovered by extracting the original paper_id and pulling its research question. Remaining 147 set to NaN. The 147 empty entries are predominantly Editorials (62) and Other (60), with only 25 substantive papers missing RQs due to extraction failures.

### `std_findings` — 97.8% coverage (3,736/3,821)

Cleaned AI-extracted findings with redundant formatting stripped. The raw `key_findings` column contained 8,198 occurrences of the word "Finding" — mostly as redundant prefixes ("Finding 1:", "Finding:", "H1a/Finding:"). After cleanup, only 180 occurrences remain (legitimate in-text uses).

**Cleaning rules:**
- `H1a/Finding: text` → `H1a: text` (keep hypothesis label, remove "/Finding")
- `Finding N: text` → `text` (strip numbered prefix)
- `Finding: text` → `text` (strip unnumbered prefix)
- `H1:`, `H2a:`, `P1:`, `P2:` prefixes are preserved (carry hypothesis/proposition info)
- Double spaces and leading semicolons cleaned up

**Approach:** All 3,674 clean entries are reformatted with the cleaning rules above. DUPLICATE and "See paper X" entries (54) recovered from originals (also cleaned). Remaining 93 set to NaN — 56 Other, 28 Editorials, and 9 substantive papers with extraction failures.

### `std_gaps` — 95.3% coverage (3,641/3,821)

Cleaned AI-extracted research gaps from the raw `research_gaps_previous_lit` column. Unlike `std_findings`, the raw text has no formatting issues — content is clean prose describing what gaps in prior literature each paper addresses.

The raw column had 118 NaN entries plus problematic text entries: 48 DUPLICATE placeholders, 55 N/A (teaching cases, practitioner pieces, commentaries), 7 OCR/file failures, and 2 "See paper X" cross-references.

**Approach:** Clean entries copied as-is (no formatting cleanup needed). DUPLICATE and "See paper X" entries recovered by extracting the original paper_id and pulling its gaps text. Remaining unrecoverable entries set to NaN. Same 3 manual DUPLICATE overrides as `std_rq` and `std_findings`: pid=528→527, pid=726→725, pid=760→759. The 196 empty entries are predominantly Editorials and Other — legitimate gaps where no prior-literature discussion exists.

### `std_future` — 94.5% coverage (3,610/3,821)

Cleaned AI-extracted future research directions from the raw `future_directions` column. Like `std_gaps`, the raw text is clean prose with no formatting issues.

The raw column had 153 NaN entries plus problematic text entries: 48 DUPLICATE placeholders, 35 N/A (teaching cases, practitioner pieces, commentaries), 15 NON-RESEARCH, 7 OCR/file failures, and 2 "See paper X" cross-references.

**Approach:** Same cleanup/recovery pattern as `std_gaps`. Clean entries copied as-is. DUPLICATE and "See paper X" entries recovered from originals. Remaining set to NaN. Same 3 manual DUPLICATE overrides: pid=528→527, pid=726→725, pid=760→759. The 211 empty entries are predominantly Editorials and Other.

### `std_notes` — 98.5% coverage (3,764/3,821)

Cleaned AI-extracted cross-references, theoretical connections, and extraction notes from the raw `connections_and_notes` column. Like the other text columns, raw text is clean prose with no formatting issues.

The raw column had 25 NaN entries plus problematic text entries: 59 DUPLICATE placeholders, 37 NON-RESEARCH, 5 OCR/file failures, and 2 "See paper X" cross-references.

**Approach:** Same cleanup/recovery pattern. Clean entries copied as-is. DUPLICATE and "See paper X" entries recovered from originals. Same 3 manual DUPLICATE overrides: pid=528→527, pid=726→725, pid=760→759. The 74 empty entries are predominantly NON-RESEARCH and OCR failures.

### `std_sample_description` — 78.7% coverage (3,009/3,821)

Cleaned AI-extracted sample descriptions from the raw `sample` column. The lower coverage rate compared to other text variables reflects the high number of legitimately N/A entries — conceptual papers, editorials, reviews, and formal models have no empirical sample.

The raw column had 355 NaN entries plus problematic text entries: 444 N/A (conceptual, editorial, formal model papers), 48 DUPLICATE placeholders, 15 NON-RESEARCH, 6 OCR/file failures, and 2 "See paper X" cross-references.

**Approach:** Same cleanup/recovery pattern. Clean entries copied as-is. DUPLICATE and "See paper X" entries recovered from originals. Same 3 manual DUPLICATE overrides: pid=528→527, pid=726→725, pid=760→759. The 822 empty entries are predominantly non-empirical papers where sample is legitimately not applicable.

### `std_iv` — 75.7% coverage (2,893/3,821)

Cleaned AI-extracted independent variables from the raw `independent_variables` column. Lower coverage reflects that many non-empirical papers (conceptual, editorial, review) and some empirical-qualitative papers have no formal IVs.

**Approach:** Same cleanup/recovery pattern using shared `_text_cleanup()` helper. Same 3 manual DUPLICATE overrides. The 941 empty entries include 391 N/A, 526 NaN, and problematic entries (DUPLICATE, OCR, NON-RESEARCH).

### `std_dv` — 76.4% coverage (2,918/3,821)

Cleaned AI-extracted dependent variables from the raw `dependent_variables` column. Similar coverage profile to `std_iv`.

**Approach:** Same cleanup/recovery pattern. Same 3 manual DUPLICATE overrides. The 916 empty entries include 256 N/A, 636 NaN, and problematic entries.

### `std_mediators` — 21.6% coverage (824/3,821)

Cleaned AI-extracted mediating variables from the raw `mediators` column. Very low coverage is expected — most papers do not test mediation.

**Approach:** Same cleanup/recovery pattern. Same 3 manual DUPLICATE overrides. The 2,999 empty entries are predominantly papers without mediation analyses (2,938 NaN in raw column).

### `std_moderators` — 44.9% coverage (1,715/3,821)

Cleaned AI-extracted moderating variables from the raw `moderators` column. Moderate coverage — many papers test moderation but not all.

**Approach:** Same cleanup/recovery pattern. Same 3 manual DUPLICATE overrides. The 2,110 empty entries are predominantly papers without moderation analyses (2,065 NaN in raw column).

### `std_controls` — 47.3% coverage (1,809/3,821)

Cleaned AI-extracted control variables from the raw `control_variables` column. Coverage limited to empirical papers with regression-type analyses.

**Approach:** Same cleanup/recovery pattern. Same 3 manual DUPLICATE overrides. The 2,024 empty entries include 1,846 NaN (non-empirical or qualitative papers), 158 N/A, and problematic entries.

### `std_paper_type` — 100% coverage

| Category | Count | % |
|----------|-------|---|
| Empirical-Quantitative | 2,139 | 56.0% |
| Conceptual | 546 | 14.3% |
| Editorial | 412 | 10.8% |
| Empirical-Qualitative | 367 | 9.6% |
| Other | 135 | 3.5% |
| Review | 124 | 3.2% |
| Empirical-Mixed | 68 | 1.8% |
| Formal Model | 30 | 0.8% |

**Approach:** Two-pass — rule-based regex on `paper_type` column (Pass 1, ~97%), then 105 manual overrides for ambiguous cases (Pass 2). Preceded by `raw_data_fixes()` which patches raw `paper_type` values for 3 teaching cases (ETP pids 504, 718, 719 → Editorial) and 2 review papers (ETP pids 1493, 1768 → Review). Journal-aware override logic ensures pid=714's JBV row (legitimate case study) is not affected by the ETP row's classification.

### `std_method_design` — 99.9% coverage (2,577/2,579 empirical)

| Category | Count | Category | Count |
|----------|-------|----------|-------|
| Survey | 1,235 | Scale Development | 43 |
| Archival | 1,068 | Experiment-Field | 39 |
| Panel/Longitudinal | 834 | Meta-Analysis | 39 |
| Interview/Fieldwork | 523 | QCA | 23 |
| Case Study | 325 | Experiment-Lab | 18 |
| Conjoint/Vignette | 170 | Simulation | 15 |
| Content/Text Analysis | 128 | Diary/ESM | 11 |
| Quasi/Natural Experiment | 92 | Bibliometric | 5 |
| Cross-Sectional | 61 | Delphi | 1 |
| Event Study | 48 | Action Research | 1 |

Note: Counts sum to >2,579 because papers can have multiple designs.

**Approach:** Rule-based regex on `method` + `data_source` + `sample` + `title` (Pass 1), then 78 manual overrides (35 original + 43 AI intelligence pass).

### `std_method_technique` — 99.9% coverage (2,576/2,579 empirical)

| Category | Count | Category | Count |
|----------|-------|----------|-------|
| OLS/Linear Regression | 945 | DiD/Matching | 56 |
| Descriptive/Exploratory | 411 | Conjoint Analysis | 56 |
| Qualitative Coding | 379 | Correlation | 51 |
| SEM/Path Analysis | 370 | Meta-Analytic Technique | 45 |
| Panel/Fixed Effects | 264 | Simulation Technique | 41 |
| Logistic/Limited DV | 233 | Time Series | 30 |
| HLM/Multilevel | 147 | QCA | 27 |
| ANOVA/t-test | 134 | Decomposition | 23 |
| Factor Analysis | 111 | Machine Learning/NLP | 22 |
| Survival/Event History | 104 | Event Study Technique | 20 |
| Cluster/Latent Class | 85 | Bayesian | 10 |
| IV/Endogeneity Correction | 82 | | |
| Network Analysis | 70 | | |

Note: Counts sum to >2,579 because papers can have multiple techniques.

**Approach:** Rule-based regex on `method` + `data_source` + `sample` + `title` + `key_findings` + `abstract` + `independent_variables` + `dependent_variables` + `control_variables` + `connections_and_notes` (Pass 1), design-based inference for qualitative papers (Pass 2), then 362 manual overrides from AI intelligence pass (Pass 3).

### `std_country` / `std_region` / `std_continent` — 81.2% coverage (3,104/3,821)

These three columns are produced together from the raw `country_context` column.

**Top 20 values:**

| Country | Count | Country | Count |
|---------|-------|---------|-------|
| United States | 1,599 | Belgium | 46 |
| Multi-Country/Global | 521 | Japan | 41 |
| United Kingdom | 192 | Spain | 37 |
| Germany | 148 | Finland | 33 |
| China | 140 | Singapore | 30 |
| Canada | 120 | Norway | 29 |
| Sweden | 96 | Russia | 29 |
| France | 67 | Switzerland | 27 |
| India | 62 | Denmark | 21 |
| Australia | 52 | South Korea | 20 |

Total unique values: 93 (92 specific countries + "Multi-Country/Global"). Note: counts for specific countries sum to >3,104 because multi-country studies list all countries.

**Region distribution (12 regions, UN geoscheme):**

| Region | Count | Region | Count |
|--------|-------|--------|-------|
| Northern America | 1,684 | Latin America & Caribbean | 63 |
| Western Europe | 431 | Sub-Saharan Africa | 62 |
| East Asia | 190 | Eastern Europe | 56 |
| Northern Europe | 161 | Southeast Asia | 52 |
| Southern Europe | 93 | Middle East & North Africa | 37 |
| South Asia | 74 | Oceania | 65 |

Note: Region/continent are derived only for papers with specific countries. Multi-Country/Global papers get inferred continent(s) where possible (e.g., "22 European countries" → Europe) but no specific region.

**Continent distribution (6 continents):**

| Continent | Count |
|-----------|-------|
| North America | 1,732 |
| Europe | 752 |
| Asia | 315 |
| Africa | 71 |
| Oceania | 65 |
| South America | 39 |

**Approach:** Three-layer classification: (1) Top-down country name lookup against a 130-country reference table (COUNTRY_GEO) plus ~90 alias patterns (demonyms, US states, Canadian provinces, UK constituents, city names); (2) Multi-Country/Global detection for studies that explicitly cover multiple countries, international samples, or global contexts; (3) Manual overrides for 4 "likely US" papers verified by context. Region and continent are derived automatically from the country-to-region-to-continent hierarchy.

### `std_theory_L1_discipline` / `std_theory_L2_name` — 88.9% coverage (3,395/3,821)

These two columns are produced together from the raw `theoretical_lens` column.

**L1 Discipline distribution (9 categories):**

| Discipline | Count | % |
|------------|-------|---|
| Management / Strategy | 903 | 23.6% |
| Entrepreneurship-Specific | 794 | 20.8% |
| Economics | 751 | 19.7% |
| Psychology | 698 | 18.3% |
| Sociology | 613 | 16.0% |
| Organizational Theory | 434 | 11.4% |
| Institutional Theory | 381 | 10.0% |
| Finance | 358 | 9.4% |
| Methodology / Philosophy | 204 | 5.3% |

Note: Counts sum to >3,395 because papers can draw on multiple disciplines.

**Top 30 L2 theories (166 unique):**

| Theory | Count | Theory | Count |
|--------|-------|--------|-------|
| Institutional Theory | 316 | Information Asymmetry | 66 |
| Resource-Based View | 271 | Socioemotional Wealth | 64 |
| Agency Theory | 253 | International Entrepreneurship | 63 |
| Social Network Theory | 165 | Resource Dependence Theory | 63 |
| Human Capital Theory | 158 | Entrepreneurial Cognition | 62 |
| Signaling Theory | 133 | Feminist Theory | 61 |
| Strategic Management | 118 | Decision Theory | 58 |
| Social Capital Theory | 111 | Family Business Theory | 57 |
| Cognitive Psychology | 102 | Contingency Theory | 57 |
| Research Methodology | 88 | Organizational Ecology | 57 |
| Entrepreneurial Orientation | 84 | Legitimacy Theory | 56 |
| Innovation Theory | 82 | Schumpeterian Theory | 55 |
| Knowledge-Based View | 79 | Upper Echelons Theory | 55 |
| Entrepreneurship Theory (General) | 78 | Theory of Planned Behavior | 50 |
| Corporate Entrepreneurship | 74 | Dynamic Capabilities | 49 |

Note: Counts sum to >3,395 because papers can use multiple theories.

**Approach:** Two-pass — rule-based regex matching against a curated THEORY_CATALOG of ~160 canonical theories with ~300+ alias patterns (Pass 1, 80.2% coverage), then AI intelligence pass classifying 335 additional papers from 442 unmatched substantive entries (Pass 2, pushing to 88.9%). Text cleanup strips parenthetical citations before matching. Each raw theory string is matched to at most one canonical L2 name (first-match-wins). L1 disciplines are derived from the L2-to-L1 mapping in the catalog.

### `std_dsType` — 80.2% overall, 99.8% empirical coverage

9 multi-valued data source type categories (semicolon-separated for papers using multiple types).

| Category | Count | Category | Count |
|----------|-------|----------|-------|
| Archival/Database | 1,468 | Ethnographic/Observational | 188 |
| Survey/Questionnaire | 1,138 | Online/Digital Data | 131 |
| Interview | 523 | Simulation/Formal | 26 |
| Government/Administrative | 343 | | |
| Case Study | 251 | | |
| Experiment | 199 | | |

Note: Counts sum to >3,066 because papers can have multiple data source types (e.g., a paper using both survey data and archival records).

**Approach:** Rule-based regex on `data_source` column with `method` column fallback. Four-layer classification: (1) ~150 regex patterns across 9 categories matched against `data_source` text; (2) method column fallback for papers where `data_source` alone is insufficient; (3) Named dataset inference — if a named dataset is detected (e.g., Compustat, GEM) but no dsType pattern matched, auto-assigns "Archival/Database"; (4) 31 manual overrides for edge cases. No "Mixed Primary" category is needed because the multi-valued format naturally captures mixed designs.

### `std_dsNamed` — 24.3% overall, 33.4% empirical coverage (929/3,821)

Named datasets extracted from `data_source`, `method`, and `sample` columns with alias normalization (e.g., "PSED" and "Panel Study of Entrepreneurial Dynamics" both map to "PSED"; "CFPS" and "China Family Panel Studies" both map to "CFPS").

Coverage breakdown by paper type: Empirical-Quantitative 38.1%, Empirical-Mixed 23.5%, Review 16.4%, Empirical-Qualitative 8.4%, Editorial 6.6%.

**Top 30 named datasets (313 unique):**

| Dataset | Count | Dataset | Count |
|---------|-------|---------|-------|
| Patent Data | 60 | Hofstede Cultural Dimensions | 14 |
| IPO Prospectuses/Data | 56 | LinkedIn | 14 |
| VentureXpert | 48 | Thomson Reuters | 13 |
| Compustat | 44 | S&P | 13 |
| GEM | 44 | Twitter/X | 12 |
| Kickstarter | 41 | CRSP | 12 |
| World Bank | 39 | Stock Exchange Data | 11 |
| VC Database | 37 | Inc. 500/5000 | 11 |
| PSED | 36 | Heritage Foundation / Economic Freedom Index | 10 |
| SEC/EDGAR | 34 | Enterprise Survey | 10 |
| US Census Bureau | 34 | SOEP | 10 |
| Statistics Sweden | 25 | Kauffman Firm Survey | 10 |
| Dun & Bradstreet | 21 | Web of Science | 15 |
| USPTO | 21 | Crunchbase | 15 |
| NFIB | 19 | SDC Platinum | 17 |
| SBDC | 18 | | |

Note: Counts sum to >929 because papers can reference multiple datasets. The 313 datasets span financial databases, government records, household surveys, crowdfunding platforms, social media, patent offices, cross-national indices, country-specific administrative registers, and platform data.

**Approach:** Three-layer extraction: (1) Regex-based matching against a curated NAMED_DATASET_CATALOG of ~195 canonical dataset names with ~450+ alias patterns, run on concatenated text from `data_source`, `method`, and `sample` columns; (2) 130 manual AI-identified overrides for papers with named datasets described in natural language; (3) All aliases normalized to a single canonical name per dataset.

---

### `std_tpL1` — 93.1% coverage (3,558/3,821), 15 broad topic domains

Multi-valued (semicolon-separated). Each paper can belong to multiple topic domains.

| L1 Category | Count | L1 Category | Count |
|-------------|-------|-------------|-------|
| Strategy & Performance | 1,069 | Institutions & Context | 443 |
| Entrepreneurial Process | 997 | Family Business | 432 |
| Entrepreneurial Cognition & Psychology | 885 | International Entrepreneurship | 418 |
| Entrepreneurial Finance | 692 | Policy & Economic Development | 401 |
| Human Capital & Teams | 670 | Corporate Entrepreneurship | 320 |
| Innovation & Technology | 490 | Gender & Diversity | 276 |
| Small Business & SMEs | 481 | Social Entrepreneurship | 202 |
| Networks & Social Capital | 447 | | |

Note: Counts sum to >3,558 because papers can belong to multiple L1 domains (e.g., a VC paper about family firms in China gets Entrepreneurial Finance, Family Business, and International Entrepreneurship).

### `std_tpL2` — 93.1% coverage, 77 subtopic categories

Each L2 maps to exactly one L1 parent. Top 20 L2 categories:

| L2 Category | Count | Parent L1 |
|-------------|-------|-----------|
| Competitive Strategy | 438 | Strategy & Performance |
| Firm Performance | 437 | Strategy & Performance |
| Human Capital | 431 | Human Capital & Teams |
| Small Business Management | 415 | Small Business & SMEs |
| Cognition & Decision-Making | 395 | Entrepreneurial Cognition & Psychology |
| Venture Creation & Nascent | 371 | Entrepreneurial Process |
| Family Firm Dynamics | 366 | Family Business |
| Venture Capital | 332 | Entrepreneurial Finance |
| Social Capital | 270 | Networks & Social Capital |
| Technology & R&D | 238 | Innovation & Technology |
| Institutional Theory | 230 | Institutions & Context |
| Opportunity Recognition & Creation | 216 | Entrepreneurial Process |
| Innovation (general) | 205 | Innovation & Technology |
| Self-Efficacy & Motivation | 199 | Entrepreneurial Cognition & Psychology |
| Women Entrepreneurship | 194 | Gender & Diversity |
| Entrepreneurial Learning & Failure | 177 | Entrepreneurial Process |
| Corporate Entrepreneurship (general) | 169 | Corporate Entrepreneurship |
| Resource Mobilization | 165 | Entrepreneurial Process |
| Emerging & Transition Economies | 158 | International Entrepreneurship |
| Organizational Design | 149 | Strategy & Performance |

**Approach:** Regex-based classification of individual tags from `topic_tags` column. Tags are split by comma/semicolon delimiters, lowercased, and matched against a TOPIC_TAXONOMY dict of 15 L1 domains × 77 L2 subcategories with ~300+ keyword regex patterns. Meta-scholarship tags (research methodology, editorials, field development, duplicates) are explicitly skipped. The 6.9% unclassified papers are almost entirely meta-scholarship without substantive research topics.

---

### `std_flag` — 100% coverage, 5 values

Quality flag for filtering papers before building the web app database.

| Flag | Count | % | Description |
|------|-------|---|-------------|
| OK | 3,683 | 96.4% | Clean paper — include in web app |
| DUPLICATE | 68 | 1.8% | Duplicate entry of another paper |
| NON_RESEARCH | 55 | 1.4% | Administrative content (editorial boards, TOC, indexes, calls for papers) |
| OCR_FAILED | 12 | 0.3% | Extraction/OCR failure with insufficient content |
| RETRACTED | 3 | 0.1% | Retracted papers, corrigenda, or errata |

**Usage:** To build the web app database, filter with `df[df['std_flag'] == 'OK']` → 3,683 papers.

**Approach:** Five-rule cascade (first match wins):

1. **DUPLICATE** — title or abstract starts with "DUPLICATE", raw journal is "DUPLICATE", or raw paper_type is "DUPLICATE". Catches 68 entries including 39 with DUPLICATE titles, 19 with DUPLICATE abstracts only, and cross-journal duplicates. Note: these papers may have populated std_ fields (recovered from originals during standardization) but are still duplicates.
2. **RETRACTED** — title or raw paper_type contains "retract", "corrigendum", or "erratum".
3. **OCR_FAILED** — title or raw paper_type contains "ocr fail", "ocr need", "garbled", "file not found", "not extracted".
4. **NON_RESEARCH** — title or raw paper_type contains administrative keywords ("table of contents", "journal index", "editorial board", "call for papers", "publisher's note"), or raw paper_type starts with "non-research"/"non_research".
5. **Catch-all for remaining `Other` papers** — if std_paper_type is "Other" AND the paper has no substantive content (std_rq < 10 chars, std_findings < 10 chars, std_abstract < 20 chars), flag as OCR_FAILED. Papers typed as "Other" but with real content (e.g., pid=971, a conceptual paper miscategorized due to OCR note) remain OK.

**Key design decisions:**
- Substantive editorials, commentaries, and teaching cases are NOT flagged — they are legitimate scholarly content
- DUPLICATE papers with recovered std_ fields are still flagged (recovery was for analytical convenience)
- The flag is mutually exclusive (one value per paper)

---

## Candidates for Future Standardization

All major raw columns have been standardized. No remaining candidates identified.

---

## Data Quality Notes

- **Duplicate paper_ids:** 33 paper_ids appear in multiple journals. Always use `(paper_id, title[:40])` as composite key.
- **DUPLICATE entries:** 15 papers flagged as "DUPLICATE" in journal column — these are identified duplicates across journals.
- **NaN handling:** Several columns contain actual NaN values. Always check with `pd.notna(x) and str(x).strip() not in ('', 'nan', 'N/A')`.
- **Encoding:** Some titles contain special characters (em-dashes, curly quotes, accented characters). The Excel file preserves these correctly.
- **Extraction quality:** The `Other` category in `std_paper_type` (135 papers) includes OCR failures, corrupted extractions, and non-research content.
- **Raw data fixes (`raw_data_fixes()`):** 19 papers had their raw data patched before standardization. Three groups:
  - **JBV pids 111–120 (10 papers):** OCR/extraction failures with mostly empty fields. Re-extracted from original PDFs. Fixes applied only to JBV rows (ETP/SEJ rows for same pids are fine). Authors: Bantel, Baron (×2), Basu et al. (×2), Bates (×5).
  - **ETP pids 1491, 1492, 1493, 1765, 1767, 1768 (6 papers):** Extraction failures with titles but most fields empty. Re-extracted from original PDFs. Includes paper_type corrections: pid 1493 → Review (bibliometric), pid 1768 → Review (industry overview).
  - **ETP pids 504, 718, 719 (3 papers):** Teaching cases misclassified as "Empirical-qualitative" in raw extraction. Reclassified to "Editorial" (Teaching Case). JBV rows for same pids are unaffected (different papers).
