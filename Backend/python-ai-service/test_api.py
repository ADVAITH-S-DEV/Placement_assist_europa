import requests
import json
import sys

# The specific PDF the user uploaded recently
pdf_path = r"c:\Users\AMARJEET KUMAR\Desktop\Placement_Assist\Backend\uploads\resume-1773402835613-178786213.pdf"

url = "http://localhost:8000/parse-resume"

with open(pdf_path, 'rb') as f:
    files = {'file': ('resume.pdf', f, 'application/pdf')}
    response = requests.post(url, files=files)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
else:
    print(response.text)
