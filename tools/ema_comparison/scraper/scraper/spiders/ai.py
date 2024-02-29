import tiktoken
import os
import openai
from openai import OpenAI
from scraper.scraper.spiders.utils import remove_newlines

CHATGPT_CLIENT = None
MODEL_MAX_TKN_COUNT_EMBEDDING = {
    "text-embedding-3-large": 8000,
}
MODEL_MAX_TKN_COUNT_COMPLETION = {
    "gpt-3.5-turbo-1106": 16285,
    "gpt-4-1106-preview": 16285, #127000
}

def num_tokens_from_string(string):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(string))

def get_chatgpt_client():
    global CHATGPT_CLIENT
    if not CHATGPT_CLIENT:
        api_key = os.getenv('OPENAI_API_KEY', 'INVALID')
        openai.api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key
        CHATGPT_CLIENT = OpenAI()
    return CHATGPT_CLIENT

def get_embedding(text):
    global MODEL_MAX_TKN_COUNT_EMBEDDING
    client = get_chatgpt_client()

    # Break the text into chunks each no more than max allowed token
    # for embedding
    EMBEDDING_MODEL = 'text-embedding-3-large'
    parts = []
    buffer = None
    finished = False
    while not finished:
        current_part_tokens = num_tokens_from_string(text)
        while current_part_tokens > MODEL_MAX_TKN_COUNT_EMBEDDING[
            EMBEDDING_MODEL
        ]:
            try:
                last_paragraph_start_loc = text.rindex("\n\n")
            except:
                import ipdb
                ipdb.set_trace()
            buffer = text[last_paragraph_start_loc:]
            text = text[:last_paragraph_start_loc]
            current_part_tokens = num_tokens_from_string(text)
        parts.append({ "part": text, "embeddings": None })
        if not buffer:
            finished = True
        else:
            text = buffer
            buffer = None

    for part in parts:
        resp = client.embeddings.create(
            input=part["part"],
            model='text-embedding-3-large',
            dimensions=1024,
        )
        part["embeddings"] = resp.data[0].embedding
    return parts

def get_ai_summary(markdown_content):
    msgs = [
        {
            "role": "system",
            "content": (
                "You are a researcher who is evaluating different software "
                "options to conduct a health research study using "
                "ecological momentary assessment softwares."
            )
        },
        {
            "role": "user",
            "content": (
                "The following content is retrieved from the documentation "
                "of one of the software packages. Please summarize it into "
                "a bulletpoint list. Also include a few-line summary of "
                "what this page talks about.\n\n"
                f"{remove_newlines(markdown_content)}"
            )
        }
    ]
    client = get_chatgpt_client()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=msgs
    )
    result = response.choices[0].message.content
    return result
