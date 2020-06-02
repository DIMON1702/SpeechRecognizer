import requests
from credentials.creds import CALENDLY_TOKEN


token = CALENDLY_TOKEN
headers = {'X-TOKEN': token}
url_events_type = 'https://calendly.com/api/v1/users/me/event_types'
url_test = 'https://calendly.com/api/v1/echo'
r = requests.get(url_test, headers=headers)
print(r.json())