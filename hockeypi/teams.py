import pandas as pd
from hockeypi.cache import make_request

def get_teams_by_year(year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves all teams that played in a given season.
  
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of all teams that played in a given season
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}teams?season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['teams']
  df = pd.DataFrame.from_records(response['teams'])
  df = df.rename(columns={'id': 'teamId'})
  return df

def get_team_information(team_id, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves information about a given team.
  
  :param team_id: NHL assigned id for the team
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of information about a given team
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}teams/{team_id}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['teams']
  df = pd.DataFrame.from_records(response['teams'])
  df = df.rename(columns={'id': 'teamId'})
  return df 

def get_team_statistics_by_year(team_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves statistics for a given team in a given season.
  
  :param team_id: NHL assigned id for the team
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of statistics for a given team in a given season
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}teams/{team_id}/stats?season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['stats'][0]['splits'][0]['stat']
  df = pd.DataFrame.from_records(response['stats'][0]['splits'][0]['stat'], index=[0])
  df.insert(loc=0, column='teamId', value=team_id)
  return df

def get_team_statistics_rankings_by_year(team_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves statistics rankings for a given team in a given season.
  
  :param team_id: NHL assigned id for the team
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of statistics rankings for a given team in a given season
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}teams/{team_id}/stats?season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['stats'][0]['splits'][0]['stat']
  df = pd.DataFrame.from_records(response['stats'][1]['splits'][0]['stat'], index=[0])
  df.insert(loc=0, column='teamId', value=team_id)
  return df

def get_all_team_statistics_by_year(year, overwrite=False, verbose=False):
  '''
  Retrieves statistics for all teams in a given season.
  
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of statistics for all teams in a given season.
  '''
  df = get_teams_by_year(year, overwrite=overwrite, verbose=verbose)
  team_ids = df['teamId'].to_list()
  dfs = [get_team_statistics_by_year(team_id, year, \
    overwrite=overwrite, verbose=verbose) for team_id in team_ids]
  return pd.concat(dfs, ignore_index=True)

def get_all_team_statistics_rankings_by_year(year, overwrite=False, verbose=False):
  '''
  Retrieves statistics rankings for all teams in a given season.
  
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param raw: returns raw json response from web if True
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of statistics rankings for all teams in a given season.
  '''
  df = get_teams_by_year(year, overwrite=overwrite, verbose=verbose)
  team_ids = df['teamId'].to_list()
  dfs = [get_team_statistics_rankings_by_year(team_id, year, \
    overwrite=overwrite, verbose=verbose) for team_id in team_ids]
  return pd.concat(dfs, ignore_index=True)

def get_team_roster_by_year(team_id, year, raw=False, overwrite=False, verbose=False):
  '''
  Retrieves roster for a given team in a given season.
  
  :param team_id: NHL assigned id for the team
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of the roster for a given team in a given season
  '''
  base = 'https://statsapi.web.nhl.com/api/v1/'
  url = f'{base}teams/{team_id}/roster?season={year}{year+1}'
  response = make_request(url, overwrite=overwrite, verbose=verbose)
  if raw: return response['roster']
  df = pd.DataFrame.from_records(response['roster'])

  # Some df cleanup for easier analysis
  df['playerId'] = df['person'].apply(lambda x : x['id'])
  df['fullName'] = df['person'].apply(lambda x : x['fullName'])
  df['positionName'] = df['position'].apply(lambda x : x['name'])
  df['positionCode'] = df['position'].apply(lambda x : x['code'])
  df['positionType'] = df['position'].apply(lambda x : x['type'])
  df.drop(['person', 'position'], axis=1, inplace=True)
  df.insert(loc=0, column='teamId', value=team_id)
  return df

def get_all_team_roster_by_year(year, overwrite=False, verbose=False):
  '''
  Retrieves roster for a all teams in a given season.
  In essence, returns all players that played in a season. 
  Note that this contains duplicates for players that were traded mid-season.

  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: dataframe of the roster for a given team in a given season
  '''
  df_team = get_teams_by_year(year, overwrite=overwrite, verbose=verbose)
  team_ids = df_team['teamId'].to_list()
  dfs = [get_team_roster_by_year(team_id, year, overwrite=overwrite, verbose=verbose) \
    for team_id in team_ids]
  return pd.concat(dfs, ignore_index=True)

def get_team_id_by_name_and_year(name, year, overwrite=False, verbose=False):
  '''
  Get the team id by name and playing year.
  Must input the correct year that the team played in, in case the team
  went through a transition (e.g. Winnipeg Jets 1970 vs Winnipeg Jets 2019)

  :param name: team name with, or without the city (Calgary Flames or Flames)
  :param year: season start year (e.g. 2018-2019 season would be 2018)
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: integer team id of the team identified by given name and year.
  '''
  df = get_teams_by_year(year, overwrite=overwrite, verbose=verbose)
  
  if len(df[df['name'].str.lower() == name.lower()]) == 1:
    return df[df['name'].str.lower() == name.lower()]['teamId'].item()
  elif len(df[df['name'].str.lower().str.contains(name.lower())]) == 1:
    return df[df['name'].str.lower().str.contains(name.lower())]['teamId'].item()
  else:
    raise Exception('Unique team not found')