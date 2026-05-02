import requests
import random
import time
import requests_cache
import difflib
from datetime import datetime, UTC

CLIENT_ID = "qnanvz0eh3tpkl5o34ts4yhvhf20rb"
ACCESS_TOKEN = "0lhonnd6ixx016aojoldnixiiw3vv3"

URL = "https://api.igdb.com/v4/games"

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

requests_cache.install_cache('igdb_cache', expire_after=86400, allowable_methods=('GET', 'POST')) # allows for caching a post request

# Example genre IDs (IGDB genre IDs)
GENRES = {
    "Adventure": 31,
    "Shooter": 5,
    "Puzzle": 9,
    "RPG": 12,
    "Strategy": 15,
    "Platformer": 8,
    "Fighting": 4,
    "Survival": 33,
    "Horror": 32
}

# Column constraints (IGDB query snippets)
COLUMNS = {
    "Highly Rated (>85)": "rating > 85",
    "Recent (after 2020)": "first_release_date > 1577836800",
    "Popular (>100 ratings)": "rating_count > 100",
    "1990s (1990–1999)": "first_release_date >= 631152000 & first_release_date < 946684800",
    "2000s (2000–2009)": "first_release_date >= 946684800 & first_release_date < 1262304000", # had chatgpt help with the dates
    "2010s (2010–2019)": "first_release_date >= 1262304000 & first_release_date < 1577836800",
    "Indie": 'genres = (32)',
    "Music": 'genres = (7)',
    "Multiplayer": 'game_modes != null & game_modes = (2)',
    "Fantasy": '(themes = (17))',
    "Sci-Fi": "(themes = (18))"
}
# ran into trouble with inconsistent tagging of games in the database (horror being under both genre and theme,
# many horror games not counting since they are listed under the "horror" theme instead); led to helper function below
# for two worst cases of this

def build_genre_filter(genre_name, genre_id):
    # Special case for Horror
    if genre_name == "Horror":
        return f"(genres = ({genre_id}) | themes = (19))"
    if genre_name == "Survival":
        return f"(genres = ({genre_id}) | themes = (21))"

    return f"genres = ({genre_id})"

# --- PRECACHE SET OF VALID GAMES SO API ISN'T CALLED LIVE DURING GAMEPLAY ---
def precache_cells(rows, cols):
    cell_answers = {}

    for i, (genre_name, genre_id) in enumerate(rows):
        for j, (_, condition) in enumerate(cols):

            genre_filter = build_genre_filter(genre_name, genre_id)

            query = f"""
            fields name;
            where {genre_filter} & {condition};
            limit 100;
            """

            r = requests.post(URL, headers=HEADERS, data=query)

            if r.status_code != 200:
                cell_answers[(i, j)] = set()
                continue

            data = r.json()

            # Store lowercase names for easier matching
            cell_answers[(i, j)] = {
                game["id"]: {
                    "name": game["name"].lower(),
                    "year": format_date(game.get("first_release_date"))
                }
                for game in data
            }

    return cell_answers

# --- GENERATE VALID GRID ---
def generate_valid_grid():
    genre_items = list(GENRES.items())
    column_items = list(COLUMNS.items())

    while True:
        rows = random.sample(genre_items, 3)
        cols = random.sample(column_items, 3)

        # Fetch real data for this grid
        cell_answers = precache_cells(rows, cols)

        # Validate: every cell must have at least one valid game
        if all(cell_answers[(i, j)] for i in range(3) for j in range(3)):
            return rows, cols, cell_answers

        time.sleep(0.2) # ensures that we do not go over our free 4 API Calls a second from IGDB

# --- VALIDATE PLAYER GUESS ---
def is_valid_guess(game_name, i, j):
    guess = game_name.strip().lower()

    # 1. quick cache check (optional UX boost)
    if guess in cell_answers[(i, j)]:
        return True

    # 2. authoritative IGDB check
    genre_name, genre_id = rows[i]
    condition = cols[j][1]

    genre_filter = build_genre_filter(genre_name, genre_id)

    query = f'''
    search "{game_name}";
    fields name;
    where {genre_filter}
    & {condition};
    limit 1;
    '''

    r = requests.post(URL, headers=HEADERS, data=query)
    data = r.json()

    if not data:
        return False

    return any(game["name"].lower() == guess for game in data) # enforce exact match

# --- CHECK TO DETERMINE IF INCORRECT GUESS IS IN THE DATA BASE OR NOT (only needed when using exact answer) ---
def is_game_in_database(game_name):
    guess = game_name.strip().lower()

    query = f'''
    search "{game_name}";
    fields name;
    limit 10;
    '''

    r = requests.post(URL, headers=HEADERS, data=query)

    if r.status_code != 200:
        return False

    data = r.json()

    return any(guess == game["name"].lower() for game in data)

