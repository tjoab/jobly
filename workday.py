import requests
from tqdm.auto import tqdm


def get_wd_api_url(url: str) -> str:
    '''Given the base Workday url, derive and return the correspodning public API url'''
    url_split = url.split('/')
    url_split.insert(3, 'wday')
    url_split.insert(4, 'cxs')
    url_split.insert(5, url_split[2].split('.')[0])
    url_split.append('jobs')

    return '/'.join(url_split)



def send_wd_req(base_url: str, facet: str, facet_value: str, search_query: str) -> list[dict[str, str]]:
    '''Fetch jobs from Workday API, with given search params'''
  
    url = get_wd_api_url(base_url)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
  # Returns 20 most recent jobs matching the search query
    payload = {
        "appliedFacets": {
            facet: facet_value
        },
        "limit": 20,
        "offset": 0,
        "searchText": search_query,
        "sort": "date"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        output = []
        for job in data.get("jobPostings", []):
            if "title" in job and "externalPath" in job:
                output.append( { 'title':job["title"], 'url': base_url+job["externalPath"] } )
        return output
    else:
        print(f'API response error: {response.text}')



def parse_wd_reqs(config: list[dict[str, str | list[str]]]) -> list[str]:
    '''Group together jobs for batching from the Workday api responses.'''

    n = len(config)
    progress_bar = tqdm(range(n), leave=False)

    wd_jobs = []
    for i in range(n):
        ds_jobs = send_wd_req(config[i]['url'], config[i]['facet'], config[i]['value'], "data science")
        ml_jobs = send_wd_req(config[i]['url'], config[i]['facet'], config[i]['value'], "machine learning")
        analytics_jobs = send_wd_req(config[i]['url'], config[i]['facet'], config[i]['value'], "analytics")

        wd_jobs.append(str(ds_jobs + ml_jobs + analytics_jobs))
        progress_bar.update(1)
    
    progress_bar.close()
    return wd_jobs