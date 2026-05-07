# dpxx-image-skill API Reference

Source: <https://docs.rootflowai.com/guide/image-generation>
Companion implementation: <https://github.com/RyanWeb31110/rootflowai-image>
Gemini native image model reference: <https://ai.google.dev/gemini-api/docs/image-generation>

## Base URL

```
https://api.rootflowai.com/v1
```

This base URL is shared by GPT-Image-2 and Gemini models. Do not route GPT and Gemini through different API addresses; split accounting and routing by API key family instead.

Override via env: `ROOTFLOWAI_BASE_URL` only for debugging or private deployment.

## Authentication

`Authorization: Bearer <API_KEY>` header. API keys are split by model family:

| Profile | Env vars (in order) | Model family |
|---------|---------------------|--------------|
| `gpt` | `ROOTFLOWAI_GPT_API_KEY` | GPT-Image-2 models |
| `gemini` | `ROOTFLOWAI_GEMINI_API_KEY` | Gemini 3.1 Flash / Gemini 3 Pro models |

When using `--api-key`, pass the key that matches the selected model family.

**CLI override**: `--api-key "<GPT_OR_GEMINI_API_KEY>"` takes precedence over env vars. **Recommended for sub-agent usage** because it works in any shell (sh / dash / bash / zsh), unlike inline `KEY=… python3 …` which is bash/zsh-only.

## Models

| Model | API key family | Max resolution | Allowed ratios |
|-------|------|----------------|----------------|
| `gpt-image-2-count` | GPT | 1K | All 13 |
| `gpt-image-2-hd-count` | GPT | 2K | All 13 |
| `gpt-image-2-4k-count` | GPT | 4K | `16:9 / 9:16 / 2:1 / 1:2 / 21:9 / 9:21` only |
| `gemini-3.1-flash-image-count` | Gemini | 1K | All 13 |
| `gemini-3.1-flash-image-hd-count` | Gemini | 2K | All 13 |
| `gemini-3.1-flash-image-4k-count` | Gemini | 4K | All 13 |
| `gemini-3-pro-image-count` | Gemini | 1K | All 13 |
| `gemini-3-pro-image-hd-count` | Gemini | 2K | All 13 |
| `gemini-3-pro-image-4k-count` | Gemini | 4K | All 13 |

## Allowed `size` values

Ratio strings (preferred): `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `5:4`, `4:5`, `16:9`, `9:16`, `2:1`, `1:2`, `21:9`, `9:21`.

Pixel strings (e.g. `1024x1024`, `1536x1024`) are also accepted and snapped to the closest ratio
internally by the backend. When you do not pass `size` in image-to-image mode, the output keeps
the input image's resolution.

## Allowed `quality` values

GPT-Image-2 models support `low`, `medium`, and `high`.

Use `high` by default. Quality only affects speed and detail. Do not downgrade quality for vague requests such as "faster", "preview", "draft", or "take a look". Use `low` only when the user explicitly asks for low-quality preview / low quality / lowest quality. Use `medium` only when the user explicitly asks for medium quality.

Gemini models do not support `quality`; the scripts omit the `quality` field automatically for all `gemini-*` count models.

## Endpoints

### `POST /v1/images/generations`

JSON body:

```json
{
  "model": "gpt-image-2",
  "prompt": "string",
  "size": "1:1",
  "quality": "high",
  "n": 1,
  "image": ["https://…", "data:image/png;base64,…"]
}
```

Notes:
- `n` 固定为 **1**，API 不支持单次请求批量出图。
- `image` is optional. When present, this becomes image-to-image. Up to **16** entries.
- Mix HTTPS URLs and base64 data URIs freely.
- Omitting `size` in image-to-image preserves the input resolution; passing `size` forces it.
- For Gemini models, omit `quality`; the shipped scripts do this automatically.

### `POST /v1/images/edits`

`multipart/form-data` with these parts:
- `model` (text)
- `prompt` (text)
- `size` (text)
- `quality` (text, GPT-Image-2 only; omitted for Gemini)
- `n` (text)
- `image` (file) — repeat for multiple input images
- `mask` (file, optional) — transparent pixels mark the region to edit
- `background`, `input_fidelity` (text, optional, model-dependent)

## Response shape

```json
{
  "created": 1714572800,
  "data": [
    { "url": "https://cdn…/image.png" }
    // OR
    // { "b64_json": "…base64…" }
  ]
}
```

Each item carries either a downloadable `url` / `image_url` or an inline `b64_json` /
`image_base64`. The shipped scripts handle both transparently and write files to `--output-dir`.

> ⚠️ **URL 有效期**：`url` 字段返回的 CDN 链接约 **24 小时**后失效。脚本已自动落盘，若直接使用 URL 需在出图后立即下载。

## Error shape

Non-2xx responses surface as JSON; the scripts re-print them on stderr and exit with code 1:

```json
{ "error": "Image generation request failed.", "status": 401, "response": "…" }
```

## CLI quick reference (this skill)

```bash
# text-to-image
python3 scripts/generate_image.py --prompt "…" --size 2:3 --quality high --output-dir ./out

# choose GPT-Image-2 + 2K
python3 scripts/generate_image.py --profile gpt --model gpt-image-2-hd-count \
  --prompt "…" --size 16:9 --quality high --output-dir ./out

# choose Gemini 3.1 Flash + 2K (no quality parameter)
python3 scripts/generate_image.py --profile gemini --model gemini-3.1-flash-image-hd-count \
  --prompt "…" --size 16:9 --output-dir ./out

# choose Gemini 3 Pro + 4K (no quality parameter)
python3 scripts/generate_image.py --profile gemini --model gemini-3-pro-image-4k-count \
  --prompt "…" --size 1:1 --output-dir ./out --timeout 600

# image-to-image (up to 16 refs)
python3 scripts/generate_image.py --prompt "…" \
  --image https://example.com/a.png --image /local/b.jpg --quality high --output-dir ./out

# masked edit
python3 scripts/edit_image.py --image /abs/in.png --mask /abs/mask.png \
  --prompt "…" --quality high --output-dir ./out

# request raw response for debugging
python3 scripts/generate_image.py --prompt "…" --response-path ./out/resp.json
```

Useful env:

```bash
export ROOTFLOWAI_GPT_API_KEY=…       # GPT-Image-2 models
export ROOTFLOWAI_GEMINI_API_KEY=…    # Gemini models
export ROOTFLOWAI_BASE_URL=https://api.rootflowai.com/v1   # rarely needed
```
