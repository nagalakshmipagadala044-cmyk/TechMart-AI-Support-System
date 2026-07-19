from fpdf import FPDF
import os
import textwrap

files = [
    "faq",
    "refund_policy",
    "shipping_policy",
    "warranty",
    "pricing",
    "products",
    "installation_guide",
    "user_manual",
]

def sanitize(text):
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u20b9": "Rs.",  # rupee symbol
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Safety net: strip any remaining character the PDF font can't render
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    return text

def txt_to_pdf(txt_path, pdf_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    with open(txt_path, "r", encoding="utf-8") as f:
        text = sanitize(f.read())

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        if line == "":
            pdf.ln(4)
            continue

        is_header = line.isupper() and len(line) < 60
        pdf.set_font("Helvetica", "B" if is_header else "", size=12 if is_header else 11)

        # Pre-wrap with textwrap instead of relying on fpdf's internal wrapping
        wrapped_lines = textwrap.wrap(line, width=90) or [""]
        for sub_line in wrapped_lines:
            pdf.set_x(pdf.l_margin)
            pdf.cell(0, 6, sub_line, ln=1)

        if is_header:
            pdf.ln(1)

    pdf.output(pdf_path)
    print(f"Created: {pdf_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)

    for name in files:
        txt_path = os.path.join(base_dir, f"{name}.txt")
        pdf_path = os.path.join(base_dir, f"{name}.pdf")

        if os.path.exists(txt_path):
            txt_to_pdf(txt_path, pdf_path)
        else:
            print(f"Skipped (not found): {txt_path}")

    print("\nAll conversions complete.")