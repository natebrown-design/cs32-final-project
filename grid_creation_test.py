import requests
import random
import time

CLIENT_ID = "qnanvz0eh3tpkl5o34ts4yhvhf20rb"
ACCESS_TOKEN = "0lhonnd6ixx016aojoldnixiiw3vv3"

URL = "https://api.igdb.com/v4/games"

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Example genre IDs (IGDB genre IDs)
GENRES = {
    "Adventure": 31,
    "Shooter": 5,
    "Puzzle": 9,
    "RPG": 12,
    "Strategy": 15,
    "Platformer": 8
}

# Column constraints (IGDB query snippets)
COLUMNS = {
    "Highly Rated (>85)": "rating > 85",
    "Recent (after 2020)": "first_release_date > 1577836800",
    "Popular (>100 ratings)": "rating_count > 100",
    "Classic (before 2010)": "first_release_date < 1262304000"
}

def has_games(genre_id, condition):
    query = f"""
    fields name;
    where genres = ({genre_id}) & {condition};
    limit 1;
    """

    response = requests.post(URL, headers=HEADERS, data=query)

    if response.status_code != 200:
        return False

    data = response.json()
    return len(data) > 0

def generate_valid_grid(max_attempts=50):
    genre_items = list(GENRES.items())
    column_items = list(COLUMNS.items())

    for attempt in range(max_attempts):
        rows = random.sample(genre_items, 3)
        cols = random.sample(column_items, 3)

        valid = True

        for r_name, r_id in rows:
            for c_name, c_cond in cols:
                if not has_games(r_id, c_cond):
                    valid = False
                    break
            if not valid:
                break

        if valid:
            return rows, cols

        time.sleep(0.2)  # avoid rate limits

    return None, None

def main()
    
