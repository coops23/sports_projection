#!/usr/bin/python3
import math, time, random, logging, datetime, csv, os
from common.constants import Seasons
from common.nba import get_todays_matchups, get_teams_players, get_players_matchup_data
from typing import List
from nba_api.stats.static import teams
from common.google_drive import upload_file, NBA_PLAYER_FOLDER_ID

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

_GP = 6 # Games played
_PTS = 30 # Points
_AST = 23 # Assists
_REB = 22 # Rebounds
_FG3M = 14 # 3 Point shots made
LOWER_SLEEP_LIMIT = 1.0
UPPER_SLEEP_LIMIT = 2.0
        
def calculate_player_projection(data) -> List[float]:    
    A = G = 0
    for i, (season, stats) in enumerate(data.items()):
        tf = math.exp((-1*i) / (len(data) - 1))
        if stats is not None:
            gf = stats[_GP]
            A += tf * gf
            G += gf
    T = G / A
    
    f_pts  = 0   
    f_ast  = 0 
    f_reb  = 0 
    f_fg3m = 0 
    for i, (season, stats) in enumerate(data.items()):
        if stats is not None:
            weight = (T * stats[_GP] * math.exp((-1*i) / (len(data) - 1))) / G
            f_pts  += stats[_PTS] * weight
            f_ast  += stats[_AST] * weight
            f_reb  += stats[_REB] * weight
            f_fg3m += stats[_FG3M] * weight

    return [f_pts, f_ast, f_reb, f_fg3m]

def format_row(team: str, player: str, data: List[float]) -> List[str]:
    row = [team, player] 
    if data:
        for i in range(0, len(data)):
            row.append("%0.2f" % (data[i]))
    else:
        row.append("Unknown. No historical match data for match up.")
    return row

try:
    LOGGER.info("------------------PLAYER PROJECTION START------------------")
    matchups = get_todays_matchups()
    time.sleep(random.uniform(LOWER_SLEEP_LIMIT, UPPER_SLEEP_LIMIT))
    if len(matchups) > 0:
        log_file = 'player_projection_%s.csv' % (str(datetime.date.today()))
        LOGGER.debug("Creating %s" % log_file)
        with open(log_file, 'w', newline='') as file:
            LOGGER.debug("Setting up writer")
            writer = csv.writer(file)
            writer.writerow(['Team', 'Player', "Points", "Assists", "Rebounds", "3 Point Shots Made"])
                
            seasons = [season for season in Seasons]
            seasons.reverse()

            for match in matchups:
                # Team
                team = match[0]
                opponent = match[1]
                players = get_teams_players(team, seasons[0].value)
                time.sleep(random.uniform(LOWER_SLEEP_LIMIT, UPPER_SLEEP_LIMIT))
                (players_data_header, players_data) = get_players_matchup_data(team_id=team,
                                        opponent_id=opponent,
                                        seasons=seasons,
                                        )
                time.sleep(random.uniform(LOWER_SLEEP_LIMIT, UPPER_SLEEP_LIMIT))
                for (player_id, player_name) in players:
                    data = players_data.get(player_id)
                    team_string = teams.find_team_name_by_id(team)['full_name']
                    row = []
                    if data is not None:
                        projection = calculate_player_projection(data)
                        row = format_row(team_string, player_name, projection)
                    else:
                        team_string = teams.find_team_name_by_id(team)['full_name']
                        row = format_row(team_string, player_name, [])
                    print(row)
                    LOGGER.info(row)
                    writer.writerow(row)
                
                # Opponent
                team = match[1]
                opponent = match[0]
                players = get_teams_players(team, seasons[0].value)
                time.sleep(random.uniform(LOWER_SLEEP_LIMIT, UPPER_SLEEP_LIMIT))
                (players_data_header, players_data) = get_players_matchup_data(team_id=team,
                                        opponent_id=opponent,
                                        seasons=seasons,
                                        )
                time.sleep(random.uniform(LOWER_SLEEP_LIMIT, UPPER_SLEEP_LIMIT))
                for (player_id, player_name) in players:
                    data = players_data.get(player_id)
                    team_string = teams.find_team_name_by_id(team)['full_name']
                    row = []
                    if data is not None:
                        projection = calculate_player_projection(data)
                        row = format_row(team_string, player_name, projection)
                    else:
                        team_string = teams.find_team_name_by_id(team)['full_name']
                        row = format_row(team_string, player_name, [])
                    print(row)
                    LOGGER.info(row)
                    writer.writerow(row)
    else:
        LOGGER.info("No games today")
    LOGGER.debug("Uploading %s to google drive" % log_file)
    upload_file(NBA_PLAYER_FOLDER_ID, log_file)
    LOGGER.debug("File uploaded to google drive!")
    os.remove(log_file)
    LOGGER.info("------------------PLAYER PROJECTION FINISH------------------")
except Exception as e:
    LOGGER.error(e)
