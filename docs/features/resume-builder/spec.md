# Feature Spec - Resume Builder

## 1. Objective
Provide a resume-building workflow that:
- Accepts a job description and converts it into a normalized markdown artifact
- Evaluates how well the current user fits the target job
- Identifies missing or weak qualification areas
- Produces follow-up questions that may uncover evidence to improve fit
- Generates a tailored resume in markdown under explicit formatting/content constraints
- Converts the tailored markdown resume into a `.docx` resume that preserves a supplied template's structure and formatting

## 2. Current Delivery Scope
The first implementation phase for this feature is agent prototyping only.

In scope for the first phase:
- Define isolated agents runnable from scripts
- Use the OpenAI Python SDK for agent/model calls
- Accept file/text inputs and return the specified artifact outputs
- Validate agent inputs/outputs independently from the larger application

Out of scope for the first phase:
- FastAPI endpoint integration
- Next.js UI integration
- Database persistence
- Full artifact revisioning integration with the wider project
- Wiring this feature into the larger end-to-end user workflow

## 3. User Journey
1. An operator provides raw job-description text to the job-description normalization agent.
2. The agent writes a markdown version of the job description to the requested output path.
3. An operator provides the normalized job-description markdown plus the available candidate context to the assessment-and-resume agent.
4. The agent returns:
   - Fit assessment
   - Gap assessment
   - Clarifying questions
   - Tailored resume in markdown
5. An operator may collect answers to the generated questions and rerun the assessment-and-resume agent with the updated Q&A context.
6. Once the tailored markdown resume is acceptable, an operator provides it along with a `.docx` template resume to the docx-rendering agent.
7. The docx-rendering agent produces a new `.docx` resume that preserves the template's structure/format while replacing the content with the tailored markdown resume content.

## 4. Functional Requirements

## 4.1 Agent Architecture
- Each resume-builder agent must be implemented in an isolated module/directory under a clear backend agent namespace.
- Each agent must be invokable from a script without requiring API or frontend layers.
- The script entrypoints must accept explicit inputs and output destinations/return payloads suitable for local validation.
- The feature must use the OpenAI Python SDK for model invocation.
- Prompt instructions, output schemas, and file handling logic must be separated clearly enough to allow later API integration.

## 4.2 Agent 1: Job Description Text to Markdown
Purpose:
- Normalize a raw job description text input into a structured markdown artifact.

Inputs:
- Raw job description text
- Output file path for the markdown artifact

Behavior:
- Convert the input text into clean markdown with consistent sectioning when section boundaries are present or inferable.
- Preserve the original job-description meaning and requirements.
- Avoid inventing employer requirements not supported by the source text.
- Write the resulting markdown to the provided output path.

Outputs:
- Markdown file at the requested output path
- Script-friendly success response including the written file path

Acceptance-level output expectations:
- Responsibilities, qualifications, preferred qualifications, location/work mode, compensation, and other important details should be represented when present in the source text.
- The output should be readable by downstream agents without additional normalization.

## 4.2a Resume Source Import Agent: PDF/DOCX to Markdown
Purpose:
- Convert an incoming resume file (`.pdf` or `.docx`) into normalized markdown for downstream resume-builder workflows.

Inputs:
- Source resume file path
- Output markdown path

Behavior:
- Accept `.pdf` and `.docx` resume inputs.
- Extract source text locally from the file.
- Normalize the extracted content into clean resume markdown.
- Preserve the candidate's actual information without inventing new content.
- Write the resulting markdown to the provided output path.

Outputs:
- Markdown file at the requested output path
- Script-friendly success response including the written file path and detected source format

## 4.3 Agent 2: Fit Assessment, Gap Analysis, Clarifying Questions, and Tailored Resume Markdown
Purpose:
- Evaluate candidate fit against a normalized job description and produce a tailored markdown resume.

Inputs:
- Job description markdown
- User profile markdown/content
- Current resume content
- LinkedIn profile content
- Other structured or unstructured user attributes/context
- Existing Q&A context, if any
- Resume-generation constraints

Behavior:
- Analyze the job description against all supplied candidate context.
- Produce an overall fit assessment expressed as a percentage.
- Produce a structured breakdown of material gaps, uncertainties, and weak evidence areas.
- Produce a list of targeted follow-up questions intended to uncover missing evidence or clarify ambiguous fit areas.
- Generate a tailored resume in markdown aligned to the job description and constrained by supplied resume rules.
- When Q&A input is supplied, incorporate it into both the fit analysis and tailored resume output.

