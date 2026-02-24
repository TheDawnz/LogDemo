@app.get("/search")
def search(q: str = "*", user=Depends(get_current_user)):

    must = []

    if user["role"] != "admin":
        must.append({"term": {"tenant": user["tenant"]}})

    query_body = {
        "query": {
            "bool": {
                "must": must
            }
        },
        "aggs": {
            "top_ip": {
                "terms": {"field": "src_ip"}
            },
            "timeline": {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "minute"
                }
            }
        }
    }

    return client.search(index="logs-demo", body=query_body)