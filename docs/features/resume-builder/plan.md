# Feature Plan - Resume Builder

## Goal
Deliver the `resume-builder` feature as a sequence of script-callable agent prototypes built and validated one at a time:
1. Resume source import script (`.pdf`/`.docx` -> markdown)
2. Job-description normalization script
3. Fit-assessment and tailored-resume markdown script
4. Markdown-to-`.docx` rendering script

Each script must be completed and validated before the next script is started.

## Phase B0 - Resume Source Import Agent
### Tasks
- Implement an agent that accepts a resume source file path (`.pdf` or `.docx`) and an output markdown path.
- Extract source text from supported file types locally.
- Normalize extracted text into markdown suitable for downstream resume-builder use.
- Ensure the agent writes the markdown artifact to disk and returns a script-consumable success result.
- Define validation behavior for unsupported file types, missing files, unreadable inputs, and invalid output paths.
- Add focused tests for `.pdf`/`.docx` handling and file-output behavior.

### Acceptance Criteria
- A script can invoke the agent with a `.pdf` or `.docx` resume file path and an output path.
- The agent writes normalized markdown to the requested path.
- Unsupported file types and missing files fail explicitly.
- Script output is usable as an input artifact for downstream resume-builder workflows.

## Phase A - Feature Contract and Agent Interface Design
### Tasks
- Define the three-agent workflow and the responsibility boundary for each agent.
- Define the implementation order and enforce single-script-at-a-time delivery.
- Define script invocation contracts for each agent:
  - Required inputs
  - Optional inputs
  - Output payloads
  - Output artifact paths
- Define initial output schemas for:
  - Job description markdown generation
  - Fit assessment
  - Gap assessment
  - Clarifying questions
  - Tailored resume markdown
  - Rendered `.docx` output metadata
- Define where prompt instructions, SDK invocation logic, and file I/O responsibilities will live.
- Document the prototype scope boundary so this phase remains decoupled from API/UI/DB integration.

### Acceptance Criteria
- Responsibilities for all three agents are documented and non-overlapping.
- The implementation order is explicit: script 1, then script 2, then script 3.
- Script entrypoint expectations are concrete enough to implement without further product clarification.
- Required outputs for each agent are explicit and testable.
- Prototype-only scope is clearly documented.

## Phase B - Script 1: Job Description Normalization Agent
### Tasks
- Implement an agent that accepts raw job-description text and an output markdown path.
- Normalize job-description text into structured markdown suitable for downstream use.
- Ensure the agent writes the markdown artifact to disk and returns a script-consumable success result.
- Define validation behavior for empty inputs, invalid output paths, and malformed source text.
- Add focused tests for normalization behavior and file-output handling.
- Do not begin implementation of script 2 until script 1 behavior is validated and accepted.

### Acceptance Criteria
- A script can invoke the agent with raw job-description text and an output path.
- The agent writes normalized markdown to the requested path.
- The output is usable as input for downstream resume-builder agents.
- Validation failures are explicit and test-covered.
- Script 1 is independently usable before any downstream scripts exist.

## Phase C - Script 2: Fit Assessment and Resume Markdown Agent
### Tasks
- Implement an agent that accepts:
  - Job description markdown
  - User profile
  - Resume
  - LinkedIn content
  - Other user attributes/context
  - Q&A context
  - Resume constraints
- Generate:
  - Percentage fit assessment
  - Gap assessment
  - Clarifying questions
  - Tailored resume markdown
- Define how follow-up Q&A is incorporated on reruns.
- Validate that unsupported claims are not introduced into generated outputs.
- Add focused tests for success paths, missing-input handling, and output schema compliance.
- Treat script 1 output as the required upstream input artifact for this phase.
- Do not begin implementation of script 3 until script 2 behavior is validated and accepted.

### Acceptance Criteria
- Script 2 starts only after script 1 is complete and validated.
- A script can invoke the agent with the required context inputs.
- The agent returns all four required outputs in a script-consumable structure.
- Fit scoring, gaps, and questions are grounded in supplied inputs.
- Tailored markdown resume respects the provided constraints.
- Tests cover both normal generation and key validation/error cases.

## Phase D - Script 3: Markdown-to-DOCX Rendering Agent
### Tasks
- Implement an agent or rendering workflow that accepts tailored resume markdown, a `.docx` template resume, and an output path.
- Generate a new `.docx` resume that preserves the template's formatting and structure as closely as practical.
- Define validation behavior for missing template files, unreadable templates, and invalid output destinations.
- Add focused tests for file generation and key formatting-preservation expectations.
- Treat script 2 output as the required upstream input artifact for this phase.

### Acceptance Criteria
- Script 3 starts only after script 2 is complete and validated.
- A script can invoke the renderer with markdown resume content and a `.docx` template.
- The workflow produces a new `.docx` file at the requested path.
- The source template remains unchanged.
- Key template structure/format preservation expectations are documented and tested.

## Phase E - Sequential Validation and Handoff Readiness
### Tasks
- Add script entrypoints for each agent so they can be exercised independently.
- Document environment-variable requirements for OpenAI SDK usage and model selection.
- After each script is completed, validate it in isolation before moving to the next script.
- Provide sample invocation patterns for local validation for each script as it is completed.
- Ensure each script's outputs are structured enough for the next script and for future backend integration.
- Keep the runner implementation modular so API integration can reuse the same agent services later.

### Acceptance Criteria
- Each script can be run locally with documented inputs.
- Environment requirements are documented.
- Each script's outputs can be consumed by the next stage or future service layer without ad hoc log parsing.

## Phase F - Integration Readiness
### Tasks
- Refine agent interfaces for later FastAPI integration without changing core behavior.
- Document future API surface expectations and artifact handoff assumptions.
- Identify where revisioning and persistence hooks will be added during full product integration.
- Record known limitations from the prototype validation stage.

### Acceptance Criteria
- The prototype agent layer is ready to be reused by later backend integration work.
- Known integration points and deferred concerns are documented.
- The feature docs accurately reflect the validated prototype behavior.

## Testing Plan
- Backend pytest coverage for:
  - Job-description normalization success path
  - Empty/invalid input handling for each agent
  - Fit/gap/question output contract validation
  - Resume markdown constraint handling
  - `.docx` template rendering success path
  - Failure cases for missing template or invalid output paths
- Use concise fixture inputs that represent realistic job descriptions, profiles, resumes, LinkedIn data, and Q&A.
- Prefer deterministic assertions on output structure and required content over brittle full-text matching.

## Definition of Done
- All phase acceptance criteria for the implemented phase are met
- Relevant pytest coverage passes
- Feature docs remain aligned with actual prototype behavior
- The resulting agent layer is callable from local scripts and ready for later project integration
