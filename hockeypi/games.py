import pandas as pd
import numpy as np
from hockeypi.cache import make_request
from hockeypi.teams import get_teams_by_year

def get_all_games_for_team_by_year(team_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves game information for a given team in a given season. 
  
  :param team_id: NHL assigned id for the team
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of game information for a given team in a given season.
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}schedule?teamId={team_id}&season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  
  if raw: return response['dates']
  df = pd.DataFrame.from_records(response['dates']).loc[:, ['date', 'games']]
  df['gameId'] = df['games'].apply(lambda x: x[0]['gamePk'])
  df['gameType'] = df['games'].apply(lambda x: x[0]['gameType'])
  df['season'] = df['games'].apply(lambda x: x[0]['season'])
  df['homeId'] = df['games'].apply(lambda x : x[0]['teams']['home']['team']['id'])
  df['awayId'] = df['games'].apply(lambda x : x[0]['teams']['away']['team']['id'])
  df['homeScore'] = df['games'].apply(lambda x : x[0]['teams']['home']['score'])
  df['awayScore'] = df['games'].apply(lambda x : x[0]['teams']['away']['score'])
  df['link'] = df['games'].apply(lambda x : x[0]['link'])
  df.drop(['games'], axis=1, inplace=True)
  df.insert(loc=0, column='teamId', value=team_id)
  return df

def get_all_games_by_year(year, overwrite=False, verbose=False):
  '''
  Retrieves game information for all teams in a given season.

  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of game information for all teams in a given season.
  '''
  df = get_teams_by_year(year, overwrite=overwrite, verbose=verbose)
  team_ids = df['teamId'].to_list()
  dfs = [get_all_games_for_team_by_year(team_id, year, \
      overwrite=overwrite, verbose=verbose) for team_id in team_ids]
  return pd.concat(dfs, ignore_index=True).drop_duplicates(['gameId'])

def get_stanley_cup_winner_by_year(year, overwrite=False, verbose=False):
  '''
  Retrieves Stanley Cup Champions for a given year.

  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: integer team id of the Stanley Cup Champions for a given year. 
  '''
  last_game = get_all_games_by_year(year, overwrite=overwrite, verbose=verbose) \
    .sort_values('date').tail(1)
  home_score = last_game['homeScore'].item()
  away_score = last_game['awayScore'].item()
  winner_id = last_game['homeId'].item() \
    if home_score > away_score else last_game['awayId'].item()
  return winner_id