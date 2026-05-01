import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai.types import GenerateContentConfig, Content, Part

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

@app.post("/api/chat")
async def chat(request: ChatRequest):
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

# Serve frontend — mounted last so /api/* routes take precedence
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
