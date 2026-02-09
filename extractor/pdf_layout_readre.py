import pdfplumber
from collections import defaultdict
from typing import List


def extract_ordered_lines(
    pdf_path: str,
    y_tolerance: float = 3.0,
    column_gap_threshold: float = 50.0
) -> List[str]:
    """
    Extracts text from PDF in correct reading order using x/y coordinates,
    handling multi-column layouts.

    Output:
    - Lines are ordered top → bottom
    - Left column fully first, then right column
    - Column breaks are explicitly marked
    """

    all_lines: List[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            words = page.extract_words(use_text_flow=False)

            if not words:
                continue

            # ---------- STEP 1: Detect columns ----------
            words_sorted_x = sorted(words, key=lambda w: w["x0"])

            columns = [[]]
            last_x = words_sorted_x[0]["x0"]

            for word in words_sorted_x:
                if word["x0"] - last_x > column_gap_threshold:
                    columns.append([])
                columns[-1].append(word)
                last_x = word["x0"]

            # ---------- STEP 2: Process each column ----------
            for col_index, column in enumerate(columns):
                # Explicit column break marker (for debugging)
                if col_index > 0:
                    all_lines.append("<<COLUMN_BREAK>>")

                rows = defaultdict(list)

                for word in column:
                    y_key = round(word["top"] / y_tolerance) * y_tolerance
                    rows[y_key].append(word)

                # Sort lines top → bottom
                for y in sorted(rows.keys()):
                    row_words = rows[y]

                    # Sort words left → right
                    row_words.sort(key=lambda w: w["x0"])

                    line = " ".join(w["text"] for w in row_words).strip()
                    if line:
                        all_lines.append(line)

    return all_lines


# ------------------------
# Debug / standalone run
# ------------------------
if __name__ == "__main__":
    lines = extract_ordered_lines("profile.pdf")

    for line in lines:
        print(line)
