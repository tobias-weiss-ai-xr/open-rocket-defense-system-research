#!/usr/bin/env python3
"""
Ingest research documents into Neo4j Knowledge Graph (chemie-lernen.org)
Uses base64 encoding to safely pass Cypher queries through SSH.

Credentials are read from environment variables:
  NEO4J_PASSWORD (required)
  NEO4J_USER (optional, default: neo4j)
  NEO4J_HOST (required)
  NEO4J_CONTAINER (optional, default: chemie-kg)
  NEO4J_DATABASE (optional, default: chemie)

Never hardcode credentials in this file - it is a public repository.
"""

import subprocess
import re
import json
import base64
import os
from pathlib import Path

# Configuration - from environment variables (never hardcode secrets in public repos)
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
NEO4J_HOST = os.environ.get("NEO4J_HOST", "")
NEO4J_CONTAINER = os.environ.get("NEO4J_CONTAINER", "chemie-kg")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "chemie")

if not NEO4J_PASSWORD:
    raise SystemExit(
        "Error: NEO4J_PASSWORD environment variable must be set.\n"
        "Example: NEO4J_PASSWORD='<password>' python3 scripts/ingest_to_knowledge_graph.py"
    )

if not NEO4J_HOST:
    raise SystemExit(
        "Error: NEO4J_HOST environment variable must be set "
        "(e.g. root@your-server). Do not hardcode hosts in this public repo."
    )

RESEARCH_DIR = Path(__file__).parent.parent / "research"
DATA_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"
ROOT_DIR = Path(__file__).parent.parent


def ssh_cypher(query: str) -> str:
    """Execute Cypher query via SSH using base64 encoding to avoid escaping issues."""
    # Encode query in base64
    query_bytes = query.encode('utf-8')
    encoded = base64.b64encode(query_bytes).decode('ascii')
    
    # Decode on remote side and pipe to cypher-shell
    cmd = f"echo '{encoded}' | base64 -d | ssh {NEO4J_HOST} 'docker exec -i {NEO4J_CONTAINER} cypher-shell -u {NEO4J_USER} -p \"{NEO4J_PASSWORD}\" -d {NEO4J_DATABASE}'"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing query: {result.stderr[:500] if result.stderr else 'Unknown error'}")
    return result.stdout


def chunk_markdown(markdown: str, max_chars: int = 1500, overlap: int = 200) -> list[dict]:
    """Split markdown by headings into chunks suitable for Neo4j Content nodes."""
    chunks = []
    lines = markdown.split('\n')
    current_chunk = []
    current_heading = "Introduction"
    current_size = 0

    for line in lines:
        heading_match = re.match(r'^(#{1,3})\s+(.+)', line)
        if heading_match and current_size > 300:
            # Save current chunk
            if current_chunk:
                chunks.append({
                    "heading": current_heading,
                    "content": '\n'.join(current_chunk).strip(),
                    "char_count": current_size
                })
            current_heading = heading_match.group(2)
            # Keep overlap: last few lines
            overlap_lines = [l for l in current_chunk if l.strip()][-3:]
            current_chunk = overlap_lines + [line]
            current_size = sum(len(l) for l in current_chunk)
        else:
            current_chunk.append(line)
            current_size += len(line) + 1

    if current_chunk:
        chunks.append({
            "heading": current_heading,
            "content": '\n'.join(current_chunk).strip(),
            "char_count": current_size
        })

    return chunks


def extract_metadata(filepath: str, markdown: str) -> dict:
    """Extract structured metadata from file path and content."""
    filename = Path(filepath).name
    title_match = re.search(r'^#\s+(.+)', markdown, re.MULTILINE)
    title = title_match.group(1) if title_match else filename.replace('.md', '').replace('-', ' ').title()
    
    # Determine topic based on file location
    rel_path = Path(filepath).relative_to(Path(__file__).parent.parent)
    if "docs/" in str(rel_path):
        topic = "military-defense"
        subtopic = "documentation"
    elif "data/" in str(rel_path):
        topic = "military-defense"
        subtopic = "data"
    else:
        topic = "military-defense"
        subtopic = "rocket-defense-systems"

    return {
        "source_file": filename,
        "source_path": str(filepath),
        "title": title,
        "topic": topic,
        "subtopic": subtopic,
    }


