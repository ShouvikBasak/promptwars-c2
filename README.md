# ElectEd India

**ElectEd India** is a conversational educational tool designed to provide clear, neutral, and grounded information about the Indian election process. It empowers citizens—especially first-time voters—with reliable knowledge directly from authoritative sources.

[![Cloud Run Deployment URL](https://img.shields.io/badge/Deployed-Cloud%20Run-blue)](https://elected-india-1075266329174.us-central1.run.app)

---

## Live Demo
Visit the live application here: **[ElectEd India](https://elected-india-1075266329174.us-central1.run.app)**

---

## Key Features

### Ask ElectEd (MVP)
A single-column conversational interface that answers questions about:
- Voter registration and eligibility.
- Election timelines and stages.
- The role of the Election Commission of India (ECI).
- The Model Code of Conduct (MCC).
- Civic education and voting procedures.

### Safety & Neutrality Guardrails
- **Intent Classification**: Every query is passed through a classification layer to ensure it remains within the educational scope.
- **Deterministic Refusals**: Out-of-scope queries (e.g., political opinions, predictions) are met with a hardcoded, non-hallucinated refusal: *"This information is not available in official Election Commission of India sources."*
- **No PII**: The system is stateless and does not collect any personal identifiable information (PII).

---

## Architecture

- **Frontend**: A zero-build React application styled with Tailwind CSS, focused on accessibility and mobile responsiveness.
- **Backend**: A stateless FastAPI (Python) orchestrator that manages session context and Vertex AI integration.
- **LLM**: Powered by **Gemini 2.5 Flash** on Google Cloud Vertex AI, enhanced with **Cloud Firestore** for static reference data.
- **Deployment**: Containerized with Docker and hosted on **Google Cloud Run** using production-grade IAM security.

---

## Google Cloud Services

ElectEd India is built natively on Google Cloud to ensure scalability, security, and observability:

- **Google Cloud Run**: Serverless compute platform used to host the stateless backend orchestrator.
- **Vertex AI (Gemini 2.5 Flash)**: Advanced LLM used for intent classification and grounded educational answer generation.
- **Cloud Logging**: Structured JSON logging for real-time observability and log analysis.
- **Cloud Monitoring**: Health checks and performance metrics derived from structured logs.
- **Error Reporting**: Automatic capture and alerting for unhandled server-side exceptions.
- **Cloud Firestore**: Serverless NoSQL database used as a read-only reference layer for static civic education content (glossary, FAQs).
- **Cloud IAM**: Fine-grained access control for service-to-service communication.

---

## Local Development

### Prerequisites
- Python 3.10+
- Google Cloud CLI (`gcloud`) authenticated with a project that has Vertex AI enabled.

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd promptwars-c2
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Authenticate with GCP**:
   ```bash
   gcloud auth application-default login
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="us-central1"
   ```

4. **Run the server**:
   ```bash
   cd backend
   uvicorn main:app --port 3000
   ```
5. **Access the app**: Open `http://localhost:3000` in your browser.

---

## Testing

The project includes a comprehensive backend test suite (`pytest`) covering:
- **Unit & Logic**: PII schema guarantees and intent classification handling.
- **Integration**: Full `/api/chat` flow with session history.
- **Negative & Edge Cases**: Handling of empty inputs, long strings, and malformed LLM responses.

**Vertex AI is mocked**: No GCP credentials or network access are required to run tests. The suite is fully deterministic and suitable for CI/CD environments.
- **CI/CD**: Tests are automatically executed via GitHub Actions on every push.
- **Coverage**: A detailed XML coverage report is generated (`coverage.xml`) for external auditing and integration.

### Run tests
Execute the single-command script to install dependencies and run the suite with coverage (generates `coverage.xml` and enforces a coverage threshold):
```bash
./scripts/run_tests.sh
```

---

## Disclaimer
*ElectEd India is an educational tool and is not officially affiliated with the Election Commission of India (ECI). All information provided is for educational purposes only.*
