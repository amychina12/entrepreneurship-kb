# App Component → Data Variable Mapping

This document maps every feature in the Entrepreneurship Research Knowledge Base web app to the data variables it uses.

**Data pipeline:** Excel (`knowledge_base_final.xlsx`, 51 columns) → `build_data.py` FIELD_MAP → JSON (`data.json`, 32 fields) → App components

---

## Complete JSON ↔ Excel Field Map

| JSON Field | Excel Column | Type | Description |
|---|---|---|---|
| id | paper_id | int | Sequential identifier |
| authors | authors | string | Author names |
| year | std_year | int | Publication year |
| title | title | string | Paper title |
| journal | std_journal | string | Abbreviated journal (ETP/JBV/SEJ) |
| journal_raw | journal | string | Raw journal name from source file |
| type | std_paper_type | string | Standardized paper type (8 categories) |
| abstract | std_abstract | string | Paper abstract |
| rq | std_rq | string | Research question (polished) |
| findings | std_findings | string | Key findings (polished) |
| gaps | std_gaps | string | Research gaps (polished) |
| future | std_future | string | Future directions (polished) |
| notes | std_notes | string | Cross-paper connections and notes |
| tags | topic_tags | string | Raw topic keywords (semicolon-separated) |
| tpL1 | std_tpL1 | string | Topic L1 domain (15 categories) |
| tpL2 | std_tpL2 | string | Topic L2 sub-domain (77 categories) |
| tName | std_theory_L2_name | string | Canonical theory name(s) |
| tDisc | std_theory_L1_discipline | string | Theory discipline (9 categories) |
| theory_raw | theoretical_lens | string | Raw theory text from extraction |
| design | std_method_design | string | Method design / L2 (21 possible values) |
| technique | std_method_technique | string | Analytical technique / L3 (24 possible values) |
| country | std_country | string | ISO country name(s) |
| region | std_region | string | UN sub-region |
| continent | std_continent | string | Continent |
| dsType | std_dsType | string | Data source type (9 categories) |
| dsNamed | std_dsNamed | string | Named dataset (309 unique datasets) |
| sample_raw | std_sample_description | string | Full sample description |
| controls | std_controls | string | Control variables |
| iv | std_iv | string | Independent variables |
| dv | std_dv | string | Dependent variables |
| med | std_mediators | string | Mediators |
| mod | std_moderators | string | Moderators |

---

## Multi-Value Field Handling

Many fields contain multiple values separated by semicolons (e.g., `"Survey; Experiment"`). The app uses `splitSemi(value)` to split, trim, and filter these.

**Multi-value fields:** type, design, technique, tDisc, tName, tpL1, tpL2, tags, country, region, continent, dsType, dsNamed, iv, dv, med, mod, controls.

**Filter matching rule:** A paper matches a filter if ANY of its split values is in the selected filter array. For example, if a paper has `tName = "Resource-Based View; Social Capital Theory"` and the user filters for "Social Capital Theory", the paper matches.

**Filter option extraction:** The app scans all papers, splits each field on semicolons, and collects unique values for each dropdown. This means individual theory names (not the full semicolon string) appear as separate checkboxes.

---

## 1. Search (BM25 Full-Text Relevance)

| JSON Field | Weight | Description |
|---|---|---|
| title | 3.0 | Highest weight — title is most important |
| authors | 1.5 | Author name matching |
| findings | 1.2 | Key findings weighted above abstract |
| abstract | 1.0 | Base weight |
| tName | 0.8 | Theory names |
| tags | 0.8 | Raw topic keywords |
| iv | 0.7 | Independent variables |
| dv | 0.7 | Dependent variables |
| rq | 0.6 | Research questions |
| gaps | 0.5 | Research gaps |
| notes | 0.4 | Cross-paper notes |

BM25 parameters: k1=1.5, b=0.75. Supports exact phrases (`"..."`) , AND/OR operators, and partial substring matching.

---

## 2. Filters (11 Dropdowns + Year Range)

