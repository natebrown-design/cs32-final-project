import requests
import requests_cache

url = "https://id.twitch.tv/oauth2/token"

params = {
    "client_id": "qnanvz0eh3tpkl5o34ts4yhvhf20rb",
    "client_secret": "qstn44yw1eqt65vmmto0fmrs17wbbo",
    "grant_type": "client_credentials"
}

response = requests.post(url, params=params)

data = response.json()
print(data)

# Enable cache (stored in SQLite file)
requests_cache.install_cache('igdb_cache', expire_after=86400)

url = "https://api.igdb.com/v4/games"
headers = {
    "Client-ID": "qnanvz0eh3tpkl5o34ts4yhvhf20rb",
    "Authorization": f"Bearer {data['access_token']}"
}

query = "fields name, rating; limit 10;"

response = requests.post(url, headers=headers, data=query)

data = response.json()
print(data)
