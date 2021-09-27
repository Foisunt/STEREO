import glob
import loadPaper as pap
import time
import re
import threading
import multiprocessing
import concurrent.futures
import Utility as ut
from random import *
from pathlib import Path
from tqdm import tqdm

AMOUNT_DOCS = 5000
amountSentences = 0
withDigit = 0
counterS = 0


def tryTaskPool(lock, rule):
    global count, paths, index
    lock.acquire()
    tmpIndex = index
    index += 1
    lock.release()
    sentences = pap.loadPaper(paths[tmpIndex])
    for s in sentences:
        foundMatch = re.search(rule, s)
        if foundMatch:
            lock.acquire()
            count += 1
            lock.release()

#returns, on how many sentences the given rule is applicable
#stop how many sentences hall be evaluated, -1 = all
def evaluateRule(rule):
    t0 = time.time()
    ps = loadPaths()

    #iterate over all paths, contained in the corpus
    cpuCount = multiprocessing.cpu_count()
    amountDocs = len(ps)
    lock = threading.Lock()

    threadList = []
    for t in range(cpuCount):
        start = amountDocs//cpuCount*t
        end = start+amountDocs//cpuCount
        if t == cpuCount-1:
            end += amountDocs % cpuCount
        else:
            end -= 1
        threadList.append(threading.Thread(target=thread_task, args=(lock, rule, start, end)))

    # start threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(thread_getRminus, param) for param in threadList]
    results = [f.result() for f in futures]

    print('Amount matches in sentences: ', sum(results))

    t1 = time.time()
    print("Duration: ", (t1-t0))


def thread_task(lock, rule, start, end):
    #print("Inside a thread:", start, end)
    count = 0
    sentences = []
    for k in range(start, end):
        sentences = pap.loadPaper(paths[k])
        for s in sentences:
            foundMatch = re.search(rule, s)
            if foundMatch:
                lock.acquire()
                count += 1
                lock.release()
    return count

#apply rule on randomly selected 1000 rules and return the amount of matches
def tryRule(rule):
    t1 = time.time()
    ps = loadPaths()
    #get AMOUNT_DOCS random selected numbers from between 1 and maximum documents in dataset and save it in a list
    docList = []
    counter = AMOUNT_DOCS
    while counter > 0:
        docNumb = randint(0, len(ps)-1)
        if docList.count(docNumb) == 0:
            docList.append(docNumb)
            counter -= 1

    cpuCount = multiprocessing.cpu_count()
    lock = threading.Lock()
    threadList = []
    for t in range(cpuCount):
        start = AMOUNT_DOCS//cpuCount*t
        end = start+AMOUNT_DOCS//cpuCount
        if t == cpuCount-1:
            end += AMOUNT_DOCS % cpuCount
        else:
            end -= 1
        threadList.append((lock, rule, start, end, docList, ps))

    global count
    count = 0
    # start threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(thread_tryRule, param) for param in threadList]
    results = [f.result() for f in futures]

    t2 = time.time()
    print("Dauer: ", t2-t1)
    return sum(results), count


#lock[0], rule[1], start[2], end[3], docList[4], ps[5]
def thread_tryRule(param):
    lock = param[0]
    rule = param[1]
    start = param[2]
    end = param[3]
    docList = param[4]
    ps = param[5]
    global count
    print(start, end)
    docs = [] #list of sentences from chosen documents
    #load the specific papers with index numbers given in docList
    for i in range(start, end):
        index = docList[i]
        docs = docs + pap.loadPaper(ps[index])
    for s in docs:
        match = re.search(rule, s)
        if match:
            lock.acquire()
            count += 1
            lock.release()
    return len(docs)

#extract sentencs in which given rules is apperent, rule is a list of tuples: (rule, index)
#index indicate which subrule file are needed for extraction
def extractSamples(rule, fileName):
    t1 = time.time()
    cpuCount = multiprocessing.cpu_count()
    lock = multiprocessing.Lock()
    threadList = []
    ps = loadPaths()
    n = len(ps)
    for t in range(cpuCount):
        start = n//cpuCount*t
        end = start+n//cpuCount
        if t == cpuCount-1:
            end += n % cpuCount
        else:
            end -= 1
        threadList.append((lock, rule, start, end, fileName, ps, t))

    processes = [multiprocessing.Process(target=thread_extractSamples, args=param) for param in threadList]
    #start processes
    for p in processes:
        p.start()
    #wait until the processes finished
    for p in processes:
        p.join()

    t2 = time.time()
    print("Duration: ", t2-t1)


