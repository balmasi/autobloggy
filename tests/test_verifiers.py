from __future__ import annotations

from autobloggy.verifiers import marker_count, run_programmatic, strip_markers
from autobloggy.verifiers.programmatic import (
    code_fences_tagged,
    heading_order,
    image_caption_alt,
    one_h1,
)


def _wrap(main_inner: str) -> str:
    return f"<!doctype html><html><head><title>t</title></head><body><main>{main_inner}</main></body></html>"


def test_strip_markers_removes_fb_comments() -> None:
    html = _wrap("<p>hi <!-- fb[voice]: too corporate --></p>")
    cleaned = strip_markers(html)
    assert "fb[" not in cleaned
    assert "<p>hi </p>" in cleaned


def test_one_h1_flags_extras() -> None:
    html = _wrap("<h1>One</h1><h1>Two</h1>")
    out, inserted = one_h1(html)
    assert inserted == ["one_h1"]
    assert "fb[one_h1]" in out


def test_one_h1_clean(monkeypatch) -> None:
    html = _wrap("<h1>Only</h1><p>x</p>")
    out, inserted = one_h1(html)
    assert inserted == []
    assert "fb[" not in out


def test_heading_order_flags_jumps() -> None:
    html = _wrap("<h1>a</h1><h2>b</h2><h4>c</h4>")
    out, inserted = heading_order(html)
    assert "heading_order" in inserted
    assert "fb[heading_order]" in out


def test_code_fences_tagged_flags_missing_class() -> None:
    html = _wrap("<pre><code>x = 1</code></pre>")
    out, inserted = code_fences_tagged(html)
    assert inserted == ["code_fences_tagged"]
    assert "fb[code_fences_tagged]" in out


def test_code_fences_tagged_passes_with_language_class() -> None:
    html = _wrap('<pre><code class="language-python">x = 1</code></pre>')
    _, inserted = code_fences_tagged(html)
    assert inserted == []


def test_image_caption_alt_flags_missing_alt() -> None:
    html = _wrap('<img src="x.png">')
    out, inserted = image_caption_alt(html)
    assert "image_caption_alt" in inserted
    assert "fb[image_caption_alt]" in out


def test_image_caption_alt_flags_figure_without_caption(repo_root, monkeypatch) -> None:
    monkeypatch.chdir(repo_root)
    html = _wrap('<figure><img src="x.png" alt="real"></figure>')
    _, inserted = image_caption_alt(html)
    assert "image_caption_alt" in inserted


def test_run_programmatic_chains_checks(repo_root, monkeypatch) -> None:
    monkeypatch.chdir(repo_root)
    html = _wrap('<h1>One</h1><h1>Two</h1><figure><img src="x.png"></figure>')
    out, inserted = run_programmatic(html)
    rule_ids = set(inserted)
    assert "one_h1" in rule_ids
    assert "image_caption_alt" in rule_ids
    assert marker_count(out) >= 3
