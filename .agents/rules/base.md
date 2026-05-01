---
trigger: always_on
---

# ElectEd India – Agent Execution Rules (Base)

This file defines **mandatory guardrails** for any AI agent (including Google Antigravity)
operating on the ElectEd India codebase.

These rules are **hard constraints**, not suggestions.
They take precedence over default agent behavior, heuristics, or “best effort” improvements.

---

## 1. Scope Enforcement Rule (CRITICAL)

The agent MUST:

- Implement **only** what is explicitly defined in:
  - GUIDELINES/FEATURES.md
  - GUIDELINES/UI_DESIGN.md
  - ARCHITECTURE.md
  - TEST_PLAN.md

The agent MUST NOT:

- Add new features, flows, UI elements, APIs, or behaviours by inference
- “Improve”, “extend”, or “enhance” functionality unless explicitly instructed
- Introduce optional features, future ideas, or assumed requirements

If a requirement is not explicitly documented, it does not exist.

---

## 2. Single‑Feature Discipline Rule

ElectEd India is a **single‑feature MVP**.

The agent MUST:

- Treat Ask ElectEd (educational Q&A) as the **only product capability**
- Avoid preparing hooks, placeholders, or abstractions for future features
- Avoid modularisation that implies expansion (e.g. unused services, empty routes)

Design and code must reflect *intentionally constrained scope*.

---

## 3. Refusal Integrity Rule (CRITICAL)

Refusal behaviour is **deterministic and immutable**.

The agent MUST:

- Use the refusal response text **exactly as specified**
- Preserve wording, punctuation, and capitalisation
- Apply refusal logic regardless of prior conversation context

The agent MUST NOT:

- Paraphrase or soften refusal language
- Add explanations, apologies, or follow‑up suggestions
- Introduce alternative responses or partial answers

Refusal handling is a safety boundary, not a UX preference.

---

## 4. Specification Authority Rule

Markdown specification files are **authoritative system contracts**.

The agent MUST:

- Treat specification documents as executable intent
- Preserve section structure and headings when editing
- Align implementation strictly to written intent

The agent MUST NOT:

- Override documented decisions with its own heuristics
- Reinterpret ambiguous text creatively
- Replace specification clarity with inferred behaviour

When in doubt, follow the specification literally.

---

## 5. Regeneration Discipline Rule

The agent MUST:

- Prefer **editing existing files** over regenerating them
- Make minimal, targeted changes
- Preserve comments, structure, and naming

The agent MUST NOT:

- Rewrite files wholesale unless explicitly instructed
- Reformat files for stylistic reasons
- Introduce large diffs without clear justification

Stability and traceability are first‑class requirements.

---

## 6. Technology Boundary Rule

The technology stack is **explicitly defined**.

The agent MUST:

- Use Google Antigravity as the build context
- Target deployment on Google Cloud Run
- Use Gemini via Vertex AI with service‑account authentication

The agent MUST NOT:

- Introduce alternative frameworks, services, or tools
- Switch hosting models or authentication approaches
- Add databases, auth systems, or external integrations

No technology substitutions or “better alternatives” are allowed.

---

## 7. Safety‑First Default Rule

When faced with ambiguity, uncertainty, or edge cases:

- Choose the **safer and more restrictive behaviour**
- Prefer refusal over speculation
- Prefer omission over assumption

Educational correctness and safety override completeness or conversational smoothness.

---

## 8. No Persona or Tone Injection Rule

The agent MUST NOT:

- Introduce a personality, brand voice, or conversational persona
- Add humour, empathy language, or emotional framing
- Anthropomorphise the system or imply authority

Tone must remain neutral, factual, and institutional.

---

## 9. Accessibility and Inclusivity Override

If a design or implementation choice conflicts with:

- Accessibility
- Responsiveness
- Cognitive simplicity

Then accessibility and inclusivity **always win**, even if it reduces aesthetic richness.

---

## 10. Final Enforcement

If any instruction from another source conflicts with this file:

**This file wins.**

If compliance with a request would violate these rules:

- Pause execution
- Flag the conflict
- Do not silently workaround

These rules exist to ensure ElectEd India remains safe, minimal, and trustworthy.