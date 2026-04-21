#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


DEFAULT_MODEL = "Aayush9029/voxtral-mini-3b-8bit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize media with ffmpeg and transcribe it locally with Voxtral."
    )
    parser.add_argument("input", help="Path or URL to an audio/video file.")
    parser.add_argument(
        "--output",
        help="Transcript text file path. Defaults to <input-stem>.txt in the current directory.",
    )
    parser.add_argument(
        "--audio-output",
        help="Optional path to keep the normalized 16 kHz mono WAV file.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Voxtral model repo or local path. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="Language code for transcription, or 'auto' to let Voxtral detect it.",
    )
    parser.add_argument(
        "--dtype",
        default="float16",
        choices=("float16", "bfloat16", "float32"),
        help="MLX dtype to request when loading the model.",
    )
    parser.add_argument(
        "--start",
        help="Optional ffmpeg start offset, for example 00:01:30.",
    )
    parser.add_argument(
        "--duration",
        help="Optional ffmpeg clip duration, for example 00:00:20.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=1024,
        help="Maximum transcript tokens to generate.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. Keep at 0.0 for deterministic transcripts.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p used during generation.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print normalization and runtime details to stderr.",
    )
    return parser.parse_args()


def default_output_path(input_value: str) -> Path:
    if "://" in input_value:
        return Path("transcript.txt")
    return Path.cwd() / f"{Path(input_value).stem}.txt"


def ensure_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise SystemExit("ffmpeg was not found on PATH.")


def run_ffmpeg(
    ffmpeg: str,
    input_value: str,
    output_audio: Path,
    *,
    start: str | None,
    duration: str | None,
) -> None:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    if start:
        cmd.extend(["-ss", start])
    cmd.extend(["-i", input_value])
    if duration:
        cmd.extend(["-t", duration])
    cmd.extend(
        [
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(output_audio),
        ]
    )
    subprocess.run(cmd, check=True)


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str,
    language: str | None,
    dtype_name: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    try:
        import mlx.core as mx
        from mlx_voxtral import VoxtralProcessor, load_voxtral_model
    except ImportError as exc:
        raise SystemExit(
            "mlx-voxtral is missing. Run this script with "
            "`uv run --with mlx-voxtral python ...`."
        ) from exc

    dtype = getattr(mx, dtype_name)
    model, _ = load_voxtral_model(model_name, dtype=dtype)
    processor = VoxtralProcessor.from_pretrained(model_name)
    inputs = processor.apply_transcrition_request(
        audio=str(audio_path),
        language=language,
    )
    output_ids = model.generate(
        input_ids=inputs.input_ids,
        input_features=inputs.input_features,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    prompt_tokens = int(inputs.input_ids.shape[1])
    transcript = processor.decode(
        output_ids[0, prompt_tokens:],
        skip_special_tokens=True,
    )
    return transcript.strip()


def main() -> int:
    args = parse_args()
    ffmpeg = ensure_ffmpeg()

    output_path = Path(args.output) if args.output else default_output_path(args.input)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    language = None if args.language.lower() == "auto" else args.language

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="voxtral-transcribe-") as tmpdir:
        normalized_audio = (
            Path(args.audio_output)
            if args.audio_output
            else Path(tmpdir) / "normalized.wav"
        )

        if args.verbose:
            print(f"Normalizing media with ffmpeg: {normalized_audio}", file=sys.stderr)

        run_ffmpeg(
            ffmpeg,
            args.input,
            normalized_audio,
            start=args.start,
            duration=args.duration,
        )

        if args.verbose:
            print(f"Loading Voxtral model: {args.model}", file=sys.stderr)

        transcript = transcribe_audio(
            normalized_audio,
            model_name=args.model,
            language=language,
            dtype_name=args.dtype,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
        )

    output_path.write_text(transcript + "\n", encoding="utf-8")
    print(transcript)

    if args.verbose:
        elapsed = time.time() - started
        print(f"Wrote transcript to {output_path}", file=sys.stderr)
        print(f"Completed in {elapsed:.2f}s", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
