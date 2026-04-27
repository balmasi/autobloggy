from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class PresetPaths(BaseModel):
    name: str
    root: Path
    strategy_template: Path
    writing_guide: Path
    brand_guide: Path
    template_html: Path


class InputTextSource(BaseModel):
    path: str
    kind: str
    title: str = ""
    headings: list[str] = Field(default_factory=list)


class InputManifest(BaseModel):
    generated_at: str
    brief: str | None = None
    raw_text_sources: list[InputTextSource] = Field(default_factory=list)
    canonical_input: str = ""


class PostMeta(BaseModel):
    slug: str
    preset: str
    status: str = "drafting"
    created_at: str
    approved_at: str | None = None
    discovery_decision: str | None = None
    discovery_decided_at: str | None = None


class PostPaths(BaseModel):
    slug: str
    root: Path
    meta: Path
    inputs_root: Path
    user_provided_root: Path
    user_readme: Path
    user_brief: Path
    user_raw_root: Path
    extracted_root: Path
    prepared_root: Path
    prepared_input: Path
    input_manifest: Path
    discovery_root: Path
    discovery_summary: Path
    strategy: Path
    outline: Path
    draft: Path
    verify_root: Path
    verify_pack: Path
    export_html_root: Path
