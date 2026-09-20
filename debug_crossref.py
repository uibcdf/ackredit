import json
import urllib.request

doi = "10.1038/s41592-021-01121-x"
url = f"https://api.crossref.org/works/{doi}"
headers = {"User-Agent": "Ackredit/0.1.0"}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())["message"]
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
