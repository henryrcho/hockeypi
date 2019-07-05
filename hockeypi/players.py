import pandas as pd
import numpy as np
from hockeypi.cache import make_request
from hockeypi.exceptions import UnknownPlayerException

def get_player_info(player_id, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves information about a given player.
  
  :param player_id: NHL assigned id for the player
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of information about a given player
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}people/{player_id}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['people']
  df = pd.DataFrame.from_records(response['people'])
  df = df.rename(columns={'id': 'playerId'})
  return df

def get_player_statistics_by_year(player_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves statistics for a given player for a given season.
  
  :param player_id: NHL assigned id for the player
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of statistics about a given player
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}people/{player_id}/stats?stats=statsSingleSeason&season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  
  if 'stats' not in response.keys() or len(response['stats'][0]['splits']) == 0:
    raise UnknownPlayerException(f'No statistics available for player \
      {player_id} for year {year}')

  if raw: return response['stats'][0]['splits'][0]['stat']
  df = pd.DataFrame.from_records(response['stats'][0]['splits'][0]['stat'], index=[0])
  df.insert(loc=0, column='playerId', value=player_id)
  df.insert(loc=0, column='season', value=f'{year}{year+1}')
  return df

def get_player_game_level_statistics_by_year(player_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves game level statistics for a given player for a given season.
  
  :param player_id: NHL assigned id for the player
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of game level statistics about a given player
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}people/{player_id}/stats?stats=gameLog&season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)

  if 'stats' not in response.keys() or len(response['stats'][0]['splits']) == 0:
    raise UnknownPlayerException(f'No game level statistics available for player \
      {player_id} for year {year}')

  if raw: return response['stats'][0]['splits']
  df = pd.DataFrame.from_records(response['stats'][0]['splits'])

  # Only extract useful fields
  df['gameId'] = df['game'].apply(lambda x : x['gamePk'])
  df['teamId'] = df['team'].apply(lambda x : x['id'])
  df['opponentTeamId'] = df['opponent'].apply(lambda x : x['id'])

  # Get consistent stat types
  stat_types = list(get_player_statistics_by_year(player_id, year, \
    overwrite=overwrite, verbose=verbose).keys())
  stat_types = [stat for stat in stat_types if 'PerGame' not in stat \
    and stat != 'playerId' and stat != 'season']
  for stat_type in stat_types:
    df[stat_type] = df['stat'].apply(lambda x : x[stat_type] if \
      stat_type in x.keys() else np.nan)

  df.insert(loc=0, column='playerId', value=player_id)
  df.drop(['game', 'team', 'opponent', 'stat'], axis=1, inplace=True)
  return df

def get_player_active_years(player_id, verbose=False, overwrite=False):
  '''
  Retrieves years in which the given player played at least one game.
  Unfortunately, there is no easy way to retrieve this information via the NHL API.
  We need to try retrieving statistics for the player for all NHL years to ascertain
  which years the player was active.
  
  :param player_id: NHL assigned id for the player
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: list of years (season start years) in which the player was active
  '''
  years = []
  nhl_years = [year for year in range(1917, 2018)]
  for year in nhl_years:
    try:
      df = get_player_statistics_by_year(player_id, year, \
        verbose=verbose, overwrite=overwrite)
      years.append(year)
    except UnknownPlayerException: pass
    except: raise
  return years

def get_player_statistics_complete_history(player_id, verbose=False, overwrite=False):
  '''
  Retrieves a player's complete statistics history.
  
  :param player_id: NHL assigned id for the player
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of a player's complete statistics history
  '''
  dfs = []
  for year in get_player_active_years(player_id, verbose=False, overwrite=False):
    dfs.append(get_player_statistics_by_year(player_id, year, \
      verbose=verbose, overwrite=overwrite))
  return pd.concat(dfs, ignore_index=True)

def get_player_game_level_statistics_complete_history(player_id, verbose=False, overwrite=False):
  '''
  Retrieves a player's complete game level statistics history.
  
  :param player_id: NHL assigned id for the player
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of a player's complete game level statistics history
  '''
  dfs = []
  for year in get_player_active_years(player_id, verbose=False, overwrite=False):
    dfs.append(get_player_game_level_statistics_by_year(player_id, year, \
      verbose=verbose, overwrite=overwrite))
  return pd.concat(dfs, ignore_index=True)