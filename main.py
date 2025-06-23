from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Allow all origins (for now — restrict to frontend domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    judgment_text = data.get("judgment", "")

    if not judgment_text.strip():
        return {"error": "No judgment text provided."}

    api_key = os.getenv("OPENROUTER_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": (
                "You are a senior legal associate in a top Indian law firm. "
                "Summarize the given Indian or UK legal judgment into two parts:\n"
                "1. Legal Summary – formal tone, key issues, judgment, reasoning, and legal principles.\n"
                "2. Plain English Summary – simplified explanation for law students.\n"
                "Always ensure the case is real. If unsure, reply: '⚠️ I couldn’t find a real match for this case.'"
            )},
            {"role": "user", "content": judgment_text}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return {"summary": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}
