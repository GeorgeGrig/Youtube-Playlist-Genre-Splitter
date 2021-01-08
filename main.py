#INSTRUCTIONS
# 1.Install dependencies
# 2.Create a file named creds.json and populate the values with the following structure
#{
#    "YT_API_KEY": "your youtube api key here",
#    "PLAYLISTS":{
#        "playlist1": "your playlist id here",
#        "playlist2": "your playlist id here"} 
#}
# 3.Get your Youtube api key from Google APIs
# 4.Get your Google Drive client_secret.json from Google APIs
# 5.Share your target document with the email address found on your client_secret.json under "client_email"

import json
import gspread
from gspread.models import Cell
import os
import time
import sys
import subprocess
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import lyricsgenius
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from youtube import addVideoToPlaylist,createPlaylist,authorizeUser

#Get credentials and value init
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
options = Options()
options.headless = True

with open("creds.json", "r") as read_file:
    data = json.load(read_file)

genius = lyricsgenius.Genius(data["GENIUS_CLIENT_ACCESS_TOKEN"])
youtube = build('youtube', 'v3', developerKey=data["YT_API_KEY"])

#Fetch all playlist entries using the youtube api
def fetch_all_youtube_videos(playlistId):
    res = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlistId,
    maxResults="50"
    ).execute()

    nextPageToken = res.get('nextPageToken')
    while ('nextPageToken' in res):
        nextPage = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlistId,
        maxResults="50",
        pageToken=nextPageToken
        ).execute()
        res['items'] = res['items'] + nextPage['items']

        if 'nextPageToken' not in nextPage:
            res.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']
    #return a clean entry title & url list
    title_list = []
    url_list = []
    stopwords = ['1.','2.','3.','6.','4.','5.','7.','8.','9.','10.','[',']','(',')','Extented','ᴴᴰ','- Lyrics','Official Audio','VÍDEO','HD','Audio','audioΑ','with lyrics','Explicit','OFFICIAL VIDEO','Official Audio','official video','Official Video','Official Video', 'with lyrics', 'lyrics','official music video','Official Music Video','Official music Video','Official Music video','Official Video']
    for video in res["items"]:
        title = video.get('snippet')['title'].lower()
        for word in stopwords:
            title = title.replace(word.lower(),"")
        title_list.append(title.strip())
        url_local = video.get('snippet')['resourceId']['videoId']
        url_list.append('https://www.youtube.com/watch?v='+url_local)
    title_list.reverse()
    url_list.reverse()
    return title_list,url_list


#Add data to the sheet
def write_sheet(videos,urls,genres):
    i = 2
    n = 0
    cells = []
    for video in videos:
        try:
            cells.append(Cell(i, 1, video))
            cells.append(Cell(i, 2, urls[n]))
            cells.append(Cell(i, 3, genres[n]))
            i+=1
            n+=1
        except:
            print('**FAILED**')
    sheet.update_cells(cells)

#Use genius api and genius website to get song genre
def get_song_info(titles):
    genres = []
    l = 0
    for title in titles:
        l += 1
        if round((len(titles) - l)/60) != 0:
            print('\rFinding genre (',l,'/',len(titles),"). Time remaining: ",round((len(titles) - l)/60)," hours        ", end='', flush=True) 
        else:           
            print('\rFinding genre (',l,'/',len(titles),"). Time remaining: ",len(titles) - l," mins            ", end='', flush=True)
        z = 1
        #supressing output of genius api
        stdout = sys.stdout 
        stderr = sys.stderr 
        devnull = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = devnull
        sys.stderr = devnull
        info = genius.search_song(title)
        sys.stdout = stdout
        sys.stderr = stderr
        if info == 'None' or info is None:
            genres.append("Couldn't find genre")
        else:
            url = info.url.strip("'")
            while z <= 15: 
                try:
                    driver = webdriver.Firefox(options=options)
                    driver.get(url)
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    driver.implicitly_wait(3)
                    genre = driver.find_element_by_class_name("metadata_with_icon-tags").text
                    driver.quit()
                    break
                except:
                    z +=1
                    driver.quit()
                    genre = "Couldn't find genre"
            genres.append(genre)           
    print('\nDone getting genres')
    return genres

if __name__ == '__main__':
    option = input('To get genres from youtube playlist press 0 to create playlists based on genre press 1: ')
    if option == '0':
        playlists = data["PLAYLISTS"].values()
        i = 0
        for playlist in playlists:
            sheet = client.open("PlaylistGenre").get_worksheet(i) #This sheet needs to be shared with the account that we are using 
            print('Getting song names and video urls from playlist...')
            videos_names,videos_urls = fetch_all_youtube_videos(playlist)
            genres = get_song_info(videos_names)
            print('Writing data to the sheet...')
            write_sheet(videos_names,videos_urls,genres)
            i += 1
    elif option == '1':
        print('Getting unique genres...')
        sheet = client.open("PlaylistGenre").get_worksheet(0)
        values_list = sheet.col_values(3)
        csv_values = ",".join(values_list)
        csv_values = csv_values.split(",")
        csv_values = [i.strip() for i in csv_values]
        unique_genres = set(csv_values)
        unique_genres.remove('Genre')
        unique_genres.remove("Couldn't find genre")
        genre = input(f'Choose one of the following genres: {unique_genres} ')
        k = 0
        indexes = []
        while k < len(values_list):
            if genre.lower() in values_list[k].lower():
                indexes.append(k)
            k+=1
        target_videoIDs = []
        print('You need to authorize this application in order to continue')
        #authorize
        youtube_auth = authorizeUser()
        #create playlist
        print('Creating playlist...')
        name = 'Created by genre splitter based on genre: ' + genre
        playlist_id = createPlaylist(name,youtube_auth)
        l = 1
        for index in indexes:
            print ('Finding genre (',l/len(indexes),")         \r",)
            video_id = sheet.cell(index+1, 2).value.split('https://www.youtube.com/watch?v=')[1]
            target_videoIDs.append(video_id)
            addVideoToPlaylist(video_id,playlist_id,youtube_auth)
            l += 1
        print(target_videoIDs)