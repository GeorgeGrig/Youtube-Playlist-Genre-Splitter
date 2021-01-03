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
#Get credentials and value init
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
options = Options()
options.headless = True

with open("creds.json", "r") as read_file:
    data = json.load(read_file)
genius = lyricsgenius.Genius(data["GENIUS_CLIENT_ACCESS_TOKEN"])

#Fetch all playlist entries using the youtube api
def fetch_all_youtube_videos(playlistId):
    youtube = build('youtube', 'v3', developerKey=data["YT_API_KEY"])
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
    stopwords = ['.','1.','2.','3.','6.','4.','5.','7.','8.','9.','10.','(audio)','- Lyrics','(VÍDEO)','Official Audio','[',']','(',')','HD','Audio','with lyrics','Explicit','OFFICIAL VIDEO','Official Audio','official video','Official Video','Official Video', 'with lyrics', 'lyrics','official music video','Official Music Video','Official music Video','Official Music video','Official Video']
    for video in res["items"]:
        title = video.get('snippet')['title']
        for word in stopwords:
            title = title.replace(word,"")
        title_list.append(title.rstrip())
        url_local = video.get('snippet')['resourceId']['videoId']
        url_list.append('https://www.youtube.com/watch?v='+url_local)
    title_list.reverse()
    url_list.reverse()
    return title_list,url_list

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

def get_song_info(titles):
    genres = []
    for title in titles:
        z = 1
        info = genius.search_song(title)
        if type(info) == 'NoneType':
            z = 5
            genres.append("Couldn't find genre")
        url = info.url.strip("'")
        print("Getting genre info from url")
        while z <= 4: 
            try:
                print("Try no: ",z)
                driver = webdriver.Firefox(options=options)
                driver.get(url)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(3)
                genre = driver.find_element_by_class_name("metadata_with_icon-tags").text
                driver.quit()
                genres.append(genre)
                break
            except:
                z +=1
                driver.quit()
                if z >= 4:
                    genre = "Couldn't find genre"
                    genres.append(genre)
    return genres



if __name__ == '__main__':
    playlists = data["PLAYLISTS"].values()
    i = 0
    for playlist in playlists:
        sheet = client.open("PlaylistGenre").get_worksheet(i) #which already shared google sheet to access
        videos_names,videos_urls = fetch_all_youtube_videos(playlist)
        genres = get_song_info(videos_names)
        i += 1