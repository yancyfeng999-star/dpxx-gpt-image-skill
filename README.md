# dpxx-image-skill v1.1.1

通用 agent 技能，用 RootFlowAI-compatible image API 生成、参考图生成和局部编辑图片。技能重点是把出图流程做稳：先让用户选择模型家族（GPT-Image-2 / Gemini），再选分辨率和比例，最后补主题、模板和风格细节后调用脚本。

## 核心流程

1. 检查 RootFlowAI API Key。
2. 先让用户选择顶层模型：`GPT-Image-2（默认）` / `Gemini 3 Pro` / `Gemini 3.1 Flash`。
3. 再让用户选择分辨率：`1K` / `2K` / `4K`。
4. 根据模型和分辨率决定具体 `--model`、是否传 `--quality`、可选比例。
5. 再让用户选择比例、主题、提示词模板和风格维度。
6. 生成完整中文提示词和 English prompt，执行前发给用户确认。
7. 用户回复“执行”后调用 API。
8. 下载图片到本地 `out` 目录，并返回模型、比例和文件路径。

## 给小白用户

如果用户不知道怎么提需求，先让他看这份教程：

[dpxx-image-skill v1.1.1 小白出图教程](./USER_GUIDE.md)

教程里有 agent 安装说明、API Key 获取方式、分辨率选择、比例选择、提示词填空模板、参考图说明和改图话术，可以直接转发给非技术用户。

## API Key 获取

使用本技能需要 RootFlowAI API Key。API Key 只分 GPT 和 Gemini：GPT-Image-2 用 GPT API Key，Gemini 3.1 Flash / Gemini 3 Pro 用 Gemini API Key。API Key 请找 **YancyFeng 工程师** 获取，拿到后再交给负责出图的 agent 或工程师使用。

RootFlowAI API 地址是统一的：`https://api.rootflowai.com/v1`。GPT / Gemini 不分不同 API 地址，只用不同 API Key 做内部统计和分流。

## 模型、分辨率与比例规则

使用 skill 开始先选模型。模型选择阶段只展示 3 个顶层选项，不展示 `count` / `hd` / `4k` / 具体 model id。

| 选择 | 适合场景 |
|------|----------|
| GPT-Image-2（默认） | 通用出图、商品图、海报、现有默认风格 |
| Gemini 3 Pro | 复杂海报、图片里有文字、专业资产 |
| Gemini 3.1 Flash | 想用 Gemini / Nano Banana，重视提示词跟随 |

分辨率阶段再映射到真实 model id：

| 档位 | GPT-Image-2 | Gemini 3 Pro | Gemini 3.1 Flash |
|------|-------------|------------------|--------------|
| 1K | `gpt-image-2-count` | `gemini-3-pro-image-count` | `gemini-3.1-flash-image-count` |
| 2K | `gpt-image-2-hd-count` | `gemini-3-pro-image-hd-count` | `gemini-3.1-flash-image-hd-count` |
| 4K | `gpt-image-2-4k-count` | `gemini-3-pro-image-4k-count` | `gemini-3.1-flash-image-4k-count` |

Gemini 3 Pro 和 Gemini 3.1 Flash 都支持 1K / 2K / 4K。

1K / 2K 可用比例：

```text
1:1   3:2   2:3   4:3   3:4   5:4   4:5
16:9  9:16  2:1   1:2   21:9  9:21
```

GPT-Image-2 4K 可用比例：

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

脚本也接受像素尺寸，并会在 4K 校验前映射到等价比例：

```text
1024x1024 -> 1:1
1536x1024 -> 3:2
1024x1536 -> 2:3
1792x1024 -> 16:9
1024x1792 -> 9:16
```

因此 `GPT-Image-2 2K + 1024x1024` 允许，`GPT-Image-2 4K + 1024x1024` 会被拦截，因为它等价于 `1:1`。Gemini 4K 不套 GPT-Image-2 的 6 种宽幅限制。

## 质量规则

GPT-Image-2 支持 `low` / `medium` / `high` 三档 `quality`，只影响速度和细节。

本技能默认始终使用：

```text
quality=high
```

不要把质量作为常规问题询问用户，也不要因为用户说“快一点”“先看看”“草稿”“预览”就自动降质量。

仅当用户明确要求低质量时才使用 `quality=low`，例如：

```text
低质量预览
用 low quality
先低质量预览一下
低清/低质量试一下
用最低质量
```

`quality=medium` 只在用户明确指定“medium / 中等质量”时使用。

Gemini 模型不支持 `quality` 参数，脚本会自动省略。不要在 Gemini 命令里传 `--quality`。

## 文件结构

