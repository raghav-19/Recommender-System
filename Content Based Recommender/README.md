# Content Based Recommender

This dataset (ml-latest-small) describes 5-star rating and free-text tagging activity from MovieLens, a movie recommendation service. It contains 100836 ratings and 3683 tag applications across 9741 movies. These data were created by 610 users between March 29, 1996 and September 24, 2018. This dataset was generated on September 26, 2018.

Users were selected at random for inclusion. All selected users had rated at least 20 movies. No demographic information is included. Each user is represented by an id, and no other information is provided.
The data are contained in the files links.csv, ratings.csv and tags.csv.

Along with MovieLens Data, it also contains TMDB Movie Metadata which contain all details of 45503 Movies in
credits.csv, movie_metadata.csv, keywords.csv

#####Dataset link - https://www.kaggle.com/datasets/raghavraipuria/tmdb-movie-dataset

### Recommendation of Similar Movies for a given title of the Movie

Built content based recommender using multiple features of movies like cast, director, genres, title, description, tagline, keywords, etc to recommend 10 similar movies for a  title of any valid movie. Created a function to explain the similarity between any 2 movies

### Movie Recommendation to a user on the basis of past rating given by him

Built content based recommender using multiple features of movies like cast, director, genres, title, description, tagline, keywords, etc to recommend movies to a user on the basis of given rating by user on watched movies
