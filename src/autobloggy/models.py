from pathlib import Path

from pydantic import BaseModel, Field


class PresetManifest(BaseModel):
    extends: str | None = None
    defaults: dict[str, str] = Field(default_factory=dict)
    definitions: dict[str, dict[str, str]] = Field(default_factory=dict)


class ResolvedPresetResource(BaseModel):
    dimension: str
    key: str
    path: Path


class ResolvedPreset(BaseModel):
    name: str
    root: Path
    selections: dict[str, str] = Field(default_factory=dict)
    resources: dict[str, ResolvedPresetResource] = Field(default_factory=dict)


class BriefSectionDef(BaseModel):
    label: str
    prompt: str
    preamble: str | None = None


class IntakeDepthConfig(BaseModel):
    ask: list[str] = Field(default_factory=list)
    omit: list[str] = Field(default_factory=list)
    discovery: str = "auto"
    require_selections: list[str] = Field(default_factory=list)


class SourceManifestEntry(BaseModel):
    id: str
    kind: str
    description: str
    path: str
    origins: list[str] = Field(default_factory=list)
    normalized: bool = False


class SourceManifest(BaseModel):
    sources: list[SourceManifestEntry] = Field(default_factory=list)


class DiscoveryMeta(BaseModel):
    policy: str = "auto"
    ran: bool = False


class PostMeta(BaseModel):
    slug: str
    preset: str
    intake_depth: str | None = None
    status: str = "briefing"
    created_at: str
    brief_approved_at: str | None = None
    selections: dict[str, str] = Field(default_factory=dict)
    discovery: DiscoveryMeta = Field(default_factory=DiscoveryMeta)


class PostPaths(BaseModel):
    slug: str
    root: Path
    meta: Path
    blog_brief: Path
    inputs_root: Path
    inputs_raw_root: Path
    prepared_root: Path
    prepared_manifest: Path
    prepared_intake_root: Path
    prepared_intake_source: Path
    prepared_discovery_root: Path
    prepared_discovery_source: Path
    draft: Path
    verify_root: Path
    verify_pack: Path
