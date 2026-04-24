import requests_cache
import requests

# Enable cache (stored in SQLite file)
requests_cache.install_cache('igdb_cache', expire_after=86400)

url = "https://api.igdb.com/v4/games"
headers = {
    "Client-ID": "qnanvz0eh3tpkl5o34ts4yhvhf20rb",
    "Authorization": f"Bearer 0lhonnd6ixx016aojoldnixiiw3vv3"
}

query = "fields name, rating; limit 10;"

response = requests.post(url, headers=headers, data=query)

data = response.json()
print(data)
print(response.from_cache)
