from fastapi import FastAPI
from opensearchpy import OpenSearch
import os

app = FastAPI()

client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "opensearch"), "port": 9200}]
)

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