from bs4 import BeautifulSoup
import requests

def test_schedule_form(players, tables, rounds, name_list):
    url = 'http://10.0.0.115:8080/schedule'  # Change to your application's URL
    data = {'players': players, 'tables': tables, 'rounds': rounds, 'nameList': name_list}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        return f"error: players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list} generated {response.status_code}"

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
                        return f"error: players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list}: Duplicate player pair found. {pair1}, or {pair2}"
                    used_pairs.update([pair1, pair2])
                    round_players.update(player_numbers[i:i+4])
                else:
                    return f"error: players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list}: Incomplete player pair found. {player_numbers[i:i+4]}"

        # Check for unique players in the round
        if not round_players.issubset(all_players):
            return f"error: players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list}: Non-unique or invalid player numbers found in a round."

        # Check for duplicate bye players
        bye_cell = cells[-1]  # The last cell is the bye cell
        players_in_bye = [int(num) for num in bye_cell.get_text().split() if num.isdigit()]
        for num in players_in_bye:
            if num in bye_players:
                return f"error: players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list}: Duplicate player number {num} found in bye column."
            bye_players.add(num)

    return f"players: {players}, tables {tables}, rounds {rounds}, namelist: {name_list}: No errors found in tournament schedule."

# Test example
print(test_schedule_form(43, 10, 10, 'game_of_thrones'))

