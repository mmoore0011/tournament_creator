from bs4 import BeautifulSoup
import time
import requests

def test_schedule_form(players, notables, rounds, name_list):
    url = 'http://10.0.0.115:8080/schedule'  # Change to your application's URL
    data = {'players': players, 'tables': notables, 'rounds': rounds, 'nameList': name_list}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        return f"error: players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list} generated {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    tournament_table = soup.find('table')  # Assuming the first table is the tournament schedule
    rows = tournament_table.find_all('tr')[1:]  # Skip the header row

    all_players = set(range(1, players + 1))
    bye_players = set()
    used_pairs = set()
    for row in rows:
        cells = row.find_all('td')[1:-1]  # Skip the first (round number) and last (bye) cells
        round_players = set()
        for cell in cells:
            cell_text = cell.get_text()
            # Splitting by 'vs' and then by commas to extract individual player numbers
            player_numbers = [int(num.strip()) for part in cell_text.split('vs') for num in part.split(',') if num.strip().isdigit()]
            for i in range(0, len(player_numbers), 4):  # Process each game (4 players per game)
                if len(player_numbers[i:i+4]) == 4:  # Ensure there are 4 players for forming two pairs
                    pair1 = tuple(sorted(player_numbers[i:i+2]))
                    pair2 = tuple(sorted(player_numbers[i+2:i+4]))
                    if pair1 in used_pairs or pair2 in used_pairs:
                        return f"error: players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list}: Duplicate player pair found. {pair1}, or {pair2}"
                    used_pairs.update([pair1, pair2])
                    round_players.update(player_numbers[i:i+4])
                else:
                    return f"error: players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list}: Incomplete player pair found. {player_numbers[i:i+4]}"

        # Check for unique players in the round
        if not round_players.issubset(all_players):
            return f"error: players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list}: Non-unique or invalid player numbers found in a round."

        # Check for duplicate bye players
        bye_cell = cells[-1]  # The last cell is the bye cell
        players_in_bye = [int(num) for num in bye_cell.get_text().split() if num.isdigit()]
        for num in players_in_bye:
            if num in bye_players:
                return f"error: players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list}: Duplicate player number {num} found in bye column."
            bye_players.add(num)

    tables = soup.find_all('table')

    # Process complete tournament schedule
    tournament_schedule = {}
    tournament_rows = tables[0].find_all('tr')[1:]  # Skip the header row
    for row in tournament_rows:
        cells = row.find_all('td')
        round_number = int(cells[0].get_text())
        games = []
        for cell in cells[1:-1]:  # Skip round number and bye cells
            game_players = cell.get_text().split(' vs ')
            if len(game_players) == 2:
                pair1 = [int(num) for num in game_players[0].split(',')]
                pair2 = [int(num) for num in game_players[1].split(',')]
                if len(pair1) == 2 and len(pair2) == 2:
                    games.append((tuple(pair1), tuple(pair2)))
        byes = [int(num) for num in cells[-1].get_text().split() if num.isdigit()]
        tournament_schedule[round_number] = {'games': games, 'byes': byes}

    # Validate each player's individual schedule
    for player in range(1, players + 1):
        player_schedule = tables[player].find_all('tr')[1:]  # Skip the header row
        for row in player_schedule:
            cells = row.find_all('td')
            round_number = int(cells[0].get_text())
            table_number = cells[1].get_text()

            if table_number == 'Bye':
                if player not in tournament_schedule[round_number]['byes']:
                    return f"error: Player {player} not found in byes for round {round_number}"
            else:
                player_game = None
                for game in tournament_schedule[round_number]['games']:
                    if player in game[0] or player in game[1]:
                        player_game = game
                        break

                if not player_game:
                    return f"error: Player {player} game not found in round {round_number}"

                # Correctly extract and verify partner and opponents
                if player in player_game[0]:
                    partner_number = player_game[0][0] if player_game[0][1] == player else player_game[0][1]
                    opponents = player_game[1]
                else:
                    partner_number = player_game[1][0] if player_game[1][1] == player else player_game[1][1]
                    opponents = player_game[0]

                if partner_number != int(cells[2].get_text().split()[0]):
                    return f"error: Incorrect partner for player {player} in round {round_number}"
 
                if sorted(opponents) != sorted([int(num.split()[0]) for num in cells[3].get_text().split('&')]):
                    return f"error: Incorrect opponents for player {player} in round {round_number}"

    return f"players: {players}, tables {notables}, rounds {rounds}, namelist: {name_list}: No errors found."

def calculate_tables(players):
    # Calculate the number of tables needed for no more than 3 unseated players
    return (players + 3) // 4

# Iterate over a range of players and rounds
for players in range(8, 56):  # From 8 to 55 players
    tables = calculate_tables(players)
    for rounds in range(2, 16):  # From 2 to 15 rounds
        print(f"Testing with {players} players, {tables} tables, and {rounds} rounds.")
        result = test_schedule_form(players, tables, rounds, 'game_of_thrones')
        print(result)
        time.sleep(5)
