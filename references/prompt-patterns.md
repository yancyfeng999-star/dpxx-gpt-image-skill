# gpt-image-2 Prompt Pattern Library

## 来源融合映射（真实数量）

| 来源 | 真实数量 | 融合方式 |
|------|---------|---------|
| [freestylefly/awesome-gpt-image-2 · docs/templates.md](https://github.com/freestylefly/awesome-gpt-image-2/blob/main/docs/templates.md) | **13 个大类模板**（每类一份样例 prompt + 防坑指南） | 抽象为模式 A 的 T01–T13 + T18，每套保留 ⚠️ 防坑段 |
| [EvoLinkAI/awesome-gpt-image-2-prompts · cases/](https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts/tree/main/cases) | **312 个具体 case**，7 类：portrait 55 / poster 101 / ui 56 / comparison 48 / ecommerce 20 / ad-creative 19 / character 13；其中 43 个用 JSON 结构化 | **全量入库**到 [`cases/`](cases/)（7 个文件）+ 索引 [`cases/INDEX.md`](cases/INDEX.md)；高频 JSON 模式抽象为 T14–T17 |

**两层使用方式**：

1. **模板优先**（90% 场景）：从下面 T01–T18 选一套，按六槽位/JSON 字段填空 → 直接出图。
2. **案例兜底**（场景生僻、想要"一模一样"参考时）：先翻 [`cases/INDEX.md`](cases/INDEX.md) 按主题关键词搜 Case 编号 → `read references/cases/<分类>.md` 取 prompt 全文 → 改写成自己主题。

**完整性自检**（如何复核）：
1. freestylefly 13 套模板 → 一一对应 T01-T13。
2. EvoLink 312 case → 全文存于 `cases/{ad-creative,character,comparison,ecommerce,portrait,poster,ui}.md`，索引 `cases/INDEX.md`。
3. EvoLink 高频 JSON 模式 → 抽象为 T14（对比图）/ T15（广告矩阵）/ T16（brand board）/ T17（UI 全屏）。
4. freestylefly 防坑段 → 每套 T 模板尾部 `⚠️ 防坑` 段。

---

## 两种提示词承载模式

### 模式 A · 自然语言段落式（默认推荐）

对话式叙述，可读性强，适合 90% 场景。结构骨架（六槽位，缺一不画）：

`Subject 主体` · `Composition 构图` · `Lighting 光线` · `Style/medium 风格` · `Color palette 配色` · `Output constraints 输出约束`

### 模式 B · 结构化 JSON（来自 EvoLink，复杂版面/多元素必用）

当画面包含 ≥3 个独立区块、需要精确控制位置、或要做模板复用时，用 JSON 描述比自然语言可控得多。

#### B.1 顶层骨架

```json
{
  "type": "<整体形式：poster / 4-panel ad grid / brand identity board / product comparison ...>",
  "theme": { "color_palette": "...", "motif": "..." },
  "layout": {
    "structure": "<grid / vertical sections / hero + footer / ...>",
    "sections": [
      { "position": "top|center|bottom|top-left|...",
        "elements": [...],
        "text_labels": ["..."] }
    ]
  },
  "subjects": [...],
  "constraints": ["sharp text", "no spelling errors", "no watermarks"]
}
```

#### B.2 `{argument}` 参数槽语法

EvoLink 模板里大量出现，**让同一个 prompt 变成可复用的"模板函数"**：

```
{argument name="<变量名>" default="<默认值>"}
```

填入时直接替换。例：

```json
"text_labels": [
  "{argument name=\"travel destination\" default=\"沖縄旅行\"}",
  "{argument name=\"campaign note\" default=\"限定特典つき\"}"
]
```

> 调用脚本时仍传**最终替换好的字符串**给 `--prompt`；参数槽只是模板编辑期的占位约定。

#### B.3 何时用 A，何时用 B

| 场景 | 模式 |
|------|------|
| 单主体写实 / 摄影 / 插画 | A |
| Logo / 单图标 | A |
| 海报但只有 1 个主视觉 + 1 行字 | A |
| **多格广告（2×2 grid）/ 多页对比图 / 品牌识别 board / UI 全屏多模块** | **B** |
| 需要复用模板批量出图（变量化主题/卖点/品类） | **B + argument** |

---

## 通用授权规则（每条 prompt 都遵守）

1. **声明式**，不要写步骤；说"画面里有什么"，不说"先画 A 再画 B"。
2. **六槽位齐全**（模式 A）/ **三段齐全**（模式 B：theme + layout + constraints）。
3. **画面内文字必须 `"..."` 引号包住**，并标明字体族 / 粗细 / 语种。
4. **负面词收尾**，简短：`No watermarks. No extra limbs. No text bleed. No spelling errors.`
5. **`--size` 配模板推荐比例**（详见 SKILL.md Step 1 表）。
6. **图生图**：以转换动词起手 — `Convert / Restyle / Recompose / Recolor this reference into …`。
7. **长度上限**：模式 A 中文 ≤ 200 字 / 英文 ≤ 120 词；模式 B 没硬上限但每个 section 控制在 5–8 个字段。

---

## T01 — 写实摄影 / 人像 photography

**推荐 size：** `2:3`（人像）· `3:2`（环境）

```text
Photograph of [SUBJECT, age/expression/wardrobe], [SHOT TYPE: close-up / mid-shot / full body],
in [ENVIRONMENT, time of day], [LIGHTING: e.g. golden-hour rim light + soft fill],
shot on [CAMERA + LENS, e.g. Sony A7IV, 85mm f/1.4], depth of field [shallow / deep],
color palette [WARM / NEUTRAL / FILMIC],
[OPTIONAL ATMOSPHERE: rain mist / sand particles / window light].
Photo-real, sharp eyes, natural skin texture, no plastic look. No watermarks. No text.
```

**⚠️ 防坑**（来源 freestylefly + EvoLink portrait 类共性）：
- 必须明写**镜头焦段** — 缺失会渲染成手机感。85mm 出人像，35mm 出纪实，24mm 出环境。
- "皮肤" 必加 `natural skin texture, no plastic look`，否则塑料感强。
- 多人画面要列**每个人的位置 + 衣着**，不要只写 `three people`。
- 拒绝 `4k, ultra HD, hyperrealistic, masterpiece` 这种"咒语堆"，本模型对它们无感反而抢权重。

---

## T02 — 3D 手办 / 盲盒 figure

**推荐 size：** `1:1`

```text
A 1/7 scale collectible figure of [CHARACTER DESCRIPTION], on a round transparent acrylic base,
displayed on a desk next to [CONTEXT: laptop / Bandai-style box art / monitor],
the box behind shows the same character art and the title "[NAME]" in [FONT/LANGUAGE],
studio product lighting, soft shadow on desk, ultra-detailed PVC material with subtle
paint highlights, crisp seams. Photoreal product render.
No watermarks. No loose parts. No blurry seams. No floating objects. No extra limbs.
```

**⚠️ 防坑**：
- 一定要写 `acrylic base`（透明亚克力底座）+ `Bandai-style box`，否则出来像散件不像手办。
- `1/7 scale` / `1/4 scale` 决定细节密度，1/7 最常用。
- 桌面物件（电脑/键盘/咖啡杯）请显式给 1–2 件，"现代办公桌"过于模糊。

---

## T03 — IP / Q 版形象 character design

**推荐 size：** `1:1` 或 `3:4`

```text
Original IP character design sheet for "[NAME]", [TRAIT WORDS: friendly / mischievous / loyal],
chibi proportion (head-to-body ≈ 1:2), [SIGNATURE COLOR PALETTE, exactly 3 colors],
turnaround: front · 3/4 · side, plus 4 expression chips (happy / surprised / sleepy / angry),
clean vector-flat shading, soft outline, white background.
Children-book friendly. No text other than the name "[NAME]" under the front pose.
```

**⚠️ 防坑**：
- "三视图"必须明写 `turnaround: front · 3/4 · side`，否则只出正脸。
- 配色限定 `exactly 3 colors`，不然会出 8 色花脸。
- 头身比一定要数字化（`1:2`/`1:3`），形容词如 `cute proportion` 不可控。

---

## T04 — 海报 / KV poster

**推荐 size：** `2:3` 或 `3:4`

```text
Movie-poster-style key visual for "[TITLE]", [GENRE/MOOD],
hero composition: [MAIN SUBJECT center, supporting elements left/right],
typography lockup at top reading "[TITLE]" in [FONT, WEIGHT], subtitle "[ONE-LINER]" beneath,
credit block at bottom with [STUDIO / DATE], color grade [TEAL-ORANGE / MONOCHROME / PASTEL],
strong rim lighting, dramatic depth, cinematic 2.39:1 framing inside a 2:3 canvas.
Sharp text, no spelling errors, no watermarks.
```

**⚠️ 防坑**：
- 字一定 `"..."` 包起来，并写字体族，否则错字率 30%+。
- `cinematic 2.39:1 framing inside a 2:3 canvas` 这一句让模型主动留黑边，海报感立增。
- credit block 用 `[]` 占位让模型生成 fake 制作团队；想要真实信息就直接写出来。

---

## T05 — Logo / 品牌识别 brand

**推荐 size：** `1:1`

```text
Logo design for "[BRAND]" — [INDUSTRY], [BRAND ADJECTIVES: e.g. modern, warm, premium].
Direction: [WORDMARK / LETTERMARK / GEOMETRIC ICON / COMBINED MARK].
Primary color [#HEX], secondary [#HEX], on white background.
Geometry: balanced grid, optical-corrected curves, scalable at 32px.
Show the mark large center, plus a small mono-color version bottom-right.
Vector-flat. No gradients. No drop shadows. Crisp edges.
```

**⚠️ 防坑**：
- 必须强调 `Vector-flat. No gradients. No drop shadows.`，否则会出 3D 立体效果毁掉 Logo 适用性。
- 给 HEX 色值（`#2A5BD7`）远比 "blue" 可控。
- `scalable at 32px` 是个魔法 — 让模型自动避开过细线条。

---

## T06 — 信息图 / Infographic

**推荐 size：** `3:4`（单页）· `9:16`（手机分享）

```text
Editorial infographic titled "[TITLE]" with subtitle "[SUBTITLE]".
Sections (top to bottom):
1. Key metric "[NUMBER + UNIT]" with one-line caption
2. [STEP / CATEGORY LIST: 4 items, each with a flat icon and 6–10 word caption]
3. Comparison block: [A] vs [B] in two columns
4. Footer: source "[SOURCE]" and date.
Style: flat editorial illustration, 2-color palette [#HEX] + [#HEX] on off-white,
sans-serif typography, generous whitespace, clean grid alignment.
Quote all visible text exactly. No spelling errors. No decorative noise.
```

**⚠️ 防坑**：
- 信息图最容易出错字，**所有文字都必须 `"..."` 包**，并在结尾再次强调 `No spelling errors`。
- 限定 2 色配色 — 信息图最忌花。
- 数字最好是整数或带单位（`38%`、`120k`），小数点容易出错。

---

## T07 — 建筑 / 室内 architecture

**推荐 size：** `3:2`（外景）· `16:9`（内景宽幅）

```text
Architectural rendering of [BUILDING / ROOM TYPE], [STYLE: e.g. Japandi, Brutalist, Bauhaus],
materials: [LIST 3 materials with finish], lighting: [natural daylight from … / warm 2700K spots],
furnished with [KEY FURNITURE PIECES], camera: [FOCAL LENGTH] eye-level one-point perspective,
ambient occlusion, physically-based render, slight film grain, color grade [WARM NEUTRAL].
Photoreal. No floating objects. No distorted geometry.
```

**⚠️ 防坑**：
- 必须明写**3 种材质 + 表面处理**（如 `brushed oak, matte concrete, frosted glass`），否则材质混乱。
- `eye-level one-point perspective` 强制透视点居中，避免畸变。
- 加 `No floating objects` 是因为模型偶尔会让家具悬空。

---

## T08 — 漫画 / 多格 comic

**推荐 size：** `3:4`

```text
A [N]-panel comic page, manga ink style, screentone shading.
Panel 1: [SCENE], dialog "[LINE]"
Panel 2: [SCENE], dialog "[LINE]"
Panel N: [PUNCHLINE], SFX "[KATAKANA/ENGLISH SFX]"
Speech bubbles with clear tails, hand-lettered look, consistent character design across panels.
Black and white, high contrast, no color. Quote dialog exactly.
```

**⚠️ 防坑**：
- "角色一致性" 在多格漫画里最难，必加 `consistent character design across panels`。
- 如果要彩色，去掉 `Black and white, high contrast` 并加 `flat color, manga screentone shading`。
- SFX（拟声词）写日文片假名出味道（`バーン!` `ドキッ`）。

---

## T09 — 插画 / 绘本 illustration

**推荐 size：** `4:3`

```text
Storybook illustration: [SUBJECT doing ACTION] in [SETTING],
warm watercolor + soft pencil outline, dappled afternoon light,
palette of muted earth tones with one accent color [#HEX],
center-weighted composition with breathing room for a caption strip at the bottom.
Friendly, gentle mood. No text inside the artwork.
```

**⚠️ 防坑**：
- `breathing room for a caption strip at the bottom` 让模型主动留白，方便后期加字。
- 插画切忌 `4k, hyper detailed`，否则失去手绘感。
- 一个 accent color，其余全部低饱和，氛围最稳。

---

## T10 — 商品 / 电商 product shot

**推荐 size：** `1:1`（主图）· `4:5`（信息流）

```text
Studio product photograph of [PRODUCT, material/color], [VIEW: front three-quarter / top-down / floating],
on [BACKGROUND: pure white / textured stone slab / colored gradient #HEX],
soft beauty-dish key light from camera-left, gentle fill from right, subtle contact shadow underneath.
Crisp focus on the product, micro-detail on logo and seams, no environment props.
Color-accurate, advertising-grade. No watermarks. No sale labels, currency symbols, or numeric amount tags.
```

**⚠️ 防坑**：
- "白底纯色" 写 `pure white #FFFFFF, seamless`，否则出米白。
- 必加 `subtle contact shadow underneath`，否则商品悬空假。
- 不要写 "professional product photo"，模型反而会加噪点；写 `advertising-grade` 最稳。

---

## T11 — 历史 / 古风 historical

**推荐 size：** `3:2` 或 `2:3`

```text
[ERA, e.g. Tang dynasty 8th century / Edo period 1750] scene of [SUBJECT + ACTION] in [SETTING],
historically-accurate costume detail (fabric: [SILK/LINEN], pattern: [MOTIF]), authentic hairstyle,
[NATURAL LIGHTING: sunlight through paper window / lantern at dusk],
classical painting medium [silk-scroll ink wash / ukiyo-e woodblock / Persian miniature],
muted period-correct palette. Avoid modern objects (no plastic, no synthetic fabric, no zippers).
```

**⚠️ 防坑**：
- 必须给**精确朝代+世纪**，光说 "ancient China" 会把唐宋明清混着画。
- 服装写**面料+纹样**两层，单写 "Han fu" 不够。
- "Avoid modern objects" 单独列，否则会出现拉链、塑料、电线。

---

## T12 — 文档 / 出版物 document

**推荐 size：** `3:4`（A4）· `2:3`

```text
Mock-up of a [DOCUMENT TYPE: book cover / magazine spread / academic paper],
title "[TITLE]" in [FONT, WEIGHT], author "[NAME]", publisher mark bottom.
Layout: [grid description, e.g. 12-column with 2-col body], body shows lorem-ipsum lines
of approximately the right density (do NOT generate readable real text in body).
Color palette [#HEX]+[#HEX]+off-white, paper texture subtle, professional typesetting.
Sharp typography. No spelling errors in title.
```

**⚠️ 防坑**：
- 长正文一律写 `lorem-ipsum approximate density, not readable`，否则模型会塞乱码。
- 标题字体族 + 字重必给（`Garamond Regular` / `Helvetica Bold`）。
- 加 `paper texture subtle` 让纸张有质感不死板。

---

## T13 — UI / 界面 ui-screen

**推荐 size：** `9:16`（手机）· `16:9`（桌面）· `4:3`（平板）

```text
Mockup of a [PLATFORM: iOS / Android / Web] screen for [APP NAME — function],
status bar at top showing [TIME, BATTERY], navigation [TAB BAR / SIDE BAR] with 4 items
([ITEM1 with icon] · [ITEM2 with icon] · [ITEM3 with icon] · [ITEM4 with icon]),
content area: [DESCRIBE THE CARDS / LIST / CHART, with realistic but anonymized labels],
typography [SF Pro / Roboto / Inter], spacing 8-pt grid, light/dark mode [LIGHT / DARK].
Quote all UI labels exactly. No lorem ipsum. No spelling errors. Pixel-crisp icons.
```

**⚠️ 防坑**：
- 必明写**平台**（iOS / Android / Web），否则 UI 元素混乱（iOS 切回按钮 vs Android 汉堡）。
- 字体族对应：iOS=SF Pro，Android=Roboto，Web=Inter，写错会跑偏。
- 文案要"真实但匿名"（`Acme Inc.` / `John Doe`），不要 lorem。
- `8-pt grid` 让间距规整。

---

## T14 — 商品对比图 product comparison（来自 EvoLink comparison/ecommerce）

**推荐 size：** `1:1` 或 `4:3`

**模式 B JSON 模板**（推荐用，因为对比图必有多区块）：

```json
{
  "type": "product comparison split-screen",
  "theme": {
    "color_palette": "neutral background #F5F5F0, accent #FF5A1F, type #111111",
    "motif": "minimalist e-commerce"
  },
  "layout": {
    "structure": "vertical 50/50 split with center divider",
    "sections": [
      {
        "position": "left",
        "label_top": "{argument name=\"left_label\" default=\"BEFORE\"}",
        "subject": "{argument name=\"left_subject\" default=\"Old worn-out leather wallet\"}",
        "background": "muted gray gradient",
        "props": ["dust particles", "soft shadow"]
      },
      {
        "position": "right",
        "label_top": "{argument name=\"right_label\" default=\"AFTER\"}",
        "subject": "{argument name=\"right_subject\" default=\"New premium leather wallet\"}",
        "background": "warm beige gradient",
        "props": ["soft rim light", "crisp shadow"]
      }
    ],
    "divider": { "style": "thin vertical line, accent color, with small label \"VS\" centered" },
    "header": "{argument name=\"title\" default=\"Upgrade Your Everyday Carry\"}",
    "footer": "{argument name=\"cta\" default=\"Shop the new line →\"}"
  },
  "constraints": [
    "identical lighting direction on both sides for fair comparison",
    "same camera angle, same product scale",
    "sharp text, no spelling errors, no watermarks"
  ]
}
```

**⚠️ 防坑**：
- 两边**光源方向必须一致**（`identical lighting direction`），否则像两张拼图。
- 商品**大小比例必须一致**（`same product scale`），不然对比失真。
- "VS" 居中标签 + 同色系 divider 是对比图的标志性元素。

---

## T15 — 多格广告矩阵 ad-creative grid（来自 EvoLink ad-creative）

**推荐 size：** `1:1`（社媒）· `4:5`（IG feed）

**模式 B JSON 模板**：

```json
{
  "type": "2x2 advertising creative grid",
  "theme": {
    "color_palette": "{argument name=\"palette\" default=\"sunshine yellow #FFD43B + deep navy #1B2541 + cream #FFF8E7\"}",
    "motif": "{argument name=\"campaign_theme\" default=\"summer travel sale\"}"
  },
  "layout": {
    "structure": "2 columns x 2 rows, equal cells, 8px gutter, all cells share the same color palette",
    "sections": [
      {
        "position": "top-left",
        "type": "hero photograph",
        "subject": "{argument name=\"product_shot\" default=\"open suitcase with travel essentials\"}",
        "text_overlay": "{argument name=\"headline\" default=\"PACK SMART. GO FAR.\"}"
      },
      {
        "position": "top-right",
        "type": "big-number stat",
        "text_overlay": "{argument name=\"stat\" default=\"NEW DROP\"}",
        "subline": "{argument name=\"stat_sub\" default=\"Travel-ready luggage edit\"}"
      },
      {
        "position": "bottom-left",
        "type": "lifestyle scene",
        "subject": "{argument name=\"lifestyle\" default=\"traveler walking through airport with suitcase\"}"
      },
      {
        "position": "bottom-right",
        "type": "logo + CTA card",
        "logo_text": "{argument name=\"brand\" default=\"WAYFARE\"}",
        "cta": "{argument name=\"cta\" default=\"Shop now →\"}"
      }
    ]
  },
  "constraints": [
    "all four cells share the same color palette and lighting temperature",
    "consistent typography family across all text",
    "sharp text, no spelling errors, no watermarks, no extra cells"
  ]
}
```

**⚠️ 防坑**：
- 一定要 `all four cells share the same color palette and lighting temperature`，否则四宫格变拼贴。
- `no extra cells` — 不写的话经常会蹦出 5、6 格。
- 字体统一：写 `consistent typography family across all text`。

---

## T16 — Brand Identity Board（来自 EvoLink character/brand）

**推荐 size：** `3:2` 或 `16:9`

**模式 B JSON 模板**：

```json
{
  "type": "brand identity moodboard",
  "subject": "{argument name=\"brand_name\" default=\"BLOOM\"}",
  "layout": {
    "structure": "single canvas with 5 zones arranged like a magazine spread",
    "sections": [
      { "position": "top-left", "content": "logo lockup, primary mark + wordmark" },
      { "position": "top-right", "content": "color swatches: 5 chips with HEX labels under each" },
      { "position": "center", "content": "product hero photo / IP character render" },
      { "position": "bottom-left", "content": "typography specimen: 'Aa Bb Cc 123' in primary + secondary fonts with names labeled" },
      { "position": "bottom-right", "content": "icon set: 6 monoline icons in primary brand color" }
    ]
  },
  "theme": {
    "color_palette": "{argument name=\"palette\" default=\"#E8B4B8 + #6A4C93 + #F4F1DE + #2C2C2C\"}",
    "mood": "{argument name=\"mood\" default=\"warm, modern, feminine\"}"
  },
  "constraints": [
    "magazine-spread aesthetic, generous whitespace",
    "all HEX codes legible, all font names spelled correctly",
    "no watermarks"
  ]
}
```

**⚠️ 防坑**：
- 5 个区域必须明确**位置**（top-left/top-right/center/bottom-left/bottom-right），否则布局乱。
- 颜色给完整 HEX，不要只写颜色名。
- 字体规格必标 `'Aa Bb Cc 123'` 让模型生成字体样张。

---

## T17 — UI 全屏多模块（来自 EvoLink ui，最复杂场景）

**推荐 size：** `9:16`（手机）

**模式 B JSON 模板**：

```json
{
  "type": "mobile app full-screen mockup",
  "platform": "{argument name=\"platform\" default=\"iOS 17\"}",
  "app_context": "{argument name=\"app_purpose\" default=\"meditation app home screen\"}",
  "layout": {
    "structure": "vertical scroll, 8 distinct modules top to bottom",
    "sections": [
      { "module": "status_bar", "content": "9:41 time, full battery, 5G" },
      { "module": "header", "content": "greeting 'Good morning, {argument name=\"user_name\" default=\"Alex\"}' + avatar circle" },
      { "module": "hero_card", "content": "today's session card with image background and 'Start' button" },
      { "module": "category_chips", "content": "horizontal scroll of 5 chips: Sleep · Focus · Calm · Anxiety · Breath" },
      { "module": "session_grid", "content": "2x2 grid of session thumbnails with title and duration" },
      { "module": "progress_card", "content": "weekly streak: 7-day dot row with 5 filled" },
      { "module": "recommendation", "content": "horizontal carousel of 3 cards with cover art" },
      { "module": "bottom_tab_bar", "content": "5 tabs: Home (active) · Discover · Sessions · Stats · Profile" }
    ]
  },
  "theme": {
    "color_palette": "soft gradient dark navy → deep purple, accent gold #D4AF37",
    "typography": "SF Pro Display, weights 400/600",
    "spacing": "8-pt grid, 16px horizontal margin"
  },
  "constraints": [
    "pixel-perfect iOS-native look, rounded corners 12px on cards",
    "all UI labels are real-looking but anonymized, no lorem ipsum",
    "no spelling errors, no watermarks"
  ]
}
```

**⚠️ 防坑**：
- 模块必须**显式列出 6–10 个**，少了会出空屏，多了会挤。
- 每个模块写**一句话内容**，不要写"显示一些内容"。
- `pixel-perfect iOS-native look` 比 "iOS style" 强力得多。

---

## T18 — 场景叙事 narrative scene（来自 freestylefly 场景类）

**推荐 size：** `3:2` 或 `16:9`

```text
Narrative scene: [CHARACTER] [SPECIFIC ACTION] in [SETTING WITH 2-3 ENVIRONMENT DETAILS].
Mood: [EMOTION WORD], time: [SPECIFIC TIME OF DAY], weather: [CONDITION].
Cinematic composition: [RULE: rule of thirds / leading lines / center focus],
[FOREGROUND ELEMENT for depth], [MIDDLE GROUND main action], [BACKGROUND atmosphere].
Color grade [TEAL-ORANGE / DESATURATED / WARM AMBER], 35mm film look, slight grain.
Cinematic, photo-real. No watermarks. No text overlays. No modern props in period scenes. No blown-out highlights. No distorted faces.
```

**⚠️ 防坑**：
- 必须写**前景/中景/背景三层**，缺一层画面就扁。
- "Mood" 一个词足够（`melancholic` / `hopeful`），写多了模型混乱。
- `35mm film look` 是叙事感的关键 buff。

---

## 自检清单（写完 prompt 后过一遍）

- [ ] 选对模式（A 还是 B）？
- [ ] 模式 A：六槽位齐全？/ 模式 B：theme + layout + constraints 齐全？
- [ ] 画面内文字都用 `"..."` 包了，并标了字体？
- [ ] 负面词收尾（`No watermarks. No spelling errors.` 等）？
- [ ] `--size` 与模板推荐比例匹配？
- [ ] 4K 模板（`gpt-image-2-4k-count`）只用 16:9/9:16/2:1/1:2/21:9/9:21？
- [ ] 长度合规（A 中文 ≤200 字 / 英文 ≤120 词；B 每 section ≤8 字段）？
- [ ] 复用模板时 `{argument …}` 占位都已替换为最终值？
