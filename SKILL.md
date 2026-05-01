---
name: gpt-image-2
version: 1.0.7
description: Generate or edit images via the RootFlowAI gpt-image-2 API with explicit control over model tier (1K / 2K / 4K, metered or count billing), aspect ratio (13 supported ratios), and prompt-engineering templates distilled from the awesome-gpt-image-2 communities. Use when the user asks to "draw / generate / create / edit / 出图 / 作图 / 生成图 / 改图 / P 图" with gpt-image-2 (RootFlowAI) and wants to choose image type (style/use-case) and size.
changelog:
  - "1.0.7 (2026-05-02): 同步 RootFlowAI quality 三档；默认始终 high 且不新增问答；仅当用户明确要求低质量预览/low quality/最低质量时使用 low，medium 只在用户明说时使用；脚本增加 quality 白名单校验；README/WORKFLOW/api 说明更新"
  - "1.0.6 (2026-05-01): 出图流程改为先选分辨率，再按分辨率动态展示比例；明确 1K/2K 支持 13 种比例，只有 4K 限 6 种宽幅；像素尺寸会映射到等价比例后执行 4K 校验；README 重写为完整使用说明"
  - "1.0.5 (2026-05-01): 合并问答为 2 轮；Q1 加费用提示；迭代改图闭环决策树；T02/T18 负向提示增强；WORKFLOW 新增 T16 Brand board 场景 E；4K 比例校验改为硬拦截；edit_image.py URL 限制说明；api.md 补充 URL 24h 有效期和 n=1 限制"
  - "1.0.1 (initial): 基础版本"
---

# gpt-image-2 (RootFlowAI)

> **设计目标：任何通用 agent（Coder / General / 自定义 agent…）加载本技能后都能照流程跑。**
> 流程是**强制**的：先问→再选→再跑→再报，少一步都可能踩坑（密钥 lane 错、4K 比例不匹配、提示词缺槽位…）。

---

## ✅ 0. 前置检查（每次必做，3 个动作）

1. **检查密钥**
   ```bash
   env | grep -E "ROOTFLOWAI_(METERED|COUNT|)_?API_KEY" || echo MISSING
   ```
   - 输出 `MISSING` → 用 `ask_user`（chat 模式）让用户贴 `<ROOTFLOWAI_API_KEY>`，**不要写入任何文件、不要 export 到 rc**。
   - **传入方式（重要，按可靠度排序）**：
     1. **首选 `--api-key "<ROOTFLOWAI_API_KEY>"`** — 直接当 CLI 参数传，跨 shell 兼容，通用 agent 跑 bash 工具最稳。
     2. 次选 `KEY=... python3 ...` 内联 export — 仅在你确定 shell 是 bash/zsh 时才用；通用 agent 调度的 `sh`/`dash` 可能不接受。
     3. 不要 `export KEY=...` 到 rc 文件，不要写入任何配置。
2. **确认密钥 lane**：用户给的 key 通常是 **count lane**（按张计费）。除非用户明说"我有按量 metered key"，否则一律走 `--profile count`。脚本现在 count / metered 两个 lane 都会回退读 `ROOTFLOWAI_API_KEY`，所以单一通用 key 也能跑。
3. **本技能脚本路径**：`{SKILL_DIR}/scripts/generate_image.py` 与 `edit_image.py`，纯 Python 3 标准库，无需 `pip install`。

---

## 🧭 1. 强制对话流程（任何 agent 都按这个顺序问 + 答）

> **核心原则**：agent 不是"按用户一句话脑补一张图"，而是**和用户共同把模糊主题拆成精确 prompt**。每一步都给用户**真实选择空间**（不要用 4 个固定按钮假装是全部），不会的就**反问**而不是脑补。
>
> **重要**：所有问答完成前**不要**跑脚本。每问用 `ask_user`（form 优先，多问可叠卡）。如果用户已在原始消息里明确给了某一步答案，可**跳过该问**但要在汇报里注明。

**先定分辨率，再定比例，2 轮问答完成出图**（用户体验优先，能跳过的问题直接跳）：

```
第 1 步（form 卡）：分辨率
  → 决定模型、费用、可选比例范围
第 2 步（form 卡）：比例 + 主题 + 模板 + 风格维度
  → 跑图
```

