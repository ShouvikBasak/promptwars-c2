# ElectEd India – Feature Guidelines (MVP)

This document defines the **user-facing features** that the ElectEd India application must implement.

For the hackathon MVP, ElectEd India intentionally focuses on **a single core feature**, implemented with strong governance, safety, and responsible AI practices.

All features described here must comply with:
- `GUIDELINES/RULES.md`
- `GUIDELINES/QUESTIONS_SCOPE.md`
- All prompts under the `PROMPTS/` directory

---

## MVP Feature: Ask ElectEd – Interactive Search & Conversation

### Feature Intent

Provide a conversational interface that allows users to **ask natural-language questions** about Indian elections and receive **simple, clear, educational answers**, grounded only in authoritative sources from the Election Commission of India.

This feature is designed to safely handle **open-ended user input**, demonstrating responsible AI behavior under unrestricted questioning.

---

### What Ask ElectEd Provides

- A free-text input where users may ask *any* question in natural language
- Plain-language, easy-to-understand answers for all **in-scope** questions
- Deterministic refusal responses for all **out-of-scope** questions
- Educational explanations suited for first-time voters and general citizens

This feature combines **semantic search** and **conversational explanation**, without exposing raw documents or performing open web search.

---

### Supported Question Scope

Ask ElectEd supports **only** the in-scope question categories defined in `QUESTIONS_SCOPE.md`, including:

- Election process and lifecycle
- Election timelines and phases
- Voter eligibility and registration (educational explanation only)
- Roles of election officials and institutions
- Model Code of Conduct (awareness only)
- First-time voter and civic education

All user input must be evaluated using intent classification before answering.

---

### Interaction Model

- Conversational question-and-answer interaction
- No guided journeys or wizards in MVP
- No menus are required to access this feature

All interactions must follow this sequence:
1. Intent classification
2. Answer generation or refusal
3. Grounding verification

---

### Grounding and Answer Behavior

- All answers must be generated **only** from allowed ECI and SVEEP sources
- Answers must be:
  - Neutral
  - Factual
  - Educational
  - Free of opinions, predictions, or advice
- If information cannot be verified from allowed sources, the assistant must respond exactly with:

> “This information is not available in official Election Commission of India sources.”

---

### Explicit Non-Capabilities

Ask ElectEd must NOT:

- Ask for or accept personal voter data (such as EPIC number, phone number, or address)
- Perform voter lookups, registrations, corrections, or downloads
- Provide legal interpretation or enforcement guidance
- Offer political opinions, preferences, or predictions
- Answer questions related to elections outside India

All such requests must be handled using the refusal behavior defined in project guidelines.

---

### MVP Scope Declaration

For the hackathon MVP:

- **Ask ElectEd is the only implemented feature**
- Other educational features (guided journeys, timelines, explainers) are intentionally deferred
- The MVP prioritizes:
  - Safety
  - Correctness
  - Clarity
  - Responsible handling of open-ended user queries

This scope is intentionally narrow to demonstrate depth rather than breadth.

---

### Antigravity Guidance

When generating the user interface, the Antigravity agent must:

- Center the entire application experience around **Ask ElectEd**
- Avoid UI elements that suggest:
  - Transactions
  - Personal data entry
  - Official actions
- Clearly communicate that the application is educational and grounded in ECI sources
- Handle refusal responses in a clear, calm, and consistent manner

---

### Disclaimer

ElectEd India is an educational tool and is not affiliated with the Election Commission of India.
