"""
Content Ingestion Module

Reads Docusaurus markdown files, splits them into chunks, and prepares them for embedding.
Each chunk is ~500 tokens to fit within context windows while preserving semantic meaning.
"""

import os
import re
from typing import List, Dict, Tuple
from pathlib import Path


class TextChunk:
    """Represents a chunk of text with metadata."""

    def __init__(self, text: str, source_file: str, section_title: str, chunk_index: int):
        self.text = text
        self.source_file = source_file
        self.section_title = section_title
        self.chunk_index = chunk_index
        self.word_count = len(text.split())

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "text": self.text,
            "source_file": self.source_file,
            "section_title": self.section_title,
            "chunk_index": self.chunk_index,
            "word_count": self.word_count
        }


def extract_title_from_markdown(content: str) -> str:
    """
    Extract the H1 title from markdown content.

    Args:
        content: Markdown file content

    Returns:
        The H1 title, or 'Untitled' if not found
    """
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def split_by_headers(content: str) -> List[Tuple[str, str]]:
    """
    Split markdown content by headers (H2 and H3).

    Args:
        content: Markdown file content

    Returns:
        List of (section_title, section_text) tuples
    """
    sections = []

    # Split by H2 headers (##)
    h2_pattern = r'^##\s+(.+)$'
    h2_splits = re.split(h2_pattern, content, flags=re.MULTILINE)

    # First element is content before first H2
    if h2_splits[0].strip():
        sections.append(("Introduction", h2_splits[0].strip()))

    # Process H2 sections (pairs of title and content)
    for i in range(1, len(h2_splits), 2):
        if i + 1 < len(h2_splits):
            title = h2_splits[i].strip()
            text = h2_splits[i + 1].strip()
            sections.append((title, text))

    return sections


def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    """
    Split text into chunks of approximately max_tokens.
    Uses a simple word-based approximation (1 token ≈ 0.75 words).

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk (default 500)

    Returns:
        List of text chunks
    """
    # Approximate: 1 token ≈ 0.75 words, so 500 tokens ≈ 375 words
    max_words = int(max_tokens * 0.75)

    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk_words = words[i:i + max_words]
        chunks.append(" ".join(chunk_words))

    return chunks


def process_markdown_file(file_path: Path, relative_path: str) -> List[TextChunk]:
    """
    Process a single markdown file into text chunks.

    Args:
        file_path: Absolute path to markdown file
        relative_path: Relative path from docs/ (e.g., "module-1-ros2/week1-intro.md")

    Returns:
        List of TextChunk objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract document title
    doc_title = extract_title_from_markdown(content)

    # Split by sections
    sections = split_by_headers(content)

    all_chunks = []
    chunk_index = 0

    for section_title, section_text in sections:
        # Skip code blocks for now (they can be added later if needed)
        # Remove triple backtick blocks
        section_text = re.sub(r'```[\s\S]*?```', '[code block]', section_text)

        # Chunk the section text
        text_chunks = chunk_text(section_text, max_tokens=500)

        for text_chunk in text_chunks:
            if text_chunk.strip():  # Skip empty chunks
                chunk = TextChunk(
                    text=text_chunk,
                    source_file=relative_path,
                    section_title=f"{doc_title} - {section_title}",
                    chunk_index=chunk_index
                )
                all_chunks.append(chunk)
                chunk_index += 1

    return all_chunks


def read_all_markdown_files(docs_directory: Path) -> List[TextChunk]:
    """
    Recursively read all markdown files from Docusaurus docs directory.

    Args:
        docs_directory: Path to docusaurus/docs/

    Returns:
        List of all TextChunk objects from all files
    """
    all_chunks = []

    # Find all .md files recursively
    md_files = list(docs_directory.glob("**/*.md"))

    print(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        # Get relative path from docs/
        relative_path = md_file.relative_to(docs_directory).as_posix()

        print(f"Processing: {relative_path}")

        try:
            chunks = process_markdown_file(md_file, relative_path)
            all_chunks.extend(chunks)
            print(f"  -> Created {len(chunks)} chunks")

        except Exception as e:
            print(f"  ERROR processing {relative_path}: {e}")

    print(f"\nTotal chunks created: {len(all_chunks)}")
    return all_chunks


# Example usage
if __name__ == "__main__":
    # Test with actual docs directory
    docs_path = Path(__file__).parent.parent.parent.parent / "docusaurus" / "docs"

    if docs_path.exists():
        chunks = read_all_markdown_files(docs_path)

        # Show sample
        if chunks:
            print("\nSample chunk:")
            sample = chunks[0]
            print(f"Source: {sample.source_file}")
            print(f"Section: {sample.section_title}")
            print(f"Text preview: {sample.text[:200]}...")
            print(f"Word count: {sample.word_count}")
    else:
        print(f"Docs directory not found: {docs_path}")
