import os
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "opensearch"), "port": 9200}]
)