| Filter Label | JSON Field | Multi-Value | Possible Values |
|---|---|---|---|
| Journal | journal | No | ETP, JBV, SEJ |
| Paper Type | type | No | Empirical-Quantitative, Empirical-Qualitative, Empirical-Mixed, Conceptual, Review, Editorial, Formal Model, Other |
| Design | design | Yes (`;` split) | Survey, Case Study, Experiment, Longitudinal/Panel, etc. (21 values) |
| Technique | technique | Yes (`;` split) | OLS, SEM, HLM, fsQCA, Grounded Theory, etc. (54 values) |
| Theory (Discipline) | tDisc | Yes (`;` split) | 9 theory disciplines |
| Theory (Name) | tName | Yes (`;` split) | 166 unique canonical theory names |
| Topic (L1) | tpL1 | Yes (`;` split) | 15 domain categories |
| Sub-topic (L2) | tpL2 | Yes (`;` split) | 77 sub-domain categories |
| Continent | continent | Yes (`;` split) | Americas, Europe, Asia, Africa, Oceania |
| Data Source | dsType | No | Survey/Questionnaire, Archival/Database, Case Study, etc. (9 types) |
| Dataset | dsNamed | No | GEM, PSED, Crunchbase, etc. (309 datasets) |
| Year Range | year | — | Numeric min/max inputs |

Filters are AND'd across categories. Paper Type filter includes tooltip descriptions via `TYPE_NOTES`.

---

## 3. Paper Card (Collapsed View)

| Element | JSON Field | Notes |
|---|---|---|
| Title | title | Highlighted with search terms |
| Authors · Year | authors, year | Highlighted |
| Journal badge | journal | Color-coded pill (ETP blue, JBV green, SEJ gold) |
| Abstract snippet | abstract | Gray text, truncated, highlighted |
| Relevance badge | (calculated _bm25) | Shown only when sorting by relevance |
| Bookmark star | (localStorage) | Not from data |

---

## 4. Paper Details (Expanded View)

### 4a. Chips at top

| Chip | JSON Field | Notes |
|---|---|---|
| Journal full name | journal | Color background |
| Year | year | |
| Paper Type | type | Full type string |
| Design | design | First value only (split on `;`, take first) |
| Country | country | First country only, hidden if "N/A" |

### 4b. Research Content group

| Label | JSON Field | Highlighted |
|---|---|---|
| Abstract | abstract | Yes |
| Research Question | rq | Yes |
| Research Gap | gaps | No |
| Key Findings | findings | Yes |
| Future Directions | future | No |

### 4c. Framework & Method group (shown if tName OR design OR dsType present)

| Label | JSON Field(s) | Notes |
|---|---|---|
| Theories | tName | Canonical names, semicolon-separated string displayed as-is, highlighted |
| Theory Detail | theory_raw | Only shown if theory_raw differs from tName; raw extraction text |
| Method | type, design, technique | Joined as "Type › Design › Technique"; only shown if design present |
| Data Source | dsType, dsNamed | Formatted as "Type — Named Dataset" |
| Sample | sample_raw | Full description text, highlighted |
| Country | country, region | Formatted as "Country — Region" |

### 4d. Variables group (shown if iv OR dv present)

| Label | JSON Field |
|---|---|
| Independent | iv |
| Dependent | dv |
| Mediators | med |
| Moderators | mod |
| Controls | controls |

### 4e. Connections & Notes group (shown if notes present)

| Label | JSON Field |
|---|---|
| (no label) | notes |

---

## 5. Related Papers (4 Tabs)

| Tab | JSON Field | Min Matches | Match Logic |
|---|---|---|---|
| By Keywords | tags (→ topic_tags) | ≥2 shared tags | Case-insensitive, split on `;` |
| By Theory | tName (→ std_theory_L2_name) | ≥1 shared theory | Exact match after split on `;` |
| By Topic | tpL2, fallback tpL1 | ≥1 shared topic | Exact match after split on `;` |
| By Method | design (→ std_method_design) | ≥1 shared design | Exact match after split on `;` |

Results sorted by match count descending, then year descending. Returns top 5. Default tab priority: Keywords > Theory > Topic > Method.

---

## 6. Analytics Overview (6 Charts)

| Chart | JSON Field(s) | Type | Notes |
|---|---|---|---|
| Publications over time | year, journal | Stacked bar | One series per journal |
| By journal | journal | Doughnut | Count per journal |
| Paper types | type | Horizontal bar | Split on `;`, top 10 |
| Most-used theories | tName | Horizontal bar | Split on `;`, top 15 |
| Topic domains | tpL1 | Horizontal bar | Split on `;`, top 10 |
| Top countries | country | Horizontal bar | Split on `;`, top 15 |

---

## 7. Research Explorer

### Theory × Topic Heatmap
- **Rows:** tName (top 20 by frequency), **Columns:** tpL1 (all unique)
- Both split on `;`; cell = count of papers at intersection

