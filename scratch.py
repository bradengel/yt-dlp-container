import yt_dlp
import ytdl_nfo
import yaml
import os
import subprocess
import time
import argparse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from logzero import logger

config = yaml.safe_load(open('yt.yaml'))

api_info = config.get('api')

if api_info.get('token') in ("$TOKEN", ""):
    api_info.update({'token': os.environ['TOKEN']})

if api_info.get('refresh_token') in ("$REFRESH", ""):
    api_info.update({'refresh_token': os.environ['REFRESH']})

if api_info.get('client_id') in ("$ID", ""):
    api_info.update({'client_id': os.environ['ID']})

if api_info.get('client_secret') in ("$SECRET", ""):
    api_info.update({'client_secret': os.environ['SECRET']})

playlists = config.get('playlists')

video_ids = []
playlist_item_ids = []
r_scope = []
rw_scope = []

# variable population
scopes = api_info.pop('scopes')
r_scope.append(scopes.get('read_only'))
rw_scope.append(scopes.get('update'))
from_playlists = playlists.get('from_id')
to_playlist = playlists.get('to_id')
playlist_processing = playlists.get('playlist_processing')

creds = Credentials.from_authorized_user_info(api_info, rw_scope)
service = build("youtube", "v3", credentials=creds)

request = service.playlistItems().list(part = "contentDetails", playlistId = from_playlists[0])

response = request.execute()