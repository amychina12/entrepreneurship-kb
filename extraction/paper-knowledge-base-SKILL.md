---
name: paper-knowledge-base
description: "Use this skill whenever the user wants to build a searchable knowledge base from a large collection of academic papers. Triggers include: requests to 'index my papers', 'build a paper database', 'extract information from my paper collection', 'create a knowledge base from PDFs', or 'catalog my research library'. Unlike the lit-review-synthesis skill (which targets a focused set of papers for a specific review), this skill is designed for large-scale extraction across hundreds or thousands of papers to create a persistent, queryable research knowledge base. The skill operates in a single deep-read pass, extracting structured information for every paper. The output is a single Excel file that grows incrementally across batches and sessions."
---

# Paper Knowledge Base Builder

A single-pass extraction skill for building a persistent, searchable knowledge base from a large collection of academic papers.

---

## ⛔ CRITICAL: MANDATORY EXTRACTION METHOD ⛔

**This section overrides all other instructions. No exceptions. No shortcuts.**

### How extraction MUST work:

For EVERY paper, you must:
1. Use Python (pymupdf/fitz) to extract the raw text from the PDF
2. **Load that text into your own context window** (i.e., read it yourself as Claude)
3. Read and comprehend the paper text with your full intelligence
4. Extract all 23 fields using your understanding of the paper
5. Save the structured output to Excel
6. Move to the next paper

### What you must NEVER do:

🚫 **NEVER write a batch Python script that uses regex/heuristics to extract fields like `abstract`, `research_question`, `key_findings`, `theoretical_lens`, `research_gaps_previous_lit`, `topic_tags`, `independent_variables`, `dependent_variables`, `mediators`, `moderators`, `method`, `sample`, `future_directions`, or `connections_and_notes`.**

🚫 **NEVER use patterns like `re.search(r'Abstract', text)` to extract abstracts.**

🚫 **NEVER write placeholder values like "See paper", "See abstract", "Not extracted", or blank strings because a regex failed to match.**

🚫 **NEVER pre-process all papers in a single Python loop where YOUR intelligence is not reading each paper.** A Python loop that extracts text and then feeds it back to you (Claude) one at a time IS allowed. A Python loop that tries to parse papers with regex IS NOT.

### Why this rule exists:

Fields like `research_question`, `key_findings`, and `theoretical_lens` require reading comprehension. No regex can extract "H1: ADHD increases entrepreneurial entry — Supported" from a PDF. Only an LLM reading the text can do this. When you write a regex batch script, you produce a spreadsheet full of "See paper" — which is useless.

### The correct pattern for large folders:

```
papers = list_pdfs_in_folder(path)
existing_excel = load_existing_excel_if_any()
last_id = get_last_paper_id(existing_excel)

for i, pdf in enumerate(papers):
    # Step 1: Extract raw text with Python
    text = extract_text_with_pymupdf(pdf)
    truncated = smart_truncate(text)
    
    # Step 2: YOU (Claude) read the text and extract fields
    #         This means the text goes into your context window.
    #         You read it. You understand it. You fill in all 23 fields.
    card = claude_reads_and_extracts(truncated)  # THIS IS YOU READING
    
    # Step 3: Save progress
    append_to_excel(card, existing_excel)
    
    # Checkpoint message every 5-10 papers
    if (i + 1) % 10 == 0:
        save_excel()
        print(f"Progress: {i+1}/{len(papers)} papers done")
```

**The key distinction**: `claude_reads_and_extracts()` is NOT a Python function you write. It is YOU reading the paper text that was loaded into your context, comprehending it, and producing the structured extraction. The Python code handles file I/O. YOU handle comprehension.

### If the folder has hundreds or thousands of papers:

- **Do not panic at the number. Do not take shortcuts.**
- Process them one at a time, exactly as you would for 10 papers.
- Save the Excel after every 5-10 papers as a checkpoint.
- If you hit context limits or session boundaries, tell the user: "I've processed X papers so far. The Excel is saved. Say 'continue' to keep going from paper X+1."
- The user understands this takes time. They chose quality over speed.
- If you want to suggest the Phase 2 API script as a faster alternative, you may — but ONLY as a suggestion, and ONLY after confirming the user wants that. Default behavior is: read each paper yourself.

### Self-check before executing:

