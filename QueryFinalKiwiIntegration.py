import gensim.downloader

from nltk.tokenize import word_tokenize
import string
import sys

import pickle
import numpy as np

from sklearn.neighbors import NearestNeighbors

from GenerateEmbeddings import generateEmbeddings, reformateTitle, calculateAveragedEmbedding
from GenerateJson import generateJsonFiles

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
import math

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
    # Use same calculation as in the dataset embeddings -> if model does not know at least 1 word we return None 
    averagedEmbedding = sum(embeddings) / len(embeddings) if len(embeddings) > 0 else None
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

def showPaintings(df):
    image_paths = df['image'].tolist()
    artist_names = df['artist_name'].tolist()
    tags = df['tags'].tolist()
    titles = df['image'].tolist()
    titles = [reformateTitle(title) for title in titles]

    # print(image_paths)
    image_paths = [f"../../../CUB+Painting_Info/{img}"for img in image_paths]
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))

    # Iterate over the image paths and plot each image
    for i, ax in enumerate(axes.flat):
        # Load the image using Matplotlib
        try:
            img = mpimg.imread(image_paths[i])
    
            # Plot the image
            ax.imshow(img)
            ax.axis('off')
            ax.set_title(f'Title: {titles[i]} \n Tags:{tags[i]} \n by {artist_names[i]}', fontdict={'fontsize': 7})
        except:
            # Some painters do not have enough paintings to show vin; just show the paintings up until the last one.
            pass

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    plt.show()  

def reformatPainterName(name):
    parts = name.split('-')
    formatted_name = ' '.join(part.capitalize() for part in parts)
    return formatted_name

def generateTitle(path):
    #images/david-burliuk_marusia-by-the-sea-1949.jpg
    filename = path.split('/')[-1]

    # david-burliuk_marusia-by-the-sea-1949.jpg
    filename = filename.split('.')[0]

    # david-burliuk_marusia-by-the-sea-1949
    desired_portion = filename.split('_')[-1]

    # marusia-by-the-sea-1949 -> some titles do not contain a year of creation
    if contains_number(desired_portion.split('-')[-1]):
        remove_year = desired_portion.split('-')[:-1]
    else:
        remove_year = desired_portion.split('-')
    
    remove_year = " ".join(part.capitalize() for part in remove_year)

    return remove_year

def contains_number(string):
    for char in string:
        if char.isdigit():
            return True
    return False

#####################################################################################################
## Functionality for finding specific painter

def integratePainter(specificPainter, df, loaded_embeddings):
    # This is more like a wrapper function where we either return painter specific df and embeddings
    # or return None, None when painter is not known to original database
    if specificPainter != "None":
        # If the user wants a specific painter try to check whether the painter exists
        try:
            dfAdjusted, loaded_embeddingsAdjusted = specificPainterData(df=df, embeddings=loaded_embeddings, painter=specificPainter)

        except ValueError as e:
            print(f"{specificPainter} {e}")
            # Go back to the top of the while loop -> we return same format as usual, but now we continue in original
            # while loop upon retrieving None, None from this function
            return None, None
        
    if specificPainter == "None":
        # If no painter is specified, search through all painters
        dfAdjusted = df
        loaded_embeddingsAdjusted = loaded_embeddings
        
    return dfAdjusted, loaded_embeddingsAdjusted

def specificPainterData(df, embeddings, painter="Vincent Van Gogh"):
    # Get unique artist names; already formatted correctly
    list_artist_names = df['artist_name'].unique().tolist()
    
    # We find the correct painter name based on query, where user can enter name or part of name
    foundPainter = findPainter(painter, list_artist_names, searchOfInterest="painter")

    # select only those rows corresponding to specific painter
    df = df[df['artist_name'].isin(foundPainter)]
    amountOfPaintings = df.shape[0] 
    if amountOfPaintings == 0:
        raise ValueError("is not known to our database. (2)")

    # Get the indices which we need to keep the embeddings for
    list_id = df['id'].tolist()
    adjustedEmbeddings = embeddings[list_id]

    print(f"{foundPainter} has a total of {amountOfPaintings} paintings present in our dataset.")
    return df, adjustedEmbeddings

