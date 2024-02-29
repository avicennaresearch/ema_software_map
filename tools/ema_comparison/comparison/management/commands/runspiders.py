from django.core.management.base import BaseCommand
import os
import re
import scrapy
import traceback
from time import sleep
from comparison.models import Software
from comparison.models import Url
from concurrent.futures import ThreadPoolExecutor
from django.db.models import Q
from urllib.parse import urlparse
from comparison.ai import get_ai_summary
from comparison.utils import calculate_hash
from comparison.utils import convert_html_to_md
from comparison.utils import now
from comparison.utils import clean_html
from comparison.utils import remove_newlines
from comparison.elastic import erase_residuals_from_es
from comparison.elastic import insert_resource_content_in_elastic
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from collections import deque
import requests
from urllib.parse import urljoin

class Command(BaseCommand):
    help = 'Run the Scrapy spider'

    allowed_domains = []
    start_urls = []
    PRODUCT_NAME = None

    def should_visit_site(self, url):
        if url.startswith("https://github.com"):
            if url.endswith("/_history"):
                return False
            if re.search(r'[a-z0-9]{40}$', url):
                return False
        return True

    def _correct_link(self, link):
        if 'atlassian.net' in link and 'login.action?os_destination=/' in link:
            return link.replace('login.action?os_destination=/', '')
        return link

    def start_crawling(self, software, start_url, url_prefix_to_follow):
        queue = deque([start_url])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        # Populated processed_urls
        processed_urls = []
        urls = Url.objects.filter(software_id=software.id)
        for url in urls:
            processed_urls.append(url.url)
            if url.similar_urls:
                similar_urls = [
                    x.strip()
                    for x in url.similar_urls.split("\n")
                    if x.strip()
                ]
                if similar_urls:
                    processed_urls.extend(similar_urls)

        processed_urls = list(set(processed_urls))

        exclude_urls = []
        if software.exclude_urls:
            exclude_urls = [
                x.strip()
                for x in software.exclude_urls.split("\n")
                if x.strip()
            ]

        while queue:
            new_links = 0
            current_url = queue.popleft()
            processed_urls.append(current_url)
            response = requests.get(current_url, headers=headers)
            resource_url = response.url
            # Cover the redirect cases
            if resource_url not in processed_urls:
                processed_urls.append(resource_url)

            # Check if URL is excluded
            is_url_excluded = False
            for exclude_url in exclude_urls:
                if exclude_url in response.url:
                    is_url_excluded = True
                    break
            if is_url_excluded:
                continue

            if 'text' not in str(response.headers['Content-Type']):
                continue

            page_source_raw = response.text
            page_source_soup = BeautifulSoup(page_source_raw, 'html.parser')
            links = [
                self._correct_link(a['href'])
                for a in page_source_soup.find_all('a', href=True)
            ]

            for link in links:
                if not link.startswith('http'):
                    link = urljoin(resource_url, link)
                if link.startswith("mailto"):
                    # print(f"Skipped {link} - Mailto")
                    continue
                if not link.startswith(url_prefix_to_follow):
                    # print(f"Skipped {link} - Does not start with {url_prefix_to_follow}")
                    continue
                if not self.should_visit_site(link):
                    # print(f"Skipped {link} - Should not visit.")
                    continue
                if link not in queue and link not in processed_urls:
                    queue.append(link)
                    new_links += 1

            print(
                f"Processing: {resource_url} - Added {new_links} links. "
                f"Already visited: {len(processed_urls)} "
                f"Current queue size: {len(queue)}"
            )
            html_content = clean_html(page_source_raw)
            md_content = convert_html_to_md(html_content)
            md_content_hash = calculate_hash(md_content.encode('utf-8'))

            url_objs = Url.objects.filter(
                Q(url=resource_url) | Q(content_hash=md_content_hash)
            )

            if len(url_objs) > 1:
                import ipdb
                ipdb.set_trace()
                print("ERROR")
                raise Exception("Found multiple objects with similar hash and URL.")
            elif len(url_objs) == 1:
                url_obj = url_objs[0]
                # If anything with the same URL, skip.
                if url_obj.url == resource_url:
                    print(f"Skipped {resource_url} - Already visited.")
                else:
                    # If similar hash, add 
                    print(f"Skipped {resource_url} - Similar Hash: ID {url_obj.id}")
                    if not url_obj.similar_urls:
                        url_obj.similar_urls = ""
                    url_obj.similar_urls = resource_url + "\n" + url_obj.similar_urls
                    url_obj.save()
                continue

            resource_name = response.url.replace('https:', '').replace('/', ' ').replace('.', ' ').strip()
            try:
                erase_residuals_from_es(resource_url)
                insert_resource_content_in_elastic(
                    resource_url, resource_name, software.name, md_content
                )
                ai_summary = None # get_ai_summary(md_content)
                Url.objects.create(
                    software=Software.objects.get(name=software.name),
                    url=resource_url,
                    name=resource_name,
                    last_updated=now(),
                    is_monitored=False,
                    ai_summary=ai_summary,
                    human_summary=None,
                    content_hash=md_content_hash,
                    content_length=len(remove_newlines(md_content))
                )
            except Exception as e:
                print(f"Failed getting {resource_url}.\nError: {e}\nStackTrace:\n")
                print("Error message:", str(e))
                traceback.print_exc()

    def start_processing(self):
        softwares = Software.objects.filter(is_monitored=True)
        for software in softwares:
            print(f"####     Working on {software}")
            start_urls = [
                url.strip()
                for url in software.base_urls.split("\n")
                if url.strip()
            ]
            for url in start_urls:
                urls = [x.strip() for x in url.split(" ") if x.strip()]
                start_url = urls[0]
                if len(urls) > 1:
                    url_prefix_to_follow = urls[1]
                else:
                    url_prefix_to_follow = start_url
                self.allowed_domains = [urlparse(url).netloc]
                self.start_crawling(software, start_url, url_prefix_to_follow)

    def handle(self, *args, **options):
        self.start_processing()
