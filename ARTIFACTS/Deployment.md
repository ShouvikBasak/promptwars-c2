# Deployment Documentation

This document outlines the production deployment configuration for the ElectEd India MVP.

## Infrastructure Overview

| Component | Service | Details |
| :--- | :--- | :--- |
| **Compute** | Google Cloud Run | Serverless container execution |
| **Model API** | Vertex AI | Gemini 2.5 Flash via `google-genai` SDK |
| **Registry** | Artifact Registry | Container image storage |
| **Logging** | Cloud Logging | Application and system logs |

## Deployment Details

- **Project ID**: `promptwars-hackathon-493401`
- **Region**: `us-central1`
- **Service Name**: `elected-india`
- **Public URL**: [https://elected-india-1075266329174.us-central1.run.app](https://elected-india-1075266329174.us-central1.run.app)

## Security & IAM

The service runs under a dedicated Service Account with **Least Privilege** access:

- **Service Account**: `elected-india-sa@promptwars-hackathon-493401.iam.gserviceaccount.com`
- **Roles**:
    - `roles/aiplatform.user`: Inference access to Vertex AI models.
    - `roles/logging.logWriter`: Ability to send logs to Cloud Logging.

**Authentication**: The application uses **Application Default Credentials (ADC)**. No API keys are stored in the codebase or environment variables.

## Configuration

### Environment Variables
- `GOOGLE_CLOUD_PROJECT`: `promptwars-hackathon-493401`
- `GOOGLE_CLOUD_LOCATION`: `us-central1`

### Container Image
- **Base Image**: `python:3.12-slim`
- **Server**: `uvicorn` (FastAPI)
- **Port**: `8080`

## Deployment Command
```bash
gcloud run deploy elected-india \
  --image us-central1-docker.pkg.dev/promptwars-hackathon-493401/elected-india/elected-india-app:latest \
  --region us-central1 \
  --platform managed \
  --service-account elected-india-sa@promptwars-hackathon-493401.iam.gserviceaccount.com \
  --set-env-vars GOOGLE_CLOUD_PROJECT=promptwars-hackathon-493401,GOOGLE_CLOUD_LOCATION=us-central1
```
