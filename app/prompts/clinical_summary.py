CLINICAL_SUMMARY_PROMPT = """
Prepare a structured summary of the clinical study.

Include:

1. Study overview
2. Study design and population
3. Primary efficacy outcomes
4. Secondary efficacy outcomes
5. Safety findings
6. Study limitations
7. Evidence gaps

Preserve the study's reported terminology.

Do not assume that a statistically significant
result is necessarily clinically significant.

Do not invent missing study characteristics.
"""