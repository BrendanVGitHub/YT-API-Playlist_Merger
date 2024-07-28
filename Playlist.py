# -- coding: utf-8 --

# Sample Python code for youtube.playlists.delete
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python
from flask import Flask, render_template, request 

import os

import google_auth_oauthlib.flow
#pip install googleauth, googleapi
#pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
import googleapiclient.discovery
import googleapiclient.errors
import pandas

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

app = Flask(__name__, template_folder='templates')


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # DO NOT leave this option enabled in production.
    #this is currently set to disabled - ran locally
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_p.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    global youtube
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


    request = youtube.playlists().list(
        part="snippet, status",
        mine=True,
        maxResults=50,

    )
    response = request.execute()


    playlist_info = {}
    #function to grab playlists from current YT Channel and add to dictionary by request
    sorting(response, playlist_info)

    print(pandas.DataFrame(playlist_info.items(), columns=['Playlist Name', 'ID']))
    #print(playlist_info)
    

    #user input for playlist to add to
    Play_ID = input("Current Playlist ID:")

    #call function with user input and verify playlist ID
    combine_playlist(Play_ID)

#function to get video IDs with Channel IDs in Playlist
def VideoIDList(Video_Block):
    blocks = Video_Block["items"]
    videoidlist = []

    #CID_VID = {channel_id:[]}
    CID_VID = {}

    #for loop to iterate through data blocks and pull out video ID and channel ID tag and put into a dictionary
    for item in blocks:

        vidid = item['contentDetails']['videoId']
        vidOCID = item['snippet']['videoOwnerChannelId']
        videoidlist.append(vidid)
        if vidOCID not in CID_VID.keys():
            CID_VID[vidOCID] = [vidid]

        else:
            CID_VID[vidOCID].append(vidid)

    #print(pandas.DataFrame(playlist_info.items(), columns=['Playlist Name', 'ID']))
    return CID_VID

#insert videos by Channel into playlist function
def insert_video(PID, VID):
    #count = len(VID)
    #for loop to go through Video IDs in list and insert into Current playlist
    for ID in VID:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": PID,
                    "position": 0,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": ID
                    }
                }
            }
        )
        response = request.execute()
        
        print("Successfully Added Video:", response['snippet']['title'], "-", response['snippet']['videoOwnerChannelTitle'])

def sorting(data,playlist_info):

    #print(len(data["items"])) -->50 playlists
    blocks = data["items"]

    for item in blocks:
        playid = item['id']
        snippet = item['snippet']
        title = snippet['title']
        #print(title, playid)
        playlist_info[title] = playid
    return playlist_info

#function to request playlist B information - videos
def playlistvideo_info(playid):

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=playid
    )
    response = request.execute()
    return response
    #print(response)

def combine_playlist(Play_ID):
    current_PID = Play_ID
    playlist_B = input("Merging Out Playlist ID:")
    #Condition = input("which one?") - list conditions
    condition = "channel"
    if condition == "channel":

        #function to search playlist B for a channel with the channel ID
        Videos = playlistvideo_info(playlist_B)
        # print("Videos:", Videos)
        ChannelID_VID = VideoIDList(Videos)
        # print(ChannelID_VID)
        playlist_channels_id = playlist_channels(Videos)
        #print(playlist_channels_id)
        pdata = playlist_channels_id
        print(pandas.DataFrame(playlist_channels_id.items(), columns=['Channel', 'ID']))
        #search_playlist()

        @app.route('/')
        def dis_playlist():
            return render_template('index.html', pdata=pdata)
        app.run()


        channel_id = input("Channel ID To Move?:")
        if channel_id in ChannelID_VID.keys():
            #VID = ChannelID_VID[channel_id]
            insert_video(current_PID, ChannelID_VID[channel_id])


#function to request list of channel titles and IDs
def playlist_channels(Video_Block):
    blocks = Video_Block["items"]

    channel_ids_titles = {}
    for item in blocks:
        # print(item['contentDetails']['videoId'])
        vidOCID = item['snippet']['videoOwnerChannelId']
        vidOCT = item['snippet']['videoOwnerChannelTitle']
        channel_ids_titles[vidOCT] = vidOCID
    return channel_ids_titles

main()