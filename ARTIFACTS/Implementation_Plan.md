# ElectEd India MVP Implementation Plan

## A. Objective

The objective for the ElectEd India MVP is to build a single-feature, conversational web application called "Ask ElectEd". This application serves as a strictly educational tool to help users understand the Indian election process, timelines, and official steps, utilizing natural language queries. It is non-political, non-transactional, and explicitly avoids handling personal data or offering legal or predictive advice. 

The MVP will rely on a stateless architecture deployed on Google Cloud Run, utilizing Google's Gemini model via Vertex AI for intent classification and answer generation. Responses must be strictly grounded in official Election Commission of India (ECI) sources. A core tenet of the MVP is its deterministic safety mechanism: any out-of-scope query must yield a hardcoded refusal message with no variation. The UI will prioritize a conversation-first, accessible, and responsive design, mimicking modern AI chat interfaces without adding complex menus or dashboards.

## B. Execution Stages

*   **Stage 1: Build UI (Ask ElectEd)**
    *   Implement a responsive, single-column, conversation-first web interface.
    *   Ensure strict adherence to accessibility standards (keyboard navigation, high contrast, non-color-only indicators).
    *   Develop the chat interface with a fixed bottom input area and chronological message flow.
*   **Stage 2: Build backend orchestration (stateless) + Vertex AI Gemini integration**
    *   Set up a lightweight Node.js backend.
    *   Implement the stateless orchestration layer to handle session-scoped context (last N turns).
    *   Integrate Vertex AI Gemini using Google Cloud Application Default Credentials (ADC) via service account.
    *   Build the strict pipeline: Intent Classification -> Validation -> Answer Generation or Deterministic Refusal.
*   **Stage 3: Deploy to Cloud Run**
    *   Configure the Google Cloud Project and enable required APIs (Vertex AI).
    *   Set up the Cloud Run service for containerized, serverless execution.
    *   Configure IAM roles (e.g., `roles/aiplatform.user`) for the Cloud Run service account.
*   **Stage 4: Validate against TEST_PLAN.md**
    *   Execute functional tests for in-scope educational answers.
    *   Verify conversational continuity and context window limits.
    *   Rigorously test the deterministic refusal behavior against out-of-scope and adversarial queries.
    *   Perform accessibility and UI responsiveness audits across device types.

## C. File/Component Plan

*   `frontend/pages/index.tsx` (or equivalent main view): The single-page application entry point housing the conversational interface.
*   `frontend/components/ChatLayout`: The single-column container managing the message history and input area.
*   `frontend/components/MessageBubble`: The component rendering individual user and assistant messages, ensuring clear visual distinction and accessible typography.
*   `frontend/components/ChatInput`: The fixed bottom input field and submission action.
*   `frontend/components/DisclaimerFooter`: The persistent footer displaying the required non-affiliation disclaimer.
*   `backend/server.js` (or equivalent entry point): The stateless Node.js server handling API routes and serving the frontend.
*   `backend/services/orchestratorService`: The core logic managing the turn-by-turn pipeline, coordinating intent classification and generation.
*   `backend/services/llmService`: The module responsible for interacting with the Vertex AI Gemini API, using ADC.
*   `backend/utils/safetyValidator`: The module enforcing intent rules and returning the exact deterministic refusal string when necessary.

## D. Conversation Flow Wiring

1.  **User Input**: User submits a natural language query via the UI.
2.  **Context Preparation**: The backend receives the query and the current session's context window (strictly limited to the last N turns, maintained client-side or via ephemeral session memory, with no persistent storage).
3.  **Intent Classification**: The LLM evaluates the query against the allowed scope (e.g., election process, timelines, voter eligibility concepts).
4.  **Routing & Enforcement**:
    *   If **In-Scope**: The backend prompts the LLM to generate an educational, neutral answer grounded *only* in ECI sources.
    *   If **Out-of-Scope** (political, transactional, predictive, unverifiable): The backend intercepts the flow and instantly returns the immutable refusal string.
5.  **Response Delivery**: The generated answer or the refusal is sent back to the UI and appended to the chronological message flow.

