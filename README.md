# PII Redaction Tool

## Project Overview
The PII Redaction Tool reads a `.docx` file, detects 9 categories of Personally Identifiable Information (PII), and replaces them with consistent, realistic fake alternatives, preserving the structure of the document as much as possible.

## Input & Output
- **Input:** The provided `input/Red Herring Prospectus.docx` which contains the text and tables to be redacted.
- **Output:** The redacted version is saved as `output/redacted_output.docx`. All detected PII is substituted with fake equivalents (e.g. realistic names, fake company names, valid IP format, etc.).

## PII Categories Handled
1. Full names (PERSON)
2. Email addresses (EMAIL_ADDRESS)
3. Phone numbers (PHONE_NUMBER)
4. Company names (ORGANIZATION)
5. Physical/mailing addresses (ADDRESS)
6. Social Security Numbers (US_SSN)
7. Credit card numbers (CREDIT_CARD)
8. Dates of birth (DATE_OF_BIRTH)
9. IP addresses (IP_ADDRESS)

## Detection Approach
The tool uses a hybrid approach:
- **NER (Named Entity Recognition):** We use `Microsoft Presidio` backed by `spaCy` (`en_core_web_sm`) to accurately identify `PERSON` and `ORGANIZATION`. 
- **Regex & Validation:** For structured PII, we rely on high-precision regexes, supplemented by Presidio's built-in validators. For example:
  - Phone Numbers: Custom regex for Indian & standard phone formats.
  - Credit Cards: Presidio handles Luhn validation to avoid flagging random 16-digit numbers.
  - IP Addresses: Presidio ensures the IP is a valid IPv4 address (e.g., `192.168.1.1` instead of `999.999.999.999`).
- **Context-Aware Rules:** Dates of birth (DOB) are detected using regex but heavily penalized in score unless surrounding context keywords (like "Born", "DOB", "Date of Birth") are found.

## Replacement Approach & Consistency
Replacements are generated using the `Faker` library (configured with the `en_IN` locale to match the Indian context of the document). 
- A `mappings` dictionary in `src/replacer.py` ensures that if a specific PII (e.g., `cs.connect@kshinternational.com`) appears multiple times, it is always mapped to the **same** fake value throughout the entire document.

## Evaluation
A manually annotated ground-truth sample (`evaluation/ground_truth.json`) was created from a stratified sample of the document. Synthetic examples were injected only for categories with zero natural occurrences (like SSN, IP, Credit Cards).

### Results Summary
- **Overall Precision:** 0.3774
- **Overall Recall:** 0.7692
- **Character-Level Accuracy:** 0.8805 (88%)
- *(See `evaluation/evaluation_report.md` for full breakdown per category and calculation methods)*

## Tradeoffs
- **Regex vs NER:** Regex is faster and more precise for structured data (emails, IPs), but NER is required for unstructured names and organizations.
- **Formatting Preservation:** `python-docx` doesn't natively support easy in-place text replacement if an entity spans multiple style "runs". As a tradeoff, if PII is detected, the paragraph's runs are cleared and the redacted text is written to the first run. This preserves the overarching paragraph/cell style but may lose mid-paragraph bolding/italics.

## False Positives & Negatives
- **False Positives:** The SpaCy model aggressively tags capitalized headings as `ORGANIZATION` (e.g., "SIZE", "OFFER", "DETAILS OF THE OFFER TO PUBLIC"). Similarly, fragmented addresses (e.g., "Taluka - Khed Pune") were occasionally flagged as `PERSON`.
- **False Negatives:** Complex, multi-line nested addresses or less common company names (e.g., "WATERLOO INDUSTRIAL PARK VI PRIVATE LIMITED") were occasionally missed if they lacked sufficient surrounding context or typical naming conventions.

## Limitations
- Performance heavily depends on the underlying `spaCy` model. Fine-tuning the model on financial prospectuses would drastically reduce false positives.
- The redactor clears internal paragraph runs when a replacement occurs, which slightly degrades intra-paragraph rich text formatting.

## Installation
1. Ensure Python 3.8+ is installed.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage
Run the redaction script from the project root:
```bash
python src/pii_redactor.py --input "input/Red Herring Prospectus.docx" --output "output/redacted_output.docx"
```

## Project Structure
- `src/pii_redactor.py` - CLI entry point and DOCX parser.
- `src/detectors.py` - Regex and NER detection logic.
- `src/replacer.py` - Consistent fake data generation.
- `src/evaluator.py` - Evaluates accuracy against ground truth.
- `tests/test_pii.py` - Unit tests for the detectors.
- `evaluation/` - Contains the evaluation report and ground truth dataset.
- `input/` - The original Red Herring Prospectus.
- `output/` - The generated redacted DOCX.
