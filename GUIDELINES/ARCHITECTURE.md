# ElectEd India – Technical Architecture (MVP)

This document defines the **end-to-end technical architecture** for ElectEd India.

The architecture is intentionally derived from:
- The conversational UI design
- Safety and governance constraints
- Accessibility and inclusivity requirements
- Hackathon MVP scope (single-feature focus)

This is a **real, deployable architecture**, not a conceptual diagram.

This document must be read together with:
- `GUIDELINES/FEATURES.md`
- `GUIDELINES/SECURITY_AND_SAFETY.md`
- `GUIDELINES/ACCESSIBILITY.md`
- `GUIDELINES/UI_DESIGN.md`

---

## 1. Architecture Philosophy

ElectEd India follows a **UI-driven, safety-first, minimal architecture**.

Core principles:
- Conversation is the core capability
- No transactions, no workflows
- No personal data collection or storage
- Session-scoped state only
- Stateless backend execution
- Explicit use of Google services

The architecture exists solely to **support safe, educational conversation**.

---

## 2. High-Level System Architecture

Mandatory requirements:
- User (Browser: Mobile / Tablet / Desktop / Laptop)
- Responsive Web UI (Ask ElectEd)
- Conversation Orchestration Layer (Stateless)
- Gemini Model (Education-Only, Grounded)

There is:
- No database
- No user identity
- No long-term storage
- No cross-session memory

---

## 3. Tech Stack

### Build Platform
- **Google Antigravity**
  - Used to generate frontend and backend code
  - Used to enforce UI design principles
  - Used to iterate and verify UI behaviour
  - Used as the primary development and build tool

### Frontend
- Web-based UI generated via Antigravity
- Responsive design for:
  - Mobile browsers
  - Tablet browsers
  - Laptop and desktop browsers
- No native mobile apps (mobile web only)

### Backend
- Lightweight Node.js-based service (Antigravity default)
- Stateless execution model
- Handles:
  - Intent classification invocation
  - Context window management
  - Gemini API calls
  - Safety enforcement

---

## 4. Hosting and Deployment

### Hosting Platform
- **Google Cloud Run**

### Deployment Characteristics
- Serverless, container-based runtime
- Auto-scaling based on request load
- No server management required
- HTTPS by default

### Why Cloud Run
- Stateless architecture fits perfectly
- Cost-efficient for MVP workloads
- Simple and secure deployment
- Native integration with Gemini and Google Cloud IAM

---

## 5. Google Account and Project Model

- ElectEd India is hosted within a **Google Cloud Project**
- A **Google Account** is used to:
  - Create and manage the Cloud project
  - Enable required APIs
  - Configure Cloud Run
  - Manage secrets and IAM roles

There is no multi-project or multi-account complexity for MVP.

---

## 6. Google Services Used

The following Google services are intentionally and meaningfully used:

### 1. Google Antigravity
- Agent-first development platform
- Used to:
  - Generate UI and backend code
  - Apply UI design rules and accessibility constraints
  - Iterate safely on the application
  - Produce verifiable build artefacts

### 2. Gemini (via Vertex AI)
- Used as the **LLM reasoning engine** via Vertex AI
- Provides:
  - Natural language understanding
  - Multi-turn conversational context
  - Educational answer generation
- Operates under strict grounding and scope constraints

### 3. Google Cloud Run
- Hosts the backend service
- Executes stateless orchestration logic
- Provides scalable and secure runtime

### 4. Google Cloud IAM
- Controls access to:
  - Cloud Run services
  - Vertex AI (Gemini model access)
- Enforces least-privilege access
- No public exposure of secrets
### 5. Google Cloud Logging
- Provides structured JSON logging for real-time observability.
- Enables audit trails and latency tracking without PII leakage.

### 6. Google Cloud Monitoring
- Monitors system health via the `/health` endpoint and log-based metrics.

### 7. Google Cloud Error Reporting
- Automatically captures and aggregates server-side exceptions for rapid triage.

### 8. Google Cloud Firestore
- Used as a **read-only reference layer** for static civic education data.
- Stores non-PII content like election glossary terms and official links.
- Operates with a local JSON fallback to ensure high availability.

These services are **core to the architecture**, not add-ons.

---

## 7. Conversation Orchestration Layer

### Responsibilities
- Receive user input from UI
- Maintain session-scoped conversation context
- Enforce intent classification per turn
- Enforce refusal rules
- Prepare bounded context for Gemini
- Return responses to UI

### Stateless by Design
- No persistent memory
- No database
- No user sessions stored server-side

Session context is passed in-memory per request.

---

## 8. Conversation Context Management

### Scope
- Context exists only for the active browser session
- No cross-session reuse
- No personal information ever stored

### Context Window Rules
- Only the **last N turns** (e.g., 5–8 message pairs) are sent to Gemini
- Older messages are dropped silently
- No summarisation of dropped content

This ensures:
- Predictable behaviour
- Resistance to prompt-injection accumulation
- Efficient token usage

---

## 9. Intent Classification and Safety Enforcement

Every user message follows the same pipeline:

User Message → Intent Classification → In Scope → Answer Generation
→ Out of Scope → Deterministic Refusal

Key rules:
- Classification happens **on every turn**
- Prior valid turns do not relax restrictions
- Refusal message is fixed and consistent

This directly enforces the safety guarantees defined in
`SECURITY_AND_SAFETY.md`.

---

## 10. Gemini Model Usage

### Allowed Role
- Educational explanation engine
- Neutral, factual, and grounded responses

### Explicit Limitations
Gemini must not:
- Perform transactions
- Access open web search
- Infer personal details
- Retain memory across sessions
- Provide opinions or political persuasion

Gemini is invoked only after:
- Intent validation
- Context preparation
- Safety checks

---

## 11. Gemini Authentication Model

Gemini is accessed exclusively via **Vertex AI** using **service account–based
authentication**.

- No Gemini API keys are used in production
- Cloud Run uses its assigned service account
- Authentication relies on Application Default Credentials (ADC)
- No static secrets or long-lived credentials are embedded in the application
- Access is controlled via Google Cloud IAM

Required IAM role:
- roles/aiplatform.user

---

## 12. Observability

ElectEd India uses production-grade observability via Google Cloud native services:

### Structured Logging
- **Service**: Google Cloud Logging
- **Format**: JSON written to `stdout`.
- **Payload**: Includes `request_id`, `method`, `path`, `status_code`, and `latency_ms`.
- **Privacy**: User messages and bodies are strictly excluded from logs to prevent PII leakage.

### Health Monitoring
- **Endpoint**: `/health`
- **Purpose**: Used by Cloud Run and Cloud Monitoring to verify service availability and readiness.

### Error Tracking
- **Service**: Google Cloud Error Reporting
- **Implementation**: Global exception handlers log full tracebacks in a format recognized by Error Reporting, ensuring no stack traces leak to the end user.

---

## 13. Architectural Non-Goals (Intentional)

The following are deliberately excluded:
- User accounts or authentication
- Databases or long-term storage
- Personalisation or user profiling
- Workflow automation
- Decision-making or recommendations

Exclusion reduces risk and reinforces the educational mandate.

---

## 14. Architecture Summary

ElectEd India’s architecture is:

- Built using **Google Antigravity**
- Hosted on **Google Cloud Run**
- Powered by **Gemini**
- Enhanced with **Cloud Firestore** for static reference data
- Governed by strict safety and scope rules
- Stateless, minimal, and auditable
- Designed for inclusive access across devices

The system exists to **explain civic processes safely**, not to act on behalf of users.

