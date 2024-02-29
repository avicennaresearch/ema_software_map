import hashlib
import html2text
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone

def split_to_paragraphs(text):
    lines = text.split('\n')
    paragraphs = []
    buffer = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            if buffer:
                paragraphs.append("\n".join(buffer))
                buffer = []
        else:
            buffer.append(line_stripped)

    if buffer:
        paragraphs.append("\n".join(buffer))

    # Process paragraphs according to the length and '#' rule
    processed_paragraphs = []
    for i, paragraph in enumerate(paragraphs):
        # Attach short paragraphs (< 80 chars) to the previous or next paragraph
        if len(paragraph) < 80:
            if paragraph.startswith("#"):
                # If it starts with '#' and is short, attach it to the next paragraph
                if i + 1 < len(paragraphs):
                    paragraphs[i + 1] = paragraph + "\n\n" + paragraphs[i + 1]
                elif processed_paragraphs:
                    # If there's no next paragraph but there is a previous one
                    processed_paragraphs[-1] += "\n\n" + paragraph
            else:
                # If it's short but doesn't start with '#', attach to the previous
                if processed_paragraphs:
                    processed_paragraphs[-1] += "\n\n" + paragraph
                elif i + 1 < len(paragraphs):
                    # If there's no previous paragraph but there is a next one
                    paragraphs[i + 1] = paragraph + "\n\n" + paragraphs[i + 1]
        else:
            # Add long paragraphs or paragraphs starting with '#' that are long enough
            processed_paragraphs.append(paragraph)

    return processed_paragraphs

def convert_html_to_md(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.ignore_images = True
    h.ignore_mailto_links = True
    markdown_content = h.handle(html_content)
    return markdown_content

def remove_newlines(s):
    s = s.replace('\n', ' ')
    s = s.replace('\\n', ' ')
    s = s.replace('\t', ' ')
    s = s.replace('\\t', ' ')
    s = s.replace('  ', ' ')
    s = s.replace('  ', ' ')
    return s

def now() -> datetime:
    """
    Returns timezone.now() with milliseconds precision as datetime.
    """
    now = timezone.now()
    return now.replace(microsecond=1000 * (now.microsecond // 1000))

def calculate_hash(content):
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()

def clean_html(html_content):
    # This function removes header, footer, and navigation menu from the HTML
    # and returns the body of the page.
    soup = BeautifulSoup(html_content, 'html.parser')
    tags = ['header', 'footer', 'nav']
    for tag in tags:
        elems = soup.find_all(tag)
        for elem in elems:
            elem.decompose()

    return soup.prettify()