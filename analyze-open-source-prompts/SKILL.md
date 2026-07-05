---
name: analyze-open-source-prompts
description: Use when analyzing a locally cloned open-source LLM or Agent repository for prompts, prompt templates, tool schemas, model API calls, or context-engineering logic; also for Chinese requests like 拆解开源项目提示词, 分析 Agent prompt, 提取工具 schema, 分析上下文工程.
---

# Analyze Open Source Prompts

## Overview

拆解本地开源 LLM/Agent 项目中的提示词、工具 schema、模型调用链和上下文工程，并在被分析项目根目录产出中文分析材料。

默认产物：

```text
ai_analysis/
├── translated_prompts/
│   ├── INDEX.md
│   └── ...
└── AI_MODEL_USAGE_ANALYSIS.md
```

## Workflow

1. **确认项目根目录**：先看 `README*`、包管理文件和顶层目录；用 `rg --files` 建立项目结构视图，识别 `src/`、`app/`、`lib/`、`prompts/`、`templates/`、`config/`、`agents/`、`tools/` 等目录。
2. **发现候选**：优先运行 `scripts/find_prompt_candidates.py <repo_root> --format markdown --output /tmp/prompt_candidates.md`，再结合 `rg -n` 深挖。扩展关键词见 `references/search-patterns.md`。
3. **确认真实调用**：完整阅读可疑文件；对代码内提示词查看前后约 20 行，并追踪导入、引用、模型请求和输出消费路径。
4. **文档化提示词**：在 `ai_analysis/translated_prompts/` 下为每个确认的提示词建立中文翻译文档，并维护 `INDEX.md`。模板见 `references/report-template.md`。
5. **分析上下文工程**：提取模型调用、上下文来源、工具 schema、循环控制或业务流程，判断项目是 Agent 型还是嵌入型。
6. **生成报告并自检**：创建 `ai_analysis/AI_MODEL_USAGE_ANALYSIS.md`，用 `references/review-checklist.md` 检查证据、假设、不确定性和下一步动作。

## 判断规则

- **真实提示词**：进入模型请求，或被拼接进 `messages`、`system`、`prompt`、`instructions`、tool/function description。
- **测试/示例提示词**：只在 tests、fixtures、examples、docs 中出现且未被生产代码引用；记录为参考，不计入核心调用链。
- **普通文案**：UI copy、日志、错误消息、README 说明，除非被传给模型，否则不要当提示词。
- **Agent 型项目**：LLM 负责计划、选择工具、根据工具结果继续或结束循环，即模型控制循环。
- **嵌入型项目**：LLM 是业务流程中的处理节点，如分类、抽取、改写、结构化或生成。
- **LLM 工具 schema**：随模型请求提供，或在提示词中介绍给模型使用；普通 REST/API schema 不要误判为工具。

## Resources

- `scripts/find_prompt_candidates.py`：无第三方依赖的候选扫描器；只辅助发现，不替代代码理解。
- `references/search-patterns.md`：搜索模式、框架线索、常见漏判和误判。
- `references/report-template.md`：报告、翻译文档和索引模板。
- `references/review-checklist.md`：输出自检、好坏标准和失败案例回填规则。

## Safety

- 不复制 `.env`、token、私钥、凭证或 secret 值；只记录键名、用途推断和引用位置。
- 动态生成提示词要提取模板、拼接逻辑、变量来源和最终调用点。
- 加密、压缩或混淆内容标注 `[无法解析]`，并说明原因。
- 未确认信息标注 `[待确认]`，不要用推测冒充事实。

## Done Criteria

- 报告链接到翻译文档和原代码位置。
- `INDEX.md` 覆盖所有确认提示词，并区分核心调用、测试示例和文档样例。
- 报告包含模型调用清单、工具 schema 清单、上下文来源、输出消费方式、风险和待确认项。
- 完成回复列出搜索范围、生成文件、提示词数量、工具数量、模型调用场景数量和待确认问题。
