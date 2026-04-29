#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


PARAKEET_DEFAULT_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"
VOXTRAL_DEFAULT_MODEL = "mzbac/voxtral-mini-3b-4bit-mixed"
DEFAULT_ENGINE = "parakeet"
# Voxtral's native window is 30 s; feeding more than one window at once hangs.
VOXTRAL_CHUNK_SIZE = 30
# Parakeet handles long files natively; chunk to bound memory on very long inputs.
PARAKEET_CHUNK_SIZE = 120
PARAKEET_OVERLAP = 15.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize media with ffmpeg and transcribe it locally with Parakeet or Voxtral."
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
        "--engine",
        default=DEFAULT_ENGINE,
        choices=("parakeet", "voxtral"),
        help=(
            f"ASR engine. Default: {DEFAULT_ENGINE} "
            "(parakeet-mlx, ~8x faster, verbatim). "
            "voxtral uses mlx-voxtral and produces editorial-style prose."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Model repo or local path. "
            f"Default for parakeet: {PARAKEET_DEFAULT_MODEL}. "
            f"Default for voxtral: {VOXTRAL_DEFAULT_MODEL}."
        ),
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="Language code for transcription, or 'auto' to let the model detect it. Voxtral only.",
    )
    parser.add_argument(
        "--dtype",
        default=None,
        choices=("float16", "bfloat16", "float32"),
        help="MLX dtype to request when loading the model. Defaults: bfloat16 for parakeet, float16 for voxtral.",
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
        "--chunk-size",
        type=int,
        default=None,
        help=(
            "Seconds per transcription chunk. "
            f"Default: {VOXTRAL_CHUNK_SIZE}s for voxtral (native window), "
            f"{PARAKEET_CHUNK_SIZE}s for parakeet."
        ),
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=1024,
        help="Maximum transcript tokens to generate per chunk. Voxtral only.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. Voxtral only. Keep at 0.0 for deterministic transcripts.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p used during generation. Voxtral only.",
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


def get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def transcribe_parakeet(
    model_name: str,
    dtype_name: str,
    audio_path: Path,
    *,
    chunk_size: int,
    verbose: bool,
) -> str:
    try:
        import mlx.core as mx
        from parakeet_mlx import from_pretrained
    except ImportError as exc:
        raise SystemExit(
            "parakeet-mlx is missing. Run this script with "
            "`uv run --with parakeet-mlx python ...`."
        ) from exc

    if verbose:
        print(f"Loading Parakeet model: {model_name}", file=sys.stderr)
    dtype = getattr(mx, dtype_name)
    model = from_pretrained(model_name, dtype=dtype)

    if verbose:
        print(
            f"Transcribing with chunk_duration={chunk_size}s, overlap={PARAKEET_OVERLAP}s …",
            file=sys.stderr,
        )
    result = model.transcribe(
        str(audio_path),
        chunk_duration=float(chunk_size),
        overlap_duration=PARAKEET_OVERLAP,
    )
    text = result.text if hasattr(result, "text") else str(result)
    return text.strip()


def transcribe_voxtral(
    model_name: str,
    dtype_name: str,
    audio_path: Path,
    tmppath: Path,
    ffmpeg: str,
    *,
    chunk_size: int,
    language: str | None,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    verbose: bool,
) -> str:
    try:
        import mlx.core as mx
        from mlx_voxtral import VoxtralProcessor, load_voxtral_model
    except ImportError as exc:
        raise SystemExit(
            "mlx-voxtral is missing. Run this script with "
            "`uv run --with mlx-voxtral python ...`."
        ) from exc

    if verbose:
        print(f"Loading Voxtral model: {model_name}", file=sys.stderr)
    dtype = getattr(mx, dtype_name)
    model, _ = load_voxtral_model(model_name, dtype=dtype)
    processor = VoxtralProcessor.from_pretrained(model_name)

    duration_sec = get_audio_duration(audio_path)
    n_chunks = math.ceil(duration_sec / chunk_size)
    if verbose:
        print(
            f"Audio duration: {duration_sec:.1f}s → {n_chunks} chunk(s) of {chunk_size}s",
            file=sys.stderr,
        )

    parts: list[str] = []
    for i in range(n_chunks):
        start_sec = i * chunk_size
        chunk_path = tmppath / f"chunk_{i:04d}.wav"
        run_ffmpeg(
            ffmpeg,
            str(audio_path),
            chunk_path,
            start=str(start_sec),
            duration=str(chunk_size),
        )
        if verbose:
            print(f"  Transcribing chunk {i + 1}/{n_chunks} …", file=sys.stderr)
        inputs = processor.apply_transcrition_request(
            audio=str(chunk_path),
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
        parts.append(
            processor.decode(
                output_ids[0, prompt_tokens:],
                skip_special_tokens=True,
            ).strip()
        )

    return " ".join(parts)


def main() -> int:
    args = parse_args()
    ffmpeg = ensure_ffmpeg()

    if args.engine == "parakeet":
        model_name = args.model or PARAKEET_DEFAULT_MODEL
        dtype_name = args.dtype or "bfloat16"
        chunk_size = args.chunk_size or PARAKEET_CHUNK_SIZE
    else:
        model_name = args.model or VOXTRAL_DEFAULT_MODEL
        dtype_name = args.dtype or "float16"
        chunk_size = args.chunk_size or VOXTRAL_CHUNK_SIZE

    output_path = Path(args.output) if args.output else default_output_path(args.input)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    language = None if args.language.lower() == "auto" else args.language

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="transcribe-") as tmpdir:
        tmppath = Path(tmpdir)
        normalized_audio = (
            Path(args.audio_output)
            if args.audio_output
            else tmppath / "normalized.wav"
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

        if args.engine == "parakeet":
            transcript = transcribe_parakeet(
                model_name,
                dtype_name,
                normalized_audio,
                chunk_size=chunk_size,
                verbose=args.verbose,
            )
        else:
            transcript = transcribe_voxtral(
                model_name,
                dtype_name,
                normalized_audio,
                tmppath,
                ffmpeg,
                chunk_size=chunk_size,
                language=language,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                verbose=args.verbose,
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
