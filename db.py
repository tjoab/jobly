import os, sqlite3
from model import Job


# Create a SQLite DB
def create_db(db_path: str):
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()


# Given a DB, create a jobs table with URL as the identifier 
def create_jobs_table(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            location TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Given a list of jobs, insert them into the DB and only return 
# the subset of new jobs
def insert_jobs(jobs: list[Job], db_path: str) -> list[Job]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    new_jobs = []

    for job in jobs:
        # Use SQL integrity to filter 'new' jobs only
        try:
            cursor.execute('''
                INSERT INTO jobs (job_title, url, location)
                VALUES (?, ?, ?)
            ''', (job.job_title, job.url, job.location))
            new_jobs.append(job)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    return new_jobs 