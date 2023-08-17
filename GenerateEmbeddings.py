import numpy as np
import gensim.downloader

from nltk.tokenize import word_tokenize
import string
import sys

import pickle
import numpy as np

import nltk
from nltk.corpus import stopwords
# nltk.download('stopwords')
# nltk.download('punkt')
import re
from itertools import chain
from sklearn.feature_extraction.text import TfidfVectorizer

with open('E:\PycharmProject#\MultimediaAnalytics\SimilarPaintings\similarPaintings.pkl', 'rb') as file:
    data = pickle.load(file)

# For some reason NaN is used as a string of nan -> remove this for now
# print(data.shape)
# data = data.drop(data[data.tags == 'nan'].index)

def contains_number(string):
    for char in string:
        if char.isdigit():
            return True
    return False

def reformateTitle(title):
    #images/david-burliuk_marusia-by-the-sea-1949.jpg
    filename = title.split('/')[-1]

    # david-burliuk_marusia-by-the-sea-1949.jpg
    filename = filename.split('.')[0]

    # david-burliuk_marusia-by-the-sea-1949
    desired_portion = filename.split('_')[-1]

    # marusia-by-the-sea-1949 -> some titles do not contain a year of creation
    if contains_number(desired_portion.split('-')[-1]):
        remove_year = desired_portion.split('-')[:-1]
    else:
        remove_year = desired_portion.split('-')

    remove_year = " ".join(remove_year)
    #marusia by the sea
    return remove_year

def mergeLists(list1, list2):
    merged_list = [f"{list1[i]},{list2[i]}" for i in range(len(list1))]
    return merged_list

def calculateAveragedEmbedding(embeddings):
    # If we have a painting with no known words we just return an embedding of only zeros
    averagedEmbedding = sum(embeddings) / len(embeddings) if len(embeddings) > 0 else np.zeros(50)
    return averagedEmbedding

def generateEmbeddings(df):
    # From here we calculate the final tag embedding for each painting:
    tags_list = df['tags'].tolist()

    # Retrieve titels for each painting
    title_list = df['image'].tolist()
    title_list = [reformateTitle(title) for title in title_list]

    # add titels to tags for more informative tag embeddings
    tags_list = mergeLists(tags_list, title_list)

    # Set of punctuation
    punctuation = set(string.punctuation)

    # Set of stop words
    stop_words = set(stopwords.words('english'))

    # Model to use for word2vec
    model = gensim.downloader.load('glove-wiki-gigaword-50')
    # Here we save final sentence embedding for each painting. With sentence I mean the embedding averaged across all tags per painting
    # first entry is the average embedding for painting 1, second for painting 2, etc...
    tag_vectors = []
    for tag in tags_list:
        # A lot of information in the tags is separated by '-'. We dehyphene this first and then tokenize in order to use for word embeddings. 
        dehyphenatedSentence = tag.replace('-', ' ')
        tokenizedSentence = word_tokenize(dehyphenatedSentence)
        # print(tokenizedSentence)
        lowerCasedAndDepunctuated = [token.lower() for token in tokenizedSentence if token not in punctuation and token not in stop_words]

        # print(tag, lowerCasedAndDepunctuated)
        # save embedding for each word in a sentence in embeddings
        embeddings = []
        unknownWords = []
        for word in lowerCasedAndDepunctuated:
            if word in model:
                embeddings.append(model[word])

            if word not in model:
                unknownWords.append(word)
        # calculate average embedding -> we can also do weighted average by tfidf
        averagedEmbedding = calculateAveragedEmbedding(embeddings)

        tag_vectors.append(averagedEmbedding)
    return np.array(tag_vectors)

def generateVocab(df):
    tags_list = df['tags'].tolist()
    title_list = df['image'].tolist()
    title_list = [reformateTitle(title) for title in title_list]

    tags_list = mergeLists(tags_list, title_list)
    punctuation = set(string.punctuation)
    stop_words = set(stopwords.words('english'))

    processedTags = []
    for tag in tags_list:
        # A lot of information in the tags is separated by '-'. We dehyphene this first and then tokenize in order to use for word embeddings. 
        dehyphenatedSentence = tag.replace('-', ' ')

        tokenizedSentence = word_tokenize(dehyphenatedSentence)
        lowerCasedAndDepunctuated = [token.lower() for token in tokenizedSentence if token not in punctuation and token not in stop_words]
        processedTags.append(lowerCasedAndDepunctuated)

    return processedTags

def generateTFIDF(documents):
    document_texts = [' '.join(doc) for doc in documents]

    vectorizer = TfidfVectorizer(norm='l2')
    tfidf_matrix = vectorizer.fit_transform(document_texts)
    
    # Print the TF-IDF values for document 4
    # document_index = 3  # Index 3 corresponds to document 4
    # doc4_tfidf_values = tfidf_matrix[document_index]
    
    # print("Document 4 TF-IDF values:")
    # for term_idx, term in enumerate(documents[document_index]):
    #     tfidf_value = doc4_tfidf_values[0, vectorizer.vocabulary_[term]]
    #     print("Term:", term, "TF-IDF:", tfidf_value)
    return tfidf_matrix


# Generate tf-idf
# documents = generateVocab(data)
# tfIdf = generateTFIDF(documents)
# sys.exit()

# we save the embeddings per painting externally
tag_vectors = generateEmbeddings(data)
np.save('embeddingsPerPainting.npy', tag_vectors)
