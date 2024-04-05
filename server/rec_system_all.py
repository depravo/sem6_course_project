import pandas as pd
import numpy as np
import json
import re
import sys
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from skimage import io
import matplotlib.pyplot as plt

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util

# Read data
spotify_df = pd.read_csv('data.csv')
data_w_genre = pd.read_csv('data_w_genres.csv')

# Data exploration/preparation
data_w_genre['genres_upd'] = data_w_genre['genres'].apply(
    lambda x: [re.sub(' ', '_', i) for i in re.findall(r"'([^']*)'", x)])
spotify_df['artists_upd_v1'] = spotify_df['artists'].apply(lambda x: re.findall(r"'([^']*)'", x))

spotify_df['artists_upd_v2'] = spotify_df['artists'].apply(lambda x: re.findall('\"(.*?)\"', x))
spotify_df['artists_upd'] = np.where(spotify_df['artists_upd_v1'].apply(lambda x: not x), spotify_df['artists_upd_v2'],
                                     spotify_df['artists_upd_v1'])

# need to create my own song identifier because there are duplicates of the same song with different ids. I see different
spotify_df['artists_song'] = spotify_df.apply(lambda row: row['artists_upd'][0] + row['name'], axis=1)
spotify_df.sort_values(['artists_song', 'release_date'], ascending=False, inplace=True)

spotify_df.drop_duplicates('artists_song', inplace=True)

artists_exploded = spotify_df[['artists_upd', 'id']].explode('artists_upd')

artists_exploded_enriched = artists_exploded.merge(data_w_genre, how='left', left_on='artists_upd', right_on='artists')
artists_exploded_enriched_nonnull = artists_exploded_enriched[~artists_exploded_enriched.genres_upd.isnull()]

artists_genres_consolidated = artists_exploded_enriched_nonnull.groupby('id')['genres_upd'].apply(list).reset_index()
artists_genres_consolidated['consolidates_genre_lists'] = artists_genres_consolidated['genres_upd'].apply(
    lambda x: list(set(list(itertools.chain.from_iterable(x)))))

spotify_df = spotify_df.merge(artists_genres_consolidated[['id', 'consolidates_genre_lists']], on='id', how='left')

# Feature engineering
spotify_df['year'] = spotify_df['release_date'].apply(lambda x: x.split('-')[0])
float_cols = spotify_df.dtypes[spotify_df.dtypes == 'float64'].index.values
ohe_cols = 'popularity'

# create 5 point buckets for popularity
spotify_df['popularity_red'] = spotify_df['popularity'].apply(lambda x: int(x / 5))

# tfidf can't handle nulls so fill any null values with an empty list
spotify_df['consolidates_genre_lists'] = spotify_df['consolidates_genre_lists'].apply(
    lambda d: d if isinstance(d, list) else [])


# simple function to create OHE features
# this gets passed later on
def ohe_prep(df, column, new_name):
    """
    Create One Hot Encoded features of a specific column

    Parameters:
        df (pandas dataframe): Spotify Dataframe
        column (str): Column to be processed
        new_name (str): new column name to be used

    Returns:
        tf_df: One hot encoded features
    """

    tf_df = pd.get_dummies(df[column])
    feature_names = tf_df.columns
    tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
    tf_df.reset_index(drop=True, inplace=True)
    return tf_df


# function to build entire feature set
def create_feature_set(df, float_cols):
    """
    Process spotify df to create a final set of features that will be used to generate recommendations

    Parameters:
        df (pandas dataframe): Spotify Dataframe
        float_cols (list(str)): List of float columns that will be scaled

    Returns:
        final: final set of features
    """

    # tfidf genre lists
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['consolidates_genre_lists'].apply(lambda x: " ".join(x)))
    genre_df = pd.DataFrame(tfidf_matrix.toarray())
    genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names()]
    genre_df.reset_index(drop=True, inplace=True)

    # explicity_ohe = ohe_prep(df, 'explicit','exp')
    explicity_ohe = ohe_prep(df, 'explicit', 'exp')
    year_ohe = ohe_prep(df, 'year', 'year') * 0.5
    popularity_ohe = ohe_prep(df, 'popularity_red', 'pop') * 0.15

    # scale float columns
    floats = df[float_cols].reset_index(drop=True)
    scaler = MinMaxScaler()
    floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns=floats.columns) * 0.2

    # concanenate all features
    final = pd.concat([genre_df, floats_scaled, popularity_ohe, year_ohe], axis=1)

    # add song id
    final['id'] = df['id'].values

    return final


complete_feature_set = create_feature_set(spotify_df, float_cols=float_cols)  # .mean(axis = 0)

# Connect to Spotipy API
# client id and secret for my application
client_id = 'd46045d10d6d4085ae61ccccc4a26f0b'
client_secret = '114f7b15392443e8a6f211d39bcd3abc'
user_id = '314g3bbza5autcj6jzlorfqjb7r4'

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# gather playlist names and images.
# images aren't going to be used until I start building a UI
id_name = {}
list_photo = {}
playlist_link = "https://open.spotify.com/playlist/6fPfZBmk0D0ZJ9xyDF4CHu?si=78f3b6c690d944c2"
playlist_URI = playlist_link.split("/")[-1].split("?")[0]

for i in sp.user_playlists(user_id)['items']:
    id_name[i['name']] = i['uri'].split(':')[2]
    list_photo[i['uri'].split(':')[2]] = i['images'][0]['url']


