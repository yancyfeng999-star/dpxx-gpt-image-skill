# dpxx-image-skill v1.1.0 端到端工作流示例

> 给通用 agent 抄的**整段示范**：从用户开口到图落盘到 chat 嵌图，一步不漏。
> 4 个常见场景全部通过实测。

---

## 场景 A：用户只说"帮我画个 Logo"

### A.1 对话流程（agent ←→ 用户）

**Agent**（执行 `env | grep ROOTFLOWAI`，发现没 key）

> 调 `ask_user(mode=chat)`：
> "需要 RootFlowAI API Key 才能调用 dpxx-image-skill，请把你的 API Key 贴这里。我用一次后立即从内存释放，不写入任何文件。"

**用户**：`<ROOTFLOWAI_GPT_API_KEY>` 或 `<ROOTFLOWAI_GEMINI_API_KEY>`

**Agent** 调 `ask_user(mode=form)` 先问 Q1，只选顶层模型：

> 卡片 1：选哪个模型？（GPT-Image-2 默认 / Gemini 3 Pro / Gemini 3.1 Flash）

**Agent** 再问 Q2 分辨率：

> 卡片 2：选哪个分辨率？（1K / 2K / 4K）

**Agent** 根据模型和分辨率决定具体 `--model`、是否传 `--quality`、比例范围，再调 `ask_user(mode=form)` 问比例 + 模板 + 主题：

> 卡片 3：选哪个尺寸比例？（GPT-Image-2 4K 只展示 6 种宽幅；Gemini 4K 可用常见比例）
> 卡片 4：选哪类提示词模板？（T05 Logo / T01 写实 / T04 海报 / T13 UI / 其他）
> 卡片 5：主题是？（让我帮你想 / 我下一条发主题）

GPT-Image-2 的 `quality` 默认 `high`，不要单独询问。只有用户明确要求"低质量预览 / low quality / 最低质量"时才传 `--quality low`；只有用户明确指定 medium 时才传 `--quality medium`。Gemini 模型不传 `--quality`。

**用户**：GPT-Image-2 · 1K · 1:1 · T05 Logo · "主题：一个叫 Accio Work 的 AI 协作平台，主色蓝橙"

### A.2 Agent 执行

```bash
# 1) read 模板原文
cat {SKILL_DIR}/references/prompt-patterns.md  # 找 T05 段落

中文提示词='为 "Accio Work" 设计一个现代、温暖、高级的 AI 协作平台 Logo。左侧是几何折纸鸟图标，右侧是字标；主色 #2A5BD7，辅色 #F5A524，白色背景；整体矢量扁平、边缘清晰、无渐变、无阴影。'
PROMPT='Logo design for "Accio Work" — AI productivity platform, modern, warm, premium.
Direction: combined mark with a geometric origami-bird icon left of the wordmark.
Primary color #2A5BD7, secondary #F5A524, on white background.
Geometry: balanced grid, optical-corrected curves, scalable at 32px.
Show the mark large center, plus a small mono-color version bottom-right.
Vector-flat. No gradients. No drop shadows. Crisp edges. No spelling errors.'

# 3) 生成前必须把中文提示词 + English prompt 发给用户确认；用户回复“执行”后再执行
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt --model gpt-image-2-count \
  --prompt "$PROMPT" --size 1:1 --quality high \
  --output-dir ./out --prefix accio-logo
```

### A.3 自检 + 汇报

```python
# stdout JSON 检查 n_saved == 1
# see_image('./out/accio-logo-01.png')  ← 自己先看一眼
```

最终给用户：

> ![Accio Work logo](./out/accio-logo-01.png)
>
> ✅ 模型 `gpt-image-2-count`（1K）· 比例 `1:1` · 模板 T05 Logo · 落盘 `./out/accio-logo-01.png`
>
> 不满意可以告诉我改哪里（颜色 / 字体 / 鸟的姿态…），我用 `edit_image.py` 在这张基础上改。

---

## 场景 B：海报 — 2K 竖版

```bash
PROMPT='Movie-poster-style key visual for "深海寻光", a sci-fi thriller,
hero composition: a lone diver center silhouetted against a giant glowing jellyfish,
typography lockup at top reading "深海寻光" in heavy serif, subtitle "光，是出口" beneath,
credit block at bottom with [STUDIO 2026 · 12 · 25],
color grade teal-orange, strong rim lighting, dramatic depth,
cinematic 2.39:1 framing inside a 2:3 canvas. Sharp text, no spelling errors.'

python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt --model gpt-image-2-hd-count \
  --prompt "$PROMPT" --size 2:3 --quality high \
  --output-dir ./out --prefix poster
```

汇报模板（同上结构）。

### Gemini 版本（不传 quality）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GEMINI_API_KEY>" \
  --profile gemini --model gemini-3.1-flash-image-hd-count \
  --prompt "$PROMPT" --size 2:3 \
  --output-dir ./out --prefix poster-gemini
```

---

## 场景 C：3D 手办（图生图，把用户头像变手办）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt --model gpt-image-2-hd-count \
  --prompt 'Restyle this person as a 1/7 scale collectible PVC figure on a round transparent acrylic base, displayed on a wooden desk next to a Bandai-style box that shows the same character art and the title "ALEX". Studio product lighting, soft shadow on desk, ultra-detailed PVC material with subtle paint highlights, crisp seams. Photoreal product render. No watermarks.' \
  --image /Users/me/Desktop/avatar.jpg \
  --size 1:1 --quality high \
  --output-dir ./out --prefix figure
```

