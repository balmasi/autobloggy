from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


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


class EvaluationSummary(BaseModel):
    run_id: str
    attempt_id: str
    target: str
    blocker_count: int
    must_have_verifier_fail_count: int
    improvement_fail_count: int
    readability_penalty: int
    banned_pattern_count: int
    passes_baseline: bool
    acceptance_tuple: tuple[int, int, int, int, int]
    missing_verdicts: list[str] = Field(default_factory=list)


class RunState(BaseModel):
    run_id: str
    latest_attempt: int = 0
    accepted_summary: EvaluationSummary | None = None


class PresetPaths(BaseModel):
    name: str
    root: Path
    strategy_template: Path
    writing_guide: Path
    brand_guide: Path


class InputTextSource(BaseModel):
    path: str
    kind: str
    title: str = ""
    headings: list[str] = Field(default_factory=list)
    extracted_from: str | None = None


class InputVisualSource(BaseModel):
    id: str
    path: str
    kind: str
    source_file: str
    source_locator: str | None = None
    width_px: int | None = None
    height_px: int | None = None
    caption: str = ""
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class InputManifest(BaseModel):
    generated_at: str
    brief: str | None = None
    raw_text_sources: list[InputTextSource] = Field(default_factory=list)
    extracted_text_sources: list[InputTextSource] = Field(default_factory=list)
    raw_visual_sources: list[InputVisualSource] = Field(default_factory=list)
    extracted_visual_sources: list[InputVisualSource] = Field(default_factory=list)
    canonical_input: str = ""


class PostPaths(BaseModel):
    slug: str
    root: Path
    inputs_root: Path
    user_provided_root: Path
    user_readme: Path
    user_brief: Path
    user_raw_root: Path
    extracted_root: Path
    extracted_text_root: Path
    extracted_visual_root: Path
    prepared_root: Path
    prepared_input: Path
    input_manifest: Path
    visuals_root: Path
    visuals_requests: Path
    legacy_main_input: Path
    legacy_supporting_root: Path
    discovery_root: Path
    discovery_summary: Path
    strategy: Path
    outline: Path
    draft: Path
    runs: Path
