import requests
url = 'http://localhost:8000/api/v1/auth/login'
data = {'username': 'testuser'}
try:
    r = requests.post(url, json=data)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
