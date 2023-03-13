from nba_api.live.nba.endpoints import scoreboard
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

if __name__ == "__main__":
    from constants import TeamId
    
    try:
        games = get_todays_matchups()
        for match in games: 
            print(TeamId(match[0]), "vs", TeamId(match[1]))
    except Exception as e:
        print("ERROR:". e)
    