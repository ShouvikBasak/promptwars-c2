import os
import json
import uuid
import time
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai.types import GenerateContentConfig, Content, Part
from backend.reference_store import store

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "promptwars-hackathon-493401")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = "gemini-2.5-flash"

# Authenticate via ADC (Cloud Run service account or local gcloud credentials)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Google Cloud Observability & Structured Logging ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(message)s')

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    # Skip logging for health checks to keep logs clean
    if request.url.path == "/health":
        return await call_next(request)
        
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Structured log entry for Google Cloud Logging
        # We explicitly avoid logging the request body (user message) to protect privacy
        log_entry = {
            "severity": "INFO",
            "message": f"{request.method} {request.url.path} - {response.status_code}",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time, 2),
            "remote_addr": request.client.host if request.client else "unknown"
        }
        print(json.dumps(log_entry))
        
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        # Structured log for Error Reporting
        process_time = (time.time() - start_time) * 1000
        error_log = {
            "severity": "ERROR",
            "message": f"Unhandled Exception: {str(e)}",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "latency_ms": round(process_time, 2),
            "exception": traceback.format_exc(),
            "serviceContext": {"service": "elected-india-backend"}
        }
        print(json.dumps(error_log))
        # Return a safe error response
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "request_id": request_id}
        )

@app.get("/health")
async def health():
    """Operational health check for Cloud Run and Monitoring."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/_crash_test")
async def crash_test():
    """Hidden internal endpoint for verifying Error Reporting resilience."""
    raise RuntimeError("Intentional crash for observability verification")

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

def load_prompt(filename):
    # Absolute path regardless of cwd — critical for Cloud Run
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "PROMPTS", filename), "r") as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("GEMINI_SYSTEM_PROMPT.md")
INTENT_CLASSIFIER_PROMPT = load_prompt("INTENT_CLASSIFIER.md")
ANSWER_GENERATOR_PROMPT = load_prompt("ANSWER_GENERATOR.md")

# Immutable refusal string — never reaches the LLM
REFUSAL_MESSAGE = "This information is not available in official Election Commission of India sources."

@app.get("/api/reference")
async def get_reference(key: str = None):
    """
    Optional utility endpoint to fetch static reference content.
    If no key is provided, returns list of available keys.
    """
    if not key:
        return {"keys": store.list_reference_keys()}
    
    entry = store.get_reference(key)
    if not entry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reference key not found")
    
    return entry

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # --- Step 1: Intent Classification ---
        intent_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=request.message,
            config=GenerateContentConfig(
                system_instruction=INTENT_CLASSIFIER_PROMPT,
                response_mime_type="application/json",
                max_output_tokens=256,
            )
        )
        try:
            text = intent_response.text.strip().removeprefix("```json").removesuffix("```").strip()
            intent_data = json.loads(text)
        except Exception:
            # Safe default: refuse on parse failure
            intent_data = {"action": "REFUSE"}

        # --- Step 2: Deterministic refusal gate ---
        if intent_data.get("action") != "ANSWER":
            return {"response": REFUSAL_MESSAGE}

        # --- Step 3: Answer Generation with session context ---
        # Convert generic history dicts to google-genai Content objects
        history_contents = []
        for turn in request.history[-10:]:  # Max 5 pairs (10 messages)
            role = turn.get("role", "user")
            parts = turn.get("parts", [])
            text_parts = [Part(text=p.get("text", "")) for p in parts if p.get("text")]
            if text_parts:
                history_contents.append(Content(role=role, parts=text_parts))

        chat_session = client.chats.create(
            model=MODEL_NAME,
            config=GenerateContentConfig(
                system_instruction=f"{SYSTEM_PROMPT}\n\n{ANSWER_GENERATOR_PROMPT}",
            ),
            history=history_contents,
        )

        answer_response = chat_session.send_message(request.message)
        return {"response": answer_response.text}
    except Exception:
        # Structured log for Error Reporting
        error_log = {
            "severity": "ERROR",
            "message": "Resilience catch-all triggered in chat endpoint",
            "exception": traceback.format_exc(),
            "serviceContext": {"service": "elected-india-backend"}
        }
        print(json.dumps(error_log))
        # Catch-all for resilience: never leak stack traces, always refuse on error
        return {"response": REFUSAL_MESSAGE}

# Serve frontend — mounted last so /api/* routes take precedence
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
