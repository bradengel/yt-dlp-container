#!/usr/bin/env python3
"""
To Do:
- Move videos from one playlist to another
- add arugements for config file and verbosity
- add logging to stdout
"""
import yt_dlp
import ytdl_nfo
import yaml
import os
import subprocess
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# global variable defs

def get_playlist_urls(user_info, scopes, playlists):
    # authenticate
    creds = Credentials.from_authorized_user_info(user_info, scopes)

    service = build("youtube", "v3", credentials=creds)

    # get ids of videos to download
    ids = []
    for playlist in playlists:
        request = service.playlistItems().list(part = "contentDetails", playlistId = playlist)
        response = request.execute()
    
    # get video ids
        for item in response.get('items'):
            ids.append(item.get('contentDetails').get('videoId'))

    return ids

def create_nfos(other):
    info_files = []
    for root, dirs, files in os.walk('/youtube'):
        for file in files:
            # if the file has a json extension and has been modified in the last 'nfo_create_since_days' days, get that info
            if file.endswith('.json'):
                print(file)
                print(os.stat(root + '/' + file).st_mtime)
                if os.stat(root + '/' + file).st_mtime > time.time() - other.get('nfo_create_since_days') * 86400:
                    info_files.append(root + '/' + file)

    for i in range(len(info_files)):
        nfo = ytdl_nfo.Ytdl_nfo(info_files[i])
        nfo.process()
        nfo.write_nfo()

def main():
    """ Main entry point of the app """
    # print("this is a script to automate the download of youtube videos")
    
    # open config file 
    config = yaml.safe_load(open('yt.yaml'))

    # info for api calls
    user_info = config.get('api')
    
    # get scopes
    scopes = user_info.pop('scopes')

    # get playlists
    playlists = config.get('playlist').get('from_id')

    # get playlist ids
    video_ids = get_playlist_urls(user_info, scopes, playlists)

    # make URLs
    URLs = []
    for id in video_ids:
        URLs.append('https://youtube.com/watch?v=' + id)

    print(URLs)

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
    main()

