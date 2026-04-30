import requests
import random
import time
import requests_cache

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
    "Classic (before 2010)": "first_release_date < 1262304000"
}

# --- CHECK IF COMBO HAS ANY GAME ---
def has_games(genre_id, condition):
    query = f"""
    fields name;
    where genres = ({genre_id}) & {condition};
    limit 1;
    """

    r = requests.post(URL, headers=HEADERS, data=query)
    if r.status_code != 200:
        return False
    return len(r.json()) > 0

# --- PRECACHE SET OF VALID GAMES SO API ISN'T CALLED LIVE DURING GAMEPLAY ---
def precache_cells(rows, cols):
    cell_answers = {}

    for i, (_, genre_id) in enumerate(rows):
        for j, (_, condition) in enumerate(cols):

            query = f"""
            fields name;
            where genres = ({genre_id}) & {condition};
            limit 500;
            """

            r = requests.post(URL, headers=HEADERS, data=query)

            if r.status_code != 200:
                cell_answers[(i, j)] = set()
                continue

            data = r.json()

            # Store lowercase names for easier matching
            names = {game["name"].lower() for game in data}
            cell_answers[(i, j)] = names

    return cell_answers

# --- GENERATE VALID GRID ---
def generate_valid_grid():
    genre_items = list(GENRES.items())
    column_items = list(COLUMNS.items())

    while True:
        rows = random.sample(genre_items, 3)
        cols = random.sample(column_items, 3)

        valid = True
        for _, g_id in rows:
            for _, cond in cols:
                if not has_games(g_id, cond):
                    valid = False
                    break
            if not valid:
                break

        if valid:
            return rows, cols

        time.sleep(0.2)


# --- VALIDATE PLAYER GUESS ---
def is_valid_guess(game_name, i, j):
    guess = game_name.strip().lower()

    # 1. quick cache check (optional UX boost)
    if guess in cell_answers[(i, j)]:
        return True

    # 2. authoritative IGDB check
    genre_id = rows[i][1]
    condition = cols[j][1]

    query = f'''
    fields name;
    where name ~ "{game_name}"
    & genres = ({genre_id})
    & {condition};
    limit 1;
    '''

    r = requests.post(URL, headers=HEADERS, data=query)
    data = r.json()

    if not data:
        return False

    return any(game["name"].lower() == guess for game in data) # enforce exact match

# --- CHECK TO DETERMINE IF INCORRECT GUESS IS IN THE DATA BASE OR NOT ---
def is_game_in_database(game_name):

    query = f'''
    fields name;
    where name = "{game_name}";
    limit 1;
    '''

    r = requests.post(URL, headers=HEADERS, data=query)
    return len(r.json()) > 0

# --- QUERIES THE PLAYER TO WHAT GAME THEY ARE REFERRING TO FOR DISAMBIGUATION (like get_person_id function in pset 5!) ---
#def get_game_name()



# --- INIT GAME ---
rows, cols = generate_valid_grid()

cell_answers = precache_cells(rows, cols)

row_tags = [r[0] for r in rows]
col_tags = [c[0] for c in cols]

# Track board state
board = [[None for _ in range(3)] for _ in range(3)]


# --- DISPLAY BOARD ---
def print_board():
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

                if is_valid_guess(guess, i, j):
                    board[i][j] = guess
                    print("✅ Correct!\n")
                    break

                elif is_game_in_database(guess):
                    print("❌ Game does not match tags. Incorrect!\n")
                    break

                else:
                    print("❗ Game is not in database. Try again! Please enter a valid game.")

    print_board()
    print("Game over!")


# --- RUN ---
if __name__ == "__main__":
    play_game()
