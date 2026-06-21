def create_chunks(text: str, chunk_size: int = 700, overlap: int = 120):
    """
    Character-based chunking with overlap.
    This is simple and reliable for bilingual Bangla-English OCR text.
    """
    text = text.replace("\n\n", "\n").strip()
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