> 如果用户在原始消息里已给出某项答案，直接跳过该问，汇报时注明"已采用你说的 X"。
> `quality` 不作为常规问题询问。默认始终使用 `high`；只有用户明确要求"低质量预览 / low quality / 先低质量跑一张 / 最低质量"时才使用 `low`。`medium` 只在用户明确指定时使用。

### Q1 · 选**分辨率**（决定模型与费用）

| 档位 | 模型 | 费用 | 适合场景 |
|------|------|------|---------|
| **1K** | gpt-image-2-count | **¥0.10 / 张** | 日常配图、社媒缩略图、快速验证 |
| **2K** | gpt-image-2-hd-count | **¥0.25 / 张** | 海报、印刷小样、桌面壁纸（推荐默认） |
| **4K** | gpt-image-2-4k-count | **¥0.50 / 张** | 超清大图，仅支持 6 种宽幅比例 |

> 第一次出图建议先用 1K 验证构图，满意再升 2K/4K。

### Q2 · 选**尺寸 / 比例**（按 Q1 动态展示）

若 Q1 = **1K / 2K**，展示 13 种比例（直接传给 `--size`）：

```
1:1   3:2   2:3   4:3   3:4   5:4   4:5
16:9  9:16  2:1   1:2   21:9  9:21
```

若 Q1 = **4K**，只展示 6 种宽幅比例：

```
16:9  9:16  2:1  1:2  21:9  9:21
```

也接受像素串如 `1024x1024`、`1536x1024`，后端自动靠齐到最近比例。

**4K 限制**：若用户选 4K 但比例不在 `{16:9, 9:16, 2:1, 1:2, 21:9, 9:21}` → 提示并要求二选一：`换 2K` 或 `换宽幅`。

### Q2.5 · **质量 quality**（不询问，按明确指令覆盖）

RootFlowAI 支持 `low` / `medium` / `high` 三档质量，价格相同，只影响生成速度和细节。技能默认一律传 `--quality high`，不要因为用户说"快一点"、"先看看"、"草稿"、"预览"就自动降质量。

只有出现明确低质量请求时才用 `low`，例如：

```
低质量预览
用 low quality
先低质量跑一张
低清/低质量试一下
用最低质量
```

`medium` 只在用户明确说"用 medium / 中等质量"时使用。

### Q3 · **主题内容**（与 Q2 合并为第 2 步 form 卡）

- 用户已在原始消息里说了 → 直接用，跳过此问。
- 没说 → 在第 2 步 form 卡里加一个文本输入项："想画什么？一句话（例：高级感咖啡杯 / 公司新品海报 / 我家狗的卡通头像）"。
- 用户说"你帮我想" → 给 3 个不同方向的示例主题让用户挑，**不要直接选一个跑**。

### Q4 · **选模板**（第 2 轮 form 卡第 1 问：根据 Q3 主题动态筛 3-5 个候选 → 用户挑 → **如果都不对就走兜底**）

> **铁律**：**绝对不能**用 form 卡只列 4 个固定模板（用户会以为只有这 4 个）。一定要根据主题先筛，再用 form 卡列出**真正相关**的 3-5 个候选 + 一个 "都不对，给我看完整 18 套表" 选项 + 一个 "都不合适，走自由六槽位" 兜底选项。

#### 三层 Fallback 决策树

```
Q4 主题 → agent 自查 → 落入哪一层？
   │
   ├─【第 1 层】命中 18 套 T 模板？
   │     例："咖啡杯" → 强命中 T10 商品 / 弱命中 T18 场景
   │     例："产品海报" → 强命中 T04 海报 / 可选 T15 多格矩阵
   │     做法：列 2-3 个相关 T 候选 + 1 个 "都不对" 选项
   │
   ├─【第 2 层】T 模板不对，但 312 case 库有相似？
   │     例："霓虹便利店人像"（T01 太宽泛）→ 翻 cases/portrait.md
   │     做法：grep INDEX.md → 列 2-3 个 case 编号 + 一句话描述给用户挑
   │
   └─【第 3 层】case 库也没有 / 用户说"都不对"？
         做法：走"自由六槽位"流程（见 Q5 拆解，把六槽位空表给用户填）
         不要硬套 T 模板，承认没有现成模板，让用户和 agent 一起搭。
```

