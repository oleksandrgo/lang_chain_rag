---
name: testcase-rag-impact
description: Runs test-case impact analysis from free-text chat input using Chroma retrieval and LLM summarization. Use when the user asks to find potentially impacted test cases, build regression scope, or analyze what to test for a new feature.
---

# Testcase RAG Impact

## Purpose
Use this skill when the user provides a free-text request in Cursor chat and wants:
- potentially impacted test cases from the vector DB,
- a compact QA analysis,
- source-backed output.

## Required workflow
1. Extract the user request text from chat as-is.
2. Run:
```bash
python scripts/chat_testcase_rag.py --persist-directory ./chroma_db --collection test_cases_chunks --k 6
```
3. Pass the user request to the script interactive prompt.
4. Use the script output block `--- Context for Cursor LLM ---` as grounding context.
5. Produce a compact response in this exact structure:
   - `## Summary`
   - `## Potentially impacted test cases`
   - `## What to test first`
   - `## Sources`

## Output rules
- Keep it compact and practical.
- Ground claims in retrieved context.
- If context is weak, explicitly say what is missing.
- Keep source references visible (metadata/doc ids).

## Failure handling
- If `OPENAI_API_KEY` is missing: ask user to set it in `.env`.
- If collection is empty/missing: tell user to run ingest first via `scripts/load_chunks_to_chroma.py`.
- If nothing relevant is retrieved: return that no strong matches were found and suggest query refinement.

## Examples
- "Новая фича меняет ERL в потоке quote. Какие тест-кейсы могут быть задеты?"
- "Собери список тестов для регресса по sampling rules."

## Additional resources
- Detailed tips and prompts: [reference.md](reference.md)
