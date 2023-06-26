import gensim.downloader

from nltk.tokenize import word_tokenize
import string
import sys

import pickle
import numpy as np

from sklearn.neighbors import NearestNeighbors

from GenerateEmbeddings import generateEmbeddings, reformateTitle, calculateAveragedEmbedding

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time

def preprocess_query(query):
    punctuation = set(string.punctuation)
    tokenizedSentence = word_tokenize(query)
    lowerCasedAndDepunctuated = [token.lower() for token in tokenizedSentence if token not in punctuation]
    return lowerCasedAndDepunctuated

def calculate_embedding(query, model):
    embeddings = []
    unknownWords = []
    for word in query:
        if word in model:
            embeddings.append(model[word])

        if word not in model:
            unknownWords.append(word)
    # Use same calculation as in the dataset embeddings        
    averagedEmbedding = averagedEmbedding = sum(embeddings) / len(embeddings) if len(embeddings) > 0 else None

    return averagedEmbedding

def retrieve_paintings(indices, df):
    selection = df.iloc[indices]
    return selection

def returnInfo(df):
    ids = df['id']
    image_paths = df['image'].tolist()
    dates = df['date'].tolist()
    names = df['artist_name'].tolist()
    nationalities = df['artist_nationality'].tolist()
    styles = df['style'].tolist()
    tags = df['tags'].tolist()
    medias = df['media'].tolist()
    titles = df['image'].tolist()
    titles = [reformateTitle(title) for title in titles]

    # This dict has the following format: 
    # {image_paths: ["pathImage1", "pathImage2"... "pathImage3"], dates: ["dateImage1", "dateImage2",.."dateImageN"], names: etc.}
    # So each list in the dict has same length, where index 0 corresponds to the closest painting w.r.t the query:
    infoPaintings = {"ids": ids, "image_paths": image_paths, "dates": dates, "names": names, "nationalities": nationalities, "styles": styles,
                     "tags": tags, "medias": medias, "titles": titles}
    return infoPaintings

#Helper functions
###############################################################################################################################################


def initializeRetrieval():
    print("Initializing retrieval...")

    # Load dataframe, model to encode user query, precomputed embeddings NearestNeighbors in memory
    with open('G:\Desktop\multimedia_project\SimilarPaintings\similarPaintings.pkl', 'rb') as file:
        df = pickle.load(file)
    model = gensim.downloader.load('glove-wiki-gigaword-50')
    loaded_embeddings = np.load('embeddingsPerPainting.npy')
    retrievalNumber = 8
    neigh = NearestNeighbors(n_neighbors=retrievalNumber)

    print("Finished initializing.")
    return df, model, loaded_embeddings, neigh

def retrievePaintings(userInput, df, model, loaded_embeddings, neigh):
    query1_processed = preprocess_query(userInput)
    query1_embedding = calculate_embedding(query=query1_processed, model=model)
    neigh.fit(loaded_embeddings)

    if query1_embedding is not None:
        neighbours = neigh.kneighbors(query1_embedding.reshape(1, -1))
        retrievedPaintings = retrieve_paintings(neighbours[1].flatten(), df)
        infoPaintings = returnInfo(retrievedPaintings)
        return infoPaintings
    else:
        return None

# df, model, loaded_embeddings, neigh = initializeRetrieval()
# query = "fish"
# retrievedPaintings = retrievePaintings(userInput=query, df=df, model=model, loaded_embeddings=loaded_embeddings, neigh=neigh)
#
# print(retrievedPaintings)


