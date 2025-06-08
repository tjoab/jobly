import os, requests, time
from model import Job 
from datetime import date
from dotenv import load_dotenv


# Load env variables
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")


# Insert jobs into a Notion database
def insert_jobs_into_notion(jobs: list[Job]) -> None:
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    for i, job in enumerate(jobs):
        payload = {
            "parent": { "type": "database_id", "database_id": NOTION_DB_ID },
            "properties": {
                "Job Title": {
                    "type": "title",
                    "title": [{ "type": "text", "text": { "content": job.job_title } }]
                },
                "URL": {
                    "type": "url",
                    "url": job.url
                },
                "Location": {
                    "rich_text": [
                        {
                            "text": {
                                "content": job.location
                            }
                        }
                    ]
                },
                "Date Added": {
                    "type": "date",
                    "date": { "start": date.today().isoformat() }
                }
            }
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f'Error adding job {job.job_title}. Error: {response.text}')    
        
        # Short cooldown to not overload Notion api
        time.sleep(0.3)
