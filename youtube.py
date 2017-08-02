# Boilerplate code for YouTube OAuth 2.0

import httplib2
import os
import sys
import time

from songs import get_song_list

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client.contrib import gce

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
	flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
		message=MISSING_CLIENT_SECRETS_MESSAGE)

	storage = Storage("%s-oauth2.json" % sys.argv[0])
	credentials = storage.get()

	# credentials = gce.AppAssertionCredentials(
	# 	scope='https://www.googleapis.com/auth/devstorage.read_write')

	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

		# Trusted testers can download this discovery document from the developers page
		# and it should be in the same directory with the code.
	return build(API_SERVICE_NAME, API_VERSION,
		http=credentials.authorize(httplib2.Http()))

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      # Convert a name like "snippet.tags[]" to snippet.tags, but handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True
      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
	good_kwargs = {}
	if kwargs is not None:
		for key, value in kwargs.items():
			if value:
				good_kwargs[key] = value
	return good_kwargs

def print_results(results):
	print(results)

args = argparser.parse_args()
service = get_authenticated_service(args)

### END BOILERPLATE CODE

def get_song_id(service, **kwargs):
	"""
	Given a song name, returns most relevant videoId for song name.
	Since song name is pulled directly from the list that has the exact song name
	the first result is the most relevant song.

	:param: dict of part, maxResults, q, type where q is title of song
	:return: String object representing a single videoId of q. Returns none if no videoId
	"""
	kwargs = remove_empty_kwargs(**kwargs)
	results = service.search().list(**kwargs).execute()
	result_dic = results['items'][0]
	if result_dic and 'videoId' in result_dic['id']:
		return result_dic['id']['videoId']
	return None

def create_playlist(properties, **kwargs):
	"""
	Create a playlist of title, description and privacyStatus and returns 
	the created playlistId for insertion.

	:param: dict of title, description and privacy status
	:return: String object representing newly created playlists' playlistId
	"""
	resource = build_resource(properties)
	kwargs = remove_empty_kwargs(**kwargs)
	results = service.playlists().insert(body=resource, **kwargs).execute()
	return results['id']

def playlist_insert(properties, **kwargs):
	"""
	Inserts a given song s into a playlist p

	:param: dict of playlistId that represents playlist p, videoId of song to insert
	"""
	resource = build_resource(properties)
	kwargs = remove_empty_kwargs(**kwargs)
	results = service.playlistItems().insert(body=resource, **kwargs).execute()

def youtube_link(playlist_id):
	return 'https://www.youtube.com/playlist?list='+playlist_id

def main():
	# Create playlist for insertion
	title = 'Instiz Chart ' + time.strftime("%m/%d/%Y")
	description = 'Instiz Chart ranking of songs for ' + time.strftime("%m/%d/%Y")
	privacy_status = 'unlisted'

	playlist_id = create_playlist(
		{'snippet.title':title,
		 'snippet.description':description,
		 'status.privacyStatus':privacy_status},
		 part='snippet,status',
		 onBehalfOfContentOwner='')

	# Convert songs to a song's videoId
	song_video_id_list = []
	for song in get_song_list():
		song_video_id = get_song_id(service,part='snippet',maxResults=1,q=str(song),type='')
		if song_video_id is not None:
			song_video_id_list.append(song_video_id)

	# Insert each song into playlist
	for video_id in song_video_id_list:
		playlist_insert(
			{'snippet.playlistId':playlist_id,
			 'snippet.resourceId.kind':'youtube#video',
			 'snippet.resourceId.videoId':video_id,
			 'snippet.position':''},
			 part='snippet',
			 onBehalfOfContentOwner='')
	# Return youtube playlist link
	print(youtube_link(playlist_id))

if __name__ == '__main__':
	main()


# get sond id
# for song in get_song_list():
# 	get_song_id(service, part='snippet', maxResults=1, q=str(song), type='')

# create playlist
# title = 'Instiz Chart ' + time.strftime("%m/%d/%Y")
# description = 'Instiz Chart ranking of songs for ' + time.strftime("%m/%d/%Y")
# privacyStatus = 'unlisted'
# playlistId = create_playlist(
# 	{'snippet.title':title,
# 	 'snippet.description':description, 
# 	 'status.privacyStatus':privacyStatus},
# 	 part='snippet,status',
# 	 onBehalfOfContentOwner='')
# print_results(playlistId)

# insert items into playlist
