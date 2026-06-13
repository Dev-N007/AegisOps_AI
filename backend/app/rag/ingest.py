import os
import glob
from sqlalchemy.orm import Session
from ..database.session import SessionLocal, engine, Base
from ..database.models import Runbook, HistoricalIncident
from ..services.vector_service import vector_service

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "knowledge"))

def parse_markdown(filepath: str) -> dict:
    """Parses markdown title and tags from headers/frontmatter"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    name = os.path.basename(filepath).replace(".md", "").replace("_", " ").title()
    # Find first header
    for line in content.split("\n"):
        if line.startswith("# "):
            name = line.replace("# ", "").strip()
            break

    # Extract tags (simple heuristic)
    tags = []
    if "database" in content.lower() or "postgres" in content.lower() or "mysql" in content.lower():
        tags.append("database")
    if "oom" in content.lower() or "memory" in content.lower():
        tags.append("memory")
    if "api" in content.lower() or "http" in content.lower() or "latency" in content.lower():
        tags.append("network")
    if "disk" in content.lower() or "space" in content.lower() or "storage" in content.lower():
        tags.append("storage")
    if "scale" in content.lower() or "cpu" in content.lower() or "traffic" in content.lower():
        tags.append("scaling")

    return {
        "name": name,
        "content": content,
        "tags": tags,
        "associated_issues": [name.lower()]
    }

def run_ingestion():
    # Make sure relational tables are created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing runbooks and historical incidents in DB
        db.query(Runbook).delete()
        db.query(HistoricalIncident).delete()
        db.commit()

        # Find markdown files in knowledge directory
        search_path = os.path.join(KNOWLEDGE_DIR, "**", "*.md")
        files = glob.glob(search_path, recursive=True)

        print(f"Found {len(files)} markdown knowledge files in {KNOWLEDGE_DIR}")

        documents = []
        metadatas = []
        ids = []

        for idx, file_path in enumerate(files):
            parsed = parse_markdown(file_path)
            rel_path = os.path.relpath(file_path, KNOWLEDGE_DIR)
            category = "runbook" if "runbook" in rel_path.lower() else "documentation"
            
            # Save to Relational DB
            if category == "runbook":
                runbook = Runbook(
                    name=parsed["name"],
                    content=parsed["content"],
                    associated_issues=parsed["associated_issues"],
                    tags=parsed["tags"]
                )
                db.add(runbook)
            else:
                hist = HistoricalIncident(
                    title=parsed["name"],
                    root_cause=parsed["name"] + " root cause analysis details",
                    resolution="Resolved by following standard troubleshooting procedures.",
                    logs={"logs": ["No logs captured in historical db"]},
                    metrics={"metrics": {}},
                    tags=parsed["tags"]
                )
                db.add(hist)

            # Prepare for Vector DB
            documents.append(parsed["content"])
            metadatas.append({
                "name": parsed["name"],
                "category": category,
                "tags": ",".join(parsed["tags"]),
                "source": rel_path
            })
            ids.append(f"doc_{idx}")

        db.commit()

        # Ingest to ChromaDB
        if documents:
            vector_service.add_documents(documents, metadatas, ids)
            print(f"Ingested {len(documents)} documents to ChromaDB.")
        else:
            print("No documents found to ingest. Make sure the 'knowledge' folder is seeded.")

    except Exception as e:
        db.rollback()
        print(f"Ingestion failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_ingestion()
