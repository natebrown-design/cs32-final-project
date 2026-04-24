# cs32-final-project
My CS32 Final Project

Set-Up Steps:
- you must obtain a personal API access key by creating a Twitch developer account, and changing the "client_id" and "client_secret" key values in IGDB_API_access.py; then, replace the access token and client ID in fp_status with your own credentials
- ensure that you have the requests_cache library installed; run 'pip install requests-cache' in terminal if not

This project is inspired by PokeDoku, a daily guessing game where the goal is to fill a 3x3 grid of pokemon where type is on the left, and specific attribute is on the right (combining the two in your selection). My project is a twist on this, instead using video games as the target input. I will grab tagged data from a massive set of video games, with tags such as "adventure", "FPS", and "puzzle" for genre and 'release date' and 'popularity' for the column-wise description. These tags will be randomized every day. If a player inputs a game that fulfills both the genre and the column requirement, then that game is saved in the space. Extra points will be awarded if a player is able to guess correctly 3 in a row. If time permits, I will add a scoring system that awards extra points for unique answers based on who has played and input a certain game before (if you guess a game that no one has guessed before, you will get more points).

AS OF FP STATUS:

This project currently randomizes the column and row tags in the game, ensuring that there is at least one game in the database that matches both of those tags. My script then pre-caches up to 500 possible games that fit in each of the 9 slots; if a player inputs a game that was not in the list of 500, then the script will manually query the IGDB API to check if that game is in the database and matches the tags associated with it.

Generative AI Tools:
ChatGPT was used to 
