from pdf_layout_readre import extract_ordered_lines
from section_detector import detect_sections


def main():
    pdf_path = "../profile.pdf"

    # 1. Extract ordered lines using layout logic
    lines = extract_ordered_lines(pdf_path)

    # Sanity check: ensure column break exists
    if "<<COLUMN_BREAK>>" not in lines:
        print("⚠️ Warning: Column break not detected — layout may be incorrect")
    else:
        print("✅ Column break detected")

    # Optional: print reconstructed text
    print("\n===== RECONSTRUCTED TEXT =====\n")
    for line in lines:
        print(line)

    # 2. Detect sections (v3)
    sections = detect_sections(lines)

    # 3. Pretty print detected sections
    print("\n===== DETECTED SECTIONS =====\n")

    print("NAME:")
    print(sections["name"])

    print("\nHEADLINE:")
    for h in sections["headline"]:
        print(h)

    print("\nABOUT:")
    for a in sections["about"]:
        print(a)

    print("\nTOP SKILLS:")
    for s in sections["top_skills"]:
        print(s)


if __name__ == "__main__":
    main()
