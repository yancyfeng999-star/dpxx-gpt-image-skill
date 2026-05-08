# dpxx-gpt-image-skill

## 中文说明

`dpxx-gpt-image-skill` 是一个 DPXX 生图技能项目，专注于通过 RootFlowAI 调用 GPT-Image-2 系列模型完成文生图、参考图生图和图片编辑。

这个仓库是独立项目，可以单独安装、分发和使用，不依赖 Gemini 版本的 skill。

当前版本：`v1.1.1`

### 版本控制

- 版本号以 `SKILL.md` frontmatter 里的 `version` 为准。
- GitHub release tag 使用同名语义版本号，例如 `v1.1.1`。
- `references/VERSION.md` 和 `scripts/VERSION.md` 必须与 `SKILL.md` 保持一致。
- 修改脚本、模型映射或对话流程时必须提升版本号。

### 适合场景

- 商品图、电商主图、海报和 KV
- 社媒配图、广告创意、品牌视觉
- 参考图改写、风格迁移、局部编辑
- 需要 GPT-Image-2 默认风格和稳定输出的 DPXX 工作流

### 模型映射

| 分辨率 | 模型 |
| --- | --- |
| 1K | `gpt-image-2-count` |
| 2K | `gpt-image-2-hd-count` |
| 4K | `gpt-image-2-4k-count` |

默认建议使用 `gpt-image-2-hd-count`。如果只是快速验证构图，可以先用 `gpt-image-2-count`。

### 比例规则

1K 和 2K 支持：

```text
1:1  3:2  2:3  4:3  3:4  5:4  4:5  16:9  9:16  2:1  1:2  21:9  9:21
```

4K 仅支持：

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

### 基本命令

运行前请先按你的部署环境完成 RootFlowAI 鉴权配置。不要把任何私密凭证写入仓库。

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

### 项目结构

```text
SKILL.md                 技能主说明
scripts/                 RootFlowAI 调用脚本
references/              prompt 模板和案例库
tests/                   单元测试
```

---

## English

`dpxx-gpt-image-skill` is a standalone DPXX image-generation skill for GPT-Image-2 models through RootFlowAI. It supports text-to-image, reference-image generation, and image editing.

This repository is self-contained and can be installed, distributed, and used independently from the Gemini skill.

Current version: `v1.1.1`

### Versioning

- The source of truth is the `version` field in `SKILL.md` frontmatter.
- GitHub release tags use the same semantic version, for example `v1.1.1`.
- `references/VERSION.md` and `scripts/VERSION.md` must match `SKILL.md`.
- Bump the version whenever scripts, model mapping, or workflow behavior changes.

### Use Cases

- Product images, e-commerce hero images, posters, and key visuals
- Social media images, ad creatives, and brand visuals
- Reference-image generation, style transfer, and image editing
- DPXX workflows that need the GPT-Image-2 visual style and stable output

### Model Mapping

| Resolution | Model |
| --- | --- |
| 1K | `gpt-image-2-count` |
| 2K | `gpt-image-2-hd-count` |
| 4K | `gpt-image-2-4k-count` |

Recommended default: `gpt-image-2-hd-count`. Use `gpt-image-2-count` for quick composition checks.

### Aspect Ratios

1K and 2K support:

```text
1:1  3:2  2:3  4:3  3:4  5:4  4:5  16:9  9:16  2:1  1:2  21:9  9:21
```

4K supports:

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

### Basic Command

Configure RootFlowAI authentication through your runtime environment before running. Do not commit private credentials to the repository.

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

### Repository Layout

```text
SKILL.md                 Skill instructions
scripts/                 RootFlowAI request scripts
references/              Prompt templates and case library
tests/                   Unit tests
```
