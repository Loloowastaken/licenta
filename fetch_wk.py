import os, json, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dotenv import load_dotenv
load_dotenv()
HEADERS = {
    "Authorization": f"Bearer {os.getenv('WANIKANI_TOKEN')}",
    "Wanikani-Revision": "20170710"
}
BASE = "https://api.wanikani.com/v2"

def fetch_all(endpoint):
    url = f"{BASE}/{endpoint}"
    results = []
    while url:
        try:
            request = Request(url, headers=HEADERS)
            with urlopen(request) as response:
                payload = json.load(response)
        except HTTPError as error:
            if error.code == 429: # prea multe cereri
                time.sleep(10)
                continue
            raise
        results.extend(payload["data"])
        url = payload["pages"]["next_url"]
    return results

def save(name, data):
    Path("data").mkdir(exist_ok=True)
    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == "__main__":
    subjects = fetch_all("subjects")
    assignments = fetch_all("assignments")
    save("subjects", subjects)
    save("assignments", assignments)
    print(len(subjects),len(assignments))