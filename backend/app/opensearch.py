from opensearchpy import OpenSearch
import os

client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "opensearch"), "port": 9200}]
)