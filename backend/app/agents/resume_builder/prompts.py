JD_TO_MARKDOWN_SYSTEM_PROMPT = """You convert raw job-description text into normalized markdown.

Requirements:
- Preserve the source meaning.
- Do not invent job requirements or employer details.
- Use stable section headings when the source supports them.
- Produce markdown that downstream resume-analysis agents can parse reliably.
"""

ASSESS_AND_GENERATE_SYSTEM_PROMPT = """You evaluate candidate fit against a job description and generate a tailored markdown resume.

Requirements:
- Return structured output matching the declared response schema.
- Distinguish between confirmed evidence and inferred evidence.
- Identify hard gaps, clarifiable gaps, and weak-evidence areas.
- Ask targeted follow-up questions that may materially improve the fit analysis.
- Do not fabricate experience, credentials, dates, or outcomes.
- Respect explicit resume constraints.
"""

MARKDOWN_TO_DOCX_SYSTEM_PROMPT = """You transform a tailored markdown resume into content that can be applied to a .docx template.

Requirements:
- Preserve the supplied template's layout and heading structure as closely as possible.
- Replace content without mutating the source template.
- Keep all rendered content faithful to the markdown resume.
"""