#### 18 套 T 模板速查（agent 内部用，不要整张直接给用户看）

| ID  | 类型                              | 模式 | 推荐比例           | 触发关键词（agent 自查） |
| --- | --------------------------------- | ---- | ------------------ | --- |
| T01 | 写实人像 / 摄影                   | A    | 2:3 或 3:2         | 人物、肖像、街拍、写真、模特 |
| T02 | 3D 手办 / 盲盒                    | A    | 1:1                | 手办、盲盒、潮玩、Q 版 3D |
| T03 | IP / Q 版形象                     | A    | 1:1 或 3:4         | 卡通形象、吉祥物、IP 设计 |
| T04 | 海报 / KV                         | A    | 2:3 或 3:4         | 海报、KV、宣传图、活动主视觉 |
| T05 | Logo / 品牌识别                   | A    | 1:1                | logo、商标、品牌符号、字标 |
| T06 | 信息图 / Infographic              | A    | 3:4 或 9:16        | 信息图、流程图、数据可视化 |
| T07 | 建筑 / 室内                       | A    | 3:2 或 16:9        | 建筑、室内设计、空间、装修 |
| T08 | 漫画 / 多格                       | A    | 3:4                | 漫画、多格、分镜、连环画 |
| T09 | 插画 / 绘本                       | A    | 4:3                | 儿童绘本、插画、童话 |
| T10 | 商品 / 电商                       | A    | 1:1 或 4:5         | 产品图、商品摄影、电商主图、白底图 |
| T11 | 历史 / 古风                       | A    | 3:2 或 2:3         | 古风、历史场景、汉服、复古 |
| T12 | 文档 / 出版物                     | A    | 3:4 或 2:3         | 书籍封面、杂志、出版物 |
| T13 | UI / 界面                         | A    | 9:16 / 16:9 / 4:3  | UI、界面、APP、网页设计 |
| T14 | 商品对比图 product comparison     | **B**| 1:1 或 4:3         | 对比、Before/After、产品对比 |
| T15 | 多格广告矩阵 ad-creative grid     | **B**| 1:1 或 4:5         | 多格广告、社媒矩阵、九宫格 |
| T16 | Brand identity board              | **B**| 3:2 或 16:9        | 品牌识别、VI 系统、提案板 |
| T17 | UI 全屏多模块（最复杂）           | **B**| 9:16               | 完整 APP 设计、全屏多组件 |
| T18 | 场景叙事 narrative scene          | A    | 3:2 或 16:9        | 故事场景、电影感、情绪图 |

**承载模式**：A 段落式（90% 场景）；B 结构化 JSON（多区块/复用模板必用，含 `{argument name="x" default="y"}` 参数槽）。

**操作**：用户选定 ID 后，**必须 `read references/prompt-patterns.md`** 取对应模板原文（含 ⚠️ 防坑段）。不要凭印象写。

#### Case 库（第 2 层兜底用）

| 分类文件 | case 数 | 适合什么场景 |
| --- | --- | --- |
| `cases/portrait.md` | 55 | 写实人像、闪光灯、CCD/胶片质感、街拍 |
| `cases/poster.md` | 101 | 海报、KV、电影感排版 |
| `cases/ui.md` | 56 | 手机 UI、网页 UI、组件 mockup |
| `cases/comparison.md` | 48 | 对比图、Before/After、信息分屏 |
| `cases/ecommerce.md` | 20 | 商品摄影、白底、场景图 |
| `cases/ad-creative.md` | 19 | 广告 banner、多格创意、社媒图 |
| `cases/character.md` | 13 | 角色设计、IP、Q 版 |

操作：`grep` `references/cases/INDEX.md` 找 case 编号 → `read` 对应分类文件取完整原文 → 改写成用户主题。

#### 第 3 层兜底 · 自由六槽位骨架（无模板）

```
Subject       主体（画什么、什么材质、什么状态）
Composition   构图（视角、机位高度、主体在画面位置）
Lighting      光线（主光方向、色温、阴影特征）
Style         风格（写实摄影 / 油画 / 3D / 日漫 / ...）
Color         调色（主色 + 辅色，最好给 hex 码）
Constraints   约束（不要什么：水印、文字、多余道具、变形）
```

agent 用 form 卡或 chat 把六槽位每一项**逐个反问**用户（一次问 2-3 项），不会的项给 3-4 个常见选项让用户挑。

