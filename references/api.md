# RootFlowAI gpt-image-2 API Reference

Source: <https://docs.rootflowai.com/guide/image-generation>
Companion implementation: <https://github.com/RyanWeb31110/rootflowai-image>

## Base URL

```
https://api.rootflowai.com/v1
```

Override via env: `ROOTFLOWAI_BASE_URL`.

## Authentication

`Authorization: Bearer <API_KEY>` header. Two billing lanes / API keys:

| Profile | Env vars (in order) | Model family |
|---------|---------------------|--------------|
| `metered` | `ROOTFLOWAI_METERED_API_KEY`, then `ROOTFLOWAI_API_KEY` | `gpt-image-2` |
| `count` | `ROOTFLOWAI_COUNT_API_KEY`, then `ROOTFLOWAI_API_KEY` | `gpt-image-2-count`, `gpt-image-2-hd-count`, `gpt-image-2-4k-count` |

`ROOTFLOWAI_API_KEY` is the universal fallback — both lanes accept it, so a user with a single generic key can still drive either profile.

**CLI override**: `--api-key "<ROOTFLOWAI_API_KEY>"` takes precedence over env vars. **Recommended for sub-agent usage** because it works in any shell (sh / dash / bash / zsh), unlike inline `KEY=… python3 …` which is bash/zsh-only.

## Models

| Model | Lane | Max resolution | Allowed ratios |
|-------|------|----------------|----------------|
| `gpt-image-2` | metered | 1K | All 13 |
| `gpt-image-2-count` | count | 1K | All 13 |
| `gpt-image-2-hd-count` | count | 2K | All 13 |
| `gpt-image-2-4k-count` | count | 4K | `16:9 / 9:16 / 2:1 / 1:2 / 21:9 / 9:21` only |

## Allowed `size` values

Ratio strings (preferred): `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `5:4`, `4:5`, `16:9`, `9:16`, `2:1`, `1:2`, `21:9`, `9:21`.

Pixel strings (e.g. `1024x1024`, `1536x1024`) are also accepted and snapped to the closest ratio
internally by the backend. When you do not pass `size` in image-to-image mode, the output keeps
the input image's resolution.

## Allowed `quality` values

RootFlowAI supports `low`, `medium`, and `high`.

Use `high` by default. The three quality levels have the same price; quality only affects speed and detail. Do not downgrade quality for vague requests such as "faster", "preview", "draft", or "take a look". Use `low` only when the user explicitly asks for low-quality preview / low quality / lowest quality. Use `medium` only when the user explicitly asks for medium quality.

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

### `POST /v1/images/edits`

`multipart/form-data` with these parts:
- `model` (text)
- `prompt` (text)
- `size` (text)
- `quality` (text)
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

# choose count + 2K
python3 scripts/generate_image.py --profile count --model gpt-image-2-hd-count \
  --prompt "…" --size 16:9 --quality high --output-dir ./out

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
export ROOTFLOWAI_METERED_API_KEY=…   # metered lane preferred
export ROOTFLOWAI_COUNT_API_KEY=…     # count lane preferred
export ROOTFLOWAI_API_KEY=…           # universal fallback (both lanes)
export ROOTFLOWAI_BASE_URL=https://api.rootflowai.com/v1   # rarely needed
```
