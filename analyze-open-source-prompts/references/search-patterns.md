# Search Patterns

Use this reference when candidate discovery feels incomplete or the project uses LLM frameworks rather than direct API calls.

## File and Directory Clues

- Names: `prompt`, `prompts`, `template`, `templates`, `instruction`, `instructions`, `system`, `agent`, `tool`, `function`, `schema`.
- Directories: `prompts/`, `templates/`, `agents/`, `tools/`, `chains/`, `workflows/`, `evals/`, `examples/`, `fixtures/`.
- Extensions: `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`.

## Code Keywords

- Prompt variables: `system_prompt`, `user_prompt`, `developer_prompt`, `prompt_template`, `PromptTemplate`, `ChatPromptTemplate`, `instructions`, `messages`.
- OpenAI-style calls: `chat.completions`, `responses.create`, `openai.ChatCompletion`, `beta.chat.completions`, `client.responses`.
- Anthropic-style calls: `anthropic.messages`, `messages.create`, `system=`, `tools=`, `tool_choice=`.
- Google/Gemini-style calls: `genai`, `google.generativeai`, `generate_content`, `system_instruction`, `contents=`.
- Generic LLM calls: `generate(`, `streamText`, `generateText`, `invoke(`, `ainvoke(`, `complete(`, `chat(`.

## Framework Clues

- LangChain: `langchain`, `ChatPromptTemplate`, `PromptTemplate`, `Runnable`, `AgentExecutor`, `create_react_agent`.
- LangGraph: `langgraph`, `StateGraph`, `create_react_agent`, `ToolNode`, `messages_state`.
- LlamaIndex: `llama_index`, `ServiceContext`, `QueryEngine`, `ChatEngine`, `PromptTemplate`.
- CrewAI: `crewai`, `Agent(`, `Task(`, `Crew(`, `backstory`, `expected_output`.
- AutoGen: `autogen`, `AssistantAgent`, `UserProxyAgent`, `system_message`, `register_for_llm`.
- Vercel AI SDK: `ai/react`, `ai`, `streamText`, `generateObject`, `tool(`, `zodSchema`.
- LiteLLM: `litellm`, `completion(`, `acompletion(`, `router.completion`.

## Tool Schema Clues

- OpenAI tools/functions: `tools`, `tool_choice`, `function_call`, `functions`, `parameters`, `strict`.
- Anthropic tools: `input_schema`, `tool_use`, `tool_result`.
- JSON schema: `json_schema`, `schema`, `properties`, `required`, `additionalProperties`.
- Zod: `z.object`, `z.string`, `z.enum`, `zodToJsonSchema`.
- MCP: `MCP`, `mcp`, `server.tool`, `list_tools`, `call_tool`.

## Common Misses

- Prompt fragments split across constants and joined later.
- Tool descriptions generated from docstrings, decorators, or schema helpers.
- Prompts stored in YAML/JSON config rather than source files.
- Real prompts inside examples that are imported by production code.
- System prompts named `policy`, `persona`, `role`, `behavior`, or `rules`.

## Common False Positives

- README examples not imported or executed.
- Test fixtures that only mock model output.
- UI labels, logs, and error messages never sent to a model.
- Business API schemas not exposed to the model as tools.
- Data validation schemas used only before or after model calls.