### Q5 · **风格拆解**（第 2 轮 form 卡第 2 问：确定模板后，把模糊主题拆成可控选项）

> **为什么必须做**：模板有 6-10 个槽位，用户主题（如"咖啡杯"）只填了"主体"一项。其他槽位**不能由 agent 脑补**——必须用 form 卡反问 3-4 个**关键维度**让用户拍板，否则成图大概率不是用户想要的。

每套 T 模板的"必问拆解维度"（agent 速查表）：

| 模板 | 必问 3-4 个维度（form 卡每问 2-4 个选项 + "都不要 / 自定义"） |
| --- | --- |
| **T01 人像** | 性别+年龄段 / 拍摄风格（街拍/棚拍/胶片/CCD） / 表情情绪 / 服装风格 |
| **T02 手办** | 比例（1/7、Q 版、等比） / 材质（PVC、树脂、毛绒） / 底座样式 / 包装盒（裸件 or 带盒） |
| **T03 IP** | 角色类型（动物/人/拟人物） / 风格（扁平/3D 渲染/像素） / 颜色基调 / 表情系列（单图 or 9 宫格） |
| **T04 海报** | 主标题文字 / 副标题文字 / 主色调 / 排版重心（顶/中/底/左右） |
| **T05 Logo** | 品牌名 / 风格（极简字标/图形+字/徽章） / 配色 / 行业气质（科技/手作/复古） |
| **T06 信息图** | 数据条目数 / 图标风格（线性/扁平/3D） / 主色 / 文字密度 |
| **T07 建筑** | 室内 or 室外 / 风格（现代极简/北欧/工业/日式） / 时间（白天/黄昏/夜晚） / 视角（俯瞰/平视/仰视） |
| **T08 漫画** | 格数（4 / 6 / 9） / 画风（日漫/美漫/中式水墨） / 是否带文字气泡 / 情绪基调 |
| **T09 插画** | 年龄受众（幼儿/小学/全年龄） / 媒介（水彩/拼贴/数字绘） / 主色 / 角色数 |
| **T10 商品** | 视角（俯/三分之三/平/微距） / 背景（白底/木质/石板/场景） / 风格（极简/高级感冷/温暖手作/工业） / 是否带配件道具 |
| **T11 古风** | 朝代（唐/宋/明/清/泛汉风） / 主体（人物/场景/器物） / 配色（青绿山水/水墨/朱砂） / 情绪 |
| **T12 文档封面** | 用途（书籍/杂志/报告） / 排版风格（学院派/极简/插画封） / 主色 / 标题文字 |
| **T13 UI** | 平台（iOS/Android/Web） / 主题（亮/暗/玻璃拟态） / 主功能（社交/工具/电商/媒体） / 配色 |
| **T14 对比图** | 对比维度（Before/After、A vs B 产品） / 排版（左右/上下） / 主色 / 是否带标签文字 |
| **T15 多格广告** | 格数（2/4/6/9） / 共同视觉元素 / 品牌色 / 是否带 CTA 文字 |
| **T16 Brand board** | 品牌名 / 行业 / 关键词三个 / 配色方向（暖/冷/中性） |
| **T17 UI 全屏** | 平台 / APP 类型 / 模块清单（首页/详情/列表/...） / 主色 |
| **T18 场景叙事** | 时间地点 / 主角 / 情绪基调 / 镜头语言（特写/中景/全景） |

**操作**：agent 拿 Q3 主题 + Q4 模板 → 查上表 → 用 1-2 个 form 卡问出这 3-4 个维度（每问 3-4 个选项，每问都允许"都不要 / 自定义"）。

### Q6 · 最终汇总确认（可选但推荐）

复杂海报、品牌方案、要花钱的 4K 大图，跑之前用 chat 模式把**完整 prompt 中文摘要**贴给用户："我准备这样画：[摘要]，OK 就回'跑'，要改就告诉我改哪里。" 简单 1K demo 可跳过。

---

## ▶️ 2. 调用脚本（按 Q1 + Q2 选好的组合）

`{SKILL_DIR}` 指向本技能目录（例如 `~/.accio/accounts/.../skills/gpt-image-2`）。在通用 agent 里建议先 `cd` 进去再跑，命令更短。

