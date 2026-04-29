---
name: transcribe
description: Run local speech transcription from audio or video files with ffmpeg media prep and a local Parakeet (default) or Voxtral model. Use when a user wants a plain text transcript from a recording without sending audio to a cloud API.
compatibility: Requires macOS on Apple Silicon, uv, ffmpeg, and enough disk for model caches.
---

# Transcribe

Use this skill to transcribe local audio or video files without sending media to a cloud API.

Normalize media with `ffmpeg`, then run the local ASR script. Use Parakeet by default; use Voxtral only when the user asks for a smoother, less verbatim transcript.

## Default Stack

- Media prep: `ffmpeg` to 16 kHz mono PCM WAV
- ASR: `mlx-community/parakeet-tdt-0.6b-v3` via `parakeet-mlx`
- Output: plain text `.txt`

## Prerequisites

- `ffmpeg` on `PATH`
- `uv`
- Enough free disk for model caches

## Commands

```bash
uv run --with parakeet-mlx python skills/transcribe/scripts/transcribe_local.py INPUT --output OUTPUT.txt
uv run --with mlx-voxtral python skills/transcribe/scripts/transcribe_local.py INPUT --engine voxtral --output OUTPUT.txt
```

Run long transcriptions in the background.

## Useful Flags

- `--engine {parakeet,voxtral}` — default `parakeet`
- `--model REPO` — override the default model for the chosen engine
- `--start 00:01:30`
- `--duration 00:00:20`
- `--language en` / `--language auto` (Voxtral only; Parakeet is monolingual EN by default)
- `--audio-output tmp/clip.wav`
- `--dtype {bfloat16,float16,float32}` — defaults: `bfloat16` for Parakeet, `float16` for Voxtral
- `--chunk-size N` — seconds per chunk (Parakeet default 120, Voxtral default 30)
