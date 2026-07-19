import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits text into overlapping chunks of ~chunk_size characters.
    Overlap helps preserve context across chunk boundaries.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

def process_knowledge_base(kb_dir="knowledge_base"):
    """
    Reads every PDF in the knowledge_base folder, chunks it,
    and returns a list of {text, source} dicts ready for embedding.
    """
    all_chunks = []
    base_dir = os.path.join(os.path.dirname(__file__), "..", kb_dir)

    for filename in os.listdir(base_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(base_dir, filename)
            text = extract_text_from_pdf(pdf_path)
            chunks = chunk_text(text)

            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "source": filename
                })

            print(f"{filename}: {len(chunks)} chunks")

    return all_chunks


if __name__ == "__main__":
    chunks = process_knowledge_base()
    print(f"\nTotal chunks across all documents: {len(chunks)}")
    print(f"\nSample chunk:\n{chunks[0]}")