> **CLI 参数速查**（已实跑验证）：必传 `--prompt`；可选 `--api-key` `--profile {auto,metered,count}` `--model` `--size` `--quality {low,medium,high}` `--n` `--image`（图生图，可重复 ≤16 次）`--output-dir` `--prefix` `--response-path` `--timeout`。**注意：不是 `--out`，是 `--output-dir`。**

### 2.1 文生图 — 1K（最常用）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-count \
  --prompt "<填好的模板正文>" \
  --size 1:1 --quality high \
  --output-dir ./out --prefix img
```

### 2.2 文生图 — 2K（推荐默认）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-hd-count \
  --prompt "..." --size 2:3 --quality high --output-dir ./out --prefix img
```

### 2.3 文生图 — 4K（仅 6 种宽幅 16:9 / 9:16 / 2:1 / 1:2 / 21:9 / 9:21）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-4k-count \
  --prompt "..." --size 21:9 --quality high --output-dir ./out --prefix img \
  --timeout 300            # 4K 必须显式拉长，默认 120s 会断
```

> ⚠️ **4K 性能 / 超时硬规则**（实测 2026-05 验证 + 官方 SLA 校准）
>
> | 项 | 数据 |
> |---|---|
> | **官方 4K 服务 SLA 上限** | **600 秒** ⏱️ — 超过即算法侧算力受限，不是网络问题 |
> | 4K 出图耗时（**简单单主体 + 短英文**） | 60-90 秒（基线，例 ICE COLD 可乐 9:16 = 80s） |
> | 4K 出图耗时（**多元素 + 中文/中英混排 + 多文字段**） | 120-180 秒（例 MARS 2026 火星 21:9 + 7 段中英文 = 150s） |
> | 4K 出图耗时（**繁忙时段 / 复杂叙事 / 多语言长 prompt**） | **180-600 秒**（理论上限，未实测，官方排队 + 推理叠加） |
> | 1K 出图耗时 | 12-15 秒 |
> | 2K 出图耗时 | 25-40 秒（实测 Accio Work 4 格 1:1 = 30s） |
> | 文件大小 | 4K 单张 **10-15 MB**；2K 约 4-6 MB；1K 约 1.5-2 MB |
> | bash 工具默认超时 | **120 秒** — 4K 必撞，**必须**绕开 |
>
> **耗时随复杂度增长的经验律**（实测 2026-05）：
> 元素数 ↑ + 文字段数 ↑ + 中文（vs 英文）→ 耗时**线性放大 1.5-2 倍**。
>
> ---
>
> **三阶段轮询策略（agent 跑 4K 必做，按这个分 60s/240s/600s 三阶段判断）**：
>
> ```
> 阶段 0 · 跑前告知用户
>     ──> 「4K 大概 1-3 分钟出图，繁忙时段最多排队 10 分钟，请稍等」
>     ──> 让用户知道**等是正常的**，不是卡死
>
> 阶段 1 · 0-240s 安静等
>     ──> 后台 nohup 跑脚本 + 每 10s 轮询文件落盘
>     ──> 这一阶段不打扰用户，覆盖 80%+ 简单和中复杂 prompt
>
> 阶段 2 · 240s 进度提示（如果还没出图）
>     ──> 给用户一句中间反馈「4K 还在生成中（已等 4 分钟），官方 SLA 上限 10 分钟，继续等候」
>     ──> 轮询间隔放宽到 60s/次
>
> 阶段 3 · 600s 判失败（硬性上限）
>     ──> kill 后台进程
>     ──> 返回用户「⚠️ 算力受限，本次 4K 排队超过 600s SLA，建议稍后重试 / 切回 2K / 简化 prompt」
>     ──> 不再无限等
> ```
>
> **完整 bash 模板**（agent 直接抄改）：
>
> ```bash
> # ① 跑前告知（用户层面）
> echo "⏳ 4K 提交中，预计 1-3 分钟，最多排队 10 分钟"
>
> # ② nohup 起后台 + heredoc 写 prompt 防 shell 转义
> cat > /tmp/p.txt <<'EOF'
> <YOUR_PROMPT_HERE>
> EOF
> PROMPT="$(cat /tmp/p.txt)"
>
> nohup python3 {SKILL_DIR}/scripts/generate_image.py \
>   --api-key "<ROOTFLOWAI_API_KEY>" --profile count --model gpt-image-2-4k-count \
>   --prompt "$PROMPT" --size 9:16 --quality high --output-dir "$OUT_DIR" --prefix img \
>   --response-path "$OUT_DIR/run.json" --timeout 600 \
>   > /tmp/img-bg.log 2>&1 &
> BG_PID=$!
> echo "PID=$BG_PID, started $(date '+%H:%M:%S')"
>
> # ③ 阶段 1+2+3 三阶段轮询（agent 在多次 bash 调用中执行；单次 bash 别超 100s 否则撞工具超时）
> # 阶段 1：每 10s × 24 次 = 240s
> for i in $(seq 1 24); do
>   [ -f "$OUT_DIR/img-01.png" ] && { echo "✅ 出图 @$((i*10))s"; exit 0; }
>   sleep 10
> done
> # —— 阶段 2 边界 —— agent 此时给用户一句「还在等」提示，再发一次 bash 跑下面：
> # 阶段 2：每 60s × 6 次 = 240→600s
> for i in $(seq 1 6); do
>   [ -f "$OUT_DIR/img-01.png" ] && { echo "✅ 出图 @$((240+i*60))s"; exit 0; }
>   sleep 60
> done
> # —— 阶段 3：600s 仍无图 —— 杀进程报失败
> ps -p $BG_PID > /dev/null && kill $BG_PID
> echo "⚠️ 算力受限：4K 排队超 600s SLA，请稍后重试 / 切 2K / 简化 prompt"
> exit 1
> ```
>
> **agent 执行注意**：
> - 上面 `for ... 24 次 = 240s` 单次 bash 跑得起（< 工具超时），但建议**拆成 3-4 个 bash 调用接力**，每次跑 60-80s，更稳；
> - 阶段 2 进入前**必须给用户进度提示**，否则用户会以为 agent 卡死；
> - prompt 含特殊字符（引号、`$`、反引号、JSON）一律走 `cat > /tmp/p.txt <<'EOF' ... EOF` heredoc，再 `PROMPT="$(cat /tmp/p.txt)"`。

### 2.4 图生图（最多 16 张参考，HTTPS URL 或本地路径）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-hd-count \
  --prompt "Restyle this portrait into a 1/7 collectible figure on an acrylic base." \
  --image https://example.com/photo.png \
  --image /Users/me/refs/board.jpg \
  --size 1:1 --quality high --output-dir ./out --prefix figure
```

