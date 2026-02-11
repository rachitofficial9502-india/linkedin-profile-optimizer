import requests
import json
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"


def call_local_llm(prompt: str) -> str:
    """
    Calls a local Ollama LLM and returns the generated text.

    Raises RuntimeError on failure.
    """

    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to connect to Ollama: {e}")

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama returned {response.status_code}: {response.text}"
        )

    data = response.json()

    if "response" not in data:
        raise RuntimeError("Invalid response format from Ollama")

    return data["response"].strip()


# -----------------------------
# CLI usage
# -----------------------------
if __name__ == "__main__":
    try:
        prompt = input("Enter: ").strip()
        result = call_local_llm(prompt)
        print("\n--- LLM RESPONSE ---")
        print(result)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