#lock[0], rule[1], start[2], end[3], fileName[4]
def thread_extractSamples(lock, tupleList, start, end, fileName, documentPaths, idn):
    #load paths to documents
    print(start, end)
    #load the specific papers with index numbers given in docList
    for i in range(start, end):
        docs = pap.loadPaper(documentPaths[i])
        if i-start == (end-start)*0.25 or i-start == (end-start)*0.5 or i-start == (end-start)*0.75:
            save_print("ID: ", idn, " at ", i, " and ", (end-i), " more to go.")
        for s in docs:
            #apply rules isolated
            for rule in tupleList:
                #rule is a tuple: (regex, index)
                match = re.search(rule[0], s)
                if match:
                    while re.search(rule[0], s):
                        match = re.search(rule[0], s)
                        #if a match is found -> save it in a .txt file
                        lock.acquire()
                        entity = ut.extractEntity(match, s, rule[1])
                        pap.updateExtracted(entity, fileName)
                        s = s[0: match.start()] + " RPLUS MATCH " + s[match.end():len(s)]
                        lock.release()


#get random #amount of sentences classified as R-
def collectMinusSentences(amount, directory="../../CORD-19/document_parses/pdf_json/"):
    global amountSentences
    amountSentences = amount
    t1 = time.time()
    ps = loadPaths(directory)
    docList = []
    counter = 1000
    #get 1000 random selected numbers from between 1 and maximum documents in dataset and save it in a list
    while counter > 0:
        docNumb = randint(0, len(ps)-1)
        if docList.count(docNumb) == 0:
            docList.append(docNumb)
            counter -= 1

    cpuCount = multiprocessing.cpu_count()
    lock = threading.Lock()
    threadList = []
    for t in range(cpuCount):
        start = 1000//cpuCount*t
        end = start+1000//cpuCount
        if t == cpuCount-1:
            end += 1000 % cpuCount
        else:
            end -= 1
        threadList.append((lock, start, end, docList, ps))

    # start threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(thread_getRminus, param) for param in threadList]
    results = [f.result() for f in futures]

    t2 = time.time()
    print("Dauer: ", t2-t1)


#lock[0], start[1], end[2], docList[3], ps[4]
def thread_getRminus(param):
    global ps, amountSentences
    lock = param[0]
    start = param[1]
    end = param[2]
    docList = param[3]
    ps = param[4]
    #load rPlus rules from saved file
    rPlusList = pap.readRules("rPlus")
    #load rMinus rules from saved file
    rMinusList = pap.readRules("rMinus")
    print(start, end)
    docs = [] #list of sentences from chosen documents
    #load the specific papers with index numbers given in docList
    for i in range(start, end):
        docs = pap.loadPaper(ps[docList[i]])
        for s in docs:
            #apply rules
            match = ut.applyRPlus(rPlusList, s)[0]
            if not match:
                matchList = ut.applyRMinus(rMinusList, s) #get all R- matches
                if not ut.checkForNumbers(matchList, s):
                    #no digit in s is unmatched -> extract
                    lock.acquire()
                    #not rPlus but rMinus
                    if amountSentences > 0:
                        amountSentences -= 1
                        file = open(Path("./Evaluierung/Samples/extracted_Rminus.txt"), "a", encoding="utf8")
                        file.write(s+"\n")
                        file.close()
                        lock.release()
                    else:
                        lock.release()
                        break
    return len(docs)


#load the path list for the file in CORD-19
def loadPaths(directory="../../CORD-19/document_parses/pdf_json/"):
    ps = glob.glob(directory+"/*.json")
    ps = list(map(lambda pa: pa.replace("\ ", "/"), ps))
    return ps

