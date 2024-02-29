from scraper.scraper.spiders.utils import split_to_paragraphs
from scraper.scraper.spiders.utils import remove_newlines
from scraper.scraper.spiders.ai import get_embedding
from elasticsearch import Elasticsearch
from django.conf import settings

ELASTIC_CONNECTION = None
ELASTIC_INDEX_NAME = "ema_comparison"

def get_es_connection():
    global ELASTIC_CONNECTION
    if not ELASTIC_CONNECTION:
        es_url = settings.DATABASES["elastic"]["ELASTIC_HOST_URL"]
        es_port = settings.DATABASES["elastic"]["ELASTIC_PORT"]
        es_username = settings.DATABASES["elastic"]["ELASTIC_USERNAME"]
        es_password = settings.DATABASES["elastic"]["ELASTIC_PASSWORD"]
        ELASTIC_CONNECTION = Elasticsearch(
            es_url + ":" + es_port,
            http_auth=(es_username, es_password)
        )
    return ELASTIC_CONNECTION

def insert_doc_into_es(doc):
    global ELASTIC_INDEX_NAME
    es = get_es_connection()
    response = es.index(index=ELASTIC_INDEX_NAME, document=doc)
    return response

def erase_residuals_from_es(resource_url):
    global ELASTIC_INDEX_NAME
    query = {
        "query": {
            "match": { "resource_url": resource_url }
        }
    }

    es = get_es_connection()
    response = es.delete_by_query(
        index=ELASTIC_INDEX_NAME, body=query, refresh=True
    )

    return response

def insert_resource_content_in_elastic(
    r_url, r_name, product_name, markdown_content
):
    if len(remove_newlines(markdown_content)) > 4000:
        paragraphs = split_to_paragraphs(markdown_content)
        for i, paragraph in enumerate(paragraphs):
            clean_paragraph = remove_newlines(paragraph)
            # A paragraph must be less than allowed tokens per embedding call.
            # embedding = get_embedding(clean_paragraph)[0]["embeddings"]
            insert_doc_into_es({
                "product_name": product_name,
                "resource_url": r_url,
                "resource_name": r_name,
                "content_type": "paragraph",
                "paragraph_index": i,
                "content": clean_paragraph,
                # "embedding_1024": embedding,
            })

    clean_content = remove_newlines(markdown_content)
    # embedding_parts = get_embedding(clean_content)
    counter = 0
    # for part in embedding_parts:
    insert_doc_into_es({
        "product_name": product_name,
        "resource_url": r_url,
        "resource_name": r_name,
        "content_type": "entire_content",
        "paragraph_index": counter,
        "content": clean_content
        # "content": part["part"],
        # "embedding_1024": part["embeddings"],
    })
        # counter += 1
