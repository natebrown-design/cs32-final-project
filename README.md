# cs32-final-project
My CS32 Final Project

Set-Up Steps:
- you must obtain a personal API access key by creating a Twitch developer account, and changing the "client_id" and "client_secret" key values in IGDB_API_access.py; then, replace the access token and client ID in fp_status with your own credentials
- ensure that you have the requests_cache library installed; run 'pip install requests-cache' in terminal if not
- MAKE SURE TO RUN fp_FINAL.py, as this is the most current correct file.

This project is inspired by PokeDoku, a daily guessing game where the goal is to fill a 3x3 grid of pokemon where type is on the left, and specific attribute is on the right (combining the two in your selection). My project is a twist on this, instead using video games as the target input. I have pulled tagged data from a massive database of video games, with tags such as "adventure", "FPS", and "puzzle" for genre and 'release date' and 'popularity' for the column-wise description. These tags will be randomized every time the script is ran. If a player inputs a game that fulfills both the genre and the column requirement, then that game is saved in the space. A player is awarded a point for each grid space they answer correctly. I have also included a detailed disambiguation system, similar to the one used in Pset 5, 

AS OF FINAL SUBMISSION:



Generative AI Tools:
ChatGPT was used to generate the board display (lines 136-146), as well as assist in understanding caching. ChatGPT also recommended the inclusion of a combination of pre-caching and live API queries mid gameplay, as initially including only pre-caching missed many popular games that fit in both the column and row tags when testing.