Required outputs:
- `fit_assessment`
- `gap_assessment`
- `clarifying_questions`
- `resume_markdown`

Fit assessment requirements:
- Must provide a percentage fit score.
- Must provide concise supporting rationale tied to the job description and candidate evidence.
- Must distinguish between confirmed strengths and inferred strengths.

Gap assessment requirements:
- Must identify missing qualifications, weak evidence, or ambiguous qualifications.
- Must separate hard gaps from gaps that may be closed with clarification.
- Must avoid presenting unsupported claims as facts.

Clarifying question requirements:
- Questions must be specific, answerable, and directly tied to an identified gap or uncertainty.
- Questions should aim to elicit evidence that may materially improve the resume or fit assessment.
- Questions must not ask for information irrelevant to the target role.

Resume markdown requirements:
- Must be tailored to the job description.
- Must adhere to supplied formatting/content constraints.
- Must not fabricate experience, credentials, or outcomes not supported by the provided inputs.
- Must emphasize the strongest relevant evidence from the candidate context.
- Must be suitable as the source for downstream `.docx` rendering.

## 4.4 Agent 3: Markdown Resume to Template-Preserved DOCX
Purpose:
- Render the tailored markdown resume into a `.docx` file using an existing `.docx` resume as the layout/template source.

Inputs:
- Tailored resume markdown
- Source template resume in `.docx` format
- Output file path for the generated `.docx`

Behavior:
- Parse the template resume structure and formatting.
- Replace the template content with content derived from the tailored markdown resume.
- Preserve heading hierarchy, section ordering where appropriate, formatting conventions, and overall template style as closely as possible.
- Produce a new `.docx` artifact rather than mutating the source template in place.

Outputs:
- Generated `.docx` file at the requested output path
- Script-friendly success response including the written file path

## 4.5 Resume Constraint Handling
- The assessment-and-resume agent must accept an explicit set of resume constraints as input.
- Constraint handling must be deterministic enough that later tests can assert compliance.
- Examples of constraints that the implementation should be prepared to support:
  - Section ordering
  - Maximum length/page guidance
  - Tone/style rules
  - Prohibitions on unsupported claims
  - Required inclusion/exclusion rules
- The exact constraint schema may evolve during implementation, but it must be documented before code integration.

## 4.6 Script Invocation Requirements
- Each agent must be callable from a local script with a documented set of inputs.
- Inputs must support both file-based and direct-text values where practical for local validation.
- Outputs must be script-consumable and not require manual parsing of free-form console logs alone.
- Non-zero exit behavior and validation errors must be explicit for invalid or missing inputs.

## 5. Data and Artifact Rules
- During the prototype phase, artifacts may be written directly to local filesystem paths supplied to scripts.
- Markdown artifacts remain the source of truth for:
  - Normalized job descriptions
  - Tailored resumes
  - Fit/gap/question outputs when persisted
- The `.docx` output is a derived artifact generated from the markdown resume plus template resume.
- When this feature is integrated into the wider system, artifact paths and revisioning must comply with global artifact rules.

## 6. API Surface (Future Integration Target)
The first phase does not require API implementation, but future integration is expected to align to a surface similar to:
- `POST /resume-builder/job-description/normalize`
- `POST /resume-builder/assess-and-generate`
- `POST /resume-builder/render-docx`

## 7. Agent and CLI Requirements
- Agents must be runnable from CLI/script and later reusable from backend services.
- Agent prompts/configuration should be isolated from transport/invocation code.
- Use environment variables for OpenAI credentials and model configuration.
- The implementation should support swapping model identifiers without rewriting agent business logic.

## 8. Acceptance Criteria
- A feature-level design exists for three distinct resume-builder agents.
- The first phase scope is explicitly limited to script-callable agent prototypes.
- Agent 1 is defined to accept raw job-description text and an output path, and to write normalized markdown.
- Agent 2 is defined to accept job-description markdown plus candidate context and to return fit assessment, gap assessment, clarifying questions, and tailored resume markdown.
- Agent 3 is defined to accept tailored resume markdown plus a `.docx` template and to produce a new `.docx` resume preserving template structure/format.
- OpenAI Python SDK usage is explicitly part of the feature contract.
- The spec clearly distinguishes current prototype scope from later application integration.
