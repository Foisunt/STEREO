#!/usr/bin/env python
# coding: utf-8

# In[2]:

from pathlib import Path

#what is saved in args, original this is a command line parser
#most params set tot the originals'
class args():
    
    #todo move cord dataset path here
    
    save_folder = Path("savedDataAndModels")
    
    pre_path = save_folder / "preprocessed.txt" #preprocessed cord dataset, big file
    filtered_path = save_folder / "filteredByPrePro.txt" #sentences that got filtered in the preprocessing step, non english
    
    extractedLoad_path = Path("../extractedSamples.json")
    extractedProcessed_path = save_folder / "processedExtracted.txt"
    
    otherLoad_path = Path("../extractedOther.json")
    extOthProcessed_path = save_folder / "processedExtOth.txt"
    
    
    cordVocab_path = save_folder / "cordVocabOcc"
    cordVocabDict_path = save_folder / "cordVocabDict.json"
    
    extrVocab_path = save_folder / "extrVocabOcc"
    extrVocabDict_path = save_folder / "extrVocabDict.json"
    
    extOthVocab_path = save_folder / "extOthVocabOcc"
    extOthVocabDict_path = save_folder / "extOthVocabDict.json"
    
    
    out_dir_path = save_folder / "outDirPath"    
    
    cordEmb_path = save_folder / "cordEmbW2V"
    extrEmb_path = save_folder / "extrEmbW2V"
    extOthEmb_path = save_folder / "extOthEmbW2V"
    
    evalSenTst_path = Path("..") / "evalSentencesAE" #dummy used for code-testing
    evalSenApa_path = Path("..") / "Evaluierung" / "AEapaSen"
    evalSenNonApa_path = Path("..") / "Evaluierung" / "AEnonApaSen"
    
    cordMin_count = 100 #pick such that w2v's vocab is geq than vocab_size
    extOthMin_count = 5 #gensims default
    extrMin_count = 3 #to cover 94% of data, 5 only covers 89% 
    
    emb_dim = 200
    vocab_size = 50000 
    
    batch_size = 32 #for extOth, for extr 10 was used
    #aspect_size = 20 #train multiple, param as list in train method
    epochs = 50
    neg_size = 20
    maxlen = 70
    seed = 1234
    algorithm = "adam"
    ortho_reg = 1
