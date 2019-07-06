import requests
import json
import os

def make_request(url, overwrite=False, verbose=False):
  '''
  Retrieves response from the given url, either from web or cache.
  
  :param overwrite: overwrites cache if True
  :param verbose: shows logs if True
  :returns: web response for the given url
  '''
  filename = 'cache/' + encode_url(url) + '.json'

  # create cache directory if it doesn't exist.
  if not os.path.exists('cache/'):
    os.makedirs('cache/')

  # cache hit - retrieve from cache.
  if os.path.isfile(filename) and not overwrite:
    if verbose:
      print(f'Cache Hit for {url}')
    with open(filename) as f:
      return json.load(f)

  # cache miss - make request, and save to cache. 
  response = requests.get(url).json()
  if verbose:
    if overwrite:
      print(f'Overwriting cache for {url}')
    else:
      print(f'Cache Miss for {url}')

  # write to cache.
  with open(filename, 'w') as f:
    json.dump(response, f)
  return response

def encode_url(url):
  '''
  Create unique fingerprint for each url that is os-compliant.
  
  :param url: url to encode
  :returns: os-compliant filename for a url
  '''
  encoding_dict = {':' : ';', '/' : '#', '?' : '$'}
  encoded_url = ''
  for char in url:
    if char in encoding_dict.keys():
      encoded_url += encoding_dict[char]
    else:
      encoded_url += char
  return encoded_url