def findPainter(query, painterList, searchOfInterest):
    # originally used to find user query painter amongst painters, now it's generalized to retrieve any query from any list
    # I just did not change the naming of variables to be generalized
    query = query.lower()
    matches = []

    for painter in painterList:
        if query in painter.lower():
            matches.append(painter)
    
    # If we find more than one match, ask user to enter one of the options
    
    # raise error
    if len(matches) == 0:
        if searchOfInterest == "painter":
            raise ValueError("is not known to our database.")
        
        if searchOfInterest == "title":
            raise ValueError(" is not known to our database.")
        
    return matches

    
#####################################################################################################
## Functionality for finding specfic title

def integrateTitle(specificTitle,df):

    try:
        dfAdjusted = specificTitleData(df=df, title=specificTitle)

    except ValueError as e:
        print(f"{specificTitle} {e}")
        # Go back to the top of the while loop -> we return same format as usual, but now we continue in original
        # while loop upon retrieving None, None from this function
        return None

    return dfAdjusted

def specificTitleData(df, title):
    list_titles = df['title'].unique().tolist()

    foundTitle = findPainter(title, list_titles, searchOfInterest="title")

    # Select all paintings that have a title that corresponds to the user's query.
    df = df[df['title'].isin(foundTitle)]

    # This will never fire because we raise value error in findPainter when no match is found
    # just as a safeguard we keep it.
    amountOfTitles = df.shape[0] 
    if amountOfTitles == 0:
        raise ValueError("is not known to our database.")
    
    return df

#####################################################################################################

def generateNeighbours(user_input, dfAdjusted, loaded_embeddingsAdjusted, model):
        print(f"Searching for paintings related to: {user_input}")
        query1_processed = preprocess_query(user_input)
        query1_embedding = calculate_embedding(query=query1_processed, model=model)

        # let's say we want to show top 10 paintings per query, sometimes painters only have 8 paintings:
        # 10 must correspond to the amount of rows and column we show in the showPaintings function
        retrievalNumber = 20
        amountOfPaintingsPresent = dfAdjusted.shape[0]
        if amountOfPaintingsPresent < retrievalNumber:
            neigh = NearestNeighbors(n_neighbors=amountOfPaintingsPresent)

        if amountOfPaintingsPresent >= retrievalNumber:
            neigh = NearestNeighbors(n_neighbors=retrievalNumber)

        neigh.fit(loaded_embeddingsAdjusted)

        if query1_embedding is not None:
            neighbours = neigh.kneighbors(query1_embedding.reshape(1, -1))
            return neighbours
        else:
            print("query is not known to our model")
            return None


#Helper functions above
###############################################################################################################################################

def initializeRetrieval():
    print("Initializing retrieval...")

    # Load dataframe, model to encode user query, precomputed embeddings NearestNeighbors in memory
    with open('G:\\Desktop\\multimedia_project\\SimilarPaintings\\similarPaintings.pkl', 'rb') as file:
        df = pickle.load(file)
    model = gensim.downloader.load('glove-wiki-gigaword-50')
    loaded_embeddings = np.load('embeddingsPerPainting.npy')
    # Reformate artist names
    df['artist_name'] = df['artist_name'].apply(reformatPainterName)
    df['title'] = df['image'].apply(generateTitle)

    print("Finished initializing.")
    return df, model, loaded_embeddings

def retrievePaintings(user_input, df, model, loaded_embeddings):
    neighbours = generateNeighbours(user_input=user_input, dfAdjusted=df, loaded_embeddingsAdjusted=loaded_embeddings, model=model)

    if neighbours is not None:
        # print(neighbours)
        retrievedPaintings = retrieve_paintings(neighbours[1].flatten(), df)
        # Create JSON files
        generateJsonFiles(retrievedPaintings)
        # showPaintings(retrievedPaintings)
        infoPaintings = returnInfo(retrievedPaintings)
        return infoPaintings
    
    if neighbours is None:
        return None
        
