import cgi
import math
import random
from itertools import combinations, permutations
import os

def get_name_files(directory):
    try:
        files = os.listdir(directory)
        return [file for file in files if os.path.isfile(os.path.join(directory, file))]
    except OSError:
        return []

def generate_schedule(players, tables, rounds):
    max_players = tables * 4
    all_players = set(range(1, players + 1))
    excess_players = max(players - max_players, 0)
    total_bye_players = excess_players * rounds
    total_pairs_needed = tables * 2 * rounds
    total_unique_pairs_possible = len(list(combinations(all_players, 2)))
    message = ""

    if total_pairs_needed > total_unique_pairs_possible:
        return "", "Players would have to play with the same partner more than once, please use fewer rounds or more players."

    if excess_players > 3:
        additional_tables_needed = math.ceil(excess_players / 4)
        return "", f"You need {additional_tables_needed} more tables to have less than 4 bye players."
    elif excess_players > 0:
        message += f"There are {excess_players} more players than can be seated at {tables} tables... Some players will have byes.<p>\n"

    if total_bye_players > players:
        return "", f"Players would have to be on bye more than once, please use fewer rounds."

    schedule = {}
    used_pairs = set()
    all_possible_pairs = list(permutations(all_players, 2))
    players_had_bye = set()

    for round_number in range(1, rounds + 1):
        valid_round = False
        while not valid_round:
            random.shuffle(all_possible_pairs)
            round_pairs = []
            round_players = set()

            for pair in all_possible_pairs:
                # Ensure the smaller number is always first in the pair
                sorted_pair = tuple(sorted(pair))
                if sorted_pair not in used_pairs and all(player not in round_players for player in sorted_pair):
             #  You can replace this line above with the line below to generate duplicate pairs for testing the tester
             #   if all(player not in round_players for player in sorted_pair):
                    round_pairs.append(sorted_pair)
                    round_players.update(sorted_pair)
                    if len(round_pairs) == tables * 2:
                        break

            # Check if an even number of pairs is formed
            if len(round_pairs) % 2 != 0:
                continue  # Re-shuffle and try again if odd number of pairs

            active_players = set(p for pair in round_pairs for p in pair)
            potential_byes = set(all_players) - active_players

            # Ensure byes are not repeated if possible
            potential_byes = list(set(all_players) - active_players)
            if not players_had_bye.isdisjoint(set(potential_byes)) and len(players_had_bye) < len(all_players):
                continue

            round_byes = random.sample(potential_byes, excess_players) if excess_players else []
            used_pairs.update(round_pairs)
            players_had_bye.update(set(round_byes))
            valid_round = True

        games = [(round_pairs[i], round_pairs[i + 1]) for i in range(0, len(round_pairs), 2)]
        schedule[round_number] = {'games': games, 'byes': round_byes}


    return schedule, message

def get_player_names(file_path, num_players):
    with open(file_path, 'r') as file:
        names = [line.strip() for line in file]
    return names[:num_players]

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        name_files = get_name_files('/usr/share/nginx/name_dictionaries/')
        response_body = '<!DOCTYPE html><html><head><title>Tournament Scheduler</title></head><body>'
        response_body += '<form action="/schedule" method="post">'
        response_body += '<label for="players">Number of Players:</label><input type="number" id="players" name="players"><br><p><p>'
        response_body += '<label for="tables">Number of Tables:</label><input type="number" id="tables" name="tables"><br><p><p>'
        response_body += '<label for="rounds">Number of Rounds:</label><input type="number" id="rounds" name="rounds"><br><p><p>'
        response_body += '<label for="nameList">Name List:</label><select id="nameList" name="nameList">'
        for file in name_files:
            response_body += f'<option value="{file}">{file}</option>'
        response_body += '</select><br><p><p><button type="submit">Generate Schedule</button></form></body></html>'
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))])
        return [response_body.encode()]

    elif environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    
        players = int(form.getvalue('players', 0))
        tables = int(form.getvalue('tables', 0))
        rounds = int(form.getvalue('rounds', 0))
        name_list = form.getvalue('nameList')
        player_names = get_player_names(f'/usr/share/nginx/name_dictionaries/{name_list}', players)
        schedule, message = generate_schedule(players, tables, rounds)
    
        response_body = "<html><body>"
    
        # Adding CSS for page breaks
        response_body += "<style>.player-schedule { page-break-before: always; }</style>"
    
        response_body += "<h1>Tournament Schedule</h1>"
        if message:
            response_body += f"<p>{message}</p>"
    
        # Include the entire tournament schedule
        if isinstance(schedule, dict):
            response_body += "<h2>Complete Tournament Schedule</h2>"
            response_body += "<table border='1'><tr><th>Round</th>"
    
            for table_num in range(1, tables + 1):
                response_body += f"<th>Table {table_num}</th>"
            response_body += "<th>Bye</th></tr>"
    
            for round_number, round_info in schedule.items():
                response_body += f"<tr><td>{round_number}</td>"
                for i, (pair1, pair2) in enumerate(round_info['games']):
                    response_body += f"<td>{pair1[0]},{pair1[1]} vs {pair2[0]},{pair2[1]}</td>"
                for _ in range(len(round_info['games']), tables):
                    response_body += "<td></td>"
                byes_str = ', '.join(map(str, round_info['byes']))
                response_body += f"<td>{byes_str}</td></tr>"
            response_body += "</table>"
    
        # Include individual player schedules with names and page breaks
        for player in range(1, players + 1):
            player_name = player_names[player - 1]
            response_body += f'<div class="player-schedule"><h2>Player {player} - {player_name}</h2>'
            response_body += "<table border='1'><tr><th>Round</th><th>Table</th><th>With</th><th>Against</th></tr>"
    
            for round_number, round_info in schedule.items():
                player_table = None
                player_partner = None
                player_opponents = []
    
                for table_num, (pair1, pair2) in enumerate(round_info['games'], 1):
                    if player in pair1:
                        player_table = table_num
                        partner_index = 1 if pair1[0] == player else 0
                        partner_number = pair1[partner_index]
                        player_partner = f"{partner_number} - {player_names[partner_number - 1]}"
                        player_opponents = [f"{p} - {player_names[p - 1]}" for p in pair2]
                        break
                    elif player in pair2:
                        player_table = table_num
                        partner_index = 1 if pair2[0] == player else 0
                        partner_number = pair2[partner_index]
                        player_partner = f"{partner_number} - {player_names[partner_number - 1]}"
                        player_opponents = [f"{p} - {player_names[p - 1]}" for p in pair1]
                        break
    
                if player in round_info['byes']:
                    response_body += f"<tr><td>{round_number}</td><td>Bye</td><td>-</td><td>-</td></tr>"
                elif player_table:
                    response_body += f"<tr><td>{round_number}</td><td>{player_table}</td><td>{player_partner}</td><td>{' & '.join(player_opponents)}</td></tr>"
    
            response_body += "</table></div>"
    
        response_body += "</body></html>"
    
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body.encode()]
    
