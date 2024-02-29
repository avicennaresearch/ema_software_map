from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.scraper.spiders.sitemap_generator import SitemapGeneratorSpider
from elasticsearch import Elasticsearch
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        es_url = settings.DATABASES["elastic"]["ELASTIC_HOST_URL"]
        es_port = settings.DATABASES["elastic"]["ELASTIC_PORT"]
        es_username = settings.DATABASES["elastic"]["ELASTIC_USERNAME"]
        es_password = settings.DATABASES["elastic"]["ELASTIC_PASSWORD"]
        es = Elasticsearch(
            es_url + ":" + es_port,
            http_auth=(es_username, es_password)
        )
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "product_name": {
                        "type": "keyword"
                    },
                    "resource_url": {
                        "type": "keyword"
                    },
                    "resource_name": {
                        # Cleaned res URL, ready for tokenization
                        "type": "keyword"
                    },
                    "content_type": {
                        # Either "entire_content" or "paragraph"
                        "type": "keyword"
                    },
                    "paragraph_index": {
                        # If "content_type" is "paragraph", which paragraph?
                        "type": "integer"
                    },
                    "content": {
                        "type": "text"
                    },
                    "embedding_1024": {
                        "type": "dense_vector",
                        "dims": 1024,
                        "index": True,
                        "similarity": "cosine",
                    },
                }
            }
        }

        index_name = "ema_comparison"
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        response = es.indices.create(index=index_name, body=index_settings, ignore=400)

        if 'acknowledged' in response:
            if response['acknowledged'] == True:
                print("Index creation successful.")
            elif 'error' in response:
                print("Index already exists.")
        else:
            import ipdb; ipdb.set_trace()
            print("Unknown error during index creation.")
