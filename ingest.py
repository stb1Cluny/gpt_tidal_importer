import simplejson as json

#old bad
#song, artist = simplejson.read("songs.json") # needs selector; might move to main

#dict of tuples?
def read_songs_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    songs = data['SONGS']
    song_artist_pairs = [(song['title'], song['artist']) for song in songs]
    
    return song_artist_pairs
