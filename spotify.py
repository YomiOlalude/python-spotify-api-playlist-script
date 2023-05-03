import spotipy
from spotipy.oauth2 import SpotifyOAuth

username = "YOUR_USERNAME"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://open.spotify.com/"
scope = "playlist-modify-private"

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id, 
        client_secret=client_secret, 
        redirect_uri=redirect_uri, 
        scope=scope
        )
    )

spotify_playlists = sp.current_user_playlists()['items']
spotify_playlists_ids = [playlist['id'] for playlist in spotify_playlists]
spotify_playlists_names = [playlist['name'] for playlist in spotify_playlists]

# Get the names of all the playlists from the text file
def get_playlists():
    with open('playlists.txt', 'r') as input_file:
        lines = input_file.readlines()
        genres = []

        for i in range(len(lines)):
            if lines[i].strip() == '---' and i < len(lines) - 1:
                genres.append(lines[i+1].strip())

    return genres

# Count the number of songs in a given genre
def genre_counter(genre):
    with open('playlists.txt', 'r') as input_file:
        count = 0
        lines = input_file.readlines()
        start = lines.index(genre.title() + '\n')

        for line in lines[start + 1:]:
            if line.lower().strip() == '---':
                break

            count += 1
    return count

def get_id_from_name(name, tuple_list):
    result = None
    for tuple in tuple_list:
        if tuple[1] == name:
            result = tuple[0]
            break
    return result

# Create the playlists
for playlist in get_playlists()[::-1]:
    if playlist not in [playlist['name'] for playlist in spotify_playlists]:
      sp.user_playlist_create(user=sp.current_user()['id'], 
                              name=playlist.strip(), 
                              public=False, 
                              description=f'A playlist of my fav {playlist} songs.')

spotify_playlists_ids_and_names = zip(spotify_playlists_ids, spotify_playlists_names)

# Open the file containing the song titles and artist names
with open('playlists.txt') as input_file:
    lines = input_file.readlines()

    for i in range(len(lines)):
        if lines[i].strip() == '---':
            current_playlist_id = get_id_from_name(lines[i+1].strip(), spotify_playlists_ids_and_names)
            continue
        if not ',' in lines[i]:
            print(lines[i])
            continue
        else:
            if lines[i].startswith('***'):
                lines[i] = lines[i][4:]

            song_title, artist_name = lines[i].strip().split(',')

            print(song_title, artist_name)

            search_results = sp.search(q=f'{song_title} {artist_name}', type='track', limit=1)
     
            try:
                track_uri = search_results['tracks']['items'][0]['uri']
                sp.playlist_add_items(playlist_id=current_playlist_id, items=[track_uri])
            except IndexError or TypeError:
                with open('errors.txt', 'a') as output_file:
                    output_file.write('\n' + lines[i])

