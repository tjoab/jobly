import os, re, csv
from datetime import date
from model import Job


# Given a text file of URLs, extract them in a list 
def get_url_list(path: str) -> list[str]:
    urls = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            urls.append(line.strip())
    return urls


# Give a text file with a prompt, extract the prompt
def get_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt


# Given a job list, save the jobs to a CSV file
def save_to_csv(jobs: list[Job], parent_dir: str) -> None:
    filename = f"{parent_dir}/jobs_{date.today()}.csv"
    file_exists = os.path.exists(filename)
    
    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_STRINGS)
        
        if not file_exists:
            writer.writerow(["Job Title", "URL", "Location"])
        for job in jobs:
            writer.writerow([job.job_title, job.url, job.location])



# Given a job title, flags if it is a senior position or not
def is_senior_job(job_title: str) -> bool:
    pattern = r"\b(senior|sr\.?|manager|staff|principal|principle|lead|director|avp|vp|president|dir|leader)\b"
    return re.search(pattern, job_title, re.IGNORECASE) is not None


# Given a job list, filter out senior and mangerial roles
def remove_senior_jobs(jobs: list[Job]) -> list[Job]:
    filtered_jobs = []
    filtered_count = 0

    for job in jobs:
        if is_senior_job(job.job_title):
            filtered_count += 1
        else:
            filtered_jobs.append(job)
    print(f'Filtered out {filtered_count} senior roles.')

    return filtered_jobs