def create_necessary_outputs(playlist_name, id_dic, df):
    """
    Pull songs from a specific playlist.

    Parameters:
        playlist_name (str): name of the playlist you'd like to pull from the spotify API
        id_dic (dic): dictionary that maps playlist_name to playlist_id
        df (pandas dataframe): spotify datafram

    Returns:
        playlist: all songs in the playlist THAT ARE AVAILABLE IN THE KAGGLE DATASET
    """

    # generate playlist dataframe
    playlist = pd.DataFrame()
    playlist_name = playlist_name

    for ix, i in enumerate(sp.playlist(id_dic[playlist_name])['tracks']['items']):
        # print(i['track']['artists'][0]['name'])
        playlist.loc[ix, 'artist'] = i['track']['artists'][0]['name']
        playlist.loc[ix, 'name'] = i['track']['name']
        playlist.loc[ix, 'id'] = i['track']['id']  # ['uri'].split(':')[2]
        playlist.loc[ix, 'url'] = i['track']['album']['images'][1]['url']
        playlist.loc[ix, 'date_added'] = i['added_at']

    playlist['date_added'] = pd.to_datetime(playlist['date_added'])

    playlist = playlist[playlist['id'].isin(df['id'].values)].sort_values('date_added', ascending=False)

    return playlist


playlist_goat = create_necessary_outputs('goat', id_name, spotify_df)


def visualize_songs(df):
    """
    Visualize cover art of the songs in the inputted dataframe

    Parameters:
        df (pandas dataframe): Playlist Dataframe
    """

    temp = df['url'].values
    plt.figure(figsize=(15, int(0.625 * len(temp))))
    columns = 5

    for i, url in enumerate(temp):
        plt.subplot(int(len(temp) / columns + 1), columns, i + 1)

        image = io.imread(url)
        plt.imshow(image)
        plt.xticks(color='w', fontsize=0.1)
        plt.yticks(color='w', fontsize=0.1)
        plt.xlabel(df['name'].values[i], fontsize=12)
        plt.tight_layout(h_pad=0.4, w_pad=0)
        plt.subplots_adjust(wspace=None, hspace=None)

    plt.show()


# Create playlist vector
def generate_playlist_feature(complete_feature_set, playlist_df, weight_factor):
    """
    Summarize a user's playlist into a single vector

    Parameters:
        complete_feature_set (pandas dataframe): Dataframe which includes all of the features for the spotify songs
        playlist_df (pandas dataframe): playlist dataframe
        weight_factor (float): float value that represents the recency bias. The larger the recency bias, the most priority recent songs get. Value should be close to 1.

    Returns:
        playlist_feature_set_weighted_final (pandas series): single feature that summarizes the playlist
        complete_feature_set_nonplaylist (pandas dataframe):
    """

    complete_feature_set_playlist = complete_feature_set[
        complete_feature_set['id'].isin(playlist_df['id'].values)]  # .drop('id', axis = 1).mean(axis =0)
    complete_feature_set_playlist = complete_feature_set_playlist.merge(playlist_df[['id', 'date_added']], on='id',
                                                                        how='inner')
    complete_feature_set_nonplaylist = complete_feature_set[
        ~complete_feature_set['id'].isin(playlist_df['id'].values)]  # .drop('id', axis = 1)

    playlist_feature_set = complete_feature_set_playlist.sort_values('date_added', ascending=False)

    most_recent_date = playlist_feature_set.iloc[0, -1]

    for ix, row in playlist_feature_set.iterrows():
        playlist_feature_set.loc[ix, 'months_from_recent'] = int(
            (most_recent_date.to_pydatetime() - row.iloc[-1].to_pydatetime()).days / 30)

    playlist_feature_set['weight'] = playlist_feature_set['months_from_recent'].apply(lambda x: weight_factor ** (-x))

    playlist_feature_set_weighted = playlist_feature_set.copy()
    # print(playlist_feature_set_weighted.iloc[:,:-4].columns)
    playlist_feature_set_weighted.update(
        playlist_feature_set_weighted.iloc[:, :-4].mul(playlist_feature_set_weighted.weight, 0))
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-4]
    # playlist_feature_set_weighted_final['id'] = playlist_feature_set['id']

    return playlist_feature_set_weighted_final.sum(axis=0), complete_feature_set_nonplaylist


complete_feature_set_playlist_vector_goat, complete_feature_set_nonplaylist_goat = generate_playlist_feature(
    complete_feature_set, playlist_goat, 1.09)


# Generate recommendations
def generate_playlist_recos(df, features, nonplaylist_features):
    """
    Pull songs from a specific playlist.

    Parameters:
        df (pandas dataframe): spotify dataframe
        features (pandas series): summarized playlist feature
        nonplaylist_features (pandas dataframe): feature set of songs that are not in the selected playlist

    Returns:
        non_playlist_df_top_10: Top 10 recommendations for that playlist
    """

    non_playlist_df = df[df['id'].isin(nonplaylist_features['id'].values)]
    # non_playlist_df.loc[:, 'sim'] = cosine_similarity(nonplaylist_features.drop('id', axis=1).values, features.values.reshape(1, -1))[:, 0]
    non_playlist_df_copy = non_playlist_df.copy()
    non_playlist_df_copy.loc[:, 'sim'] = cosine_similarity(nonplaylist_features.drop('id', axis=1).values,
                                                           features.values.reshape(1, -1))[:, 0]
    non_playlist_df_top_10 = non_playlist_df_copy.sort_values('sim', ascending=False).head(10)
    non_playlist_df_top_10['url'] = non_playlist_df_top_10['id'].apply(
        lambda x: sp.track(x)['album']['images'][1]['url'])

    return non_playlist_df_top_10


goat_top10 = generate_playlist_recos(spotify_df, complete_feature_set_playlist_vector_goat,
                                     complete_feature_set_nonplaylist_goat)

print(goat_top10['name'])