### 2.5 局部编辑（multipart + 可选 mask）

> **注意**：`edit_image.py` 的 `--image` 和 `--mask` 只接受**本地绝对路径**，不支持 HTTPS URL（multipart 上传限制）。

```bash
python3 {SKILL_DIR}/scripts/edit_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-hd-count \
  --image /abs/portrait.jpg --mask /abs/mask.png \
  --prompt "Replace background with soft blue studio backdrop, keep subject unchanged." \
  --size 3:2 --quality high --output-dir ./out --prefix edit
```

### 2.6 metered（按量计费 lane，仅当用户明说时）

```bash
python3 {SKILL_DIR}/scripts/generate_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --prompt "..." --size 1:1 --quality high --output-dir ./out --prefix img
# 不传 --profile / --model，默认就是 metered + gpt-image-2
```

### 2.7 备选 — 内联环境变量（仅 bash/zsh 可用）

如果你确定 shell 是 bash/zsh，也可以这样写（与 `--api-key` 等价，不要混用）：

```bash
ROOTFLOWAI_API_KEY="<ROOTFLOWAI_API_KEY>" python3 {SKILL_DIR}/scripts/generate_image.py \
  --profile count --model gpt-image-2-count \
  --prompt "..." --size 1:1 --quality high --output-dir ./out --prefix img
```

`ROOTFLOWAI_API_KEY` 是通用回退名，count 和 metered 两个 lane 都识别。专用名（`ROOTFLOWAI_COUNT_API_KEY` / `ROOTFLOWAI_METERED_API_KEY`）优先级更高。

---

## 📊 3. 校验输出

每次脚本会在 stdout 打印一段 JSON，例如：

