from pathlib import Path
import loadPaper as pap
import GuiAskUser as gui
import random
import Utility as ut

#start the evaluation for uncovered sentences -> sentences in which nether a R+ rule nor a R- rule matches
def evaluationUncovered():
    currentLength = 0
    stat = 0
    nonStat = 0
    parseError = 0
    #load samples
    file = open(Path('./Evaluierung/Samples/extractedStatistics_uncoveredSamples.txt'), 'r', encoding="utf-8")
    sampleList = file.readlines()
    file.close()
    for sample in sampleList:
        answer = gui.callEvalUncovered(sample, len(sampleList)-currentLength) #answer: Stat, NonStat, ParseError
        if answer == 'Stat':
            stat += 1
        elif answer == "NonStat":
            nonStat += 1
        elif answer == "ParseError":
            parseError += 1
        currentLength += 1
    #write results into .txt
    file = open(Path('./Evaluierung/results.txt'), "a", encoding="utf-8")
    file.writelines("Uncovered: From"+str(len(sampleList))+" uncovered sentences, "+str(stat)+" contain statistics "+str(nonStat) +"do not"
                    " contain statistics and "+str(parseError)+" do contain a parse error\n")
    file.close()

#with given rules, call evalGUI and let user evaluate the results
def evaluation(stat):
    if stat != "rMinus":
        correct = 0
        currentLength = 0
        #load samples for respective test
        filename = Path('./Evaluierung/Samples/extractedStatistics_'+stat+'.json')
        extractedList = pap.loadExtracted(Path(filename))
        #let user evaluate the extracted samples
        for extracted in extractedList:
            answer = gui.callEval(extracted.sentence, len(extractedList)-currentLength, False, extracted)
            currentLength += 1
            if answer:
                #save how many of them are correct
                correct += 1
        #save results from evaluation
        file = open(Path('./Evaluierung/results.txt'), "a", encoding="utf-8")
        file.writelines(stat+": "+str(correct)+" from "+str(len(extractedList))+" are correct."+"\n")
        file.close()
    else:
        rMinusFile = open(Path('./Evaluierung/Samples/extracted_Rminus.txt'), 'r', encoding="utf-8")
        rMinusSamplesList = rMinusFile.readlines()
        rMinusFile.close()
        currentLength = 0
        correct = 0
        for sample in rMinusSamplesList:
            answer = gui.callEval(sample, len(rMinusSamplesList)-currentLength, True, None)
            currentLength += 1
            if answer:
                #save how many of them are correct
                correct += 1
        file = open(Path('./Evaluierung/results.txt'), "a", encoding="utf-8")
        file.writelines("R- :" +str(correct)+" from "+str(len(rMinusSamplesList))+" are correct."+"\n")
        file.close()

#and extract them into the corresponding evaluation file
def callCollectSamples(statType, sourceName='extractedSamples.json', capSize=200):
    #read the keywords
    supPath = "supStatistics" + ".txt"
    file = open(Path(supPath))
    statList = []
    lines = file.read().splitlines()
    for line in lines:
        statList.append(line)
    file.close()
    #get from extraxtedSamples
    filename = sourceName
    extractedList = pap.loadExtracted(Path(filename))
    for stat in statList:
        if stat != statType:
            continue
        sampleList = list(filter(lambda x: x.statisticType == stat, extractedList))
        random.shuffle(sampleList)
        filename = Path('./Evaluierung/Samples/extractedStatistics_'+stat+'.json')
        counter = 0
        for sample in sampleList:
            if counter < capSize:
                pap.updateExtracted(sample, filename)
            counter += 1
        print('Done with '+stat)


if __name__ == '__main__':
    #collect samples
    #print('Start sample collection.')
    #callCollectSamples()
    #callCollectOtherSamples()
    #call evalutation
    #ut.getUncoveredSentences(200)
    evaluation('rMinus')
    #evaluationUncovered()