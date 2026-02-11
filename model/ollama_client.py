# model/ollama_client.py

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_local_llm(prompt: str, model_name: str) -> str:
    """
    Calls a local Ollama model.
    """

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama error {response.status_code}: {response.text}"
        )

    data = response.json()

    if "response" not in data:
        raise RuntimeError("Invalid Ollama response format")

    return data["response"].strip()


result = call_local_llm("Hi phi.", "phi")
print(result)