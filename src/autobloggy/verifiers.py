from __future__ import annotations

from pathlib import Path

from .artifacts import extract_frontmatter, read_claims, read_text, write_json
from .models import VerifierRequest, VerifierVerdict
from .utils import ensure_dir, paragraphs, sentences


VERIFIER_SPECS = [
    ("opening_clarity", True, "prompts/verifiers/opening_clarity.md"),
    ("paragraph_focus", True, "prompts/verifiers/paragraph_focus.md"),
    ("claim_support", True, "prompts/verifiers/claim_support.md"),
    ("unsupported_superlatives", True, "prompts/verifiers/unsupported_superlatives.md"),
    ("voice", True, "prompts/verifiers/voice.md"),
    ("overstatement", True, "prompts/verifiers/overstatement.md"),
    ("specificity", False, "prompts/verifiers/specificity.md"),
    ("so_what", False, "prompts/verifiers/so_what.md"),
    ("filler_hype", False, "prompts/verifiers/filler_hype.md"),
]


def build_verifier_requests(draft_path: Path, claims_path: Path) -> list[VerifierRequest]:
    draft_text = read_text(draft_path)
    _, body = extract_frontmatter(draft_text)
    draft_body = body or draft_text
    claim_doc = read_claims(claims_path)
    opening_excerpt = " ".join(sentences(draft_body)[:3])
    focus_excerpt = "\n\n".join(paragraphs(draft_body)[:3])
    claim_excerpt = "\n".join(f"- {claim.text}" for claim in claim_doc.claims if claim.status == "active")
    whole_excerpt = draft_body[:1600]

    requests: list[VerifierRequest] = []
    for verifier, must_have, prompt_path in VERIFIER_SPECS:
        if verifier == "opening_clarity":
            excerpt = opening_excerpt
        elif verifier == "paragraph_focus":
            excerpt = focus_excerpt
        elif verifier == "claim_support":
            excerpt = claim_excerpt or whole_excerpt
        else:
            excerpt = whole_excerpt
        requests.append(
            VerifierRequest(
                verifier=verifier,
                must_have=must_have,
                prompt_path=prompt_path,
                scope="draft",
                target_excerpt=excerpt,
                instructions="Return only pass or fail with a short rationale and evidence list.",
            )
        )
    return requests


def write_verifier_bundle(attempt_dir: Path, draft_path: Path, claims_path: Path) -> dict[str, str]:
    requests = build_verifier_requests(draft_path, claims_path)
    write_json(attempt_dir / "verifier_requests.json", {"requests": [request.model_dump(mode="json") for request in requests]})
    verdict_dir = ensure_dir(attempt_dir / "verdicts")
    written: dict[str, str] = {"requests": str(attempt_dir / "verifier_requests.json")}
    for request in requests:
        verdict_path = verdict_dir / f"{request.verifier}.json"
        if not verdict_path.exists():
            verdict = VerifierVerdict(
                verifier=request.verifier,
                must_have=request.must_have,
                scope=request.scope,
            )
            write_json(verdict_path, verdict.model_dump(mode="json"))
        written[request.verifier] = str(verdict_path)
    return written