Before running your extraction code, verify:
- [ ] Am I reading each paper's text in my context window? (Not just parsing it with regex)
- [ ] Does my code produce ALL 23 fields per paper with real content? (Not "See paper")
- [ ] Is there any `re.search` or `re.match` that tries to extract semantic fields? (If yes, DELETE IT)
- [ ] Would every field pass the specificity test? (Could this text appear in a different paper's row?)

If any check fails, stop and rewrite your approach.

---

## Overview

This skill processes academic paper PDFs and produces a single, growing Excel knowledge base with 23 columns per paper. The design prioritizes scannability — every field should be readable in seconds when scanning hundreds of rows.

**Design principles**:
1. **Scannable**: Write for your future self scanning 200 rows. Brief, clear, parallel structure.
2. **Specific**: Every field must contain information unique to THIS paper. If it could describe any paper, don't write it.
3. **Consistent**: Same vocabulary, same format across all papers so the Excel is filterable and sortable.
4. **Let the paper speak**: Use the abstract verbatim rather than paraphrasing. Extract what's there; don't embellish.

---

## Core Workflow

```
Session 1:  Point to PDF folder → Deep extraction (one by one) → Save Excel
Session 2:  Load existing Excel → Continue from where you left off → Save
...
Session N:  All papers extracted. Knowledge base is complete and queryable.
```

**For large folders (100+ papers)**: The workflow is identical — just more sessions. Process continuously within each session, saving checkpoints. Between sessions, the user says "continue" and you pick up from the last paper_id.

---

## Before Starting: Ask the User

At the start of each session, determine the mode:

1. **"New batch"** — User has new PDFs to process
2. **"Continue"** — User wants to continue processing papers from a folder
3. **"Query"** — User wants to search or analyze the existing knowledge base
4. **"Fix"** — User found errors and wants to re-extract specific papers by ID

Also ask (first session only):
- **What are your primary research areas?** (Helps generate consistent topic tags.)
- **Where are your PDFs stored?** (Folder path for iteration, or the user will upload directly.)

---

## Extraction Process

### Step 1: Extract Text

Use Python PDF libraries (pymupdf/fitz or pdfplumber) to extract text from ONE PDF.

### Step 2: Smart Text Truncation

If extracted text exceeds 50,000 characters:

- **Always keep**: Abstract, Introduction, Hypotheses/Theory section, Method (full), Results (prose), Discussion, Conclusion
- **Remove first**: Reference list, Appendices, Acknowledgments, Author bios, Footnotes
- **Remove second**: Tables (often garbled), Figure captions
- Fall back to 50,000 character cutoff if no clear section headers found.

### Step 3: Read and Extract (YOU, Claude, must do this)

**Load the truncated text into your context window.** Read it with comprehension. Fill in every field in the template below based on your understanding of the paper. This is the step that makes the knowledge base valuable — your intelligence reading the paper, not a regex.

### Step 4: Normalize and Save

Run normalization checks, then save to Excel. If existing Excel exists, load first and append.

### Step 5: Progress Report (after every checkpoint save)

After every checkpoint save, print a status message in exactly this format:

```
═══ PROGRESS: [X]/[total] papers done. Last paper_id saved: [id]. PDF: [filename] ═══
═══ To resume in a new session: "Continue building the knowledge base. Excel at [path]. PDFs at [path]." ═══
```

This ensures the user always knows where things stand and can resume if the session is interrupted.

### Step 6: Next Paper

Repeat Steps 1-5 for the next PDF. Save checkpoint every 5-10 papers.

---

## Extraction Template

### Brevity Rules (apply to ALL fields)

1. **Be brief.** Most fields: 1-3 short sentences or a concise semicolon-separated list.
2. **No regression output in key_findings.** No β, p-values, standard errors, odds ratios, marginal effects. Say what was found, not the numbers.
3. **Semicolons for lists.** No numbered lists (1, 2, 3) within cells.
4. **No filler.** If a sentence could describe any paper ("implications for theory and practice"), don't write it.

---

### Column Definitions

| # | Column | Type | Guidance |
|---|--------|------|----------|
| A | `paper_id` | Integer | Auto-assigned, sequential. Continue from last ID in existing Excel. |
| B | `authors` | String | "Last, F.I.; Last, F.I." format. Full author list. |
| C | `year` | Integer | Publication year. |
| D | `title` | String | Full title. |
| E | `journal` | String | Full journal name (not abbreviation). |
| F | `paper_type` | String | One of: "Empirical-quantitative", "Empirical-qualitative", "Mixed-methods", "Conceptual/Theory", "Review", "Meta-analysis", "Commentary/Editorial", "Book chapter". |
| G | `topic_tags` | String | 3-7 keyword tags, semicolon-separated. See Topic Tag Guidelines. |
| H | `abstract` | String | **Copy the abstract verbatim from the paper.** Do not paraphrase, summarize, or shorten. The abstract is the authors' own summary and should be preserved exactly as written. If the abstract is not clearly identifiable, extract the first substantive paragraph that serves as a summary. |
| I | `research_gaps_previous_lit` | String | What gap(s) in prior literature does this paper address? What was missing or unresolved before this paper? Write in 1-3 sentences. e.g., "Prior research on ADHD and entrepreneurship focused on entrepreneurial intention but not actual entry; no studies used population-level registry data to track real transitions." This field captures the paper's MOTIVATION — why it needed to be written. |
| J | `research_question` | String | The paper's stated research question or purpose in 1-2 sentences. Must be specific. |
| K | `theoretical_lens` | String | Theory or framework used. Semicolons if multiple. "Atheoretical / empirically driven" if none. |
| L | `independent_variables` | String | Name and brief operationalization of each IV. Semicolons between IVs. e.g., "ADHD symptoms (ASRS-6 self-report); Gender (binary)". For conceptual papers: "N/A". For qualitative: "Constructs explored: [list]". |
| M | `dependent_variables` | String | Name and brief operationalization. For conceptual: "N/A". For qualitative: "Constructs explored: [list]". |
| N | `mediators` | String | Name and brief operationalization. "None" if not tested. |
| O | `moderators` | String | Name and brief operationalization. "None" if not tested. |
| P | `control_variables` | String | Only substantively important or unusual controls. ONE short line. e.g., "Firm size, industry FE, year FE, worker FE from AKM decomposition". For qualitative/conceptual: "N/A". |
| Q | `sample` | String | "[N] [who] from [source]" in one sentence. e.g., "1,247 entrepreneurs from PSED II, 2005-2011". |
| R | `data_source` | String | Where the data came from. Brief. e.g., "Swedish population registry linked with military records". |
| S | `country_context` | String | e.g., "Portugal, 2005-2019" or "United States, S&P 500 firms". |
| T | `method` | String | 1-2 sentences. The main analytical method and ONE notable robustness feature if important. e.g., "Staggered DiD (Callaway & Sant'Anna) with entropy balancing." Do not list every robustness check. |
| U | `key_findings` | String | **Follow the Key Findings Format Guide below.** Most important field for scannability. |
| V | `future_directions` | String | 1-3 key suggestions for future research from the authors, semicolon-separated. Brief. |
| W | `connections_and_notes` | String | How this paper connects to other work, plus any noteworthy context. e.g., "Extends Mishina et al. (2012) stigma framework to entrepreneurship; Part of JBV special issue on diversity; Uses retracted measure — caution." |
| X | `pdf_filename` | String | Original filename for later retrieval. |

---

## Key Findings Format Guide

### For empirical papers WITH formal hypotheses:

```
H1: [description] — Supported / Not supported / Partially supported (brief qualifier);
H2: [description] — Supported;
H3: [description] — Not supported
```

Example:
```
H1: Current option wealth reduces cleantech investment — Supported;
H2: Prospective option wealth increases cleantech investment — Supported;
H3: Founder status weakens the negative effect of current option wealth — Supported
```

### For empirical papers WITHOUT formal hypotheses (exploratory, abductive):

Use "Finding:" prefix for parallel structure:

```
Finding: Founder-directors positively associated with patents, negatively with supply chain agreements;
Finding: VC-directors positively associated with exits, negatively with R&D and patents;
Finding: CVC-directors negatively associated with patents and product introductions
```

### For conceptual/theory papers:

List propositions:

```
P1: Extended healthspan would expand entrepreneurial opportunities;
P2: Longer healthspans extend future time perspectives, affecting strategic planning;
P3: Age-success relationship shifts, enabling older entrepreneurs longer
```

### For review papers and meta-analyses:

Summarize main conclusions:

```
Three mechanisms link class origin to entrepreneurial outcomes: financial transfer, habitus formation, network access;
Lower-class origins face fewer starts and reduced mobility but possess unique strengths;
Subjective class indicators used in only 3% of reviewed studies
```

### For qualitative papers:

Describe core themes or process model:

```
Phase 1: Growth-at-all-costs framing triggered hubristic culture and morally reckless practices;
Phase 2: Regulatory intervention forced reframing to no-harmful-growth;
Phase 3: Emotional catharsis and purpose-driven culture enabled legitimacy repair
```

### Rules for ALL paper types:
- **No coefficients, β values, p-values, odds ratios, or marginal effects**
- **One exception**: percentage effects are acceptable when they ARE the finding (e.g., "16% increase in acquisition likelihood per SD")
- Keep each finding to one line
- Use semicolons between findings

---

## Topic Tag Guidelines

1. **Noun phrases, not sentences.** "gender stereotypes" not "how gender stereotypes affect funding."
2. **Specific but not hyper-specific.** "venture capital decision-making" good; "Series A biotech VC" too narrow.
3. **Consistent vocabulary.** Reuse canonical terms across papers. Don't alternate between synonyms.
4. **Tag topic AND mechanism.** "ADHD; entrepreneurial entry; impulsivity; self-regulation."
5. **Tag distinctive methods if noteworthy.** "natural experiment; staggered DiD."
6. **Maintain running vocabulary.** After each batch, display all unique tags. Prefer existing tags.

---

## Adapting for Paper Types

### Empirical-quantitative
Use all fields as described. This is the default.

### Empirical-qualitative
- `independent_variables` / `dependent_variables`: "Constructs explored: [list]".
- `method`: Tradition, N of interviews/cases, analytical approach. e.g., "Gioia method, 42 interviews, NVivo."
- `key_findings`: Themes or process model (see format guide).
- `control_variables`: "N/A".

### Conceptual / theory papers
- `independent_variables` through `control_variables`: "N/A"
- `sample` / `data_source`: "N/A"
- `method`: e.g., "Conceptual — propositional inventory" or "Historical tracing and conceptual analysis."
- `key_findings`: Propositions (see format guide).

### Review papers and meta-analyses
- `method`: e.g., "Systematic review (PRISMA, 219 articles, 1990-2023)" or "Meta-analysis (random effects, k=87)."
- `sample`: Scope. e.g., "219 articles from Scopus/WoS, 1990-2023."
- `key_findings`: Main conclusions (see format guide).

### Commentary / editorial
- Fill what you can. Most empirical fields: "N/A."

---

## Anti-Filler Rules

### Banned phrases (never write these):
- "discussion about the results and their implications for theory and practice"
- "the results support the hypotheses"
- "this paper makes important contributions to the literature"
- "future research should address these limitations"
- Any sentence that could apply to literally any paper

### Also banned (extraction-failure placeholders):
- "See paper"
- "See abstract"
- "Not extracted"
- "Abstract not found" (you are reading the paper — find the abstract)
- Any blank or empty field that should have content

If you genuinely cannot find information after reading the paper, write "Not reported" — which means you looked and it isn't there. Never write a placeholder that means you didn't look.

### The specificity test:
For every field, ask: "Could this exact text appear in a DIFFERENT paper's row?" If yes, rewrite with specifics from THIS paper.

### When information is absent:
Write "Not reported" or "N/A" — never filler, never placeholders.

---

## Normalization Rules

```python
def normalize_card(card):
    """Flatten any nested structures and enforce type rules."""
    string_fields = [
        "authors", "title", "journal", "paper_type", "topic_tags",
        "pdf_filename", "abstract", "research_gaps_previous_lit",
        "research_question", "theoretical_lens",
        "independent_variables", "dependent_variables", "mediators",
        "moderators", "control_variables", "sample", "data_source",
        "country_context", "method", "key_findings",
        "future_directions", "connections_and_notes"
    ]

    for field in string_fields:
        val = card.get(field, "")
        if isinstance(val, dict):
            card[field] = "; ".join(f"{k}: {v}" for k, v in val.items())
        elif isinstance(val, list):
            card[field] = "; ".join(str(item) for item in val)
        elif val is None:
            card[field] = ""
        elif not isinstance(val, str):
            card[field] = str(val)

    for field in ["year", "paper_id"]:
        val = card.get(field)
        if val is not None:
            try:
                card[field] = int(val)
            except (ValueError, TypeError):
                card[field] = 0

    return card
```

---

## Quality Checks

### Mandatory:
1. `abstract` is at least 100 characters (should be a full abstract, not a fragment)
2. `research_question` is specific (not just "studies entrepreneurship")
3. `method` is specific (not just "regression" or "qualitative")
4. `key_findings` follows the format guide (H1/Finding/P1/themes — not prose paragraphs)
5. `key_findings` contains NO β values, p-values, or regression coefficients
6. `research_gaps_previous_lit` describes what was MISSING in prior literature (not what this paper found)
7. `topic_tags` has at least 3 tags
8. `sample` includes a number (N, k, or informant count)
9. No banned phrases anywhere
10. **No placeholder values ("See paper", "See abstract", blank fields) in any semantic field**

### Brevity checks:
- `control_variables`: ONE short line
- `method`: 1-2 sentences max
- `future_directions`: 1-3 items, semicolon-separated
- `connections_and_notes`: 2-4 sentences max

---

## Excel File Structure

Single sheet called "Knowledge Base" with columns:

| Col | Field | Width |
|-----|-------|-------|
| A | paper_id | 8 |
| B | authors | 25 |
| C | year | 8 |
| D | title | 40 |
| E | journal | 25 |
| F | paper_type | 18 |
| G | topic_tags | 40 |
| H | abstract | 70 |
| I | research_gaps_previous_lit | 50 |
| J | research_question | 45 |
| K | theoretical_lens | 30 |
| L | independent_variables | 35 |
| M | dependent_variables | 35 |
| N | mediators | 25 |
| O | moderators | 25 |
| P | control_variables | 30 |
| Q | sample | 30 |
| R | data_source | 30 |
| S | country_context | 18 |
| T | method | 35 |
| U | key_findings | 55 |
| V | future_directions | 35 |
| W | connections_and_notes | 45 |
| X | pdf_filename | 30 |

### Formatting:
- **Header row**: Bold, frozen, auto-filter enabled on all columns
- **Text wrapping**: Enabled on all columns except paper_id, year
- **Row height**: Auto-fit to content

---

## Multi-Session Workflow

### First session
1. Ask for research areas and PDF location
2. List all PDFs in the folder. Note the total count.
3. Process papers one by one (read each into context, extract all fields)
4. Save Excel checkpoint every 5-10 papers
5. Display tag vocabulary and batch summary
6. At session end, report: "Processed papers 1-N. Say 'continue' next session to resume from paper N+1."

### Subsequent sessions
1. Load existing Excel
2. Note last paper_id and existing tag vocabulary
3. List all PDFs in the folder. Compare against `pdf_filename` column to find which are already done.
4. Report: "Found [total] PDFs. [done] already processed. Resuming from paper [next_id]."
5. Continue from next unprocessed PDF in the folder
6. Prefer existing tags over new synonyms
7. Append and save checkpoints
8. Display updated tag vocabulary and batch summary

### Batch output (every session)
1. Updated Excel file
2. Batch summary: papers processed, any issues
3. Updated tag vocabulary (sorted alphabetical list)
4. Quality flags: any cards that failed checks
5. **Resume instruction**: Always end every session with:
   ```
   ═══ SESSION COMPLETE: Processed papers [first_id]-[last_id] ([count] papers this session, [total] total). ═══
   ═══ To resume: "Continue building the knowledge base. Excel at [path]. PDFs at [path]." ═══
   ```

### For very large folders (500+ papers)
The workflow is the same. Just more sessions. Expect:
- ~10-15 papers per session (depending on paper length and context limits)
- Save progress religiously
- The user will say "continue" at the start of each new session
- **Never suggest switching to a regex batch script to "save time." The user chose this skill for quality.**

If you want to suggest the Anthropic Batch API as a faster automated alternative, you may do so once — but only as an option, not as a replacement for the default one-by-one reading approach.

---

## Edge Cases

- **Scanned PDFs**: If text extraction returns <500 characters for multi-page PDF: flag "OCR needed." Keep row as placeholder with paper_id, filename, and "OCR needed" in connections_and_notes. Move to next paper.
- **Not in English**: Flag language in connections_and_notes. Attempt extraction.
- **Very long papers (50+ pages)**: Note in paper_type. Truncation rules apply.
- **Duplicate detection**: Check by title (fuzzy match). Alert and skip if duplicate.
- **Non-standard structure**: Adapt per paper type guidance. Note in connections_and_notes.
- **Garbled extraction**: Note "Poor extraction — manual review needed" in connections_and_notes.
- **Re-extraction**: Overwrite existing row by paper_id. Don't duplicate.

---

## Query Mode

When the user asks a question about the knowledge base:

1. Load Excel into context
2. Answer using structured fields
3. Cite specific papers by Author (Year)
4. If deeper reading needed, tell the user which PDFs to upload

### Example queries:
- "Which papers use staggered DiD?" → Search `method`
- "What theories explain fraud spillovers?" → Search `topic_tags`, return `theoretical_lens` and `abstract`
- "What gap does the Bendig paper fill?" → Return `research_gaps_previous_lit`
- "Papers relevant to my guilt spillovers project" → Search `topic_tags`, `abstract`, `key_findings`
- "What should future research examine in ADHD-entrepreneurship?" → Filter by topic, aggregate `future_directions`

---

## Performance Expectations

- **Speed**: ~3-5 minutes per paper.
- **Batch size**: 8-12 papers per batch is optimal. Larger folders just mean more batches.
- **Context window**: Process one paper at a time. Load text → read → extract → save → clear → next.
- **Large folders**: 1,500 papers ≈ 100-150 sessions. Each session processes ~10-15 papers.