def create_document_node(metadata: dict, content_hash: str = "") -> str:
    """Create a Document node in Neo4j"""
    # Escape single quotes for Cypher
    title = metadata['title'].replace("'", "\\'")
    source_file = metadata['source_file'].replace("'", "\\'")
    source_path = metadata['source_path'].replace("'", "\\'")
    topic = metadata['topic'].replace("'", "\\'")
    subtopic = metadata['subtopic'].replace("'", "\\'")
    
    query = f"""
CREATE (d:Document {{
  title: '{title}',
  sourceFile: '{source_file}',
  sourcePath: '{source_path}',
  topic: '{topic}',
  subtopic: '{subtopic}',
  ingestionDate: datetime(),
  contentType: 'markdown',
  contentHash: '{content_hash}',
  wordCount: {len(metadata['title'].split())}
}})
RETURN d.sourceFile AS id
"""
    result = ssh_cypher(query)
    return result


def create_content_chunks(document_file: str, chunks: list[dict]) -> int:
    """Create Content nodes linked to a Document"""
    count = 0
    doc_file_escaped = document_file.replace("'", "\\'")
    for i, chunk in enumerate(chunks):
        heading = chunk['heading'].replace("'", "\\'")
        content = chunk['content'].replace("'", "\\'")
        query = f"""
MATCH (d:Document {{sourceFile: '{doc_file_escaped}'}})
CREATE (c:Content {{
  heading: '{heading}',
  content: '{content}',
  charCount: {chunk['char_count']},
  chunkIndex: {i},
  createdAt: datetime()
}})
CREATE (d)-[:HAS_CONTENT]->(c)
RETURN c
"""
        ssh_cypher(query)
        count += 1
    return count


def add_tags(document_file: str, tags: list[str]) -> None:
    """Add tags to a Document"""
    doc_file_escaped = document_file.replace("'", "\\'")
    tags_escaped = [tag.replace("'", "\\'") for tag in tags]
    tags_list = "', '".join(tags_escaped)
    query = f"""
MATCH (d:Document {{sourceFile: '{doc_file_escaped}'}})
FOREACH (tag IN ['{tags_list}'] |
  MERGE (t:Tag {{name: tag}})
  MERGE (d)-[:HAS_TAG]->(t)
)
RETURN d
"""
    ssh_cypher(query)


def delete_document(document_file: str) -> None:
    """Delete an existing Document and all connected Content nodes (used for re-ingest)."""
    doc_file_escaped = document_file.replace("'", "\\'")
    query = f"""
MATCH (d:Document {{sourceFile: '{doc_file_escaped}'}})
OPTIONAL MATCH (d)-[:HAS_CONTENT]->(c:Content)
DETACH DELETE d, c
"""
    ssh_cypher(query)


def file_content_hash(markdown: str) -> str:
    """Stable short hash to detect content changes for re-ingestion."""
    import hashlib
    return hashlib.sha256(markdown.encode('utf-8')).hexdigest()[:16]


def ingest_markdown_file(filepath: str) -> dict:
    """Ingest a single markdown file into Neo4j.

    Re-ingests if the file content changed since the last ingestion
    (tracked via contentHash on the Document node).
    """
    print(f"\nProcessing: {filepath}")

    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        markdown = f.read()

    # Extract metadata
    metadata = extract_metadata(filepath, markdown)
    print(f"  Title: {metadata['title']}")

    content_hash = file_content_hash(markdown)
    source_file_escaped = metadata['source_file'].replace("'", "\\'")

    # Check if document exists and whether content changed
    check_query = f"MATCH (d:Document {{sourceFile: '{source_file_escaped}'}}) " \
                  f"RETURN d.contentHash AS hash, d.title AS title"
    existing = ssh_cypher(check_query).strip()

    if existing:
        stored_hash = ""
        for line in existing.splitlines()[1:]:  # skip header
            if "," in line:
                stored_hash = line.split(",")[0].strip('" ')
                break
        if stored_hash == content_hash:
            print(f"  Unchanged (hash {content_hash[:8]}[...]), skipping")
            return {"status": "skipped", "file": metadata['source_file'], "unchanged": True}
        print(f"  Content CHANGED (was {stored_hash[:8]}[...], now {content_hash[:8]}[...]) -> re-ingesting")
        delete_document(metadata['source_file'])

    # Chunk content
    chunks = chunk_markdown(markdown)
    print(f"  Created {len(chunks)} content chunks")

    # Create Document node
    doc_result = create_document_node(metadata, content_hash)
    print(f"  Created Document node")

    # Create Content chunks
    content_count = create_content_chunks(metadata['source_file'], chunks)
    print(f"  Created {content_count} Content nodes")

    # Add tags
    tags = ["military-defense", "ukraine", "rocket-defense", "cost-analysis", "air-defense"]
    add_tags(metadata['source_file'], tags)
    print(f"  Added tags: {', '.join(tags)}")

    return {"status": "ingested", "file": metadata['source_file'], "chunks": len(chunks)}


