# LinkedIn PDF Profile Extractor (Layout-Aware)

This project extracts structured profile information from a **LinkedIn-exported PDF** by first fixing the **core problem**:  
**PDFs are layout documents, not text streams.**

Instead of fighting brittle heuristics, this system rebuilds the **reading order using x/y coordinates**, then performs **simple, deterministic section detection** on clean input.

---

## Demo Video:

https://youtu.be/vu9_eH5pEO4

## Why This Exists

Earlier attempts failed because:
- PDF text extraction **loses layout**
- Multi-column text gets interleaved
- Headers, summaries, and skills mix together
- Fixing this downstream leads to endless hacks

### Key Insight

> **If the input order is wrong, extraction logic will always be fragile.**

So we fixed the **representation first**, not the heuristics.

---

## High-Level Pipeline

PDF

└─► Layout Reconstruction (x/y coordinates)

└─► Ordered Lines + Column Break

└─► Section Detection (simple rules)

└─► Clean, structured data


---

## Core Design Decisions

### 1. Layout comes first
- Uses word-level `(x, y)` coordinates
- Rebuilds lines top → bottom, left → right
- Detects **column boundaries using x-distance**
- Inserts an explicit `<<COLUMN_BREAK>>` marker

### 2. Column break is intentional
- Left column = metadata (Contact, Top Skills, etc.)
- Right column = actual profile content
- Makes section detection **trivial and reliable**
- Marker is **kept**, not removed

### 3. Scope is intentionally small
This MVP extracts only:
- **Name**
- **Headline**
- **About (Summary only)**
- **Top Skills (pinned skills from left column)**

It explicitly does **not**:
- Guess skills from prose
- Parse experience yet
- Infer missing information

---

## Project Structure

```
extractor/
├── pdf_layout_reader.py # Layout-aware PDF → ordered lines
├── section_detector_v3.py # Column-aware section detection
main.py # Test harness / entry point
```

---

## Layout Reconstruction (`pdf_layout_reader.py`)

What it does:
- Extracts words with coordinates
- Groups words into lines using y-proximity
- Detects columns using large x-gaps
- Reads **left column fully, then right column**
- Inserts `<<COLUMN_BREAK>>` between columns

Why it matters:
- Eliminates interleaving bugs
- Preserves natural reading order
- Makes downstream logic boring (good)

---

## Section Detection (`section_detector_v3.py`)

Built **on top of clean ordered lines**.

Rules:
- Ignore everything before `<<COLUMN_BREAK>>` for main content
- Left column:
  - Only extracts `Top Skills`
  - Stops at next heading (Certifications, Education, etc.)
- Right column:
  - First non-empty line → Name
  - Next 1–2 meaningful lines → Headline
  - `Summary` → About section (only)
  - Stops at Education / Experience

No regex.  
No ML.  
No guessing.

---


## Example Output:

```
{
  "name": "Rachit Garg",
  "headline": [
    "Learning | Fullstack web development | AI Engineering",
    "Sharing My Journey through #100DaysOfCode"
  ],
  "about": [
    "I’m a Computer Science student building real systems...",
    "...",
  ],
  "top_skills": [
    "JavaScript Frameworks",
    "Full-Stack Development",
    "IBM Certified"
  ]
}
```

