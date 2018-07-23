import requests
import os

home_url = os.environ['APP_URL']
r = requests.get(home_url)
