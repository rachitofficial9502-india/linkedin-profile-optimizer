# analyzer.py (retry-on-invalid added)

from typing import Dict, Any
import json

from model.ollama_client import call_local_llm

from model.openrouter_client import call_openrouter_llm

from analyzer.config import OPENROUTER_MODEL, OPENROUTER_API_KEY


MODEL_BACKEND = "openrouter"
LOCAL_MODEL_NAME = "phi"

VALID_HEADLINE = {"missing", "generic", "clear"}
VALID_SUMMARY = {"missing", "thin", "substantive"}
VALID_SKILLS = {"missing", "generic", "focused"}

import ast

def _parse_llm_output(raw: str) -> dict:
    """
    Safely parses LLM output that may be:
    - valid JSON
    - JSON with extra text
    - Python-style dict
    """

    # 1️⃣ Extract JSON-like block
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("No object found in model output")

    block = raw[start:end + 1].strip()

    # 2️⃣ Try strict JSON first
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        pass

    # 3️⃣ Fallback: Python literal (safe)
    try:
        parsed = ast.literal_eval(block)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    raise RuntimeError("Failed to parse model output as JSON or dict")

def _validate_and_weaken(output: Dict[str, Any]) -> Dict[str, Any]:
    
    if output.get("headline_status") not in VALID_HEADLINE:
        output["headline_status"] = "generic"

    if output.get("summary_status") not in VALID_SUMMARY:
        output["summary_status"] = "thin"

    if output.get("skills_status") not in VALID_SKILLS:
        output["skills_status"] = "generic"

    if not isinstance(output.get("notes"), list):
        output["notes"] = []

    return output


def analyze_profile(input_data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(input_data, dict):
        raise ValueError("Analyzer input must be a dict")

    prompt = f"""
You are a deterministic classification engine.

Your job is ONLY to classify signal strength.
You are NOT a chatbot.
You are NOT an editor.
You are NOT allowed to summarize or rewrite.

You MUST return JSON only.

--------------------------------
OUTPUT SCHEMA (STRICT)
--------------------------------
{{
  "headline_status": "missing" | "generic" | "clear",
  "summary_status": "missing" | "thin" | "substantive",
  "skills_status": "missing" | "generic" | "focused",
  "notes": string[]
}}

No extra fields.
No explanations outside JSON.

--------------------------------
JUDGMENT RULES
--------------------------------

HEADLINE:
- "missing" → null or empty
- "generic" → identity or education only
- "clear" → states role, direction, or specialization

SUMMARY:
- "missing" → null or empty
- "thin" → short, vague, buzzwords, interests only
- "substantive" → explains work, learning, or building clearly

SKILLS:
- "missing" → empty or null
- "generic" → vague or mixed unrelated categories
- "focused" → concrete and relevant skills

If unsure, choose the WEAKER label.

--------------------------------
NOTES RULES
--------------------------------
- Notes must justify why a weaker or non-clear label was chosen.
- Notes must describe structural or signal issues.
- Do NOT copy sentences from input.
- Do NOT summarize content.
- Maximum 2 notes.
- Each note must be under 15 words.
- If no justification is needed, return [].

--------------------------------
INPUT
--------------------------------
{json.dumps(input_data)}
"""


    last_error = None

    for attempt in range(2):  # 🔁 retry once
        try:
            if MODEL_BACKEND == "local":
                raw = call_local_llm(
                    prompt=prompt,
                    model_name=LOCAL_MODEL_NAME
                )

            elif MODEL_BACKEND == "openrouter":
                raw = call_openrouter_llm(
                    prompt=prompt,
                    api_key=OPENROUTER_API_KEY,
                    model_name=OPENROUTER_MODEL
                )

            output = _parse_llm_output(raw)
            output = _validate_and_weaken(output)

            return output  # ✅ success

        except Exception as e:
            last_error = e

    # ❌ both attempts failed
    raise RuntimeError(f"Analyzer failed after retry: {last_error}")
