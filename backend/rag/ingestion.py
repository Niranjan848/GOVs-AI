"""
GOVs-AI PDF Ingestion Pipeline
Extracts text from PDFs, chunks it, generates embeddings, and adds to FAISS index.
"""

import os
import logging
from typing import List, Dict

from config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extract text from a PDF file using PyMuPDF.
    Returns a list of dicts with 'text' and 'page' keys.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not installed. Using mock extraction.")
        return [{"text": f"Mock content from {os.path.basename(pdf_path)}", "page": 1}]

    pages = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages.append({"text": text, "page": page_num + 1})
        doc.close()
        logger.info(f"Extracted {len(pages)} pages from {pdf_path}")
    except Exception as e:
        logger.error(f"Error extracting PDF {pdf_path}: {e}")

    return pages


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[str]:
    """
    Split text into overlapping chunks using recursive character splitting.
    Respects sentence boundaries where possible.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if len(text) <= chunk_size:
        return [text]

    # Split on paragraph breaks first, then sentences
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]
    chunks = []

    def _split_recursive(text: str, sep_idx: int = 0) -> List[str]:
        if len(text) <= chunk_size:
            return [text]

        if sep_idx >= len(separators):
            # Hard split at chunk_size
            result = []
            for i in range(0, len(text), chunk_size - chunk_overlap):
                result.append(text[i:i + chunk_size])
            return result

        sep = separators[sep_idx]
        parts = text.split(sep)

        current_chunk = ""
        result = []

        for part in parts:
            candidate = current_chunk + sep + part if current_chunk else part
            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    result.append(current_chunk.strip())
                if len(part) > chunk_size:
                    result.extend(_split_recursive(part, sep_idx + 1))
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk.strip():
            result.append(current_chunk.strip())

        return result

    chunks = _split_recursive(text)

    # Add overlap between consecutive chunks
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_end = chunks[i - 1][-chunk_overlap:]
            overlapped.append(prev_end + " " + chunks[i])
        chunks = overlapped

    return [c for c in chunks if len(c.strip()) > 20]  # Filter tiny chunks


def ingest_pdf(pdf_path: str, source_name: str = None) -> int:
    """
    Full ingestion pipeline: extract → chunk → embed → index.
    Returns number of chunks added to the index.
    """
    from rag.embeddings import embed_documents
    from rag.retriever import add_documents

    source_name = source_name or os.path.basename(pdf_path)
    logger.info(f"Ingesting PDF: {source_name}")

    # Step 1: Extract text
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        logger.warning(f"No text extracted from {source_name}")
        return 0

    # Step 2: Chunk each page
    all_chunks = []
    all_metadata = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "content": chunk,
                "source": source_name,
                "page": page_data["page"],
            })

    if not all_chunks:
        logger.warning(f"No chunks generated from {source_name}")
        return 0

    logger.info(f"Generated {len(all_chunks)} chunks from {source_name}")

    # Step 3: Generate embeddings
    embeddings = embed_documents(all_chunks)

    # Step 4: Add to FAISS index
    count = add_documents(embeddings, all_metadata)

    logger.info(f"Ingested {count} chunks from {source_name}")
    return count


def ingest_directory(directory: str) -> int:
    """Ingest all PDF files from a directory."""
    total = 0
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return 0

    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            total += ingest_pdf(filepath, filename)

    logger.info(f"Total chunks ingested from directory: {total}")
    return total


def ingest_scheme_data(schemes: list) -> int:
    """
    Ingest structured scheme data (from schemes.json) into the vector store.
    This provides baseline retrieval even without PDF uploads.
    """
    from rag.embeddings import embed_documents
    from rag.retriever import add_documents

    chunks = []
    metadata = []

    for scheme in schemes:
        # Create a rich text representation of each scheme
        text_parts = [
            f"Scheme: {scheme['name']}",
            f"Category: {scheme.get('category', '')}",
            f"Description: {scheme.get('description', '')}",
            f"Benefits: {scheme.get('benefits', '')}",
        ]

        if scheme.get("eligibility"):
            elig = scheme["eligibility"]
            if isinstance(elig, dict):
                for key, val in elig.items():
                    text_parts.append(f"Eligibility - {key}: {val}")
            elif isinstance(elig, str):
                text_parts.append(f"Eligibility: {elig}")

        if scheme.get("documents_required"):
            docs = scheme["documents_required"]
            if isinstance(docs, list):
                text_parts.append(f"Documents Required: {', '.join(docs)}")

        full_text = "\n".join(text_parts)

        # Chunk if necessary, but usually scheme descriptions are short enough
        scheme_chunks = chunk_text(full_text, chunk_size=600)

        for chunk in scheme_chunks:
            chunks.append(chunk)
            metadata.append({
                "content": chunk,
                "source": f"scheme_{scheme.get('short_name', scheme['name'])}",
                "page": 0,
                "scheme_id": scheme.get("id"),
                "scheme_name": scheme["name"],
            })

    if not chunks:
        return 0

    embeddings = embed_documents(chunks)
    count = add_documents(embeddings, metadata)
    logger.info(f"Ingested {count} scheme data chunks into vector store.")
    return count
