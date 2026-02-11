# model/openrouter_client.py

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_llm(prompt: str, api_key: str, model_name: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a strict JSON classification engine."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter error: {response.text}")

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()
