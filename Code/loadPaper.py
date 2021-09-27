import json
import os
import re
import glob
from enum import Enum
from json import JSONEncoder
from collections import namedtuple
from pathlib import Path

class ExtractedData:
    def __init__(self,position,sentence, statisticType,record,aspect,condition):
        self.position = position; #information position (which sentence or position in sentence)
        self.sentence = sentence; #complete sentence where statisic has been found
        self.statisticType = statisticType; #e.g. t-Statisitc, regression, etc. #TODO als enum?
        self.record = record; #tupel of extracted values, e.g.(degOfFreedom,t-Statsitics,pvalue)
        self.aspect = aspect; #information about what the statisitcs are about
        self.condition = condition
#Load a File and return whole File as String

def loadJsonFile(path = "../../Cord-19/document_parses/pdf_json/e34e9be0e605d8e691716a6ca50e22b8ee4fb56a.json"):
    #print("Path: ", path)
    file = open(Path(path),"r")
    fileString = file.read().replace("\n", " ")
    file.close()
    return fileString
	
# returns a list of matched strings
def match11(regex, text):
    return re.findall(regex, text)
	
def seperateTextFromJson(jsonString):
    jsonDict = json.loads(jsonString)
    bodyText = jsonDict["body_text"]
    listOfTexts = list(map(lambda x: x.get("text"), bodyText))
    #the empty character determine how the strings are concatenated, "-" would put - between them.
    text = ''.join(listOfTexts) 
    return text
	
def loadJson(path = "../../Cord-19/document_parses/pdf_json/e34e9be0e605d8e691716a6ca50e22b8ee4fb56a.json"):
	#print("Json: ", path)
	jsonString = loadJsonFile(path)
	textTag = seperateTextFromJson(jsonString)
	return textTag

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

#filter on list to return only significant elements
def filterSignificance(splitText):
    regexFilterNumbers = '[0-9]';
    filteredList = list(filter(lambda x : match11(regexFilterNumbers,x) != [],splitText))
    return filteredList;

#loadsPaper and returns bodyText as List of sentences filtered: only numbers
def loadPaper(path = "../../Cord-19/document_parses/pdf_json/e34e9be0e605d8e691716a6ca50e22b8ee4fb56a.json"):
	text = loadJson(path)
	splitPos = matchPositions('\.\s?[A-Z]',text);
	splitText = splitAtPosition(splitPos,text);
	filteredText = filterSignificance(splitText)
	return filteredText

#returns list of all sentences in corpus
def loadCorpusAndFilter():
    paths = glob.glob("../../Cord-19/document_parses/pdf_json/*.json")
    paths = list(map(lambda path : path.replace("\ ","/"), paths))
    sentences = []
    for path in paths :
        sentences += loadPaper(path)
    return sentences

#append the new found rule to the dictionary for the respective stat type
def updateRplus(newRule,idn):
    #add rule to rPlus
    file = open(Path("rPlus.txt"), "a", encoding="utf-8")
    file.write("\n"+newRule)
    file.close()
    #create empty subrule File
    print('./subRules/' + "R" + str(idn) + '.txt')
    with open(Path('subRules', "R" + str(idn) + '.txt'), 'w') as fp:
        pass

#sType = rPlus for supp statistics, ttest for doF, sigNiv etc..
def loadKeyWords(sType):
    if sType == "rPlus":
        filename = "supStatistics" + ".txt"
    else :
        filename = "./supKeywords/" + str(sType) + ".txt"
    file = open(Path(filename))
    keyList = []
    lines = file.read().splitlines()
    for line in lines:
        keyList.append(line)
    file.close()
    return Enum(str(sType), keyList)

def defineStatisitc(sType):
    filename = "supStatistics" + ".txt"
    file = open(Path(filename))
    file.write("\n"+str(sType))
    file.close()
    #create empty subrule File
    with open(Path('supKeywords/' + str(sType) + '.txt'), 'w') as fp:
        pass


def defineKeywords(sType, keyWord):
    filename = "./supKeywords/" + str(sType) + ".txt"
    file = open(Path(filename))
    file.write("\n" + str(keyWord))
    file.close()


#append the new found rule to the set of rMinus rules
def updateRminus(newRule):
    file = open(Path("rMinus.txt"), "a", encoding="utf-8")
    file.write("\n"+newRule)
    file.close()


#append the new rules to the respective subRules dictionary
def updateSubRule(newRule, idn, overwrite = False):
    #update subRules IF statistic subRule for that statType already exists
    fileExists = os.path.isfile('./subRules/'+"R"+str(idn)+'.txt')
    if fileExists:
        file = open(Path('subRules', "R"+str(idn)+'.txt'), "a", encoding="utf-8")
        if overwrite:
            file.truncate(0)
            file.writelines(newRule)
        else:
            file.writelines(newRule+"\n")
        file.close()
    else:
        print("Could not find file in subRules directory with name R", idn)

