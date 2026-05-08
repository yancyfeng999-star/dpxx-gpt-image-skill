<div align="center">

# DPXX GPT Image Skill

RootFlowAI-powered GPT-Image-2 image generation workflow for DPXX.

[English](README.md) · [简体中文](README.zh.md) · [Release v1.1.1](https://github.com/yancyfeng999-star/dpxx-gpt-image-skill/releases/tag/v1.1.1)

![Version](https://img.shields.io/badge/version-v1.1.1-blue)
![Provider](https://img.shields.io/badge/provider-RootFlowAI-111827)
![Model](https://img.shields.io/badge/model-GPT--Image--2-10b981)
![Python](https://img.shields.io/badge/python-3.x-3776ab)

</div>

## Overview

`dpxx-gpt-image-skill` is a standalone DPXX image-generation skill for GPT-Image-2 models through RootFlowAI. It supports text-to-image, reference-image generation, and image editing.

This repository is independent from the Gemini skill. A customer can install this GPT skill by itself when the preferred output style is GPT-Image-2.

## Highlights

- Single-provider GPT workflow through RootFlowAI
- Shared DPXX prompt, request, download, and output conventions
- Text-to-image, reference-image generation, and edit workflows
- Version-controlled skill metadata, script metadata, and release tags
- Public documentation with private runtime configuration kept outside the repository

## Model Map

| Resolution | Model |
| --- | --- |
| 1K | `gpt-image-2-count` |
| 2K | `gpt-image-2-hd-count` |
| 4K | `gpt-image-2-4k-count` |

Recommended default: `gpt-image-2-hd-count`. Use `gpt-image-2-count` for quick composition checks.

## Aspect Ratios

1K and 2K support:

```text
1:1  3:2  2:3  4:3  3:4  5:4  4:5  16:9  9:16  2:1  1:2  21:9  9:21
```

4K supports:

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

## Quick Start

Configure RootFlowAI authentication through your runtime environment before running. Keep private credentials outside the repository.

```bash
python3 scripts/generate_image.py \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "A clean product hero image on a plain background." \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix gpt
```

## Workflow

1. Pick the GPT model that matches the target resolution.
2. Write the prompt using the DPXX prompt rules in `SKILL.md`.
3. Run `scripts/generate_image.py` with `--profile gpt`.
4. Review the generated image and rerun with a refined prompt when needed.
5. Keep version files aligned before publishing workflow changes.

## Versioning

Current version: `v1.1.1`

- `SKILL.md` frontmatter is the source of truth.
- `references/VERSION.md` and `scripts/VERSION.md` must match `SKILL.md`.
- GitHub release tags use the same semantic version, for example `v1.1.1`.
- Bump the version when scripts, model mapping, or user-facing workflow behavior changes.

## Repository Layout

```text
SKILL.md                 Skill instructions
USER_GUIDE.md            User-facing operation guide
WORKFLOW.md              End-to-end generation workflow
scripts/                 RootFlowAI request scripts
references/              Prompt templates and case library
tests/                   Unit tests
```
