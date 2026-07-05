# Review Checklist

Use this before reporting that the analysis is complete.

## Output Checklist

- [ ] `ai_analysis/translated_prompts/INDEX.md` exists.
- [ ] `ai_analysis/AI_MODEL_USAGE_ANALYSIS.md` exists.
- [ ] Every confirmed prompt links to an original `path:line`.
- [ ] Every confirmed prompt explains its call scenario and code context.
- [ ] Test/example prompts are separated from production call-chain prompts.
- [ ] Model calls include provider/API, inputs, outputs, and evidence.
- [ ] Tool schemas include name, description, parameters, return value when discoverable, and call scenario.
- [ ] Context engineering describes sources, construction logic, and output consumption.
- [ ] Uncertain claims are marked `[待确认]` with reason.
- [ ] `.env` or secret-like values are not copied into any output.

## Good Output

- Evidence-first: claims point to files, line numbers, imports, or call sites.
- Decision-useful: summary tells the reader what the project uses LLMs for and what risks matter.
- Structured: reports can feed review, refactor planning, security review, or product explanation.
- Honest: missing evidence and ambiguity are visible.

## Bad Output

- Lists many keyword hits without confirming real model usage.
- Treats README prose, UI copy, or tests as production prompts.
- Translates prompts but misses how they are invoked.
- Describes tools without schema, parameter meaning, or model-facing value.
- Omits assumptions, risks, or unresolved questions.

## Failure Case Log

When a real analysis goes poorly, update the skill or references with the smallest durable fix:

```markdown
## Failure: [short name]
- Symptom:
- Missed/incorrect behavior:
- Root cause:
- Skill/resource update:
```
