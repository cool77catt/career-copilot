# Resume Builder Agent Interfaces

This package defines the scriptable contracts and agents for the `resume-builder` feature.

## Scope
- Shared request/response schemas for resume-builder scripts
- Prompt-boundary placeholders
- Model-selection configuration

## Planned module layout
- `contracts.py`: script input/output models shared by runners and tests
- `config.py`: model-selection registry sourced from settings
- `prompts.py`: isolated system-prompt text per script

## Script order
1. Resume source import to markdown
2. Job description normalization
3. Fit assessment + clarifying questions + tailored resume markdown
4. Markdown-to-`.docx` rendering

### Resume Import Script
- Input model: `ResumeSourceToMarkdownRequest`
- Output model: `ResumeSourceToMarkdownResult`
- Agent: `resume_source_to_markdown_agent.py`
- Runner: `resume_source_to_markdown_runner.py`
- CLI: `resume_source_to_markdown_cli.py`
- CLI contract: `--input-resume-file <resume.pdf|resume.docx> --output-markdown-path <resume.md>`

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
- Agent: `assessment_agent.py`
- Runner: `assessment_runner.py`
- CLI: `assessment_cli.py`
- CLI contract:
  - `--job-description-file <job-description.md>`
  - optional context file args for profile/resume/linkedin/additional context
  - optional `--qa-json-file <qa.json>`
  - optional `--constraints-json-file <constraints.json>`
  - `--output-json-path <assessment.json>`
  - `--output-resume-markdown-path <tailored-resume.md>`

### Script 3
- Input model: `ResumeDocxRenderRequest`
- Output model: `ResumeDocxRenderResult`
- Renderer: `docx_renderer.py`
- Runner: `docx_runner.py`
- CLI: `render_docx_cli.py`
- CLI contract: `--resume-markdown-file <tailored-resume.md> --template-docx-file <template.docx> --output-docx-path <tailored-resume.docx>`

## Integration rule
Runners, CLIs, and future API handlers should depend on these contracts rather than defining duplicate payload shapes.
