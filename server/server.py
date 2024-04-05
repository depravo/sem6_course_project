import json
import time
import pytz
import requests

from flask import Flask, request, jsonify
from spotipy import oauth2

from rec_system import *
from DBHelper import *

app = Flask(__name__)
Session = sessionmaker(bind=engine)
rs = RecommendationSystem()

@app.route("/")
def showHomePage():
    return "This is home page"


def checkCredentials(username, password=None):
    if password is None:
        with Session() as session:
            results = session.query(User).filter(User.login == username).all()
        if len(results) > 0:
            return -1
        else:
            return 0
    else:
        with Session() as session:
            results = session.query(User).filter(and_(User.login == username, User.password == password)).all()
        if len(results) != 1:
            return -1
        else:
            return results[0].id


def addUser(username, password):
    user = User(login=username, password=password)
    with Session() as session:
        session.add(user)
        max_id = session.query(func.max(User.id)).first()
        session.commit()
    return max_id[0]


def getUserPlaylist(user_id):
    with Session() as session:
        links = session.query(Link.song_id, Link.added_at).filter(Link.user_id == user_id).all()

        song_ids = []
        for link in links:
            song_ids.append((link.song_id, link.added_at))

        song_list = []
        for song_id, date_added in song_ids:
            song = session.query(Song).filter(Song.id == song_id).one()
            song_dict = {'id': song.id, 'name': song.name, 'artist': song.artist, 'url': song.logoResource, 'date_added': datetime.strptime(date_added,"%Y-%m-%d %H:%M:%S%z")}
            song_list.append(song_dict)

        playlist = pd.DataFrame(song_list)
        return playlist

@app.route("/addSong", methods=["POST"])
def addSongToPlaylist():
    user_id = request.json.get('userId')
    song_name = request.json.get('songName')
    now = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S%z")
    added_at = now[:-2] + ':' + now[-2:]
    with Session() as session:
        song_id = session.query(Song).filter(Song.name == song_name).first().id
        link = Link(user_id=user_id, song_id=song_id, added_at=added_at)
        if session.query(Link).filter_by(user_id=user_id, song_id=song_id).first() is not None:
            response = {'success': False, 'message': 'Song has been already added!'}
            return response
        session.add(link)
        session.commit()
    response = {'success': True, 'message': 'Song added successful!'}
    return response

@app.route("/getSongsByName", methods=["POST"])
def getSongsByName():
    substring = request.json
    song_list = []
    with Session() as session:
        songs = session.query(Song).filter(Song.name.like(f'%{substring}%')).all()
        for song in songs:
            song_dict = {'name': song.name, 'artist': song.artist, 'logoResource': song.logoResource}
            if song_dict['logoResource'] is None:
                song_dict['logoResource'] = "https://i.scdn.co/image/ab67616d0000b2736a1a23328cbd43ad75829e90"
            song_list.append(song_dict)
    return json.dumps(song_list)

@app.route("/signIn", methods=["POST"])
def signIn():
    username = request.json.get('username')
    password = request.json.get('password')
    current_user_id = checkCredentials(username=username, password=password)

    if current_user_id != -1:
        response = {'success': True, 'message': 'Login successful!', 'userId': current_user_id}
    else:
        response = {'success': False, 'message': 'Invalid username or password.', 'userId': None}
    return jsonify(response)


@app.route("/register", methods=["POST"])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if checkCredentials(username=username) == -1:
        response = {'success': False, 'message': 'User with same name already exists.', user_id: None}
    else:
        current_user_id = addUser(username=username, password=password)
        response = {'success': True, 'message': 'Register and login successful!', 'userId': current_user_id}
    return jsonify(response)


@app.route("/playlist", methods=["POST"])
def getPlaylist():
    user_id = request.json
    playlist = getUserPlaylist(user_id)
    songs = playlist[["name", "artist", "url"]]
    song_data = songs.rename(columns={'url': 'logoResource'})
    response = song_data.to_json(orient="records")
    return response

@app.route("/recommendations", methods=["POST"])
def getRecommendations():
    user_id = request.json
    playlist = getUserPlaylist(user_id)
    recs = rs.generate_playlist_recos(playlist, 10)
    pd.set_option("display.max_columns", None)
    songs = recs[["name", "artists", "url"]]
    song_data = songs.rename(columns={'artists': 'artist', 'url': 'logoResource'})
    response = song_data.to_json(orient="records")
    return response

app.run(host='0.0.0.0', port=5000)
# pl = getUserPlaylist(1)
# print(rs.generate_playlist_recos(pl, 10))
# auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
# sp = spotipy.Spotify(auth_manager=auth_manager)
#
# AUTH_URL = 'https://accounts.spotify.com/api/token'
#
# auth_response = requests.post(AUTH_URL, {
#     'grant_type': 'client_credentials',
#     'client_id': client_id,
#     'client_secret': client_secret,
# })
#
# auth_response_data = auth_response.json()
# access_token = auth_response_data['access_token']
# headers = {
#     'Authorization': 'Bearer {token}'.format(token=access_token)
# }
#
# BASE_URL = 'https://api.spotify.com/v1/'
#
# with Session() as session:
#     for ix, row in rs.spotify_df.iterrows():
#         # Retrieve the song ID from the current row
#         if ix >= 104725:
#             time.sleep(0.5)
#             song_id = row['id']
#
#         # Query the Song table for a row with the matching song ID
#             song = session.query(Song).filter(Song.id == song_id).first()
#
#         # If a matching row is found, update the logoResource attribute with the value from the playlist DataFrame
#             if song is not None:
#                 #track_info = sp.track(song_id)
#                 r = requests.get(BASE_URL + 'tracks/' + song_id, headers=headers)
#                 print(r)
#                 track_info = r.json()
#                 if track_info['album']['images']:
#                     song.logoResource = track_info['album']['images'][0]['url']
#                 else:
#                     song.logoResource = None
#                 session.commit()
#         print(ix)