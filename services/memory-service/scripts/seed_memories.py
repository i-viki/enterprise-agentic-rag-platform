import asyncio
import asyncpg
import httpx
import json

DATABASE_URL = "postgresql://rag_admin:rag_secure_password_2026@localhost:5432/enterprise_rag"
OLLAMA_EMBED_URL = "http://localhost:11434/v1/embeddings"
EMBED_MODEL = "nomic-embed-text:v1.5"

DOCUMENTS = [
    {
        "kind": "procedural",
        "content": "Corporate Travel Policy Section 4.1: Domestic flights are reimbursed up to the economy class limit of $500 per round-trip flight. Any higher fare or business class booking requires prior written approval from the Department Vice President. Hotel lodging is reimbursed up to $250 per night in Tier-1 cities and $180 per night in Tier-2 cities.",
        "source_reference": "Corporate Travel Policy Section 4.1",
        "required_clearance_level": 1,
        "confidence": 0.98,
        "tenant_id": "tenant-enterprise-prod",
        "user_id": "admin",
        "department_id": "HR_FINANCE"
    },
    {
        "kind": "procedural",
        "content": "InfoSec SOP 12: Lost or stolen corporate laptops, tablets, or mobile devices must be reported to the Security Operations Center (SOC) helpdesk within 1 hour of discovery. An automated remote wipe command will be initiated immediately via MDM to protect enterprise data. The employee must file a local police report within 24 hours.",
        "source_reference": "InfoSec SOP 12",
        "required_clearance_level": 1,
        "confidence": 0.99,
        "tenant_id": "tenant-enterprise-prod",
        "user_id": "infosec",
        "department_id": "CYBERSECURITY"
    },
    {
        "kind": "semantic",
        "content": "Architecture Governance Guideline 8: All East-West microservice communication within the enterprise Kubernetes cluster must be encrypted via mTLS using SPIFFE/SPIRE x509 certificates alongside signed JWT bearer tokens. Ingress traffic must pass through the API gateway perimeter with rate-limiting and format-preserving tokenization.",
        "source_reference": "Architecture Governance Guideline 8",
        "required_clearance_level": 2,
        "confidence": 0.95,
        "tenant_id": "tenant-enterprise-prod",
        "user_id": "architect",
        "department_id": "ENGINEERING"
    },
    {
        "kind": "semantic",
        "content": "Compliance Policy FIN-901: All financial transaction ledgers, customer audit logs, and cryptographic hash verification trails must be preserved for exactly 7 years in immutable Write-Once-Read-Many (WORM) storage. Deletion or modification of audit ledger records is strictly prohibited under federal regulations.",
        "source_reference": "Compliance Policy FIN-901",
        "required_clearance_level": 3,
        "confidence": 0.97,
        "tenant_id": "tenant-enterprise-prod",
        "user_id": "compliance_officer",
        "department_id": "LEGAL_COMPLIANCE"
    },
    {
        "kind": "episodic",
        "content": "Employee Handbook Section 6: Full-time employees with at least 6 months of continuous service are entitled to 16 weeks of fully paid parental leave following the birth, adoption, or foster placement of a child. Parental leave may be taken continuously or in two-week increments within the first 12 months.",
        "source_reference": "Employee Handbook Section 6",
        "required_clearance_level": 1,
        "confidence": 0.95,
        "tenant_id": "tenant-enterprise-prod",
        "user_id": "hr_lead",
        "department_id": "PEOPLE_OPS"
    }
]

async def get_embedding(client: httpx.AsyncClient, text: str):
    try:
        resp = await client.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "input": text},
            timeout=10.0
        )
        if resp.status_code == 200:
            return resp.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Embedding failed via Ollama: {e}, using zero vector fallback")
    return [0.0] * 768

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connected to PostgreSQL enterprise_rag")

    # Ensure pgvector type is registered
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    async with httpx.AsyncClient() as http_client:
        for doc in DOCUMENTS:
            print(f"Embedding chunk: {doc['source_reference']}...")
            emb = await get_embedding(http_client, doc["content"])
            emb_str = f"[{','.join(str(x) for x in emb)}]"

            await conn.execute(
                """
                INSERT INTO memories (
                    tenant_id, user_id, department_id, required_clearance_level,
                    allowed_roles, kind, content, embedding, source_type,
                    source_reference, confidence, relevance, retention, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8::vector, $9, $10, $11, $12, $13, $14::jsonb
                );
                """,
                doc["tenant_id"],
                doc["user_id"],
                doc["department_id"],
                doc["required_clearance_level"],
                ["ALL"],
                doc["kind"],
                doc["content"],
                emb_str,
                "document",
                doc["source_reference"],
                doc["confidence"],
                1.0,
                "long_term",
                json.dumps({"seeded": True, "source": "official_sop"})
            )
            print(f"  -> Successfully indexed: {doc['source_reference']}")

    count = await conn.fetchval("SELECT count(*) FROM memories;")
    print(f"\nTotal memories in vector database now: {count}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())

