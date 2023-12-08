#!/usr/bin/env python3
"""

"""
__author__ = "Bradley Engel"
__version__ = "0.1.0"

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

# global variable defs

def get_playlist_urls(api_info, playlists):
    # variable creation
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

    # read only
    # read_creds = Credentials.from_authorized_user_info(api_info, r_scope)
    # read_service = build("youtube", "v3", credentials=read_creds)

    # authenticate
    creds = Credentials.from_authorized_user_info(api_info, rw_scope)
    service = build("youtube", "v3", credentials=creds)

    # get ids of videos to download
    for playlist in from_playlists:
        request = service.playlistItems().list(part = "contentDetails", playlistId = playlist)
        response = request.execute()

    # populate vdeo_ids variable
    for item in response.get('items'):
        video_ids.append(item.get('contentDetails').get('videoId'))
        playlist_item_ids.append(item.get('id'))

    if playlist_processing == "Copy" or playlist_processing == "Move":
        # add videos to completed playlist
        for video in video_ids:
            body = {
                "snippet": {
                    "playlistId": to_playlist,
                    "position": 0,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video
                    }
                }
            }
            request = service.playlistItems().insert(part = "snippet", body = body)
            request.execute()

    if playlist_processing == "Move":
        for id in playlist_item_ids:
            # remove video from "from_playlists"
            request = service.playlistItems().delete(id = id)
            response = request.execute()
    
    return video_ids

def create_nfos(days):
    info_files = []
    for root, dirs, files in os.walk('/youtube'):
        for file in files:
            # if the file has a json extension and has been modified in the last 'nfo_create_since_days' days, get that info
            if file.endswith('.json'):
                print(file)
                print(os.stat(root + '/' + file).st_mtime)
                if os.stat(root + '/' + file).st_mtime > time.time() - days * 86400:
                    info_files.append(root + '/' + file)

    for i in range(len(info_files)):
        nfo = ytdl_nfo.Ytdl_nfo(info_files[i])
        nfo.process()
        nfo.write_nfo()

def main(args):
    """ Main entry point of the app """
    # print("this is a script to automate the download of youtube videos")
    
    # open config file
    config = yaml.safe_load(open(args.config))

    # info for api calls
    api_info = config.get('api')

    # get playlists
    playlists = config.get('playlists')

    # get playlist ids
    video_ids = get_playlist_urls(api_info, playlists)

    # make URLs
    URLs = []
    URL_prefix = 'https://youtube.com/watch?v='
    for id in video_ids:
        URLs.append(URL_prefix + id)

    # create useful variables
    ytdl = config.get('ytdl')
    opts = ytdl.get('opts')
    pp = ytdl.get('postprocessors')

    ydl_opts = {}

    # get ffmpeg path and make sure it works
    for root, dirs, files in os.walk('/'):
        for file in files:
            if file.endswith('mpeg'):
                ffmpeg = root+'/'+file

    if subprocess.run([ffmpeg, '-version'], stdout=subprocess.PIPE).returncode == 0:
        print('ffmpeg works')
    else:
        print('ffmpeg does not work')

    # add ffmpeg location to ydl_opts
    ydl_opts.update({'ffmpeg_location':ffmpeg})

    # populate ydl_opts
    for i in opts:
        if isinstance(i, str):
            # print("Updating ydl_opts with" + i)
            ydl_opts.update({i:"True"})
        elif isinstance(i, dict):
            if i.get('outtmpl'):
                outtmpl = '/youtube/'+i.get('outtmpl')
                i.update({'outtmpl':outtmpl})
            # print("i am a dict")
            ydl_opts.update(i)
            # if the variable is output, append the correct file structure
        else:
            print("I don't know what I am")

    # create postprocessor list
    postprocessors = []

    # create postprocessor dictionaries
    for key in pp.keys():
        key_dict = {}
        key_dict.update({'key':key})
        for subkey in pp.get(key):
            key_dict.update({subkey:pp.get(key).get(subkey)})
        postprocessors.append(key_dict)

    # update ydl_opts with postprocessors
    ydl_opts.update({'postprocessors':postprocessors})

    print(ydl_opts)

    # download videos
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(URLs)

    # create NFOs
    if config.get('other').get('nfo_creation') and config.get('other').get('nfo_create_since_days'):
        create_nfos(config.get('other').get('nfo_create_since_days'))
    
    # move videos to new playlist

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", action="store", dest="config")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