def ingest_threat_profiles(filepath: str) -> dict:
    """Ingest threat profiles JSON into Neo4j"""
    print(f"\nProcessing threat profiles: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create Document node
    metadata = {
        "source_file": Path(filepath).name,
        "source_path": filepath,
        "title": "Russian Offensive Systems Threat Profiles",
        "topic": "military-defense",
        "subtopic": "threat-intelligence",
    }
    
    # Check if document already exists
    source_file_escaped = metadata['source_file'].replace("'", "\\'")
    check_query = f"MATCH (d:Document {{sourceFile: '{source_file_escaped}'}}) RETURN d"
    existing = ssh_cypher(check_query)
    if existing.strip():
        print(f"  Document already exists, skipping...")
        return {"status": "skipped", "file": metadata['source_file']}
    
    create_document_node(metadata)
    print(f"  Created Document node")
    
    # Create Entity nodes for each threat system
    count = 0
    doc_file_escaped = metadata['source_file'].replace("'", "\\'")
    for system_name, specs in data.get("russian_offensive_systems", {}).items():
        entity_name = system_name.replace("_", " ").title().replace("'", "\\'")
        specs_json = json.dumps(specs).replace("'", "\\'")
        
        query = f"""
MATCH (d:Document {{sourceFile: '{doc_file_escaped}'}})
CREATE (e:Entity {{
  name: '{entity_name}',
  type: 'weapon-system',
  specs: '{specs_json}',
  createdAt: datetime()
}})
CREATE (d)-[:MENTIONS]->(e)
RETURN e
"""
        ssh_cypher(query)
        count += 1
    
    # Add tags
    tags = ["military-defense", "threat-intelligence", "russia", "weapon-systems"]
    add_tags(metadata['source_file'], tags)
    print(f"  Created {count} Entity nodes for threat systems")
    print(f"  Added tags: {', '.join(tags)}")
    
    return {"status": "ingested", "file": metadata['source_file'], "entities": count}


def verify_ingestion() -> None:
    """Verify the ingestion was successful"""
    print("\n=== Verification ===")
    
    # Count documents
    query = "MATCH (d:Document) RETURN count(d) AS total"
    result = ssh_cypher(query)
    print(f"Total Documents: {result.strip()}")
    
    # Sample recent documents
    query = """
MATCH (d:Document) 
WHERE d.topic = 'military-defense'
RETURN d.sourceFile, d.title, d.subtopic 
ORDER BY d.ingestionDate DESC 
LIMIT 5
"""
    result = ssh_cypher(query)
    print("\nRecent military-defense documents:")
    print(result)
    
    # Count content chunks
    query = "MATCH (c:Content) RETURN count(c) AS total"
    result = ssh_cypher(query)
    print(f"Total Content nodes: {result.strip()}")
    
    # List new tags
    query = """MATCH (t:Tag) 
WHERE t.name STARTS WITH 'military' OR t.name STARTS WITH 'ukraine' OR t.name STARTS WITH 'rocket' OR t.name STARTS WITH 'russia'
RETURN t.name AS tag ORDER BY t.name"""
    result = ssh_cypher(query)
    print("\nMilitary-defense related tags:")
    print(result)


def main():
    """Main ingestion pipeline"""
    print("=== Neo4j Knowledge Graph Ingestion ===")
    print(f"Target: chemie-kg @ {NEO4J_HOST}")
    print(f"Database: {NEO4J_DATABASE}")
    
    results = []
    
    # Ingest markdown research files
    print("\n--- Ingesting Research Files ---")
    for md_file in RESEARCH_DIR.glob("*.md"):
        result = ingest_markdown_file(str(md_file))
        results.append(result)
    
    # Ingest documentation files
    print("\n--- Ingesting Documentation Files ---")
    for md_file in DOCS_DIR.glob("*.md"):
        result = ingest_markdown_file(str(md_file))
        results.append(result)
    
    # Ingest root README
    print("\n--- Ingesting Root README ---")
    readme_file = ROOT_DIR / "README.md"
    if readme_file.exists():
        result = ingest_markdown_file(str(readme_file))
        results.append(result)
    
    # Ingest JSON data files
    print("\n--- Ingesting Data Files ---")
    for json_file in DATA_DIR.glob("*.json"):
        if "threat" in json_file.name:
            result = ingest_threat_profiles(str(json_file))
            results.append(result)
    
    # Summary
    print("\n=== Ingestion Summary ===")
    ingested = [r for r in results if r.get("status") == "ingested"]
    skipped = [r for r in results if r.get("status") == "skipped"]
    print(f"Ingested: {len(ingested)} files")
    print(f"Skipped (already exists): {len(skipped)} files")
    
    # Verify
    verify_ingestion()
    
    print("\n=== Ingestion Complete ===")


if __name__ == "__main__":
    main()
