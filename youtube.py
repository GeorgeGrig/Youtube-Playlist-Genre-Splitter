import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def authorizeUser():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_youtube.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    return youtube

def addVideoToPlaylist(videoId,playlistId,youtube):
    try:
        playlist_insert_response = youtube.playlistItems().insert(
        part="snippet",

        body={
            'snippet': {
                'playlistId': playlistId,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': videoId
                },
                'position': 0
            }
        }
    ).execute()

    except:
        print('EH')

def createPlaylist(name,youtube):
    res = youtube.playlists().insert(
        part="snippet",
        body={
            'snippet': {
                'title': name}}
    ).execute()
    return res['id']