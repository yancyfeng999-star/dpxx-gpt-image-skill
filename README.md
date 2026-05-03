# DPXX gpt-image-2 v1.0.10

通用 agent 技能，用 RootFlowAI 的 `gpt-image-2` API 生成、参考图生成和局部编辑图片。技能重点是把出图流程做稳：先选分辨率，再根据分辨率展示可用比例，默认高质量输出，最后补主题、模板和风格细节后调用脚本。

## 核心流程

1. 检查 RootFlowAI API Key。
2. 先让用户选择分辨率：`1K` / `2K` / `4K`。
3. 根据分辨率决定模型和可选比例。
4. 再让用户选择比例、主题、提示词模板和风格维度。
5. 生成完整 prompt，调用 API。
6. 下载图片到本地 `out` 目录，并返回模型、比例和文件路径。

## 给小白用户

如果用户不知道怎么提需求，先让他看这份教程：

[DPXX gpt-image-2 v1.0.10 小白出图教程](./USER_GUIDE.md)

也可以直接发 PDF 版：

[DPXX gpt-image-2 v1.0.10 小白出图教程 PDF](./USER_GUIDE.pdf)

教程里有 agent 安装说明、API Key 获取方式、分辨率选择、比例选择、提示词填空模板、参考图说明和改图话术，可以直接转发给非技术用户。

## API Key 获取

使用本技能需要 RootFlowAI API Key。API Key 请找 **YancyFeng 工程师** 获取，拿到后再交给负责出图的 agent 或工程师使用。

## 分辨率与比例规则

| 档位 | 模型 | 可用比例 |
|------|------|----------|
| 1K | `gpt-image-2-count` | 13 种全部支持 |
| 2K | `gpt-image-2-hd-count` | 13 种全部支持 |
| 4K | `gpt-image-2-4k-count` | 仅 6 种宽幅比例 |

1K / 2K 可用比例：

```text
1:1   3:2   2:3   4:3   3:4   5:4   4:5
16:9  9:16  2:1   1:2   21:9  9:21
```

4K 可用比例：

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

因此 `2K + 1024x1024` 允许，`4K + 1024x1024` 会被拦截，因为它等价于 `1:1`。

## 质量规则

RootFlowAI 支持 `low` / `medium` / `high` 三档 `quality`，只影响速度和细节。

本技能默认始终使用：

```text
quality=high
```

不要把质量作为常规问题询问用户，也不要因为用户说“快一点”“先看看”“草稿”“预览”就自动降质量。

仅当用户明确要求低质量时才使用 `quality=low`，例如：

```text
低质量预览
用 low quality
先低质量跑一张
低清/低质量试一下
用最低质量
```

`quality=medium` 只在用户明确指定“medium / 中等质量”时使用。

## 文件结构

```text
gpt-image-2-1.0.10/
├── README.md
├── USER_GUIDE.md
├── USER_GUIDE.pdf
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

推荐分别配置 count lane 和 metered lane：

```bash
export ROOTFLOWAI_COUNT_API_KEY="<ROOTFLOWAI_API_KEY>"
export ROOTFLOWAI_METERED_API_KEY="<ROOTFLOWAI_API_KEY>"
```

也可以只配置通用变量：

```bash
export ROOTFLOWAI_API_KEY="<ROOTFLOWAI_API_KEY>"
```

如果不想写入环境变量，可以在调用脚本时用 `--api-key` 传一次性 key。

## 文生图示例

1K 快速验证：

```bash
python3 scripts/generate_image.py \
  --profile count \
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
  --profile count \
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
  --profile count \
  --model gpt-image-2-4k-count \
  --prompt "A cinematic ultra-wide city skyline at sunrise, premium commercial photography." \
  --size 21:9 \
  --quality high \
  --output-dir ./out \
  --prefix city-4k \
  --timeout 300
```

## 图生图与局部编辑

参考图生成可以给 `generate_image.py` 传一个或多个 `--image`：

```bash
python3 scripts/generate_image.py \
  --profile count \
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
  --profile count \
  --model gpt-image-2-hd-count \
  --prompt "Replace the background with a minimal warm studio backdrop." \
  --image ./input/photo.png \
  --mask ./input/mask.png \
  --size 1:1 \
  --quality high \
  --output-dir ./out \
  --prefix photo-edit
```

## 安装 / 更新

让 agent 直接执行下面命令。已安装时会更新到最新版，未安装时会从 GitHub 开源仓库安装：

```bash
mkdir -p ~/.claude/skills
if [ -d ~/.claude/skills/gpt-image-2/.git ]; then
  git -C ~/.claude/skills/gpt-image-2 pull --ff-only
else
  git clone https://github.com/yancyfeng999-star/gpt-image-2.git ~/.claude/skills/gpt-image-2
fi
```

## 参考来源

- 脚本：[RyanWeb31110/rootflowai-image](https://github.com/RyanWeb31110/rootflowai-image)
- API 文档：[docs.rootflowai.com](https://docs.rootflowai.com/guide/image-generation)
- Prompt 方法论：[freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2)
- Case 库：[EvoLinkAI/awesome-gpt-image-2-prompts](https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts)

## License

MIT License. See [LICENSE](./LICENSE).

## 更新日志

**v1.0.10 (2026-05-02)**

- 统一 GitHub 对外展示版本。
- 刷新 `scripts/` 与 `references/` 目录版本标记，避免 GitHub 文件列表显示旧提交信息。
- 保留可直接复制给 agent 的安装 / 更新命令。

- 基础版本发布。
