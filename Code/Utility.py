import loadPaper as pap
import re
from pathlib import Path
import glob

#checks if a number can be found in sentence after already found matches are deleted
def checkForNumbers(matchList, sentence):
    if matchList != []:
        #sort matchList according to (start, end)
        spanList = list(map(lambda match: [match.span(0)[0], match.span(0)[1]], matchList))
        spanList.sort(key=lambda interval: interval[0])
        merged = [spanList[0]]
        for current in spanList:
            previous = merged[-1]
            if current[0] <= previous[1]:
                previous[1] = max(previous[1], current[1])
            else:
                merged.append(current)

        merged.reverse()
        #get rid of every found match
        for span in merged:
            endOfMatch = span[1]
            startOfMatch = span[0]
            sentence = sentence[0: startOfMatch] + sentence[endOfMatch:len(sentence)]

    #check for any number
    match = re.search("\d", sentence)
    if match:
        return True
    else:
        return False

# applies RPlus rules in a certain order and returns a tuple of match and the index of the matched rule
def applyRPlus(rulesList, sentence):
    for condition in [lambda i: 'apa' in pap.getType(rulesList[i]),
              lambda i: not 'apa' in pap.getType(rulesList[i]) and not 'other' == pap.getType(rulesList[i]),
              lambda i: 'other' == pap.getType(rulesList[i])]:
        for i in range(1,len(rulesList)):
            match = None
            if condition(i):
                match = re.search(rulesList[i], sentence)
            if match is not None:
                return (match, i)
    return (None, None)

#returns a list of matches
def applyRMinus(ruleList, sentence):
    #matchList = list(map(lambda rule: re.matchAll(rule, sentence), ruleList))
    matchList = []
    for rule in ruleList:
        for m in re.finditer(rule, sentence):
            matchList.append(m)
    return matchList

# extracts match from sentence with the rules specified at row number idn in rPlus file
def extractEntity(match, sentence, idn):
    #get the found match
    dic = match.groupdict()
    #determine the statistic type of the record
    filtered = {k: v for k, v in dic.items() if v is not None} #only not None keys
    key = list(filtered.keys())[0] #its always just one because of re.search method
    endOfMatch = match.span(0)[1]
    subSentence = sentence[match.span(0)[0]:endOfMatch]
    record = extractNumbers(key, subSentence, idn)
    return pap.ExtractedData(None, sentence[0:endOfMatch], key, record, None, None)


def extractNumbers(statType, subSentence, idn):
    #subRulesDict = load file dependent on StatType
    subRuleList = pap.readRules("subRule", idn)
    #subRulesDict = lod.openDict('./subRules/'+statType+'.txt')
    record = dict()
    keyWords = pap.loadKeyWords(statType)
    keyList = list(map(lambda x: x.name, keyWords))
    for key in keyList:
        record[key] = None

    #for every subrule in given list, search for the match an extract the value into record
    for rule in subRuleList:
        match = re.search(rule, subSentence)
        if not match is None:
            dictn = match.groupdict()
            for key in dictn.keys():
                record[key] = match.groupdict()[key]
    return record
    
#apply one rule on a given document and save the extractions
def extractFromDocument(rule, documentId):
    path = "../../Cord-19/document_parses/pdf_json/"+documentId+".json"
    doc = pap.loadPaper(path)
    rPlusList = pap.readRules("rPlus")
    extracted = []
    for s in doc:
        match = re.search(rule, s)
        if match:
            #extract
            (matchEntity, ruleIndex) = ut.applyRPlus(rPlusList, s)
            entity = ut.extractEntity(matchEntity, s, ruleIndex)
            if checkRecord(entity):
                extracted.append(entity)
                pap.updateExtracted(entity)
            else:
                #call GUI- fixSubrules
                #actual used rule: rPlusList[ruleIndex]
                #list of subRules: pap.readRules("subRule", ruleIndex)
                gui.fixSubRules(entity, pap.readRules("subRule", ruleIndex), rPlusList[ruleIndex], ruleIndex)


def loadPaths():
    ps = glob.glob("../../CORD-19/document_parses/pdf_json/*.json")
    ps = list(map(lambda pa: pa.replace("\ ", "/"), ps))
    return ps

def getUncoveredSentences(amount):
    ps = loadPaths()
    documentCounter = 501
    rPlusList = pap.readRules('rPlus')
    rMinusList = pap.readRules('rMinus')
    sentencesList = []
    while len(sentencesList) < amount:
        doc = pap.loadPaper(ps[documentCounter])
        for s in doc:
            if applyRPlus(rPlusList, s)[0] is None:
                matchList = applyRMinus(rMinusList, s)
                if checkForNumbers(matchList, s):
                    sentencesList.append(s)
                    documentCounter += 1
                    break
        documentCounter += 1
    with open(Path('./Evaluierung/Samples/uncoveredSamples.txt'), 'w+', encoding='utf-8') as file:
        for s in sentencesList:
            file.write("%s\n" % s)
    file.close()
