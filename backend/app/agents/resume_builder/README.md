# Resume Builder Agent Interfaces

This package defines the Phase A contracts for the `resume-builder` feature.

## Scope
- Shared request/response schemas for all three scripts
- Prompt-boundary placeholders
- Model-selection configuration

This package does not yet implement:
- `.docx` rendering

## Planned module layout
- `contracts.py`: script input/output models shared by runners and tests
- `config.py`: model-selection registry sourced from settings
- `prompts.py`: isolated system-prompt text per script

## Script order
1. Job description normalization
2. Fit assessment + clarifying questions + tailored resume markdown
3. Markdown-to-`.docx` rendering

## Planned script contracts

### Script 1
- Input model: `JobDescriptionNormalizeRequest`
- Output model: `JobDescriptionNormalizeResult`
- Agent: `jd_to_markdown_agent.py`
- Runner: `jd_to_markdown_runner.py`
- CLI: `jd_to_markdown_cli.py`
- CLI contract: `--input-file <jd.txt> --output-path <job-description.md>`

### Script 2
- Input model: `ResumeMarkdownGenerateRequest`
- Output model: `ResumeMarkdownGenerateResult`

### Script 3
- Input model: `ResumeDocxRenderRequest`
- Output model: `ResumeDocxRenderResult`

## Integration rule
Runners, CLIs, and future API handlers should depend on these contracts rather than defining duplicate payload shapes.
