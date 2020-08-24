# Python
# PlaylistUpdater class

import sys
import spotipy
import spotipy.util as util
import base64

from datetime import date


playlist_title  = "Better Music Friday"
playlist_desc   = "All of your favorite's new music. No exceptions. " \
                  "If you want to keep this playlist, just change the title. " \
                  "Automatically Generated via Joseph Koetting."
playlist_img    = "cloud.jpg"


class Found(Exception):
    pass


class PlaylistUpdater:

    def __init__(self, user):
        self.user = user
        self.sp = None

        # User Information
        scope = 'user-library-read playlist-modify-private user-follow-read ugc-image-upload playlist-modify-public'

        # Get user
        self.user = "1233486068"  # Joseph Koetting

        token = util.prompt_for_user_token(user,
                                           scope,
                                           client_id='c3296302a21d4ff59d4e6cff9057041d',
                                           client_secret='ebccd31d637441cbbd96503c0fb054b7',
                                           redirect_uri='http://localhost:8888/callback/')
        if token:
            self.sp = spotipy.Spotify(auth=token)
        else:
            print("Can't get token for user:", user)
            print("Exiting...")
            sys.exit()


    @staticmethod
    def __helper_compare_date(release_date):
        ## Spotify sometimes only stores the year -- annoying and why
        try:
            release_date = date.fromisoformat(release_date)
        except ValueError:
            return False

        if abs(date.today() - release_date).days < 7:
            return True
        return False


    def __add_songs_to_playlist(self, playlist_id, songs=None):
        if songs is None: return

        # Clears the playlist
        self.sp.user_playlist_replace_tracks(user=self.user, playlist_id=playlist_id, tracks=[])

        tracks = []
        track_count = 0
        for song in songs:
            tracks.append(song['uri'])
            track_count = track_count + 1

            # you can only add 100 songs per request, while adding remainder
            if track_count == 100 or songs[-1] == song:
                self.sp.user_playlist_add_tracks(user=self.user, playlist_id=playlist_id, tracks=tracks)
                tracks = []
                track_count = 0


    def __create_user_playlist(self):
        playlist = self.sp.user_playlist_create(user=self.user, name=playlist_title, public=True, description=playlist_desc)
        return playlist['id']


    ## may not work if user has more than 50 playlists
    def __update_user_playlist(self, songs=None):
        playlists = self.sp.user_playlists(user=self.user)
        playlist_id = None

        print("LOG: Getting", playlist_title, "playlist id")

        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.user and playlist['name'] == playlist_title:
                playlist_id = playlist['id']
                break

        if playlist_id is None:
            print("LOG:", playlist_title, "playlist not found. Creating...")
            playlist_id = self.__create_user_playlist()

        print("LOG: Updating", playlist_title, "playlist")
        # Add the songs
        self.__add_songs_to_playlist(playlist_id, songs)
        # Refresh the description
        self.sp.user_playlist_change_details(user=self.user, playlist_id=playlist_id, description=playlist_desc)

        print("LOG: Updating Playlist Picture")
        with open(playlist_img, "rb") as img_file:
            playlist_img_b64 = base64.b64encode(img_file.read())
        self.sp.playlist_upload_cover_image(playlist_id=playlist_id, image_b64=playlist_img_b64)


    ## doesnt get all songs in album if over 50
    ## it's a feature not a bug
    def __get_songs_by_album(self, albums=None, artists=None):
        songs = []

        print("LOG: Getting songs per Album")

        # Filters out content would probably prefer to still have
        # but too annoying to fix. Wish I could just do a sql stmt on database
        for album in albums:
            # skip all compilations they are bad
            if not album['album_type'] == "compilation" and not album['album_group'] == "appears_on":
                songs = songs +  self.sp.album_tracks(album['uri'])['items']

        print("LOG: Returning songs per Album")
        return songs


    def __get_albums_by_artist(self, artists):
        recent_albums = []

        print("LOG: Getting Followed Artists new Albums")

        for artist in artists:
            # Gets only albums from US
            albums = self.sp.artist_albums(artist_id=artist['uri'], country="US")['items']

            ## Apparently you can be an artist without any albums
            if albums is None:
                break

            for album in albums:
                ## Filter Albums by release date (date < 7 days)
                if self.__helper_compare_date(album['release_date']):
                        recent_albums.append(album)

        print("LOG: Returning Followed Artists new Albums")
        return recent_albums


    def __get_followed_artists(self):
        followed_artists = []
        followed_after = None

        print("LOG: Getting Followed Artists")

        # If doesnt follow any artists
        # NOTE: Spotify will give you a wrong total number if you follow over 1,000 artists
        if (self.sp.current_user_followed_artists(limit=1, after=followed_after)['artists']['total']) == 0:
            print("User Follows no Playlists")
            return None

        while True:

            followed_info = self.sp.current_user_followed_artists(limit=50, after=followed_after)
            items = followed_info['artists']['items']
            followed_artists = followed_artists + items

            # check if added all follow artists
            if len(items) < 50:
                break

            followed_after = items[len(items) - 1]['id']

        print("LOG: Returning Followed Artists")
        return followed_artists


    def update(self):
        # noinspection PyBroadException
        # try:
            print("LOG: Beginning Update")
            print("LOG: This may take 1-4 minutes")
            followed_artists = self.__get_followed_artists()
            new_albums = self.__get_albums_by_artist(artists=followed_artists)
            new_songs = self.__get_songs_by_album(albums=new_albums, artists=followed_artists)
            self.__update_user_playlist(songs=new_songs)
            print("LOG: Finished Update")
        # except:
            print("LOG: Unexpected Error occurred. Please Fix")
            print("LOG: ERROR:", sys.exc_info()[0])