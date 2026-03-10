#!/usr/bin/env python3
"""
Convert knowledge_base_final.xlsx to data.json for the web app.

Usage:
    cd 4_app
    python3 build_data.py

Input:  ../3_standardized/knowledge_base_final.xlsx
Output: data.json
"""

import pandas as pd
import json
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(SCRIPT_DIR, '..', '3_standardized', 'knowledge_base_final.xlsx')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'data.json')

# Field mapping: app_field → excel_column
FIELD_MAP = {
    'id':         'paper_id',
    'authors':    'authors',
    'year':       'std_year',
    'title':      'title',
    'journal':    'std_journal',
    'journal_raw': 'journal',
    'type':       'std_paper_type',
    'abstract':   'std_abstract',
    'rq':         'std_rq',
    'findings':   'std_findings',
    'gaps':       'std_gaps',
    'future':     'std_future',
    'notes':      'std_notes',
    'tags':       'topic_tags',
    'tpL1':       'std_tpL1',
    'tpL2':       'std_tpL2',
    'tName':      'std_theory_L2_name',
    'tDisc':      'std_theory_L1_discipline',
    'theory_raw': 'theoretical_lens',
    'design':     'std_method_design',
    'technique':  'std_method_technique',
    'country':    'std_country',
    'region':     'std_region',
    'continent':  'std_continent',
    'dsType':     'std_dsType',
    'dsNamed':    'std_dsNamed',
    'sample_raw': 'std_sample_description',
    'controls':   'std_controls',
    'iv':         'std_iv',
    'dv':         'std_dv',
    'med':        'std_mediators',
    'mod':        'std_moderators',
}

# Fields that should be integers
INT_FIELDS = {'id', 'year'}


def clean_value(val, field_name):
    """Convert a value to JSON-safe format."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return '' if field_name not in INT_FIELDS else 0
    if field_name in INT_FIELDS:
        return int(val)
    # Convert tags from comma-separated to semicolon-separated
    if field_name == 'tags' and isinstance(val, str):
        return '; '.join(t.strip() for t in val.replace(',', ';').split(';') if t.strip())
    return str(val).strip()


def main():
    if not os.path.exists(EXCEL_PATH):
        print(f"ERROR: {EXCEL_PATH} not found")
        return

    df = pd.read_excel(EXCEL_PATH)
    print(f"Loaded {len(df)} papers from Excel")
    print(f"Columns: {len(df.columns)}")

    # Build JSON records
    papers = []
    for _, row in df.iterrows():
        paper = {}
        for app_field, excel_col in FIELD_MAP.items():
            if excel_col in df.columns:
                paper[app_field] = clean_value(row[excel_col], app_field)
            else:
                paper[app_field] = '' if app_field not in INT_FIELDS else 0
        papers.append(paper)

    # Validate
    journals = set(p['journal'] for p in papers)
    types = set(p['type'] for p in papers)
    year_range = (min(p['year'] for p in papers if p['year']),
                  max(p['year'] for p in papers if p['year']))

    print(f"\nJournals: {sorted(journals)}")
    print(f"Paper types: {sorted(types)}")
    print(f"Year range: {year_range[0]}–{year_range[1]}")

    # Write JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=None, separators=(',', ':'))

    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"\nWrote {len(papers)} papers to {OUTPUT_PATH} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    main()
