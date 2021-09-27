#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import logging
import codecs
import sys

from pathlib import Path
from operator import add

import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
#tf.sysconfig.get_build_info()


from model import create_model
from reader import get_vocab
from argParseDummy import args


# In[ ]:


#load model, this method is quite inefficiant as it reuses the same code as is used to create the models in the first place
#this leads to no chance of compatability issues but also to an unneccesary kmeans run for init that is thrown away instantly
def loadModel(args,vocab, emb_path, saveFolder, k):
    load_dir = args.out_dir_path  / saveFolder /"model_param"
    model = create_model(args, vocab, emb_path, k)
    model.load_weights(filepath = load_dir)
    return model

#apply model to sentence
def applyABAE(sentence, model, vocab):
    from preprocess import parse_sentence
    from reader import is_number
    wordList = parse_sentence(sentence)
    num_hit, unk_hit, total = 0., 0., 0.
    indices = []
    for word in wordList:
        if is_number(word):
            indices.append(vocab['<num>'])
            num_hit += 1
        elif word in vocab:
            indices.append(vocab[word])
        else:
            indices.append(vocab['<unk>'])
            unk_hit += 1
        total += 1
        
    from tensorflow.keras.preprocessing import sequence
    indices = sequence.pad_sequences([indices], maxlen=args.maxlen)
    
    test_fn = K.function(model.get_layer('sentence_input').input, model.get_layer('p_t').output)
    pt = test_fn(([indices, []], np.ones((1, 1))))
    return pt[0]

def loadAspectWords(args, saveName, k=15):
    p = args.out_dir_path  / (saveName+str(k)) / 'aspect.log'
    content = None
    with p.open(encoding="utf-8") as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    aspectWords = [[y.split(":")[0] for y in content[1+3*x].split()] for x in range(int(len(content)/3))]
    return aspectWords

def loadInfAspectsDict(args, saveName):
    path = args.out_dir_path  / saveName / 'infAspects'
    infAspect_file = codecs.open(path, 'r', 'utf-8')
    aspDict = {}
    for i,aspect in enumerate(infAspect_file):
        aspDict[i]= " ".join(aspect.split()[1:])
    return aspDict


# In[ ]:


#use abae
def loadModelFromName(name):
    embDict = {"cord":args.cordEmb_path, "extr":args.extrEmb_path, "extO":args.extOthEmb_path}
    vocabPathDict = {"cord":args.cordVocabDict_path, "extr":args.extrVocabDict_path, "extO":args.extOthVocabDict_path}
    vocabDict = get_vocab(vocab_path = vocabPathDict[name[0:4]])
    model = loadModel(args, vocabDict, embDict[name[:4]], name, int(name[-2:]))
    infDict = loadInfAspectsDict(args, name)
    return model, vocabDict, infDict

def inference(sentence, model, vocabDict, infDict):
    pt = applyABAE(sentence, model, vocabDict)
    aspectNumber = np.argsort(pt)[-1]
    aspectName = infDict[aspectNumber]
    return aspectName


# In[ ]:


#this one and the cell below can be used for testing a single model.
#loading a model takes some time depending on the model, that's the reason this is split into two cells
#modelName = "extrModelExtr15"
#model, vocabDict, infDict = loadModelFromName(modelName)


# In[ ]:


#sentence = "A simple slopes test confirmed that the effect of having a child with a mental health condition was associated with increased negative affect for fathers (β = 1.43,  RPLUS MATCH ) but not for mothers (β = 0.27, t (977) = 0.74, p = .459"
#inference(sentence, model, vocabDict, infDict)


# In[ ]:


def useABAE(inPath, outPath, modelPath):
    inPath=Path(inPath)
    outPath=Path(outPath)
    modelPath=Path(modelPath)
    modelName=modelPath.parts[-1]
    model, vocabDict, infDict = loadModelFromName(modelName)
    
    import os,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir) 
    sys.path.insert(0,parentdir) 
    from loadPaper import loadExtracted, createExtractionFile, updateExtracted, delExtracted
    
    recordList = loadExtracted(inPath)
    if inPath == outPath:
        delExtracted(inPath)
    createExtractionFile(outPath)
    for r in recordList:
        r.aspect=inference(r.sentence, model, vocabDict, infDict)
        updateExtracted(r,outPath)