#toRead from File ruleType rPlus, rMinus or subRule
def readRules(ruleType, idn=None):
    if ruleType == "subRule":
        filename = "subRules/" + "R" + str(idn) + ".txt"
    else:
        filename = ruleType + ".txt"
    file = open(Path(filename), encoding="utf-8")
    ruleList = []
    lines = file.read().splitlines()
    for line in lines:
        ruleList.append(line)
    file.close()
    return ruleList

def concatRules(ruleList):
    ruleSet = '|'.join(ruleList)
    return ruleSet


def validCheck(newRule,ruleType) :
    regex = "\(\?P\<(?P<key>[a-zA-Z-_]*)\>"
    if ruleType == "rMinus":
        return True
    validKey = loadKeyWords(ruleType)
    validKeysList = list(map(lambda x: x.name, validKey))
    while(newRule):
        ma = re.search(regex, newRule)
        if ma == None: break
        key = ma.groupdict()["key"]
        if key not in validKeysList:
            return False
        newRule = newRule[ma.span(0)[1] : -1]
    return True


def validityCheckRule(newRule, ruleType):
    re.compile(newRule)
    if not validCheck(newRule, ruleType):
        raise Exception('InvalidKey', 'InvalidKey2')


def updateExtracted(extraction, filename = "extracted.json"):
    extraxtionJson = json.dumps(extraction.__dict__)


    with open(Path(filename)) as json_file:
        data = json.load(json_file)
        temp = data['extractions']
        # appending data to emp_details
        temp.append(extraxtionJson)
        with open(Path(filename),'w') as f:
            json.dump(data, f, indent=4)

# checks if the .json files exists and if not creates a new file
def createExtractionFile(fileName):
    #check if files exists
    file = Path(fileName)
    if not file.is_file():
        #file does not exist
        with open(Path(file), 'w') as f:
            dict = {"extractions":[]}
            content = json.dump(dict, f, indent=4)
            
def delExtracted(filePath):
    p = Path(filePath)
    p.unlink()

def loadExtracted(filename = "extracted.json"):
    with open(Path(filename)) as f:
        extractedList = json.load(f)["extractions"]
        namedTupleList = list(map(lambda x: json.loads(x, object_hook = jsonToObject) ,extractedList))
        if len(namedTupleList[0]) <= 5:
            #added a new attribute "condition" to the ExtractedData datatype -> check here to still support old version
            result = list(map(lambda x: ExtractedData(x.position,x.sentence, x.statisticType,supExtracted(x.record),x.aspect, None), namedTupleList))
        else:
            result = list(map(lambda x: ExtractedData(x.position,x.sentence, x.statisticType,supExtracted(x.record),x.aspect, x.condition), namedTupleList))
        return result


def supExtracted(strangeObject):
    keys = strangeObject._fields
    record = dict()
    count = 0
    for key in keys:
        record[key] = strangeObject[count]
        count += 1
    return record

def jsonToObject(x):
    return namedtuple('X', x.keys())(*x.values())


#Increment the counter for documents or sentences
def incrementSkip(forDocuments = False):
    if forDocuments:
        with open(Path("skipCounterDocuments.txt"), "r") as f:
            counter = int(f.readline())
        counter += 1
        print(counter, type(counter))
        with open(Path("skipCounterDocuments.txt"), "w") as f:
            f.truncate(0)
            f.write(str(counter))
        with open(Path("skipCounter.txt"), "w") as f:
            f.truncate(0)
            f.write(str(0))
			
		
    else:
        with open(Path("skipCounter.txt"), "r") as f:
            counter = int(f.readline())
        counter += 1
        print(counter, type(counter))
        with open(Path("skipCounter.txt"), "w") as f:
            f.truncate(0)
            f.write(str(counter))
        
def readSkip(forDocuments = False):
    if forDocuments:
        with open(Path("skipCounterDocuments.txt"), "r") as f:
            counter = int(f.readline())
    else:
        with open(Path("skipCounter.txt"), "r") as f:
            counter = int(f.readline())
    return counter

def getType(rule):
    regex = "\(\?P\<(?P<key>[a-zA-Z-_]*)\>"
    ma = re.search(regex, rule)
    key = ma.groupdict()["key"]
    return key

#get every rPlus rule (except key:other) with the respective index, which is needed to
#load the correct subrules; returns a list of tupels: (rule, index)
def loadRelevantRPlus(other = False):
    file = open(Path("rPlus.txt"), encoding="utf-8")
    ruleList = []
    regex = "\(\?P\<(?P<key>[a-zA-Z-_]*)\>"
    lines = file.read().splitlines()
    index = 0
    for line in lines:
        ma = re.search(regex, line)
        if ma is None:
            index += 1
            continue
        key = ma.groupdict()["key"]
        if key == "other":
            if other:
                ruleList.append((line, index))
            index += 1
            continue
        else:
            if not other:
                ruleList.append((line, index))
        index += 1
    file.close()
    return ruleList
