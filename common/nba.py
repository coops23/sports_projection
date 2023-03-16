from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.library.parameters import PerModeDetailed
from .constants import Seasons
from typing import List
from datetime import datetime

def get_todays_matchups() -> List[List]:
    try:
        games = scoreboard.ScoreBoard()
        matchups = []
        for game in games.get_dict()['scoreboard']['games']:
            datetime_str = game['gameEt'] # 2023-03-13T19:00:00Z
            date_str = datetime_str.split("T")[0]
            date_object = datetime.strptime(date_str, '%Y-%m-%d')
            if date_object.date() < datetime.now().date():
                raise Exception("Games pulled are not today's games")
            home_team_id = game['homeTeam']['teamId']
            away_team_id = game['awayTeam']['teamId']
            matchups.append([home_team_id, away_team_id])
        return matchups
    except Exception as e:
        raise e

def get_teams_players(team_id: str, season: str) -> List[str]:
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(team_id_nullable=team_id, season=season)
    player_data = player_stats.get_dict()['resultSets'][0]['rowSet']
    _player_header = player_stats.get_dict()['resultSets'][0]['headers']

    players = []
    for player in player_data:
        players.append((player[0], player[1]))
    
    return players

def get_players_matchup_data(team_id: str, opponent_id: str, seasons: Seasons, per_mode: PerModeDetailed = PerModeDetailed.per_game):
    data = {}
    season_data_template = {}
    for season in seasons:
        season_data_template[season.value] = None
    for season in seasons:
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(team_id_nullable=team_id, opponent_team_id=opponent_id, season=season.value, per_mode_detailed=per_mode)
        player_data = player_stats.get_dict()['resultSets'][0]['rowSet']
        header = ["SEASON"] + player_stats.get_dict()['resultSets'][0]['headers']
        
        for i in range(0, len(player_data)):
            player_id = player_data[i][0]
            if data.get(player_id) is None:
                season_data = season_data_template.copy()
                data[player_id] = season_data
            data[player_id][season.value] = player_data[i]
            
    return (header, data)
    