import requests

url = "https://id.twitch.tv/oauth2/token"

params = {
    "client_id": "qnanvz0eh3tpkl5o34ts4yhvhf20rb",
    "client_secret": "qstn44yw1eqt65vmmto0fmrs17wbbo",
    "grant_type": "client_credentials"
}

response = requests.post(url, params=params)

data = response.json()
print(data)
