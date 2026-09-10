import requests
import json

url = "http://localhost:8000/api/chat"
payload = {"question": "What are the Gold Loan interest rates and NCD prospectus details?"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print("HTTP Status:", response.status_code)
print(json.dumps(response.json(), indent=2))
