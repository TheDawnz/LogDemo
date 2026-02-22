from fastapi import Body
from datetime import datetime

@app.post("/ingest")
def ingest(log: dict = Body(...)):
    log["@timestamp"] = log.get("@timestamp", datetime.utcnow().isoformat())
    log["raw"] = log.copy()

    client.index(index="logs-demo", body=log)

    return {"status": "indexed"}