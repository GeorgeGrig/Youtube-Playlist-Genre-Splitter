# Youtube-Playlist-Genre-Splitter  
Split Youtube playlists based on song genre.  

# INSTRUCTIONS  
1.Install dependencies.  
2.Create a file named creds.json and populate the values with the following structure  
`
{
    "YT_API_KEY": "your youtube api key here",
    "PLAYLISTS":{
        "playlist1": "playlist id",
        "playlist2": "playlist id"},
    "GENIUS_CLIENT_ACCESS_TOKEN": "your genius client access token here"
}
`   
3.Get your client secret [oauth 2](https://developers.google.com/sheets/api/guides/authorizing) for google sheets and rename it 'client_secret.json'  
4.Get your client secret [oauth 2](https://developers.google.com/youtube/registering_an_application) from youtube api (in scopes you need 'https://www.googleapis.com/auth/youtube.force-ssl') and rename it 'client_secret_youtube.json'.  

# Usage  
Choose either to split a playlist in it's genres or to create a playlist based on those genres.  
Follow in-console instrucions.  
Note that Genius API is imperfect and sometimes genre cannot be found (especially for non-lyric songs), however, you can manually add genres on the google sheet before creating the final genre-based playlist.  

# Other  
Why not use *only* the Genius API to get genres? When this script was first created Genius API did not include genres.  
Why not use another API? Considering the limitations of other APIs when this script was first created Genius API seemed like the simpler and more robust choice.  
A future implementation should include multithreading because currently it takes a really long time for really big playlists.  