# --- QUERIES THE PLAYER TO WHAT GAME THEY ARE REFERRING TO FOR DISAMBIGUATION (like get_person_id function in pset 5!) ---
def format_date(timestamp): # helper function for displaying release date
    if not timestamp:
        return "Unknown"
    return datetime.fromtimestamp(timestamp, UTC).strftime("%Y")

def disambiguate_game_name(game_name):
    guess = game_name.strip().lower()

    # --- 1. SEARCH PRECACHE FIRST ---
    all_cached_games = set()
    for names in cell_answers.values():
        all_cached_games.update(names)

    local_matches = difflib.get_close_matches(guess, all_cached_games, n=10, cutoff=0.7)

    if local_matches:
        print("\nDid you mean one of these? (from cached games)\n")
        print(f"0. Use exactly \"{game_name}\"")

        for idx, name in enumerate(local_matches):
            print(f"{idx + 1}. {name.title()}")

        print(f"{len(local_matches) + 1}. Search more (API)")

        while True:
            choice = input("\nEnter your choice: ").strip()

            if not choice.isdigit():
                continue

            choice = int(choice)

            if choice == 0:
                # ONLY HERE we check database
                if is_game_in_database(guess):
                    return guess
                else:
                    return None

            if 1 <= choice <= len(local_matches):
                return local_matches[choice - 1]

            elif choice == len(local_matches) + 1:
                break

    # --- 2. API SEARCH ---
    query = f'''
    search "{game_name}";
    fields name, first_release_date;
    limit 10;
    '''

    r = requests.post(URL, headers=HEADERS, data=query)
    results = r.json() if r.status_code == 200 else []

    if not results:
        return None

    print("\nDid you mean one of these?\n")
    print(f"0. Use exactly \"{game_name}\"")

    for idx, game in enumerate(results):
        name = game.get("name", "Unknown")
        year = format_date(game.get("first_release_date"))
        print(f"{idx + 1}. {name} ({year})")

    print(f"{len(results) + 1}. Re-enter guess")

    while True:
        choice = input("\nEnter your choice: ").strip()

        if not choice.isdigit():
            continue

        choice = int(choice)

        if choice == 0:
            if is_game_in_database(guess):
                return guess
            else:
                return None

        if 1 <= choice <= len(results):
            return results[choice - 1]["name"].lower()

        elif choice == len(results) + 1:
            return None

# --- INIT GAME ---
rows, cols, cell_answers = generate_valid_grid()

row_tags = [r[0] for r in rows]
col_tags = [c[0] for c in cols]

# Track board state
board = [[None for _ in range(3)] for _ in range(3)]

# Track score/used games to prevent duplicates
score = 0
used_games = set()

# --- DISPLAY BOARD ---
def print_board():
    print(f"\nCurrent PTS: {score}/9")
    print("\nCurrent Board:")
    print(" " * 20 + " | ".join(col_tags))
    print("-" * 60)
    for i in range(3):
        row_display = []
        for j in range(3):
            cell = board[i][j] if board[i][j] else "EMPTY"
            row_display.append(cell[:15])
        print(f"{row_tags[i]:<18} | " + " | ".join(row_display))
    print()


# --- GAME LOOP ---
def play_game():
    global score
    print("Welcome to Video Game-doku!")
    print("Enter a game that matches BOTH the row and column tags.\n")
    #for key, val in cell_answers.items():
        #print(key, len(val))
    for i in range(3):
        for j in range(3):

            while True:
                print_board()
                print(f"Cell: Row = '{row_tags[i]}', Column = '{col_tags[j]}'")

                guess = input("Your guess: ").strip()

                # Try disambiguation
                resolved_name = disambiguate_game_name(guess)

                if not resolved_name:
                    print("❗ Not a valid game. Try again.")
                    continue

                guess = resolved_name.lower()

                # prevents duplicate games from being used
                if guess in used_games:
                    print("❗ You've already used that game! Try a different one.\n")

                elif is_valid_guess(guess, i, j):
                    board[i][j] = guess.title()
                    used_games.add(guess)
                    score += 1 # modifying a global variable in function, so must declare it at start of play_game
                    print("✅ Correct!\n")
                    break

                else:
                    board[i][j] = '❌'
                    print("❌ Game exists but does not match tags. Incorrect!\n")
                    break

    print_board()
    print(f"Game over! Final Score: {score}/9")


# --- RUN ---
if __name__ == "__main__":
    play_game()