```text
dpxx-image-skill-2-1.1.1/
├── README.md
├── USER_GUIDE.md
├── SKILL.md
├── WORKFLOW.md
├── references/
│   ├── api.md
│   ├── prompt-patterns.md
│   └── cases/
│       ├── INDEX.md
│       ├── portrait.md
│       ├── poster.md
│       ├── ui.md
│       ├── comparison.md
│       ├── ecommerce.md
│       ├── ad-creative.md
│       └── character.md
└── scripts/
    ├── generate_image.py
    ├── edit_image.py
    └── image_api_common.py
```

## 环境变量

API Key 只分 GPT 和 Gemini。推荐分别配置：

```bash
export ROOTFLOWAI_GPT_API_KEY="<GPT_API_KEY>"
export ROOTFLOWAI_GEMINI_API_KEY="<GEMINI_API_KEY>"
```

如果不想写入环境变量，可以在调用脚本时用 `--api-key` 传一次性 key。

## 文生图示例

1K 快速验证：

```bash
python3 scripts/generate_image.py \
  --profile gpt \
  --model gpt-image-2-count \
  --prompt "A clean logo mark for Accio Work, blue and orange, modern AI collaboration platform." \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix accio-logo
```

2K 海报或正式图：

```bash
python3 scripts/generate_image.py \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "A premium product poster for a matte black smart speaker, dramatic studio lighting." \
  --size 2:3 \
  --quality high \
  --output-dir ./out \
  --prefix speaker-poster
```

4K 宽幅大图：

```bash
python3 scripts/generate_image.py \
  --profile gpt \
  --model gpt-image-2-4k-count \
  --prompt "A cinematic ultra-wide city skyline at sunrise, premium commercial photography." \
  --size 21:9 \
  --quality high \
  --output-dir ./out \
  --prefix city-4k \
  --timeout 300
```

Gemini 3.1 Flash 2K：

```bash
python3 scripts/generate_image.py \
  --profile gemini \
  --model gemini-3.1-flash-image-hd-count \
  --prompt "A clean product hero image for a matte black ceramic coffee cup." \
  --size 16:9 \
  --output-dir ./out \
  --prefix gemini-cup
```

Gemini 3 Pro 4K：

```bash
python3 scripts/generate_image.py \
  --profile gemini \
  --model gemini-3-pro-image-4k-count \
  --prompt "A premium watch campaign poster, crisp typography, studio lighting." \
  --size 1:1 \
  --output-dir ./out \
  --prefix gemini-watch \
  --timeout 600
```

## 图生图与局部编辑

参考图生成可以给 `generate_image.py` 传一个或多个 `--image`：

```bash
python3 scripts/generate_image.py \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "Redesign this product photo into a clean premium e-commerce hero image." \
  --image ./input/product.png \
  --size 3:2 \
  --quality high \
  --output-dir ./out \
  --prefix product-redesign
```

局部编辑使用 `edit_image.py`，可选 `--mask`。mask 规则是：透明像素代表要编辑的区域，非透明像素尽量保持原样。

```bash
python3 scripts/edit_image.py \
  --profile gpt \
  --model gpt-image-2-hd-count \
  --prompt "Replace the background with a minimal warm studio backdrop." \
  --image ./input/photo.png \
  --mask ./input/mask.png \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix photo-edit
```

Gemini 图生图或编辑也可以使用同一脚本接口，只是命令不要传 `--quality`。整体改图、风格迁移、多参考融合优先用 Gemini；明确需要 mask 的局部编辑优先用 GPT-Image-2。

## 安装 / 更新

让 agent 直接执行下面命令。已安装时会更新到最新版，未安装时会从 GitHub 开源仓库安装：

```bash
mkdir -p ~/.claude/skills
if [ -d ~/.claude/skills/dpxx-image-skill/.git ]; then
  git -C ~/.claude/skills/dpxx-image-skill pull --ff-only
else
  git clone https://github.com/yancyfeng999-star/gpt-image-2.git ~/.claude/skills/dpxx-image-skill
fi
```

## 参考来源

- 脚本：[RyanWeb31110/rootflowai-image](https://github.com/RyanWeb31110/rootflowai-image)
- API 文档：[docs.rootflowai.com](https://docs.rootflowai.com/guide/image-generation)
- Prompt 方法论：[freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2)
- Case 库：[EvoLinkAI/awesome-gpt-image-2-prompts](https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts)

## Copyright

Copyright (c) 2026 YancyFeng. All rights reserved.

## 更新日志

**v1.1.1 (2026-05-07)**

- 发布目录名同步更新为 `dpxx-image-skill-2-1.1.1`。
- 固化模型选择阶段只展示 `GPT-Image-2（默认）` / `Gemini 3 Pro` / `Gemini 3.1 Flash` 三个顶层选项。
- 生成前汇总必须包含参数、中文提示词和 English prompt，用户回复“执行”后才调用脚本。
- 自由六槽位改为引导式提问，给每个槽位提供解释、选项和自定义提示。
