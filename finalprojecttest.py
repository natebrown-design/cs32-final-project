# Sample game database (9 games)
games = {
    "The Legend of Zelda: Breath of the Wild": {"open-world", "fantasy", "singleplayer"},
    "Elden Ring": {"open-world", "fantasy", "soulslike"},
    "Dark Souls": {"fantasy", "soulslike", "singleplayer"},
    "Call of Duty: Modern Warfare": {"shooter", "multiplayer", "modern"},
    "Overwatch": {"shooter", "multiplayer", "hero"},
    "Halo Infinite": {"shooter", "multiplayer", "sci-fi"},
    "Stardew Valley": {"indie", "farming", "singleplayer"},
    "Minecraft": {"sandbox", "open-world", "multiplayer"},
    "Hades": {"indie", "roguelike", "singleplayer"},
}

# Define grid tags
row_tags = ["open-world", "shooter", "indie"]
col_tags = ["multiplayer", "singleplayer", "fantasy"]

# Track board state
board = [[None for _ in range(3)] for _ in range(3)] # initalizes game board like a matrix, all filled with None to start

# Function to check if a guess is valid
def is_valid_guess(game_name, row_tag, col_tag):
    if game_name not in games:
        return False
    tags = games[game_name]
    return row_tag in tags and col_tag in tags

# --- Display board ---
def print_board():
    print("\nCurrent Board:")
    print(" " * 20 + " | ".join(col_tags))
    print("-" * 60)
    for i in range(3):
        row_display = []
        for j in range(3):
            cell = board[i][j] if board[i][j] else "EMPTY"
            row_display.append(cell[:15])  # shorten long titles
        print(f"{row_tags[i]:<18} | " + " | ".join(row_display))
    print()

# --- Game loop ---
def play_game():
    print("Welcome to Video Game-doku!")
    print("Enter a game that matches BOTH the row and column tags.\n")

    for i in range(3):
        for j in range(3):
            print_board()
            print(f"Cell: Row = '{row_tags[i]}', Column = '{col_tags[j]}'")

            guess = input("Your guess: ").strip()

            if is_valid_guess(guess, row_tags[i], col_tags[j]):
                board[i][j] = guess
                print("✅ Correct!\n")
            else:
                print("❌ Incorrect or invalid game.\n")

    print_board()
    print("Game over!")

# --- Run the game ---
if __name__ == "__main__":
    play_game()