def countSentences():
    global ps
    loadPaths()

    cpuCount = multiprocessing.cpu_count()
    lock = threading.Lock()
    threadList = []
    n = len(ps)
    for t in range(cpuCount):
        start = n//cpuCount*t
        end = start+n//cpuCount
        if t == cpuCount-1:
            end += n % cpuCount
        else:
            end -= 1
        threadList.append((lock, start, end))

    global withDigit, counterS
    # start threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(thread_countSentences, param) for param in threadList]
    results = [f.result() for f in futures]

    print('Sentences overall: ', counterS)
    print('With digits: ', withDigit)


#lock[0], start[1], end[2]
def thread_countSentences(param):
    global ps, counterS, withDigit
    lock = param[0]
    start = param[1]
    end = param[2]
    print(start, end)
    docs = [] #list of sentences from chosen documents
    #load the specific papers with index numbers given in docList
    for i in range(start, end):
        text = pap.loadJson(ps[i])
        splitPos = pap.matchPositions('\.\s?[A-Z]', text)
        sen = pap.splitAtPosition(splitPos, text)
        lock.acquire()
        counterS += len(sen)
        lock.release()
        docs = docs + sen

    for s in docs:
        #apply rules
        match = re.search('\d', s)
        if match:
            lock.acquire()
            withDigit += 1
            lock.release()

    return len(docs)

#count how many sentences are not covered by any rule
def evaluateCoverage(amountPaper):
    ps = loadPaths()
    docList = []
    counter = amountPaper
    t1 = time.time()
    while counter > 0:
        docNumb = randint(1000, len(ps))
        if docList.count(docNumb) == 0:
            docList.append(docNumb)
            counter -= 1
    print(len(docList))
    cpuCount = multiprocessing.cpu_count()
    threadList = []
    n = amountPaper
    for t in range(cpuCount):
        start = n//cpuCount*t
        end = start+n//cpuCount
        if t == cpuCount-1:
            end += n % cpuCount
        else:
            end -= 1
        threadList.append((start, end, docList, ps, t))

    results = []
    processes = [multiprocessing.Process(target=thread_evaluateCoverage, args=param) for param in threadList]

    #start processes
    for p in processes:
        p.start()
    #wait until the processes finished
    for p in processes:
        p.join()

    for i in range(cpuCount):
        file = open(Path('./tmp/Thread'+str(i)+'.txt'), 'r')
        sC, mC = file.read().splitlines()
        results.append((int(sC), int(mC)))

    print(results)
    buf = list(zip(*results))
    res = sum(buf[1])/sum(buf[0])
    print('Duration: ',time.time()-t1)
    return res

#param[0] = start, param[1] = end, param[2] = docList, param[3] = id, param[4] = ps, param[5] = id
def thread_evaluateCoverage(start, end, docList, ps, idn):
    sentenceCounter = 0
    missedCounter = 0
    file = open(Path('./tmp/Thread'+str(idn)+'.txt'), 'w+')
    index = 0
    print(id, start, end)
    #load rPlus rules from saved file
    rPlusList = pap.readRules("rPlus")
    #load rMinus rules from saved file
    rMinusList = pap.readRules("rMinus")
    save_print("Start thread: ", idn)
    for i in range(start, end):
        if i % 10 == 0:
            save_print("ID: ", idn, " at ", i, " and ", (end-i), " more to go.")
        index = docList[i]
        sentences = pap.loadPaper(ps[index])
        for s in sentences:
            sentenceCounter += 1
            matchList = ut.applyRMinus(rMinusList, s)
            if ut.checkForNumbers(matchList, s):
                match = ut.applyRPlus(rPlusList, s)[0]
                if match is None:
                    missedCounter += 1
    file.write(str(sentenceCounter))
    file.write('\n')
    file.write(str(missedCounter))
    file.close()
    
print_lock = threading.Lock()
def save_print(*args, **kwargs):
  with print_lock:
    print (*args, **kwargs)


def countKeywords():
    extractedList = pap.loadExtracted('extractedSamples.json')
    extractedDict = {}
    for extracted in extractedList:
        tmpVal = extractedDict.get(extracted.statisticType)
        if tmpVal is None:
            extractedDict.update({extracted.statisticType: 1})
        else:
            extractedDict[extracted.statisticType]= tmpVal + 1
    print(extractedDict)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    #res = evaluateCoverage(1000)
    #print("Amount of sentences not covered in CORd-19: ",res)
    ruleList = pap.loadRelevantRPlus()
    extractSamples(ruleList, "./extractedSamples.json")
