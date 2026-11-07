EFFICACY_SUMMARY_PROMPT = """
Prepare a scientific summary focused on efficacy.

Extract, where available:

- Primary endpoint
- Secondary endpoints
- Treatment groups
- Sample sizes
- Baseline measurements
- Follow-up duration
- Reported outcome values
- Effect sizes
- Confidence intervals
- P-values

Preserve exact numerical values and units.

If an efficacy result is unavailable in the
retrieved evidence, report it as not available.
"""