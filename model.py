import os, re, random, time
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from google.genai.errors import ServerError, ClientError


# Load env variables
load_dotenv()
API_KEY = os.getenv("API_KEY")


# Gemini auth
client = genai.Client(api_key=API_KEY)


# Data structure to be returned by Gemini (response schema)
class Job(BaseModel):
  job_title: str
  url: str
  location: str


def send_gemini_req(content: str, model: str) -> list[Job]:
    '''Send a request to Gemini and parse its response.'''
    response = client.models.generate_content(model=model, contents=content,
                                              config={'response_mime_type': 'application/json',
                                                    'response_schema': list[Job]})
    found_jobs = response.parsed
    return found_jobs


def safe_send_gemini_req(content: str, model: str, max_attempt: int = 8) -> list[Job]:
    '''Retry sending function to wrap around Gemini request, with exponential backoff.'''
    for attempt in range(max_attempt):
        try:
            return send_gemini_req(content, model)
        
        except (ServerError, ClientError) as error_message:
            is_downtime_error = any(error in str(error_message) for error in ["UNAVAILABLE", "CANCELLED", "TOO_MANY_REQUESTS"])
            
            if is_downtime_error and attempt < max_attempt - 1:
                cooldown = 2 ** attempt + random.uniform(0, 1)
                print(f"Server downtime error. Retrying in {cooldown:.2f}s")
                time.sleep(cooldown)
            else:
                raise


# Count how many tokens are in a outgoing request to ensure you stay within API limits
def count_tokens(content: str, model: str) -> int:
    '''Returns how many tokens are in the given text content'''
    response = client.models.count_tokens(model=model, contents=content)
    match = re.search(r"total_tokens=(\d+)", str(response))
    num_tokens = int(match.group(1))

    return num_tokens