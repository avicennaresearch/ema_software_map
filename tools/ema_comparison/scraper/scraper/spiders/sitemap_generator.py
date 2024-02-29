import re
import scrapy
import traceback
from time import sleep
from comparison.models import Software
from comparison.models import Url
from concurrent.futures import ThreadPoolExecutor
from django.db.models import Q
from urllib.parse import urlparse
from scraper.scraper.spiders.ai import get_ai_summary
from scraper.scraper.spiders.utils import calculate_hash
from scraper.scraper.spiders.utils import convert_html_to_md
from scraper.scraper.spiders.utils import now
from scraper.scraper.spiders.utils import clean_html
from scraper.scraper.spiders.utils import remove_newlines
from scraper.scraper.spiders.elastic import erase_residuals_from_es
from scraper.scraper.spiders.elastic import insert_resource_content_in_elastic
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
# from scrapy.http import HtmlResponse

class SitemapGeneratorSpider(scrapy.Spider):
    name = "sitemap_generator"
    allowed_domains = []
    start_urls = []
    PRODUCT_NAME = None

    def __init__(self, *args, **kwargs):
        super(SitemapGeneratorSpider, self).__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=4)
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--window-size=1920x1080")

        # Initialize the WebDriver with the specified options
        print("Initializing webdriver")
        # self.driver = webdriver.Chrome(
        #     service=Service(ChromeDriverManager().install()),
        #     options=chrome_options
        # )
        print("Webdriver initialized")

    def start_requests(self):
        future = self.executor.submit(
            lambda: [x for x in Software.objects.filter(name='MetricWire')]
        )
        softwares = future.result()
        for software in softwares:
            print(f"####     Working on {software}")
            start_urls = [
                url.strip()
                for url in software.base_urls.split("\n")
                if url.strip()
            ]
            self.PRODUCT_NAME = software.name
            start_urls = ["https://metricwire.atlassian.net/wiki/spaces/mwknowledgebase/pages/1048617/Triggers https://metricwire.atlassian.net/wiki/spaces/mwknowledgebase/pages"]
            for url in start_urls:
                urls = [x.strip() for x in url.split(" ") if x.strip()]
                start_url = urls[0]
                if len(urls) > 1:
                    url_prefix_to_follow = urls[1]
                else:
                    url_prefix_to_follow = start_url
                self.allowed_domains = [urlparse(url).netloc]
                yield scrapy.Request(
                    start_url,
                    meta={
                        'base_url': url,
                        'url_prefix_to_follow': url_prefix_to_follow
                    }
                )

    def should_visit_site(self, url):
        if url.startswith("https://github.com"):
            if url.endswith("/_history"):
                return False
            if re.search(r'[a-z0-9]{40}$', url):
                return False
        return True

    def parse(self, response):
        if 'text' not in str(response.headers['Content-Type']):
            return

        # Using Selenium
        # self.driver.get(response.url)
        # sleep(2)
        # page_source_raw = self.driver.page_source
        # resource_url = self.driver.current_url
        # 
        # Using requests
        page_source_raw = response.text
        resource_url = response.url

        base_url = response.meta['base_url']
        url_prefix_to_follow = response.meta['url_prefix_to_follow']
        page_source_soup = BeautifulSoup(page_source_raw, 'html.parser')
        def _correct_link(link):
            if 'atlassian.net' in link and 'login.action?os_destination=/' in link:
                return link.replace('login.action?os_destination=/', '')
            return link
        links = [
            _correct_link(a['href'])
            for a in page_source_soup.find_all('a', href=True)
        ]

        for link in links:
            if not link.startswith('http'):
                link = response.urljoin(link)
            if link.startswith("mailto"):
                # print(f"Skipped {link} - Mailto")
                continue
            if not link.startswith(url_prefix_to_follow):
                # print(f"Skipped {link} - Does not start with {url_prefix_to_follow}")
                continue
            if not self.should_visit_site(link):
                # print(f"Skipped {link} - Should not visit.")
                continue
            yield scrapy.Request(
                link,
                callback=self.parse,
                meta={
                    'base_url': base_url,
                    'referer': resource_url,
                    'url_prefix_to_follow': url_prefix_to_follow
                }
            )

        # import ipdb
        # ipdb.set_trace()
        links_to_pause = [
            "/wiki/spaces/mwknowledgebase/pages/1048620",
            "/wiki/spaces/mwknowledgebase/pages/1048622/Creating+Triggers",
            "/wiki/spaces/mwknowledgebase/pages/1048628/Using+Once+Triggers",
            "/wiki/spaces/mwknowledgebase/pages/1048630/Using+Ongoing+Triggers",
            "/wiki/spaces/mwknowledgebase/pages/1048633/Using+Daily+Triggers",
            "/wiki/spaces/mwknowledgebase/pages/1048635/Using+Random+Triggers",
            "/wiki/spaces/mwknowledgebase/pages/1048637/Using+Geofence+Triggers",
            '/wiki/spaces/mwknowledgebase/pages/1048639/Using+the+Participant+Portal+Trigger',
        ]
        for ltp in links_to_pause:
            if ltp in resource_url:
                import ipdb
                ipdb.set_trace()
                break
        html_content = clean_html(page_source_raw)
        md_content = convert_html_to_md(html_content)
        md_content_hash = calculate_hash(md_content.encode('utf-8'))

        # Directly calling Django ORM lead to crash due to async nature of
        # scrapy. Running ORM call in a Thread instead.
        future = self.executor.submit(
            (
                lambda r_url, hash :
                [
                    x for x
                    in Url.objects.filter(Q(url=r_url) | Q(content_hash=hash))
                ]
            ),
            resource_url, md_content_hash
        )
        url_objs = future.result()

        if len(url_objs) > 1:
            raise Exception("Found multiple objects with similar hash and URL.")
        elif len(url_objs) == 1:
            url_obj = url_objs[0]
            # If anything with the same URL, skip.
            if url_obj.url == resource_url:
                print(f"Skipped {resource_url} - Already visited.")
            else:
                # If similar hash, add 
                print(f"Skipped {resource_url} - Similar Hash: ID {url_obj.id}")
                def _add_url_to_similar_urls(url_obj, new_url):
                    if not url_obj.similar_urls:
                        url_obj.similar_urls = ""
                    url_obj.similar_urls = new_url + "\n" + url_obj.similar_urls
                    url_obj.save()
                self.executor.submit(_add_url_to_similar_urls, url_obj, resource_url)
            return

        print(f"Working on {response.url} from {base_url}")
        resource_name = response.url.replace('https:', '').replace('/', ' ').replace('.', ' ').strip()
        try:
            erase_residuals_from_es(resource_url)
            insert_resource_content_in_elastic(
                resource_url, resource_name, self.PRODUCT_NAME, md_content
            )
            ai_summary = None # get_ai_summary(md_content)
            future = self.executor.submit(
                (
                    lambda s, u, n, t, a, h, l : 
                    Url.objects.create(
                        software=Software.objects.get(name=s),
                        url=u,
                        name=n,
                        last_updated=t,
                        is_monitored=False,
                        ai_summary=a,
                        human_summary=None,
                        content_hash=h,
                        content_length=l
                    )
                ),
                self.PRODUCT_NAME,
                resource_url,
                resource_name,
                now(),
                ai_summary,
                md_content_hash,
                len(remove_newlines(md_content))
            )
            _ = future.result()
        except Exception as e:
            print(f"Failed getting {resource_url}.\nError: {e}\nStackTrace:\n")
            print("Error message:", str(e))
            traceback.print_exc()
