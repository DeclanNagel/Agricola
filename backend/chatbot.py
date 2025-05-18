from openai import OpenAI
#from sentence_transformers import SentenceTransformer
import numpy as np
import json
from pathlib import Path

#model = SentenceTransformer("all-MiniLM-L6-v2")


#vector_db = []  
session_cache = []
CACHE_LIMIT = 10

API_KEY = "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"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

MEMORY_FILE = Path("agricola_memory.json")

if MEMORY_FILE.exists():
    with open(MEMORY_FILE, "r") as f:
        vector_db = json.load(f)
else:
    vector_db = []

def store_in_memory(text: str):
    #embedding = model.encode(text).tolist()  # convert to list for JSON
    #vector_db.append({"embedding": embedding, "text": text})
    with open(MEMORY_FILE, "w") as f:
        json.dump(vector_db, f)
    
    session_cache.append(text)
    if len(session_cache) > CACHE_LIMIT:
        session_cache.pop(0)


def agricola_chat(prompt: str) -> str:
    recent_context = "\n".join(f"User said: {m}" for m in session_cache[-3:])
    full_prompt = f"{recent_context}\n\nCurrent question: {prompt}" if recent_context else prompt

    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[
            {"role": "system", "content": "You are Agricola, a helpful and practical AI farming assistant."},
            {"role": "user", "content": full_prompt}
        ]
    )
    answer = response.choices[0].message.content.strip()

    store_in_memory(prompt)
    store_in_memory(answer)

    return answer