注意：
- `--image` 可重复，最多 16 张；HTTPS URL 与本地路径混传 OK。
- 不传 `--size` 会保留输入图分辨率；想强制比例就传 `--size`。
- Gemini 图生图也走 `generate_image.py --image`，但不要传 `--quality`。

---

## 场景 D：局部编辑（带 mask 换背景）

```bash
python3 {SKILL_DIR}/scripts/edit_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt --model gpt-image-2-hd-count \
  --image ./out/accio-logo-01.png \
  --mask  ./out/accio-logo-01-mask.png \
  --prompt "Replace the background area (transparent in mask) with a soft warm beige #F5EFE6 gradient. Keep the logo unchanged." \
  --size 1:1 --quality high \
  --output-dir ./out --prefix accio-logo-bg
```

mask 约定：**透明像素是要被改的区域**，非透明像素保持原样。

---

## 通用 checklist（每次执行前对一遍）

- [ ] `env | grep -E "ROOTFLOWAI_(GPT|GEMINI)_API_KEY"` 看 key 是否就绪；没有就按模型 family 拿一次性 key，**优先用 `--api-key` 直传**（跨 shell 兼容）。
- [ ] 模型 / 分辨率 / 比例 已在 `ask_user(form)` 里问到答案；使用 skill 开始必须先选模型。
- [ ] GPT-Image-2 4K → 比例必须 ∈ `{16:9, 9:16, 2:1, 1:2, 21:9, 9:21}`，否则二次确认。
- [ ] GPT-Image-2 的 `quality` 默认 `high`；只有用户明确要求低质量预览才改 `low`，只有用户明确指定 medium 才改 `medium`。
- [ ] Gemini 模型不传 `--quality`。
- [ ] 模板 ID 选定 → `read references/prompt-patterns.md` **取出对应 T 段原文**再填。
- [ ] 主题已确认（用户给的 / 你给的并征得同意）。
- [ ] 生成前必须汇总给用户确认：参数 + 中文提示词 + English prompt；用户回复“执行”后才执行。
- [ ] `--profile` 和 `--model` 匹配 API Key family：GPT 用 `--profile gpt`，Gemini 用 `--profile gemini`。
- [ ] **CLI 是 `--output-dir`，不是 `--out`**；`--prefix` 显式给，方便定位文件。
- [ ] 执行完成后用 `see_image` 看一眼成品再汇报。
- [ ] 最终消息里 markdown 嵌图 + 一句话技术摘要 + 一句话迭代提示。

## 通用 checklist（每次执行后对一遍）

- [ ] 临时 key 没有写进任何文件、没有 `export` 到 rc、没有出现在 git diff 中。

- [ ] 如果是测试性产物，主动删 `--output-dir` 或问用户是否保留。

---

## 场景 E：品牌 VI 全套（T16 Brand Identity Board，模式 B）

> 最复杂的 B 模式模板，一张图输出 Logo + 色板 + 字体样张 + 图标集。

### E.1 第 1 步问答（模型 + 分辨率）

- 模型：GPT-Image-2 或 Gemini 3 Pro Image（复杂文字/专业资产优先 Gemini 3 Pro）
- 分辨率：2K（推荐；4K 也可选 16:9）

### E.2 第 2 步问答（比例 + 主题）

- 比例：3:2 或 16:9
- 主题：品牌名 + 行业 + 3 个关键词（例："BLOOM · 女性护肤 · 温暖/现代/高级"）

### E.3 第 3 步问答（模板 + 风格拆解）

- 模板：T16 Brand Identity Board
- 必问维度：品牌名 / 配色方向（暖/冷/中性 + 给 2-3 个 HEX 参考） / 字体气质（衬线/无衬线/手写）

### E.4 执行

```bash
# 1) read T16 模板原文
# cat {SKILL_DIR}/references/prompt-patterns.md  # 找 T16 段落，取 JSON 模板

# 2) 填好的 JSON prompt（heredoc 防转义）
cat > /tmp/p.txt <<'EOF'
{
  "type": "brand identity moodboard",
  "subject": "BLOOM",
  "layout": {
    "structure": "single canvas with 5 zones arranged like a magazine spread",
    "sections": [
      { "position": "top-left", "content": "logo lockup, primary mark + wordmark" },
      { "position": "top-right", "content": "color swatches: 5 chips with HEX labels under each" },
      { "position": "center", "content": "product hero photo of a minimalist skincare bottle" },
      { "position": "bottom-left", "content": "typography specimen: 'Aa Bb Cc 123' in Cormorant Garamond + DM Sans with names labeled" },
      { "position": "bottom-right", "content": "icon set: 6 monoline icons in primary brand color" }
    ]
  },
  "theme": {
    "color_palette": "#E8B4B8 + #6A4C93 + #F4F1DE + #2C2C2C",
    "mood": "warm, modern, feminine"
  },
  "constraints": [
    "magazine-spread aesthetic, generous whitespace",
    "all HEX codes legible, all font names spelled correctly",
    "no watermarks"
  ]
}
EOF
PROMPT="$(cat /tmp/p.txt)"

# 3) 执行（2K + 3:2）
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_GPT_API_KEY>" \
  --profile gpt --model gpt-image-2-hd-count \
  --prompt "$PROMPT" --size 3:2 --quality high \
  --output-dir ./out --prefix bloom-brand
```

### E.4 防坑提示

- JSON 模板里 5 个区域**必须明确位置**（top-left/top-right/center/bottom-left/bottom-right），否则布局乱。
- 颜色必须给完整 HEX，不要只写颜色名。
- 字体规格必标 `'Aa Bb Cc 123'` 让模型生成字体样张。
- 出图后如果某个区域不满意，用 `edit_image.py` 局部改，不需要整张重画。
