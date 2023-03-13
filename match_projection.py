import time, random, math, csv, os, datetime
from common.constants import TeamId, Seasons
from common.nba import get_todays_matchups
from typing import Tuple, List
from common.google_drive import upload_file, NBA_TEAM_FOLDER_ID
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.library.parameters import PerModeDetailed

def get_matchup_data(seasons: List[Seasons], team: str, opponent: str):
    data = []
    for season in seasons:
        print("Pulling", season.value, TeamId(team), "vs", TeamId(opponent), "data")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(season=season.value, per_mode_detailed=PerModeDetailed.per_game, team_id_nullable=team, opponent_team_id=opponent)
        team_stats.get_json()
        result = team_stats.get_dict()
        result_sets = result['resultSets']
        data.append(result_sets[0]['rowSet'])
        time.sleep(random.uniform(1.0, 2.0))
    return data

def calculate_match_projection(seasons, data) -> Tuple[float, float, float, float, float]:
    _GP = 2
    _PTS = 26
    _W = 3
    _PLUS_MINUS = 27
    
    A = 0
    G = 0
    for i in range(0, len(seasons)):
        dt = (i-len(seasons)+1) / len(seasons)
        time_factor = math.exp(dt)
        if data[i] is not None:
            if len(data[i]) > 0:
                game_factor = data[i][0][_GP]
                A += time_factor * game_factor   
                G += data[i][0][_GP]
    T = G / A
    
    # Weighting
    weight = []
    for i in range(0, len(seasons)):
        t_i = math.exp((i-len(seasons)+1) / len(seasons))
        if data[i] is not None:
            if len(data[i]) > 0:
                weight.append((T * data[i][0][_GP] * t_i) / G)
            else:
                weight.append(None)   
        else:
            weight.append(None)
        
    # Win % / MoneyLine ---	FGM Home --- FGM Away --- Total (over/under) --- Spread
    f_moneyline = 0
    f_fgm_home = 0
    f_fgm_away = 0
    f_total_over_under = 0
    f_spread = 0
    for i in range(0, len(seasons)):
        if data[i] is not None:
            if len(data[i]) > 0:
                moneyline = data[i][0][_W] / data[i][0][_GP]
                fgm_home = data[i][0][_PTS]
                fgm_away = data[i][0][_PTS] - data[i][0][_PLUS_MINUS]
                total_over_under = fgm_home + fgm_away
                spread = data[i][0][_PLUS_MINUS]
            
                f_moneyline         += moneyline * weight[i]
                f_fgm_home          += fgm_home * weight[i]
                f_fgm_away          += fgm_away * weight[i]
                f_total_over_under  += total_over_under * weight[i]
                f_spread            += spread * weight[i]
    
    return (f_moneyline, f_fgm_home, f_fgm_away, f_total_over_under, f_spread)

def format_row(team: str, opponent: str, moneyline, fgm_home, fgm_away, total_over_under, spread) -> List[str]:
    if moneyline < 0.5:
        moneyline = opponent
    else:
        moneyline = team
    if spread >= 0:
        spread = "%s +%0.2f" % (team, spread)
    else:
        spread = "%s +%0.2f" % (opponent, spread*-1)
    row = [team + " vs " + opponent, moneyline, spread, '%.0f' % total_over_under]
    return row

log_file = 'match_projection_%s.csv' % (str(datetime.date.today()))
with open(log_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Matchup', 'Money Line', "Spread", "Total"])
    
    todays_matchups = get_todays_matchups()
    seasons = [season for season in Seasons]

    for matchup in todays_matchups:
        team = matchup[0]
        opponent = matchup[1]
        data = get_matchup_data(seasons, team, opponent)
        (moneyline, fgm_home, fgm_away, total_over_under, spread) = calculate_match_projection(seasons, data)
        row = format_row(str(TeamId(team)), str(TeamId(opponent)), moneyline, fgm_home, fgm_away, total_over_under, spread)
        writer.writerow(row)
upload_file(NBA_TEAM_FOLDER_ID, log_file)
os.remove(log_file)