## E. Security & Safety Enforcement Points

*   **Pipeline Interception**: Scope is enforced *before* answer generation. Every turn requires intent classification.
*   **Immutable Refusal**: The refusal wording (`“This information is not available in official Election Commission of India sources.”`) is hardcoded in the backend logic, preventing the LLM from softening, explaining, or altering it.
*   **Statelessness**: The backend maintains no database and no persistent user sessions, entirely eliminating the risk of storing personal data (PII).
*   **UI Constraints**: The UI completely lacks input fields for PII (like EPIC numbers) and transactional buttons, discouraging users from attempting official actions.
*   **Grounding Rules**: The prompt provided to the LLM strictly forbids the use of external knowledge or memory-based reasoning beyond the allowed ECI sources.

## F. Accessibility & Responsiveness Checklist

*   [ ] **Keyboard Navigation**: Entire UI, including the chat input and submission, is fully operable via keyboard (Tab, Enter).
*   [ ] **Focus Management**: Visible and distinct focus states exist for all interactive elements.
*   [ ] **High Contrast**: Text and background colors meet accessibility contrast ratios; no low-contrast aesthetic choices.
*   [ ] **Non-Color Dependence**: Message differentiation relies on alignment and spacing, not just color.
*   [ ] **Cognitive Simplicity**: Language is plain; layouts avoid heavy chrome, menus, or flashing animations.
*   [ ] **Device Responsiveness**: The single-column layout scales cleanly from mobile to desktop without horizontal scrolling; touch targets are adequately sized for mobile.

## G. Deployment Checklist (Cloud Run + Vertex AI)

*   [ ] **Project Setup**: Google Cloud Project created with billing enabled.
*   [ ] **API Enablement**: Vertex AI API enabled in the project.
*   [ ] **Service Account**: A dedicated service account is created for the Cloud Run instance.
*   [ ] **IAM Roles**: The service account is granted `roles/aiplatform.user` (minimum required role for Gemini invocation).
*   [ ] **Authentication**: The application uses Application Default Credentials (ADC) to authenticate with Google Cloud services. **No API keys are hardcoded or exposed to the client.**
*   [ ] **Cloud Run Configuration**: Service deployed as a stateless container, accessible via HTTPS.

## H. Test Plan Mapping

*   **Functional Testing** -> Validates that in-scope questions (e.g., "What is the electoral roll?") receive educational, neutral, and ECI-grounded answers.
*   **Conversational Continuity Testing** -> Validates that the context window (last N turns) correctly resolves pronouns and context without leaking across sessions.
*   **Intent Classification and Scope Enforcement** -> Validates that borderline questions are correctly categorized on *every single turn*.
*   **Deterministic Refusal Testing (Critical)** -> Validates that out-of-scope questions (e.g., "Predict the election result", "Check my voter ID") trigger the exact, hardcoded refusal string with zero variation.
*   **Safety and Abuse Testing** -> Validates that prompt injection or attempts to extract opinions fail and hit the refusal boundary.
*   **Accessibility & Responsive UI Testing** -> Validates keyboard navigation, contrast, and layout scaling on mobile, tablet, and desktop.
*   **Deployment Validation** -> Validates successful HTTPS loading and secure Gemini invocation via the service account.

## I. Risks & Non-goals Confirmation

**Non-Goals:**
*   No user accounts, authentication, or personalization.
*   No databases or long-term storage of conversation history.
*   No transactional workflows (e.g., voter registration actions).
*   No dashboards, multiple features, or exploratory UI elements.

**Common Agent Mistakes to Avoid:**
*   **Scope Creep**: Adding features like "save chat," "share," or "related questions." (Do not build these).
*   **Paraphrased Refusals**: Allowing the LLM to generate the refusal instead of using the hardcoded string. (Must use the exact string).
*   **Adding UI Fields**: Creating inputs for names or ID numbers to "help" the user. (Must remain a simple text box).
*   **Over-Styling**: Creating a UI that looks like an official government portal. (Must remain neutral and distinct).