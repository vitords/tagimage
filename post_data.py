import requests

api_url = 'http://127.0.0.1:5000/search'
# max_videos can't be larger than 50 as YouTube won't accept it
payload = {'topic': '/m/068hy', 'max_videos': 50, 'region_code': 'US', 'key': 'YOUTUBE API KEY HERE'}

response = requests.post(api_url, data=payload)
print(response.text)
