---
name: autobloggy-transcribe
description: Run local speech transcription from audio or video files with ffmpeg media prep and a local Voxtral model. Use when a user wants a plain text transcript from a recording without sending audio to a cloud API.
---

# Autobloggy Transcribe

Use this skill for local transcription on Apple Silicon.

This workflow always normalizes media with `ffmpeg` first, then runs Voxtral locally with `mlx-voxtral`.

If the task also needs visual video inspection, read `.agents/skills/ffmpeg-analyse-video/SKILL.md`.

## Default Stack

- Media prep: `ffmpeg` to 16 kHz mono PCM WAV
- ASR: `Aayush9029/voxtral-mini-3b-8bit`
- Output: plain text `.txt`

Use this default unless the user explicitly asks for another Voxtral variant. `Voxtral-Small-24B` is not the practical local choice on this Mac; the quantized Voxtral Mini path worked locally.

## Prerequisites

- `ffmpeg` on `PATH`
- `uv`
- Apple Silicon with enough free disk for the first model download

## Command

```bash
uv run --with mlx-voxtral python skills/autobloggy-transcribe/scripts/transcribe_local.py INPUT --output OUTPUT.txt
```

## Useful Flags

- `--start 00:01:30`
- `--duration 00:00:20`
- `--language en`
- `--language auto`
- `--audio-output tmp/clip.wav`
- `--model Aayush9029/voxtral-mini-3b-8bit`
- `--dtype float16`

## Test Command

```bash
uv run --with mlx-voxtral python skills/autobloggy-transcribe/scripts/transcribe_local.py posts/nps-alternatives/IMG_3399.denoised.mp4 --start 00:00:00 --duration 00:00:20 --language en --output tmp/asr/voxtral-test.txt --audio-output tmp/asr/voxtral-test.wav --verbose
```

That command should leave both a normalized WAV file and a transcript text file under `tmp/asr/`.
