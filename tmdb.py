import pandas as pd
import requests
import config
import json

# Extract
# get request to the API
API_KEY = config.api_key

response_list = []

# get movie_id
for movie_id in range(550, 556):
    url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id, API_KEY)
    r = requests.get(url)
    response_list.append(r.json())

# Create a pandas dataframe
df = pd.DataFrame.from_dict(response_list)

# Transform
# create a list of column names
df_columns = ['budget', 'genres', 'id', 'imdb_id', 'original_title', 'release_date', 'revenue', 'runtime']
genres_list = df['genres'].tolist()
flat_list = [item for sublist in genres_list for item in sublist]

# temporary column called genres_all as a list of lists of genres
result = []
for l in genres_list:
    r = []
    for d in l:
        r.append(d['name'])
    result.append(r)
df = df.assign(genres_all=result)

# create the genres table
df_genres = pd.DataFrame.from_records(flat_list).drop_duplicates()

# takes a column of lists and turns it into a set of columns of frequency values
df_columns = ['budget', 'id', 'imdb_id', 'original_title', 'release_date', 'revenue', 'runtime']
df_genre_columns = df_genres['name'].to_list()
df_columns.extend(df_genre_columns)

s = df['genres_all'].explode()
df = df.join(pd.crosstab(s.index, s))

# expand out the datetime column into a table
df['release_date'] = pd.to_datetime(df['release_date'])
df['day'] = df['release_date'].dt.day
df['month'] = df['release_date'].dt.month
df['year'] = df['release_date'].dt.year
df['day_of_week'] = df['release_date'].dt.day_name()
df_time_columns = ['id', 'release_date', 'day', 'month', 'year', 'day_of_week']

# Load
# export our tables to csv files
df[df_columns].to_csv('tmdb_movies.csv', index=False)
df_genres.to_csv('tmdb_genres.csv', index=False)
df[df_time_columns].to_csv('tmdb_datetimes.csv', index=False)
