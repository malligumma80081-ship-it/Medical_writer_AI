class ClaimExtractor:

    GROUPS = [
        "primary_efficacy_outcomes",
        "secondary_outcomes",
        "safety_findings",
        "study_limitations",
    ]

    def extract(self, summary: dict) -> list[dict]:

        claims = []

        for group in self.GROUPS:

            findings = summary.get(group, [])

            for index, finding in enumerate(findings):

                claim_text = finding.get("finding", "").strip()

                if not claim_text:
                    continue

                claims.append({
                    "claim_id": f"{group}_{index}",
                    "claim": claim_text,
                    "citation_ids": finding.get(
                        "citation_ids", []
                    ),
                    "group": group,
                })

        return claims