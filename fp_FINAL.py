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

requests_cache.install_cache('igdb_cache', expire_after=86400, allowable_methods=('GET', 'POST'))

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

COLUMNS = {
    "Highly Rated (>85)": "rating > 85",
    "Recent (after 2020)": "first_release_date > 1577836800",
    "Popular (>100 ratings)": "rating_count > 100",
    "1990s (1990–1999)": "first_release_date >= 631152000 & first_release_date < 946684800",
    "2000s (2000–2009)": "first_release_date >= 946684800 & first_release_date < 1262304000",
    "2010s (2010–2019)": "first_release_date >= 1262304000 & first_release_date < 1577836800",
    "Indie": 'genres = (32)',
    "Music": 'genres = (7)',
    "Multiplayer": 'game_modes != null & game_modes = (2)',
    "Fantasy": '(themes = (17))',
    "Sci-Fi": "(themes = (18))"
}

# --- HELPERS ---

def format_date(timestamp):
    if not timestamp:
        return "Unknown"
    return datetime.fromtimestamp(timestamp, UTC).strftime("%Y")

def build_genre_filter(genre_name, genre_id):
    if genre_name == "Horror":
        return f"(genres = ({genre_id}) | themes = (19))"
    if genre_name == "Survival":
        return f"(genres = ({genre_id}) | themes = (21))"
    return f"genres = ({genre_id})"


# --- PRECACHE ---

def precache_cells(rows, cols):
    cell_answers = {}

    for i, (genre_name, genre_id) in enumerate(rows):
        for j, (_, condition) in enumerate(cols):

            genre_filter = build_genre_filter(genre_name, genre_id)

            query = f"""
            fields id, name, first_release_date;
            where {genre_filter} & {condition};
            limit 100;
            """

            r = requests.post(URL, headers=HEADERS, data=query)

            if r.status_code != 200:
                cell_answers[(i, j)] = {}
                continue

            data = r.json()

            cell_answers[(i, j)] = {
                game["id"]: {
                    "name": game["name"].lower(),
                    "year": format_date(game.get("first_release_date"))
                }
                for game in data
            }

    return cell_answers


# --- GRID GENERATION ---

def generate_valid_grid():
    genre_items = list(GENRES.items())
    column_items = list(COLUMNS.items())

    while True:
        rows = random.sample(genre_items, 3)
        cols = random.sample(column_items, 3)

        cell_answers = precache_cells(rows, cols)

        if all(cell_answers[(i, j)] for i in range(3) for j in range(3)):
            return rows, cols, cell_answers

        time.sleep(0.2)


# --- VALIDATION (ID-BASED) ---

def is_valid_guess(game_id, game_name, i, j):
    # Fast path: already in precache by ID
    if game_id and game_id in cell_answers[(i, j)]:
        return True

    genre_name, genre_id = rows[i]
    _, condition = cols[j]
    genre_filter = build_genre_filter(genre_name, genre_id)

    if game_id:
        where_clause = f"id = {game_id} & {genre_filter} & {condition}"
    else:
        safe_name = game_name.replace('"', '\\"')
        where_clause = f"name ~ \"{safe_name}\" & {genre_filter} & {condition}"

    query = f"""
    fields id, name, first_release_date;
    where {where_clause};
    limit 1;
    """

    r = requests.post(URL, headers=HEADERS, data=query)
    if r.status_code != 200:
        return False

    data = r.json()
    if data:
        game = data[0]
        cell_answers[(i, j)][game["id"]] = {
            "name": game["name"].lower(),
            "year": format_date(game.get("first_release_date"))
        }
        return True

    return False


# --- DISAMBIGUATION ---

def disambiguate_game_name(game_name):
    guess = game_name.strip().lower()

    # --- Build cached lookup ---
    all_cached_games = {}
    for cell in cell_answers.values():
        for gid, data in cell.items():
            all_cached_games[gid] = data["name"]

    # --- Fuzzy match ---
    local_matches = difflib.get_close_matches(
        guess,
        list(all_cached_games.values()),
        n=10,
        cutoff=0.7
    )

    if local_matches:
        print("\nDid you mean one of these?\n")
        print(f"0. Use exactly \"{game_name}\"")

        matched_ids = [
            gid for gid, name in all_cached_games.items()
            if name in local_matches
        ]

        for idx, gid in enumerate(matched_ids):
            print(f"{idx + 1}. {all_cached_games[gid].title()}")

        print(f"{len(matched_ids) + 1}. Search more (API)")

        while True:
            choice = input("\nEnter your choice: ").strip()

            if not choice.isdigit():
                continue

            choice = int(choice)

            if choice == 0:
                return {"id": None, "name": game_name}  # was just: break

            if 1 <= choice <= len(matched_ids):
                gid = matched_ids[choice - 1]
                return {"id": gid, "name": all_cached_games[gid]}

            elif choice == len(matched_ids) + 1:
                break

    # --- API SEARCH ---
    query = f'''
    search "{game_name}";
    fields id, name, first_release_date;
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
            return {"id": None, "name": game_name}

        if 1 <= choice <= len(results):
            return {
                "id": results[choice - 1]["id"],
                "name": results[choice - 1]["name"].lower()
            }
        elif choice == len(results) + 1:
            new_guess = input("Re-enter your guess: ").strip()
            return disambiguate_game_name(new_guess)

# --- INIT ---

rows, cols, cell_answers = generate_valid_grid()

row_tags = [r[0] for r in rows]
col_tags = [c[0] for c in cols]

board = [[None for _ in range(3)] for _ in range(3)]
score = 0
used_games = set()


# --- DISPLAY ---

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

    for i in range(3):
        for j in range(3):

            while True:
                print_board()
                print(f"Cell: Row = '{row_tags[i]}', Column = '{col_tags[j]}'")

                guess_input = input("Your guess: ").strip()

                resolved = disambiguate_game_name(guess_input)

                game_id = resolved["id"]
                game_name = resolved["name"]

                if game_id in used_games:
                    print("❗ You've already used that game!\n")
                    continue

                if is_valid_guess(game_id, game_name, i, j):
                    board[i][j] = game_name.title()
                    used_games.add(game_id)
                    score += 1
                    print("✅ Correct!\n")
                    break
                else:
                    if game_id is None:  # exact typed guess, not found in DB
                        print("❗ Game not found in database. Try again.\n")
                        continue        # re-prompt instead of penalizing
                    board[i][j] = '❌'
                    print("❌ Does not fit tags. Incorrect!\n")
                    break

    print_board()
    print(f"Game over! Final Score: {score}/9")


# --- RUN ---

if __name__ == "__main__":
    play_game()
