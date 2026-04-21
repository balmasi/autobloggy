from __future__ import annotations

from autobloggy.models import ClaimRecord, ClaimsDocument
from autobloggy.prepare import merge_claims


def test_merge_claims_preserves_ids_for_unchanged_claims() -> None:
    existing = ClaimsDocument(
        claims=[
            ClaimRecord(
                id="clm-001",
                text="A checklist cut handoff time",
                section="opening",
                source_ids=["src-seed"],
            )
        ]
    )

    merged = merge_claims(existing, [("A checklist cut handoff time", "opening")], ["src-seed"])

    assert merged.claims[0].id == "clm-001"


def test_merge_claims_marks_removed_claims_inactive() -> None:
    existing = ClaimsDocument(
        claims=[
            ClaimRecord(
                id="clm-001",
                text="A checklist cut handoff time",
                section="opening",
                source_ids=["src-seed"],
            )
        ]
    )

    merged = merge_claims(existing, [("A new claim", "opening")], ["src-seed"])

    assert {claim.id for claim in merged.claims} == {"clm-001", "clm-002"}
    removed = next(claim for claim in merged.claims if claim.id == "clm-001")
    assert removed.status == "inactive"

