import sys
import json
import requests
import spotipy
import spotipy.util as util
import plot_art

SCOPE = 'user-library-read'


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
            album_song_count[album] = (year, img, album_song_count[album][2] + 1)
    album_song_count = {k: v for (k, v) in album_song_count.items() if v[2] != 1}
    return album_song_count


def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print(f"Usage: {sys.argv[0]} username")
        sys.exit()

    token = util.prompt_for_user_token(username, SCOPE)

    if token:
        sp = spotipy.Spotify(auth=token)
        total_list = []
        for i in range(0, 4000, 50):
            results = sp.current_user_saved_tracks(limit=50, offset=i)
            for item in results['items']:
                json_obj = parse_item(item)
                total_list.append(json_obj)
        with open('albums.json', 'w') as output:
            json.dump(reduce_to_albums(total_list), output)
            output.close()
        plot_art.main(['-a', 'albums.json'])
    else:
        print(f"Can't get token for {username}")


if __name__ == '__main__':
    main()
