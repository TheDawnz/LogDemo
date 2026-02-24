from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.opensearch import client

router = APIRouter()


@router.get("/search")
def search(q: str, user=Depends(get_current_user)):

    if user["role"] == "admin":
        index_name = "logs-*"
    else:
        index_name = f"logs-{user['tenant']}-*"

    query = {
        "query": {
            "query_string": {
                "query": q
            }
        }
    }

    result = client.search(index=index_name, body=query)

    return result