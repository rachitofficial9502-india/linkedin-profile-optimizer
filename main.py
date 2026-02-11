# main.py

from extractor.extractor import extract_profile
from analyzer.analyzer import analyze_profile


def main():
    """
    Entry point for LinkedIn Profile Optimizer (MVP).
    Flow:
    PDF -> Extractor -> Analyzer -> Print result
    """

    # -----------------------------
    # Input (example)
    # -----------------------------
    pdf_path = "profile.pdf"

    # -----------------------------
    # Extraction
    # -----------------------------
    extracted_data = extract_profile(pdf_path)

    print("\n--- EXTRACTED DATA ---")
    print(extracted_data)

    # -----------------------------
    # Analysis
    # -----------------------------
    analysis_result = analyze_profile(extracted_data)

    print("\n--- ANALYZER OUTPUT ---")
    print(analysis_result)


if __name__ == "__main__":
    main()


