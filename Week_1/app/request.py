import requests

api_key = ""

response = requests.post(
"https://api.campusai.compute.dtu.dk/v1/chat/completions",
headers={
"Authorization": f"Bearer {api_key}",
"Content-Type": "application/json",
},
json={
"model": "cai",
"messages": [{"role": "user", "content": "Hello!"}],
},
)
print(response.json())