```json
{
  "saved": ["./out/img-01.png"],
  "skipped_items": [],
  "response_path": null,
  "model": "gpt-image-2-count",
  "profile_requested": "count",
  "profile_resolved": "count",
  "api_key_source": "ROOTFLOWAI_COUNT_API_KEY",
  "size": "1:1",
  "n_requested": 1,
  "n_saved": 1
}
```

**自检**：
- `n_saved == n_requested` ？否则报告差异。
- `skipped_items` 非空 → 把 `reason` 原样转给用户（多半是网络/CDN 问题）。
- 落盘文件存在且非 0 字节。

---

## 📤 4. 向用户汇报（必做）

1. 用 `see_image` **先看一眼**自己画出来的成品（避免离谱却报告"完成"）。
2. 在最终消息里**用 markdown 内嵌图**：
   ```markdown
   ![caption](./out/img-01.png)
   ```
3. 一句话说明：模型 / 分辨率 / 比例 / 质量 / 模板 ID / 落盘路径。
4. 主动给迭代选项（**必须给，不能省**）：

   > "不满意可以告诉我：**改哪里**（换背景/调色/换风格/局部修改）或**重新画**（换主题/换模板）。"

---

## 🔄 5. 迭代改图闭环（出图后用户反馈时必走此决策树）

```
用户反馈
   │
   ├─ "换背景 / 局部改 / 去掉某个元素 / 调整某区域"
   │     → 走 edit_image.py（2.5 节）
   │     → --image 传上一张落盘路径，--prompt 描述改动，--mask 可选
   │     → 不需要重走 Q1-Q5，直接跑
   │
   ├─ "整体重画 / 换风格 / 换模板 / 不满意"
   │     → 重走 Q4（选模板）+ Q5（风格拆解），跳过 Q1-Q3（参数不变）
   │     → 用新 prompt 重新调 generate_image.py
   │
   ├─ "换分辨率 / 换比例"
   │     → 重走 Q1+Q2，其余参数复用
   │     → 4K 比例校验照常执行
   │
   └─ "OK / 满意 / 好的"
         → 结束，提示用户图片已落盘路径，CDN URL 24h 后失效
```

**edit_image.py 快速模板**（局部改时直接抄）：

```bash
python3 {SKILL_DIR}/scripts/edit_image.py \
  --api-key "<ROOTFLOWAI_API_KEY>" \
  --profile count --model gpt-image-2-hd-count \
  --image <上一张落盘路径> \
  --prompt "<用户描述的改动>" \
  --size <原比例> --quality high --output-dir <原输出目录> --prefix edit
```

---

## 🛡️ 安全硬规则

- 远端 `--image` URL **必须 HTTPS**，localhost 与私网 IP 在运行时被阻断。
- 用户提供的 API key 仅在内存里传给脚本那一次；**禁止**写入文件、禁止 `export` 到 shell rc、禁止在日志/git 里出现。
- 本地图片自动 base64 → data URI 进 JSON body；`edit_image.py` 走 multipart。
- 服务方 CDN（`*.rootflowai.com`）下载时跳过 SSRF DNS 校验并自动遵循 `HTTPS_PROXY`/`HTTP_PROXY`，避免本机 fake-IP 代理（如 ClashX）误杀。

---

## 📁 文件结构

```
gpt-image-2/
├── SKILL.md                         ← 你正在读
├── WORKFLOW.md                      ← 4 个常见场景的端到端示例（可选阅读）
├── references/
│   ├── api.md                       ← API 完整规格、字段、错误码、env 变量
│   ├── prompt-patterns.md           ← 18 套模板（A 段落式 T01–T13/T18 + B JSON 式 T14–T17，必读）
│   └── cases/                        ← EvoLink 312 个真实 case 全量入库（INDEX.md + 7 类 md 文件）
└── scripts/
    ├── generate_image.py            ← 文生图 / 图生图（JSON body）
    ├── edit_image.py                ← 局部编辑（multipart，可选 mask）
    └── image_api_common.py          ← 通用：鉴权 / HTTP / SSRF / 落盘
```

## 📚 references（按需加载）

- `references/api.md` — endpoint、字段、错误格式、env 变量速查。
- `references/prompt-patterns.md` — **每次确定 Q3 后必读对应 T 段**。
- `WORKFLOW.md` — 4 个端到端场景示例（Logo / 海报 / 3D 手办 / 局部编辑），抄一遍就能跑。
