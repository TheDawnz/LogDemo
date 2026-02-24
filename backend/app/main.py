from fastapi import FastAPI
from app.auth import router as auth_router
from app.ingest import router as ingest_router
from app.search import router as search_router
from app.opensearch import client
from app.database import SessionLocal, engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(search_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/os-health")
def os_health():
    return client.info()

@app.on_event("startup")
def create_index():
    if not client.indices.exists(index="logs-*"):
        client.indices.create(
            index="logs-demo",
            body={
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "tenant": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "event_type": {"type": "keyword"},
                        "severity": {"type": "integer"},
                        "src_ip": {"type": "ip"},
                        "user": {"type": "keyword"},
                        "raw": {"type": "object"}
                    }
                }
            }
        )