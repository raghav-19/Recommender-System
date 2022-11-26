# -*- coding: utf-8 -*-
"""Similar movie recommender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bJfbQ37hJ2BWtrjxUffPOez2sOtvkLzq
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import string
import nltk
from nltk.stem.snowball import SnowballStemmer
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import QuantileTransformer
from sklearn.metrics.pairwise import cosine_similarity
pd.set_option('display.max.columns', None)

metadata = pd.read_csv('/content/drive/MyDrive/Dataset/data/movies_metadata_small.csv')
keywords = pd.read_csv('/content/drive/MyDrive/Dataset/data/keywords_small.csv')
credits = pd.read_csv('/content/drive/MyDrive/Dataset/data/credits_small.csv')

metadata.head(2)

metadata.isnull().sum()

metadata['adult'].value_counts()

metadata['video'].value_counts()

metadata['budget'].value_counts().head()

metadata['revenue'].value_counts().head()

metadata[metadata['original_title']!=metadata['title']][['original_title','title']].head(5)

metadata.drop(columns=['adult','belongs_to_collection','budget','homepage','imdb_id','original_language','original_title',
                       'poster_path','production_companies','production_countries','revenue','runtime',
                       'spoken_languages','status','video','vote_count'], inplace=True)

metadata.isnull().sum()

metadata[metadata['release_date'].isna()]

metadata.dropna(subset=['release_date'], inplace=True) # Since both are unpopular movies
metadata['release_date'] = metadata['release_date'].apply(lambda x : int(x[0:4]))
metadata = metadata[metadata['release_date']>1960].reset_index(drop=True) # removing very old movies
metadata.fillna("",inplace=True) # we can fill overview and tagline with empty strings
metadata.isnull().sum()

def get_genres(genres):
    return ' '.join([i['name'] for i in genres])
def get_cast(cast):
    if len(cast)>7:
        cast=cast[:7];
    return [people['name'].replace(' ','').replace('-','') for people in cast]
def get_director(crew):
    for person in crew:
        if person['job']=='Director':
            return [person['name'].replace(' ','').replace('-','')]
    return []
def get_people(x):
    people = x['cast'] if x['genres'].find('Animation')==-1 else x['cast'][0:3]
    for d in x['director']:
        if d not in people:
            people.append(d)
    return ' '.join(people)
def get_keywords(keywords):
    return ' '.join([i['name'] for i in keywords])

metadata['genres']= metadata['genres'].apply(literal_eval).apply(get_genres)
credits['cast'] = credits['cast'].apply(literal_eval).apply(get_cast)
credits['director'] = credits['crew'].apply(literal_eval).apply(get_director)
keywords['keywords'] = keywords['keywords'].apply(literal_eval).apply(get_keywords)

info = pd.merge(credits[['id', 'cast', 'director']], keywords, how='inner', on='id')
metadata = pd.merge(metadata, info, how='inner', on='id')
metadata.head(2)

metadata['keys']=metadata.apply(lambda x : x['title']+" "+x['overview']+" "+x['tagline']+" "+x['keywords'],axis=1)
metadata['people'] = metadata.apply(get_people, axis=1)
metadata = metadata[['id','title','people','genres','keys','popularity','release_date','vote_average']].copy()
metadata.head(2)

stemmer = SnowballStemmer(language='english')
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
def get_keys(x):
    x = x.translate(str.maketrans('', '', string.punctuation))
    return ' '.join([stemmer.stem(w) for w in x.split() if stemmer.stem(w) not in stopwords])
metadata['keys'] = metadata['keys'].apply(get_keys)

transformer = QuantileTransformer(output_distribution='uniform')
metadata['popularity'] = pd.Series(transformer.fit_transform(metadata[['popularity']]).reshape(-1)-0.5)/2
metadata['vote_average'] = metadata['vote_average'].apply(lambda x : np.nan if x==0 else x)
mean_average = metadata['vote_average'].mean()
metadata.fillna(mean_average, inplace=True)
metadata['vote_average'] = (metadata['vote_average']/20)-0.25
metadata = metadata.sort_values('popularity', ascending=False).reset_index(drop=True)
metadata.head(2)

movie_id = metadata[['id']].values
movie_title = metadata['title'].drop_duplicates()
movie_ind = dict(zip(movie_title.values, movie_title.index))

obj_cnt = CountVectorizer(lowercase=True, analyzer='word', min_df=5)
cnt_val = obj_cnt.fit_transform(metadata['people']).toarray()/2
obj_genre = TfidfVectorizer()
genre_val = obj_genre.fit_transform(metadata['genres']).toarray()/3
obj_tfidf = TfidfVectorizer(min_df=10)
tfidf_val = obj_tfidf.fit_transform(metadata['keys']).toarray()
num_val = metadata[['vote_average']].values
movie_id.shape, num_val.shape, cnt_val.shape, genre_val.shape, tfidf_val.shape

col_names=['vote_average'] + list(obj_cnt.get_feature_names_out()) + list(obj_genre.get_feature_names_out()) + list(obj_tfidf.get_feature_names_out())
features = np.concatenate((num_val, cnt_val, genre_val, tfidf_val), axis=1)
similarity = cosine_similarity(features, features)
len(col_names), features.shape, similarity.shape

def get_similar_from_title(movie_name):
    try:
        index = movie_ind[movie_name]
        print(f"given movie index : {index}")
        scores = list(enumerate(similarity[index]))
        scores = sorted(scores, key = lambda x : x[1], reverse=True)
        top_mv_index = [i[0] for i in scores[1:21]]
        top_mv_score = pd.Series([i[1] for i in scores[1:21]], index=top_mv_index, name='score')
        df = pd.concat([metadata[['title', 'popularity', 'vote_average']].iloc[top_mv_index], top_mv_score],axis=1)
        df['total'] = df['score'] + (df['popularity']+df['vote_average'])/2
        df = df.sort_values('total',ascending=False)
        df = df[(df['popularity']>0) & (df['vote_average']>0)].copy()
        return df[['title']][0:10]
    except:
        print("Please enter correct Movie name")

get_similar_from_title('The Avengers')

get_similar_from_title('Batman Begins')

get_similar_from_title('Forrest Gump')

def why_two_movie_are_similar(m1, m2):
    score = list(enumerate(features[m1]*features[m2]))
    score = sorted(score, key = lambda x : x[1], reverse=True)
    keywords = [(col_names[i[0]],i[1]) for i in score[0:10] if i[1]>0]
    return keywords

why_two_movie_are_similar(103,205)