class CitationValidator:

    def validate(
        self,
        summary,
        sources: list[dict],
    ) -> dict:

        valid_ids = {
            source["citation_id"]
            for source in sources
        }

        findings = (
            summary.primary_efficacy_outcomes
            + summary.secondary_outcomes
            + summary.safety_findings
            + summary.study_limitations
        )

        errors = []
        uncited_findings = []

        for index, finding in enumerate(findings):

            if not finding.citation_ids:
                uncited_findings.append(index)
                continue

            for citation_id in finding.citation_ids:

                if citation_id not in valid_ids:
                    errors.append(
                        f"Unknown citation ID: {citation_id}"
                    )

        return {
            "is_valid": (
                not errors and not uncited_findings
            ),
            "errors": errors,
            "uncited_findings": uncited_findings,
            "valid_source_ids": sorted(valid_ids),
        }