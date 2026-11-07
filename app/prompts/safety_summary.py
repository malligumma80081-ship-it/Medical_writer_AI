SAFETY_SUMMARY_PROMPT = """
Prepare a scientific summary focused on safety.

Extract, where available:

- Adverse events
- Serious adverse events
- Treatment discontinuations
- Deaths reported in the study
- Laboratory abnormalities
- Safety monitoring duration
- Reported safety conclusions

Preserve event counts, percentages and denominators.

Do not interpret an unreported event as an event
that did not occur.

Do not conclude that a treatment is safe merely
because no adverse event appears in the retrieved
passages.
"""