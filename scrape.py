import os, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from model import count_tokens
from tqdm.auto import tqdm


# Load env variables
load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
MAX_TOKENS_PER_BATCH = int(os.getenv("MAX_TOKENS_PER_BATCH"))



def fetch_html_content(url: str) -> str:
    '''Given a URL, grab its HTML text content.'''
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.body

    for tag in body(['script', 'style', 'noscript']):
        tag.decompose()
    html_as_str = body.decode_contents()

    return html_as_str



def batch_htmls(urls: list[str], base_prompt: str) -> list[str]:
    '''Given a list of URLs, grab their HTML and batch them together with a prompt.'''
    batches = []
    curr_batch = ""
    curr_tokens = count_tokens(base_prompt, MODEL_NAME)
    
    n = len(urls)
    progress_bar = tqdm(range(n), leave=False)

    for url in urls:
        # Get HTML content and count how many tokens there are
        html = fetch_html_content(url)
        num_tokens = count_tokens(html, MODEL_NAME)

        # Append current batch and start a new once we reach max token limit
        if curr_tokens + num_tokens > MAX_TOKENS_PER_BATCH:
            batches.append(base_prompt + "\n\n" + curr_batch)
            curr_batch = html
            curr_tokens = num_tokens
        else:
            if curr_batch:
                curr_batch += "\n\n" + html
            else:
                curr_batch = html
            curr_tokens += num_tokens
        progress_bar.update(1)

    # Append anything left over that was under the max token limit
    if curr_batch:
        batches.append(base_prompt + "\n\n" + curr_batch)
    progress_bar.close()

    return batches



def batch_wd(jobs: list[str], base_prompt: str) -> list[str]:
    '''Given a list Workday jobs as raw text, batch them together with a prompt.'''
    batches = []
    curr_batch = ""
    curr_tokens = count_tokens(base_prompt, MODEL_NAME)

    for job_subset in jobs:
        num_tokens = count_tokens(job_subset, MODEL_NAME)

        if curr_tokens + num_tokens > MAX_TOKENS_PER_BATCH:
            batches.append(base_prompt + "\n\n" + curr_batch)
            curr_batch = job_subset
            curr_tokens = num_tokens
        else:
            if curr_batch:
                curr_batch += "\n\n" + job_subset
            else:
                curr_batch = job_subset
            curr_tokens += num_tokens

    if curr_batch:
        batches.append(base_prompt + "\n\n" + curr_batch)

    return batches