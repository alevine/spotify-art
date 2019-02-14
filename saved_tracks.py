import sys
import json
import os
import glob
import argparse
import spotipy
import spotipy.util as util
from retrying import retry
import plot_art

SCOPE_LIBRARY = 'user-library-read'
SCOPE_PLAYLIST= 'playlist-read-private playlist-read-collaborative'


def parse_item(item):
    """Parses an item from the Spotify results JSON.

    Given a JSON object, obtains the necessary fields from it such as the
    artists, the song name, and the album name.

    Arguments:
      item {JSON Object} -- the JSON song result
    """
    track = item['track']
    artists = [artist['name'] for artist in track['artists']]
    name = track['name']
    album = track['album']['name']
    # release date is YYYY-MM-DD, get only YYYY
    year = track['album']['release_date'][0:4]
    img = track['album']['images'][0]['url']

    return {'artists': artists, 'name': name, 'album': album, 'year': year, 'img': img}


def reduce_to_albums(song_json):
    album_song_count = {}
    for song in song_json:
        album = song['album']
        year = song['year']
        img = song['img']
        if album not in album_song_count:
            album_song_count[album] = (year, img, 1)
        else:
            album_song_count[album] = (
                year, img, album_song_count[album][2] + 1)
    album_song_count = {
        k: v for (k, v) in album_song_count.items() if v[2] != 1}
    return album_song_count


def get_tracks_from_library(sp):
    """Gets all saved tracks from a user's library.

    Polls 5k songs from a user's library to return for saving.

    Returns:
        list -- list of songs!
    """
    total_list = []
    for i in range(0, 5000, 50):
        results = sp.current_user_saved_tracks(limit=50, offset=i)
        for item in results['items']:
            json_obj = parse_item(item)
            total_list.append(json_obj)
    return total_list

def get_tracks_from_playlists(sp, username):
    """Gets all saved tracks from a user's playlists.

    Gets songs from playlists instead of library, may need work.

    Arguments:
        sp {Spotify Object} -- spotify API object
        user {string} -- the user

    Returns:
        list -- list of songs
    """
    playlists = sp.current_user_playlists()
    total_list = []
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            results = get_results(sp, username, playlist)
            tracks = results['tracks']
            for item in tracks['items']:
                json_obj = parse_item(item)
                total_list.append(json_obj)
    return total_list

@retry
def get_results(sp, username, playlist):
    return sp.user_playlist(username, playlist['id'], fields='tracks')

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # remove cached auth files each time
    for fl in glob.glob(dir_path + "/.cache-*"):
        os.remove(fl)

    parser = argparse.ArgumentParser(
        description='Gets a users saved tracks, either from playlists or library.')
    parser.add_argument('-u', '--user', type=str, required=True,
                        help='username to poll from')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--playlists', action='store_true',
                       help='poll from user\'s playlists for songs')
    group.add_argument('-l', '--library', action='store_true',
                       help='poll from user\'s library for songs')

    args = parser.parse_args()

    username = args.user
    playlist = args.playlists
    library = args.library

    used_scope = SCOPE_LIBRARY if library else SCOPE_PLAYLIST + f' {SCOPE_LIBRARY}'

    token = util.prompt_for_user_token(username, used_scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        if library:
            total_list = get_tracks_from_library(sp)
        elif playlist:
            total_list = get_tracks_from_playlists(sp, username)
        with open('albums.json', 'w') as output:
            json.dump(reduce_to_albums(total_list), output)
            output.close()
        plot_art.main(['-a', 'albums.json'])
    else:
        print(f"Can't get token for {username}")


if __name__ == '__main__':
    main()
