<div align="center">

# DPXX GPT 生图 Skill

面向 DPXX 工作流的 RootFlowAI GPT-Image-2 生图项目。

[简体中文](README.zh.md) · [English](README.md) · [版本 v1.1.1](https://github.com/yancyfeng999-star/dpxx-gpt-image-skill/releases/tag/v1.1.1)

![版本](https://img.shields.io/badge/version-v1.1.1-blue)
![渠道](https://img.shields.io/badge/provider-RootFlowAI-111827)
![模型](https://img.shields.io/badge/model-GPT--Image--2-10b981)
![Python](https://img.shields.io/badge/python-3.x-3776ab)

</div>

## 项目简介

`dpxx-gpt-image-skill` 是一个独立的 DPXX 生图技能项目，专注于通过 RootFlowAI 调用 GPT-Image-2 系列模型完成文生图、参考图生图和图片编辑。

这个仓库不依赖 Gemini 版本。客户如果更偏向 GPT-Image-2 的默认画面风格，可以单独安装和使用这个 skill。

## 核心特点

- 单独保留 GPT 生图流程，渠道为 RootFlowAI
- 复用 DPXX 的 prompt、请求、下载和输出规范
- 支持文生图、参考图生图和图片编辑
- 技能元数据、脚本元数据和 GitHub release 统一控版
- 公开文档不包含任何私密运行配置

## 模型映射

| 分辨率 | 模型 |
| --- | --- |
| 1K | `gpt-image-2-count` |
| 2K | `gpt-image-2-hd-count` |
| 4K | `gpt-image-2-4k-count` |

默认建议使用 `gpt-image-2-hd-count`。如果只是快速验证构图，可以先用 `gpt-image-2-count`。

## 比例规则

1K 和 2K 支持：

```text
1:1  3:2  2:3  4:3  3:4  5:4  4:5  16:9  9:16  2:1  1:2  21:9  9:21
```

4K 仅支持：

```text
16:9  9:16  2:1  1:2  21:9  9:21
```

## 快速开始

运行前请先在你的部署环境中完成 RootFlowAI 鉴权配置。所有私密凭证都应保留在运行环境里，不要提交到仓库。

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

## 使用流程

1. 根据目标分辨率选择 GPT 模型。
2. 按 `SKILL.md` 中的 DPXX prompt 规则整理提示词。
3. 使用 `scripts/generate_image.py` 并指定 `--profile gpt`。
4. 检查生成结果，根据画面继续优化 prompt。
5. 发布流程变更前，保持所有版本文件一致。

## 版本控制

当前版本：`v1.1.1`

- `SKILL.md` frontmatter 里的 `version` 是版本源头。
- `references/VERSION.md` 和 `scripts/VERSION.md` 必须与 `SKILL.md` 保持一致。
- GitHub release tag 使用同名语义版本号，例如 `v1.1.1`。
- 修改脚本、模型映射或用户可感知流程时必须提升版本号。

## 项目结构

```text
SKILL.md                 技能主说明
USER_GUIDE.md            用户操作指南
WORKFLOW.md              端到端生图流程
scripts/                 RootFlowAI 调用脚本
references/              prompt 模板和案例库
tests/                   单元测试
```
