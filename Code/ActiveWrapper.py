import glob
import re
import loadPaper as pap
import GuiAskUser as gui
import Utility as ut
import langdetect as langdect
import sys

#regexes: List of regex pattern for the respective statistics
def activeWrapperAllPaths(directory="../../Cord-19/document_parses/pdf_json"):
    paths = glob.glob(directory+"/*.json")
    paths = list(map(lambda path : path.replace("\ ","/"), paths))
    #load rPlus rules from saved file
    rPlusList = pap.readRules("rPlus")
    #load rMinus rules from saved file
    rMinusList = pap.readRules("rMinus")
    toSkip = pap.readSkip()
    print(toSkip)
    documentSkip = pap.readSkip(True)
    print(documentSkip)

    for path in paths:
        #skip the next <documentSkip> documents
        if documentSkip > 0:
            documentSkip -= 1
            continue
        #load paper,split in sentences, and filter not numbers
        sentences = pap.loadPaper(path)
        print(path)
        # '$^' #Initial Rule matches nothing
        activeWrapperLoop(sentences, rPlusList, rMinusList, toSkip)
        #finished with that document -> increment skip counter for documents
        pap.incrementSkip(True)


def activeWrapperLoop(sentences, rPlusList, rMinusList, toSkip):
    #while senteces not empty
    foundEntitys = []
    extracted = []
    
    while sentences:
        #maybe better from front?
        sentence = sentences.pop() #get and remove last element
        try:
            en = False
            for lang in langdect.detect_langs(sentence):
                if str(lang)[0:2]=="en":
                    en = True
            if not en:
                break
        except:
            break

        #extract statistics for each sentence
        while sentence: #checks if string is empty
            #apply R+
            match = ut.applyRPlus(rPlusList, sentence)[0]
            rPlusList = pap.readRules("rPlus")
            idn = len(rPlusList)
            
            if match is None:
                matchList = ut.applyRMinus(rMinusList, sentence)   #apply R-
                if ut.checkForNumbers(matchList, sentence):
                    
                    if toSkip > 0:
                        toSkip -= 1
                        break
                    #Start Interaction
                    skip = gui.callGui(sentence, idn, matchList)
                    #update Dictionary for current session
                    rPlusList = pap.readRules("rPlus")
                    rMinusList = pap.readRules("rMinus")
                    idn = len(rPlusList)
                    if skip:
                        pap.incrementSkip()     #increment skip counter
                        #break loop, because this sentence must to be skipped
                        break
                    else:
                        continue
                else:
                    
                    break
            else:
                
                #Found match -> Extract Data and add
                endOfMatch = match.span(0)[1]
                startOfMatch = match.span(0)[0]
                (matchEntity, ruleIndex) = ut.applyRPlus(rPlusList, sentence)
                entity = ut.extractEntity(matchEntity, sentence, ruleIndex)
                while not checkRecord(entity):
                    #call GUI- fixSubrules
                    #actual used rule: rPlusList[ruleIndex]
                    #list of subRules: pap.readRules("subRule", ruleIndex)
                    skip = gui.callFixSubRules(entity, pap.readRules("subRule", ruleIndex), rPlusList[ruleIndex], ruleIndex)
                    if not skip:
                        #skip not used -> extract with new subrule(s)
                        entity = ut.extractEntity(matchEntity, sentence, ruleIndex)
                    else:
                        #break out of fixSubRules routine
                        break
                extracted.append(entity)
                pap.updateExtracted(entity)
                sentence = sentence[0: startOfMatch] + " RPLUS MATCH " + sentence[endOfMatch:len(sentence)]

    return foundEntitys

#True if record is complete
def checkRecord(entity):
    if entity.statisticType == "other" : return True
    if None not in entity.record.values():
        return True
    else:
        return False

def main():
    arguments = sys.argv
    if len(arguments) < 2:
        activeWrapperAllPaths()
    else:
        activeWrapperAllPaths(arguments[1])

main()