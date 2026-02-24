from datetime import datetime
from typing import List
from fastapi import Depends, APIRouter, HTTPException, Header
from app.auth import get_current_user
from app.opensearch import client
import os

router = APIRouter()
INGEST_TOKEN = os.getenv("INGEST_TOKEN")

@router.post("/ingest")
def ingest(log: dict, user=Depends(get_current_user)):

    if user["role"] != "admin":
        log["tenant"] = user["tenant"]

    raw_log = log.copy()

    log["@timestamp"] = log.get("@timestamp") or datetime.utcnow().isoformat()
    log["raw"] = raw_log

    client.index(index="logs-demo", body=log)

    return {"status": "indexed"}


@router.post("/ingest/syslog")
def ingest_syslog(logs: List[dict]):

    for log in logs:
        message = log.get("log")

        parsed = {
            "@timestamp": datetime.utcnow().isoformat(),
            "tenant": "demoA",
            "source": "firewall",
            "event_type": "syslog_event",
            "raw": message
        }

        client.index(index="logs-demoa", body=parsed)

    return {"status": "syslog indexed"}