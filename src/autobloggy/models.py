from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ClaimVerification(BaseModel):
    claim_fingerprint: str | None = None
    status: Literal["needs_rerun", "pass", "fail"] = "needs_rerun"
    reason: str = "new"
    checked_at: str | None = None


class ClaimRecord(BaseModel):
    id: str
    text: str
    section: str
    source_ids: list[str] = Field(default_factory=list)
    status: Literal["active", "inactive"] = "active"
    last_verification: ClaimVerification = Field(default_factory=ClaimVerification)


class ClaimsDocument(BaseModel):
    claims: list[ClaimRecord] = Field(default_factory=list)


class SourceSnippet(BaseModel):
    id: str
    text: str


class SourceRecord(BaseModel):
    id: str
    title: str
    kind: Literal["local_markdown", "local_pptx", "url", "manual"] = "manual"
    locator: str
    notes: str | None = None
    snippets: list[SourceSnippet] = Field(default_factory=list)


class SourcesDocument(BaseModel):
    sources: list[SourceRecord] = Field(default_factory=list)


class CheckResult(BaseModel):
    id: str
    passed: bool
    severity: Literal["blocker", "warning"] = "blocker"
    details: str


class CheckSummary(BaseModel):
    target: str
    generated_at: str
    results: list[CheckResult]
    blocker_count: int
    readability_penalty: int
    banned_pattern_count: int


class VerifierRequest(BaseModel):
    verifier: str
    must_have: bool
    prompt_path: str
    scope: str
    target_excerpt: str
    instructions: str


class VerifierVerdict(BaseModel):
    verifier: str
    must_have: bool
    scope: str
    status: Literal["needs_review", "pass", "fail"] = "needs_review"
    rationale: str = ""
    evidence: list[str] = Field(default_factory=list)


class EvaluationSummary(BaseModel):
    run_id: str
    attempt_id: str
    target: str
    blocker_count: int
    must_have_verifier_fail_count: int
    claim_issue_count: int
    improvement_fail_count: int
    readability_penalty: int
    banned_pattern_count: int
    passes_baseline: bool
    acceptance_tuple: tuple[int, int, int, int, int, int]
    missing_verdicts: list[str] = Field(default_factory=list)


class RunState(BaseModel):
    run_id: str
    latest_attempt: int = 0
    accepted_summary: EvaluationSummary | None = None


class PostPaths(BaseModel):
    slug: str
    root: Path
    brief: Path
    outline: Path
    claims: Path
    sources: Path
    draft: Path
    runs: Path

