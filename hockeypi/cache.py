import requests
import json
import os

def make_request(url, overwrite=False, verbose=False):
  '''
  Make a request and cache the data. 
  If data is in cache, retrieve data from cache.
  '''
  filename = 'cache/' + encode_url(url) + '.json'

  # create cache directory if it doesn't exist.
  if not os.path.exists('cache/'):
    os.makedirs('cache/')

  # cache hit - retrieve from cache.
  if os.path.isfile(filename) and not overwrite:
    if verbose:
      print('Cache Hit for ' + url)
    with open(filename) as f:
      return json.load(f)
      
  # cache miss - make request, and save to cache. 
  response = requests.get(url).json()
  if verbose:
    print('Cache Miss for ' + url)
  with open(filename, 'w') as f:
    json.dump(response, f)
  return response

def encode_url(url):
  '''
  Encode url for os compliant filenames.
  '''
  encoding_dict = {':' : ';', '/' : '#', '?' : '$'}
  encoded_url = ''
  for char in url:
    if char in encoding_dict.keys():
      encoded_url += encoding_dict[char]
    else:
      encoded_url += char
  return encoded_url