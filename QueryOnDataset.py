import gensim.downloader

from nltk.tokenize import word_tokenize
import string
import sys

import pickle
import numpy as np

# tag embeddings words2vec(wikidata and gigga corpus) nearest neighbor search in embedding space
from sklearn.neighbors import NearestNeighbors

from GenerateEmbeddings import generateEmbeddings, reformateTitle, calculateAveragedEmbedding

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time

print("Initializing retrieval...")
with open('G:\Desktop\multimedia_project\SimilarPaintings\similarPaintings.pkl', 'rb') as file:
    data = pickle.load(file)

# data = data.drop(data[data.tags == 'nan'].index)
model = gensim.downloader.load('glove-wiki-gigaword-50')
punctuation = set(string.punctuation)

def preprocess_query(query):
    tokenizedSentence = word_tokenize(query)
    lowerCasedAndDepunctuated = [token.lower() for token in tokenizedSentence if token not in punctuation]
    return lowerCasedAndDepunctuated

def calculate_embedding(query):
    embeddings = []
    unknownWords = []
    for word in query:
        if word in model:
            embeddings.append(model[word])

        if word not in model:
            unknownWords.append(word)
    # Use same calculation as in the dataset embeddings        
    averagedEmbedding = calculateAveragedEmbedding(embeddings)

    return averagedEmbedding

def getPainterData(data, artist_name="vincent-van-gogh"):
    artist_data = data[data['artist_name'] == artist_name]
    # Maybe for later this might be useful
    artist_data = artist_data.reset_index(drop=True)
    return artist_data

def retrieve_paintings(indices, df):
    selection = df.iloc[indices]
    # print(selection['tags'].tolist())
    # print()
    # print(selection['artist_name'].tolist())
    return selection

def showPaintings(df):
    image_paths = df['image'].tolist()
    artist_names = df['artist_name'].tolist()
    tags = df['tags'].tolist()
    titles = df['image'].tolist()
    titles = [reformateTitle(title) for title in titles]

    # print(image_paths)
    image_paths = [f"../../CUB+Painting_Info/{img}"for img in image_paths]
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))

    # Iterate over the image paths and plot each image
    for i, ax in enumerate(axes.flat):
        # Load the image using Matplotlib
        img = mpimg.imread(image_paths[i])
    
        # Plot the image
        ax.imshow(img)
        ax.axis('off')
        ax.set_title(f'Title: {titles[i]} \n Tags:{tags[i]} \n by {artist_names[i]}', fontdict={'fontsize': 7})

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    plt.show()

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

def getUserInput(df):
    while True:
        user_input = input("Enter a topic of paintings you are interested in (or 'quit' to exit): ")
        if user_input == 'quit':
            break
        # Process the user input
        print(f"Searching for paintings related to: {user_input}")

        query1_processed = preprocess_query(user_input)
        query1_embedding = calculate_embedding(query1_processed)
        # Amount of paintings to retrieve
        retrievalNumber = 8
        neigh = NearestNeighbors(n_neighbors=retrievalNumber)

        neigh.fit(loaded_embeddings)
        if query1_embedding is not None:
            neighbours = neigh.kneighbors(query1_embedding.reshape(1, -1))
            retrievedPaintings = retrieve_paintings(neighbours[1].flatten(), df)
            showPaintings(retrievedPaintings)
            # Here we retrieve info to be used in our application
            infoPaintings = returnInfo(retrievedPaintings)
            print(infoPaintings)

        else:
            print("query is not known to our model")
            
# if true we look through all paintings
# if false we only look through paintings of a specific artist
nonSpecificData = True

if nonSpecificData:
    # Load the embeddings from the file; if we want it from whole dataset
    loaded_embeddings = np.load('embeddingsPerPainting.npy')
    print("Finished initializing.")
    # Here we ask keep asking for user input
    getUserInput(df=data)

if not nonSpecificData:
    # Here we only are interested in specific painters
    # So we don't load all embeddings but generate a subset of the data instead
    painter_specific_data = getPainterData(data)
    loaded_embeddings = generateEmbeddings(painter_specific_data)
    print("Finished initializing.")
    # Here we ask keep asking for user input
    getUserInput(df=painter_specific_data)
