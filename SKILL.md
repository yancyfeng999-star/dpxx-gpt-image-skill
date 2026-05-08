---
name: "dpxx-gpt-image-skill v1.1.1"
version: 1.1.1
description: Generate or edit images with RootFlowAI GPT-Image-2 models. Use when the user asks to draw, generate, create, edit, 出图, 作图, 生成图, 改图, or P 图 and wants the DPXX GPT image workflow.
changelog:
  - "1.1.1 (2026-05-08): 独立为 GPT-Image-2 专用 RootFlowAI skill。"
---

# dpxx-gpt-image-skill v1.1.1

This skill is GPT-only. It uses RootFlowAI as the only image provider.

## 0. Required Checks

1. Check the API key before calling scripts:
   ```bash
   env | grep -E "ROOTFLOWAI_GPT_API_KEY" || echo MISSING
   ```
2. If missing, ask the user for the GPT RootFlowAI key and pass it as `--api-key "<ROOTFLOWAI_GPT_API_KEY>"`. Do not write keys to files and do not edit shell rc files.
3. Use `https://api.rootflowai.com/v1` unless the user explicitly gives another RootFlowAI base URL.
4. Scripts are standard-library Python:
   - `{SKILL_DIR}/scripts/generate_image.py`
   - `{SKILL_DIR}/scripts/edit_image.py`

## 1. Mandatory Flow

Collect the generation parameters before running the script:

1. Ask for resolution: `1K`, `2K`, or `4K`.
2. Ask for ratio or pixel size.
3. Ask for subject if the user did not provide one.
4. Pick a prompt template by reading `references/prompt-patterns.md`; if no template fits, use the six-slot prompt flow: Subject, Composition, Lighting, Style, Color, Constraints.
5. Show a concise execution summary and wait for user confirmation.

## 2. Model Mapping

| Resolution | Model |
| --- | --- |
| 1K | `gpt-image-2-count` |
| 2K | `gpt-image-2-hd-count` |
| 4K | `gpt-image-2-4k-count` |

Default: use `gpt-image-2-hd-count` for final-looking work and `gpt-image-2-count` for quick composition checks.

## 3. Size Rules

For 1K and 2K, support these ratios:

```text
1:1  3:2  2:3  4:3  3:4  5:4  4:5  16:9  9:16  2:1  1:2  21:9  9:21
```

For 4K, only use:

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

If the user asks for GPT 4K with any other ratio, ask them to switch to 2K or choose one of the 4K ratios.

## 4. Quality

GPT-Image-2 supports `low`, `medium`, and `high`.

Default to `--quality high`. Use `low` only when the user explicitly asks for low quality. Use `medium` only when the user explicitly asks for medium.

## 5. Commands

Text to image:

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "<FINAL_PROMPT>" \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix gpt
```

Image to image:

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "<FINAL_PROMPT>" \
  --image ./input.png \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix gpt-ref
```

Edit:

```bash
python3 {SKILL_DIR}/scripts/edit_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "<EDIT_INSTRUCTION>" \
  --image ./input.png \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix gpt-edit
```

## 6. Output Rules

Return saved image paths and the effective model, resolution, ratio, quality, and prompt source. Keep user-visible error text concise and do not expose API keys.
