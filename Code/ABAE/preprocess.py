#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import nltk
#nltk.download('wordnet')
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import codecs

import json
import os
import re
import glob

from pathlib import Path
from langdetect import detect_langs
from argParseDummy import args
from tqdm import tqdm

# In[ ]:


#mostly copied from loadPaper, slight changes

def loadJson(path):
    file = open(path,"r")
    fileString = file.read().replace("\n", " ")
    file.close()
    return fileString

def seperateTextFromJson(jsonString):
    jsonDict = json.loads(jsonString)
    bodyText = jsonDict["body_text"]
    listOfTexts = list(map(lambda x: x.get("text"), bodyText))
    #the empty character determine how the strings are concatenated, "-" would put - between them.
    text = ''.join(listOfTexts) 
    return text

#returns positions of matched pattern
def matchPositions(regex,text):
    p = re.compile(regex)
    result = []
    for m in p.finditer(text):
        result.append(m.start())
    return result

#splits list at given indices list
def splitAtPosition(indices,text):
    indices.insert(0,0);
    parts = [text[i:j] for i,j in zip(indices, indices[1:]+[None])]
    parts = list(filter(lambda x : len(x) != 0, parts))
    parts = list(map(lambda x : x[1:len(x)].strip() if x[0]=='.' else x.strip(),parts))

    return parts

#loadsPaper and returns bodyText as List of sentences
def loadPaper(path = '../../../Cord-19/document_parses/pdf_json/000a0fc8bbef80410199e690191dc3076a290117.json'):
    jsonString = loadJson(path)
    text = seperateTextFromJson(jsonString)
    splitPos = matchPositions('\.\s?[A-Z]',text); #\s? means optional whitespace; compensate for parse errors
    splitText = splitAtPosition(splitPos,text);
    return splitText


# In[ ]:

#gets a string and returns a list of tokens, does: lowercase, stopword removal, lemmatization
def parse_sentence(line):
    lmtzr = WordNetLemmatizer()
    stop = stopwords.words('english')
    text_token = CountVectorizer().build_tokenizer()(line.lower())
    text_rmstop = [i for i in text_token if i not in stop]
    text_stem = [lmtzr.lemmatize(w) for w in text_rmstop]
    return text_stem


# In[ ]:

#loads all paper in the cord path, preprocesses them and saves them to one file
def preprocess_Dataset(args, start=0, stop=10000):
    paths = glob.glob("../../../Cord-19/document_parses/pdf_json/*.json")[start:stop]
    paths = list(map(lambda path : path.replace("\ ","/"), paths))
    out = codecs.open(args.pre_path, 'w', 'utf-8')
    filt = codecs.open(args.filtered_path, 'w', 'utf-8')
    en = False
    for path in tqdm(paths):
        textList = loadPaper(path)
        for line in textList:
            if len(line) == 0:
                continue
            try:
                en = False
                for lang in detect_langs(line):
                    if str(lang)[0:2]=="en": 
                        en = True
                if not en:
                    filt.write(line +"\n")
                    filt.write("\n")
                    continue
                tokens = parse_sentence(line)
                if len(tokens) > 0:
                    out.write(' '.join(tokens) + '\n')
                    out.write(" \n")
            except:
                continue



#filter other stat, filter duplicates, apply stopword and lemma, write to file and return stats
def processExtracted(loadPath=args.extractedLoad_path, savePath = args.extractedProcessed_path, 
                     statTypes=["ttest_apa", "cpearson_apa", "cspearman_apa", "anova_apa", "mwutest_apa", "wsrtest_apa", "cstest_apa", "ttest", "cpearson", "cspearman", "anova", "mwutest", "wsrtest", "cstest"]):
    
    #quickfix to import from different folder
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir) 
    sys.path.insert(0,parentdir) 
    from loadPaper import loadExtracted
    
    listOfExtData = loadExtracted(loadPath)
    sentSet = set()
    statCounter={}
    for extObj in listOfExtData:
        try:
            statCounter[extObj.statisticType] +=1
        except:
            statCounter[extObj.statisticType] =1
        if extObj.statisticType in statTypes: 
            tokens = parse_sentence(extObj.sentence)
            if len(tokens) > 0:
                sentSet.add(' '.join(tokens))
    out = codecs.open(savePath, 'w', 'utf-8')
    for sentence in sentSet:
            out.write(sentence + '\n')
            out.write(" \n")
    out.close()
    return sentSet, statCounter
    

def processExtOth(loadPaths=[args.extractedLoad_path, args.otherLoad_path], savePath = args.extOthProcessed_path):
    #quickfix to import from different folder
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir) 
    sys.path.insert(0,parentdir) 
    from loadPaper import loadExtracted
    
    sentSet = set()
    
    for l_path in loadPaths:
        listOfExtData = loadExtracted(l_path)
        for extObj in listOfExtData:
            tokens = parse_sentence(extObj.sentence)
            if len(tokens) > 0:
                sentSet.add(' '.join(tokens))
    
    out = codecs.open(savePath, 'w', 'utf-8')
    for sentence in sentSet:
            out.write(sentence + '\n')
            out.write(" \n")
    out.close()
    return sentSet
    
# In[ ]:


if __name__ == "__main__":
    print('Preprocessing whole Dataset ...')
    args()
    preprocess_Dataset(args)
    print('finished')