def retrievePaintingsTitleSpecific(user_input, df):
    dfAdjusted = integrateTitle(specificTitle=user_input, df=df)
    # If painter is not known, we go back to top of this loop and ask for a painter again
    if dfAdjusted is None:
        return None
    
    amountOfPaintings  = dfAdjusted.shape[0]
    maxNum =  50

    print(f"Our dataset has a total of {amountOfPaintings} paintings") 
    print(f"We return a maximum of {maxNum} paintings")   

    if amountOfPaintings > maxNum:
        dfAdjusted = dfAdjusted.head(maxNum)
        print(f"We reduced to amount of paintings from {amountOfPaintings} to {maxNum}")

    # Generate Json + show paintings
    generateJsonFiles(dfAdjusted)
    # showPaintings(dfAdjusted)
    infoPaintings = returnInfo(dfAdjusted)
    return infoPaintings

def retrievePaintingsPainterSpecific(painterInput, df, model, loaded_embeddings, topicInfo=None):    
    # Here we generate painter specific data
    dfAdjusted, loaded_embeddingsAdjusted = integratePainter(specificPainter=painterInput, df=df,loaded_embeddings=loaded_embeddings)

    # If painter is not known, we go back to top of this loop and ask for a painter again
    if dfAdjusted is None:
        return None
    
    amountOfPaintings  = dfAdjusted.shape[0]
    maxNum =  50

    # Just check for the painter specified
    if topicInfo is None: 
        if amountOfPaintings > maxNum:
            dfAdjusted = dfAdjusted.head(maxNum)
            print(f"We reduced to amount of paintings from {amountOfPaintings} to {maxNum}")

        # showPaintings(dfAdjusted)
        generateJsonFiles(dfAdjusted)
        infoPaintings = returnInfo(dfAdjusted)
        return infoPaintings


    # Fires when we additionally want to check a specific topic on top of painter specific
    if topicInfo is not None:
        neighbours = generateNeighbours(user_input=topicInfo, dfAdjusted=dfAdjusted, loaded_embeddingsAdjusted=loaded_embeddingsAdjusted, model=model)

        if neighbours is not None:
            retrievedPaintings = retrieve_paintings(neighbours[1].flatten(), dfAdjusted)

            # Create JSON files
            generateJsonFiles(retrievedPaintings)
            # showPaintings(retrievedPaintings)
            infoPaintings = returnInfo(retrievedPaintings)
            return infoPaintings
        
        if neighbours is None:
            return None

# Initialize search
# df, model, loaded_embeddings = initializeRetrieval()

# topic = "sun"
# title = "potato"
# author = "Vincent"

# Start user interaction when not wanting to search for titles or painters, merely for topics
# returns either None when search is unsuccesful, or painting information according to 

# USE THIS WHEN ONLY THE TOPIC SEARCH BAR IS USED; ONLY TOPIC
# retrievedPaintings = retrievePaintings(user_input=topic, df=df, model=model, loaded_embeddings=loaded_embeddings)

# When only wanting to search for specific titles; ONLY TITLE
# retrievedPaintings = retrievePaintingsTitleSpecific(user_input=title, df=df)

# When wanting to search for specific authors, or authors and topic; USE THIS WHEN EITHER ONLY THE AUTHOR SEARCH BAR IS USED, 
# OR WHEN BOTH THE AUTHOR SEARCH BAR AND THE TOPIC SEARCH BAR IS USED; If you dont provide the topicInfo parameter
# then, we only search for specified painter

# PAINTER + TOPIC
# retrievedPaintings = retrievePaintingsPainterSpecific(painterInput=author, topicInfo=topic, df=df, model=model, loaded_embeddings=loaded_embeddings)


# ONLY PAINTER
# retrievedPaintings = retrievePaintingsPainterSpecific(painterInput=author, df=df, model=model, loaded_embeddings=loaded_embeddings)


#LASTLY, IF WE RETURN NONE FOR ANY OF THE SEARCH MAYBE YOU CAN NOTIFY THE USER BY SAYING THE SEARCH WAS UNSUCCESFUL?