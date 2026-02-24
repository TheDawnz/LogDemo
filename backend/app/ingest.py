from fastapi import APIRouter, Depends, Header, HTTPException
from datetime import datetime
from typing import List
import os

from app.auth import get_current_user
from app.opensearch import client

router = APIRouter()

INGEST_TOKEN = os.getenv("INGEST_TOKEN", "supersecretingestkey")


@router.post("/ingest")
def ingest(log: dict, user=Depends(get_current_user)):

    if user["role"] != "admin":
        log["tenant"] = user["tenant"]

    tenant = log["tenant"]

    raw_log = log.copy()
    log["@timestamp"] = log.get("@timestamp") or datetime.utcnow().isoformat()
    log["raw"] = raw_log

    index_name = f"logs-{tenant}-{datetime.utcnow().strftime('%Y.%m.%d')}"

    client.index(index=index_name, body=log)

    return {"status": "indexed"}


@router.post("/ingest/syslog")
def ingest_syslog(
    logs: List[dict],
    x_ingest_token: str = Header(None)
):

    if x_ingest_token != INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized ingest")

    for log in logs:
        message = log.get("log")

        parsed = {
            "@timestamp": datetime.utcnow().isoformat(),
            "tenant": "demoA",
            "source": "firewall",
            "event_type": "syslog_event",
            "raw": message
        }

        index_name = f"logs-demoA-{datetime.utcnow().strftime('%Y.%m.%d')}"

        client.index(index=index_name, body=parsed)

    return {"status": "syslog indexed"}