### Variable Relationship Map (Pathway Explorer)
- Extracts pathways from: iv, dv, med, mod (all split on `;`)
- Groups by [IV, DV] pair, collects mediators/moderators
- Shows top 50 pathways by paper count

### Method × Topic Heatmap
- **Rows:** design (all unique, sorted by frequency), **Columns:** tpL1 (all unique)
- Both split on `;`; cell = count of papers at intersection

---

## 8. Journal Comparison

| Metric | JSON Field(s) | Notes |
|---|---|---|
| Paper count | journal | Count per journal |
| Year range | year | Min–max per journal |
| % Empirical | type | Count where type includes "Empirical" or "Mixed" |
| Theory breakdown | tName | Split, count per journal |
| Topic breakdown | tpL1 | Split, count per journal |
| Paper type doughnut | type | Split, count per journal |
| Top countries table | country | Split, top 5 per journal |

---

## 9. AI Summarization

### Context metadata sent to AI:
- Paper count, journal counts (journal), year range (year), type counts (type), top 10 theories (tName), top 10 topics (tpL2 or tpL1)

### Per-paper fields sent:
| Field | JSON Field | Included |
|---|---|---|
| Authors | authors | Always |
| Year | year | Always |
| Title | title | Always |
| Journal | journal | Always |
| Abstract | abstract | If present |
| Key Findings | findings | If present |
| Theories | tName | If present |
| Paper Type | type | If present |
| Design | design | If present |
| Technique | technique | If present |
| IVs | iv | If present |
| DVs | dv | If present |
| Mediators | med | If present |
| Moderators | mod | If present |
| Gaps | gaps | If present |
| Future | future | If present |
| Research Question | rq | If present |
| Sample | sample_raw | If present |

Two-stage strategy: if >150 papers with BM25 scores, top 80 get full detail; rest get title+year+journal only.

---

## 10. Export

### CSV (6 fields)
title, authors, year, journal, rq, findings

### BibTeX (4 fields)
authors, title, journal (full name), year

### Excel — Admin only (31 fields)
id, title, authors, year, journal, journal_raw, type, abstract, rq, findings, gaps, future, tDisc, tName, theory_raw, tpL1, tpL2, design, technique, country, region, continent, dsType, dsNamed, sample_raw, controls, iv, dv, med, mod, tags, notes

---

## 11. Wiki Tab

### Coverage statistics
Uses `pct(field)` helper: counts papers where field is non-empty, divides by total.

### Filter reference tables
- Journal: journal → ETP/JBV/SEJ with paper counts
- Paper Type: type → 8 categories with descriptions and counts
- Theory Discipline: tDisc → 9 disciplines with counts (dynamically computed)
- Topic L1: tpL1 → 15 domains with counts (dynamically computed)
- Continent: continent → 5 continents with counts
- Data Source Type: dsType → 9 types with counts (dynamically computed)

### JSON fields reference
Lists all 32 fields with description and coverage %.

---

## Summary: Component → Primary Fields

| Component | Primary JSON Fields |
|---|---|
| Search | title, authors, findings, abstract, tName, tags, iv, dv, rq, gaps, notes |
| Filters | journal, type, design, technique, tDisc, tName, tpL1, tpL2, continent, dsType, dsNamed, year |
| Card | title, authors, year, journal, abstract |
| Details: Research | abstract, rq, gaps, findings, future |
| Details: Framework | tName, theory_raw, type, design, technique, dsType, dsNamed, sample_raw, country, region |
| Details: Variables | iv, dv, med, mod, controls |
| Details: Notes | notes |
| Related: Keywords | tags |
| Related: Theory | tName |
| Related: Topic | tpL2 (fallback tpL1) |
| Related: Method | design |
| Analytics Overview | year, journal, type, tName, tpL1, country |
| Theory×Topic Heatmap | tName, tpL1 |
| Variable Pathways | iv, dv, med, mod |
| Method×Topic Heatmap | design, tpL1 |
| Journal Comparison | type, tName, tpL1, country, year |
| AI Summarization | authors, year, title, journal, abstract, findings, tName, type, design, technique, iv, dv, med, mod, gaps, future, rq, sample_raw |
| Export CSV | title, authors, year, journal, rq, findings |
| Export BibTeX | authors, title, journal, year |
| Export Excel | All 32 fields |
| Wiki | All fields (coverage stats) |
