"""
STANDARDIZATION CODEBOOK
========================
Entrepreneurship Knowledge Database
Created: 2026-03-10

This file records every finalized standardization procedure for creating
new variables from the raw columns in '2_raw_extracted/'.

Each variable has:
  - Source column(s) from raw data
  - Standardization logic (the exact code/rules)
  - Decision rationale (why we chose this approach)
  - Date finalized

To run all standardizations:
    python standardization_codebook.py

Output: 3_standardized/knowledge_base_standardized.xlsx
"""

import pandas as pd
import os
import re

# ============================================================
# CONFIGURATION
# ============================================================
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', '2_raw_extracted')
OUTPUT_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'knowledge_base_standardized.xlsx')

RAW_FILES = [
    os.path.join(RAW_DIR, 'paper_knowledge_base_ETP.xlsx'),
    os.path.join(RAW_DIR, 'paper_knowledge_base_JBV.xlsx'),
    os.path.join(RAW_DIR, 'paper_knowledge_base_SEJ.xlsx'),
]


def load_raw_data():
    """Load and concatenate all raw extracted files."""
    dfs = [pd.read_excel(f) for f in RAW_FILES]
    df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(df)} papers from {len(RAW_FILES)} files.")
    return df


# ============================================================
# RAW DATA FIXES (runs before all standardization)
# ============================================================
# Patches raw columns for papers with OCR/extraction failures
# that were re-extracted from original PDFs.
# Date added: 2026-03-10
# ============================================================

def raw_data_fixes(df):
    """
    Patch raw data for papers with extraction failures.

    Three groups of fixes:
      1. JBV pids 111-120: OCR failures, re-extracted from PDFs
      2. ETP pids 1491, 1492, 1493, 1765, 1767, 1768: extraction failures, re-extracted from PDFs
      3. ETP pids 504, 718, 719: teaching cases misclassified as Empirical-qualitative
      4. ETP pid 1768: paper_type correction (Empirical-Quantitative → Review)

    Decision rationale:
      - These papers had empty or garbled fields in the raw extraction
      - Original PDFs were re-read and metadata extracted manually
      - Fixes applied at raw-data level so all downstream std_ functions benefit
      - Only JBV rows for pids 111-120 are patched (ETP/SEJ rows are fine)
      - List fields (IVs, DVs, etc.) converted to semicolon-separated strings
    """
    print("Applying raw data fixes...")

    def _list_to_str(val):
        """Convert list to semicolon-separated string, or empty string for None."""
        if val is None:
            return ''
        if isinstance(val, list):
            return '; '.join(str(v) for v in val)
        return str(val)

    # ── Field mapping: extraction dict key → raw column name ──
    FIELD_MAP = {
        'title': 'title',
        'research_question': 'research_question',
        'abstract': 'abstract',
        'research_gaps_previous_lit': 'research_gaps_previous_lit',
        'key_findings': 'key_findings',
        'sample': 'sample',
        'data_source': 'data_source',
        'method': 'method',
        'theoretical_lens': 'theoretical_lens',
        'country_context': 'country_context',
        'paper_type': 'paper_type',
        'notes': 'connections_and_notes',
    }
    LIST_FIELDS = {
        'independent_variables': 'independent_variables',
        'dependent_variables': 'dependent_variables',
        'mediators': 'mediators',
        'moderators': 'moderators',
        'control_variables': 'control_variables',
    }

    def _apply_extraction(df, pid, extraction, journal_filter=None):
        """Apply an extraction dict to matching rows."""
        mask = df['paper_id'] == pid
        if journal_filter:
            mask = mask & df['journal'].str.contains(journal_filter, case=False, na=False)
        if not mask.any():
            print(f"  WARNING: No rows found for pid={pid}" +
                  (f" journal={journal_filter}" if journal_filter else ""))
            return
        for ext_key, col_name in FIELD_MAP.items():
            if ext_key in extraction and extraction[ext_key] is not None:
                df.loc[mask, col_name] = extraction[ext_key]
        for ext_key, col_name in LIST_FIELDS.items():
            if ext_key in extraction:
                df.loc[mask, col_name] = _list_to_str(extraction[ext_key])

    # ================================================================
    # GROUP 1: JBV papers pids 111-120 (OCR failures)
    # Re-extracted from PDFs in /1_raw_pdfs/JBV/
    # Only patch JBV rows (ETP/SEJ rows for same pids are fine)
    # ================================================================
    JBV_FIXES = {
        111: {
            'title': 'Technology-Based, "Adolescent" Firm Configurations: Strategy Identification, Context, and Performance',
            'research_question': 'What patterns of strategy, context, and performance characterize technology-based firms in their "adolescent" stage (5-12 years old)?',
            'abstract': 'This study provides insight into strategic and contextual factors related to success for 162 "adolescent" (5-12 years old) firms, competing within a variety of rapidly changing technology-based industries. Analyses focus on pinpointing patterns of strategy, context, and performance. Six nonmutually exclusive dimensions of strategy were identified: (1) technology/product leader; (2) product/market breadth; (3) marketing/sales expertise; (4) quality/service; (5) customer alliances; and (6) specialization.',
            'research_gaps_previous_lit': 'Prior literature lacked systematic examination of how strategic patterns relate to contextual factors and performance outcomes in adolescent technology-based firms.',
            'key_findings': 'Six distinct firm clusters identified with different strategic emphases and performance outcomes. Defenders/specialists achieved high performance in operating efficiency and market development. Technology leaders showed highest R&D results and sales growth. Firms lacking clear strategic profile were poor performers.',
            'independent_variables': ['Strategy dimensions (6 types)', 'Environmental instability', 'Stage of product development', 'Firm age'],
            'dependent_variables': ['R&D results', 'Operating efficiency', 'Market development', 'Sales growth', 'Future prospects', 'Overall performance'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Environmental instability', 'Product development stage', 'Firm age'],
            'sample': 'N=162 technology-based firms, aged 5-12 years',
            'data_source': 'Survey/questionnaire of firm executives',
            'method': 'Empirical-Quantitative; Cross-sectional survey; Cluster analysis; ANOVA',
            'theoretical_lens': 'Miles and Snow strategy framework; K-selection and r-selection theory',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Examines strategic configurations in rapidly changing technology industries. Uses cluster analysis to identify strategic patterns.',
        },
        112: {
            'title': 'The cognitive perspective: a valuable tool for answering entrepreneurship\'s basic "why" questions',
            'research_question': 'Can a cognitive perspective provide insights into three basic questions: (1) Why do some persons but not others choose to become entrepreneurs? (2) Why do some persons but not others recognize opportunities? (3) Why are some entrepreneurs more successful than others?',
            'abstract': 'This paper suggests that a cognitive perspective may provide important insights into key aspects of the entrepreneurial process. It is proposed that this perspective can help answer three basic questions about why some persons choose entrepreneurship, recognize opportunities, and succeed. Specific cognitive factors relevant to each question are identified.',
            'research_gaps_previous_lit': 'Prior entrepreneurship literature had not systematically incorporated cognitive psychology perspectives to understand entrepreneur decision-making, opportunity recognition, and success.',
            'key_findings': 'Prospect theory explains entrepreneur risk-taking through loss framing; cognitive biases (optimistic bias, planning fallacy, illusion of control) influence entrepreneurial decisions; opportunity recognition involves perceptual processes and pattern recognition.',
            'independent_variables': None,
            'dependent_variables': None,
            'mediators': None,
            'moderators': None,
            'control_variables': None,
            'sample': None,
            'data_source': 'Theoretical review and integration; no empirical data collection',
            'method': 'Conceptual; Theoretical framework development; Literature review and synthesis',
            'theoretical_lens': 'Cognitive psychology; Prospect theory; Decision-making theory; Affect regulation theory; Alertness theory',
            'country_context': 'United States',
            'paper_type': 'Conceptual',
            'notes': 'Theoretical paper introducing cognitive perspective to entrepreneurship research. Proposes that cognitive mechanisms are essential to understanding entrepreneurship.',
        },
        113: {
            'title': 'Counterfactual Thinking and Venture Formation: The Potential Effects of Thinking About "What Might Have Been"',
            'research_question': 'Are entrepreneurs less likely than other individuals to engage in counterfactual thinking, and does this cognitive pattern contribute to their decisions to start new ventures?',
            'abstract': 'This study investigates the potential effects of counterfactual thinking on new venture formation. Three groups were compared: entrepreneurs, potential entrepreneurs, and non-entrepreneurs. Results indicated entrepreneurs were significantly less likely to engage in counterfactual thinking and experienced less regret over past events.',
            'research_gaps_previous_lit': 'Counterfactual thinking had not previously been examined in the context of new venture formation. The cognitive mechanisms underlying entrepreneurial decisions remained poorly understood.',
            'key_findings': 'Entrepreneurs were significantly less likely to engage in counterfactual thinking than potential or non-entrepreneurs. Entrepreneurs experienced less regret about past events and found it easier to admit past mistakes.',
            'independent_variables': ['Entrepreneurial status (entrepreneur vs. potential entrepreneur vs. non-entrepreneur)'],
            'dependent_variables': ['Counterfactual thinking tendency', 'Regret over past events', 'Admission of past mistakes'],
            'mediators': ['Negative affective states'],
            'moderators': None,
            'control_variables': None,
            'sample': 'Three groups of individuals: entrepreneurs, potential entrepreneurs, non-entrepreneurs',
            'data_source': 'Survey/questionnaire assessing counterfactual thinking and regret',
            'method': 'Empirical-Quantitative; Cross-sectional; Group comparison; Statistical testing',
            'theoretical_lens': 'Cognitive psychology; Affect regulation; Entrepreneurial decision-making',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Pioneering work connecting cognitive biases to entrepreneurial behavior.',
        },
        114: {
            'title': 'Towards understanding who makes corporate venture capital investments and why',
            'research_question': 'When do established firms participate in corporate venture capital (CVC) investments? How do industry conditions and firm resources influence CVC investment decisions?',
            'abstract': 'This study examines when established firms participate in corporate venture capital. Using the resource-based view and longitudinal data on 477 firms from 1990 to 2000, findings show that firms in industries with rapid technological change, high competitive intensity and weak appropriability engage in greater CVC activity.',
            'research_gaps_previous_lit': 'Prior research had limited understanding of when and why established firms engage in CVC investments. The interaction between industry conditions and firm resources had not been systematically examined.',
            'key_findings': 'Industry technological change positively associated with CVC activity. Competitive intensity positively associated with CVC partnerships. Firms with strong technological resources more likely to engage in CVC. Firm resources moderate industry effects in non-linear ways.',
            'independent_variables': ['Industry technological change rate', 'Industry competitive intensity', 'Appropriability regime strength', 'Firm technological resources', 'Firm marketing resources', 'Diverse venturing experience'],
            'dependent_variables': ['Number of new CVC partnerships', 'CVC investment activity'],
            'mediators': None,
            'moderators': ['Firm technological resources', 'Firm marketing resources', 'Prior CVC experience'],
            'control_variables': ['Industry characteristics', 'Firm characteristics (size, age)'],
            'sample': 'N=477 firms from 1990 Fortune 500 list across 312 primary industries; longitudinal 1990-2000',
            'data_source': 'Secondary data from Fortune 500 list, patent databases, Thomson Financial databases',
            'method': 'Empirical-Quantitative; Longitudinal panel data; Regression analysis; Interaction effects',
            'theoretical_lens': 'Resource-based view; Strategic flexibility theory; Dynamic capabilities',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Longitudinal study of corporate entrepreneurship through CVC partnerships.',
        },
        115: {
            'title': 'Parent inheritance, founder expertise, and venture strategy: Determinants of new venture knowledge impact',
            'research_question': 'How do parent firm knowledge, founder expertise, and venture technological strategy influence the creation of impactful knowledge by new ventures spawned from established firms?',
            'abstract': 'This study examines how the knowledge available to a venture from its parent firms and individual founders, as well as its initial technological direction, influences its creation of impactful knowledge. Testing with 219 biotechnology ventures founded 1990-2000 and tracked through 2010 reveals inverted-U relationship between venture-parent knowledge overlap and knowledge impact.',
            'research_gaps_previous_lit': 'Prior genealogical literature assumed knowledge transfer from parent to progeny occurred spontaneously without examining founder choices. The role of founder expertise independent of parent firm knowledge had not been examined.',
            'key_findings': 'Inverted-U shaped relationship: moderate overlap with parent knowledge produces highest impact knowledge. Founder divergence from parent firm knowledge negatively affects venture knowledge impact. Moderate divergence from parent technological direction yields superior knowledge creation outcomes.',
            'independent_variables': ['Venture technological domain overlap with parent', 'Founder knowledge domain divergence from parent', 'Founder technical expertise breadth'],
            'dependent_variables': ['Venture knowledge impact (measured by forward patent citations)'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Venture characteristics', 'Industry characteristics', 'Founder characteristics'],
            'sample': 'N=219 biotechnology ventures founded 1990-2000; tracked through 2010',
            'data_source': 'Dow Jones VentureSource database; NBER database; patent databases',
            'method': 'Empirical-Quantitative; Longitudinal; Patent citation analysis; Regression analysis',
            'theoretical_lens': 'Genealogical theory of new venture creation; Knowledge recombination theory; Organizational learning theory',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Uses patent data to measure knowledge impact of spinoff ventures from established firms.',
        },
        116: {
            'title': 'Self-Employment Entry Across Industry Groups',
            'research_question': 'How do barriers to self-employment entry vary across different industry groups, and what personal characteristics predict self-employment entry within specific industries?',
            'abstract': 'Highly educated individuals possessing substantial net worth are most likely to enter self-employment. Entry barriers shape not only the decision to enter but also the types of industries that potential business owners enter.',
            'research_gaps_previous_lit': 'Prior studies treated self-employment as a homogeneous phenomenon, but entry barriers differ substantially across industries.',
            'key_findings': 'Self-employment likelihood increases with age, peaking around age 40. In skilled services, advanced education is the strongest predictor; in construction, financial capital constraints are primary.',
            'independent_variables': ['Age', 'Education level', 'Net worth/financial capital', 'Race/ethnicity', 'Gender', 'Prior work experience', 'Industry type'],
            'dependent_variables': ['Self-employment entry (binary)'],
            'mediators': None,
            'moderators': ['Industry type'],
            'control_variables': ['Age', 'Prior work experience', 'Demographic characteristics'],
            'sample': 'N=24,428 adults observed over 32-month period',
            'data_source': 'Survey of Income and Program Participation (SIPP), 1984; U.S. Bureau of the Census',
            'method': 'Empirical-Quantitative; Longitudinal; Logit regression; Industry-specific analysis',
            'theoretical_lens': 'Human capital theory; Barriers to entry framework',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Uses large government survey data. Demonstrates importance of industry-specific analysis in entrepreneurship research.',
        },
        117: {
            'title': 'Financing Small Business Creation: The Case of Chinese and Korean Immigrant Entrepreneurs',
            'research_question': 'What are the actual sources and amounts of start-up capital used by Chinese and Korean immigrant entrepreneurs?',
            'abstract': 'Analysis of data from over 2,000 Korean-Chinese entrepreneurs shows that the majority of start-up capital came from family wealth and financial institution loans, mirroring financing patterns for all groups.',
            'research_gaps_previous_lit': 'Scholarly literature attributed Asian immigrant entrepreneurial success to rotating credit associations, but empirical evidence was lacking.',
            'key_findings': 'Family wealth and financial institution loans were the primary financing sources for all groups including Korean-Chinese immigrants. Rotating credit associations played minimal role.',
            'independent_variables': ['Ethnicity (Korean, Chinese, nonminority)', 'Firm and owner characteristics', 'Source of financing'],
            'dependent_variables': ['Start-up capital amount', 'Loan size', 'Debt-to-equity ratio', 'Financing source choice'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Firm characteristics', 'Owner characteristics'],
            'sample': 'N=2,000+ Korean and Chinese immigrant entrepreneurs who opened firms 1979-1987',
            'data_source': 'U.S. Bureau of the Census; self-reported startup capital data',
            'method': 'Empirical-Quantitative; Cross-sectional; Descriptive statistics; Regression analysis',
            'theoretical_lens': 'Social capital theory; Financial capital constraints; Ethnic entrepreneurship',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Challenges conventional wisdom about rotating credit associations.',
        },
        118: {
            'title': 'Survival patterns among newcomers to franchising',
            'research_question': 'What are survival patterns among franchisee versus non-franchise small firms? Does franchising reduce failure risk for newcomers?',
            'abstract': 'Franchise units have better survival prospects than independents at the establishment level, but young firms formed without a franchisor parent are more likely to remain in operation than franchised start-ups at the firm level. The inconsistency arises because 84% of new franchise establishments were units of multi-establishment corporations.',
            'research_gaps_previous_lit': 'Prior literature presented conflicting evidence on franchise survival rates. Firm-level versus establishment-level differences had not been clearly distinguished.',
            'key_findings': 'At establishment level: franchise units have better survival than independents. At firm level: franchisee firms have lower survival than independent start-ups. Multi-establishment franchisees adding new units face lower risk than newcomer franchisees.',
            'independent_variables': ['Franchise status', 'Unit of analysis (firm vs. establishment)', 'Industry type', 'Owner experience'],
            'dependent_variables': ['Firm/establishment survival', 'Years until closure'],
            'mediators': None,
            'moderators': ['Industry type', 'Corporate ownership structure'],
            'control_variables': ['Firm size', 'Owner characteristics', 'Industry characteristics'],
            'sample': 'N=52,088 young restaurant establishments from 1986-1987 cohort',
            'data_source': 'U.S. Census Bureau restaurant establishment data; IRS payroll data; CBO database',
            'method': 'Empirical-Quantitative; Longitudinal; Survival analysis; Comparative analysis',
            'theoretical_lens': 'Agency theory; Firm dynamics theory; Transaction cost economics',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Reconciles conflicting findings by distinguishing firm-level from establishment-level analysis.',
        },
        119: {
            'title': 'Restricted access to markets characterizes women-owned businesses',
            'research_question': 'Are women-owned businesses discriminated against when seeking to sell to government agencies and other businesses?',
            'abstract': 'When WBE traits such as firm size, age, and industry of operation are controlled for statistically, WBEs are shown to have less access to business clients than male-owned firms.',
            'research_gaps_previous_lit': 'Limited knowledge existed about whether WBE underrepresentation in business markets reflected capacity limitations or discriminatory barriers.',
            'key_findings': 'WBEs average $103,312 in sales versus $311,794 for male-owned firms. After controlling for capacity, WBEs significantly less likely than male-owned firms to sell to business clients, indicating gender-based discrimination.',
            'independent_variables': ['Owner gender', 'Firm size', 'Firm age', 'Industry type', 'Education level', 'Prior work experience'],
            'dependent_variables': ['Likelihood of selling to business clients', 'Likelihood of selling to government clients'],
            'mediators': None,
            'moderators': ['Firm size', 'Industry type', 'Firm age'],
            'control_variables': ['Firm characteristics (size, age, industry)', 'Owner characteristics'],
            'sample': 'N=nearly 40,000 small businesses nationwide, representative sample 1992',
            'data_source': 'U.S. Bureau of the Census CBO database; IRS small-business income tax returns 1992',
            'method': 'Empirical-Quantitative; Cross-sectional; Logistic regression; Stratified analysis',
            'theoretical_lens': 'Discrimination economics; Gender inequality; Market access theory',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Tests for discrimination by comparing same-sized firms in same industries.',
        },
        120: {
            'title': 'Analysis of young, small firms that have closed: delineating successful from unsuccessful closures',
            'research_question': 'How do successful firm closures differ from unsuccessful closures? What factors distinguish entrepreneurs who close successful firms from those whose firms fail?',
            'abstract': 'Owners often described their firms as "successful" when the closure decision was made. Alternative opportunities are identified as a key reason for choosing to discontinue successful firms.',
            'research_gaps_previous_lit': 'Literature typically equated firm closure with failure, ignoring that some successful firms close due to better opportunities.',
            'key_findings': 'Among closed firms: 37.7% described as successful at closure. Highly educated owners in skilled services often close successful firms due to attractive employment alternatives. Sunk costs and owner human capital differentiate successful from unsuccessful closures.',
            'independent_variables': ['Owner education level', 'Owner industry-specific experience', 'Owner demographics (gender, race)', 'Firm startup capitalization', 'Firm size at closure', 'Industry type'],
            'dependent_variables': ['Closure status (successful vs. unsuccessful)'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Firm characteristics', 'Owner characteristics', 'Industry characteristics'],
            'sample': 'N=1,425 young firms that closed between 1993-1996 (founded 1989-1992)',
            'data_source': 'U.S. Bureau of the Census CBO database; 1996 survey of 1992 business owners',
            'method': 'Empirical-Quantitative; Cross-sectional analysis of closures; Descriptive statistics; Comparative analysis',
            'theoretical_lens': 'Opportunity cost theory; Active learning model; Sunk cost theory',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Challenges assumption that closure equals failure.',
        },
    }

    # ── GROUP 2: ETP papers (extraction failures) ──
    ETP_FIXES = {
        1491: {
            'title': 'Role Model Performance Effects on Development of Entrepreneurial Career Preference',
            'research_question': 'Does the presence of a parent entrepreneurial role model affect the development of preference for an entrepreneurial career?',
            'abstract': 'This study examines how parental entrepreneurial role models influence offspring career preferences using Social Learning Theory. Results indicate that presence of a parent entrepreneurial role model is associated with increased education and training aspirations, task self-efficacy, and expectancy for an entrepreneurial career.',
            'research_gaps_previous_lit': 'Previous research identified parental entrepreneurship as a background factor but did not investigate whether parental role models actually affected career preference.',
            'key_findings': 'Individuals with high-performing parent entrepreneurial role models had significantly higher education aspirations, task self-efficacy, and expectancy for entrepreneurial careers compared to those with low-performing models or no model.',
            'independent_variables': ['Parental role model performance (high, low, none)'],
            'dependent_variables': ['Entrepreneurial career preference', 'Education and training aspirations', 'Task self-efficacy', 'Expectancy for entrepreneurial career entry'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Gender', 'Demographics (age, ethnicity, region)', 'Business education/training'],
            'sample': '366 junior and senior business administration students at a southeastern U.S. university, mean age 21 years',
            'data_source': 'Cross-sectional survey at single university; Likert-scale questionnaires',
            'method': 'Empirical-Quantitative; MANCOVA, ANOVA, canonical discriminant analysis',
            'theoretical_lens': 'Social Learning Theory (Bandura); career selection theory; role modeling',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Addresses criticism of trait approach by proposing environmental/learning mechanisms for entrepreneurial career choice.',
        },
        1492: {
            'title': 'Explorative and Exploitative Learning from External Corporate Ventures',
            'research_question': 'What antecedents drive explorative versus exploitative learning outcomes from external corporate ventures?',
            'abstract': 'This study examines factors influencing explorative versus exploitative learning from external corporate ventures among 110 largest U.S. ICT companies (1992-2000). Uses patent citation data to show that governance mode and technological relatedness significantly affect explorative learning likelihood.',
            'research_gaps_previous_lit': 'Prior studies focus on whether firms learn from external sources but not the type (explorative vs. exploitative) of learning outcomes.',
            'key_findings': 'Corporate venture capital investments more likely to yield explorative learning; tighter integration (joint ventures, acquisitions) favors exploitative learning. Technological unrelatedness increases explorative learning.',
            'independent_variables': ['Governance mode (CVC, alliance, joint venture, acquisition)', 'Industry relatedness', 'Downstream vertical relatedness', 'Technological relatedness'],
            'dependent_variables': ['Explorative learning (vs. exploitative)', 'Learning outcomes (patent citations)'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Company size', 'Prior patent activity', 'Industry factors'],
            'sample': '110 largest U.S. public ICT companies; 8,176 external ventures; 5,091 patents analyzed',
            'data_source': 'Patent citation data (Derwent), Thompson Financial Platinum database, Compustat',
            'method': 'Empirical-Quantitative; Logistic regression analysis of patent citations',
            'theoretical_lens': 'March exploration-exploitation framework; interorganizational learning theory; absorptive capacity',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Novel approach using patent citation data to measure learning types.',
        },
        1493: {
            'title': 'Scholarly Communities in Entrepreneurship Research: A Co-Citation Analysis',
            'research_question': 'What is the intellectual structure of entrepreneurship research? What distinct research streams exist?',
            'abstract': 'Bibliometric analysis examining co-citation patterns in entrepreneurship articles (2000-2004) identifies 25 research streams. Reveals entrepreneurship research is fragmented across multiple communities.',
            'research_gaps_previous_lit': 'Entrepreneurship research characterized as diverse and fragmented with no clear research trajectories. No widely accepted categorization of distinct research streams.',
            'key_findings': '25 distinct scholarly communities identified; 10 major groups include entrepreneurial networks, corporate entrepreneurship, entrepreneurial processes, value creation, opportunity recognition, psychological characteristics, and others.',
            'independent_variables': None,
            'dependent_variables': None,
            'mediators': None,
            'moderators': None,
            'control_variables': None,
            'sample': '733 articles published 2000-2004 in 30 entrepreneurship-related journals; over 21,000 cited references analyzed',
            'data_source': 'Social Sciences Citation Index (ISI Web of Science)',
            'method': 'Review; Bibliometric; Co-citation network analysis',
            'theoretical_lens': 'Bibliometric analysis; citation theory',
            'country_context': 'International',
            'paper_type': 'Review',
            'notes': 'Uses novel algorithm for bibliometric clustering; maps intellectual structure of entrepreneurship field.',
        },
        1765: {
            'title': 'Gender, Entrepreneurial Self-Efficacy, and Entrepreneurial Career Intentions: Implications for Entrepreneurship Education',
            'research_question': 'How do gender, entrepreneurial self-efficacy, and entrepreneurial intentions interact at different life stages?',
            'abstract': 'Examines relationships between gender, entrepreneurial self-efficacy, and career intentions in adolescents and MBA students. Finds gender differences in self-efficacy significantly mediate entrepreneurial intentions, with education effects stronger for women.',
            'research_gaps_previous_lit': 'Limited research on interactions between entrepreneurial self-efficacy, entrepreneurial intentions, and gender. Unclear whether self-efficacy effects differ by gender.',
            'key_findings': 'Teen girls show lower entrepreneurial self-efficacy and intentions than boys; relationship between self-efficacy and intentions stronger for girls. MBA women have lower self-efficacy than men. Entrepreneurship education increases self-efficacy more for MBA women than men.',
            'independent_variables': ['Gender', 'Age group (adolescent vs. adult)', 'Entrepreneurship education (MBA sample)'],
            'dependent_variables': ['Entrepreneurial self-efficacy', 'Entrepreneurial career intentions'],
            'mediators': ['Entrepreneurial self-efficacy'],
            'moderators': ['Gender'],
            'control_variables': ['School type/region', 'Socioeconomic status', 'Ethnicity'],
            'sample': 'Study 1: 4,292 middle/high school students from 29 schools; Study 2: 933 MBA students from 7 top-tier business schools',
            'data_source': 'Two separate survey studies (2002-2004)',
            'method': 'Empirical-Quantitative; Logistic regression, correlation analysis, moderation testing',
            'theoretical_lens': 'Self-efficacy theory (Bandura); Social Cognitive Career Theory; intentionality models',
            'country_context': 'United States',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Addresses gender gap in entrepreneurship by examining psychological mechanisms.',
        },
        1767: {
            'title': 'Family Business Survival and the Role of Boards',
            'research_question': 'Are family firms more likely to survive as viable entities than non-family firms? What board characteristics explain survival differences?',
            'abstract': 'Analyzes over 700,000 private UK firms (2007-2010) to determine family firm survival advantages and the role of board composition. Finds family firms significantly less likely to fail.',
            'research_gaps_previous_lit': 'Extensive succession literature but little empirical evidence on determinants of firm viability/bankruptcy. Major gap in board structure impacts on survival rates.',
            'key_findings': 'Family firm failure rate 1.3% vs. 1.8% for non-family firms; family firms have more stable boards, greater gender diversity, older/more experienced directors; board characteristics critical to explaining survival advantage.',
            'independent_variables': ['Family firm status', 'Board composition (turnover, gender diversity, age, experience, proximity, failed directorships, multiple directorships, independence)'],
            'dependent_variables': ['Firm survival (vs. bankruptcy)'],
            'mediators': None,
            'moderators': None,
            'control_variables': ['Firm size, age, sector', 'Financial metrics', 'Industry risk', 'Diversification', 'Subsidiary status'],
            'sample': '700,000+ private family and non-family firms in UK (2007-2010); 12,598 bankruptcy instances',
            'data_source': 'Companies House database (UK), Insolvency Service records, company accounts',
            'method': 'Empirical-Quantitative; Panel logistic regression; survival analysis (Shumway approach)',
            'theoretical_lens': 'Family business theory (SEW, survivability capital); agency theory; social capital theory; governance theory',
            'country_context': 'United Kingdom',
            'paper_type': 'Empirical-Quantitative',
            'notes': 'Large-scale systematic analysis of family firm survival with board-level determinants.',
        },
        1768: {
            'title': 'Franchising: An Overview',
            'research_question': 'What is franchising as a business model? What are key trends, opportunities, and challenges in the franchising industry?',
            'abstract': 'Provides comprehensive overview of franchising industry (estimated $176.9B in retail sales in 1975). Documents growth in new franchise sectors, market development strategies, international expansion, and emerging legal/regulatory framework.',
            'research_gaps_previous_lit': None,
            'key_findings': 'Franchising represents ~33% of U.S. retail sales and 11% of GNP; new sectors growing at 15-37% annually; traditional franchises declining; international opportunities expanding especially Japan/Canada.',
            'independent_variables': None,
            'dependent_variables': None,
            'mediators': None,
            'moderators': None,
            'control_variables': None,
            'sample': None,
            'data_source': 'U.S. Department of Commerce data, franchise industry statistics (1973-1975)',
            'method': 'Review; Descriptive overview with industry statistics',
            'theoretical_lens': 'Institutional economics; marketing channels; business strategy',
            'country_context': 'United States',
            'paper_type': 'Review',
            'notes': 'Non-empirical overview piece; documents industry in transition.',
        },
    }

    # ── GROUP 3: Teaching case reclassifications (ETP only) ──
    # pids 504, 718, 719 are teaching cases misclassified as Empirical-qualitative in ETP
    TEACHING_CASE_FIXES = {
        504: 'Editorial',   # The Pharos Project
        718: 'Editorial',   # Blue Moon Natural Foods
        719: 'Editorial',   # Sparrow Therapeutics Exit Strategy
    }

    # ── Apply JBV fixes (only JBV rows) ──
    jbv_count = 0
    for pid, extraction in JBV_FIXES.items():
        _apply_extraction(df, pid, extraction, journal_filter='Journal of Business Venturing')
        jbv_count += 1
    print(f"  Applied {jbv_count} JBV paper fixes (pids 111-120)")

    # ── Apply ETP fixes (no journal filter needed; these pids are unique to ETP) ──
    etp_count = 0
    for pid, extraction in ETP_FIXES.items():
        _apply_extraction(df, pid, extraction)  # No journal filter — pids unique to ETP
        etp_count += 1
    print(f"  Applied {etp_count} ETP paper fixes (pids 1491-1493, 1765, 1767, 1768)")

    # ── Apply teaching case reclassifications (ETP only) ──
    for pid, new_type in TEACHING_CASE_FIXES.items():
        mask = (df['paper_id'] == pid) & (
            df['journal'].str.contains('Entrepreneurship Theory and Practice|American Journal of Small Business',
                                        case=False, na=False))
        if mask.any():
            df.loc[mask, 'paper_type'] = new_type
            print(f"  Reclassified ETP pid={pid} paper_type → {new_type}")
        else:
            print(f"  WARNING: No ETP row found for pid={pid}")

    total = jbv_count + etp_count + len(TEACHING_CASE_FIXES)
    print(f"  Total fixes applied: {total}")
    return df


# ============================================================
# STANDARDIZATION FUNCTIONS
# ============================================================
# Each function below corresponds to one finalized variable.
# Add new functions as we finalize each variable.
# ============================================================


# ============================================================
# VARIABLE 0: std_year
# ============================================================
# Source: year (raw)
# Approach: Clean raw year + manual corrections for 8 invalid/missing entries
# Date finalized: 2026-03-10

def std_year(df):
    """
    Variable: std_year
    Source column(s): year
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'year' column has 17 problematic entries:
        6 NaN, 2 with year=0, 1 with year='Unknown', 8 with year='DUPLICATE'
      - Correct years looked up from ScienceDirect/web search/PDF metadata
      - DUPLICATE entries get year from their original paper's title
      - 'Unknown' entry (pid=729) year=2001 confirmed via PDF metadata (creation date June 2001)
      - All values converted to integer
    """
    print("Standardizing year...")

    # Manual corrections for missing/invalid years
    # Key: (paper_id, title[:40]) → corrected year
    YEAR_CORRECTIONS = {
        (6, 'From science to technology to products '): 2000,     # Abetti, JBV
        (73, 'The Rise and Fall of the Merlin-Gerin F'): 1995,    # Badguerahanian & Abetti, JBV
        (111, 'Technology-Based, "Adolescent" Firm Con'): 1998,       # Bantel, JBV (title updated by raw_data_fixes)
        (113, 'Counterfactual Thinking and Venture Form'): 2000,    # Baron, JBV (title updated by raw_data_fixes)
        (826, 'OCR FAILED – Limited attention and the '): 1997,    # Gifford, JBV
        (1325, 'NON-RESEARCH: The birth and growth of T'): 1997,   # Abetti (Toshiba), JBV
        (729, 'Advantage beyond founding: The strategic'): 2001,    # Kelley & Rice, JBV (year='Unknown', confirmed via PDF metadata)
        (1046, 'DUPLICATE of Paper 1045: Patel et al. 20'): 2019,  # Patel et al., SEJ
        (1052, 'DUPLICATE of Paper 1051: Patzelt et al. '): 2020,  # Patzelt et al., SEJ
        (1354, 'DUPLICATE of paper 1353 (Unger et al. 2'): 2011,   # Unger et al., ETP
        (1357, 'DUPLICATE of paper 1356 (Uy et al. 2015'): 2015,   # Uy et al., ETP
        (1435, 'DUPLICATE of paper 1434 (Williams & Shep'): 2016,  # Williams & Shepherd, ETP
        (1448, 'DUPLICATE of paper 1447 (Wood et al. 201'): 2017,  # Wood et al., ETP
        (1461, 'DUPLICATE of paper 1460 (Yamakawa & Card'): 2017,  # Yamakawa & Cardon, ETP
        (1480, 'DUPLICATE of paper 1479 (Yu et al. 2022 '): 2022,  # Yu et al., ETP
        (1481, 'DUPLICATE of paper 1477 (Yu et al. 2023 '): 2023,  # Yu et al., ETP
        (1482, 'DUPLICATE of paper 1477 (Yu et al. 2023 '): 2023,  # Yu et al., ETP
    }

    # Copy raw year and convert to numeric
    df['std_year'] = pd.to_numeric(df['year'], errors='coerce')

    # Apply manual corrections
    corrected = 0
    for idx in df.index:
        y = df.at[idx, 'std_year']
        if pd.isna(y) or y == 0:
            pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
            title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''
            for (oid, tstart), correct_year in YEAR_CORRECTIONS.items():
                if pid == oid and title.startswith(tstart):
                    df.at[idx, 'std_year'] = correct_year
                    corrected += 1
                    break

    # Convert to integer (NaN-safe)
    df['std_year'] = df['std_year'].astype('Int64')

    # Validation
    filled = df['std_year'].notna().sum()
    still_missing = df['std_year'].isna().sum()
    yr_min = df['std_year'].min()
    yr_max = df['std_year'].max()
    print(f"std_year: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"Corrected: {corrected} entries")
    print(f"Still missing: {still_missing}")
    print(f"Range: {yr_min} - {yr_max}")

    return df


# ============================================================
# VARIABLE 0b: std_journal
# ============================================================
# Source: journal (raw) + pdf_filename (to infer from PDF folder)
# Approach: PDF folder lookup → raw journal text mapping → manual overrides
# Date finalized: 2026-03-10

def std_journal(df):
    """
    Variable: std_journal
    Source column(s): journal, pdf_filename
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'journal' column has 20 distinct values + 28 NaN entries
      - Three core journals: ETP (1,568), JBV (1,505), SEJ (454)
      - "American Journal of Small Business" (221) is ETP's predecessor (renamed 1988) → maps to ETP
      - 9 ETP spelling variants (colon, ampersand, etc.) → ETP
      - 28 NaN entries: 27 confirmed ETP from PDF folder, 1 (Samuelsson 2021) confirmed ETP via web search
      - 15 DUPLICATE entries: inherit journal from original paper
      - 16 papers with other journal names (JSBM, SBE, FBR, etc.): extraction errors,
        actual journal inferred from PDF folder where possible → "Other" if not resolvable
      - "Vol. 46(1)" (pid=1521, Sekerci 2022) confirmed ETP via web search
      - "Unknown" (pid=1477) in ETP folder → ETP
      - "NON-RESEARCH" (pid=1325) in ETP folder → ETP
      - Final categories: ETP, JBV, SEJ, Other
    """
    print("Standardizing journal...")

    # --- Layer 1: Build PDF folder lookup ---
    PDF_BASE = os.path.join(os.path.dirname(__file__), '..', '1_raw_pdfs')
    pdf_to_folder = {}
    for folder in ['ETP', 'JBV', 'SEJ']:
        folder_path = os.path.join(PDF_BASE, folder)
        if os.path.exists(folder_path):
            for f in os.listdir(folder_path):
                pdf_to_folder[f] = folder

    # --- Layer 2: Raw journal text mapping ---
    JOURNAL_MAP = {
        'Entrepreneurship Theory and Practice': 'ETP',
        'Entrepreneurship: Theory and Practice': 'ETP',
        'Entrepreneurship Theory & Practice': 'ETP',
        'American Journal of Small Business': 'ETP',
        'American Journal of Small Business (later Entrepreneurship Theory and Practice)': 'ETP',
        'Journal of Business Venturing': 'JBV',
        'Strategic Entrepreneurship Journal': 'SEJ',
    }

    # --- Layer 3: Manual overrides for edge cases ---
    # Key: (paper_id, title[:40]) → journal
    JOURNAL_OVERRIDES = {
        # NaN journal, not in any PDF folder — confirmed ETP via web search
        (1460, 'Path Dependence in New Ventures Capital '): 'ETP',
        # "Vol. 46(1)" — confirmed ETP Vol 46(1) via web search (Sekerci et al. 2022)
        (1521, "Investors' Reactions to CSR News in Fami"): 'ETP',
    }

    results = []
    corrected_folder = 0
    corrected_map = 0
    corrected_override = 0
    other_count = 0

    for idx in df.index:
        pdf = str(df.at[idx, 'pdf_filename']) if pd.notna(df.at[idx, 'pdf_filename']) else ''
        raw_j = str(df.at[idx, 'journal']) if pd.notna(df.at[idx, 'journal']) else ''
        pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
        title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

        # Check manual overrides first
        override_val = None
        for (oid, tstart), oj in JOURNAL_OVERRIDES.items():
            if pid == oid and title.startswith(tstart):
                override_val = oj
                break

        if override_val:
            results.append(override_val)
            corrected_override += 1
        elif pdf in pdf_to_folder:
            results.append(pdf_to_folder[pdf])
            corrected_folder += 1
        elif raw_j in JOURNAL_MAP:
            results.append(JOURNAL_MAP[raw_j])
            corrected_map += 1
        elif raw_j in ('DUPLICATE', 'NON-RESEARCH', 'Unknown', '') or raw_j == 'nan':
            # Try to infer from DUPLICATE title or set Other
            # DUPLICATE entries: check if original paper's journal can be found
            if raw_j == 'DUPLICATE':
                import re as _re
                m = _re.search(r'paper (\d+)', str(df.at[idx, 'title']), _re.I)
                if m:
                    orig_pid = int(m.group(1))
                    orig_rows = df[df['paper_id'] == orig_pid]
                    found = False
                    for _, orig_r in orig_rows.iterrows():
                        orig_pdf = str(orig_r['pdf_filename']) if pd.notna(orig_r['pdf_filename']) else ''
                        if orig_pdf in pdf_to_folder:
                            results.append(pdf_to_folder[orig_pdf])
                            found = True
                            corrected_folder += 1
                            break
                        orig_j = str(orig_r['journal']) if pd.notna(orig_r['journal']) else ''
                        if orig_j in JOURNAL_MAP:
                            results.append(JOURNAL_MAP[orig_j])
                            found = True
                            corrected_map += 1
                            break
                    if not found:
                        results.append('Other')
                        other_count += 1
                else:
                    results.append('Other')
                    other_count += 1
            else:
                results.append('Other')
                other_count += 1
        else:
            # Other journals (JSBM, SBE, FBR, etc.) — extraction errors
            results.append('Other')
            other_count += 1

    df['std_journal'] = results

    # Validation
    vc = df['std_journal'].value_counts()
    print("std_journal distribution:")
    for j, c in vc.items():
        print(f"  {j}: {c} ({c/len(df)*100:.1f}%)")
    print(f"Resolved via: folder={corrected_folder}, text_map={corrected_map}, override={corrected_override}, other={other_count}")

    return df


# ============================================================
# VARIABLE 0c: std_abstract
# ============================================================
# Source: abstract (raw)
# Approach: Cleanup + DUPLICATE recovery from original papers
# Date finalized: 2026-03-10

def std_abstract(df):
    """
    Variable: std_abstract
    Source column(s): abstract
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'abstract' column contains AI-generated summaries (not original abstracts)
      - 3,715 entries (97.2%) are clean and usable — copied as-is
      - 106 problematic entries (2.8%) break down as:
        * 58 DUPLICATE references (just say "Duplicate of paper X")
        * 18 NaN (completely missing)
        * 14 editorial board listings
        * 7 N/A editorial/intro placeholders
        * 6 OCR FAILED / garbled
        * 3 FILE NOT FOUND
      - DUPLICATE entries: recover abstract from original paper (resolves ~57 of 58)
      - All other problematic entries: set to empty (legitimate gaps — editorials,
        OCR failures, missing files)
    """
    print("Standardizing abstract...")

    # --- Detect problematic abstracts ---
    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        # DUPLICATE references
        if s_lower.startswith('duplicate'):
            return True
        # OCR failures
        if any(p in s_lower for p in ['ocr failed', 'garbled', 'text extraction failed',
                                       'no text could be extracted']):
            return True
        # N/A placeholders
        if s.startswith('N/A'):
            return True
        # Editorial board listings (only if it's the entire content, not mentioned in passing)
        if s_lower.startswith('editorial board listing'):
            return True
        # FILE NOT FOUND
        if 'file not found' in s_lower:
            return True
        # Editorial note (very short)
        if s_lower in ('editorial note.', 'editorial note'):
            return True
        return False

    # --- Extract original paper_id from DUPLICATE text ---
    def extract_orig_pid(row):
        """Try to find original paper_id from abstract or title text."""
        for field in ['abstract', 'title']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            # Pattern 1: "paper 1320", "Paper 624"
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            # Pattern 2: "paper_id 182", "ID 408"
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            # Pattern 3: "Same paper as ID 253"
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    # --- Find best abstract from original paper ---
    def get_orig_abstract(orig_pid, df):
        """Get a clean abstract from the original paper."""
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            abs_text = str(o['abstract']) if pd.notna(o['abstract']) else ''
            if len(abs_text) > 50 and not is_problematic(o['abstract']):
                return abs_text
        return None

    # --- Manual override for pid=528 (title starts with "DUPLICATE:" but no paper ref number) ---
    ABSTRACT_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
    }

    # --- Process all rows ---
    results = []
    copied = 0
    recovered_dup = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, 'abstract']

        if not is_problematic(raw):
            # Clean abstract — copy as-is
            results.append(str(raw).strip())
            copied += 1
        else:
            # Check if it's a DUPLICATE we can recover
            is_dup = pd.notna(raw) and 'duplicate' in str(raw).lower()[:30]
            if not is_dup:
                # Also check title for DUPLICATE
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_dup = 'duplicate' in title.lower()[:20]

            if is_dup:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                # Check manual overrides
                orig_pid = None
                for (oid, tstart), opid in ABSTRACT_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_abs = get_orig_abstract(orig_pid, df)
                    if orig_abs:
                        results.append(orig_abs)
                        recovered_dup += 1
                        continue

            # Could not recover — set empty
            results.append(None)
            set_empty += 1

    df['std_abstract'] = results

    # Validation
    filled = df['std_abstract'].notna().sum()
    empty = df['std_abstract'].isna().sum()
    print(f"std_abstract: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied}")
    print(f"  Recovered from DUPLICATE originals: {recovered_dup}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


# ============================================================
# VARIABLE 0d: std_rq
# ============================================================
# Source: research_question (raw)
# Approach: Cleanup + DUPLICATE/cross-reference recovery from original papers
# Date finalized: 2026-03-10

def std_rq(df):
    """
    Variable: std_rq
    Source column(s): research_question
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'research_question' column contains AI-extracted research questions
      - 3,632 entries are clean and usable — copied as-is
      - Problematic entries:
        * 107 NaN
        * 48 DUPLICATE placeholders
        * 18 N/A (editorials, commentaries, teaching cases)
        * 15 NON-RESEARCH placeholders
        * 7 OCR/extraction failures
        * 3 FILE NOT FOUND
        * 2 "See paper X" cross-references
        * 1 RETRACTED
      - DUPLICATE + "See paper X" entries: recover from original paper
      - All other problematic entries: set to empty
    """
    print("Standardizing research_question...")

    SRC_COL = 'research_question'

    # --- Detect problematic entries ---
    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    # --- Extract original paper_id from text ---
    def extract_orig_pid(row):
        """Try to find original paper_id from research_question or title text."""
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            # "paper 1320", "Paper 624"
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            # "paper_id 182", "ID 408"
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            # "Same paper as ID 253"
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    # --- Find best value from original paper ---
    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 30 and not is_problematic(o[SRC_COL]):
                return val
        return None

    # --- Manual overrides for cross-references without standard patterns ---
    RQ_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    # --- Process all rows ---
    results = []
    copied = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            results.append(str(raw).strip())
            copied += 1
        else:
            # Check if recoverable (DUPLICATE or "See paper X")
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                # Also check title for DUPLICATE
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                # Check manual overrides
                orig_pid = None
                for (oid, tstart), opid in RQ_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            # Could not recover — set empty
            results.append(None)
            set_empty += 1

    df['std_rq'] = results

    # Validation
    filled = df['std_rq'].notna().sum()
    print(f"std_rq: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


# ============================================================
# VARIABLE 0e: std_findings
# ============================================================
# Source: key_findings (raw)
# Approach: Strip redundant "Finding:"/"Finding N:" prefixes + DUPLICATE recovery
# Date finalized: 2026-03-10

def std_findings(df):
    """
    Variable: std_findings
    Source column(s): key_findings
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'key_findings' column contains AI-extracted findings, but with messy formatting:
        * "Finding 1: ... Finding 2: ..." (619 papers) — redundant numbered prefixes
        * "Finding: ... Finding: ..." (1,714 papers) — redundant repeated prefix
        * "H1a/Finding: ..." (23 papers) — hybrid prefix, cleaned to "H1a: ..."
      - "H1:", "H2a:", "P1:", "P2:" prefixes are KEPT — they carry hypothesis/proposition info
      - Standard problem patterns: 50 DUPLICATE, 24 N/A, 15 NON-RESEARCH, 4 OCR, 3 FILE NOT FOUND
      - Cleanup: strip "Finding"/"Finding N:" prefixes, normalize whitespace
      - Recovery: DUPLICATE + "See paper X" entries resolved from originals
    """
    print("Standardizing key_findings...")

    SRC_COL = 'key_findings'

    # --- Clean formatting ---
    def clean_text(text):
        s = str(text).strip()
        # 'H1a/Finding:' -> 'H1a:'
        s = re.sub(r'(H\d+[a-z]?)/Finding:\s*', r'\1: ', s)
        # 'Finding N:' -> remove
        s = re.sub(r'Finding \d+:\s*', '', s)
        # Standalone 'Finding:' -> remove (at start or after whitespace)
        s = re.sub(r'(?:^|(?<=\s))Finding:\s*', '', s)
        # Clean double spaces
        s = re.sub(r'  +', ' ', s).strip()
        # Clean leading semicolons/spaces
        s = re.sub(r'^[;\s]+', '', s).strip()
        return s

    # --- Detect problematic entries ---
    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    # --- Extract original paper_id ---
    def extract_orig_pid(row):
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    # --- Find best value from original paper ---
    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 30 and not is_problematic(o[SRC_COL]):
                return clean_text(val)
        return None

    # --- Manual overrides ---
    FINDINGS_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    # --- Process all rows ---
    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            # Clean and copy
            results.append(clean_text(raw))
            copied_clean += 1
        else:
            # Check if recoverable
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in FINDINGS_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df['std_findings'] = results

    # Validation
    filled = df['std_findings'].notna().sum()
    print(f"std_findings: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Cleaned and copied: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def std_gaps(df):
    """
    Variable: std_gaps
    Source column(s): research_gaps_previous_lit
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'research_gaps_previous_lit' column contains AI-extracted research gaps
      - No formatting issues (unlike findings) — content is clean prose
      - Standard problem patterns: 48 DUPLICATE, 2 "See paper X", 55 N/A, 7 OCR/FILE
      - Recovery: DUPLICATE + "See paper X" entries resolved from originals
      - Remaining unrecoverable entries set to NaN
    """
    print("Standardizing research_gaps_previous_lit...")

    SRC_COL = 'research_gaps_previous_lit'

    # --- Detect problematic entries ---
    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    # --- Extract original paper_id ---
    def extract_orig_pid(row):
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    # --- Find best value from original paper ---
    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 30 and not is_problematic(o[SRC_COL]):
                return val.strip()
        return None

    # --- Manual overrides ---
    GAPS_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    # --- Process all rows ---
    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            # Copy as-is (no formatting cleanup needed)
            results.append(str(raw).strip())
            copied_clean += 1
        else:
            # Check if recoverable
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in GAPS_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df['std_gaps'] = results

    # Validation
    filled = df['std_gaps'].notna().sum()
    print(f"std_gaps: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def std_future(df):
    """
    Variable: std_future
    Source column(s): future_directions
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'future_directions' column contains AI-extracted future research directions
      - No formatting issues — content is clean prose
      - Standard problem patterns: 48 DUPLICATE, 2 "See paper X", 35 N/A, 15 NON-RESEARCH, 7 OCR/FILE
      - Recovery: DUPLICATE + "See paper X" entries resolved from originals
    """
    print("Standardizing future_directions...")

    SRC_COL = 'future_directions'

    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    def extract_orig_pid(row):
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 30 and not is_problematic(o[SRC_COL]):
                return val.strip()
        return None

    FUTURE_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            results.append(str(raw).strip())
            copied_clean += 1
        else:
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in FUTURE_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df['std_future'] = results

    filled = df['std_future'].notna().sum()
    print(f"std_future: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def std_notes(df):
    """
    Variable: std_notes
    Source column(s): connections_and_notes
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'connections_and_notes' column contains AI-extracted cross-references and notes
      - No formatting issues — content is clean prose
      - Standard problem patterns: 59 DUPLICATE, 2 "See paper X", 37 NON-RESEARCH, 5 OCR/FILE
      - Recovery: DUPLICATE + "See paper X" entries resolved from originals
    """
    print("Standardizing connections_and_notes...")

    SRC_COL = 'connections_and_notes'

    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    def extract_orig_pid(row):
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 30 and not is_problematic(o[SRC_COL]):
                return val.strip()
        return None

    NOTES_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            results.append(str(raw).strip())
            copied_clean += 1
        else:
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in NOTES_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df['std_notes'] = results

    filled = df['std_notes'].notna().sum()
    print(f"std_notes: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def std_sample_description(df):
    """
    Variable: std_sample_description
    Source column(s): sample
    Date finalized: 2026-03-10

    Decision rationale:
      - Raw 'sample' column contains AI-extracted sample descriptions
      - No formatting issues — content is clean prose
      - High N/A count (444) because many non-empirical papers legitimately have no sample
      - Standard problem patterns: 48 DUPLICATE, 2 "See paper X", 444 N/A, 15 NON-RESEARCH, 6 OCR/FILE
      - Recovery: DUPLICATE + "See paper X" entries resolved from originals
    """
    print("Standardizing sample...")

    SRC_COL = 'sample'

    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    def extract_orig_pid(row):
        for field in [SRC_COL, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    def get_orig_value(orig_pid, df):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[SRC_COL]) if pd.notna(o[SRC_COL]) else ''
            if len(val) > 20 and not is_problematic(o[SRC_COL]):
                return val.strip()
        return None

    SAMPLE_DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, SRC_COL]

        if not is_problematic(raw):
            results.append(str(raw).strip())
            copied_clean += 1
        else:
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in SAMPLE_DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid, df)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df['std_sample_description'] = results

    filled = df['std_sample_description'].notna().sum()
    print(f"std_sample_description: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def _text_cleanup(df, src_col, std_col, label):
    """
    Shared helper for simple text cleanup/recovery variables.
    Copies clean entries, recovers DUPLICATEs, sets rest to NaN.
    """
    DUP_OVERRIDES = {
        (528, 'DUPLICATE: Self-employment and well-bei'): 527,
        (726, 'VENTURE FINANCING AND SPECIAL ISSUES'): 725,
        (760, 'Estimating the valuation of new venture '): 759,
    }

    def is_problematic(x):
        if pd.isna(x):
            return True
        s = str(x).strip()
        if len(s) == 0:
            return True
        s_lower = s.lower()
        if s_lower.startswith('duplicate'):
            return True
        if s_lower.startswith('see paper'):
            return True
        if s_lower.startswith('n/a'):
            return True
        if s_lower.startswith('non-research'):
            return True
        if s_lower in ('retracted',):
            return True
        if any(p in s_lower for p in ['ocr failed', 'ocr needed', 'garbled',
                                       'unable to extract', 'could not be extracted',
                                       'file not found']):
            return True
        return False

    def extract_orig_pid(row):
        for field in [src_col, 'title', 'abstract']:
            text = str(row[field]) if pd.notna(row[field]) else ''
            m = re.search(r'paper\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'(?:paper_id|id)\s+(\d+)', text, re.I)
            if m:
                return int(m.group(1))
            m = re.search(r'same\s+paper\s+as\s+(?:id\s+)?(\d+)', text, re.I)
            if m:
                return int(m.group(1))
        return None

    def get_orig_value(orig_pid):
        orig_rows = df[df['paper_id'] == orig_pid]
        for _, o in orig_rows.iterrows():
            val = str(o[src_col]) if pd.notna(o[src_col]) else ''
            if len(val) > 20 and not is_problematic(o[src_col]):
                return val.strip()
        return None

    results = []
    copied_clean = 0
    recovered = 0
    set_empty = 0

    for idx in df.index:
        raw = df.at[idx, src_col]

        if not is_problematic(raw):
            results.append(str(raw).strip())
            copied_clean += 1
        else:
            is_ref = False
            if pd.notna(raw):
                s_lower = str(raw).lower().strip()
                is_ref = s_lower.startswith('duplicate') or s_lower.startswith('see paper')
            if not is_ref:
                title = str(df.at[idx, 'title']) if pd.notna(df.at[idx, 'title']) else ''
                is_ref = 'duplicate' in title.lower()[:20]

            if is_ref:
                pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
                title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''

                orig_pid = None
                for (oid, tstart), opid in DUP_OVERRIDES.items():
                    if pid == oid and title.startswith(tstart):
                        orig_pid = opid
                        break

                if orig_pid is None:
                    orig_pid = extract_orig_pid(df.iloc[idx])

                if orig_pid is not None:
                    orig_val = get_orig_value(orig_pid)
                    if orig_val:
                        results.append(orig_val)
                        recovered += 1
                        continue

            results.append(None)
            set_empty += 1

    df[std_col] = results

    filled = df[std_col].notna().sum()
    print(f"{label}: {filled}/{len(df)} papers ({filled/len(df)*100:.1f}%)")
    print(f"  Copied as-is: {copied_clean}")
    print(f"  Recovered from originals: {recovered}")
    print(f"  Set empty (unrecoverable): {set_empty}")

    return df


def std_iv(df):
    """
    Variable: std_iv
    Source column(s): independent_variables
    Date finalized: 2026-03-10
    Decision rationale: Cleanup/recovery of AI-extracted independent variables.
    """
    print("Standardizing independent_variables...")
    return _text_cleanup(df, 'independent_variables', 'std_iv', 'std_iv')


def std_dv(df):
    """
    Variable: std_dv
    Source column(s): dependent_variables
    Date finalized: 2026-03-10
    Decision rationale: Cleanup/recovery of AI-extracted dependent variables.
    """
    print("Standardizing dependent_variables...")
    return _text_cleanup(df, 'dependent_variables', 'std_dv', 'std_dv')


def std_mediators(df):
    """
    Variable: std_mediators
    Source column(s): mediators
    Date finalized: 2026-03-10
    Decision rationale: Cleanup/recovery of AI-extracted mediating variables.
    """
    print("Standardizing mediators...")
    return _text_cleanup(df, 'mediators', 'std_mediators', 'std_mediators')


def std_moderators(df):
    """
    Variable: std_moderators
    Source column(s): moderators
    Date finalized: 2026-03-10
    Decision rationale: Cleanup/recovery of AI-extracted moderating variables.
    """
    print("Standardizing moderators...")
    return _text_cleanup(df, 'moderators', 'std_moderators', 'std_moderators')


def std_controls(df):
    """
    Variable: std_controls
    Source column(s): control_variables
    Date finalized: 2026-03-10
    Decision rationale: Cleanup/recovery of AI-extracted control variables.
    """
    print("Standardizing control_variables...")
    return _text_cleanup(df, 'control_variables', 'std_controls', 'std_controls')


def std_paper_type(df):
    """
    Variables: std_paper_type
    Source column(s): paper_type
    Date finalized: 2026-03-10

    Decision rationale:
      - 8 primary categories chosen to be mutually exclusive and substantively meaningful
      - std_paper_type_detail was DROPPED in favor of separate std_method_design/std_method_technique variables
      - Meta-Analysis placed under Empirical-Quantitative (it IS quantitative empirical work)
      - QCA placed under Empirical-Quantitative (set-theoretic, systematic, not interpretive)
      - Formal Model separated from Conceptual (methodologically distinct: math/simulation vs prose theory)
      - Teaching Cases placed under Editorial (not empirical research)
      - Two-pass approach: Pass 1 rule-based (97%), Pass 2 hardcoded overrides for ambiguous papers

    std_paper_type categories (8):
      1. Empirical-Quantitative  - surveys, archival, experiments, meta-analyses, scale dev, QCA, etc.
      2. Empirical-Qualitative   - case studies, grounded theory, ethnography, process studies, etc.
      3. Empirical-Mixed         - explicitly mixed-methods designs
      4. Conceptual              - theory building, frameworks, propositions, typologies
      5. Review                  - literature reviews, systematic reviews, bibliometrics
      6. Editorial               - editorials, commentaries, SI intros, practitioner pieces, teaching cases
      7. Formal Model            - mathematical/analytical/computational models (no empirical testing)
      8. Other                   - duplicates, OCR failures, retractions, non-research admin

    std_paper_type_detail sub-types (populated when raw text provides enough info):
      Empirical-Quantitative: Survey, Archival/Secondary, Experimental, Longitudinal, Scale Development,
                              Meta-Analysis, QCA, Simulation, Descriptive, Network Analysis,
                              Content Analysis, Neuroscience, Replication, Delphi, Bibliometric
      Empirical-Qualitative:  Case Study, Grounded Theory, Ethnography, Process Study,
                              Historical/Comparative, Content Analysis, Longitudinal Qualitative
      Empirical-Mixed:        QCA (if mixed context), or blank
      Conceptual:             Framework, Model Development, Propositions, Typology/Taxonomy
      Review:                 Systematic Review, Integrative Review, Bibliometric, Narrative Review
      Editorial:              Commentary, SI Introduction, Executive Forum, Practitioner,
                              Teaching Case, Editorial, Editorial-Conceptual, Editorial-Review
      Formal Model:           Mathematical, Analytical, Simulation/Computational
      Other:                  Duplicate, OCR/Extraction Failed, Retracted/Corrected, Non-Research, Missing
    """

    # ── PASS 2: Hardcoded overrides for 105 ambiguous papers ──
    # These were classified by reading title + method + abstract for each paper.
    # Keys are paper_id (int), values are (std_paper_type, std_paper_type_detail).
    PASS2_OVERRIDES = {
        # Teaching Cases → Editorial
        1349: ('Editorial', 'Teaching Case'), 1350: ('Editorial', 'Teaching Case'),
        1366: ('Editorial', 'Teaching Case'), 1368: ('Editorial', 'Teaching Case'),
        1371: ('Editorial', 'Teaching Case'), 1385: ('Editorial', 'Teaching Case'),
        1387: ('Editorial', 'Teaching Case'), 1388: ('Editorial', 'Teaching Case'),
        1391: ('Editorial', 'Teaching Case'), 1402: ('Editorial', 'Teaching Case'),
        1410: ('Editorial', 'Teaching Case'), 1411: ('Editorial', 'Teaching Case'),
        1412: ('Editorial', 'Teaching Case'), 1413: ('Editorial', 'Teaching Case'),
        1414: ('Editorial', 'Teaching Case'), 1416: ('Editorial', 'Teaching Case'),
        1417: ('Editorial', 'Teaching Case'), 1421: ('Editorial', 'Teaching Case'),
        1424: ('Editorial', 'Teaching Case'), 1466: ('Editorial', 'Teaching Case'),
        1471: ('Editorial', 'Teaching Case'), 1489: ('Editorial', 'Teaching Case'),
        1490: ('Editorial', 'Teaching Case'), 1534: ('Editorial', 'Teaching Case'),
        1562: ('Editorial', 'Teaching Case'), 1568: ('Editorial', 'Teaching Case'),
        1569: ('Editorial', 'Teaching Case'), 1617: ('Editorial', 'Teaching Case'),
        1647: ('Editorial', 'Teaching Case'), 1648: ('Editorial', 'Teaching Case'),
        1664: ('Editorial', 'Teaching Case'), 1665: ('Editorial', 'Teaching Case'),
        1679: ('Editorial', 'Teaching Case'), 1692: ('Editorial', 'Teaching Case'),
        1717: ('Editorial', 'Teaching Case'), 1769: ('Editorial', 'Teaching Case'),
        1770: ('Editorial', 'Teaching Case'), 1771: ('Editorial', 'Teaching Case'),
        1772: ('Editorial', 'Teaching Case'), 1773: ('Editorial', 'Teaching Case'),
        1774: ('Editorial', 'Teaching Case'), 1780: ('Editorial', 'Teaching Case'),
        1844: ('Editorial', 'Teaching Case'), 1845: ('Editorial', 'Teaching Case'),
        # Empirical-Qualitative Case Studies (theory-building research)
        1359: ('Empirical-Qualitative', 'Case Study'),
        1360: ('Empirical-Qualitative', 'Case Study'),
        1615: ('Empirical-Qualitative', 'Case Study'),   # Ethnographic with network analysis
        1616: ('Empirical-Qualitative', 'Case Study'),   # Multiple case - process study
        1782: ('Empirical-Qualitative', 'Case Study'),   # Ethnographic observation
        711:  ('Empirical-Qualitative', 'Case Study'),   # Engines of progress - multiple case
        712:  ('Empirical-Qualitative', 'Case Study'),
        713:  ('Empirical-Qualitative', 'Case Study'),
        714:  ('Empirical-Qualitative', 'Case Study'),
        # Generic "Journal Article" / "Research Article" / "Original Article"
        1514: ('Review', 'Narrative Review'),              # Cash Management - literature review
        1515: ('Empirical-Qualitative', 'Case Study'),    # Risk Management - case study analysis
        1517: ('Empirical-Quantitative', 'Survey'),        # Generational involvement - survey/regression
        1518: ('Empirical-Mixed', ''),                     # Enterprise and Inequality - mixed methods
        1564: ('Empirical-Quantitative', 'Longitudinal'),  # Human Capital - longitudinal regression
        1565: ('Empirical-Quantitative', ''),              # Knowledge Spillover - quantitative
        1566: ('Empirical-Quantitative', 'Survey'),        # Strategic Management - survey/chi-square
        1567: ('Conceptual', ''),                          # Biases/Misperceptions - conceptual model
        1599: ('Empirical-Qualitative', ''),               # Corporate Entrepreneurial Role - qualitative
        1600: ('Empirical-Quantitative', 'Survey'),        # Information Sources - quantitative survey
        1601: ('Conceptual', 'Model Development'),         # Munificence - theoretical model
        1602: ('Empirical-Qualitative', 'Case Study'),     # Relational Organization - case study
        1629: ('Empirical-Quantitative', 'Longitudinal'),  # Home-Peers Export - hazard rate panel
        1630: ('Empirical-Quantitative', ''),              # Networks early ventures
        1631: ('Empirical-Quantitative', 'Longitudinal'),  # Microfinance - multilevel panel
        1632: ('Conceptual', 'Framework'),                 # Governing by Managing Identity
        1633: ('Empirical-Quantitative', 'Survey'),        # Insurance/Pension Plans - questionnaire
        1719: ('Empirical-Quantitative', ''),              # EO Learning Orientation - regression
        1720: ('Empirical-Quantitative', 'Longitudinal'),  # Social Structure - longitudinal
        1721: ('Empirical-Quantitative', 'Longitudinal'),  # Family Diversity - longitudinal survey
        1722: ('Empirical-Quantitative', 'Longitudinal'),  # Male/Female businesses - ANOVA
        1723: ('Empirical-Qualitative', 'Content Analysis'),  # EO Rhetoric - content analysis
        1729: ('Empirical-Quantitative', 'Experimental'),  # Emotions/Opportunities - experimental
        1735: ('Empirical-Quantitative', 'Experimental'),  # Social Proof Angel - experiment
        1736: ('Empirical-Quantitative', ''),              # Collective Cognition - exploratory
        1737: ('Empirical-Quantitative', ''),              # Temporal Dimensions - empirical TMT
        1738: ('Empirical-Qualitative', ''),               # Latin American Economies - qualitative
        # Methodological papers (classified by actual content)
        969:  ('Empirical-Quantitative', ''),              # NCA - with empirical illustration
        1018: ('Conceptual', 'Framework'),                 # Content Analysis IPOs - framework
        1175: ('Empirical-Quantitative', 'Neuroscience'),  # fMRI brain imaging study
        1455: ('Conceptual', 'Framework'),                 # QCA methodology - review/framework
        1470: ('Empirical-Quantitative', 'Replication'),   # Subjective Evaluations - replication
        1538: ('Empirical-Qualitative', ''),               # Attributions coding - qualitative
        1587: ('Conceptual', 'Framework'),                 # Selecting Methodologies - framework
        1621: ('Conceptual', 'Framework'),                 # Field Research Coda - synthesis
        384:  ('Empirical-Quantitative', ''),              # Event magnitude regression - method demo
        408:  ('Empirical-Quantitative', 'QCA'),           # fsQCA - methodological with empirical
        1001: ('Conceptual', 'Framework'),                 # Beyond averages - perspective
        1690: ('Conceptual', 'Framework'),                 # Achieving Empirical Progress - proposal
        1760: ('Conceptual', 'Framework'),                 # O*Net primer - methodological guide
        # Remaining individual papers
        1742: ('Empirical-Quantitative', 'Descriptive'),   # Accounting/Marketing - chi-square
        1427: ('Empirical-Quantitative', ''),              # GEM NES assessment - CFA
        1439: ('Conceptual', ''),                          # Educated Entrepreneurs essay
        1440: ('Conceptual', ''),                          # Educated Entrepreneurs reprint
        1477: ('Editorial', 'Practitioner'),               # Using Statistics - practical/applied
        1488: ('Empirical-Quantitative', 'Experimental'),  # Family Firm Brands - experimental
        1510: ('Empirical-Quantitative', 'Longitudinal'),  # Entrepreneurship Research - regression
        1516: ('Formal Model', 'Simulation/Computational'),  # Monte Carlo simulation
        1570: ('Empirical-Quantitative', ''),              # Dissertation Abstract - field study
        1581: ('Empirical-Quantitative', 'Replication'),   # Replicating Davidsson & Honig
        1656: ('Empirical-Quantitative', 'Scale Development'),  # Entrepreneurial Intent
        971:  ('Other', 'OCR/Extraction Failed'),          # OCR needed
    }

    def _classify_pass1(raw):
        """
        Pass 1: Rule-based classification.
        Returns (std_paper_type, std_paper_type_detail) or (None, None) if ambiguous.
        """
        if pd.isna(raw) or str(raw).strip() == '':
            return ('Other', 'Missing')

        s = str(raw).strip()
        low = s.lower()

        # ── OTHER: Duplicates, OCR failures, retractions, non-research admin ──
        if any(k in low for k in ['duplicate', 'ocr fail', 'ocr_fail', 'file not found',
                                   'not extracted', 'garbled', 'retract', 'corrigendum',
                                   'erratum', 'table of contents', 'journal index',
                                   'editorial board', 'call for papers']):
            if 'duplicate' in low:
                return ('Other', 'Duplicate')
            elif any(k in low for k in ['ocr', 'file not found', 'not extracted', 'garbled']):
                return ('Other', 'OCR/Extraction Failed')
            elif any(k in low for k in ['retract', 'corrigendum', 'erratum']):
                return ('Other', 'Retracted/Corrected')
            else:
                return ('Other', 'Non-Research')

        if low.startswith('non-research') or low.startswith('non_research'):
            return ('Other', 'Non-Research')

        # ── EDITORIAL ──
        editorial_keywords = ['editorial', 'commentary', 'executive forum', 'practitioner',
                              'special issue intro', 'discussant', 'moderator comment',
                              'call for paper', 'reflective', 'opinion', 'tribute',
                              'research pioneers', 'biographical', 'observation',
                              'administrative']
        if 'teaching case' in low or 'instructor' in low:
            return ('Editorial', 'Teaching Case')
        if any(k in low for k in editorial_keywords):
            if any(k in low for k in ['commentary', 'discussant', 'moderator', 'observation',
                                       'opinion', 'reflective', 'response']):
                return ('Editorial', 'Commentary')
            elif 'special issue' in low or ('introduction' in low and 'editorial' in low):
                return ('Editorial', 'SI Introduction')
            elif 'executive forum' in low:
                return ('Editorial', 'Executive Forum')
            elif 'practitioner' in low:
                return ('Editorial', 'Practitioner')
            elif 'editorial' in low and ('concept' in low or 'theor' in low or 'framework' in low):
                return ('Editorial', 'Editorial-Conceptual')
            elif 'editorial' in low and ('review' in low or 'method' in low):
                return ('Editorial', 'Editorial-Review')
            else:
                return ('Editorial', 'Editorial')

        # ── FORMAL MODEL ──
        formal_keywords = ['formal model', 'mathematical', 'analytical model', 'analytical/model',
                           'analytical/math', 'analytical/theo', 'theoretical/formal',
                           'theoretical/math', 'theoretical/analytical', 'computational',
                           'conceptual/analytical', 'conceptual/formal', 'analytical model',
                           'theory – analytical', 'theoretical – analytical']
        if any(k in low for k in formal_keywords) and 'empiric' not in low:
            if 'simulation' in low or 'computational' in low:
                return ('Formal Model', 'Simulation/Computational')
            elif 'mathematical' in low:
                return ('Formal Model', 'Mathematical')
            else:
                return ('Formal Model', 'Analytical')

        # ── REVIEW ──
        review_keywords = ['literature review', 'systematic review', 'integrative review',
                           'bibliometric', 'review/conceptual', 'conceptual/review',
                           'review article', 'review paper', 'literature synthesis',
                           'field analysis', 'review/method', 'review/practitioner',
                           'review/bibliometric', 'citation analysis']
        if any(k in low for k in review_keywords):
            if 'systematic' in low:
                return ('Review', 'Systematic Review')
            elif 'integrative' in low:
                return ('Review', 'Integrative Review')
            elif 'bibliometric' in low or 'citation analysis' in low:
                return ('Review', 'Bibliometric')
            else:
                return ('Review', 'Narrative Review')
        if re.match(r'^review$', low):
            return ('Review', 'Narrative Review')

        # ── EMPIRICAL-MIXED ──
        if ('mixed' in low and ('empiric' in low or 'method' in low)) or \
           low in ['mixed-methods', 'mixed methods']:
            if 'qca' in low:
                return ('Empirical-Quantitative', 'QCA')  # QCA → Quant per decision
            return ('Empirical-Mixed', '')

        # ── EMPIRICAL-QUALITATIVE ──
        qual_keywords = ['qualitat', 'case study', 'case stud', 'ethnograph', 'grounded theory',
                         'process study', 'historical', 'comparative case']
        if any(k in low for k in qual_keywords) and ('empiric' in low or 'qualitat' in low):
            if 'qca' in low or 'fsqca' in low:
                return ('Empirical-Quantitative', 'QCA')
            if 'ethnograph' in low:
                return ('Empirical-Qualitative', 'Ethnography')
            elif 'grounded' in low:
                return ('Empirical-Qualitative', 'Grounded Theory')
            elif 'process study' in low:
                return ('Empirical-Qualitative', 'Process Study')
            elif 'historical' in low or 'comparative' in low:
                return ('Empirical-Qualitative', 'Historical/Comparative')
            elif 'case study' in low or 'case stud' in low:
                return ('Empirical-Qualitative', 'Case Study')
            elif 'longitudinal' in low:
                return ('Empirical-Qualitative', 'Longitudinal Qualitative')
            else:
                return ('Empirical-Qualitative', '')

        # ── EMPIRICAL-QUANTITATIVE ──
        if 'empiric' in low:
            if 'meta' in low and 'analy' in low:
                return ('Empirical-Quantitative', 'Meta-Analysis')
            elif 'experiment' in low or 'rct' in low:
                return ('Empirical-Quantitative', 'Experimental')
            elif 'survey' in low:
                return ('Empirical-Quantitative', 'Survey')
            elif 'archival' in low or 'secondary data' in low:
                return ('Empirical-Quantitative', 'Archival/Secondary')
            elif 'scale develop' in low or 'scale valid' in low:
                return ('Empirical-Quantitative', 'Scale Development')
            elif 'longitudinal' in low or 'panel' in low:
                return ('Empirical-Quantitative', 'Longitudinal')
            elif 'simulation' in low:
                return ('Empirical-Quantitative', 'Simulation')
            elif 'bibliometric' in low:
                return ('Empirical-Quantitative', 'Bibliometric')
            elif 'delphi' in low:
                return ('Empirical-Quantitative', 'Delphi')
            elif 'neuroscience' in low or 'fmri' in low:
                return ('Empirical-Quantitative', 'Neuroscience')
            elif 'descriptive' in low:
                return ('Empirical-Quantitative', 'Descriptive')
            elif 'network analysis' in low:
                return ('Empirical-Quantitative', 'Network Analysis')
            elif 'content analysis' in low:
                return ('Empirical-Quantitative', 'Content Analysis')
            elif 'replication' in low:
                return ('Empirical-Quantitative', 'Replication')
            elif 'qca' in low or 'fsqca' in low:
                return ('Empirical-Quantitative', 'QCA')
            else:
                return ('Empirical-Quantitative', '')

        # Standalone meta-analysis
        if 'meta' in low and 'analy' in low:
            return ('Empirical-Quantitative', 'Meta-Analysis')

        # ── CONCEPTUAL ──
        concept_keywords = ['concept', 'theor', 'framework', 'proposition', 'typolog', 'taxonom']
        if any(k in low for k in concept_keywords):
            if 'framework' in low:
                return ('Conceptual', 'Framework')
            elif 'model' in low:
                return ('Conceptual', 'Model Development')
            elif 'proposition' in low:
                return ('Conceptual', 'Propositions')
            elif 'typolog' in low or 'taxonom' in low:
                return ('Conceptual', 'Typology/Taxonomy')
            else:
                return ('Conceptual', '')

        # ── AMBIGUOUS → return None for Pass 2 ──
        return (None, None)

    # ── Apply Pass 1 ──
    results = df['paper_type'].apply(_classify_pass1)
    df['std_paper_type'] = results.apply(lambda x: x[0])

    # ── Apply Pass 2 overrides ──
    # Note: some paper_ids exist across multiple journals with different content.
    # For pid=714, the override (Case Study) applies only to the JBV paper
    # "Engines of progress V", NOT the ETP paper "The Chicken and the Computer".
    JOURNAL_SPECIFIC_OVERRIDES = {
        714: 'Journal of Business Venturing',  # Only apply to JBV row
    }
    for pid, (stype, sdetail) in PASS2_OVERRIDES.items():
        if pid in JOURNAL_SPECIFIC_OVERRIDES:
            jfilter = JOURNAL_SPECIFIC_OVERRIDES[pid]
            mask = (df['paper_id'] == pid) & (df['journal'].str.contains(jfilter, case=False, na=False))
        else:
            mask = df['paper_id'] == pid
        if mask.any():
            df.loc[mask, 'std_paper_type'] = stype

    # ── Validation: no nulls should remain ──
    nulls = df['std_paper_type'].isna().sum()
    if nulls > 0:
        print(f"WARNING: {nulls} papers still unclassified after Pass 1 + Pass 2!")
        print(df[df['std_paper_type'].isna()][['paper_id', 'paper_type']].to_string())
    else:
        print(f"std_paper_type: all {len(df)} papers classified successfully.")

    print("\nstd_paper_type distribution:")
    print(df['std_paper_type'].value_counts().to_string())

    return df


def std_method_design_and_technique(df):
    """
    Classify empirical academic papers into std_method_design and std_method_technique categories.

    Variables: std_method_design, std_method_technique
    Source column(s): std_paper_type, method, data_source, sample, title
    Date finalized: 2026-03-10

    Decision rationale:
      - Two-pass approach: comprehensive rule-based matching + manual overrides (35 papers)
      - Multi-valued outputs: both design and technique are semicolon-separated lists
      - Only applies to empirical papers (Empirical-Quantitative, Empirical-Qualitative, Empirical-Mixed)
      - Non-empirical papers receive empty strings
      - Uses combined text from method + data_source + sample + title (lowercased) for matching
      - Method design captures research design/methodology (e.g., Survey, Experiment, Case Study)
      - Method technique captures statistical/analytical technique (e.g., OLS, SEM, Qualitative Coding)
      - Archival = analyzed pre-existing records/databases without primary data collection
      - Cross-Sectional is NOT treated as a residual category; must be explicitly identified
      - Meta-Analysis placed under Empirical-Quantitative (for std_paper_type)
      - QCA placed under Empirical-Quantitative (for std_paper_type); own category for design/technique

    std_method_design categories (21):
      Survey, Experiment-Lab, Experiment-Field, Conjoint/Vignette, Quasi/Natural Experiment,
      Panel/Longitudinal, Cross-Sectional, Archival, Case Study, Interview/Fieldwork,
      Grounded Theory, Meta-Analysis, Content/Text Analysis, QCA, Event Study,
      Simulation, Scale Development, Diary/ESM, Bibliometric, Delphi, Action Research

    std_method_technique categories (24):
      OLS/Linear Regression, Logistic/Limited DV, SEM/Path Analysis, HLM/Multilevel,
      Panel/Fixed Effects, Survival/Event History, ANOVA/t-test, Factor Analysis,
      IV/Endogeneity Correction, DiD/Matching, QCA, Meta-Analytic Technique,
      Conjoint Analysis, Event Study Technique, Qualitative Coding,
      Descriptive/Exploratory, Network Analysis, Cluster/Latent Class,
      Machine Learning/NLP, Bayesian, Correlation, Simulation Technique,
      Decomposition, Time Series
    """

    # ── DESIGN RULES (comprehensive patterns from Pass 1 + Pass 2) ──
    DESIGN_RULES = {
        'Survey': r'\bsurvey|\bquestionnaire|\bmail.?out|\blikert|\bself.report|\bresponse rate|\bmail survey|\btelephone survey|\bonline survey|\bweb.?based survey|\bprimary data|primary.*collection|structured\s+interview|\bself.?administr',
        'Experiment-Lab': r'\blab\w*\s+experiment|\blaboratory|\bstudent.?subject|\bundergraduate.?\bparticipant|\blab.?based|\blaboratory.?setting|\btrust game|\bbehavioral game|\bbehavioral experiment|\bcomputer.?based.*experiment|\beye track\w+ experiment',
        'Experiment-Field': r'\bfield experiment|\brct|\brandomized control|\brandomised control|\bfield trial|\brandomized.?experiment|\brandom\w*\s+assign\w*.*(?:treat|condition|group)|random\w*\s+control\w*\s+(?:trial|experiment)\b|\bpreregistered.*randomized|\brandomized.*trial|\baudit study|\bmail experiment',
        'Conjoint/Vignette': r'\bconjoint|\bvignette|\bpolicy.?captur|\bdiscrete choice|\bbetween.subject|\bwithin.subject|\bfactorial\s+(design|experiment)|\bscenario.?based|\b2x2|\b2\s*[×x]\s*2|\b3x2|\bgoldberg.?type|\bexperimental\s+(?:design|stud|manipul)|\bexperiment\w*\s+(?:with|where|using)|\bcontrolled\s+experiment',
        'Quasi/Natural Experiment': r'\bquasi.?experiment|\bnatural experiment|\bdifference.?in.?difference|\bdiff.?in.?diff|\bregression discontinuity|\bexogenous\s+(?:shock|variation|change|event)\b|\binstrumental variable|\bplausibly exogenous|\bdiscontinuity design',
        'Panel/Longitudinal': r'\bpanel|\blongitudinal|\btime.?series|\bmulti.?year|\bmulti.?wave|\bfollow.?up|\bover\s+time|\byear\s+period|\btime.?lag|\blagged|\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\b|\brepeat\w*\s+measure|\bwave\s*[123]\b|\b\d+\s*years?\s+(?:of\s+)?data|\bannual\s+data|\bmultiple\s+years|\bcohort\s+(stud|analy|design)',
        'Cross-Sectional': r'\bcross.?sectional|\bsnapshot|\bone.?time|\bsingle.?point|\bat one point in time',
        'Archival': (
            r'\barchival|\bsecondary data|\bsecondary\s+source|\bdatabase|\bpublic\w*\s+available|\badministrative\s+(?:data|record|register)'
            r'|\bregister\s+data|\bplatform\s+data|\bweb.?scrap'
            r'|\bcrunchbase|\bcompustat|\borbis|\bgem\b.*data|\bcensus'
            r'|\bgovernment\s+(?:data|statistics|records)\b|\bfcc\s+data|\btax\s+(?:data|record)\b|\bregistry'
            r'|\bcorporate\s+(?:data|record|report)\b|\bfinancial\s+(?:data|record|report|account|statement)\b'
            r'|\bpatent\s+data|\bipo\s+data|\bsec\s+fil|\bstock\s+market|\bmarket\s+data'
            r'|\bemployment\s+data|\blabor\s+market|\bdun\s+[&a]\b|\brobert\s+morris|\bkauffman'
            r'|\bglobal\s+entrepreneurship\s+monitor|\bworld\s+bank|\boecd|\bglobal\s+competitiveness'
            r'|\beurobarometer|\bflash\s+euro|\bpsed|\bpopulation\s+(?:data|register)\b'
            r'|\bvc\s+(?:data|investment|deal|fund)\b|\bventure\s+capital\s+data'
            r'|\bcrowdfund\w+\s+(?:platform|data)\b|\bkickstarter|\bindiegogo'
            r'|\bfortune\s+(?:500|1000|global)\b|\bindustry\s+data'
            r'|\bbank\s+(?:of\s+italy|record|internal|data)\b|\bbalance sheet|\bannual report'
            r'|\bsb(?:dc|i)\b|\binc\.?\s+500|\bs&p\s+500|\bfranchise\s+(?:data|director|system)\b'
            r'|\bfirm.level data|\bhand.collected|\bproprietorship\s+data|\balumni\s+records'
            r'|\bhofstede|\bheritage\s+foundation|\bbelgian\s+national|\bslovenian|\bpolish\s+central'
            r'|\bbarclays|\bb\s+lab|\bashoka\s+fellow|\bdragons.*den|\bshark.*tank'
            r'|\bloan\s+data|\bcredit\s+(?:record|data)\b|\bico\s+(?:data|white\s+paper)\b'
            r'|\blinkedin\s+profile|\bstock\s+exchange|\bchinese\s+industrial'
            r'|\bsba|\bpims|\bofficial\s+.*statistics|\bmicro\s*data'
            r'|\b(?:eu|european)\s+(?:data|statistics|silc)\b'
            r'|\btv\s+show\s+(?:data|record)\b|\bpitch\s+competition\s+data'
        ),
        'Case Study': r'\bcase\s+stud|\bsingle\s+case|\bmultiple\s+case|\bin.?depth\s+case|\bmulti.?case|\bcase\s+analysis|\bcase\s+method|\bcase\s+research|\bcase\s+comparison|\bmatched\s+pair|\bcross.?case|\bteaching case',
        'Interview/Fieldwork': r'\binterview|\bfocus group|\bethnograph|\bparticipant observ|\bfield.?work|\bfield research|\bfield stud|\bautoethnograph|\bobservation\w*\s+(of|at|in)\b|\binformant|\bverbal protocol|\bthink.?aloud|\bprotocol analysis|\brepertory grid|\bsemi.?structured|\bin.?depth\s+(?:interview|conversation)\b',
        'Grounded Theory': r'\bgrounded theory|\bgioia|\bstrauss\b.*\bcorbin|\bglaser\b.*\bstrauss|\bopen coding|\baxial coding|\bselective coding|\btheoretical sampl',
        'Meta-Analysis': r'\bmeta.?analy|\bmeta.?regress|\bmeta.?review|\bmeta.?synthe|\bhoma|\bhunter.?schmidt|\beffect size.*(?:pool|aggregat|synthes)\b|\bmasem',
        'Content/Text Analysis': r'\bcontent analy|\btext analy|\bnlp|\bliwc|\btopic model|\bnarrative analy|\bdiscourse analy|\bcoding of|\bhand.?cod|\btext\s+mining|\bsentiment|\bcomputer.?aided text|\bcata|\bcritical discourse|\bmetaphor analysis',
        'QCA': r'\bfsqca|\bqca|\bqualitative comparative analysis|\bcrisp.?set|\bfuzzy.?set',
        'Simulation': r'\bsimulat\w+(?:.{0,20})(?:study|model|based|technique|analysis)\b|\bmonte carlo|\bagent.based|\bcomputational model',
        'Scale Development': r'\bscale develop|\bscale valid|\bpsychometric|\binstrument develop|\bitem generat|\bexploratory factor.*confirmatory factor|\bmulti.?study.*valid',
        'Diary/ESM': r'\bdiary|\bexperience sampl|\besm|\bday.level|\bdaily (?:surv|diary|report|measure)\b',
        'Event Study': r'\bevent stud|\bevent.?history|\bcumulative abnormal return',
        'Bibliometric': r'\bbibliometr|\bcitation analy',
        'Delphi': r'\bdelphi',
        'Action Research': r'\baction research|\bcommunity.?based participatory|\bco.?creation.*research',
    }

    # ── TECHNIQUE RULES ──
    TECHNIQUE_RULES = {
        'OLS/Linear Regression': r'\bols|\blinear regress|\bmultiple regress|\bregression analy|\bhierarchical regress|\bstepwise regress|\bmoderated regress|\bregression with\b|\bregression model|\bregression examining|\bregression of\b|\bmultivariate regress|\bregression;\b|\bregression\s*$|\bwith regression|\becono?metric|\bmodera\w+\s+(analy|test|effect|regress)|\bcurvilinear\s+regress|\binteraction\s+(?:term|effect|model)|\bquadratic\s+(?:term|effect|regress)|\blongitudinal\s+regress|\bpanel\s+regress|\bcross.?national\s+(?:regress|analy)|\bcross.?state\s+analy',
        'Logistic/Limited DV': r'\blogist|\blogit|\bprobit|\btobit|\bnegative binomial|\bpoisson|\bzero.inflat|\bcount model|\bbinary\s+(choice|model|outcome|regress)\b|\bfractional logit|\bmultinomial',
        'SEM/Path Analysis': r'\bsem|\bstructural equation|\bpath analy|\bpath model|\blisrel|\bamos|\blavaan|\bpls|\bpartial least square|\bmediat\w+\s+(analy|test|effect|model)|\bsobel\s+test|\bindirect effect|\bmediation',
        'HLM/Multilevel': r'\bhlm|\bhierarchical linear model|\bmultilevel|\bmulti.level|\bcross.level|\bnested\s+model|\bmulti.?level\s+analy|\bmixed.?effect|\brandom\s+intercept|\brandom\s+slope',
        'Panel/Fixed Effects': r'\bfixed.?effect|\brandom.?effect|\bhausman|\bgmm|\bgeneralized method of moment|\bfeasible generalized|\bfgls|\barellano.bond|\bsystem gmm|\bpanel\s+(data\s+)?analy|\bpanel\s+regress|\bfirm.?year\s+fixed|\byear\s+fixed|\bindustry\s+fixed',
        'Survival/Event History': r'\bhazard|\bsurvival analy|\bcox|\bduration model|\bevent history analy|\bkaplan.meier|\bcompeting risk|\baccelerated failure',
        'ANOVA/t-test': r'\banova|\bmanova|\bancova|\bt.test|\bt test|\bmean (compar|differ)|\bgroup (compar|differ)|\bfactorial\s+analy|\bmann.?whitney|\bwilcoxon|\bkruskal|\banalysis of variance|\banalysis of covariance',
        'Factor Analysis': r'\bfactor analy|\bcfa|\befa|\bpca|\bprincipal component|\bexploratory factor|\bconfirmatory factor|\bvarimax|\bpromax',
        'IV/Endogeneity Correction': r'\binstrumental variable|\b2sls|\btwo.stage\s+least|\bheckman|\bendogen\w+\s+(correct|control|test|address|concern)\b|\bselection (bias|correct|model)\b|\btreatment effect|\bcontrol function',
        'DiD/Matching': r'\bdifference.?in.?difference|\bdiff.?in.?diff|\bpropensity score|\bmatching\s+(method|estimat|approach|techniq|analys)\b|\bcoarsened exact|\bnearest neighbor|\bentropy balancing',
        'QCA': r'\bfsqca|\bqca|\bqualitative comparative analysis|\bcrisp.?set|\bfuzzy.?set|\bnecessary condition|\bsufficient condition',
        'Meta-Analytic Technique': r'\bmeta.?analy|\bmeta.?regress|\bhoma|\bmara|\bhunter.?schmidt|\bhedges\b.*\bolkin|\beffect size\b.*\b(pool|aggregat|synthes)\b',
        'Conjoint Analysis': r'\bconjoint\b.*\b(analy|design)\b|\bpart.?worth|\buttility\s+score',
        'Event Study Technique': r'\bevent stud|\bcumulative abnormal return|\bcar\b.*\b(window|event)\b',
        'Qualitative Coding': r'\bgrounded theory|\bgioia|\bthematic (analy|coding)|\btemplate analy|\bopen coding|\baxial coding|\bnvivo|\batlas\.ti|\bcoding (process|scheme|framework)|\bfirst.order\b.*\bsecond.order|\binductive (analy|coding|approach)|\bqualitative\s+(?:inductive|analysis|methodology|coding)|\babductive',
        'Descriptive/Exploratory': r'\bdescriptive|\bchi.?square|\bcross.?tabul|\bfrequency (analy|distribut|count)|\bexploratory (analy|stud|research|quant)|\bfisher.*exact|\bcomparative\s+analy|\bratio\s+analy|\bcohort\s+analy|\bfinancial\s+analy|\bperformance\s+analy',
        'Network Analysis': r'\bnetwork analy|\bsocial network|\bqap|\bergm|\bbrokerage\b.*\bnetwork|\bcentrality',
        'Cluster/Latent Class': r'\bcluster analy|\blatent class|\blatent profile|\blca|\blpa|\btaxonomic|\btypolog\w+\s+(analy|develop|identif)\b|\bk.?means|\bdiscriminant\s+analy',
        'Machine Learning/NLP': r'\bmachine learn|\brandom forest|\bneural net|\bdeep learn|\bsvm|\bsupervised\s+classif|\btext mining|\btopic model|\blda|\bsentiment',
        'Bayesian': r'\bbayesian|\bbayes|\bmcmc|\bposterior',
        'Correlation': r'\bcorrelation\b.*\b(analy|matrix|table)|\bpearson|\bspearman|\bbivariate\s+correlat|\bcorrelation\s+(coefficient|analy)',
        'Simulation Technique': r'\bsimulat|\bmonte carlo|\bagent.based|\bcomputational model|\bbootstrap',
        'Decomposition': r'\bdecompos|\bshift.share|\bblinder.oaxaca|\boaxaca|\bcommonality analy',
        'Time Series': r'\btime.series|\bvector auto|\barima|\bcointegrat|\bgranger',
    }

    # ── MANUAL DESIGN OVERRIDES (35 papers that don't match any rule) ──
    # Keys: (paper_id, title_starts_with) → design value
    # These were classified by reading method + data_source + sample for each paper.
    MANUAL_DESIGN_OVERRIDES = {
        (109, 'Roads Leading'): 'Archival',
        (299, 'Adverse Selection'): 'Archival',
        (982, 'Entrepreneurial Orientation: The'): 'Archival',
        (1630, 'How Entrepreneurs Use'): 'Survey',
        (1736, 'Collective Cognition'): 'Survey',
        (1765, 'Gender, Entrepreneurial'): 'Survey',
        (1767, 'Family Business Survival'): 'Archival',
        (387, 'Do others think you'): 'Archival',
        (753, "Women's self-employment"): 'Archival',
        (731, 'Reaching out or going'): 'Survey',
        (52, 'Gender Differences in Peer'): 'Archival',
        (95, 'Do differences among'): 'Archival',
        (338, 'Comparing Alliance Network'): 'Archival',
        (427, 'Technology emergence'): 'Archival',
        (1223, 'Evaluating Franchise'): 'Archival',
        (211, 'Are entrepreneurs influenced'): 'Experiment-Lab',
        (520, 'Entrepreneurial cognition'): 'Experiment-Lab',
        (1122, 'The Differential Impact'): 'Simulation',
        (1280, 'A Technical Aid'): 'Simulation',
        (1409, 'A Systems Approach'): 'Simulation',
        (1709, 'Linking Corporate'): 'Simulation',
        (1401, 'Agency, Strategic'): 'Archival',
        (1532, 'Strategic Divestments'): 'Archival',
        (1759, 'Employer Legitimacy'): 'Archival',
        (1807, 'Entrepreneurial Entry'): 'Archival',
        (1822, 'Why Do Family Firms'): 'Archival',
        (1724, 'The Entrepreneurship Process'): 'Case Study',
        (1175, 'Advancing'): 'Experiment-Lab',
        (1130, 'What Do Entrepreneurs'): 'Interview/Fieldwork',
        (969, 'Necessary Conditions'): 'Archival',
        (714, 'The Chicken'): 'Interview/Fieldwork',
        (374, 'The project-management'): 'Case Study',
        (204, 'Historicizing'): 'Case Study',
        (637, 'Network-based research'): 'Archival',
        (1427, 'DUPLICATE'): 'Archival',
        # ── AI Intelligence Pass 2 (43 papers classified by reading metadata) ──
        (60, "Don't Pitch Like a Girl"): 'Archival',
        (111, 'Small Business Growth Characteristic'): 'Archival',
        (194, 'Skill Balance and Entrepreneurship'): 'Archival',
        (304, 'The Role of Agents in Private Entrep'): 'Archival',
        (308, 'Human Resources in Initial Public Off'): 'Archival',
        (314, 'Board of Directors Leadership and Str'): 'Archival',
        (430, 'Diversity in National Culture and Fin'): 'Archival',
        (947, 'Goal Programming for Decision Making'): 'Simulation',
        (1008, 'The Role of Political Values and Ide'): 'Archival; Content/Text Analysis',
        (1437, 'Organization Principles and Financia'): 'Survey',
        (1645, 'Family Firm Value in the Acquisition'): 'Archival',
        (1684, 'How Prior Corporate Venture Capital'): 'Archival',
        (1838, 'The Influence of Top Management Team'): 'Archival',
        (60, 'Entrepreneurship Capital and Its Impa'): 'Archival',
        (78, 'Factors that determine the reputation'): 'Archival',
        (215, 'New evidence in the pursuit of locat'): 'Archival',
        (345, 'Entrepreneurial Orientation and Inte'): 'Survey',
        (346, 'Investment Bankers and IPO Pricing'): 'Archival',
        (494, 'Initial coin offerings (ICOs) to fin'): 'Archival',
        (518, 'An institutional perspective on borr'): 'Archival',
        (550, "New insights into venture capitalist"): 'Survey',
        (566, 'Bank strategies toward firms in decl'): 'Archival',
        (652, 'Entrepreneurial exit intentions and'): 'Archival',
        (664, 'Improving new venture performance'): 'Archival',
        (703, 'Do networks of financial intermediar'): 'Archival',
        (738, 'The many faces of entrepreneurial fa'): 'Interview/Fieldwork; Survey',
        (792, 'Prediction of failure of a newly fou'): 'Archival',
        (943, 'Institutional logics, family firm go'): 'Archival',
        (988, 'The double-edged sword of purpose-dr'): 'Case Study',
        (1087, 'The dual nature of innovative activ'): 'Archival',
        (1088, 'Multinationality, product diversifi'): 'Archival',
        (1252, 'Testing Baumol: Institutional quali'): 'Archival',
        (1301, 'The anatomy of a corporate venturin'): 'Archival',
        (1356, 'Perceived progress variability and'): 'Diary/ESM',
        (1401, 'Broadening versus reinforcing inves'): 'Archival',
        (1404, 'Express yourself: Facial expression'): 'Content/Text Analysis',
        (1423, 'The informal venture capital market'): 'Archival',
        (1454, 'The pricing of a brand name product'): 'Archival',
        (1462, 'Timing is everything? Curvilinear e'): 'Archival',
        (1473, 'The aftermarket performance of smal'): 'Archival',
        (53, 'Does the Apple Always Fall Close to'): 'Archival',
        (346, 'Fire in the belly? Employee motives'): 'Archival',
        (388, 'Adaptations to knowledge templates'): 'Archival',
    }


    # ── MANUAL TECHNIQUE OVERRIDES (360 papers that don't match any technique rule) ──
    # Keys: (paper_id, title_starts_with) → technique value
    # These were classified by AI intelligence (reading method, data_source, sample, title,
    # key_findings, abstract, and other columns for each paper).
    MANUAL_TECHNIQUE_OVERRIDES = {
        (28, 'Local Context and Post-Crisis Social Ven'): 'Panel/Fixed Effects',
        (33, 'Venturing for Others, Subject to Role Ex'): 'Qualitative Coding',
        (34, 'No Credit for Success, Penalized for Fai'): 'Conjoint Analysis; Panel/Fixed Effects; Qualitative Coding',
        (48, 'Start-Up Capital and Chinese Entrepreneu'): 'Descriptive/Exploratory',
        (51, 'Agency and Governance in Strategic Entre'): 'OLS/Linear Regression',
        (61, 'How Strategic Entrepreneurship and the I'): 'Panel/Fixed Effects',
        (65, 'Signaling and initial public offerings: '): 'OLS/Linear Regression',
        (65, 'A Cognitive Approach to the Expected Val'): 'Conjoint Analysis',
        (66, 'Religion, social class, and entrepreneur'): 'Logistic/Limited DV',
        (79, 'An examination of the impact of initial '): 'OLS/Linear Regression; Panel/Fixed Effects',
        (80, 'The temporal nature of growth determinan'): 'Panel/Fixed Effects',
        (94, 'Investment dynamics and financial constr'): 'Panel/Fixed Effects',
        (96, 'Customer value propositions in declining'): 'Descriptive/Exploratory',
        (101, 'Biased Calibration: Exacerbating Instead'): 'Descriptive/Exploratory',
        (102, 'Self-efficacy and entrepreneurs\' adoptio'): 'OLS/Linear Regression',
        (104, 'Self-efficacy and entrepreneurs\' adoptio'): 'OLS/Linear Regression',
        (106, 'A quantitative content analysis of the c'): 'OLS/Linear Regression',
        (111, 'TECHNOLOGY-BASED FIRM CONFIGURATIONS'): 'OLS/Linear Regression',
        (114, ''): 'OLS/Linear Regression',
        (115, ''): 'OLS/Linear Regression',
        (116, 'SELF-EMPLOYMENT ENTRY ACROSS INDUSTRIES '): 'OLS/Linear Regression',
        (117, 'FINANCING SMALL BUSINESS: IMMIGRANTS'): 'OLS/Linear Regression',
        (118, ''): 'OLS/Linear Regression',
        (119, ''): 'OLS/Linear Regression',
        (120, ''): 'OLS/Linear Regression',
        (123, 'Financial optimism and entrepreneurial s'): 'Panel/Fixed Effects',
        (124, 'The Cost of Equity Capital for Small Bus'): 'Simulation Technique',
        (126, 'The Varying Effects of Family Relationsh'): 'Panel/Fixed Effects',
        (126, 'Doing good while making profits: A typol'): 'Descriptive/Exploratory',
        (127, 'Venture debt financing: Determinants of '): 'Conjoint Analysis',
        (130, 'Endogenous growth through knowledge spil'): 'Panel/Fixed Effects',
        (131, 'Using Founder Status, Age of Firm, and C'): 'OLS/Linear Regression',
        (135, 'Crowdfunding: Tapping the Right Crowd'): 'Descriptive/Exploratory',
        (136, 'Affordable loss: Behavioral economic asp'): 'Descriptive/Exploratory',
        (138, 'Are entrepreneurs penalized during job s'): 'Conjoint Analysis',
        (142, 'Amplifying angels: Evidence from the INV'): 'Conjoint Analysis; Panel/Fixed Effects',
        (144, 'How alliance formation shapes corporate '): 'Panel/Fixed Effects',
        (145, 'Trust, fast and slow: A comparison study'): 'Descriptive/Exploratory',
        (146, 'Regional influences on the prevalence of'): 'Panel/Fixed Effects',
        (147, 'Impact of the Type of Corporate Spin-Off'): 'Descriptive/Exploratory',
        (149, 'Open innovation, information, and entrep'): 'Descriptive/Exploratory',
        (162, 'The Rewards of Entrepreneurship: Explori'): 'OLS/Linear Regression; Panel/Fixed Effects',
        (165, 'An Analysis of the Work Roles of CEOs of'): 'Descriptive/Exploratory',
        (171, 'Profitable Small Business Strategies und'): 'OLS/Linear Regression',
        (175, 'Selection of Borrowing Partners in Joint'): 'Descriptive/Exploratory',
        (179, 'Control Structures Used in Family Busine'): 'Factor Analysis; OLS/Linear Regression',
        (196, 'Resources of the firm, Russian high-tech'): 'OLS/Linear Regression',
        (209, 'Entry and exit in disequilibrium'): 'Panel/Fixed Effects',
        (211, 'Are entrepreneurs influenced by risk att'): 'Conjoint Analysis',
        (211, 'Forecasting Errors of New Venture Surviv'): 'OLS/Linear Regression',
        (214, 'Differences between entrepreneurs and ma'): 'Descriptive/Exploratory',
        (218, 'Misfortunes or mistakes? Cultural sensem'): 'SEM/Path Analysis',
        (220, 'Bypassing the financial growth cycle: Ev'): 'Logistic/Limited DV',
        (222, 'Angel group members\' decision process an'): 'Descriptive/Exploratory',
        (229, 'Impact of Employee Stock Ownership Plans'): 'ANOVA/t-test',
        (235, 'Ethnic-immigrants in founding teams: Eff'): 'DiD/Matching',
        (237, 'How images and color in business plans i'): 'Conjoint Analysis',
        (246, 'No politics in funding pitches: An expec'): 'SEM/Path Analysis',
        (269, 'The Conflicting Cognitions of Corporate '): 'OLS/Linear Regression',
        (271, 'Firm dynamics and industrialization in t'): 'OLS/Linear Regression',
        (272, 'Small businesses and liquidity constrain'): 'OLS/Linear Regression',
        (283, 'The costs and benefits of public sector '): 'Logistic/Limited DV',
        (289, 'Entrepreneurs meet financiers: Evidence '): 'DiD/Matching; Panel/Fixed Effects',
        (297, 'The sandwich game: Founder-CEOs and fore'): 'Descriptive/Exploratory',
        (299, 'Adverse Selection and Capital Structure:'): 'Descriptive/Exploratory',
        (306, 'Strategic Issues Management in the Commu'): 'Descriptive/Exploratory',
        (307, 'Decision Theory: Its Value in the Small '): 'Descriptive/Exploratory',
        (315, 'Entrepreneurial Learning from Failure: A'): 'Qualitative Coding',
        (323, 'The Impact of Electric Rates on Small Bu'): 'Panel/Fixed Effects; Simulation Technique',
        (326, 'Much Ado About Nothing? The Surprising P'): 'Panel/Fixed Effects',
        (331, 'Understanding Gendered Variations in Bus'): 'Panel/Fixed Effects',
        (335, 'Predictors of Later-Generation Family Me'): 'Descriptive/Exploratory',
        (342, 'A Profile of New Venture Success and Fai'): 'Simulation Technique',
        (343, 'Measuring the Market Newness of New Vent'): 'Factor Analysis',
        (347, 'Bank Involvement with Export Trading Com'): 'Descriptive/Exploratory',
        (348, 'Relocation to Get Venture Capital: A Res'): 'IV/Endogeneity Correction; Panel/Fixed Effects',
        (349, 'Control Techniques and Upward Flow of In'): 'Descriptive/Exploratory',
        (351, 'The Role of Gender in Opportunity Identi'): 'Conjoint Analysis',
        (354, 'The accidental entrepreneur: The emergen'): 'Descriptive/Exploratory',
        (358, 'Venture capital financing and the growth'): 'Panel/Fixed Effects',
        (365, 'Effects of relational capital and commit'): 'OLS/Linear Regression',
        (368, 'Surviving the emotional rollercoaster ca'): 'Logistic/Limited DV',
        (375, 'Do innovative users generate more useful'): 'Descriptive/Exploratory',
        (385, 'Religion and Enterprise: An Introductory'): 'Descriptive/Exploratory',
        (385, 'Do policy makers take grants for granted'): 'Panel/Fixed Effects',
        (388, 'Criteria for corporate venturing: Import'): 'Conjoint Analysis',
        (388, 'Adaptations to knowledge templates in ba'): 'Event Study Technique',
        (397, 'Foreign vs. domestic listing: An entrepr'): 'OLS/Linear Regression',
        (426, 'Differing Perceptions of Small Business '): 'Panel/Fixed Effects',
        (427, 'Technology emergence through entrepreneu'): 'OLS/Linear Regression',
        (435, 'Venturing from emerging economies'): 'OLS/Linear Regression',
        (445, 'Gender, Structural Factors, and Credit T'): 'Descriptive/Exploratory',
        (470, 'Exploring start-up event sequences'): 'Descriptive/Exploratory',
        (483, 'Gender bias and the availability of busi'): 'Conjoint Analysis',
        (490, 'Complementary theoretical perspectives o'): 'OLS/Linear Regression',
        (495, 'How does entrepreneurial failure change '): 'Panel/Fixed Effects',
        (509, 'Venture capital and high technology entr'): 'Cluster/Latent Class',
        (520, 'Entrepreneurial cognition and the qualit'): 'Descriptive/Exploratory',
        (524, 'Defining a forum for entrepreneurship sc'): 'OLS/Linear Regression',
        (532, 'Star entrepreneurs on digital platforms:'): 'Simulation Technique',
        (544, 'A longitudinal study of cognitive factor'): 'Panel/Fixed Effects; Simulation Technique',
        (551, 'A total eclipse of the heart: Compensati'): 'Panel/Fixed Effects',
        (561, 'Sleep and entrepreneurs\' abilities to im'): 'Panel/Fixed Effects',
        (584, 'Owls, larks, or investment sharks? The r'): 'Conjoint Analysis',
        (591, 'Gender differences in evaluation of new '): 'Conjoint Analysis',
        (628, 'Strategy-organization configurations in '): 'Panel/Fixed Effects',
        (637, 'Network-based research in entrepreneursh'): 'Descriptive/Exploratory',
        (653, '\'I know I can, but I don\'t fit\': Perceiv'): 'Descriptive/Exploratory',
        (658, 'Cracks in the wall: Entrepreneurial acti'): 'Descriptive/Exploratory',
        (664, 'Improving new venture performance: The r'): 'OLS/Linear Regression',
        (673, 'Firm creation and economic transitions'): 'Descriptive/Exploratory',
        (676, 'Factors influencing the choice between f'): 'OLS/Linear Regression',
        (684, 'Entrepreneurship and growth: The strateg'): 'OLS/Linear Regression',
        (687, 'Novelty and new firm performance: The ca'): 'Panel/Fixed Effects',
        (696, 'Venture management in Japanese companies'): 'Descriptive/Exploratory',
        (699, 'New technologies and technological infor'): 'Descriptive/Exploratory',
        (721, 'Franchising and the choice of self-emplo'): 'Panel/Fixed Effects',
        (722, 'Multi-unit franchising: Growth and manag'): 'OLS/Linear Regression',
        (724, 'Venture Capital in Transition Economies:'): 'Qualitative Coding',
        (727, 'A stage-contingent model of design and g'): 'OLS/Linear Regression',
        (731, 'Reaching out or going it alone? How birt'): 'SEM/Path Analysis',
        (734, 'Assessing venture capital investments wi'): 'Conjoint Analysis',
        (737, 'Information and the Small Manufacturing '): 'Descriptive/Exploratory',
        (742, 'Entrepreneurial imaginativeness and new '): 'Cluster/Latent Class',
        (745, 'The tortoise versus the hare: Progress a'): 'HLM/Multilevel',
        (751, 'The risk/return attributes of publicly t'): 'Time Series',
        (765, 'An analytical framework for science park'): 'Qualitative Coding',
        (790, 'Why and how do founding entrepreneurs bo'): 'Conjoint Analysis; Event Study Technique',
        (806, 'Public versus private venture capital: S'): 'Panel/Fixed Effects',
        (808, 'Behavioral disinhibition and nascent ven'): 'Descriptive/Exploratory',
        (818, 'Formal institutions, culture, and ventur'): 'Panel/Fixed Effects',
        (836, 'The Management of Growth: An Entrepreneu'): 'Panel/Fixed Effects',
        (845, 'Intuitive optimizing: Experimental findi'): 'Descriptive/Exploratory',
        (856, 'Corporate venturing: Alternatives, obsta'): 'Descriptive/Exploratory',
        (881, 'Escaping the knowledge corridor: How fou'): 'OLS/Linear Regression',
        (882, 'The order and size of entry into interna'): 'OLS/Linear Regression',
        (884, 'False signaling by platform team members'): 'SEM/Path Analysis',
        (889, 'A comparison of Japanese and U.S. firms '): 'Descriptive/Exploratory',
        (894, 'Going public: The impact of insiders\' ho'): 'Time Series',
        (897, 'New venture internationalization, strate'): 'OLS/Linear Regression',
        (900, 'More like each other than anyone else? A'): 'OLS/Linear Regression',
        (907, 'Assessing economic value added by univer'): 'Descriptive/Exploratory',
        (916, 'Patterns of growth, competitive technolo'): 'OLS/Linear Regression',
        (917, 'Modeling new venture performance: An ana'): 'Descriptive/Exploratory',
        (920, 'Uncovering the influence of social ventu'): 'Time Series',
        (924, 'When Failure Is Not Fatal: Examining Ven'): 'Panel/Fixed Effects',
        (926, 'Cross-border private equity syndication:'): 'Time Series',
        (927, 'Venturing into the unknown with stranger'): 'Descriptive/Exploratory',
        (928, 'The RICH Entrepreneur: Using Conservatio'): 'Factor Analysis',
        (929, 'The Failure Syndrome'): 'Descriptive/Exploratory',
        (932, 'Can a franchise chain coordinate?'): 'Descriptive/Exploratory',
        (933, 'Participative Management in the Small Fi'): 'ANOVA/t-test; Panel/Fixed Effects',
        (935, 'The frugal entrepreneur: A self-regulato'): 'OLS/Linear Regression',
        (939, 'Making the most of group relationships: '): 'Descriptive/Exploratory',
        (942, 'Lost in time: Intergenerational successi'): 'Descriptive/Exploratory',
        (943, 'Institutional logics, family firm govern'): 'Descriptive/Exploratory',
        (944, 'Entry order, market share, and competiti'): 'OLS/Linear Regression',
        (947, 'Goal Programming for Decision Making in '): 'Simulation Technique',
        (948, 'Productivity in the Small Business Secto'): 'Panel/Fixed Effects',
        (948, 'Defining the inventor-entrepreneur in th'): 'Descriptive/Exploratory',
        (951, 'Microcomputers and the SBI Program'): 'Descriptive/Exploratory',
        (952, 'Nothing Ventured, Nothing Gained: Parasi'): 'Panel/Fixed Effects',
        (957, 'Should Small, Young Technology-Based Fir'): 'Descriptive/Exploratory',
        (957, 'From distinctiveness to optimal distinct'): 'SEM/Path Analysis',
        (959, 'Accountability for social impact: A bric'): 'Qualitative Coding',
        (961, 'How Do \'Resource Bundles\' Develop and Ch'): 'Panel/Fixed Effects',
        (964, 'Are SMEs with immigrant owners exception'): 'Descriptive/Exploratory',
        (968, 'Funding the story of hybrid ventures: Cr'): 'Descriptive/Exploratory',
        (969, 'Partnerships as an enabler of resourcefu'): 'SEM/Path Analysis',
        (972, 'Research Note: Trade Name Franchise Memb'): 'Descriptive/Exploratory',
        (974, 'Culture and entrepreneurial potential: A'): 'Descriptive/Exploratory',
        (975, 'A System Justification Theory of Entrepr'): 'Descriptive/Exploratory',
        (976, 'Early growth decisions of entrepreneurs:'): 'Conjoint Analysis',
        (977, 'How Different Institutional Logics Affec'): 'Panel/Fixed Effects',
        (977, 'Missing the boat or sinking the boat: A '): 'Conjoint Analysis',
        (979, 'Hot Markets, Sociocognitive Cues, and Ne'): 'Panel/Fixed Effects',
        (979, 'Assessing the impact of public venture c'): 'Time Series',
        (984, 'From principles to action: Community-bas'): 'Descriptive/Exploratory',
        (988, 'Risky Decisions and the Family Firm Bias'): 'Conjoint Analysis',
        (989, 'The effect of a tax training program on '): 'Descriptive/Exploratory',
        (990, 'Entrepreneurial growth: The role of inte'): 'OLS/Linear Regression',
        (996, 'Measuring the Costs and Coverage of SME '): 'Panel/Fixed Effects',
        (996, 'Do young firms owned by recent immigrant'): 'OLS/Linear Regression',
        (997, 'Can One Stone Kill Two Birds? Political '): 'Qualitative Coding',
        (997, 'Atypical entrepreneurs in the venture id'): 'Conjoint Analysis',
        (1004, 'Satisfaction With Firm Performance in Fa'): 'Descriptive/Exploratory',
        (1004, 'Strategic experimentation: Understanding'): 'Time Series',
        (1005, 'The Legitimization Effect of Crowdfundin'): 'Conjoint Analysis',
        (1007, 'Do Incumbents\' Mergers Influence Entrepr'): 'Descriptive/Exploratory',
        (1008, 'The Role of Political Values and Ideolog'): 'Descriptive/Exploratory',
        (1012, 'Capital structure and small public firms'): 'Descriptive/Exploratory',
        (1013, 'Specialization versus diversification as'): 'OLS/Linear Regression',
        (1022, 'Entrepreneurs in Japan and Silicon Valle'): 'Descriptive/Exploratory',
        (1032, 'Sounds novel or familiar? Entrepreneurs\''): 'Time Series',
        (1033, 'Trustworthiness: A Critical Ingredient f'): 'Descriptive/Exploratory',
        (1034, 'How entrepreneurs seduce business angels'): 'Time Series',
        (1035, 'How venture capitalists respond to unmet'): 'Descriptive/Exploratory',
        (1036, 'Linguistic style and crowdfunding succes'): 'Descriptive/Exploratory',
        (1038, 'Agency Costs, Market Discipline and Mark'): 'Panel/Fixed Effects',
        (1044, 'The entrepreneur\'s mode of entry: Busine'): 'Descriptive/Exploratory',
        (1047, 'Communicating During Societal Crises: Ho'): 'Conjoint Analysis',
        (1048, 'Congruence in Exchange: The Influence of'): 'Descriptive/Exploratory',
        (1051, 'Some Problems in Using Subjective Measur'): 'Correlation',
        (1056, 'Is Prior Failure a Burden for Entreprene'): 'Panel/Fixed Effects',
        (1057, 'Marketing strategies that make entrepren'): 'Time Series',
        (1058, 'Entrepreneurial recovery strategies of s'): 'OLS/Linear Regression',
        (1059, 'Effects of managers\' entrepreneurial beh'): 'Descriptive/Exploratory',
        (1068, 'Explaining the formation of internationa'): 'Descriptive/Exploratory',
        (1069, 'Building entrepreneurial tie portfolios '): 'Descriptive/Exploratory',
        (1070, 'Is lack of funds the main obstacle to gr'): 'Descriptive/Exploratory',
        (1073, 'Improving new technology venture perform'): 'Descriptive/Exploratory',
        (1074, 'The Relationship Between Marketing Orien'): 'Descriptive/Exploratory',
        (1075, 'Exploring the Practice of Corporate Vent'): 'Descriptive/Exploratory',
        (1076, 'Labor Productivity in Large and Small En'): 'Descriptive/Exploratory',
        (1077, 'Bringing the elephant into the room? Ena'): 'Qualitative Coding',
        (1080, 'In user\'s shoes: An experimental design '): 'Conjoint Analysis',
        (1084, 'Entrepreneurial visions in founding team'): 'Qualitative Coding',
        (1085, 'Governance, Social Identity, and Entrepr'): 'OLS/Linear Regression',
        (1085, 'Team resilience building in response to '): 'Descriptive/Exploratory',
        (1086, 'Bifurcating Time: How Entrepreneurs Reco'): 'Descriptive/Exploratory',
        (1089, 'Are \'sea turtles\' slower? Returnee entre'): 'Qualitative Coding',
        (1090, 'Social entrepreneurship and intersection'): 'Descriptive/Exploratory',
        (1099, 'Venture Capital Supply and Accounting In'): 'Descriptive/Exploratory',
        (1106, 'Motivating Prosocial Venturing in Respon'): 'Descriptive/Exploratory',
        (1108, 'Entrepreneurial alliances as contractual'): 'Descriptive/Exploratory',
        (1113, 'Loan guarantees: Costs of default and be'): 'Factor Analysis',
        (1119, 'An examination of the influence of indus'): 'Descriptive/Exploratory',
        (1120, 'Product life-cycle considerations and th'): 'Qualitative Coding',
        (1131, 'Comparing the information acquisition st'): 'Descriptive/Exploratory',
        (1132, 'Assessing the effectiveness of guided pr'): 'Descriptive/Exploratory',
        (1134, 'A Synthesis of Six Exploratory, European'): 'Descriptive/Exploratory',
        (1136, 'A venture capital model of the developme'): 'Descriptive/Exploratory',
        (1146, 'Institutional Arrangements and Internati'): 'Descriptive/Exploratory',
        (1153, 'SME Survey Methodology: Response Rates, '): 'Conjoint Analysis',
        (1156, 'The Legitimacy of Social Entrepreneurshi'): 'Qualitative Coding',
        (1157, 'News and Nuances of the Entrepreneurial '): 'Qualitative Coding',
        (1170, 'The Interdependence Between Donors and I'): 'Descriptive/Exploratory',
        (1171, 'A Longitudinal Study of Conditional Stud'): 'Panel/Fixed Effects',
        (1181, 'A Benefit-Cost Study of an Education Inv'): 'Panel/Fixed Effects',
        (1186, 'Are champions different from non-champio'): 'OLS/Linear Regression',
        (1212, 'Stratification, Economic Adversity, and '): 'Descriptive/Exploratory',
        (1238, 'Exploring the relative efficacy of \'with'): 'Descriptive/Exploratory',
        (1243, 'University spin-out companies: Technolog'): 'Descriptive/Exploratory',
        (1244, 'Decision making behavior in smaller entr'): 'Qualitative Coding',
        (1246, 'Information Systems in Small Business: A'): 'Descriptive/Exploratory',
        (1260, 'A tale of two life stages: The imprintin'): 'OLS/Linear Regression',
        (1293, 'Globalization and affordability of micro'): 'Panel/Fixed Effects',
        (1307, 'Mortgage affordability and entrepreneurs'): 'DiD/Matching',
        (1310, 'Venture Capitalist and CEO Dismissal'): 'Descriptive/Exploratory',
        (1311, 'CEO Dismissal in Venture Capital-Backed '): 'Descriptive/Exploratory',
        (1311, 'Venturing in turbulent water: A historic'): 'Descriptive/Exploratory',
        (1312, 'Growth of industry clusters and innovati'): 'Descriptive/Exploratory',
        (1313, 'Phase transitions and emergence of entre'): 'OLS/Linear Regression',
        (1314, 'A Growth Mindset Intervention: Enhancing'): 'Conjoint Analysis',
        (1316, 'Equity Crowdfunders\' Human Capital and S'): 'Descriptive/Exploratory',
        (1318, 'Up to standard? Market positioning and p'): 'Panel/Fixed Effects',
        (1323, 'Size of investment, opportunity choice a'): 'Qualitative Coding',
        (1326, 'The evolution of strategic alliances: Op'): 'Descriptive/Exploratory',
        (1328, 'The relationship between governance stru'): 'OLS/Linear Regression',
        (1339, 'Top management teams and corporate succe'): 'Time Series',
        (1340, 'Corporate Entrepreneurship in Family Fir'): 'Descriptive/Exploratory',
        (1343, 'Technology-Based Strategic Actions in Ne'): 'Descriptive/Exploratory',
        (1344, 'Effects of strategy and environment on c'): 'OLS/Linear Regression',
        (1354, 'The Relationship Between Knowledge Trans'): 'Panel/Fixed Effects',
        (1356, 'Bounded Rationality and Bounded Reliabil'): 'Descriptive/Exploratory',
        (1357, 'Cultural Influences on Entrepreneurial O'): 'Descriptive/Exploratory',
        (1367, 'Preparing for scaling: A study on founde'): 'Qualitative Coding',
        (1369, 'See Paris and… found a business? The imp'): 'SEM/Path Analysis',
        (1370, 'From platform growth to platform scaling'): 'Qualitative Coding',
        (1375, 'Hostile environmental jolts, transaction'): 'SEM/Path Analysis',
        (1380, 'Time Perspective and Entrepreneurs\' Aler'): 'Qualitative Coding',
        (1386, 'Risky Decisions and the Family Firm Bias'): 'Conjoint Analysis',
        (1390, 'The leisure paradox for entrepreneurs: A'): 'Descriptive/Exploratory',
        (1401, 'Agency, Strategic Entrepreneurship, and '): 'Descriptive/Exploratory',
        (1403, 'Assessing Mission and Resources for Soci'): 'Conjoint Analysis',
        (1405, 'Head in the clouds? Cannabis users\' crea'): 'Conjoint Analysis',
        (1409, 'A Systems Approach To Water Pollution Ab'): 'Descriptive/Exploratory',
        (1415, 'Women Entrepreneurs and Financial Capita'): 'OLS/Linear Regression',
        (1422, 'The internationalization of new and smal'): 'Qualitative Coding',
        (1427, 'DUPLICATE of paper 1426 (Wiklund et al. '): 'Descriptive/Exploratory',
        (1431, 'The Monitoring of Venture Capital Firms'): 'Qualitative Coding',
        (1432, 'Entrepreneurship Education in America\'s '): 'Panel/Fixed Effects',
        (1434, 'Strategic versus Operational Planning in'): 'Descriptive/Exploratory',
        (1436, 'The Human Resource Factor in Small Busin'): 'Panel/Fixed Effects',
        (1446, 'Gender and Ownership in UK Small Firms'): 'Panel/Fixed Effects',
        (1460, 'Path Dependence in New Ventures Capital '): 'Panel/Fixed Effects',
        (1464, 'The Use of Verbal Protocols in Determini'): 'Descriptive/Exploratory',
        (1469, 'Founder Characteristics, Start-Up Proces'): 'Descriptive/Exploratory',
        (1478, 'When a crisis hits: An examination of th'): 'Conjoint Analysis',
        (1480, 'Belated Recognition for Work Flow Entrep'): 'Descriptive/Exploratory',
        (1485, 'The nature of information and overconfid'): 'Conjoint Analysis; OLS/Linear Regression',
        (1491, 'Role Model Performance Effects on Develo'): 'Descriptive/Exploratory',
        (1492, 'Explorative and Exploitative Learning fr'): 'Descriptive/Exploratory',
        (1499, 'Labor Market Segmentation in Small Busin'): 'Descriptive/Exploratory',
        (1504, 'Bankruptcy Regulation and Self-Employmen'): 'Descriptive/Exploratory',
        (1523, 'Transnational Entrepreneurship: Determin'): 'Descriptive/Exploratory',
        (1531, 'Four Bases of Family Business Successor '): 'Descriptive/Exploratory',
        (1532, 'Strategic Divestments in Family Firms: R'): 'Descriptive/Exploratory',
        (1540, 'Prior Knowledge, Potential Financial Rew'): 'Conjoint Analysis',
        (1559, 'Credit Strategy in Small and Large Compa'): 'Descriptive/Exploratory',
        (1565, 'The Knowledge Spillover Theory of Entrep'): 'Descriptive/Exploratory',
        (1575, 'Informal Entrepreneurship and Industry C'): 'Descriptive/Exploratory',
        (1580, 'The Influence of Internal Social Capital'): 'Descriptive/Exploratory',
        (1586, 'Informal Institutions as Inhibitors of R'): 'Descriptive/Exploratory',
        (1598, 'The Collaborative Network Orientation: A'): 'Descriptive/Exploratory',
        (1604, 'Estimates of The Number of Quasi and Sma'): 'Panel/Fixed Effects',
        (1607, 'Performance Configurations over Time: Im'): 'Panel/Fixed Effects',
        (1622, 'Environmental Perceptions and Scanning i'): 'Descriptive/Exploratory',
        (1630, 'How Entrepreneurs Use Networks to Addres'): 'Descriptive/Exploratory',
        (1633, 'A Comparison of Insurance and Pension Pl'): 'Descriptive/Exploratory',
        (1639, 'Regulatory Environment and Strategic Ori'): 'Descriptive/Exploratory',
        (1640, 'Culture, Nation, and Entrepreneurial Str'): 'Conjoint Analysis',
        (1642, 'Exploring an Inverted U-Shape Relationsh'): 'Descriptive/Exploratory',
        (1643, 'Proactiveness, Stakeholder-Firm Power Di'): 'OLS/Linear Regression',
        (1650, 'Entrepreneurial Start-up and Growth: A C'): 'Cluster/Latent Class',
        (1654, 'Training Needs Of Managers Of Small Manu'): 'OLS/Linear Regression',
        (1656, 'Individual Entrepreneurial Intent: Const'): 'Factor Analysis',
        (1658, 'Productivity in Small Business: An Analy'): 'OLS/Linear Regression',
        (1659, 'Passing Up the Job: The Role of Gendered'): 'Logistic/Limited DV',
        (1663, 'Economic and Noneconomic Factors Affecti'): 'Logistic/Limited DV',
        (1667, 'Too Red for Crowdfunding: The Legitimati'): 'Logistic/Limited DV',
        (1671, 'The Goal Setting Process Within Small Bu'): 'Qualitative Coding',
        (1672, 'Easy Now, Desirable Later: The Moderatin'): 'Conjoint Analysis',
        (1677, 'Increasing the Advertising Effectiveness'): 'SEM/Path Analysis',
        (1683, 'Do Serial and Non-Serial Investors Behav'): 'Logistic/Limited DV',
        (1684, 'How Prior Corporate Venture Capital Inve'): 'Logistic/Limited DV',
        (1688, 'Outside Board Human Capital and Early St'): 'Panel/Fixed Effects',
        (1691, 'Consumer Responses to Small Business Cou'): 'Conjoint Analysis; Simulation Technique',
        (1702, 'Venture Capital Through \'Regulation A\' P'): 'Descriptive/Exploratory',
        (1709, 'Linking Corporate Entrepreneurship to Fi'): 'Simulation Technique',
        (1711, 'Valuation Methods and Estimates in Relat'): 'Conjoint Analysis',
        (1714, 'Entrepreneurial Attitudes and Knowledge '): 'Logistic/Limited DV',
        (1720, 'Social Structure of Regional Entrepreneu'): 'Cluster/Latent Class; Panel/Fixed Effects',
        (1721, 'Family Diversity and Business Start-Up: '): 'Panel/Fixed Effects',
        (1724, 'The Entrepreneurship Process in Base of '): 'Descriptive/Exploratory',
        (1729, 'Emotions and Opportunities: The Interpla'): 'Conjoint Analysis',
        (1735, 'Following in the Footsteps of Others: So'): 'Conjoint Analysis',
        (1736, 'Collective Cognition: When Entrepreneuri'): 'OLS/Linear Regression',
        (1737, 'Temporal Dimensions of Opportunistic Cha'): 'OLS/Linear Regression',
        (1740, 'Family Firm Research: The Need for a Met'): 'OLS/Linear Regression',
        (1741, 'Novice, Portfolio, and Serial Founders i'): 'Descriptive/Exploratory',
        (1746, 'The Sustainability of the Entrepreneuria'): 'Panel/Fixed Effects',
        (1776, 'Differences Between Exporters and Non-Ex'): 'Panel/Fixed Effects',
        (1788, 'Harvesting and the Longevity of Manageme'): 'OLS/Linear Regression',
        (1793, 'Second-Order Gender Effects: The Case of'): 'OLS/Linear Regression',
        (1794, 'Internal Resources, External Network, an'): 'OLS/Linear Regression',
        (1798, 'Rising From the Ashes: Cognitive Determi'): 'OLS/Linear Regression',
        (1803, 'ADHD Symptoms, Entrepreneurial Orientati'): 'Panel/Fixed Effects',
        (1804, 'ADHD Symptoms, Entrepreneurial Orientati'): 'OLS/Linear Regression',
        (1805, 'ADHD Symptoms, Entrepreneurial Orientati'): 'OLS/Linear Regression',
        (1809, 'New Product Innovation in Established Co'): 'OLS/Linear Regression',
        (1810, 'The Effect of the Environment on Export '): 'OLS/Linear Regression',
        (1825, 'Missing the Forest for the Trees: Prior '): 'Conjoint Analysis',
        (1826, 'Founders Matter! Serial Entrepreneurs an'): 'Logistic/Limited DV',
        (1838, 'The Influence of Top Management Team Het'): 'OLS/Linear Regression',
        (1839, 'Toward a Theory of Family Social Capital'): 'Qualitative Coding',
        (1841, 'Founding a Business Inspired by Close En'): 'Panel/Fixed Effects',
        (1842, 'Which Entrepreneurs Bribe and What Do Th'): 'OLS/Linear Regression',
        (1843, 'Entrepreneurial Behavior in Organization'): 'Panel/Fixed Effects',
        (1846, 'Are We Comparing Apples With Apples or A'): 'OLS/Linear Regression',
        (1759, 'Employer Legitimacy and Recruitment Suc'): 'Descriptive/Exploratory',
        (1765, 'Gender, Entrepreneurial Self'): 'OLS/Linear Regression',
    }

    # ── Filter to empirical papers only ──
    empirical_types = ['Empirical-Quantitative', 'Empirical-Qualitative', 'Empirical-Mixed']
    mask = df['std_paper_type'].isin(empirical_types)

    df['std_method_design'] = ''
    df['std_method_technique'] = ''

    for idx in df[mask].index:
        row = df.loc[idx]

        # ── DESIGN: match against method + data_source + sample + title ──
        method_text = str(row.get('method', '')).lower()
        data_text = str(row.get('data_source', '')).lower()
        sample_text = str(row.get('sample', '')).lower()
        title_text = str(row.get('title', '')).lower()
        combined_design = f"{method_text} ||| {data_text} ||| {sample_text} ||| {title_text}"

        designs = set()
        for category, pattern in DESIGN_RULES.items():
            if re.search(pattern, combined_design):
                designs.add(category)

        # ── TECHNIQUE: match against ALL useful columns (broader search) ──
        # Many papers mention techniques in key_findings, abstract, etc. but not in method
        extra_cols = ['key_findings', 'abstract', 'independent_variables',
                      'dependent_variables', 'control_variables', 'connections_and_notes']
        extra_text = ' ||| '.join(
            str(row.get(c, '')).lower() for c in extra_cols
            if pd.notna(row.get(c, '')) and str(row.get(c, '')).strip() not in ('', 'nan', 'N/A')
        )
        combined_technique = f"{combined_design} ||| {extra_text}"

        techniques = set()
        for category, pattern in TECHNIQUE_RULES.items():
            if re.search(pattern, combined_technique):
                techniques.add(category)

        # ── TECHNIQUE INFERENCE: if no technique found, infer from design + paper type ──
        # Rationale: Qualitative papers with Case Study / Interview / Grounded Theory
        # designs almost always use some form of qualitative coding, even if not stated.
        if not techniques:
            paper_type = str(row.get('std_paper_type', ''))
            if paper_type == 'Empirical-Qualitative':
                techniques.add('Qualitative Coding')
            elif paper_type == 'Empirical-Mixed':
                # Mixed methods: if designs include qualitative elements, add Qualitative Coding
                qual_designs = {'Case Study', 'Interview/Fieldwork', 'Grounded Theory', 'Action Research'}
                if designs & qual_designs:
                    techniques.add('Qualitative Coding')

        # ── DESIGN: Manual override if no design matched ──
        if not designs:
            pid = int(row.get('paper_id', -1))
            title = str(row.get('title', ''))[:40]
            for (oid, tstart), dval in MANUAL_DESIGN_OVERRIDES.items():
                if pid == oid and title.startswith(tstart):
                    # Support multi-valued overrides (semicolon-separated)
                    for d in dval.split(';'):
                        d = d.strip()
                        if d:
                            designs.add(d)
                    break

        # ── TECHNIQUE: Manual override if no technique matched ──
        if not techniques:
            pid = int(row.get('paper_id', -1))
            title = str(row.get('title', ''))[:40]
            for (oid, tstart), tval in MANUAL_TECHNIQUE_OVERRIDES.items():
                if pid == oid and title.startswith(tstart):
                    for t in tval.split(';'):
                        t = t.strip()
                        if t:
                            techniques.add(t)
                    break

        df.at[idx, 'std_method_design'] = '; '.join(sorted(designs)) if designs else ''
        df.at[idx, 'std_method_technique'] = '; '.join(sorted(techniques)) if techniques else ''

    # ── Validation ──
    emp = df[mask]
    has_design = emp['std_method_design'].ne('').sum()
    has_tech = emp['std_method_technique'].ne('').sum()
    print(f"std_method_design: {has_design}/{len(emp)} empirical papers classified ({has_design/len(emp)*100:.1f}%)")
    print(f"std_method_technique: {has_tech}/{len(emp)} empirical papers classified ({has_tech/len(emp)*100:.1f}%)")

    return df


def std_country_region_continent(df):
    """
    Variables: std_country, std_region, std_continent
    Source column(s): country_context
    Date finalized: 2026-03-10

    Decision rationale:
      - Top-down approach: match country names from a comprehensive lookup table
      - Multi-valued: papers studying multiple countries get semicolon-separated values
      - Three derived variables: std_country (specific), std_region (sub-continental), std_continent
      - "Likely/inferred" entries verified by AI intelligence before inclusion
      - "Multi-Country/Global" assigned to studies explicitly covering multiple countries,
        international samples, cross-national designs, or global contexts without listing
        specific individual countries
      - Region/continent still derived where possible (e.g., "European countries" → Europe)
      - For truly global studies, region/continent left empty
      - Entries with no identifiable country AND no multi-country signal (e.g., "General",
        "Not specified", "Not applicable", conceptual papers) receive empty values
      - Region groupings follow UN geoscheme with minor adaptations for research relevance
      - US states/cities, Canadian provinces, and UK constituent countries map to parent country

    std_continent categories (6):
      North America, South America, Europe, Asia, Africa, Oceania

    std_region categories (13):
      Northern America, Latin America & Caribbean,
      Western Europe, Southern Europe, Northern Europe, Eastern Europe,
      East Asia, Southeast Asia, South Asia, Central Asia,
      Middle East & North Africa, Sub-Saharan Africa,
      Oceania
    """

    # ── COUNTRY → (CONTINENT, REGION) LOOKUP ──
    COUNTRY_GEO = {
        # North America
        'United States': ('North America', 'Northern America'),
        'Canada': ('North America', 'Northern America'),
        'Mexico': ('North America', 'Latin America & Caribbean'),
        'Guatemala': ('North America', 'Latin America & Caribbean'),
        'Costa Rica': ('North America', 'Latin America & Caribbean'),
        'Panama': ('North America', 'Latin America & Caribbean'),
        'Cuba': ('North America', 'Latin America & Caribbean'),
        'Jamaica': ('North America', 'Latin America & Caribbean'),
        'Trinidad and Tobago': ('North America', 'Latin America & Caribbean'),
        'Puerto Rico': ('North America', 'Latin America & Caribbean'),
        'El Salvador': ('North America', 'Latin America & Caribbean'),
        'Honduras': ('North America', 'Latin America & Caribbean'),
        'Nicaragua': ('North America', 'Latin America & Caribbean'),
        'Dominican Republic': ('North America', 'Latin America & Caribbean'),
        'Haiti': ('North America', 'Latin America & Caribbean'),
        # South America
        'Brazil': ('South America', 'Latin America & Caribbean'),
        'Argentina': ('South America', 'Latin America & Caribbean'),
        'Chile': ('South America', 'Latin America & Caribbean'),
        'Colombia': ('South America', 'Latin America & Caribbean'),
        'Peru': ('South America', 'Latin America & Caribbean'),
        'Venezuela': ('South America', 'Latin America & Caribbean'),
        'Ecuador': ('South America', 'Latin America & Caribbean'),
        'Bolivia': ('South America', 'Latin America & Caribbean'),
        'Paraguay': ('South America', 'Latin America & Caribbean'),
        'Uruguay': ('South America', 'Latin America & Caribbean'),
        # Western Europe
        'United Kingdom': ('Europe', 'Western Europe'),
        'Germany': ('Europe', 'Western Europe'),
        'France': ('Europe', 'Western Europe'),
        'Netherlands': ('Europe', 'Western Europe'),
        'Belgium': ('Europe', 'Western Europe'),
        'Switzerland': ('Europe', 'Western Europe'),
        'Austria': ('Europe', 'Western Europe'),
        'Luxembourg': ('Europe', 'Western Europe'),
        'Ireland': ('Europe', 'Western Europe'),
        # Southern Europe
        'Italy': ('Europe', 'Southern Europe'),
        'Spain': ('Europe', 'Southern Europe'),
        'Portugal': ('Europe', 'Southern Europe'),
        'Greece': ('Europe', 'Southern Europe'),
        'Malta': ('Europe', 'Southern Europe'),
        'Cyprus': ('Europe', 'Southern Europe'),
        'Croatia': ('Europe', 'Southern Europe'),
        'Slovenia': ('Europe', 'Southern Europe'),
        # Northern Europe
        'Sweden': ('Europe', 'Northern Europe'),
        'Norway': ('Europe', 'Northern Europe'),
        'Denmark': ('Europe', 'Northern Europe'),
        'Finland': ('Europe', 'Northern Europe'),
        'Iceland': ('Europe', 'Northern Europe'),
        # Eastern Europe
        'Poland': ('Europe', 'Eastern Europe'),
        'Czech Republic': ('Europe', 'Eastern Europe'),
        'Slovakia': ('Europe', 'Eastern Europe'),
        'Hungary': ('Europe', 'Eastern Europe'),
        'Romania': ('Europe', 'Eastern Europe'),
        'Bulgaria': ('Europe', 'Eastern Europe'),
        'Serbia': ('Europe', 'Eastern Europe'),
        'Lithuania': ('Europe', 'Eastern Europe'),
        'Latvia': ('Europe', 'Eastern Europe'),
        'Estonia': ('Europe', 'Eastern Europe'),
        'Ukraine': ('Europe', 'Eastern Europe'),
        'Belarus': ('Europe', 'Eastern Europe'),
        'Moldova': ('Europe', 'Eastern Europe'),
        'Albania': ('Europe', 'Eastern Europe'),
        'North Macedonia': ('Europe', 'Eastern Europe'),
        'Bosnia and Herzegovina': ('Europe', 'Eastern Europe'),
        'Montenegro': ('Europe', 'Eastern Europe'),
        'Kosovo': ('Europe', 'Eastern Europe'),
        'Russia': ('Europe', 'Eastern Europe'),
        # East Asia
        'China': ('Asia', 'East Asia'),
        'Japan': ('Asia', 'East Asia'),
        'South Korea': ('Asia', 'East Asia'),
        'Taiwan': ('Asia', 'East Asia'),
        'Hong Kong': ('Asia', 'East Asia'),
        # Southeast Asia
        'Singapore': ('Asia', 'Southeast Asia'),
        'Malaysia': ('Asia', 'Southeast Asia'),
        'Indonesia': ('Asia', 'Southeast Asia'),
        'Thailand': ('Asia', 'Southeast Asia'),
        'Vietnam': ('Asia', 'Southeast Asia'),
        'Philippines': ('Asia', 'Southeast Asia'),
        'Cambodia': ('Asia', 'Southeast Asia'),
        'Myanmar': ('Asia', 'Southeast Asia'),
        'Laos': ('Asia', 'Southeast Asia'),
        # South Asia
        'India': ('Asia', 'South Asia'),
        'Pakistan': ('Asia', 'South Asia'),
        'Bangladesh': ('Asia', 'South Asia'),
        'Sri Lanka': ('Asia', 'South Asia'),
        'Nepal': ('Asia', 'South Asia'),
        # Central Asia
        'Kazakhstan': ('Asia', 'Central Asia'),
        'Uzbekistan': ('Asia', 'Central Asia'),
        # Middle East & North Africa
        'Turkey': ('Asia', 'Middle East & North Africa'),
        'Israel': ('Asia', 'Middle East & North Africa'),
        'Iran': ('Asia', 'Middle East & North Africa'),
        'Saudi Arabia': ('Asia', 'Middle East & North Africa'),
        'United Arab Emirates': ('Asia', 'Middle East & North Africa'),
        'Lebanon': ('Asia', 'Middle East & North Africa'),
        'Jordan': ('Asia', 'Middle East & North Africa'),
        'Egypt': ('Africa', 'Middle East & North Africa'),
        'Morocco': ('Africa', 'Middle East & North Africa'),
        'Tunisia': ('Africa', 'Middle East & North Africa'),
        'Bahrain': ('Asia', 'Middle East & North Africa'),
        'Kuwait': ('Asia', 'Middle East & North Africa'),
        'Oman': ('Asia', 'Middle East & North Africa'),
        'Qatar': ('Asia', 'Middle East & North Africa'),
        # Sub-Saharan Africa
        'South Africa': ('Africa', 'Sub-Saharan Africa'),
        'Nigeria': ('Africa', 'Sub-Saharan Africa'),
        'Kenya': ('Africa', 'Sub-Saharan Africa'),
        'Ghana': ('Africa', 'Sub-Saharan Africa'),
        'Ethiopia': ('Africa', 'Sub-Saharan Africa'),
        'Uganda': ('Africa', 'Sub-Saharan Africa'),
        'Tanzania': ('Africa', 'Sub-Saharan Africa'),
        'Rwanda': ('Africa', 'Sub-Saharan Africa'),
        'Cameroon': ('Africa', 'Sub-Saharan Africa'),
        'Senegal': ('Africa', 'Sub-Saharan Africa'),
        'Zambia': ('Africa', 'Sub-Saharan Africa'),
        'Zimbabwe': ('Africa', 'Sub-Saharan Africa'),
        'Mozambique': ('Africa', 'Sub-Saharan Africa'),
        'Botswana': ('Africa', 'Sub-Saharan Africa'),
        'Namibia': ('Africa', 'Sub-Saharan Africa'),
        'Malawi': ('Africa', 'Sub-Saharan Africa'),
        # Oceania
        'Australia': ('Oceania', 'Oceania'),
        'New Zealand': ('Oceania', 'Oceania'),
        'Fiji': ('Oceania', 'Oceania'),
        'Papua New Guinea': ('Oceania', 'Oceania'),
        'Samoa': ('Oceania', 'Oceania'),
        'Tonga': ('Oceania', 'Oceania'),
        # Additional countries
        'Afghanistan': ('Asia', 'South Asia'),
        'Palestine': ('Asia', 'Middle East & North Africa'),
        'Ivory Coast': ('Africa', 'Sub-Saharan Africa'),
        'Barbados': ('North America', 'Latin America & Caribbean'),
        'Mongolia': ('Asia', 'East Asia'),
        'Syria': ('Asia', 'Middle East & North Africa'),
        'Iraq': ('Asia', 'Middle East & North Africa'),
        'Yemen': ('Asia', 'Middle East & North Africa'),
        'Algeria': ('Africa', 'Middle East & North Africa'),
        'Libya': ('Africa', 'Middle East & North Africa'),
        'Congo DRC': ('Africa', 'Sub-Saharan Africa'),
        'Burkina Faso': ('Africa', 'Sub-Saharan Africa'),
    }

    # ── TEXT → COUNTRY ALIASES (order matters: more specific first) ──
    COUNTRY_ALIASES = [
        # US variants
        (r"\bUnited States\b", 'United States'),
        (r"\bU\.?S\.?A\.?(?=[\s,;.\)\]]|$)", 'United States'),
        (r"\bU\.S\.?\b", 'United States'),
        (r"\bUS\b(?!.*(?:Journal|eful|age|ing|ed\b))", 'United States'),
        # UK variants
        (r"\bUnited Kingdom\b", 'United Kingdom'),
        (r"\bU\.?K\.?\b", 'United Kingdom'),
        (r"\bGreat Britain\b", 'United Kingdom'),
        (r"\bBritain\b", 'United Kingdom'),
        (r"\bBritish\b(?!.*Columbia)", 'United Kingdom'),
        (r"\bEngland\b", 'United Kingdom'),
        (r"\bScotland\b", 'United Kingdom'),
        (r"\bWales\b", 'United Kingdom'),
        (r"\bNorthern Ireland\b", 'United Kingdom'),
        (r"\bLondon\b", 'United Kingdom'),
        # China variants
        (r"\bPeople'?s?\s+Republic\s+of\s+China\b", 'China'),
        (r"\bPRC\b", 'China'),
        (r"\bChinese\b", 'China'),
        # Korea
        (r"\bSouth Korea\b", 'South Korea'),
        (r"\bKorea\b(?!.*North)", 'South Korea'),
        # UAE
        (r"\bUAE\b", 'United Arab Emirates'),
        # Czech
        (r"\bCzech(?:\s+Republic)?\b", 'Czech Republic'),
        (r"\bCzechia\b", 'Czech Republic'),
        # Demonyms
        (r"\bSwiss\b", 'Switzerland'),
        (r"\bDutch\b", 'Netherlands'),
        (r"\bBelgian\b", 'Belgium'),
        (r"\bSwedish\b", 'Sweden'),
        (r"\bNorwegian\b", 'Norway'),
        (r"\bDanish\b", 'Denmark'),
        (r"\bFinnish\b", 'Finland'),
        (r"\bItalian\b", 'Italy'),
        (r"\bSpanish\b", 'Spain'),
        (r"\bIrish\b", 'Ireland'),
        (r"\bRussian\b", 'Russia'),
        (r"\bAustralian\b", 'Australia'),
        (r"\bCanadian\b", 'Canada'),
        (r"\bBrazilian\b", 'Brazil'),
        (r"\bIsraeli\b", 'Israel'),
        (r"\bTurkish\b", 'Turkey'),
        (r"\bJapanese\b", 'Japan'),
        (r"\bGerman\b(?!y)", 'Germany'),
        (r"\bFrench\b(?!.*franchise)", 'France'),
        # US states/cities
        (r"\bSilicon Valley\b", 'United States'),
        (r"\bNew York\b", 'United States'),
        (r"\bCalifornia\b", 'United States'),
        (r"\bTexas\b", 'United States'),
        (r"\bMassachusetts\b", 'United States'),
        (r"\bIndiana\b(?!.*Ocean)", 'United States'),
        (r"\bVirginia\b", 'United States'),
        (r"\bWashington\b", 'United States'),
        (r"\bMidwest\w*\b", 'United States'),
        (r"\bTennessee\b", 'United States'),
        (r"\bUtah\b", 'United States'),
        (r"\bOhio\b", 'United States'),
        (r"\bPennsylvania\b", 'United States'),
        (r"\bIllinois\b", 'United States'),
        (r"\bColorado\b", 'United States'),
        (r"\bFlorida\b", 'United States'),
        (r"\bNorth Carolina\b", 'United States'),
        (r"\bGeorgia\b(?!.*(?:Europe|Eastern|Soviet|Caucasus))", 'United States'),
        (r"\bKickstarter\b", 'United States'),
        # Canadian provinces/cities
        (r"\bQuebec\b", 'Canada'),
        (r"\bOntario\b", 'Canada'),
        (r"\bAlberta\b", 'Canada'),
        (r"\bBritish Columbia\b", 'Canada'),
        (r"\bMontréal\b", 'Canada'),
        (r"\bEdmonton\b", 'Canada'),
        # Additional countries/territories not in main lookup
        (r"\bAfghanistan\b", 'Afghanistan'),
        (r"\bPalestin\w*\b", 'Palestine'),
        (r"\bWest Bank\b", 'Palestine'),
        (r"\bCôte d.Ivoire\b", 'Ivory Coast'),
        (r"\bIvory Coast\b", 'Ivory Coast'),
        (r"\bBarbados\b", 'Barbados'),
        (r"\bSoviet Union\b", 'Russia'),
        (r"\bFiji\b", 'Fiji'),
        (r"\bPapua New Guinea\b", 'Papua New Guinea'),
        (r"\bMongolia\b", 'Mongolia'),
        (r"\bSyria\b", 'Syria'),
        (r"\bIraq\b", 'Iraq'),
        (r"\bYemen\b", 'Yemen'),
        (r"\bAlgeria\b", 'Algeria'),
        (r"\bLibya\b", 'Libya'),
        (r"\bCongo\b", 'Congo DRC'),
        (r"\bBurkina Faso\b", 'Burkina Faso'),
        (r"\bSamoa\b", 'Samoa'),
        (r"\bTonga\b", 'Tonga'),
    ]

    # ── MANUAL COUNTRY OVERRIDES ──
    # For "likely/inferred" entries verified by AI intelligence.
    # Keys: (paper_id, title_starts_with) → 'Country1; Country2'
    MANUAL_COUNTRY_OVERRIDES = {
        # "Likely US" entries verified by context (PIMS database = US, patent data = USPTO, etc.)
        (85, 'Alternative Knowledge Strategies, Compe'): 'United States',
        (670, 'Intangible assets, entry strategies, an'): 'United States',
        (1091, 'The expectations game: The contingent v'): 'United States',
        (1254, 'When do firms benefit from university-i'): 'United States',
    }

    def _extract_countries(text):
        """Extract all country names from a country_context string."""
        if pd.isna(text) or str(text).strip() in ('', 'nan', 'N/A'):
            return set()
        text = str(text).strip()
        found = set()

        # Direct country name matches
        for country in COUNTRY_GEO.keys():
            if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
                found.add(country)

        # Alias matches
        for pattern, canonical in COUNTRY_ALIASES:
            if re.search(pattern, text):
                found.add(canonical)

        return found

    # ── MULTI-COUNTRY/GLOBAL DETECTION ──
    # Patterns that indicate a multi-country or global study
    MULTI_COUNTRY_PATTERNS = [
        r'\bGlobal\b', r'\bInternational\b', r'\bMulti-?country\b',
        r'\bMultiple\s+countr', r'\bMultiple\b(?=.*\b(?:countr|context|econom|market))',
        r'\bMultiple\b', r'\bMulti-?national\b',
        r'\bCross-national\b', r'\bCross-country\b',
        r'\bCross-cultural\b', r'\bCross-European\b',
        r'\d+\s+\w*\s*countr',  # "42 countries", "74 low- and middle-income countries"
        r'\b(?:Nine|Eight|Seven|Six|Five|Four|Three|Two)\s+countr',  # word-form numbers
        r'\bcountr(?:y|ies)\b.*\bcross\b',
        r'\bmeta-analy',  # meta-analyses are usually multi-country
        r'\bemerging\s+(?:econom|market)', r'\bdeveloping\s+(?:econom|countr|market|nation)',
        r'\b(?:low|middle)[\s-]+income\s+countr',
        r'\bOECD\b', r'\bEU[\s-]', r'\bEuropean\s+Union\b',
        r'\bworld\s*wide\b', r'\bnations\b',
        r'\bLDC', r'\btransition\s+econom',
        r'\bBOP\s+market', r'\bBase\s+of\s+the\s+pyramid',
    ]

    # Patterns for region inference from multi-country text
    REGION_HINTS = {
        'Europe': {
            'continents': {'Europe'},
            'patterns': [r'\bEurop\w+\b', r'\bEU[\s\-]', r'\bEuropean\s+Union\b', r'\bOECD\b'],
        },
        'Africa': {
            'continents': {'Africa'},
            'patterns': [r'\bAfric\w+\b', r'\bSub-Saharan\b'],
        },
        'Latin America': {
            'continents': {'South America', 'North America'},
            'patterns': [r'\bLatin\s+Americ\w+\b', r'\bCaribbean\b'],
        },
        'Asia': {
            'continents': {'Asia'},
            'patterns': [r'\bAsi\w+\b', r'\bBRIC\b'],
        },
        'Middle East': {
            'continents': {'Asia', 'Africa'},
            'patterns': [r'\bMiddle\s+East\b', r'\bMENA\b', r'\bArab\b'],
        },
        'North America': {
            'continents': {'North America'},
            'patterns': [r'\bNorth\s+Americ\w+\b'],
        },
        'Oceania': {
            'continents': {'Oceania'},
            'patterns': [r'\bOceani\w+\b', r'\bPacific\s+Island'],
        },
    }

    def _is_multi_country(text):
        """Check if text indicates a multi-country/global study."""
        if not text:
            return False
        text_str = str(text).strip()
        for pat in MULTI_COUNTRY_PATTERNS:
            if re.search(pat, text_str, re.IGNORECASE):
                return True
        # Also check region-only entries like "Europe", "Latin America"
        for region_key, info in REGION_HINTS.items():
            for pat in info['patterns']:
                if re.search(pat, text_str, re.IGNORECASE):
                    return True
        return False

    def _infer_continents_from_text(text):
        """Try to infer continent(s) from multi-country text."""
        text_str = str(text).strip()
        continents = set()
        for region_key, info in REGION_HINTS.items():
            for pat in info['patterns']:
                if re.search(pat, text_str, re.IGNORECASE):
                    continents.update(info['continents'])
        return continents

    # ── N/A PATTERNS (entries that should remain empty) ──
    NA_PATTERNS = [
        r'^Not\s+(?:specified|applicable|specific|reported|extracted)',
        r'^N/?A\b',
        r'^General(?:\s|/|$)',
        r'^Conceptual\b',
        r'^NON-RESEARCH\b',
        r'^FILE NOT FOUND\b',
        r'^OCR FAILED\b',
        r'^DUPLICATE\b',
        r'^RETRACTED\b',
        r'^See paper\b',
    ]

    def _is_na_entry(text):
        """Check if text is a non-applicable entry (no country info)."""
        if not text or pd.isna(text):
            return True
        text_str = str(text).strip()
        if text_str in ('', 'nan', 'N/A'):
            return True
        for pat in NA_PATTERNS:
            if re.search(pat, text_str, re.IGNORECASE):
                return True
        return False

    # ── Apply to all papers ──
    df['std_country'] = ''
    df['std_region'] = ''
    df['std_continent'] = ''

    for idx in df.index:
        row = df.loc[idx]
        text = row['country_context']
        countries = _extract_countries(text)

        # Apply manual overrides (for papers where extraction failed)
        if not countries:
            pid = int(row.get('paper_id', -1))
            title = str(row.get('title', ''))[:40]
            for (oid, tstart), cval in MANUAL_COUNTRY_OVERRIDES.items():
                if pid == oid and title.startswith(tstart):
                    for c in cval.split(';'):
                        c = c.strip()
                        if c:
                            countries.add(c)
                    break

        if countries:
            # Derive region and continent from country lookup
            regions = set()
            continents = set()
            for c in countries:
                if c in COUNTRY_GEO:
                    cont, reg = COUNTRY_GEO[c]
                    continents.add(cont)
                    regions.add(reg)

            df.at[idx, 'std_country'] = '; '.join(sorted(countries))
            df.at[idx, 'std_region'] = '; '.join(sorted(regions))
            df.at[idx, 'std_continent'] = '; '.join(sorted(continents))

        elif _is_multi_country(text):
            # Multi-country/global study — no specific countries extracted
            # Multi-country signals take priority over N/A prefixes (e.g.,
            # "N/A (global literature review)" should be Multi-Country/Global)
            df.at[idx, 'std_country'] = 'Multi-Country/Global'
            # Try to infer continent(s) from text
            inferred_continents = _infer_continents_from_text(text)
            if inferred_continents:
                df.at[idx, 'std_continent'] = '; '.join(sorted(inferred_continents))

    # ── Validation ──
    has_country = df['std_country'].ne('').sum()
    total = len(df)
    print(f"std_country: {has_country}/{total} papers classified ({has_country/total*100:.1f}%)")

    # Distribution
    from collections import Counter
    country_counts = Counter()
    for val in df['std_country']:
        if val:
            for c in val.split('; '):
                country_counts[c] += 1
    print(f"\nTop 20 countries:")
    for c, n in country_counts.most_common(20):
        print(f"  {c:25s} {n:5d}")

    region_counts = Counter()
    for val in df['std_region']:
        if val:
            for r in val.split('; '):
                region_counts[r] += 1
    print(f"\nRegion distribution:")
    for r, n in sorted(region_counts.items(), key=lambda x: -x[1]):
        print(f"  {r:30s} {n:5d}")

    continent_counts = Counter()
    for val in df['std_continent']:
        if val:
            for c in val.split('; '):
                continent_counts[c] += 1
    print(f"\nContinent distribution:")
    for c, n in sorted(continent_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:20s} {n:5d}")

    return df


def std_theory_L1_L2(df):
    """
    Variables: std_theory_L1_discipline, std_theory_L2_name
    Source column(s): theoretical_lens
    Date finalized: 2026-03-10

    Decision rationale:
      - Two-level hierarchy: L1 = broad discipline (9 categories), L2 = canonical theory name
      - Top-down approach: curated catalog of ~160 canonical theories with alias patterns
      - Text cleanup step strips citations (parentheticals with years/authors) before matching
      - Multi-valued: papers can invoke multiple theories, each gets its own L1;L2 pair
      - First-match wins: each raw theory string maps to at most one canonical name
      - Unmatched strings left empty (AI pass fills in remaining)

    std_theory_L1_discipline categories (9):
      1. Economics
      2. Psychology
      3. Sociology
      4. Management / Strategy
      5. Organizational Theory
      6. Entrepreneurship-Specific
      7. Finance
      8. Institutional Theory
      9. Methodology / Philosophy
    """

    # ── THEORY CATALOG: L1 → { L2 canonical: [regex patterns] } ──
    # Patterns are matched case-insensitively against cleaned theory text.
    THEORY_CATALOG = {
        # ============================================================
        # 1. ECONOMICS
        # ============================================================
        'Economics': {
            'Agency Theory': [
                r'\bagency\s+theor', r'\bagency\s+(?:model|perspective|framework)\b',
                r'\bprincipal[\s-]+agent\b', r'\bjensen\s+(?:&|and)\s+meckling\b',
                r'\bbehavioral\s+agency\s+model',
            ],
            'Transaction Cost Economics': [
                r'\btransaction\s+cost', r'\bTCE\b',
            ],
            'Property Rights Theory': [
                r'\bproperty\s+rights?\s+theor',
            ],
            'Occupational Choice Theory': [
                r'\boccupational\s+choice',
            ],
            'Austrian Economics': [
                r'\baustrian\s+econom', r'\bkirzner(?:ian)?\b',
            ],
            'Information Economics': [
                r'\binformation\s+econom',
            ],
            'Game Theory': [
                r'\bgame\s+theor',
            ],
            'Labor Economics': [
                r'\blabou?r\s+econom', r'\blabou?r\s+market\s+theor',
            ],
            'Industrial Organization': [
                r'\bindustrial\s+organiz',
            ],
            'Expected Utility Theory': [
                r'\bexpected\s+utility', r'\butility\s+maximiz',
                r'\butility\s+theor',
            ],
            'Market Failure Theory': [
                r'\bmarket\s+failure',
            ],
            'Agglomeration Economics': [
                r'\bagglomeration',
            ],
            'Regional Economics': [
                r'\bregional\s+econom', r'\bregional\s+development\s+theor',
                r'\beconomic\s+geography\b',
            ],
            'Platform Economics': [
                r'\bplatform\s+econom', r'\btwo[\s-]+sided\s+market',
                r'\bplatform\s+(?:theory|ecosystem\s+theor)',
            ],
            'Human Capital Theory': [
                r'\bhuman\s+capital',
            ],
            'Knowledge Spillover Theory': [
                r'\bknowledge\s+spillover', r'\bKSTE\b',
            ],
            'Contract Theory': [
                r'\bcontract\s+theor', r'\bincomplete\s+contract',
                r'\bfinancial\s+contract',
            ],
            'Financial Intermediation Theory': [
                r'\bfinancial\s+intermediat',
            ],
            'Public Choice Theory': [
                r'\bpublic\s+choice\s+theor', r'\bpublic\s+policy\s+theor',
                r'\bgovernment\s+failure\s+theor',
            ],
            'Rational Choice Theory': [
                r'\brational\s+choice',
            ],
            'Evolutionary Economics': [
                r'\bevolutionary\s+econom', r'\bevolutionary\s+theor',
                r'\bNelson\s+(?:&|and)\s+Winter\b',
            ],
            'Endogenous Growth Theory': [
                r'\bendogenous\s+growth', r'\bgrowth\s+theor(?!.*\bfirm)',
                r'\beconomic\s+growth\s+theor', r'\beconomic\s+development\b',
            ],
            'Transition Economics': [
                r'\btransition\s+econom',
            ],
            'Neoclassical Economics': [
                r'\bneoclassical\s+econom',
            ],
            'Cost-Benefit Analysis': [
                r'\bcost[\s-]+benefit\s+analy',
            ],
            'Rent-Seeking Theory': [
                r'\brent[\s-]+seeking',
            ],
            'Resource Scarcity Theory': [
                r'\bresource\s+scarcity',
            ],
            'Cluster Theory': [
                r'\bcluster\s+theor',
            ],
        },

        # ============================================================
        # 2. PSYCHOLOGY
        # ============================================================
        'Psychology': {
            'Prospect Theory': [
                r'\bprospect\s+theor', r'\bloss\s+aversion',
                r'\bheuristics\s+(?:and|&)\s+biases',
            ],
            'Theory of Planned Behavior': [
                r'\bplanned\s+behavio', r'\bTPB\b', r'\bajzen\b',
                r'\breasoned\s+action\b', r'\bentrepreneurial\s+intent',
            ],
            'Self-Efficacy Theory': [
                r'\bself[\s-]+efficacy',
            ],
            'Self-Regulation Theory': [
                r'\bself[\s-]+regulat',
            ],
            'Self-Determination Theory': [
                r'\bself[\s-]+determinat', r'\bSDT\b(?!.*\bsoftware)',
            ],
            'Bounded Rationality': [
                r'\bbounded\s+rational',
            ],
            'Cognitive Psychology': [
                r'\bcognitive\s+psycholog', r'\bcognitive\s+science\b',
                r'\bcognitive\s+theor(?!.*\binstitut)',
                r'\bmental\s+model', r'\bcognitive\s+bias',
                r'\bschema\s+theor',
            ],
            'Entrepreneurial Cognition': [
                r'\bentrepreneurial\s+cognit', r'\bmanagerial\s+cognit',
                r'\bcounterfactual\s+(?:reason|think)',
            ],
            'Decision Theory': [
                r'\bdecision[\s-]+making\s+theor', r'\bdecision\s+theor',
                r'\bbehavioral\s+decision',
                r'\bjudg(?:ment|e?ment)\s+(?:and|&)\s+decision',
            ],
            'Attribution Theory': [
                r'\battribution\s+theor',
            ],
            'Goal-Setting Theory': [
                r'\bgoal[\s-]+setting\s+theor',
            ],
            'Regulatory Focus Theory': [
                r'\bregulatory\s+focus', r'\bpromotion[\s/-]+prevention',
            ],
            'Motivation Theory': [
                r'\bmotivation\s+theor', r'\bentrepreneurial\s+motivat',
                r'\bprosocial\s+motivat',
            ],
            'Expectancy Theory': [
                r'\bexpectancy\s+(?:theor|violat|value)',
            ],
            'Construal Level Theory': [
                r'\bconstrual\s+level',
            ],
            'Affect Theory': [
                r'\baffect\s+theor', r'\baffective\s+(?:events?|science)\s*(?:theor)?',
                r'\bemotion\s+(?:theor|regulat)',
                r'\bbroaden[\s-]+and[\s-]+build',
            ],
            'Creativity Theory': [
                r'\bcreativity\s+theor',
            ],
            'Identity Theory': [
                r'^identity\s+theor', r'\bidentity\s+(?:work|confirm)',
            ],
            'Social Identity Theory': [
                r'\bsocial\s+identity\s+theor',
            ],
            'Stress and Coping Theory': [
                r'\bstress\s+(?:and|&)\s+coping', r'\bcoping\s+theor',
                r'\bconservation\s+of\s+resources', r'\bCOR\s+theor',
                r'\bjob\s+demands[\s-]+resources',
            ],
            'Learning Theory': [
                r'^learning\s+theor', r'\bsocial\s+learning\s+theor',
                r'\bexperiential\s+learning', r'\bobservational\s+learning',
            ],
            'Impression Management': [
                r'\bimpression\s+management',
            ],
            'Optimal Distinctiveness Theory': [
                r'\boptimal\s+distinctiveness',
            ],
            'Framing Theory': [
                r'\bframing\s+(?:theory|effect)',
            ],
            'Behavioral Economics': [
                r'\bbehaviou?ral\s+econom',
            ],
            'Behavioral Genetics': [
                r'\bbehaviou?ral\s+genetic',
            ],
            'Resilience Theory': [
                r'\bresilience\s+theor', r'\borganizational\s+resilience\b',
            ],
            'Passion Theory': [
                r'\bpassion\s+theor', r'\bentrepreneurial\s+passion',
            ],
            'Personality Psychology': [
                r'\bpersonality\s+psycholog', r'\bbig\s+five\s+personality',
                r'\bpersonality\s+theor', r'\btrait\s+theor',
                r'\bnarcissism\s+theor', r'\blocus\s+of\s+control\b',
            ],
            'Overconfidence Theory': [
                r'\boverconfidence', r'\bhubris\s+theor',
            ],
            'Escalation of Commitment': [
                r'\bescalation\s+of\s+commitment',
            ],
            'Person-Environment Fit': [
                r'\bperson[\s-]+environment\s+fit',
                r'\bperson[\s-]+organi[sz]ation\s+fit',
            ],
            'Expertise Theory': [
                r'\bexpertise\s+(?:theor|develop)',
            ],
            'Metacognition': [
                r'\bmetacognit', r'\bcognitive\s+adaptab',
            ],
            'Well-Being Theory': [
                r'\bwell[\s-]+being\s+theor', r'\beudaimonic',
                r'\bjob\s+satisfaction\s+theor',
            ],
        },

        # ============================================================
        # 3. SOCIOLOGY
        # ============================================================
        'Sociology': {
            'Social Capital Theory': [
                r'\bsocial\s+capital',
            ],
            'Social Network Theory': [
                r'\bsocial\s+network\s+theor', r'\bnetwork\s+theor',
                r'\bnetwork\s+(?:perspective|analysis)\b',
                r'\bstructural\s+holes?\b', r'\bweak\s+ties?\b',
                r'\bgranovetter\b', r'\bhomophil',
            ],
            'Social Exchange Theory': [
                r'\bsocial\s+exchange', r'\brelational\s+exchange',
            ],
            'Social Constructionism': [
                r'\bsocial\s+construction',
            ],
            'Role Theory': [
                r'\brole\s+(?:theor|congruity)', r'\bgender\s+role',
                r'\bsocial\s+role\s+theor',
            ],
            'Embeddedness Theory': [
                r'\bembeddedness', r'\brelational\s+embeddedness',
            ],
            'Cultural Theory': [
                r'\bhofstede\b', r'\bcultural\s+dimensions?\b',
                r'\bcross[\s-]+cultural\s+(?:theor|management|psycholog)',
                r'\bGLOBE\s+framework\b',
            ],
            'Narrative Theory': [
                r'\bnarrative\s+(?:theor|analysis|approach)',
            ],
            'Feminist Theory': [
                r'\bfeminist\s+theor', r'\bsocial\s+feminist',
                r'\bliberal\s+feminist', r'\bgender\s+(?:and|&)\s+entrepreneurship\b',
                r'\bgender\s+theor', r'\bgender\s+(?:stereo|discrim)',
                r'\bintersectionalit',
            ],
            'Trust Theory': [
                r'\btrust\s+theor',
            ],
            'Conflict Theory': [
                r'\bconflict\s+theor',
            ],
            'Social Cognitive Theory': [
                r'\bsocial\s+cognitive\s+theor', r'\bsocial\s+cognition',
            ],
            'Structuration Theory': [
                r'\bstructuration\s+theor', r'\bgiddens\b',
                r'\bduality\s+of\s+structure',
            ],
            'Social Influence Theory': [
                r'\bsocial\s+influence', r'\bsocial\s+contagion',
                r'\bsocial\s+comparison\s+theor',
            ],
            'Social Status Theory': [
                r'\bsocial\s+status\s+theor', r'\bstatus\s+theor',
            ],
            'Authenticity Theory': [
                r'\bauthenticity\s+theor',
            ],
            'Category Theory (Sociology)': [
                r'\bcategory\s+theor', r'\bmarket\s+categor',
                r'\bcategoriz',
            ],
            'Practice Theory': [
                r'\bpractice\s+theor', r'\bpractice\s+turn',
            ],
            'Collective Action Theory': [
                r'\bcollective\s+action\s+theor',
            ],
            'Postcolonial Theory': [
                r'\bpostcolonial', r'\bdecoloni',
            ],
        },

        # ============================================================
        # 4. MANAGEMENT / STRATEGY
        # ============================================================
        'Management / Strategy': {
            'Resource-Based View': [
                r'\bresource[\s-]+based\s+(?:view|theor|perspective|framework)',
                r'\bRBV\b', r'\bRBT\b', r'\bbarney\b',
                r'\bfamiliness\b', r'\bVRIN\b', r'\bVRIO\b',
            ],
            'Dynamic Capabilities': [
                r'\bdynamic\s+capabilit', r'\bdynamic\s+managerial\s+capabilit',
                r'\bcapabilit(?:y|ies)\s+(?:perspective|development|theory)\b',
            ],
            'Knowledge-Based View': [
                r'\bknowledge[\s-]+based\s+(?:view|theor|perspective)',
                r'\bKBV\b', r'\bknowledge\s+(?:creation|transfer|management)\b',
            ],
            'Upper Echelons Theory': [
                r'\bupper\s+echelon', r'\bhambrick\s+(?:&|and)\s+mason\b',
            ],
            'Contingency Theory': [
                r'\bcontingency\s+theor', r'\benvironmental\s+contingency',
                r'\benvironmental\s+determin',
            ],
            'Configurational Theory': [
                r'\bconfig(?:uration|urational)',
            ],
            'Competitive Strategy': [
                r'\bcompetitive\s+(?:strategy|advantage\s+theor|dynamics)\b',
                r'\bporter\b', r'\bfive\s+forces\b',
                r'\bfirst[\s-]+mover\s+advantage',
            ],
            'Resource Dependence Theory': [
                r'\bresource\s+dependenc',
            ],
            'Stakeholder Theory': [
                r'\bstakeholder\s+theor',
            ],
            'Strategic Management': [
                r'^strategic\s+management', r'\bstrategic\s+(?:choice|planning|leadership)\b',
                r'\bstrategic\s+groups?\s+theor',
            ],
            'Strategic Alliance Theory': [
                r'\bstrategic\s+alliance', r'\balliance\s+theor',
            ],
            'Absorptive Capacity': [
                r'\babsorptive\s+capacit',
            ],
            'Exploration-Exploitation': [
                r'\bexploration[\s/-]+exploitation', r'\bambidext',
            ],
            'Attention-Based View': [
                r'\battention[\s-]+based', r'\bABV\b',
            ],
            'Business Model Theory': [
                r'\bbusiness\s+model\s+(?:theor|innovat|framework)',
            ],
            'Innovation Theory': [
                r'\binnovation\s+(?:theor|management|diffus|system|econom)',
                r'\bopen\s+innovation\b',
            ],
            'Penrose Growth Theory': [
                r'\bpenrose\b',
                r'\btheory\s+of\s+(?:the\s+)?(?:growth\s+of\s+the\s+)?firm\b',
            ],
            'Leadership Theory': [
                r'\bleadership\s+theor',
            ],
            'Diversification Theory': [
                r'\bdiversification\s+theor',
            ],
            'Resource Orchestration': [
                r'\bresource\s+orchestrat', r'\bresource\s+mobiliz',
            ],
            'Relational View': [
                r'\brelational\s+view\b',
            ],
        },

        # ============================================================
        # 5. ORGANIZATIONAL THEORY
        # ============================================================
        'Organizational Theory': {
            'Organizational Ecology': [
                r'\borganizational\s+ecolog', r'\bpopulation\s+ecolog',
                r'\bhannan\s+(?:&|and)\s+freeman\b',
                r'\bliability\s+of\s+(?:newness|smallness|adolescence|aging|foreignness|obsolescence)',
                r'\bdensity\s+dependence\b', r'\bcommunity\s+ecology\b',
            ],
            'Organizational Learning': [
                r'\borganizational\s+learning', r'\borganisational\s+learning',
            ],
            'Behavioral Theory of the Firm': [
                r'\bbehaviou?ral\s+theory\s+of\s+the\s+firm',
                r'\bcyert\s+(?:&|and)\s+march\b',
                r'\baspiration\s+level', r'\bperformance\s+feedback\b',
                r'\bproblemistic\s+search',
            ],
            'Imprinting Theory': [
                r'\bimprinting',
            ],
            'Organizational Life Cycle': [
                r'\b(?:organizational|industry|venture)\s+life\s+cycle',
                r'\blife\s+cycle\s+theor', r'\bstages?\s+of\s+development',
                r'\bventure\s+lifecycle',
            ],
            'Information Processing Theory': [
                r'\binformation\s+processing',
            ],
            'Organizational Design': [
                r'\borganizational\s+design',
            ],
            'Organizational Identity': [
                r'\borganizational\s+identity', r'\borganisational\s+identity',
            ],
            'Sensemaking Theory': [
                r'\bsensemak', r'\bsense[\s-]+making',
            ],
            'Paradox Theory': [
                r'\bparadox\s+theor',
            ],
            'Complexity Theory': [
                r'\bcomplexity\s+(?:theor|science)', r'\bchaos\s+theor',
                r'\bnonlinear\s+dynamic',
            ],
            'Organizational Justice': [
                r'\borganizational\s+justice', r'\bprocedural\s+justice',
                r'\bfairness\s+theor',
            ],
            'Systems Theory': [
                r'\bsystems?\s+theor',
            ],
            'Punctuated Equilibrium': [
                r'\bpunctuated\s+equilibrium',
            ],
            'Organizational Emergence': [
                r'\borganizational\s+emergence',
                r'\borganizational\s+(?:founding|creation)\s+theor',
            ],
            'Dominant Coalition Theory': [
                r'\bdominant\s+(?:coalition|logic)\s+theor',
                r'\bdominant\s+logic\b',
            ],
            'Threat-Rigidity Theory': [
                r'\bthreat[\s-]+rigidity',
            ],
        },

        # ============================================================
        # 6. ENTREPRENEURSHIP-SPECIFIC
        # ============================================================
        'Entrepreneurship-Specific': {
            'Entrepreneurial Orientation': [
                r'\bentrepreneurial\s+orientation',
                r'\bEO\b(?=.*\b(?:theory|framework|construct|dimension))',
                r'\bcovin\s+(?:&|and)\s+slevin\b',
                r'\blumpkin\s+(?:&|and)\s+dess\b',
            ],
            'Effectuation Theory': [
                r'\beffectuat', r'\bsarasvathy\b',
                r'\bcausat(?:ion\b.*\beffectuat|ion\s+(?:vs|versus|logic))',
            ],
            'Schumpeterian Theory': [
                r'\bschumpeter', r'\bcreative\s+destruc',
                r'\bbaumol\b.*\b(?:productive|unproductive|destructive)',
            ],
            'Knightian Uncertainty': [
                r'\bknightian\b', r'\bknight\b.*\buncertain',
            ],
            'Corporate Entrepreneurship': [
                r'\bcorporate\s+entrepreneurship', r'\bcorporate\s+venturing',
                r'\bintrapreneurship\b', r'\bCVC\b.*\b(?:liter|theor)',
            ],
            'Strategic Entrepreneurship': [
                r'\bstrategic\s+entrepreneurship',
            ],
            'International Entrepreneurship': [
                r'\binternational\s+entrepreneurship',
                r'\binternationali[sz]ation\s+theor',
                r'\bborn\s+global\b', r'\binternational\s+new\s+venture',
                r'\buppsala\b',
            ],
            'Social Entrepreneurship': [
                r'\bsocial\s+entrepreneurship', r'\bprosocial\s+organiz',
            ],
            'Entrepreneurial Ecosystem': [
                r'\bentrepreneurial\s+ecosystem', r'\becosystem\s+theor',
            ],
            'Entrepreneurial Learning': [
                r'\bentrepreneurial\s+learning',
            ],
            'Entrepreneurial Action Theory': [
                r'\bentrepreneurial\s+(?:action|agency)\b',
                r'\bindividual[\s-]+opportunity\s+nexus',
            ],
            'Bricolage Theory': [
                r'\bbricolage',
            ],
            'Family Business Theory': [
                r'\bfamily\s+(?:business|firm)\s+(?:theor|governance)',
                r'\bfamily\s+systems?\s+theor',
                r'\bsuccession\s+theor', r'\btransgenerational\s+entrepreneurship',
                r'\bprimogeniture\b',
            ],
            'Socioemotional Wealth': [
                r'\bsocioemotional\s+wealth', r'\bSEW\b',
            ],
            'Sustainable Entrepreneurship': [
                r'\bsustainable\s+entrepreneurship',
            ],
            'Cultural Entrepreneurship': [
                r'\bcultural\s+entrepreneurship',
            ],
            'Entrepreneurial Finance': [
                r'\bentrepreneurial\s+finance\b',
            ],
            'Opportunity Theory': [
                r'\bopportunity\s+(?:recogni|discover|creation|theor|identif)',
                r'\balertness\b', r'\bshane\b.*\bprior\s+knowledge',
                r'\bdiscovery\s+(?:theory|vs)',
                r'\bcreation\s+theory\b',
            ],
            'Entrepreneurship Theory (General)': [
                r'^entrepreneurship\s+(?:theory|research)$',
                r'\bentrepreneurship\s+education',
                r'\bacademic\s+entrepreneurship\b',
                r'\bnascent\s+entrepreneurship\b',
            ],
            'Entrepreneurial Exit Theory': [
                r'\bentrepreneurial\s+exit',
            ],
            'Push-Pull Theory': [
                r'\bpush[\s/-]+pull\s+theor',
                r'\bnecessity\s+vs\.?\s+opportunity',
            ],
            'Improvisation Theory': [
                r'\bimprovisat',
            ],
            'Shapero Entrepreneurial Event': [
                r'\bshapero\b',
            ],
        },

        # ============================================================
        # 7. FINANCE
        # ============================================================
        'Finance': {
            'Signaling Theory': [
                r'\bsignal(?:ing|ling)\s+theor', r'\bspence\b',
                r'\bmarket\s+signal', r'\bcertification\s+theor',
            ],
            'Real Options Theory': [
                r'\breal\s+option',
            ],
            'Venture Capital Theory': [
                r'\bventure\s+capital\s+(?:theor|invest|decision|value)',
                r'\bVC\s+(?:governance|value|decision)',
            ],
            'Information Asymmetry': [
                r'\binformation\s+asymmetr', r'\basymmetric\s+inform',
                r'\badverse\s+selection\b', r'\bmoral\s+hazard\b',
            ],
            'Stewardship Theory': [
                r'\bstewardship\s+theor',
            ],
            'Pecking Order Theory': [
                r'\bpecking\s+order',
            ],
            'Capital Structure Theory': [
                r'\bcapital\s+structure',
            ],
            'Portfolio Theory': [
                r'\bportfolio\s+theor', r'\bportfolio\s+entrepreneurship\b',
            ],
            'Corporate Governance': [
                r'\bcorporate\s+governance', r'\bboard\s+governance',
            ],
            'Tournament Theory': [
                r'\btournament\s+theor',
            ],
            'IPO Theory': [
                r'\bIPO\s+(?:theor|pricing)',
            ],
            'Behavioral Finance': [
                r'\bbehaviou?ral\s+finance',
            ],
            'Syndication Theory': [
                r'\bsyndication\s+theor',
            ],
        },

        # ============================================================
        # 8. INSTITUTIONAL THEORY
        # ============================================================
        'Institutional Theory': {
            'Institutional Theory': [
                r'\binstitutional\s+theor', r'\bneo[\s-]+institutional',
                r'\bnorth\b.*\binstitution', r'\bscott\b.*\binstitution',
                r'\binstitutional\s+logic', r'\binstitutional\s+isomorphism',
                r'\binstitution[\s-]+based\s+view',
                r'\binstitutional\s+(?:pillar|voids?|context|work)',
                r'\bhistorical\s+institutional',
            ],
            'Institutional Economics': [
                r'\binstitutional\s+econom',
            ],
            'Institutional Entrepreneurship': [
                r'\binstitutional\s+entrepreneurship',
            ],
            'Legitimacy Theory': [
                r'\blegitimacy\b',
            ],
        },

        # ============================================================
        # 9. METHODOLOGY / PHILOSOPHY
        # ============================================================
        'Methodology / Philosophy': {
            'Research Methodology': [
                r'^research\s+methodolog', r'\bmeasurement\s+theor',
                r'\bconstruct\s+valid', r'\bsurvey\s+methodolog',
                r'\bset[\s-]+theoretic\s+method',
                r'\bprogram\s+evaluation',
                r'\bbibliometric\s+analysis\b',
                r'\bresearch\s+design\b',
            ],
            'Philosophy of Science': [
                r'\bphilosophy\s+of\s+science', r'\bcritical\s+realis',
                r'\bpragmatism\b', r'\binterpretivism\b', r'\bsubjectivism\b',
                r'\bphenomenolog',
            ],
            'Process Theory': [
                r'\bprocess\s+theor',
            ],
            'Grounded Theory': [
                r'^grounded\s+theor',
            ],
            'Multilevel Theory': [
                r'\bmultilevel\s+theor', r'\bmulti[\s-]+level\s+(?:theor|analysis)\b',
            ],
        },
    }

    # ── Build flat lookup list ──
    THEORY_LOOKUP = []
    for discipline, theories in THEORY_CATALOG.items():
        for canonical, patterns in theories.items():
            for pat in patterns:
                THEORY_LOOKUP.append((re.compile(pat, re.IGNORECASE), canonical, discipline))

    # ── Text cleanup function ──
    def _clean_theory_text(text):
        """Strip citations, parenthetical authors/years, and normalize."""
        text = text.strip()
        # Remove parenthetical content with years or author names
        text = re.sub(r'\s*\([^)]*\d{4}[^)]*\)', '', text)
        # Remove trailing parenthetical with just names
        text = re.sub(r'\s*\([A-Z][a-z]+(?:\s*(?:&|and|,)\s*[A-Z][a-z]+)*\)$', '', text)
        # Remove leading/trailing whitespace and punctuation
        text = text.strip().rstrip(',;.')
        return text

    # ── MANUAL THEORY OVERRIDES ──
    # Keys: (paper_id, title_starts_with) → (L2_theories_str, L1_disciplines_str)
    # Generated by AI intelligence pass on 442 substantive unmatched papers
    MANUAL_THEORY_OVERRIDES = {
        (1, 'A Methodology for Participative Formulat'): ('Systems Theory', 'Organizational Theory'),
        (1, 'Machines augmenting entrepreneurs: Oppor'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (4, 'A comparison of methods and sources for '): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (15, 'Conducting field experiments using eLanc'): ('Research Methodology', 'Methodology / Philosophy'),
        (18, 'Crowdfunding in a Prosocial Microlending'): ('Affect Theory', 'Psychology'),
        (22, 'Crafting Business Architecture: The Ant'): ('Business Model Theory', 'Management / Strategy'),
        (26, 'The effect of entrepreneurial rhetoric o'): ('Behavioral Economics; Framing Theory', 'Economics; Psychology'),
        (27, 'Persuasion in crowdfunding: An elaborati'): ('Framing Theory', 'Psychology'),
        (29, 'The Chicken or the Egg? Causal Inference'): ('Research Methodology', 'Methodology / Philosophy'),
        (36, 'Spawned by Opportunity or Out of Neces'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (37, 'Factors That Influence the Business Succ'): ('Systems Theory; Entrepreneurship Theory (General)', 'Organizational Theory; Entrepreneurship-Specific'),
        (43, 'Technology ventures\' engagement of exter'): ('Human Capital Theory', 'Economics'),
        (47, 'Measuring Enterprise Potential in Young '): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (70, 'Communities at the nexus of entrepreneur'): ('Social Capital Theory; Entrepreneurship Theory (General)', 'Entrepreneurship-Specific; Sociology'),
        (81, 'A New Methodology for Aggregating Tables'): ('Research Methodology', 'Methodology / Philosophy'),
        (97, 'Attitudes of Owner-Managers\' Children To'): ('Family Business Theory', 'Entrepreneurship-Specific'),
        (98, 'Do Women Entrepreneurs Require Different'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (100, 'A quantitative content analysis of the c'): ('Strategic Management', 'Management / Strategy'),
        (106, 'Are Family Firms Doing More Innovation O'): ('Innovation Theory; Research Methodology', 'Entrepreneurship-Specific; Methodology / Philosophy'),
        (106, 'A quantitative content analysis of the c'): ('Strategic Management; International Entrepreneurship', 'Entrepreneurship-Specific; Management / Strategy'),
        (107, 'General managers control new and existin'): ('Strategic Management', 'Management / Strategy'),
        (110, 'Cultures of success: Characteristics of '): ('Leadership Theory; International Entrepreneurship', 'Entrepreneurship-Specific'),
        (114, 'Unpacking the Nature of Orchestrator Coh'): ('Entrepreneurial Ecosystem', 'Entrepreneurship-Specific'),
        (124, 'The Cost of Equity Capital for Small Bus'): ('Portfolio Theory', 'Finance'),
        (129, 'Validation of a didactic model for the a'): ('Strategic Management', 'Management / Strategy'),
        (131, 'Using Founder Status, Age of Firm, and C'): ('Research Methodology', 'Methodology / Philosophy'),
        (145, 'A fresh look at patterns and assumptio'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (150, 'Private business sales environments in t'): ('Cultural Theory; Entrepreneurial Ecosystem', 'Entrepreneurship-Specific; Sociology'),
        (152, 'Exploring the Heart: Entrepreneurial Emo'): ('Affect Theory', 'Psychology'),
        (153, 'Motivational Cues and Angel Investing: I'): ('Affect Theory; Signaling Theory', 'Psychology; Finance'),
        (159, 'What is scaling?'): ('Research Methodology', 'Methodology / Philosophy'),
        (177, 'University revenues from technology tran'): ('Innovation Theory; Strategic Management', 'Management / Strategy'),
        (182, 'Entrepreneurial judgment governance ad'): ('Sensemaking Theory', 'Organizational Theory'),
        (183, 'Opportunity creation: Entrepreneurial'): ('Opportunity Theory; Social Network Theory', 'Entrepreneurship-Specific; Sociology'),
        (195, 'In Pursuit of Impact: From Research Ques'): ('Research Methodology', 'Methodology / Philosophy'),
        (198, 'Defining the field of research in entrep'): ('Philosophy of Science; Entrepreneurship Theory (General)', 'Entrepreneurship-Specific; Methodology / Philosophy'),
        (200, 'Social class origin and entrepreneurship'): ('Social Capital Theory', 'Sociology'),
        (227, 'Work-Family Conflict and Microfinance'): ('Organizational Justice', 'Organizational Theory'),
        (234, 'A study of the impact of owner\'s mode of'): ('International Entrepreneurship; Strategic Management', 'Entrepreneurship-Specific; Management / Strategy'),
        (237, 'How images and color in business plans i'): ('Process Theory', 'Organizational Theory'),
        (237, 'Time to Unicorn Status: An Exploratory'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (247, 'Social entrepreneurship as emancipatory '): ('Social Entrepreneurship; Human Capital Theory', 'Economics; Entrepreneurship-Specific'),
        (249, 'The relationship between prior and'): ('Entrepreneurship Theory (General); Institutional Theory; Social Network Theory', 'Entrepreneurship-Specific; Sociology'),
        (251, 'Waves and rips: Abalone, entrepreneurial'): ('Opportunity Theory; Sustainable Entrepreneurship', 'Entrepreneurship-Specific'),
        (258, 'The Power and Effects of Entrepreneurshi'): ('Research Methodology', 'Methodology / Philosophy'),
        (261, 'External enablement of new venture crea'): ('Entrepreneurial Ecosystem', 'Entrepreneurship-Specific'),
        (268, 'Is microcredit a blessing for the poor'): ('Human Capital Theory; Resource-Based View; Well-Being Theory', 'Economics; Management / Strategy; Psychology'),
        (269, 'Social entrepreneurship as an essentia'): ('Philosophy of Science', 'Methodology / Philosophy'),
        (273, 'Entrepreneurial Studies: The Dynamic Res'): ('Research Methodology', 'Methodology / Philosophy'),
        (275, 'Organizational Entrepreneurship as Activ'): ('Corporate Entrepreneurship', 'Entrepreneurship-Specific'),
        (277, 'Foreign Market Entry and Internationaliz'): ('International Entrepreneurship', 'Entrepreneurship-Specific'),
        (286, 'Bank lending to new and growing enterp'): ('Entrepreneurial Finance', 'Finance'),
        (289, 'Entrepreneurs meet financiers: Evidenc'): ('Labor Economics; Venture Capital Theory', 'Economics; Finance'),
        (292, 'Dutch Druggists in Distress: Franchisees'): ('Family Business Theory', 'Entrepreneurship-Specific'),
        (298, 'National Rates of Opportunity Entreprene'): ('Institutional Theory', 'Institutional Theory'),
        (306, 'Strategic Issues Management in the Commu'): ('Strategic Management', 'Management / Strategy'),
        (310, 'Third World Joint Venturing: A Strategic'): ('International Entrepreneurship', 'Entrepreneurship-Specific'),
        (310, 'Determinants of Satisfaction for Entre'): ('Motivation Theory', 'Psychology'),
        (317, 'In the Mood for Entrepreneurial Creati'): ('Creativity Theory', 'Psychology'),
        (320, 'Time and Entrepreneurial Risk Behavior'): ('Decision Theory; Prospect Theory', 'Psychology; Economics'),
        (320, 'An Investigation of Marketing Practice'): ('Competitive Strategy; Strategic Management', 'Management / Strategy'),
        (323, 'The Impact of Electric Rates on Small Bu'): ('Cost-Benefit Analysis', 'Economics'),
        (324, 'Debt, Liquidity, and Profitability Probl'): ('Capital Structure Theory', 'Finance'),
        (325, 'Ditching Discovery-Creation for Unified '): ('Effectuation Theory; Structuration Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (326, 'Much Ado About Nothing? The Surprising P'): ('Escalation of Commitment', 'Psychology'),
        (334, 'Opportunities for Small Business in Thir'): ('Competitive Strategy', 'Management / Strategy'),
        (335, 'Predictors of Later-Generation Family Me'): ('Family Business Theory', 'Entrepreneurship-Specific'),
        (337, 'Advancing a Framework for Coherent Resea'): ('Research Methodology', 'Methodology / Philosophy'),
        (337, 'The evolution of craft work in the stra'): ('Practice Theory', 'Sociology'),
        (341, 'Para-Social Mentoring: The Effects of '): ('Entrepreneurial Learning; Leadership Theory', 'Entrepreneurship-Specific; Management / Strategy'),
        (341, 'The pre-commercialization emergence of'): ('Dominant Coalition Theory; Innovation Theory', 'Organizational Theory'),
        (342, 'A Profile of New Venture Success and F'): ('Entrepreneurship Theory (General); Strategic Management', 'Entrepreneurship-Specific; Management / Strategy'),
        (346, 'Sector-Based Entrepreneurial Capabilitie'): ('Entrepreneurial Orientation', 'Entrepreneurship-Specific'),
        (347, 'Bank Involvement with Export Trading Com'): ('Institutional Theory', 'Institutional Theory'),
        (354, 'The Past, Present, and Future of Entrepr'): ('Research Methodology', 'Methodology / Philosophy'),
        (360, 'The Chances of Financial Success (and Lo'): ('Opportunity Theory', 'Entrepreneurship-Specific'),
        (364, 'Personal strain and ethical standards'): ('Stress and Coping Theory', 'Psychology'),
        (364, 'A sense of risk: Responses to crowdfun'): ('Cognitive Psychology; Entrepreneurial Finance', 'Psychology; Finance'),
        (372, 'The fallacy of \'only the strong surviv'): ('Escalation of Commitment; Motivation Theory', 'Psychology'),
        (374, 'Critical Success Factors and Small Busin'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (374, 'The project-management approach in the'): ('Innovation Theory; Strategic Management', 'Organizational Theory; Management / Strategy'),
        (385, 'Religion and Enterprise: An Introductory'): ('Cultural Theory; Resource Scarcity Theory', 'Sociology; Entrepreneurship-Specific'),
        (385, 'More than you think: An inclusive esti'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (386, 'The Role of Negative Emotions in the Soc'): ('Social Network Theory', 'Sociology'),
        (387, 'Do others think you have a viable busi'): ('Social Identity Theory; Social Network Theory', 'Sociology'),
        (401, 'Metaphors and meaning: A grounded cult'): ('Cultural Theory; Narrative Theory', 'Sociology'),
        (405, 'The Critical Incident Method, An Overloo'): ('Research Methodology', 'Methodology / Philosophy'),
        (411, 'Growth pattern of academic entrepreneur'): ('Entrepreneurship Theory (General); Innovation Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (413, 'Toward a Theory of Entrepreneurial Caree'): ('Entrepreneurial Orientation; Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (421, 'Entrepreneurship and the initial size '): ('Entrepreneurship Theory (General); Organizational Life Cycle', 'Entrepreneurship-Specific'),
        (422, 'Planning for Growth: Life Stage Differen'): ('Family Business Theory; Organizational Life Cycle', 'Entrepreneurship-Specific; Organizational Theory'),
        (427, 'Financial Leverage Analysis for Small Bu'): ('Capital Structure Theory', 'Finance'),
        (432, 'Industry changes in technology and com'): ('Innovation Theory; Resource-Based View', 'Organizational Theory; Management / Strategy'),
        (434, 'Social insurance and entrepreneurship:'): ('Institutional Economics', 'Economics'),
        (436, 'The Value Orientations of Minority and N'): ('Organizational Identity; Contingency Theory', 'Organizational Theory'),
        (443, 'Developing theoretical insights in ent'): ('Philosophy of Science', 'Methodology / Philosophy'),
        (448, 'Residential Segregation Influences on th'): ('Resource Scarcity Theory; Social Influence Theory', 'Entrepreneurship-Specific; Psychology'),
        (453, 'How venture capital firms differ'): ('Venture Capital Theory', 'Finance'),
        (454, 'Volunteer Retention in Prosocial Venturi'): ('Social Entrepreneurship; Organizational Design', 'Entrepreneurship-Specific; Organizational Theory'),
        (472, 'Personal value systems of men and wom'): ('Feminist Theory; Personality Psychology', 'Sociology; Psychology'),
        (474, 'Residential segregation influences on '): ('International Entrepreneurship; Social Identity Theory', 'Entrepreneurship-Specific; Sociology'),
        (475, 'A Marketing Strategy Analysis of Small R'): ('Competitive Strategy', 'Management / Strategy'),
        (475, 'The influence of residential segregati'): ('International Entrepreneurship; Social Identity Theory', 'Entrepreneurship-Specific; Sociology'),
        (477, 'NAFTA and franchising: A comparison of'): ('Institutional Economics; International Entrepreneurship', 'Economics; Entrepreneurship-Specific'),
        (481, 'Entrepreneurship in the Agricultural Sec'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (484, 'Emotions and Entrepreneurial Opportunity'): ('Affect Theory; Entrepreneurial Cognition', 'Psychology; Entrepreneurship-Specific'),
        (484, 'Incubators and performance: A compariso'): ('Entrepreneurial Ecosystem; Organizational Learning', 'Entrepreneurship-Specific; Organizational Theory'),
        (489, 'The Potential Value of Leasing'): ('Capital Structure Theory', 'Finance'),
        (493, '2D:4D and Self-Employment: A Preregister'): ('Behavioral Genetics', 'Psychology'),
        (494, 'Friendship within Entrepreneurial Teams '): ('Social Capital Theory; Entrepreneurial Action Theory', 'Entrepreneurship-Specific; Sociology'),
        (501, 'How Crowdfunders Are Influenced by Entre'): ('Bounded Rationality; Affect Theory', 'Psychology'),
        (505, 'Venture Capital Research: Past, Present '): ('Venture Capital Theory; Resource Dependence Theory', 'Finance; Organizational Theory'),
        (509, 'The Role of Incubators in Small Business'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (510, 'How Can Problems Be Turned Into Somethin'): ('Self-Regulation Theory; Stress and Coping Theory', 'Psychology'),
        (515, 'Impact of SME Manager\'s Behavior on the '): ('Entrepreneurial Orientation', 'Entrepreneurship-Specific'),
        (520, 'How International is Entrepreneurship?'): ('Research Methodology', 'Methodology / Philosophy'),
        (523, 'Angels and non-angels: Are there diffe'): ('Venture Capital Theory', 'Finance'),
        (524, 'Defining a forum for entrepreneurship '): ('Philosophy of Science; Research Methodology', 'Methodology / Philosophy'),
        (528, 'Is There an Elephant in Entrepreneurship'): ('Opportunity Theory', 'Entrepreneurship-Specific'),
        (529, 'Obsessive passion and the venture team'): ('Passion Theory; Social Exchange Theory', 'Psychology; Sociology'),
        (532, 'Star entrepreneurs on digital platform'): ('Social Status Theory', 'Sociology'),
        (538, 'What are we talking about when we talk'): ('Philosophy of Science', 'Methodology / Philosophy'),
        (543, 'Predicting new venture survival: An a'): ('Organizational Life Cycle', 'Organizational Theory'),
        (546, 'Rags to riches? Entrepreneurs\' social'): ('Social Capital Theory; Social Status Theory', 'Sociology'),
        (548, 'International Entrepreneurship: The Stat'): ('International Entrepreneurship', 'Entrepreneurship-Specific'),
        (550, 'Motives and Outcomes in Family Business '): ('Family Business Theory', 'Entrepreneurship-Specific'),
        (554, 'An Intergeneration Solidarity Perspectiv'): ('Family Business Theory; Social Capital Theory', 'Entrepreneurship-Specific; Sociology'),
        (555, 'A temporal analysis of how entrepren'): ('Goal-Setting Theory; Theory of Planned Behavior', 'Psychology'),
        (564, 'Characteristics of Minority Entrepreneur'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (565, 'The Social Responsibility of Minority-Ow'): ('Social Entrepreneurship; Stakeholder Theory', 'Entrepreneurship-Specific; Management / Strategy'),
        (566, 'Bank strategies toward firms in declin'): ('Corporate Governance; Strategic Management', 'Management / Strategy'),
        (567, 'Institutional lending to knowledge-ba'): ('Entrepreneurial Finance; Knowledge-Based View', 'Finance; Management / Strategy'),
        (570, 'Academics\' organizational characterist'): ('Institutional Entrepreneurship; Innovation Theory', 'Institutional Theory; Organizational Theory'),
        (574, 'KenKen: The Wisdom Squared of Puzzling B'): ('Business Model Theory', 'Entrepreneurship-Specific'),
        (575, 'Whitetracks Design, Inc.'): ('Entrepreneurial Exit Theory', 'Entrepreneurship-Specific'),
        (591, 'Gender differences in evaluation of ne'): ('Social Identity Theory', 'Sociology'),
        (600, 'Work hard or play hard: The effect of'): ('Self-Determination Theory; Well-Being Theory', 'Psychology'),
        (601, 'Determinants of the round-to-round re'): ('Venture Capital Theory', 'Finance'),
        (606, 'Towards a theory of entrepreneurial t'): ('Leadership Theory; Social Network Theory', 'Management / Strategy; Sociology'),
        (608, 'International perspectives on the supp'): ('International Entrepreneurship; Venture Capital Theory', 'Entrepreneurship-Specific; Finance'),
        (612, 'Strategic windows in the entrepreneuri'): ('Strategic Entrepreneurship', 'Entrepreneurship-Specific'),
        (614, 'Goal achievement and satisfaction of'): ('Goal-Setting Theory; Strategic Alliance Theory', 'Psychology; Management / Strategy'),
        (624, 'Technology Transfer to Minority Business'): ('Knowledge Spillover Theory; Innovation Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (624, 'Self-employment and work-related stre'): ('Stress and Coping Theory', 'Psychology'),
        (629, 'Variations in university entrepreneursh'): ('Entrepreneurial Ecosystem; Entrepreneurial Learning', 'Entrepreneurship-Specific'),
        (631, 'Intuition in venture capital decisions'): ('Entrepreneurial Cognition', 'Entrepreneurship-Specific'),
        (648, 'The pricing of successful venture capi'): ('Venture Capital Theory', 'Finance'),
        (652, 'Entrepreneurial exit intentions and t'): ('Entrepreneurial Exit Theory; Family Business Theory', 'Entrepreneurship-Specific'),
        (654, 'Business founders\' work design and new'): ('Entrepreneurship Theory (General); Self-Regulation Theory', 'Entrepreneurship-Specific; Psychology'),
        (656, 'Examining Psychological Mediators in Ent'): ('Research Methodology', 'Methodology / Philosophy'),
        (657, 'Visual totality of rewards-based crowd'): ('Entrepreneurial Finance', 'Finance'),
        (659, 'Acquiring financial resources from for'): ('Entrepreneurial Finance; International Entrepreneurship', 'Finance; Entrepreneurship-Specific'),
        (660, 'Factors affecting equity capital acqui'): ('Entrepreneurial Finance', 'Finance'),
        (664, 'Improving new venture performance: The'): ('Strategic Management', 'Management / Strategy'),
        (665, 'Entrepreneurial Masculinity: A Fatherhoo'): ('Feminist Theory; Entrepreneurship Theory (General)', 'Sociology; Entrepreneurship-Specific'),
        (666, 'Ex Ante Predictability of Rapid Growth: '): ('Research Methodology', 'Methodology / Philosophy'),
        (667, 'Entrepreneurial Responsibility: A Concep'): ('Philosophy of Science', 'Methodology / Philosophy'),
        (669, 'Perceived Causes of Success in Small Bus'): ('Personality Psychology; Entrepreneurship Theory (General)', 'Psychology; Entrepreneurship-Specific'),
        (671, 'Entrepreneurship and Small Business Rese'): ('Research Methodology', 'Methodology / Philosophy'),
        (683, 'Japanese entrepreneurs and corporate m'): ('Entrepreneurship Theory (General); International Entrepreneurship', 'Entrepreneurship-Specific'),
        (686, 'Individual responses to firm failure: '): ('Stress and Coping Theory', 'Psychology'),
        (687, 'Living the Dream? Assessing the \'Entrepr'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (693, 'A Recombinant Framework of Technological'): ('Innovation Theory; Complexity Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (694, 'A woman\'s place is in the... startup!'): ('Feminist Theory; Social Identity Theory', 'Sociology'),
        (698, 'International Entrepreneurship research'): ('Research Methodology', 'Methodology / Philosophy'),
        (699, 'New technologies and technological inf'): ('Innovation Theory', 'Organizational Theory'),
        (700, 'Entrepreneurship for Sustainable Develop'): ('Sustainable Entrepreneurship', 'Entrepreneurship-Specific'),
        (701, 'Small Business Commercial Loan Selection'): ('Decision Theory', 'Economics'),
        (715, 'New product development process: An i'): ('Innovation Theory; Strategic Management', 'Organizational Theory; Management / Strategy'),
        (717, 'Entrepreneurial Teams in New Venture Cre'): ('Entrepreneurial Action Theory', 'Entrepreneurship-Specific'),
        (720, 'The chronology and intellectual trajec'): ('Philosophy of Science; Research Methodology', 'Methodology / Philosophy'),
        (723, 'Franchising and the domain of entrepre'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (724, 'Standardization and adaptation in busi'): ('Contingency Theory; Strategic Management', 'Organizational Theory; Management / Strategy'),
        (726, 'A Comparative Study of Entrepreneurship '): ('Entrepreneurial Cognition', 'Entrepreneurship-Specific'),
        (729, 'Endowed Positions: Entrepreneurship and '): ('Institutional Theory', 'Institutional Theory'),
        (731, 'Reaching out or going it alone? How b'): ('Social Network Theory', 'Sociology'),
        (732, 'A Psychosocial Cognitive Model of Employ'): ('Bounded Rationality; Cognitive Psychology', 'Psychology; Economics'),
        (738, 'Entrepreneurial Dimensions: The Relation'): ('Entrepreneurial Orientation; Contingency Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (748, 'The entrepreneur\'s character, life iss'): ('Personality Psychology', 'Psychology'),
        (757, 'Fail but Try Again? The Effects of Age, '): ('Occupational Choice Theory; Personality Psychology', 'Psychology'),
        (772, 'Researching Small Firms and Entrepreneur'): ('Research Methodology; Philosophy of Science', 'Methodology / Philosophy'),
        (774, 'Applying the Community Development Corpo'): ('Systems Theory', 'Organizational Theory'),
        (779, 'Separated by a Common Language? Entrepre'): ('Organizational Design', 'Organizational Theory'),
        (792, 'Prediction of failure of a newly found'): ('Organizational Life Cycle', 'Organizational Theory'),
        (793, 'Informal risk capital in Sweden and s'): ('Venture Capital Theory', 'Finance'),
        (804, 'The Social Dynamics of Entrepreneurship'): ('Social Network Theory; Complexity Theory', 'Sociology; Organizational Theory'),
        (809, 'Pandemic Depression: COVID-19 and the Me'): ('Stress and Coping Theory; Well-Being Theory', 'Psychology'),
        (825, 'Gray marketing as an alternative marke'): ('Competitive Strategy', 'Management / Strategy'),
        (836, 'The Management of Growth: An Entrepreneu'): ('Organizational Life Cycle', 'Organizational Theory'),
        (841, '\'Who Is an Entrepreneur?\' Is the Wrong Q'): ('Entrepreneurial Action Theory', 'Entrepreneurship-Specific'),
        (844, 'The effect of aging on entrepreneurial'): ('Personality Psychology', 'Psychology'),
        (854, 'The Impact of Managerial Attitudes on Ex'): ('Entrepreneurial Orientation; International Entrepreneurship', 'Entrepreneurship-Specific'),
        (857, 'What\'s in a logo? The impact of compl'): ('Signaling Theory', 'Economics'),
        (858, 'The role of venture capital in financi'): ('Venture Capital Theory', 'Finance'),
        (874, 'External Enablers of Entrepreneurship: A'): ('Entrepreneurial Ecosystem', 'Entrepreneurship-Specific'),
        (876, 'Technical Consultancy in Hungary, Poland'): ('Opportunity Theory; Knowledge Spillover Theory', 'Entrepreneurship-Specific'),
        (883, 'Is it worth it? The rates of return fr'): ('Venture Capital Theory', 'Finance'),
        (889, 'A comparison of Japanese and U.S. fir'): ('International Entrepreneurship; IPO Theory', 'Entrepreneurship-Specific; Finance'),
        (893, 'Business angel early stage decision mak'): ('Decision Theory', 'Economics'),
        (896, 'International versus domestic entrepre'): ('International Entrepreneurship', 'Entrepreneurship-Specific'),
        (904, 'Exploring Perceptions of A Priori Barrie'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (911, 'An Audience Analysis of Inner City Black'): ('Impression Management', 'Psychology'),
        (913, 'A temporal typology of entrepreneurial'): ('Opportunity Theory; Process Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (921, 'How entrepreneurial intentions influenc'): ('Theory of Planned Behavior', 'Psychology'),
        (925, 'The Social Imaginary of Emancipation in '): ('Philosophy of Science', 'Methodology / Philosophy'),
        (926, 'Mapping the Field of Research on Entrepr'): ('Research Methodology', 'Methodology / Philosophy'),
        (928, 'The commons: A model for understanding'): ('Collective Action Theory', 'Sociology'),
        (930, 'Assessing and managing the university '): ('Institutional Entrepreneurship; Knowledge-Based View', 'Institutional Theory; Management / Strategy'),
        (931, 'The Nature and Focus of Entrepreneurship'): ('Research Methodology', 'Methodology / Philosophy'),
        (933, 'Participative Management in the Small Fi'): ('Organizational Design', 'Organizational Theory'),
        (942, 'Toward an Integrative Model of Effective'): ('Family Business Theory', 'Entrepreneurship-Specific'),
        (948, 'Productivity in the Small Business Secto'): ('Evolutionary Economics', 'Economics'),
        (948, 'Defining the inventor-entrepreneur in '): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (952, 'Nothing Ventured, Nothing Gained: Parasi'): ('Behavioral Genetics', 'Psychology'),
        (955, 'Angel investor characteristics that det'): ('Venture Capital Theory', 'Finance'),
        (969, 'Partnerships as an enabler of resourcef'): ('Bricolage Theory; Social Network Theory', 'Entrepreneurship-Specific; Sociology'),
        (972, 'Forecasting the liquidity of very small'): ('Entrepreneurial Finance', 'Finance'),
        (979, 'Hot Markets, Sociocognitive Cues, and Ne'): ('Effectuation Theory; Social Cognitive Theory', 'Entrepreneurship-Specific; Psychology'),
        (987, 'Facing the future through entrepreneurship'): ('Philosophy of Science', 'Methodology / Philosophy'),
        (989, 'The effect of a tax training program o'): ('Institutional Economics', 'Economics'),
        (990, 'Screening Practices of New Business Incu'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (994, 'Images of Entrepreneurship: Exploring Ro'): ('Human Capital Theory', 'Economics'),
        (995, 'Funding-source-induced bias: How socia'): ('Social Capital Theory; Social Network Theory', 'Sociology'),
        (997, 'Atypical entrepreneurs in the venture '): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1007, 'Switching to self-employment can be go'): ('Well-Being Theory', 'Psychology'),
        (1018, 'A conceptual framework for entrepreneurship'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1025, 'Actions in words: How entrepreneurs us'): ('Narrative Theory', 'Sociology'),
        (1029, 'Do we understand each other? Toward a'): ('Entrepreneurial Cognition', 'Entrepreneurship-Specific'),
        (1031, 'Computers in Small Business: A Case of U'): ('Strategic Management', 'Management / Strategy'),
        (1032, 'Sounds novel or familiar? Entrepreneur'): ('Framing Theory', 'Psychology'),
        (1035, 'How venture capitalists respond to unm'): ('Venture Capital Theory', 'Finance'),
        (1040, 'Personnel Practices in Smaller Firms: A '): ('Resource-Based View', 'Management / Strategy'),
        (1042, 'A New Approach to Capital Budgeting in C'): ('Human Capital Theory', 'Economics'),
        (1047, 'Communicating During Societal Crises: Ho'): ('Strategic Management', 'Management / Strategy'),
        (1049, 'Growth and Financial Profiles Amongst Ma'): ('Strategic Management', 'Management / Strategy'),
        (1051, 'Perceived project transition support a'): ('Organizational Learning; Stress and Coping Theory', 'Organizational Theory; Psychology'),
        (1058, 'Entrepreneurial recovery strategies of'): ('Strategic Entrepreneurship', 'Entrepreneurship-Specific'),
        (1059, 'Navigating a Sea of Change: Identity Mis'): ('Identity Theory', 'Sociology'),
        (1063, 'One Path Does Not Fit All: A Career Path'): ('Identity Theory', 'Sociology'),
        (1076, 'Labor Productivity in Large and Small En'): ('Strategic Management', 'Management / Strategy'),
        (1076, 'The prediction of bankruptcy of small-'): ('Organizational Life Cycle', 'Organizational Theory'),
        (1091, 'The expectations game: The contingent'): ('Narrative Theory', 'Sociology'),
        (1098, 'A meta-analysis of different HR-enhanc'): ('Organizational Learning', 'Organizational Theory'),
        (1112, 'Co-production of business assistance i'): ('Organizational Learning', 'Organizational Theory'),
        (1122, 'The Differential Impact of Taxes on Inve'): ('Resource-Based View', 'Management / Strategy'),
        (1125, 'Exit, stage left: Why entrepreneurs en'): ('Entrepreneurial Exit Theory', 'Entrepreneurship-Specific'),
        (1134, 'Predictors of success in new technology'): ('Innovation Theory; Strategic Management', 'Organizational Theory; Management / Strategy'),
        (1141, 'The Impact of Consulting on Small Busine'): ('Strategic Management', 'Management / Strategy'),
        (1142, 'Capital market myopia'): ('Behavioral Finance', 'Finance'),
        (1144, 'Digital Entrepreneurship: Toward a Digit'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1172, 'Entrepreneurship: Process and Abilities'): ('Cognitive Psychology; Process Theory', 'Organizational Theory; Psychology'),
        (1178, 'Exoskeletons, entrepreneurs, and commu'): ('Opportunity Theory; Social Network Theory', 'Entrepreneurship-Specific; Sociology'),
        (1179, 'An examination of the relationship bet'): ('Feminist Theory; Self-Efficacy Theory', 'Sociology; Psychology'),
        (1180, 'The CAGE around cyberspace? How digita'): ('International Entrepreneurship; Innovation Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (1190, 'Encouraging university entrepreneurshi'): ('Institutional Entrepreneurship; Innovation Theory', 'Institutional Theory; Organizational Theory'),
        (1210, 'Government Discourses on Entrepreneurshi'): ('Strategic Management', 'Management / Strategy'),
        (1231, 'The Dark Side of Entrepreneurs\' Creativi'): ('Human Capital Theory', 'Economics'),
        (1242, 'East Indian Small Businesses in the U.S.'): ('Strategic Management', 'Management / Strategy'),
        (1242, 'Creating the technopolis: High-technolo'): ('Cluster Theory; Regional Economics', 'Sociology; Economics'),
        (1243, 'University spin-out companies: Technolo'): ('Innovation Theory; Institutional Entrepreneurship', 'Organizational Theory; Institutional Theory'),
        (1244, 'Decision making behavior in smaller ent'): ('Decision Theory', 'Economics'),
        (1255, 'The artisans\' dilemma: Artisan entrepre'): ('Practice Theory', 'Sociology'),
        (1263, 'Habitual entrepreneurs: Possible cases'): ('Behavioral Theory of the Firm', 'Management / Strategy'),
        (1269, 'Colas, burgers, shakes, and shirkers: T'): ('Cultural Theory', 'Sociology'),
        (1278, 'Successful intelligence as a basis for'): ('Personality Psychology', 'Psychology'),
        (1280, 'Knocking at the gate: The path to publi'): ('Research Methodology', 'Methodology / Philosophy'),
        (1281, 'Out of control or right on the money?:'): ('Self-Efficacy Theory; Venture Capital Theory', 'Psychology; Finance'),
        (1288, 'Jacks-(and Jills)-of-all-trades: On whe'): ('Feminist Theory; Occupational Choice Theory', 'Sociology; Economics'),
        (1289, 'Start-up ventures: Towards the predicti'): ('Organizational Life Cycle', 'Organizational Theory'),
        (1299, 'Researching Small Firms and Entrepreneur'): ('Research Methodology', 'Methodology / Philosophy'),
        (1307, 'Mortgage affordability and entrepreneurship'): ('Entrepreneurial Finance', 'Finance'),
        (1324, 'The Corridor Principle'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1330, 'Progress without a venture? Individual'): ('Well-Being Theory', 'Psychology'),
        (1333, '\'Who Is an Entrepreneur?\' Is the Wrong Q'): ('Entrepreneurial Cognition; Process Theory', 'Entrepreneurship-Specific; Organizational Theory'),
        (1359, 'How cultural tightness interacts with'): ('Cultural Theory; Feminist Theory', 'Sociology'),
        (1364, 'The Changing Role of Social Capital Duri'): ('Contingency Theory', 'Organizational Theory'),
        (1372, 'Goal Programming for Decision Making in '): ('Research Methodology; Systems Theory; Bounded Rationality', 'Economics; Methodology / Philosophy; Organizational Theory'),
        (1376, 'Microcomputers and the SBI Program'): ('Strategic Management', 'Management / Strategy'),
        (1377, 'Nothing Ventured, Nothing Gained: Parasi'): ('Personality Psychology', 'Psychology'),
        (1379, 'Business accomplishments, gender and e'): ('Feminist Theory', 'Sociology'),
        (1407, 'Adjusting for risk in comparing the per'): ('Entrepreneurial Finance; Strategic Management', 'Finance; Management / Strategy'),
        (1420, 'A typology of new manufacturing firm f'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1423, 'The informal venture capital market: As'): ('Venture Capital Theory', 'Finance'),
        (1427, 'DUPLICATE of paper 1426'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1428, 'Operations Management and Financial Perf'): ('Strategic Management', 'Management / Strategy'),
        (1434, 'Strategic versus Operational Planning in'): ('Strategic Management', 'Management / Strategy'),
        (1436, 'The Human Resource Factor in Small Busin'): ('Strategic Management', 'Management / Strategy'),
        (1437, 'Organization Principles and Financial Me'): ('Strategic Management', 'Management / Strategy'),
        (1439, 'Financial bootstrapping in small busine'): ('Entrepreneurial Finance', 'Finance'),
        (1442, 'Venture capital investing for corporat'): ('Corporate Entrepreneurship; Venture Capital Theory', 'Entrepreneurship-Specific; Finance'),
        (1444, 'Entrepreneurial Processes as Virtuous an'): ('Grounded Theory', 'Methodology / Philosophy'),
        (1444, 'The development and interpretation of'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1445, 'Entrepreneurial Processes of Business Cl'): ('Strategic Management', 'Management / Strategy'),
        (1446, 'Gender and Ownership in UK Small Firms'): ('Strategic Management', 'Management / Strategy'),
        (1450, 'Venture capital and management-led, lev'): ('Venture Capital Theory', 'Finance'),
        (1454, 'The pricing of a brand name product: F'): ('Signaling Theory', 'Economics'),
        (1479, 'Firm-Level Entrepreneurship and Field Re'): ('Research Methodology', 'Methodology / Philosophy'),
        (1483, 'A lack of insight: Do venture capitali'): ('Venture Capital Theory', 'Finance'),
        (1484, 'Entrepreneurial Fraud: A Multidisciplina'): ('Strategic Management', 'Management / Strategy'),
        (1503, 'Rule breaking in adolescence and entrep'): ('Personality Psychology', 'Psychology'),
        (1515, 'Risk Management for the Small Importer-E'): ('Strategic Management', 'Management / Strategy'),
        (1520, 'The Informational Needs Of The Small Fir'): ('Information Economics', 'Economics'),
        (1523, 'Transnational Entrepreneurship: Determin'): ('Strategic Management', 'Management / Strategy'),
        (1541, 'The Lean Startup Framework: Closing the '): ('Effectuation Theory', 'Entrepreneurship-Specific'),
        (1551, 'Entrepreneurship and Poverty Alleviation'): ('Push-Pull Theory', 'Entrepreneurship-Specific'),
        (1559, 'Credit Strategy in Small and Large Compa'): ('Transaction Cost Economics', 'Economics'),
        (1582, 'Time, Growth, Complexity, and Transition'): ('Strategic Management', 'Management / Strategy'),
        (1587, 'Selecting Methodologies for Entrepreneur'): ('Research Methodology', 'Methodology / Philosophy'),
        (1593, 'Management Training In Small Business'): ('Strategic Management', 'Management / Strategy'),
        (1594, 'Trends in Small Business Management and '): ('Research Methodology', 'Methodology / Philosophy'),
        (1597, 'An Attitudinal Comparison of Black and W'): ('Social Identity Theory', 'Sociology'),
        (1604, 'Estimates of The Number of Quasi and Sma'): ('Strategic Management', 'Management / Strategy'),
        (1608, 'Shouting From the Ivory Tower: A Marketi'): ('Framing Theory', 'Psychology'),
        (1619, 'A Prospectus on the Anthropology of Entr'): ('Research Methodology', 'Methodology / Philosophy'),
        (1620, 'Help One Another, Use One Another: Towar'): ('Research Methodology', 'Methodology / Philosophy'),
        (1633, 'A Comparison of Insurance and Pension Pl'): ('Strategic Management', 'Management / Strategy'),
        (1649, 'Transnational Entrepreneurs\' Venture Int'): ('Resource-Based View', 'Management / Strategy'),
        (1654, 'Training Needs Of Managers Of Small Manu'): ('Strategic Management', 'Management / Strategy'),
        (1655, 'Britain\'s Efforts to Stimulate Productiv'): ('Innovation Theory', 'Management / Strategy'),
        (1677, 'Increasing the Advertising Effectiveness'): ('Behavioral Economics', 'Economics'),
        (1682, 'Entrepreneurship and Black Capitalism'): ('Strategic Management', 'Management / Strategy'),
        (1686, 'Entrepreneurial Team Development in Acad'): ('Upper Echelons Theory', 'Management / Strategy'),
        (1706, 'Unlisted Businesses are Not Financial Cl'): ('Resource-Based View', 'Management / Strategy'),
        (1726, 'Varieties of Necessity Entrepreneurship:'): ('Push-Pull Theory', 'Entrepreneurship-Specific'),
        (1727, 'A Long-Run Product Diversification Growt'): ('Strategic Management', 'Management / Strategy'),
        (1742, 'Accounting and Marketing—Key Small Busin'): ('Strategic Management', 'Management / Strategy'),
        (1760, 'Using O*Net to Study the Intersection of'): ('Entrepreneurship Theory (General)', 'Entrepreneurship-Specific'),
        (1782, 'The Creation and Configuration of Infras'): ('Entrepreneurial Ecosystem; Innovation Theory', 'Entrepreneurship-Specific; Management / Strategy'),
        (1789, 'Editors\' Introduction: Habitual Entrepre'): ('Strategic Management', 'Management / Strategy'),
        (1801, 'Information Source Selection Patterns as'): ('Information Processing Theory', 'Organizational Theory'),
        (1825, 'Missing the Forest for the Trees: Prior '): ('Identity Theory', 'Sociology'),
        (1830, 'The Role of Stereotype Threat, Anxiety, '): ('Social Identity Theory', 'Sociology'),
        (1836, 'Entrepreneurial Networking During Early '): ('Learning Theory', 'Organizational Theory'),
        (1848, 'Creating the Future Together: Toward a F'): ('Research Methodology', 'Methodology / Philosophy'),
        (1849, 'Digital Technologies as External Enabler'): ('Entrepreneurial Ecosystem; Effectuation Theory; Process Theory', 'Entrepreneurship-Specific; Organizational Theory'),
    }

    # ── Apply to all papers ──
    df['std_theory_L1_discipline'] = ''
    df['std_theory_L2_name'] = ''

    skip_values = {'DUPLICATE', 'N/A', 'NON-RESEARCH', 'FILE NOT FOUND', 'OCR FAILED',
                   'NON-RESEARCH (editorial)', 'RETRACTED'}

    for idx in df.index:
        raw = df.at[idx, 'theoretical_lens']
        if not pd.notna(raw) or str(raw).strip() in ('', 'nan', 'N/A'):
            continue

        text = str(raw).strip()
        # Split on semicolons to get individual theories
        parts = re.split(r'[;]', text)

        l1_set = set()
        l2_set = set()

        for p in parts:
            p = p.strip()
            if not p or p.upper() in skip_values or p.startswith('N/A') or p.startswith('n/a'):
                continue

            # Clean the text before matching
            cleaned = _clean_theory_text(p)
            if not cleaned:
                continue

            # Try to match against catalog
            matched = False
            for compiled_pat, canonical, discipline in THEORY_LOOKUP:
                if compiled_pat.search(cleaned):
                    l1_set.add(discipline)
                    l2_set.add(canonical)
                    matched = True
                    break  # first match wins for this theory string

        # Apply manual overrides if nothing matched
        if not l1_set and not l2_set:
            pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
            title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''
            for (oid, tstart), (l2_str, l1_str) in MANUAL_THEORY_OVERRIDES.items():
                if pid == oid and title.startswith(tstart):
                    for t in l2_str.split(';'):
                        t = t.strip()
                        if t:
                            l2_set.add(t)
                    for d in l1_str.split(';'):
                        d = d.strip()
                        if d:
                            l1_set.add(d)
                    break

        if l1_set or l2_set:
            df.at[idx, 'std_theory_L1_discipline'] = '; '.join(sorted(l1_set))
            df.at[idx, 'std_theory_L2_name'] = '; '.join(sorted(l2_set))

    # ── Validation ──
    has_theory = df['std_theory_L2_name'].ne('').sum()
    total = len(df)
    print(f"std_theory_L2_name: {has_theory}/{total} papers classified ({has_theory/total*100:.1f}%)")

    from collections import Counter
    # L1 distribution
    l1_counts = Counter()
    for val in df['std_theory_L1_discipline']:
        if val:
            for d in val.split('; '):
                l1_counts[d] += 1
    print(f"\nL1 Discipline distribution:")
    for d, n in l1_counts.most_common():
        print(f"  {d:30s} {n:5d}")

    # Top L2 theories
    l2_counts = Counter()
    for val in df['std_theory_L2_name']:
        if val:
            for t in val.split('; '):
                l2_counts[t] += 1
    print(f"\nTop 30 L2 theories:")
    for t, n in l2_counts.most_common(30):
        print(f"  {t:45s} {n:5d}")

    # Unique L2 count
    print(f"\nUnique L2 theories: {len(l2_counts)}")

    return df


def std_data_source_type_and_named(df):
    """
    Variables: std_dsType, std_dsNamed
    Source column(s): data_source, method, sample
    Date finalized: 2026-03-10
    Decision rationale: Two complementary views of data sourcing — std_dsType captures
    the general category of data collection/origin (9 mutually non-exclusive categories),
    while std_dsNamed extracts specific named datasets with alias normalization.
    Both are multi-valued (semicolon-separated).
    """

    # ── DATA SOURCE TYPE — 9 categories ──
    DS_TYPE_PATTERNS = {
        'Survey/Questionnaire': [
            r'\bsurveys?\b', r'\bquestionnaires?\b', r'\bself[- ]report',
            r'\blikert\b', r'\bresponse\s+rate\b', r'\bonline\s+survey',
            r'\btelephone\s+survey', r'\bweb\s+survey', r'\be-?mail\s+survey',
            r'\bexperience[- ]sampling', r'\bdiary\s+(?:stud|data|method|entries)',
            r'\bESM\b', r'\bprimary\s+data\b(?!.*(?:interview|case|ethnograph|observ))',
            r'\bscale\s+(?:development|measure)',
            r'\bgallup\b', r'\bworld\s+poll\b',
        ],
        'Interview': [
            r'\binterview', r'\bverbal\s+protocol', r'\boral\s+(?:histor|narrative)',
            r'\bfocus\s+group', r'\binformant', r'\bconversation\s+analy',
            r'\blife\s+stor', r'\bnarrative\s+inquiry', r'\bnarrative\s+data',
            r'\bthink[- ]aloud', r'\bprotocol\s+analysis',
            r'\btape[- ]record', r'\btranscri(?:pt|bed|ption)',
            r'\bpress\s+conference\s+transcript',
        ],
        'Experiment': [
            r'\bexperiment', r'\brandomiz', r'\btreatment\s+(group|condition|arm)',
            r'\bcontrol\s+group', r'\blab(?:oratory)?\s+stud', r'\bfield\s+experiment',
            r'\bconjoint', r'\bvignette', r'\bdiscrete\s+choice\s+experiment',
            r'\bpolicy\s+captur', r'\bA/B\s+test', r'\bRCT\b',
            r'\bmanipulat', r'\bscenario[- ]based\s+experiment',
            r'\bbetween[- ]subject', r'\bwithin[- ]subject',
            r'\bfactorial\s+design', r'\bexperimental\s+(?:design|data|stud)',
            r'\bfMRI\b', r'\bEEG\b', r'\bneuro(?:scien|imag)',
            r'\bskin\s+conductance', r'\beye[- ]track', r'\bphysiological',
            r'\bAmazon\s+Mechanical\s+Turk\b', r'\bMTurk\b', r'\bProlific\b',
            r'\bpitch\s+competition', r'\bbusiness\s+plan\s+competition',
            r'\bvideo\s+record(?:ing|ed)',
            r'\brs-fMRI\b', r'\bbrain\s+scan',
        ],
        'Archival/Database': [
            r'\barchival\b', r'\bsecondary\s+(?:data|source|financial)',
            r'\bdatabase\b', r'\bdataset\b',
            r'\brecords?\b(?!.*(?:interview|oral|tape))',
            r'\bannual\s+report', r'\bfinancial\s+(?:data|statement|report|account|record)',
            r'\bprospectus', r'\b10-?K\b', r'\bproxy\s+statement',
            r'\bIPO\s+(?:data|prospectus|filing|firm|sample)',
            r'\bS-1\s+filing', r'\bSEC\s+filing',
            r'\bhand[- ]collect', r'\bregist(?:er|ry)\s+data',
            r'\bpanel\s+(?:data|study)\b', r'\blongitudinal\s+(?:data|panel|dataset|firm|tracking|cohort|measurement|study)',
            r'\btime[- ]series\s+data', r'\bcross[- ](?:section|country|industr)\w*\s+(?:data|panel|sample)',
            r'\bbalance\s+sheet', r'\btax\s+(?:data|return|record|file)',
            r'\bcourt\s+record', r'\blegal\s+record',
            r'\bcompany\s+(?:record|report|document|data|financial|website)',
            r'\bcorporate\s+(?:report|record|data|governance|proxy)',
            r'\bnewspaper\b', r'\bmedia\s+(?:data|coverage|report|content)',
            r'\btrade\s+data', r'\bexport\s+data', r'\bimport\s+data',
            r'\bstock\s+(?:market|exchange|data|price|return)',
            r'\bmarket\s+data', r'\bfirm[- ]level\s+data', r'\bfirm\s+data\b',
            r'\bindustry\s+(?:data|statistics|level\s+data)',
            r'\binstitutional\s+data', r'\bfamily\s+firm\s+data',
            r'\bpublished\s+(?:data|studies|empirical|research|article|sales)',
            r'\bmeta[- ]analy(?:sis|tic)', r'\bsystematic\s+(?:literature\s+)?review',
            r'\bcontent\s+analy', r'\btext\s+analy',
            r'\bdisclosure\s+document', r'\bfranchise\s+(?:disclosure|contract|system|data|operations)',
            r'\bproprietary\s+(?:data|dataset)', r'\bunique\s+dataset',
            r'\bpopulation[- ](?:based|level)', r'\bregist(?:er|ry)\b',
            r'\bcountry[- ]level\s+(?:data|panel)', r'\bcounty[- ]level',
            r'\bregional\s+(?:data|statistic)', r'\bmacroeconomic\s+(?:data|statistic)',
            r'\blabor\s+market\s+data', r'\bwage\s+(?:data|and\s+employment)',
            r'\bbank\s+(?:data|record|internal|charter|loan|account)',
            r'\bfund\s+(?:data|performance|record)', r'\bVC\s+(?:data|fund|firm|invest)',
            r'\bPE\s+(?:data|fund|invest|firm)', r'\bprivate\s+equity',
            r'\binvestment\s+(?:data|memo|record|fund|proposal)',
            r'\binvestor\s+(?:data|record|evaluat)',
            r'\bloan\s+data', r'\bcredit\s+(?:data|record|report)',
            r'\baccounting\s+(?:data|record)',
            r'\bbibliometric', r'\bcitation\s+data',
            r'\bhistorical\s+(?:data|record|archiv|source)',
            r'\bbiograph', r'\bmanufactur(?:ing|er)\s+(?:data|director|statistic)',
            r'\bblockchain\s+(?:data|ledger)', r'\btoken\s+(?:data|market|offering)',
            r'\bICO\b(?:\s+data)?',
            r'\beconomic\s+(?:data|statistic|indicator)',
            r'\bCSR\s+(?:data|rating)', r'\bESG\b', r'\bKLD\b',
            r'\binnovation\s+(?:data|metric|measure)',
            r'\bmatched[- ]pair', r'\bmatched\s+case',
            r'\bventure\s+(?:data|performance|life|capital)',
            r'\bangel\s+(?:invest|network|group)',
            r'\bbiotechnology\s+(?:data|firm|venture|alliance)',
            r'\bpricing\s+data', r'\bcash[- ]flow\s+data',
            r'\bsales\s+data', r'\bperformance\s+(?:data|review|metric)',
            r'\bfinancing\s+(?:data|round|record)',
            r'\bboard\s+(?:data|appointment)', r'\bgovernance\s+data',
            r'\bcoupon\s+(?:data|redemption)',
            r'\bvat\s+registration', r'\bbusiness\s+plan(?!.*competition)',
            r'\boriginal\s+business\s+plan',
            r'\bprocess[- ]tracing', r'\bQCA\b',
            r'\bmicrofinance\s+(?:data|information)',
            r'\bdiscourse\s+analy', r'\bliterature\s+review',
            r'\brating\s+agency', r'\bthird[- ]party\s+(?:data|rating|report)',
            r'\bICPSR\b', r'\bworkforce\s+survey',
            r'\balmanac\b', r'\bstatistical\s+abstract',
            r'\bdata\s+collection', r'\bphase\s+data',
            r'\blabor\s+(?:market\s+)?statistic',
            r'\bAustralian\s+(?:firm|longitudinal)',
        ],
        'Government/Administrative': [
            r'\bcensus', r'\bgovernment\s+(?:data|statistic|record|survey|source|report)',
            r'\badministrative\s+(?:data|record)',
            r'\bpatent\s+(?:data|record|filing|ownership)', r'\bUSPTO\b', r'\bEPO\b', r'\bPATSTAT\b',
            r'\bIRS\b', r'\bInternal Revenue\b',
            r'\bSEC\b(?!\s+(?:tion|ond|ret|ure|tor))', r'\bEDGAR\b',
            r'\bBLS\b', r'\bBureau of Labor\b',
            r'\bSBA\b', r'\bSmall Business Administration\b',
            r'\bSBIR\b', r'\bSmall Business Innovation Research\b',
            r'\bNational\s+(?:Science\s+Foundation|Survey|Longitudinal|Federation|Statistics)',
            r'\bNSF\b', r'\bfederal\s+(?:data|record|register|reserve|election)',
            r'\bstate\s+(?:data|record|register|filing|sales\s+tax|level\s+instit)',
            r'\bregulatory\s+(?:data|filing|record)',
            r'\bEurostat\b', r'\bOECD\b', r'\bWorld\s+Bank\b',
            r'\bUN\s+(?:data|statistic)', r'\bUnited Nations\b',
            r'\bFDA\b', r'\bFCC\b', r'\bDepartment\s+of\s+(?:Energy|Commerce|Labor|Natural)',
            r'\bIMF\b', r'\bInternational Monetary Fund\b',
            r'\bWIPO\b', r'\bWorld\s+Intellectual\s+Property',
            r'\bStatistics\s+(?:Canada|Denmark|Sweden|Norway|Finland)',
            r'\bSwedish\s+(?:register|population|firm\s+registry)',
            r'\bDanish\s+(?:register|linked)',
            r'\bNorwegian\s+(?:register|registry|population)',
            r'\bBrazilian\s+business\s+registry',
            r'\bChinese\s+(?:business\s+registration|IPO\s+registry|industrial\s+statistic)',
            r'\bUK\s+(?:university\s+spin|Small\s+Business\s+Service)',
            r'\bpublic\s+(?:records|register|data)',
            r'\bvoter\s+registration',
            r'\bEPA\b', r'\bEnvironmental Protection\b',
            r'\bpolicy\s+document', r'\bgovernment\s+budget',
            r'\blabor\s+(?:market\s+)?statistic',
            r'\bStatistisches\s+Bundesamt\b',
            r'\bBureau\s+of\s+Economic\s+Analysis\b',
        ],
        'Case Study': [
            r'\bcase\s+stud', r'\bin-?depth\s+(?:single|multiple|comparative)\s+case',
            r'\bfield\s+stud', r'\bfield\s+research\b', r'\baction\s+research\b',
            r'\bcase\s+(?:example|analys|file|history|histories)',
            r'\bteaching\s+case\b', r'\bcase\s+data\b',
        ],
        'Ethnographic/Observational': [
            r'\bethnograph', r'\bobservation(?:al|s)?\b(?!.*(?:from\s+census))',
            r'\bfield\s*work\b', r'\bparticipant\s+observ',
            r'\bsite\s+visit', r'\bshadow(?:ing)?\b', r'\bimmers',
            r'\bauto-?ethnograph', r'\bnetnograph',
            r'\bphotograph', r'\bvideo\s+(?:file|data|ethnograph)',
            r'\bfield\s+note',
        ],
        'Online/Digital Data': [
            r'\bplatform\s+data', r'\bweb[- ]scrap', r'\bcrowdfund',
            r'\bsocial\s+media\b', r'\btwitter\b', r'\btweet', r'\blinkedin\b',
            r'\bfacebook\b', r'\binstagram\b', r'\byoutube\b', r'\breddit\b',
            r'\bonline\s+(?:platform|review|data|content|communit|CV)',
            r'\buser[- ]generated\s+content', r'\bdigital\s+trace',
            r'\bapp\s+store\b', r'\bGoogle\s+Trends\b',
            r'\bNLP\b', r'\bweb\s+data\b',
            r'\bwebsite\s+(?:data|content|text)',
            r'\bGlassdoor\b', r'\bYelp\b', r'\bTripAdvisor\b',
            r'\bDownload\.com\b', r'\bCNET\b',
            r'\bKickstarter\b', r'\bIndiegogo\b', r'\bKiva\b', r'\bAngelList\b',
            r'\bCrunchbase\b', r'\bPitchBook\b',
            r'\bICObench\b', r'\bCoindesk\b', r'\bCoinschedule\b',
            r'\bGitHub\b', r'\bsource\s+code\s+data',
            r'\bapp\b(?:\s+store|\s+data)',
        ],
        'Simulation/Formal': [
            r'\bsimulat', r'\bagent[- ]based\s+model', r'\bcomputational\s+model',
            r'\bMonte\s+Carlo\b', r'\bformal\s+model', r'\bmathematical\s+model',
            r'\bnumerical\s+(?:model|simulat|analy)',
            r'\bcomputerized\s+(?:model|industr)',
        ],
    }

    DS_TYPE_COMPILED = {}
    for cat, patterns in DS_TYPE_PATTERNS.items():
        combined = '|'.join(f'(?:{p})' for p in patterns)
        DS_TYPE_COMPILED[cat] = re.compile(combined, re.IGNORECASE)

    # ── NAMED DATASET CATALOG ──
    NAMED_DATASET_CATALOG = {
        # Entrepreneurship-specific
        'PSED': [r'\bPSED\b', r'Panel Study of Entrepreneurial Dynamics', r'\bCAUSEE\b', r'\bSW-PSED\b'],
        'GEM': [r'\bGEM\b(?!\s+(?:stone|s\b))', r'Global Entrepreneurship Monitor'],
        'Kauffman Firm Survey': [r'\bKauffman\b', r'\bKFS\b'],
        'GUESSS': [r'\bGUESS\b', r'Global University Entrepreneurial Spirit'],
        # Financial
        'Compustat': [r'\bCOMPUSTAT\b|\bCompustat\b'],
        'CRSP': [r'\bCRSP\b'],
        'VentureXpert': [r'\bVentureXpert\b', r'Venture\s*Expert\b', r'VentureOne\b', r'Venture\s*Economics\b'],
        'Thomson Reuters': [r'\bThomson(?:\s+Reuters)?\b(?!.*(?:VentureXpert|Venture\s*Expert|VentureOne|Venture\s*Econ))'],
        'Bloomberg': [r'\bBloomberg\b'],
        'Datastream': [r'\bDatastream\b'],
        'PitchBook': [r'\bPitchBook\b'],
        'VentureSource': [r'\bVentureSource\b'],
        'Preqin': [r'\bPreqin\b'],
        'Dealogic': [r'\bDealogic\b'],
        'Zephyr': [r'\bZephyr\b'],
        'WRDS': [r'\bWRDS\b'],
        'SDC Platinum': [r'\bSDC\b(?:\s+Platinum)?'],
        'S&P Capital IQ': [r'Capital\s*IQ\b', r'S&P\s+Capital'],
        'ExecuComp': [r'\bExecuComp\b'],
        'Refinitiv/EIKON': [r'\bRefinitiv\b', r'\bEIKON\b'],
        'KLD/MSCI ESG': [r'\bKLD\b', r'\bMSCI\s+ESG\b'],
        # Business
        'Dun & Bradstreet': [r'Dun\s*[&and]+\s*Bradstreet', r"\bDun'?s\s+Market\b", r'\bDMI\b(?:\s+file)?'],
        'Orbis/BvD': [r'\bOrbis\b(?!\s+(?:terrarum))', r'Bureau van Dijk', r'\bBvD\b'],
        'Amadeus': [r'\bAmadeus\b(?:\s+(?:datab|firm|financial))'],
        'DIANE': [r'\bDIANE\b(?:\s+(?:datab|French))'],
        'SABI': [r'\bSABI\b'],
        'Crunchbase': [r'\bCrunchbase\b'],
        'CB Insights': [r'\bCB\s*Insights\b'],
        'Inc. 500/5000': [r'\bInc\.?\s*(?:500|5000)\b'],
        'PIMS': [r'\bPIMS\b'],
        'Fortune 500': [r'\bFortune\s*500\b'],
        'LexisNexis': [r'LexisNexis', r'Lexis.?Nexis'],
        'Factiva': [r'\bFactiva\b'],
        'ABI/Inform': [r'ABI.?Inform'],
        'ProQuest': [r'\bProQuest\b(?:\s+(?:datab|dissert))'],
        'Creditreform': [r'\bCreditreform\b'],
        'CEPRES': [r'\bCEPRES\b'],
        'VICO': [r'\bVICO\b'],
        # Crowdfunding/Platform
        'Kickstarter': [r'\bKickstarter\b', r'\bKicktraq\b'],
        'Indiegogo': [r'\bIndiegogo\b'],
        'Kiva': [r'\bKiva\b'],
        'AngelList': [r'\bAngelList\b'],
        'GoFundMe': [r'\bGoFundMe\b'],
        'ICObench': [r'\bICObench\b'],
        # Government/Census
        'US Census Bureau': [r'Census\s+Bureau', r'U\.?S\.?\s*Census', r'American\s+Community\s+Survey'],
        'Current Population Survey': [r'Current Population Survey', r'\bCPS\b(?:\s+(?:data|survey|sample|microdata))'],
        'Survey of Business Owners': [r'Survey of Business Owners', r'\bSBO\b(?:\s+(?:data|survey))'],
        'Bureau of Labor Statistics': [r'Bureau of Labor Statistics', r'\bBLS\b(?:\s+(?:data|stat|employ))'],
        'USPTO': [r'\bUSPTO\b', r'U\.?S\.?\s*Patent\s+(?:and\s+Trademark\s+)?Office'],
        'SEC/EDGAR': [r'\bEDGAR\b', r'\bSEC\b(?:\s+(?:fil|data|disclos|report|document|prospectus))'],
        'IRS': [r'\bIRS\b(?!\s+(?:h\b))', r'Internal Revenue Service'],
        'SBIR': [r'\bSBIR\b', r'Small Business Innovation Research'],
        'SBA': [r'\bSBA\b(?:\s+(?:data|loan|program|file|microdata|survey|record|Freedom|7\(a\)|Office|list|director))'],
        'EEOC': [r'\bEEOC\b', r'Equal Employment Opportunity Commission'],
        'FDA': [r'\bFDA\b(?:\s+(?:data|approv|device|drug|database|medical|clearance|510))', r'Food and Drug Administration'],
        'NSF': [r'\bNSF\b(?:\s+(?:data|fund|grant|award|survey))', r'National Science Foundation(?:\s+(?:data|fund|survey))'],
        'FHLBB': [r'\bFHLBB\b', r'Federal Home Loan Bank Board'],
        'NFIB': [r'\bNFIB\b', r'National Federation of Independent Business'],
        'FDIC': [r'\bFDIC\b'],
        'Federal Reserve': [r'\bFederal Reserve\b'],
        'NSF/SESTAT': [r'\bSESTAT\b', r'NSF.{0,10}Science\s+and\s+Engineering'],
        'NASA': [r'\bNASA\b'],
        'SBDC': [r'\bSBDC\b', r'Small Business Development Center'],
        'SBI': [r'\bSBI\b(?:\s+(?:program|case|Small\s+Business\s+Institute))', r'Small Business Institute\b'],
        # Household/Labor
        'NLSY': [r'\bNLSY\b', r'National Longitudinal Survey of Youth'],
        'PSID': [r'\bPSID\b', r'Panel Study of Income Dynamics'],
        'SOEP': [r'\bSOEP\b', r'(?:German\s+)?Socio-?Economic Panel(?:\s+Study)?'],
        'BCS70': [r'\bBCS70\b', r'(?:1970\s+)?British Cohort Study'],
        'BHPS': [r'\bBHPS\b', r'British Household Panel\b'],
        'ELSA': [r'\bELSA\b(?:\s+(?:data|survey|study|wave))', r'English Longitudinal Study of Ageing'],
        'ECHP': [r'\bECHP\b', r'European Community Household Panel'],
        'HILDA': [r'\bHILDA\b', r'Household,?\s+Income\s+and\s+Labour\s+Dynamics'],
        'HRS': [r'\bHRS\b(?:\s+(?:data|genetic|1992))', r'Health and Retirement Study'],
        'SSBF': [r'\bSSBF\b', r'Survey of Small Business Finance'],
        'SCF': [r'\bSCF\b(?:\s+(?:data|survey))', r'Survey of Consumer Finance'],
        'CFPS': [r'\bCFPS\b', r'China Family Panel Stud'],
        'CPES': [r'\bCPES\b', r'Chinese Private Enterprise Survey'],
        'CSMAR': [r'\bCSMAR\b', r'China Stock Market'],
        'China Statistical Yearbook': [r'China Statistical Yearbook'],
        'NEEQ': [r'\bNEEQ\b', r'New Third Board', r'National Equities Exchange'],
        'Labour Force Survey': [r'Labour Force Survey', r'\bLFS\b(?:\s+(?:data|survey))'],
        'GSS': [r'General Social Survey', r'\bGSS\b(?:\s+(?:data|survey))'],
        'NHANES': [r'\bNHANES\b', r'National Health and Nutrition Examination'],
        'NESARC': [r'\bNESARC\b', r'National Epidemiologic Survey on Alcohol'],
        'World Values Survey': [r'World Values Survey', r'\bWVS\b'],
        'Eurobarometer': [r'\bEurobarometer\b', r'Flash Eurobarometer'],
        'European Social Survey': [r'European Social Survey', r'\bESS\b(?:\s+(?:data|survey|wave))'],
        'Gallup World Poll': [r'\bGallup\b(?:\s+World\s+Poll)?'],
        'Hofstede Cultural Dimensions': [r'\bHofstede\b'],
        'GLOBE': [r'\bGLOBE\b(?:\s+(?:study|data|cultural|project))'],
        'Schwartz Value Survey': [r'\bSchwartz\b(?:\s+(?:value|cultural|dimension))'],
        # International/Macro
        'World Bank': [r'World Bank\b'],
        'Eurostat': [r'\bEurostat\b'],
        'OECD': [r'\bOECD\b'],
        'Heritage Foundation / Economic Freedom Index': [r'Heritage Foundation', r'Economic Freedom\s+(?:Index|of the World)'],
        'Fraser Institute': [r'\bFraser Institute\b'],
        'World Economic Forum': [r'World Economic Forum', r'Global Competitiveness\s+(?:Index|Report)'],
        'Doing Business': [r'Doing Business\b'],
        'Penn World Table': [r'Penn World Table', r'\bPWT\b'],
        'Global Innovation Index': [r'Global Innovation Index'],
        'CPI/Transparency International': [r'Corruption Perception.*Index', r'Transparency International'],
        'NBER': [r'\bNBER\b'],
        'IMF': [r'\bIMF\b', r'International Monetary Fund'],
        'WIPO': [r'\bWIPO\b', r'World Intellectual Property'],
        # Social Media/Web
        'LinkedIn': [r'\bLinkedIn\b'],
        'Twitter/X': [r'\bTwitter\b', r'\btweet'],
        'Facebook': [r'\bFacebook\b'],
        'YouTube': [r'\bYouTube\b'],
        'Reddit': [r'\bReddit\b'],
        'Glassdoor': [r'\bGlassdoor\b'],
        'Google Trends': [r'\bGoogle\s+Trends\b'],
        'Google Scholar': [r'\bGoogle\s+Scholar\b'],
        'Amazon Mechanical Turk': [r'\bMechanical\s+Turk\b', r'\bMTurk\b'],
        'Prolific': [r'\bProlific\b'],
        # Academic
        'Web of Science': [r'Web of (?:Science|Knowledge)', r'\bWoS\b', r'\bWOS\b', r'\bISI\b(?:\s+Web)'],
        'Scopus': [r'\bScopus\b'],
        # Innovation/Patent
        'EPO': [r'\bEPO\b', r'European Patent Office'],
        'PATSTAT': [r'\bPATSTAT\b'],
        # Country-specific
        'Statistics Denmark': [r'Statistics Denmark', r'\bDanish\s+(?:linked|register|employer|statist|longitudinal)'],
        'IDA Denmark': [r'\bIDA\b(?:\s+(?:data|panel|register|Danish))', r'Integrated Database for La(?:bor|bour) Market Research'],
        'Statistics Sweden': [r'Statistics Sweden', r'\bSwedish\s+(?:register|population|firm\s+registry|longitudinal)'],
        'Statistics Canada': [r'Statistics Canada'],
        'Statistics Norway': [r'Statistics Norway', r'Norwegian\s+(?:register|registry|National Register)'],
        'Statistics Finland': [r'Statistics Finland', r'Finnish\s+(?:register|registry)'],
        'Statistics Netherlands': [r'Statistics Netherlands', r'\bCBS\b(?:\s+(?:Dutch|Netherlands|data))'],
        'Enterprise Survey': [r'Enterprise Survey\b'],
        'Community Innovation Survey': [r'Community Innovation Survey', r'\bCIS\b(?:\s+(?:data|survey|innov))'],
        'Mannheim Enterprise Panel / ZEW': [r'\bMannheim\b', r'\bZEW\b'],
        'KfW': [r'\bKfW\b(?:\s+(?:panel|survey|data|start|Gr.nd))'],
        'Longitudinal Business Database': [r'Longitudinal Business Database', r'\bLBD\b'],
        'IAB Germany': [r'\bIAB\b(?:\s+(?:establishment|data|Betriebs|panel))'],
        'Bank of Italy': [r'Bank of Italy\b'],
        'Deutsche Bundesbank': [r'Deutsche Bundesbank\b', r'\bUSTAN\b'],
        'ESEE Spain': [r'\bESEE\b', r'Spanish Survey on Business Strategies'],
        'ENOE Mexico': [r'\bENOE\b', r'Mexican household survey'],
        'ASI India': [r'Annual Survey of Industries\b', r'\bASI\b(?:\s+(?:India|data|survey))'],
        'NSSO India': [r'\bNSSO\b', r'National Sample Survey(?:\s+(?:Office|Organisation|data))'],
        'CMBOR': [r'\bCMBOR\b'],
        'Zhongguancun Science Park': [r'Zhongguancun\b'],
        'FDD': [r'Franchise Disclosure Document', r'\bFDD\b(?:\s+(?:data|franchise))'],
        "Bond's Franchise Guide": [r"Bond'?s Franchise Guide"],
        'NVCA': [r'\bNVCA\b', r'National Venture Capital Association'],
        'SIC Codes': [r'\bSIC\b(?:\s+(?:code|classif|industr))'],
        'NAICS': [r'\bNAICS\b'],
        'NFBS': [r'\bNFBS\b', r'National Family Business Survey'],
        'MIRP': [r'\bMIRP\b', r'Minnesota Innovation Research Program'],
        'Iowa Gambling Task': [r'Iowa Gambling Task', r'\bIGT\b(?:\s+(?:task|data|measure|performance))'],
        'Crowdcube': [r'\bCrowdcube\b'],
        'BEEPS': [r'\bBEEPS\b', r'Business Environment.*Enterprise.*Performance'],
        'B Lab / B Impact': [r'\bB\s+Lab\b', r'\bB\s+Impact\b'],
        'MIX (Microfinance)': [r'\bMIX\b(?:\s+data)?', r'Microfinance Information Exchange'],
        'EVCA': [r'\bEVCA\b', r'European Venture Capital Association'],
        'CVCA': [r'\bCVCA\b', r'Canadian Venture Capital Association'],
        'GALI': [r'\bGALI\b', r'Global Accelerator Learning'],
        'Planet Retail': [r'\bPlanet Retail\b'],
        'Brewers Association': [r'Brewers?\s+Association\b', r'Institute for Brewing'],
        # Neuro/Bio
        'fMRI': [r'\bfMRI\b', r'\brs-fMRI\b'],
        'EEG': [r'\bEEG\b'],
        # Broader identifiable data source categories
        # VC/PE sources
        'VC Database': [r'(?:VC|venture capital)\s+(?:database|data\b|syndication|investment\s+data|fund\s+data|portfolio|deal)', r'venture\s+capital\s+(?:firm|fund)\s+data'],
        'Angel Investment Data': [r'angel\s+(?:invest|capital|group|network)\s+(?:data|database|record|track|portfolio)'],
        # IPO sources
        'IPO Prospectuses/Data': [r'\bIPO\b(?:\s+(?:prospectus|prospecti|filing|data\b|firm\s+data|sample\s+data|market\s+data))', r'IPO\s+(?:databases|records)'],
        # Patent data (generic, beyond USPTO/EPO/PATSTAT)
        'Patent Data': [r'patent\s+(?:data\b|database|citation|application|filing|record)', r'patent\s+portfolio\s+data'],
        # M&A data
        'M&A Data': [r'M&A\s+(?:data|database|deal|transaction)', r'(?:merger|acquisition)\s+(?:data|database|record)'],
        # Stock exchange data
        'Stock Exchange Data': [r'(?:NYSE|NASDAQ|AMEX|LSE|SSE|SZSE|TSX|KOSDAQ|KOSPI)\b', r'stock\s+(?:exchange|market)\s+(?:data|record|listing)'],
        # Country-specific firm/register data (broader patterns)
        'Chinese Firm/Industry Data': [r'Chinese\s+(?:firm|company|enterprise|IPO|industry|industrial|private|stock|listed)\s+(?:data|database|record|sample|panel)', r'Chinese\s+(?:A-share|stock\s+market)'],
        'Danish Register Data': [r'Danish\s+(?:register|registry|administrative|matched|employer|longitudinal|panel)\s+data'],
        'Swedish Register Data': [r'Swedish\s+(?:register|registry|administrative|matched|employer|longitudinal|full.population)\s+data'],
        'Norwegian Register Data': [r'Norwegian\s+(?:register|registry|administrative|matched|employer|longitudinal)\s+data'],
        'Finnish Register Data': [r'Finnish\s+(?:register|registry|administrative|matched|employer|longitudinal|panel)\s+data'],
        'German Firm Data': [r'German\s+(?:firm|company|enterprise|start.up|family\s+firm)\s+(?:data|database|panel|sample)'],
        'French Firm Data': [r'French\s+(?:firm|company|enterprise|start.up|VC)\s+(?:data|database|panel|sample)'],
        'Dutch Firm Data': [r'Dutch\s+(?:firm|company|enterprise|film|art)\s+(?:data|database|panel|sample|record)'],
        'Korean Firm Data': [r'Korean\s+(?:firm|company|enterprise|venture|IPO)\s+(?:data|database|panel|sample)'],
        # Platform-specific
        'Airbnb': [r'\bAirbnb\b', r'InsideAirbnb'],
        'CorpTech': [r'\bCorpTech\b'],
        'AURELIA Neo': [r'\bAURELIA\b'],
        'Qualtrics': [r'\bQualtrics\b(?:\s+(?:panel|sample|platform))'],
        # Industry directories / chambers
        'Chamber of Commerce Data': [r'Chamber of (?:Commerce|Industry)\s+(?:data|database|member|director|record|list)', r'(?:industry|trade)\s+director(?:y|ies)\s+(?:data|database)'],
        # Accelerator/incubator
        'Accelerator/Incubator Data': [r'(?:accelerator|incubator)\s+(?:data|database|program\s+data|participant\s+data|portfolio)'],
        # Business plan competition
        'Business Plan Competition Data': [r'(?:business plan|venture|startup)\s+competition\s+(?:data|participant|entry|submission)'],
        # Online review/UGC platforms
        'TripAdvisor': [r'\bTripAdvisor\b'],
        'Yelp': [r'\bYelp\b'],
        # National-level surveys (specific)
        'NSCW': [r'National Study of the Changing Workforce'],
        'Forum of Private Business': [r'Forum of Private Business'],
        'Grant Thornton Survey': [r'Grant Thornton\b'],
        # Bankruptcy
        'Bankruptcy Data': [r'bankruptcy\s+(?:data|filing|record|database|court)'],
        # Additional specific sources
        'Worldscope': [r'\bWorldscope\b'],
        'Prowess/CMIE': [r'\bProwess\b', r'\bCMIE\b'],
        'HKEX': [r'\bHKEX\b', r'Hong Kong\s+(?:Stock\s+)?Exchange\s+(?:data|filing|listing)'],
        'BSE/NSE India': [r'Bombay Stock Exchange', r'National Stock Exchange of India'],
        'ACEF': [r'Angel Capital Education Foundation', r'\bACEF\b'],
        'Business/Trade Directory': [r'(?:business|company|trade|industry)\s+director(?:y|ies)\s+(?:data|database|list|record)'],
        'Linked Employer-Employee Data': [r'(?:employer.employee|linked\s+employer)\s+(?:data|register|panel)', r'matched\s+employer.employee'],
        'Population Registry': [r'(?:population|national)\s+(?:registry|register)\s+(?:data|of\s+\w)'],
        'Encyclopaedia Metallum': [r'Encyclopaedi?a Metallum'],
        'CIEP': [r'Comparative Immigrant Entrepreneurship'],
        'Beer Institute': [r'Beer Institute', r'Brewer.?s Almanac'],
        'VAT Registration Data': [r'\bVAT\b\s+(?:registr|data)'],
        'Thomson Financial': [r'Thomson Financial\b'],
        'I/B/E/S': [r'\bI/B/E/S\b', r'\bIBES\b'],
        'BoardEx': [r'\bBoardEx\b'],
        'RiskMetrics': [r'\bRiskMetrics\b'],
        'Ritter IPO Data': [r'(?:Jay\s+)?Ritter.?s?\s+IPO'],
        'Office for National Statistics UK': [r'Office for National Statistics'],
        'Statistisches Bundesamt': [r'Statistisches Bundesamt'],
        'ISTAT Italy': [r'\bIstat\b', r'Italian National Institute of Statistics'],
        # --- Pass 2 additions: broader sources found in scan ---
        'Freedom House': [r'Freedom\s+House'],
        'Grameen Bank': [r'Grameen\s+Bank'],
        'FCC': [r'\bFCC\b\s+(?:data|licens|record|filing|report)'],
        'Energy Information Administration': [r'Energy\s+Information\s+Administration'],
        'Robert Morris Associates': [r'Robert\s+Morris(?:\s+(?:and|&)\s+Associates)?(?:.{0,10}(?:Statement|Annual|Stud))'],
        'National Retail Merchants Association': [r'National\s+Retail\s+Merchants\s+Association'],
        'Branham 300/400': [r'Branham\s+\d{3}'],
        'MicroRate': [r'\bMicroRate\b', r'\bMicrofinanza\b', r'\bPlanet\s+Rating\b', r'\bM-?Cril\b'],
        'HVCA': [r'\bHVCA\b'],
        'BOSS Directory': [r'BOSS\s+Directory'],
        'Venture Capital Report': [r'Venture\s+Capital\s+Report\b'],
        'Southampton Business School Database': [r'Southampton\s+Business\s+School\s+(?:database|data)'],
        'Buffalo Courier-Express': [r'Buffalo\s+Courier'],
        'IMEC': [r'\bIMEC\b\s+(?:TTO|data|record|technology)'],
        'White House Conference on Small Business': [r'White\s+House\s+Conference'],
        'Regional Development Funds Sweden': [r'Regional\s+Development\s+Fund'],
        "Hoover's": [r"Hoover['']?s?\s+(?:Guide|Online|data|database|Handbook)"],
        "Moody's": [r"Moody['']?s?\s+(?:financial|report|data|manual|Investor|Industrial)"],
        'International Data Corporation': [r'International\s+Data\s+Corp', r'\bIDC\b\s+(?:data|census|report|survey)'],
        'Business Dynamics Statistics': [r'Business\s+Dynamics\s+Statistics', r'\bBDS\b\s+(?:data|database)'],
        'S&P': [r'\bS\s*&\s*P\s*(?:500|1500|Composite|Capital|data|firm)', r'Standard\s+(?:and|&)\s+Poor'],
    }

    NAMED_DS_COMPILED = {}
    for canonical, patterns in NAMED_DATASET_CATALOG.items():
        combined = '|'.join(f'(?:{p})' for p in patterns)
        NAMED_DS_COMPILED[canonical] = re.compile(combined, re.IGNORECASE)

    # ── MANUAL DATA SOURCE OVERRIDES ──
    MANUAL_DS_OVERRIDES = {
        # Remaining unmatched empirical papers — exact title[:40] keys
        (98, 'New firm performance and the replacemen'): ('Government/Administrative', 'Statistics Denmark'),
        (269, 'Shooting Stars? Uncertainty in Hiring E'): ('Government/Administrative', ''),
        (295, 'Growth paths and survival chances: An a'): ('Archival/Database', ''),
        (388, 'Adaptations to knowledge templates in b'): ('Ethnographic/Observational', ''),
        (492, 'Trends in the market for entrepreneursh'): ('Archival/Database', ''),
        (518, 'An institutional perspective on borrowi'): ('Archival/Database', ''),
        (527, 'Self-employment and well-being across i'): ('Archival/Database', 'Eurostat'),
        (571, 'Risky business? The survival implicatio'): ('Government/Administrative', ''),
        (703, 'Do networks of financial intermediaries'): ('Archival/Database', ''),
        (706, 'When do female-owned businesses out-sur'): ('Government/Administrative', ''),
        (731, 'Reaching out or going it alone? How bir'): ('Archival/Database', ''),
        (738, 'The many faces of entrepreneurial failu'): ('Survey/Questionnaire', ''),
        (867, 'The founding rate of venture capital fir'): ('Archival/Database', ''),
        (884, 'False signaling by platform team member'): ('Online/Digital Data', ''),
        (927, 'Venturing into the unknown with strange'): ('Archival/Database', ''),
        (968, 'Many Roads Lead to Rome: How Human, Soc'): ('Archival/Database', ''),
        (969, 'Necessary Conditions and Theory-Method '): ('Archival/Database', ''),
        (982, 'Entrepreneurial Orientation: The Dimens'): ('Archival/Database', ''),
        (984, 'From principles to action: Community-ba'): ('Ethnographic/Observational', ''),
        (1088, 'Multinationality, product diversificati'): ('Archival/Database', ''),
        (1175, "The entrepreneur: A capable executive a"): ('Survey/Questionnaire', ''),
        (1176, 'Female and male entrepreneurs: Psycholo'): ('Survey/Questionnaire', ''),
        (1252, 'Testing Baumol: Institutional quality a'): ('Government/Administrative', ''),
        (1301, 'The anatomy of a corporate venturing pr'): ('Case Study', ''),
        (1330, 'Progress without a venture? Individual '): ('Interview', ''),
        (1462, 'Timing is everything? Curvilinear effec'): ('Archival/Database', ''),
        (1630, 'How Entrepreneurs Use Networks to Addre'): ('Archival/Database', ''),
        (1645, 'Family Firm Value in the Acquisition Co'): ('Archival/Database', ''),
        (1684, 'How Prior Corporate Venture Capital Inv'): ('Archival/Database', ''),
        (1709, 'Linking Corporate Entrepreneurship to F'): ('Archival/Database', ''),
        (1736, 'Collective Cognition: When Entrepreneuri'): ('Survey/Questionnaire', ''),
    }

    # ── MANUAL NAMED DATASET OVERRIDES (AI intelligence pass) ──
    # These add named datasets to papers where regex couldn't extract them.
    # Format: (paper_id, title[:40]) -> 'Named Dataset'
    MANUAL_DS_NAMED_OVERRIDES = {
        (4, 'Signaling in Equity Crowdfunding'): 'ASSOB',
        (7, 'The entrepreneurial control imperative: '): 'Steria',
        (9, 'Zobele chemical industries: the evolutio'): 'Zobele',
        (10, 'Managing dilemmas of resource mobilizati'): 'Ziqitza',
        (11, 'Well-being effects of self-employment: A'): 'UKHLS',
        (17, 'Entrepreneurship and Human Capital: Evid'): 'NSF Survey of Academic Researchers',
        (20, 'Network embeddedness and new-venture int'): 'German Biotech Directory',
        (34, 'Opportunities and institutions: A co-cre'): 'Wakefield Seafoods',
        (52, 'Should business angels diversify their i'): 'Angel Investment Platform',
        (53, 'Does the Apple Always Fall Close to the '): 'Disk/Trend',
        (75, 'Domestic versus foreign listing: Does a '): 'Chinese IPO Registry',
        (79, 'An examination of the impact of initial '): "Polk's Bank Directory",
        (80, 'The temporal nature of growth determinan'): "Polk's Bank Directory",
        (84, "New Venture Teams' Assessment of Learnin"): 'Venture Capital Journal',
        (108, 'Agency and institutional influences on f'): 'Toute la Franchise',
        (109, 'Roads Leading to Self-Employment: Compar'): 'IZA',
        (117, 'Marketplace lending of small- and medium'): 'Zencap',
        (129, 'Validation of a didactic model for the a'): 'INTERMAN',
        (164, 'Joining the pack or going solo? A dynami'): 'VMCC Archives',
        (195, 'Ownership dynamics within founder teams:'): 'BC Registry',
        (218, 'How Optimal Distinctiveness Shapes Platf'): 'Apple App Store',
        (246, 'Entrepreneurial Space and the Freedom fo'): 'NSF',
        (248, 'The lean startup method: Early-stage tea'): 'NSF',
        (268, 'Is microcredit a blessing for the poor? '): 'Microcredit Meta-analysis',
        (275, 'Attention Across Borders: Investor Atten'): 'Equity Crowdfunding Platform',
        (284, 'The Mortality Problem of Learning and Mi'): 'Lipper TASS',
        (295, 'Growth paths and survival chances: An ap'): 'Barclays Bank',
        (296, 'The Influence of Sensation Seeking in th'): 'TwinsUK',
        (302, 'Crowdlending, Self-Employment, and Entre'): 'TransUnion',
        (315, 'In the eye of the beholder? The returns '): 'Wisconsin Longitudinal Study',
        (331, 'Signalling reputation in international o'): 'Download.com',
        (334, 'Creating and capturing value from freemi'): 'Steam',
        (344, 'Natural disasters as a source of entrepr'): 'AIDA',
        (345, 'Firm-specific determinants of product li'): 'IDC',
        (346, 'Investment Bankers and IPO Pricing: Does'): 'SEC Filings',
        (359, 'Distinctiveness from whom? Evaluation of'): 'Chinese Angel Platform',
        (377, 'Industry environments and new venture fo'): 'SBA Establishment Microdata',
        (387, 'The Effects of Education on Business Own'): 'NLSLME',
        (411, 'More than Money: Political Participation'): 'Chilean Business Families Database',
        (415, 'Subsidies, rent seeking and performance:'): 'Chinese NBS',
        (425, 'Seeing parochially and acting locally: S'): 'NCCS',
        (428, 'The Entrepreneurial Decision: Economic T'): 'Council of Economic Advisors',
        (430, 'Nascent ventures competing for start-up '): 'Dutch Film Industry Data',
        (470, 'Exploring start-up event sequences'): 'Reynolds-White Wisconsin Study',
        (492, 'Trends in the market for entrepreneurshi'): 'AOM Placement Roster',
        (494, 'Initial coin offerings (ICOs) to finance'): 'CoinSchedule',
        (507, 'The Long-Run Effects of Communism and Tr'): 'German Statistical Office',
        (526, 'New business formation and the productiv'): 'IAB Establishment Data',
        (532, 'Star entrepreneurs on digital platforms:'): 'Udemy',
        (571, 'Risky business? The survival implication'): 'Canadian Charities Directorate',
        (587, 'The Determinants of Commercialization St'): 'TNS Global',
        (639, 'Franchise turnover and failure: New rese'): 'UFOC',
        (673, 'Firm creation and economic transitions'): 'Polish CSO',
        (707, 'Competitive Strategy and Performance of '): 'CRIQ',
        (729, 'Endowed Positions: Entrepreneurship and '): 'Vesper-Kierulff Database',
        (733, 'How Satisfied Are the Self-Employed: A S'): 'ICPSR',
        (753, 'Improving Survey Response Rates from Chi'): 'OPASTCO',
        (797, 'The Framing of Perceptions of Fairness i'): 'Venture Capital Journal',
        (817, 'Family Involvement, Family Influence, an'): 'SBA Financial Studies',
        (837, 'Partnering strategies and performance of'): 'Toyo Keizai',
        (845, 'Deciding to Persist: Adversity, Values, '): 'Dept of Commerce Business List',
        (898, 'Using R&D cooperative arrangements to le'): 'SEC Filings',
        (900, 'More like each other than anyone else? A'): 'Scheinberg Database',
        (901, 'Does culture endure, or is it malleable?'): 'Scheinberg Database',
        (902, 'Elitists, risk-takers, and rugged indivi'): 'Scheinberg Database',
        (912, 'From cultural entrepreneurship to econom'): 'Chinese Online Publishing Platform',
        (937, 'The impact of early imprinting on the ev'): 'Recap Alliance Database',
        (948, 'Productivity in the Small Business Secto'): 'County Business Patterns',
        (948, 'Defining the inventor-entrepreneur in th'): 'NSF',
        (955, 'Angel investor characteristics that dete'): 'Angel Investor Network',
        (957, 'From distinctiveness to optimal distinct'): 'Crowdfunding Platform',
        (964, 'Multi-Founding Family Firms: Effects on '): 'Anderson Family Firm Dataset',
        (989, 'The effect of a tax training program on '): 'Netherlands Tax Authority',
        (990, 'Screening Practices of New Business Incu'): 'SBA Incubator Directory',
        (1025, 'Actions in words: How entrepreneurs use '): 'Crowdfunding Platform',
        (1035, 'A Real Options Perspective on Entreprene'): 'Center for Responsive Politics',
        (1045, 'Self-employment and allostatic load'): 'MIDUS',
        (1049, 'Growth and Financial Profiles Amongst Ma'): 'Australian BLS',
        (1066, 'Social Ventures from a Resource-Based Pe'): 'Ashoka Fellows',
        (1076, 'The prediction of bankruptcy of small- a'): 'Belgian National Bank',
        (1085, 'Governance, Social Identity, and Entrepr'): 'Fortune 1000',
        (1095, 'Ownership structure, founder leadership,'): 'Norwegian Stock Exchange',
        (1102, 'Factors affecting success and failure of'): 'WAVC Survey',
        (1103, 'A meta-analytic review of effectuation a'): 'JBV Database',
        (1139, 'Taking root in fertile ground: Community'): 'Green America Database',
        (1144, 'Entrepreneurs as prime targets: The role'): 'ENVE Survey',
        (1180, 'The CAGE around cyberspace? How digital '): 'Apple App Store',
        (1187, "Knocking on Heaven's Door? Entrepreneurs"): 'Finnish Register',
        (1193, 'Creative personality, opportunity recogn'): 'TwinsUK',
        (1222, 'When is it time to stop doing the same o'): 'MLB History',
        (1227, "'Harvesting' Through Initial Public Offe"): 'OTC Market',
        (1232, 'Entrepreneurship and Human Capital in Pr'): 'Italian Serie A',
        (1276, 'Self-employment and eudaimonic well-bein'): 'EWCS',
        (1298, 'Entrepreneurship and Financial Incentive'): 'Dutch Education Admin Data',
        (1301, 'Playing the Business Angel: The Impact o'): "Dragon's Den",
        (1307, 'Mortgage affordability and entrepreneurs'): 'UK Business Population Data',
        (1335, "Venture capital's role in financing inno"): 'NSF',
        (1343, 'Institutional quality and market selecti'): 'Vietnamese Enterprise Census',
        (1359, 'How cultural tightness interacts with ge'): 'EDP',
        (1369, 'The F-PEC Scale of Family Influence: Con'): 'German Trade Register',
        (1370, 'From platform growth to platform scaling'): 'Takeaway.com',
        (1423, 'The informal venture capital market: Asp'): 'VCN',
        (1430, 'In order to grow, must the founder go: A'): 'Inc. Magazine',
        (1449, 'Creating opportunities for institutional'): 'MCC Records',
        (1469, 'Founder Characteristics, Start-Up Proces'): 'ICC',
        (1473, 'The aftermarket performance of small fir'): 'OTC Stock Journal',
        (1504, 'Turning a curse into a blessing: Conting'): 'CVSource',
        (1510, "Strategic entrepreneurship's dynamic ten"): 'Video Game Industry Database',
        (1521, "Investors' Reactions to CSR News in Fami"): 'French Stock Market',
        (1575, 'Informal Entrepreneurship and Industry C'): 'Brazilian Business Registry',
        (1604, 'Estimates of The Number of Quasi and Sma'): 'County Business Patterns',
        (1680, 'Financial Strategies of Small, Public Fi'): 'Compact Disclosure',
        (1706, 'Unlisted Businesses are Not Financial Cl'): 'Datex',
        (1735, 'Following in the Footsteps of Others: So'): 'Angel Group Records',
        (1754, 'Internal Versus External Ownership Trans'): 'Swedish Registry of Corporations',
        (1837, 'Democratic Governance, Kinship Networks,'): 'China National Survey',
        # --- AI Pass 2 additions ---
        (397, 'A Financial Profile of Small Retailing F'): 'Financial Research Associates',
        (1646, 'The Value of Patience and Start-up Firms'): 'Corporate Technology Directory; Hoover; International Data Corporation; Moody',
        (24, 'Understanding the Relationship between E'): 'SPIRC',
        (1382, 'Resource mobilization in entrepreneurial'): 'Van de Ven and Walker Study',
        (66, 'Religion, social class, and entrepreneur'): 'Indian Census',
        (262, 'Childhood adversity and the propensity f'): 'Chinese Census',
        (992, 'Sight unseen: The visibility paradox of '): 'US Census Bureau',
        (884, 'False signaling by platform team members'): 'Equity Crowdfunding Platform',
        (1237, 'The Impact of Entrepreneur-CEOs in Micro'): 'MicroRate; Microfinanza; Planet Rating',
        (139, 'Infrastructure Investments and Entrepren'): 'US Census Bureau; Business Dynamics Statistics',
        (432, 'Industry changes in technology and compl'): 'BLS; US Census Bureau',
        (1007, "Do Incumbents' Mergers Influence Entrepr"): 'FCC',
        (1508, 'An institutional logics approach to soci'): 'MFO Lending Database',
        (629, 'Small and Medium-Size Firms in Sweden an'): 'Regional Development Funds Sweden',
    }

    # ── Apply to all papers ──
    skip_values = {'DUPLICATE', 'N/A', 'NON-RESEARCH', 'FILE NOT FOUND', 'OCR FAILED',
                   'NON-RESEARCH (editorial)', 'RETRACTED'}

    df['std_dsType'] = ''
    df['std_dsNamed'] = ''

    for idx in df.index:
        raw = df.at[idx, 'data_source']
        if not pd.notna(raw) or str(raw).strip() in ('', 'nan', 'N/A'):
            continue
        text = str(raw).strip()
        if text.upper() in skip_values:
            continue

        method_text = str(df.at[idx, 'method']) if pd.notna(df.at[idx, 'method']) else ''
        sample_text = str(df.at[idx, 'sample']) if pd.notna(df.at[idx, 'sample']) else ''
        combined_text = f"{text} ||| {method_text} ||| {sample_text}"

        # --- dsType: match against data_source text ---
        type_set = set()
        for cat, compiled in DS_TYPE_COMPILED.items():
            if compiled.search(text):
                type_set.add(cat)

        # If nothing matched in data_source, check method column
        if not type_set:
            for cat, compiled in DS_TYPE_COMPILED.items():
                if compiled.search(method_text):
                    type_set.add(cat)

        # --- dsNamed: match against combined text ---
        named_set = set()
        for canonical, compiled in NAMED_DS_COMPILED.items():
            if compiled.search(combined_text):
                named_set.add(canonical)

        # Apply AI named dataset overrides (always, regardless of regex match)
        pid = int(df.at[idx, 'paper_id']) if pd.notna(df.at[idx, 'paper_id']) else -1
        title = str(df.at[idx, 'title'])[:40] if pd.notna(df.at[idx, 'title']) else ''
        for (oid, tstart), ds_named_override in MANUAL_DS_NAMED_OVERRIDES.items():
            if pid == oid and title.startswith(tstart):
                for n in ds_named_override.split(';'):
                    n = n.strip()
                    if n:
                        named_set.add(n)
                break

        # KEY RULE: if we found named datasets but no dsType, infer Archival/Database
        if named_set and not type_set:
            type_set.add('Archival/Database')

        # Apply manual dsType overrides if nothing matched
        if not type_set:
            for (oid, tstart), (ds_type, ds_named) in MANUAL_DS_OVERRIDES.items():
                if pid == oid and title.startswith(tstart):
                    for t in ds_type.split(';'):
                        t = t.strip()
                        if t:
                            type_set.add(t)
                    for n in ds_named.split(';'):
                        n = n.strip()
                        if n:
                            named_set.add(n)
                    break

        if type_set:
            df.at[idx, 'std_dsType'] = '; '.join(sorted(type_set))
        if named_set:
            df.at[idx, 'std_dsNamed'] = '; '.join(sorted(named_set))

    # ── Validation ──
    has_type = df['std_dsType'].ne('').sum()
    has_named = df['std_dsNamed'].ne('').sum()
    print(f"std_dsType: {has_type}/{len(df)} papers classified ({has_type/len(df)*100:.1f}%)")
    print(f"std_dsNamed: {has_named}/{len(df)} papers with named datasets ({has_named/len(df)*100:.1f}%)")

    # Report distributions
    from collections import Counter
    type_counter = Counter()
    for val in df['std_dsType']:
        if val:
            for v in val.split('; '):
                if v.strip():
                    type_counter[v.strip()] += 1
    print(f"\ndsType distribution:")
    for k, v in type_counter.most_common():
        print(f"  {k}: {v}")

    named_counter = Counter()
    for val in df['std_dsNamed']:
        if val:
            for v in val.split('; '):
                if v.strip():
                    named_counter[v.strip()] += 1
    print(f"\ndsNamed: {len(named_counter)} unique datasets")
    print(f"Top 30:")
    for k, v in named_counter.most_common(30):
        print(f"  {k}: {v}")

    # Empirical coverage
    emp = df[df['std_paper_type'].isin(['Empirical-Quantitative', 'Empirical-Qualitative', 'Empirical-Mixed'])]
    emp_has_ds = emp['data_source'].notna() & (emp['data_source'].astype(str).str.strip() != '')
    emp_has_type = emp['std_dsType'].ne('')
    print(f"\nEmpirical coverage: {emp_has_type.sum()}/{emp_has_ds.sum()} ({emp_has_type.sum()/emp_has_ds.sum()*100:.1f}%)")

    return df


# ============================================================
# VARIABLE 7: std_tpL1 (broad topic) / std_tpL2 (detailed topic)
# ============================================================
# Source: topic_tags (primary), title (fallback)
# Approach: Two-level topic taxonomy with regex-based tag classification
# L1: 15 broad topic domains (multi-valued, semicolon-separated)
# L2: More specific subtopics within each L1 (multi-valued)
# Date finalized: 2026-03-10

def std_topic_L1_L2(df):
    """Standardize topics into L1 (broad) and L2 (specific) categories."""
    print("Standardizing topics (L1/L2)...")

    # ── L2-to-L1 MAPPING ──
    # Each L2 has a list of keyword regex patterns.
    # When a tag matches an L2 pattern, it gets both the L2 label and its parent L1.
    # Structure: { L1: { L2: [regex_patterns] } }

    TOPIC_TAXONOMY = {
        'Entrepreneurial Finance': {
            'Venture Capital': [
                r'\bventure\s+capital\b', r'\bvc\b(?:\s|$)', r'\bventure\s+capitalist',
                r'\bvc\s+(?:fund|firm|invest|back|syndic|network)',
            ],
            'Crowdfunding': [
                r'\bcrowdfund', r'\bkickstarter\b', r'\bindiegogo\b',
                r'\bequity\s+crowdfund', r'\breward.based\s+crowdfund',
                r'\blending.based\s+crowdfund', r'\bcivic\s+crowdfund',
                r'\bcrowdlend',
            ],
            'IPO & Going Public': [
                r'\bipo\b', r'\binitial\s+public\s+offer', r'\bgoing\s+public\b',
                r'\bunderpricing\b', r'\bipo\s+underpricing', r'\bnew\s+issue',
                r'\bstock\s+market\s+list',
            ],
            'Angel Investing': [
                r'\bangel\s+invest', r'\bbusiness\s+angel', r'\bangel\s+group',
                r'\bangel\s+network', r'\bangel\s+capital',
            ],
            'Private Equity': [
                r'\bprivate\s+equity\b', r'\bleveraged\s+buyout', r'\bbuyout\b',
                r'\blbo\b', r'\bmbo\b', r'\bmanagement\s+buyout',
            ],
            'Microfinance': [
                r'\bmicrofinanc', r'\bmicrocredit', r'\bmicro.?lend',
                r'\bmicroenterprise\s+financ', r'\bgrameen\b',
            ],
            'Small Business Finance': [
                r'\bsmall\s+business\s+financ', r'\bcapital\s+structure\b',
                r'\bdebt\s+financ', r'\bbootstrap', r'\btrade\s+credit',
                r'\bbank\s+lend', r'\bloan\s+(?:default|guarantee|access)',
                r'\bcredit\s+(?:access|constraint|ration)',
                r'\bfinancial\s+constraint', r'\bfinancial\s+capital\b',
                r'\bventure\s+financ', r'\bstartup\s+fund', r'\bseed\s+fund',
                r'\bfinancing\b(?!.*crowd)',
            ],
            'Corporate Venture Capital': [
                r'\bcorporate\s+venture\s+capital', r'\bcvc\b',
            ],
            'Investment Decisions': [
                r'\binvestment\s+decision', r'\bscreening\b', r'\bdue\s+diligence',
                r'\bdeal\s+flow', r'\binvestor\s+behavi', r'\binvestment\s+criteria',
                r'\bportfolio\s+(?:management|diversif|selection)',
            ],
            'Signaling & Information Asymmetry': [
                r'\bsignal(?:ing|s)\b', r'\binformation\s+asymmetr',
                r'\bmoral\s+hazard', r'\badverse\s+selection',
                r'\bsignaling\s+theory',
            ],
        },

        'Family Business': {
            'Family Firm Dynamics': [
                r'\bfamily\s+(?:firm|business|enterprise|compan|owned)',
                r'\bfamiliness\b', r'\bfamily\s+involvement',
                r'\bfamily\s+influence', r'\bfamily\s+control',
                r'\bfamily\s+embeddedness', r'\bfamily\s+(?:sme|management)',
            ],
            'Succession': [
                r'\bsuccession\b', r'\bgenerational\b', r'\bintergenerational\b',
                r'\bnext\s+generation', r'\bfamily\s+transition',
                r'\bsuccession\s+planning', r'\bceo\s+succession',
            ],
            'Socioemotional Wealth': [
                r'\bsocioemotional\s+wealth\b', r'\bsew\b',
                r'\bnonfinancial\s+goal', r'\bsocio-emotional',
            ],
            'Family Governance': [
                r'\bfamily\s+governance', r'\bfamily\s+council',
                r'\bfamily\s+constitution', r'\bprimogeniture',
                r'\bboard\s+of\s+director', r'\bboard\s+composition',
                r'\bcorporate\s+governance(?!.*(?:corporate\s+entrepr|intrap))',
                r'\bfamily\s+board',
            ],
            'Stewardship & Altruism': [
                r'\bstewardship\b', r'\baltruism\b', r'\blong.term\s+orientation',
                r'\bfamily\s+(?:altruism|steward)',
            ],
        },

        'Corporate Entrepreneurship': {
            'Corporate Entrepreneurship (general)': [
                r'\bcorporate\s+entrepreneur', r'\bintrapreneurship\b',
                r'\bintrapreneur(?:ial)?\b', r'\bcorporate\s+ventur(?:ing|e)\b(?!.*capital)',
                r'\bnew\s+corporate\s+venture', r'\binternal\s+corporate\s+venture',
            ],
            'Strategic Entrepreneurship': [
                r'\bstrategic\s+entrepreneur', r'\bstrategic\s+renewal',
                r'\bentrepreneurial\s+strateg',
            ],
            'New Product Development': [
                r'\bnew\s+product\s+develop', r'\bproduct\s+innovation',
                r'\bproduct\s+develop', r'\bnpd\b',
            ],
            'Business Model Innovation': [
                r'\bbusiness\s+model\s+innovat', r'\bbusiness\s+model\b',
                r'\bvalue\s+proposition',
            ],
            'Spin-offs & Divestitures': [
                r'\bspin.?off', r'\bdivestiture', r'\bcarve.?out',
                r'\bcorporate\s+spin',
            ],
        },

        'Social Entrepreneurship': {
            'Social Entrepreneurship (general)': [
                r'\bsocial\s+entrepreneur', r'\bsocial\s+venture',
                r'\bsocial\s+enterprise', r'\bsocial\s+innovation',
                r'\bsocial\s+value\s+creat',
            ],
            'Hybrid Organizations': [
                r'\bhybrid\s+organiz', r'\bmission\s+drift',
                r'\bsocial.commercial\s+tension', r'\bdual\s+mission',
                r'\binstitutional\s+logic.*(?:social|hybrid)',
            ],
            'Sustainability & Environment': [
                r'\bsustainab', r'\benvironmental\s+entrepreneur',
                r'\bgreen\s+entrepreneur', r'\bcircular\s+economy',
                r'\bclean\s*tech', r'\benergy\s+entrepreneur',
                r'\bclimate\b.*(?:entrepreneur|innovat)',
            ],
            'Poverty & Development': [
                r'\bpoverty\b', r'\bbase\s+of\s+(?:the\s+)?pyramid',
                r'\bbop\b', r'\bpoverty\s+alleviat', r'\bmicroenterprise\b',
                r'\bprosocial\b', r'\bprosocial\s+ventur',
            ],
        },

        'International Entrepreneurship': {
            'International Entrepreneurship (general)': [
                r'\binternational\s+entrepreneur', r'\binternational\s+business\b',
                r'\binternational\s+(?:new\s+)?venture',
                r'\bfdi\b', r'\bforeign\s+direct\s+invest',
            ],
            'Internationalization': [
                r'\binternationaliz', r'\bexport(?:ing|s|er)?\b',
                r'\bforeign\s+(?:market|expan|sale|entry)',
                r'\binternational\s+(?:expan|market|entry|growth|diversif)',
                r'\bcross-border',
            ],
            'Born Globals': [
                r'\bborn\s+global', r'\binternational\s+new\s+venture',
                r'\binv\b', r'\bearly\s+internationaliz',
                r'\bglobal\s+start.?up',
            ],
            'Emerging & Transition Economies': [
                r'\bemerging\s+(?:econom|market)', r'\btransition\s+econom',
                r'\bdeveloping\s+(?:countr|econom)', r'\bemerging\s+economy',
            ],
            'Cross-Cultural': [
                r'\bcross.cultural', r'\bnational\s+culture',
                r'\bcross.country\b', r'\bcross.national',
                r'\bcultural\s+(?:differ|dimension|value|tight|distance)',
            ],
        },

        'Innovation & Technology': {
            'Innovation (general)': [
                r'^innovation$', r'\binnovation\s+(?:management|process|system|policy)',
                r'\binnovative(?:ness)?\b', r'\bradical\s+innovat',
                r'\bincremental\s+innovat', r'\bdisruptive\s+innovat',
                r'\bopen\s+innovation', r'\buser\s+innovation',
            ],
            'Technology & R&D': [
                r'\br&d\b', r'\bresearch\s+and\s+development',
                r'\btechnology\s+(?:transfer|adopt|commerc|develop|strateg|entrepren)',
                r'\btech(?:nology)?\s+venture', r'\bbiotech',
                r'\bdigital\s+(?:transform|technol|innovat|entrepreneurship)',
                r'\bartificial\s+intelligence', r'\bmachine\s+learning',
                r'\bblockchain\b', r'\bfintech\b',
            ],
            'Academic Entrepreneurship': [
                r'\bacademic\s+entrepreneur', r'\buniversity\s+(?:spin|tech|entrepreneur)',
                r'\bscience.based\s+start', r'\bknowledge\s+spillover',
                r'\btechnology\s+licensing',
            ],
            'Intellectual Property': [
                r'\bpatent', r'\bintellectual\s+property', r'\bip\s+(?:protect|strateg)',
                r'\btrademark', r'\btrade\s+secret',
            ],
            'Creative Destruction': [
                r'\bcreative\s+destruction', r'\bschumpeter',
                r'\bentrepreneurial\s+destruction',
            ],
        },

        'Entrepreneurial Cognition & Psychology': {
            'Cognition & Decision-Making': [
                r'\bentrepreneurial\s+cognit', r'\bcogniti(?:on|ve)\b',
                r'\bdecision.?making\b', r'\bbounded\s+rational',
                r'\bheuristic', r'\bcognitive\s+bias', r'\boverconfiden',
                r'\bescalation\s+of\s+commit', r'\bcounterfactual\s+think',
                r'\battention.based', r'\binformation\s+processing',
                r'\bmental\s+model', r'\bcognitive\s+(?:evaluation|style)',
                r'\bsensemaking\b',
            ],
            'Emotions & Affect': [
                r'\bemotion', r'\baffect\b', r'\bpassion\b',
                r'\bentrepreneurial\s+passion', r'\bfear\s+of\s+failure',
                r'\bgrief\b', r'\benthusiasm\b', r'\banger\b',
            ],
            'Self-Efficacy & Motivation': [
                r'\bself.efficacy\b', r'\bentrepreneurial\s+self.efficac',
                r'\bmotivat', r'\bentrepreneurial\s+intent',
                r'\btheory\s+of\s+planned\s+behav', r'\bneed\s+for\s+achievement',
                r'\bcareer\s+choice', r'\boccupational\s+choice',
                r'\bautonomy\b', r'\bentrepreneurial\s+motivation',
            ],
            'Identity': [
                r'\bidentity\b(?!.*(?:organ|social\s+ent|institution))',
                r'\bidentity\s+work', r'\bentrepreneurial\s+identity',
                r'\brole\s+identity', r'\bnarrative\s+identity',
                r'\bfounder\s+identity',
            ],
            'Well-Being & Health': [
                r'\bwell.?being\b', r'\bmental\s+health', r'\bstress\b',
                r'\bburnout\b', r'\blife\s+satisfaction', r'\bjob\s+satisfaction',
                r'\bwork.life\s+balance', r'\badhd\b', r'\bhealth\b',
                r'\bresilience\b', r'\brecovery\b.*(?:entrepreneur|failure)',
                r'\bpsychological\s+(?:capital|well)',
            ],
            'Personality & Traits': [
                r'\bpersonality\b', r'\bbig\s+five\b', r'\bnarcissi',
                r'\brisk.?taking\b', r'\brisk\s+propensity',
                r'\brisk\s+perception', r'\brisk\s+tolerance',
                r'\bproactiven', r'\bneed\s+for\s+cognition',
                r'\blocus\s+of\s+control', r'\bself.regulat',
                r'\btrait', r'\bdisposit', r'\bagreeableness',
                r'\bconscientious', r'\bopenness\s+to\s+experience',
                r'\bextraversion', r'\bneuroticism',
            ],
            'Creativity': [
                r'\bcreativity\b', r'\bcreative\b(?!.*destruct)',
                r'\bimaginat',
            ],
        },

        'Entrepreneurial Process': {
            'Opportunity Recognition & Creation': [
                r'\bopportunity\s+(?:recognit|identif|discover|creat|develop|evaluat|exploit)',
                r'\bopportunity\b(?!.*cost)', r'\bentrepreneurial\s+opportunit',
                r'\balertness\b', r'\bentrepreneurial\s+alertness',
                r'\bopportunity\s+nexus',
            ],
            'Venture Creation & Nascent': [
                r'\bventure\s+creation', r'\bnascent\s+entrepren',
                r'\bnew\s+venture\s+creation', r'\bventure\s+emergence',
                r'\bnew\s+firm\s+(?:form|creat|found)', r'\bstart.?up\s+process',
                r'\bbusiness\s+gestation', r'\bfounding\b',
                r'\bentrepreneurial\s+(?:action|entry|process|behav)',
                r'\bstart.?up\b(?!.*fund)',
            ],
            'Effectuation & Bricolage': [
                r'\beffectuat', r'\bbricolage\b', r'\bcausation\b',
                r'\bsarasvathy\b', r'\baffordable\s+loss',
                r'\bexperimentation\b',
            ],
            'Entrepreneurial Learning & Failure': [
                r'\bentrepreneurial\s+(?:learn|fail|exit)',
                r'\blearning\s+from\s+failure', r'\bbusiness\s+failure',
                r'\bventure\s+failure', r'\bfailure\b',
                r'\bpivot(?:ing)?\b', r'\brestart\b',
                r'\bexit\b(?!.*ipo)',
            ],
            'Resource Mobilization': [
                r'\bresource\s+(?:mobiliz|acquis|assembl|orchestr)',
                r'\bresourcefulness\b', r'\bresource\s+constraint',
                r'\blegitimacy\b', r'\bliability\s+of\s+(?:newness|smallness|foreignness)',
                r'\bstakeholder\s+(?:legitim|engag)',
            ],
            'Scaling & Growth Process': [
                r'\bscaling\b', r'\bbusiness\s+growth\b',
                r'\bgrowth\s+(?:strateg|process|path)',
                r'\bventure\s+growth', r'\bfirm\s+growth\b',
                r'\bhigh.growth\b', r'\bgazelle',
            ],
        },

        'Strategy & Performance': {
            'Entrepreneurial Orientation': [
                r'\bentrepreneurial\s+orientation', r'\beo\b(?:\s|$)',
                r'\beo.performance', r'\bstrategic\s+orientation',
            ],
            'Firm Performance': [
                r'\bfirm\s+performance', r'\bventure\s+performance',
                r'\bnew\s+venture\s+performance', r'\bperformance\b(?!.*measurement)',
                r'\bfinancial\s+performance', r'\bprofitabilit',
                r'\bproductivit', r'\bfirm\s+value',
                r'\bsme\s+performance',
            ],
            'Competitive Strategy': [
                r'\bcompetitive\s+(?:advantag|strateg)', r'\bstrateg(?:y|ic)\b',
                r'\bbusiness\s+strategy', r'\bstrategic\s+(?:planning|management)',
                r'\bdynamic\s+capabilit', r'\bcompetition\b',
                r'\bmarket\s+entry', r'\bfirst.mover',
            ],
            'Business Models': [
                r'\bbusiness\s+model\b(?!.*innovat)', r'\bvalue\s+creation\b',
                r'\bplatform\b(?!.*crowd)', r'\bfreemium\b',
            ],
            'Firm Survival': [
                r'\bfirm\s+survival', r'\bventure\s+survival',
                r'\bnew\s+venture\s+survival', r'\bsurvival\b',
                r'\bfirm\s+(?:exit|death|mortality)',
                r'\borganizational\s+ecology', r'\bpopulation\s+ecology',
            ],
            'Organizational Design': [
                r'\borganizational\s+(?:design|structure|form|change)',
                r'\borganizational\s+(?:learn|cultur|identit)',
                r'\bformalization\b', r'\bcentralization\b',
                r'\bambidexteri', r'\borganizational\s+capabilit',
            ],
        },

        'Networks & Social Capital': {
            'Social Capital': [
                r'\bsocial\s+capital\b', r'\bsocial\s+network',
                r'\bnetwork(?:s|ing)?\b(?!.*neural)', r'\bentrepreneurial\s+network',
                r'\bstructural\s+hole', r'\bweak\s+tie', r'\bstrong\s+tie',
                r'\bnetwork\s+(?:structur|embed|densit|centrali)',
            ],
            'Trust & Social Exchange': [
                r'\btrust\b', r'\bsocial\s+exchange',
                r'\brelational\s+(?:capital|trust|governance)',
                r'\breciprocit',
            ],
            'Alliances & Partnerships': [
                r'\bstrategic\s+allianc', r'\ballianc', r'\bpartnership',
                r'\bjoint\s+venture', r'\bcooperat(?!.*crowdfund)',
                r'\bsyndication\b', r'\bco.?invest',
            ],
            'Embeddedness': [
                r'\bembeddedness\b', r'\bsocial\s+embeddedness',
                r'\brelational\s+embeddedness', r'\bstructural\s+embeddedness',
            ],
        },

        'Small Business & SMEs': {
            'Small Business Management': [
                r'\bsmall\s+business\b(?!.*financ)', r'\bsme\b(?!.*performance)',
                r'\bsmes\b', r'\bsmall\s+firm', r'\bsmall\s+enterprise',
                r'\bsmall\s+business\s+manage', r'\bmicro.?enterprise',
                r'\bsmall\s+business\s+(?:owner|research|policy|strateg)',
            ],
            'Franchising': [
                r'\bfranchis', r'\bfranchise(?:e|or|ing)?\b',
                r'\bfranchise\s+(?:system|network|turn)',
            ],
            'Family SMEs': [
                r'\bfamily\s+sme',
            ],
        },

        'Gender & Diversity': {
            'Women Entrepreneurship': [
                r'\bwomen\b.*(?:entrepreneur|business|founder)',
                r'\bfemale\s+entrepreneur', r'\bgender\b',
                r'\bgender\s+(?:differ|gap|stereotype|bias|equal|divers|role|effect)',
                r'\bsex\s+differ', r'\bmaternal\b', r'\bmotherhood',
            ],
            'Minority & Immigrant Entrepreneurship': [
                r'\bimmigrant\s+entrepreneur', r'\bethnic\s+entrepreneur',
                r'\bminority\s+entrepreneur', r'\bracial\b', r'\brace\b',
                r'\brefugee\s+entrepreneur', r'\bdiaspora\b',
            ],
            'Diversity': [
                r'\bdiversity\b', r'\binclusi(?:on|ve)', r'\bdisabilit',
                r'\bteam\s+diversity', r'\bworkforce\s+diversity',
            ],
        },

        'Institutions & Context': {
            'Institutional Theory': [
                r'\binstitution(?:al|s)\b(?!.*(?:voids|logics|entrepren|environment))',
                r'\binstitutional\s+theory', r'\bregulatory\s+(?:environ|quality|frame)',
                r'\bformal\s+institution', r'\binstitutional\s+change',
            ],
            'Institutional Voids & Logics': [
                r'\binstitutional\s+(?:void|logic|complex|plural)',
                r'\binstitutional\s+entrepren',
            ],
            'Culture': [
                r'\bculture\b(?!.*(?:cross|organ))', r'\bcultural\s+(?:context|influence|factor)',
                r'\bhofstede\b', r'\bindividualism\b', r'\bcollectivism\b',
                r'\bpower\s+distance', r'\buncertainty\s+avoidance',
            ],
            'Informal Economy': [
                r'\binformal\s+(?:economy|sector|institution|entrepren)',
                r'\bshadow\s+economy', r'\bnecessity\s+entrepreneur',
            ],
            'Context & Geography': [
                r'\bcontext\b', r'\bregional\s+(?:entrepreneur|innovat|develop)',
                r'\bagglomerat', r'\bentrepreneurial\s+ecosystem',
                r'\bcluster\b', r'\bindustrial\s+district',
                r'\brural\s+entrepreneur', r'\burban\s+entrepreneur',
            ],
        },

        'Human Capital & Teams': {
            'Human Capital': [
                r'\bhuman\s+capital\b', r'\beducation\b(?!.*entrepren.*education)',
                r'\bexperience\b(?!.*sampling)', r'\bknowledge\b(?!.*spillov)',
                r'\bskill', r'\bcompetenc',
                r'\bfounder\s+(?:characteristic|experience|human|background)',
                r'\bentrepreneurial\s+(?:experience|human|competen)',
                r'\bprior\s+(?:experience|knowledge)',
            ],
            'Entrepreneurial Teams': [
                r'\bentrepreneurial\s+team', r'\bfounding\s+team',
                r'\bnew\s+venture\s+team', r'\bventure\s+team',
                r'\btop\s+management\s+team', r'\btmt\b',
                r'\bteam\s+(?:composition|formation|dynamic|conflict|cohes)',
                r'\bco.?founder',
            ],
            'Human Resource Management': [
                r'\bhuman\s+resource\b', r'\bhrm\b', r'\bhr\s+(?:practice|manage|strateg)',
                r'\bemployee\s+(?:relat|select|manag|recruit)',
                r'\bcompensation\b', r'\btalent\b(?!.*show)',
            ],
            'Leadership': [
                r'\bleadership\b', r'\bceo\b', r'\bfounder.ceo',
                r'\bentrepreneurial\s+leadership', r'\bmanagerial\b',
            ],
        },

        'Policy & Economic Development': {
            'Entrepreneurship Policy': [
                r'\bentrepreneurship\s+policy', r'\bpublic\s+policy',
                r'\bgovernment\s+policy', r'\bsmall\s+business\s+policy',
                r'\bregulat(?:ion|ory)\b(?!.*(?:self|emotion))',
                r'\btax\b.*(?:policy|incentiv|entrepren)', r'\bsubsid',
            ],
            'Self-Employment': [
                r'\bself.employment\b', r'\boccupational\s+choice',
                r'\blabor\s+(?:market|supply|mobility)',
                r'\bwage\b.*(?:employ|worker|entrepren)',
            ],
            'Economic Development': [
                r'\beconomic\s+(?:develop|growth)\b',
                r'\bwealth\s+creation\b', r'\bjob\s+creation',
                r'\bproductivity\b(?!.*firm)',
            ],
            'Entrepreneurial Ecosystems': [
                r'\bentrepreneurial\s+ecosystem', r'\becosystem\b',
                r'\bincubator', r'\baccelerator\b',
                r'\bscience\s+park', r'\btechnopark',
            ],
            'COVID & Crisis': [
                r'\bcovid', r'\bpandemic\b', r'\bcrisis\b',
                r'\bnatural\s+disaster', r'\bwar\b.*(?:entrepren|econom)',
            ],
        },
    }

    # ── Non-topic tags to skip (theories, methods, meta) ──
    SKIP_PATTERNS = [
        r'^duplicate$', r'^non.research$', r'^editorial$',
        r'^special\s+issue', r'^teaching\s+case$',
        r'^research\s+(?:method|agenda|design)', r'^methodology$',
        r'^qualitative\s+(?:method|research)', r'^quantitative\s+method',
        r'^longitudinal\b', r'^case\s+study$', r'^ethnograph',
        r'^meta.analysis$', r'^systematic\s+review$', r'^literature\s+review$',
        r'^content\s+analysis$', r'^conjoint\s+analysis$',
        r'^grounded\s+theory$', r'^fsqca$', r'^experiment$',
        r'^field\s+development', r'^entrepreneurship\s+(?:research|field|theory)$',
        r'^scale\s+develop', r'^measurement\b', r'^replicat',
        r'^(?:psed|gem|sbdc|nfib|kickstarter)$',  # dataset names, not topics
        r'^(?:china|india|usa|uk|germany|italy|sweden|norway|japan|kenya|russia|canada|europe)$',
        r'^discourse\s+analysis', r'^multilevel\s+analysis',
        r'^(?:theory\s+(?:building|develop|test))',
        r'^(?:process\s+theory|research\s+method)',
    ]
    SKIP_COMPILED = [re.compile(p, re.IGNORECASE) for p in SKIP_PATTERNS]

    # ── Compile taxonomy patterns ──
    TOPIC_COMPILED = {}
    for l1, l2_dict in TOPIC_TAXONOMY.items():
        TOPIC_COMPILED[l1] = {}
        for l2, patterns in l2_dict.items():
            combined = '|'.join(f'(?:{p})' for p in patterns)
            TOPIC_COMPILED[l1][l2] = re.compile(combined, re.IGNORECASE)

    # ── Apply to all papers ──
    df['std_tpL1'] = ''
    df['std_tpL2'] = ''

    for idx in df.index:
        raw = df.at[idx, 'topic_tags']
        if not pd.notna(raw) or str(raw).strip() in ('', 'nan'):
            continue

        # Split tags (handle both comma and semicolon delimiters)
        tags = [t.strip() for t in str(raw).replace(';', ',').split(',') if t.strip()]

        l1_set = set()
        l2_set = set()

        for tag in tags:
            tag_lower = tag.lower().strip()

            # Skip non-topic tags
            if any(sp.search(tag_lower) for sp in SKIP_COMPILED):
                continue

            # Match against taxonomy
            for l1, l2_compiled in TOPIC_COMPILED.items():
                for l2, compiled in l2_compiled.items():
                    if compiled.search(tag_lower):
                        l1_set.add(l1)
                        l2_set.add(l2)

        if l1_set:
            df.at[idx, 'std_tpL1'] = '; '.join(sorted(l1_set))
        if l2_set:
            df.at[idx, 'std_tpL2'] = '; '.join(sorted(l2_set))

    # ── Validation ──
    has_l1 = df['std_tpL1'].ne('').sum()
    has_l2 = df['std_tpL2'].ne('').sum()
    print(f"std_tpL1: {has_l1}/{len(df)} papers classified ({has_l1/len(df)*100:.1f}%)")
    print(f"std_tpL2: {has_l2}/{len(df)} papers classified ({has_l2/len(df)*100:.1f}%)")

    from collections import Counter
    l1_counter = Counter()
    for val in df['std_tpL1']:
        if val:
            for v in val.split('; '):
                if v.strip():
                    l1_counter[v.strip()] += 1
    print(f"\nL1 distribution ({len(l1_counter)} categories):")
    for k, v in l1_counter.most_common():
        print(f"  {k}: {v}")

    l2_counter = Counter()
    for val in df['std_tpL2']:
        if val:
            for v in val.split('; '):
                if v.strip():
                    l2_counter[v.strip()] += 1
    print(f"\nL2 distribution ({len(l2_counter)} categories):")
    for k, v in l2_counter.most_common():
        print(f"  {k}: {v}")

    # Papers with topic_tags but no L1 match
    has_tags = df['topic_tags'].notna() & (df['topic_tags'].astype(str).str.strip() != '') & (df['topic_tags'].astype(str).str.strip() != 'nan')
    no_l1 = has_tags & (df['std_tpL1'] == '')
    print(f"\nPapers with topic_tags but no L1 match: {no_l1.sum()}/{has_tags.sum()} ({no_l1.sum()/has_tags.sum()*100:.1f}%)")

    return df


# ============================================================
# VARIABLE 0p: std_flag
# ============================================================
# Source: title, abstract, paper_type, journal (raw), std_paper_type
# Approach: Flag papers that should be excluded from the web app
# Date finalized: 2026-03-10

def std_flag(df):
    """
    Variable: std_flag
    Source column(s): title, abstract, paper_type, journal (raw), std_paper_type
    Date finalized: 2026-03-10

    Decision rationale:
      - The web app needs a clean database of substantive research papers
      - Several categories of entries should be excluded:
        (1) DUPLICATE entries — same paper appearing multiple times
        (2) OCR/extraction failures — entries with garbled/missing content
        (3) Retracted/corrected papers — no longer valid research
        (4) Non-research content — editorial board listings, TOC, indexes, calls for papers
      - Flag values are mutually exclusive; first matching rule wins (Rules 1-5)
      - Rule 6 (title-based dedup) runs as a second pass after Rules 1-5,
        catching duplicates the extractor created without flagging them
      - Substantive papers (editorials, commentaries, teaching cases) are NOT flagged
        even though they are non-empirical — they are legitimate scholarly content
      - Papers whose std_ fields were recovered from DUPLICATE originals are still
        flagged as duplicates (the recovery was for analysis convenience, not because
        they are distinct papers)

    std_flag values:
      'OK'          — clean paper, include in web app
      'DUPLICATE'   — duplicate entry of another paper (keyword-based or title-based)
      'OCR_FAILED'  — extraction/OCR failure, insufficient content
      'RETRACTED'   — retracted, corrected, or errata
      'NON_RESEARCH' — administrative content, wrong-journal papers, or out-of-scope entries
    """
    print("Standardizing std_flag...")

    flags = []
    counts = {'OK': 0, 'DUPLICATE': 0, 'OCR_FAILED': 0, 'RETRACTED': 0, 'NON_RESEARCH': 0}

    for idx in df.index:
        title = str(df.at[idx, 'title']).lower().strip() if pd.notna(df.at[idx, 'title']) else ''
        abstract = str(df.at[idx, 'abstract']).lower().strip() if pd.notna(df.at[idx, 'abstract']) else ''
        raw_type = str(df.at[idx, 'paper_type']).lower().strip() if pd.notna(df.at[idx, 'paper_type']) else ''
        raw_journal = str(df.at[idx, 'journal']).lower().strip() if pd.notna(df.at[idx, 'journal']) else ''
        std_pt = str(df.at[idx, 'std_paper_type']).strip() if pd.notna(df.at[idx, 'std_paper_type']) else ''

        flag = 'OK'

        # ── Rule 1: DUPLICATE ──
        # Title or abstract starts with "DUPLICATE", or raw journal is "DUPLICATE"
        if (title.startswith('duplicate') or
            abstract.startswith('duplicate') or
            'duplicate' in raw_journal or
            raw_type == 'duplicate'):
            flag = 'DUPLICATE'

        # ── Rule 2: RETRACTED ──
        elif any(k in title or k in raw_type for k in
                 ['retract', 'corrigendum', 'erratum']):
            flag = 'RETRACTED'

        # ── Rule 3: OCR_FAILED ──
        elif any(k in title or k in raw_type for k in
                 ['ocr fail', 'ocr need', 'garbled', 'file not found',
                  'not extracted', 'could not be extracted', 'ocr_fail']):
            flag = 'OCR_FAILED'

        # ── Rule 4: NON_RESEARCH ──
        # Editorial board listings, TOC, indexes, calls for papers, etc.
        # (but NOT editorials, commentaries, teaching cases — those are scholarly)
        elif any(k in title or k in raw_type for k in
                 ['table of contents', 'journal index', 'editorial board',
                  'call for papers', 'reviewer acknowledgement',
                  'acknowledgement of reviewer', "publisher's note"]):
            flag = 'NON_RESEARCH'
        elif raw_type.startswith('non-research') or raw_type.startswith('non_research'):
            flag = 'NON_RESEARCH'

        # ── Rule 5: Wrong journal (not ETP/JBV/SEJ) ──
        # Papers that ended up in the database but belong to a different journal
        elif str(df.at[idx, 'std_journal']).strip() == 'Other':
            flag = 'NON_RESEARCH'

        # ── Rule 6: Catch remaining Other-typed papers not yet flagged ──
        # std_paper_type == 'Other' entries that slipped through rules above
        # These are typically papers with missing/garbled content
        elif std_pt == 'Other':
            # Check if it has any substantive content
            rq = str(df.at[idx, 'std_rq']).strip() if pd.notna(df.at[idx, 'std_rq']) else ''
            findings = str(df.at[idx, 'std_findings']).strip() if pd.notna(df.at[idx, 'std_findings']) else ''
            ab_std = str(df.at[idx, 'std_abstract']).strip() if pd.notna(df.at[idx, 'std_abstract']) else ''
            if len(rq) < 10 and len(findings) < 10 and len(ab_std) < 20:
                flag = 'OCR_FAILED'  # Empty content → treat as extraction failure

        flags.append(flag)
        counts[flag] += 1

    df['std_flag'] = flags

    # ── Rule 7: Title-based deduplication ──
    # After the keyword-based rules, detect remaining duplicates by exact title match.
    # The keyword rules above only catch papers explicitly labeled as "DUPLICATE" in the
    # raw extraction. But the extractor sometimes creates separate entries for the same
    # paper without flagging them. This rule catches those by comparing exact titles
    # among OK-flagged papers, keeping the copy with the most filled fields.
    ok_mask = df['std_flag'] == 'OK'
    ok_df = df[ok_mask].copy()
    ok_df['_title_norm'] = ok_df['title'].str.strip().str.lower()
    dup_titles = ok_df[ok_df.duplicated(subset='_title_norm', keep=False)]['_title_norm'].unique()

    title_dedup_count = 0
    if len(dup_titles) > 0:
        # For each duplicate group, keep the row with the most non-empty std_ columns
        std_cols = [c for c in df.columns if c.startswith('std_') and c != 'std_flag']
        for dup_title in dup_titles:
            group_idx = ok_df[ok_df['_title_norm'] == dup_title].index
            # Score: count of non-empty std_ fields
            scores = []
            for gidx in group_idx:
                filled = sum(1 for c in std_cols if pd.notna(df.at[gidx, c]) and str(df.at[gidx, c]).strip() not in ('', 'nan', 'N/A'))
                scores.append((filled, gidx))
            scores.sort(key=lambda x: -x[0])
            # Keep best (first), flag rest as DUPLICATE
            for _, gidx in scores[1:]:
                df.at[gidx, 'std_flag'] = 'DUPLICATE'
                title_dedup_count += 1
                counts['DUPLICATE'] += 1
                counts['OK'] -= 1

    ok_df.drop(columns=['_title_norm'], inplace=True)

    print(f"\nstd_flag distribution:")
    print(f"  OK (include):     {counts['OK']}")
    print(f"  DUPLICATE:        {counts['DUPLICATE']}  (keyword-based: {counts['DUPLICATE'] - title_dedup_count}, title-dedup: {title_dedup_count})")
    print(f"  OCR_FAILED:       {counts['OCR_FAILED']}")
    print(f"  RETRACTED:        {counts['RETRACTED']}")
    print(f"  NON_RESEARCH:     {counts['NON_RESEARCH']}")
    total_flagged = sum(v for k, v in counts.items() if k != 'OK')
    print(f"  Total flagged:    {total_flagged}")
    print(f"  Total clean:      {counts['OK']}")
    print(f"  Web app papers:   {counts['OK']}/{len(df)} ({counts['OK']/len(df)*100:.1f}%)")

    return df


# ============================================================
# MASTER PIPELINE
# ============================================================
# Add each finalized function here in order.
PIPELINE = [
    raw_data_fixes,
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
    std_flag,
]


def run_pipeline():
    """Run all finalized standardization steps and save output."""
    df = load_raw_data()
    for func in PIPELINE:
        print(f"\n{'='*60}")
        print(f"Running: {func.__name__}")
        print('='*60)
        df = func(df)

    # Remove std_paper_type_detail (superseded by std_method_design/std_method_technique)
    if 'std_paper_type_detail' in df.columns:
        df = df.drop(columns=['std_paper_type_detail'])

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved standardized data to: {OUTPUT_FILE}")
    print(f"Total papers: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    return df


if __name__ == '__main__':
    run_pipeline()
