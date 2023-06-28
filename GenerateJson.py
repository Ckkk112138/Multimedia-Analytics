import  math
from GenerateEmbeddings import reformateTitle
import json
import shutil
import os
import warnings
import pandas as pd
warnings.filterwarnings("ignore", category=Warning)


def splitDfEra(df):
    minimumDate = df['date'].min()
    maximumDate =  df['date'].max()

    beginYear = math.floor(minimumDate / 100) * 100
    maxYear = math.ceil(maximumDate / 100) * 100

    # Create eras to divide paintings in.
    increment = 100
    eras = []
    startYear = beginYear 
    while startYear < maxYear:
        endEra = startYear + increment - 1
        eras.append((startYear, endEra))
        startYear += increment

    # Create new column with titles of each painting
    df['title'] = df['image'].apply(reformateTitle)
    # print(df[['id','date','style']])
    # Separate the painitings based on era
    eraDataframes = []
    # This is used for later in the menu.json
    listOfEras = [] 
    for era in eras:
         startYear, endYear = era
         eraDf = df[(df['date'] >= startYear) & (df['date'] <= endYear)]
         # Create column that determines the era of painting
         eraDf['era'] = f"{startYear}-{endYear}"
         # add eras to list
         listOfEras.append(f"{startYear}-{endYear}")
         eraDataframes.append(eraDf[['id','date','style', 'image', 'title', 'era']])

    return eraDataframes, listOfEras 

def splitDfStyle(listDf):
    eraStyleDataframes = []
    counter = 1
    for df in listDf:
        # Get all styles per daatframe
        listOfStyles = df['style'].unique()

        for style in listOfStyles:
            # Separate style per era
            eraStyleDf = df[df['style'] == style]
            # We use this counter for the menu.json
            eraStyleDf['count'] = counter
            eraStyleDataframes.append(eraStyleDf)
            counter += 1

    return eraStyleDataframes

def splitDfEraStyle(df):
    # Separate the painitings based on era
    eraDataframes, listOfEras = splitDfEra(df)

    # Separate the era dataframes in sub dataframes on style
    # -> we want same era and same style paintings in 1 dataframe
    eraStyleDataframes = splitDfStyle(eraDataframes)

    return eraStyleDataframes, listOfEras

def formatRes(df):
    listOfNodesDictionaries =  []
    listOfLinksDictioanries = []

    for index, row in df.iterrows():
        nodeDictionary = {"id":row['id'] + 2, "type": "painting", "name": row['title'], "r": 20, "color": "#00000000", "cover": row['image']}
        # For now I use negative id instead of id + max id num of df
        linkDictionary = {"id":-1* (row['id'] + 2), "source": 1 , "type": f"{int( row['date'] )} {row['style']}", "target": row['id'] + 2}

        listOfNodesDictionaries.append(nodeDictionary)
        listOfLinksDictioanries.append(linkDictionary)

    # print(listOfNodesDictionaries)
    # print(listOfLinksDictioanries)

    jsonFormat = {
    "nodes": listOfNodesDictionaries,
    "links": listOfLinksDictioanries
    }

    return jsonFormat

def flushFolder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)

def generateRes(listDfs, folder):
    for i,df in enumerate(listDfs):
        jsonFormat = formatRes(df)
        # print(i, jsonFormat)
        path = f"{folder}/res_{i + 1}.json"
        with open(path, "w") as json_file:
            json.dump(jsonFormat, json_file)

def generateChildren(listSplitDfs, era, resCounter):
    listOfChildren = []
    # generatec children per era
    for df in listSplitDfs:
        checkDfEra =  df.iloc[0, df.columns.get_loc('era')]
        if checkDfEra == era:
            style = df.iloc[0, df.columns.get_loc("style")]
            child = { "name": f"{style}", "type": f"{str(resCounter)}", "event": { "type": "add", "source": f"addNodes_{str(resCounter)}" } }
            listOfChildren.append(child)
            resCounter += 1

    return listOfChildren, resCounter

def initializeMenu(listSplitDfs, listOfEras):
    listOfEraDictionaries = []
    eraCounter = 1
    resCounter =  1

    for era in listOfEras:
        children, resCounter = generateChildren(listSplitDfs, era, resCounter)
        
        eraDictionary = {"name": era,
                         "type": f"era_{eraCounter}",
                          "children":children }
        listOfEraDictionaries.append(eraDictionary)
        eraCounter += 1

    jsonFormat = {
        "menu": listOfEraDictionaries
    }
    return jsonFormat

def showStylesPerEra(listOfEras, listSplitDfs):
    for era in listOfEras:
        for df in listSplitDfs:
            eraPerDataframe = df.iloc[0, df.columns.get_loc('era')]
            if eraPerDataframe == era:
                stylePerDataframe = df.iloc[0, df.columns.get_loc('style')]
                print(f"{era} has following styles: {stylePerDataframe}")

def generateMenu(listSplitDfs, listOfEras, folder):
    initializedMenu = initializeMenu(listSplitDfs, listOfEras)
    # print(initializedMenu)
    path = f"{folder}/menu.json"
    with open(path, "w") as json_file:
            json.dump(initializedMenu, json_file)
    # showStylesPerEra(listSplitDfs, listSplitDfs)


def generateJsonFiles(df):
    # List of dataframes split by era and style
    listSplitDfs, listOfEras = splitDfEraStyle(df)
    # delete and recreate folder where we save json in:
    folder = "G:\Desktop\multimedia_project\dist\jsonData"
    flushFolder(folder)

    generateRes(listSplitDfs, folder)

    generateMenu(listSplitDfs, listOfEras, folder)





