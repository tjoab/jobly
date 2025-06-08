import os, yaml
from dotenv import load_dotenv
from db import insert_jobs
from notion import insert_jobs_into_notion
from util import save_to_csv, remove_senior_jobs
from process import process, process_wd


# Load env variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
SAVE_DIR = os.getenv("SAVE_DIR")
CONFIG_PATH = os.getenv("CONFIG_PATH")


def main(config_file: str):

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    jobs = []

    if config['regular']['enabled']:
        url_path = config['regular']['url_path']
        prompt_path = config['regular']['prompt_path']
        jobs += process(url_path, prompt_path)

    if config['workday']['enabled']:
        wd_config_path = config['workday']['config_path']
        prompt_path = config['workday']['prompt_path']
        jobs += process_wd(wd_config_path, prompt_path)

    if config['remove_senior']:
        print('Removing and senior roles ...')
        jobs = remove_senior_jobs(jobs)

    print('Filtering and inserting new jobs into SQLite ...')
    new_jobs = insert_jobs(jobs, DB_PATH)

    if new_jobs and config['save']['notion']:
        print('Inserting new jobs to into Notion ...')
        insert_jobs_into_notion(new_jobs)

    if new_jobs and config['save']['local']:
        print('Saving new jobs to CSV ...')
        save_to_csv(new_jobs, SAVE_DIR)

    else:
        print('No new jobs ...')


if __name__ == '__main__':
    main(CONFIG_PATH)

