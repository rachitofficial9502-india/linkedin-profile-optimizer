from typing import List, Dict


def detect_sections(lines: List[str]) -> Dict[str, object]:
    """
    Section detector for LinkedIn PDFs using column-aware ordered lines.

    Extracts:
    - name
    - headline
    - about (Summary only)
    - top_skills (from left column only)

    Assumes <<COLUMN_BREAK>> is present.
    """

    result = {
        "name": None,
        "headline": [],
        "about": [],
        "top_skills": [],
    }

    # ----------------------------------
    # 1. Split left / right columns
    # ----------------------------------
    try:
        split_idx = lines.index("<<COLUMN_BREAK>>")
        left_column = lines[:split_idx]
        right_column = lines[split_idx + 1 :]
    except ValueError:
        # Fallback: treat everything as right column
        left_column = []
        right_column = lines[:]

    # ----------------------------------
    # 2. LEFT COLUMN → Top Skills only
    # ----------------------------------
    collecting_top_skills = False

    for line in left_column:
        lower = line.lower().strip()

        if lower == "top skills":
            collecting_top_skills = True
            continue

        # Stop if another known heading starts
        if collecting_top_skills and lower in {
            "certifications",
            "education",
            "experience",
            "languages"
        }:
            break

        if collecting_top_skills:
            if line.strip():
                result["top_skills"].append(line.strip())

    # ----------------------------------
    # 3. RIGHT COLUMN → Name + Headline + About
    # ----------------------------------
    idx = 0
    n = len(right_column)

    # --- Name ---
    while idx < n and not right_column[idx].strip():
        idx += 1

    if idx < n:
        result["name"] = right_column[idx].strip()
        idx += 1

    # --- Headline (until Summary / empty gap) ---
    while idx < n:
        line = right_column[idx].strip()
        lower = line.lower()

        if not line:
            idx += 1
            continue

        if lower == "summary":
            break

        # Skip location-like lines (simple heuristic)
        if len(line.split()) <= 2:
            idx += 1
            continue

        result["headline"].append(line)
        idx += 1

    # --- About (Summary only) ---
    if idx < n and right_column[idx].strip().lower() == "summary":
        idx += 1

        while idx < n:
            line = right_column[idx].strip()
            lower = line.lower()

            if lower in {"education", "experience"}:
                break

            if line:
                result["about"].append(line)

            idx += 1

    return result
