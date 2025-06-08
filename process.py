import os, json, time
from scrape import batch_htmls, batch_wd
from model import safe_send_gemini_req, Job
from util import get_prompt, get_url_list
from dotenv import load_dotenv
from workday import parse_wd_reqs

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
SLEEP_BETWEEN_CALLS = int(os.getenv("SLEEP_BETWEEN_CALLS"))



def process(url_path: str, prompt_path: str) -> list[Job]:
    print('Running regular workflow...')
    
    urls = get_url_list(url_path)
    base_prompt = get_prompt(prompt_path)
    batches = batch_htmls(urls, base_prompt)

    jobs = []
    for i, batch in enumerate(batches):
        print(f'Batch {i+1}/{len(batches)}')
        try:
            batch_res = safe_send_gemini_req(batch, MODEL_NAME)
            jobs += batch_res
        except:
            print('Batch skipped.')
        time.sleep(SLEEP_BETWEEN_CALLS)

    return jobs



def process_wd(wd_config_path: str, prompt_path: str) -> list[Job]:
    print('Running Workday workflow...')
    with open(wd_config_path, "r", encoding="utf-8") as f:
        wd_config = json.load(f)

 
    base_prompt = get_prompt(prompt_path)
    wd_jobs = parse_wd_reqs(wd_config)
    batches = batch_wd(wd_jobs, base_prompt)

    jobs = []
    for i, batch in enumerate(batches):
        print(f'Batch {i+1}/{len(batches)}')
        try:
            batch_res = safe_send_gemini_req(batch, MODEL_NAME)
            jobs += batch_res
        except:
            print('Batch skipped.')
        time.sleep(SLEEP_BETWEEN_CALLS)

    return jobs