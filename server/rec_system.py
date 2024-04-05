import pandas as pd
import numpy as np
import re
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# client id and secret for my application
client_id = '1f640d39f9a14736b02a11cb12400a66'
client_secret = '499269edddef4a33b2e949ec5be7c615'
user_id = '314g3bbza5autcj6jzlorfqjb7r4'

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
    playlist_feature_set_weighted.update(
        playlist_feature_set_weighted.iloc[:, :-4].mul(playlist_feature_set_weighted.weight, 0))
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-4]

    return playlist_feature_set_weighted_final.sum(axis=0), complete_feature_set_nonplaylist

class RecommendationSystem:
    spotify_df = pd.DataFrame()
    data_w_genre = pd.DataFrame()
    complete_feature_set = pd.DataFrame()

    def __init__(self):
        # Read data
        self.spotify_df = pd.read_csv('data.csv')
        self.data_w_genre = pd.read_csv('data_w_genres.csv')
        # Data exploration/preparation
        self.data_w_genre['genres_upd'] = self.data_w_genre['genres'].apply(
            lambda x: [re.sub(' ', '_', i) for i in re.findall(r"'([^']*)'", x)])
        self.spotify_df['artists_upd_v1'] = self.spotify_df['artists'].apply(lambda x: re.findall(r"'([^']*)'", x))

        self.spotify_df['artists_upd_v2'] = self.spotify_df['artists'].apply(lambda x: re.findall('\"(.*?)\"', x))
        self.spotify_df['artists_upd'] = np.where(self.spotify_df['artists_upd_v1'].apply(lambda x: not x),
                                             self.spotify_df['artists_upd_v2'],
                                             self.spotify_df['artists_upd_v1'])

        # need to create my own song identifier because there are duplicates of the same song with different ids. I see different
        self.spotify_df['artists_song'] = self.spotify_df.apply(lambda row: row['artists_upd'][0] + row['name'], axis=1)
        self.spotify_df.sort_values(['artists_song', 'release_date'], ascending=False, inplace=True)

        self.spotify_df.drop_duplicates('artists_song', inplace=True)

        artists_exploded = self.spotify_df[['artists_upd', 'id']].explode('artists_upd')

        artists_exploded_enriched = artists_exploded.merge(self.data_w_genre, how='left', left_on='artists_upd',
                                                           right_on='artists')
        artists_exploded_enriched_nonnull = artists_exploded_enriched[~artists_exploded_enriched.genres_upd.isnull()]

        artists_genres_consolidated = artists_exploded_enriched_nonnull.groupby('id')['genres_upd'].apply(
            list).reset_index()
        artists_genres_consolidated['consolidates_genre_lists'] = artists_genres_consolidated['genres_upd'].apply(
            lambda x: list(set(list(itertools.chain.from_iterable(x)))))

        self.spotify_df = self.spotify_df.merge(artists_genres_consolidated[['id', 'consolidates_genre_lists']], on='id',
                                      how='left')

        # Feature engineering
        self.spotify_df['year'] = self.spotify_df['release_date'].apply(lambda x: x.split('-')[0])
        float_cols = self.spotify_df.dtypes[self.spotify_df.dtypes == 'float64'].index.values

        # create 5 point buckets for popularity
        self.spotify_df['popularity_red'] = self.spotify_df['popularity'].apply(lambda x: int(x / 5))

        # tfidf can't handle nulls so fill any null values with an empty list
        self.spotify_df['consolidates_genre_lists'] = self.spotify_df['consolidates_genre_lists'].apply(
            lambda d: d if isinstance(d, list) else [])

        self.complete_feature_set = create_feature_set(self.spotify_df, float_cols=float_cols)  # .mean(axis = 0)

    # Generate recommendations
    def generate_playlist_recos(self, playlist, amount):
        """
        Pull songs from a specific playlist.

        Parameters:
            playlist_name(string): name of user playlist
            id_name(dict): id name of user playlists
            amount(int): amount of recommendations
        Returns:
            non_playlist_df_top_n: Top amount recommendations for that playlist
        """
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        features, nonplaylist_features = generate_playlist_feature(self.complete_feature_set, playlist, 1.09)

        non_playlist_df = self.spotify_df[self.spotify_df['id'].isin(nonplaylist_features['id'].values)]
        non_playlist_df_copy = non_playlist_df.copy()
        non_playlist_df_copy.loc[:, 'sim'] = cosine_similarity(nonplaylist_features.drop('id', axis=1).values,
                                                               features.values.reshape(1, -1))[:, 0]
        non_playlist_df_top_n = non_playlist_df_copy.sort_values('sim', ascending=False).head(amount)

        non_playlist_df_top_n['url'] = non_playlist_df_top_n['id'].apply(
            lambda x: sp.track(x)['album']['images'][1]['url'])
        tr_map = {
            ord('[') : None,
            ord(']') : None,
            ord('\'') : None
        }
        non_playlist_df_top_n['artists'] = non_playlist_df_top_n['artists'].apply(lambda x: x.translate(tr_map))
        return non_playlist_df_top_n