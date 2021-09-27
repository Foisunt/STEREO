import texttable
import spacy

## check the conditions for enumerations -> Split the condition in different conditions ########################################################
#only works on output object with non-empty conditions
    #in: spaCy Doc object, not empty Result object
    #out: Result object
def checkForEnumerations(doc, output):
    print("Starting checkForEnumerations")
    #case 1: Check if enumeration with more than 2 conditions
    for token in doc:
        if token.tag_ ==",":
            conditionBegin = output.getconditionBegin()
            conditionEnd = output.getconditionEnd()
            for x in range(len(conditionBegin)):
                if (conditionBegin[x] < token.i < conditionEnd[x]): #if token is part of a condition ...
                    tempConditionEnd = conditionEnd[x]
                    output.insertconditionEnd(x, token.i-1)
                    output.insertconditionBegin(x+1, token.i+1)
                    #refresh temporal vars after manipulations
                    conditionBegin = output.getconditionBegin()
                    conditionEnd = output.getconditionEnd()

    #case 2: Check if enumeration with a comparing conjunction
        if token.pos_ == "CCONJ": #if token is a coordinating conjunction
            conditionBegin = output.getconditionBegin()
            conditionEnd = output.getconditionEnd()
            print("CONJUNCTION '{}' FOUND".format(token.text))

            for x in range(len(conditionBegin)):
                if (conditionBegin[x] == token.i):

                    output.deleteconditionBegin(conditionBegin[x])
                    output.insertconditionBegin(x, token.i+1)

                elif (conditionBegin[x] < token.i < conditionEnd[x]): #if token is part of a condition ...
                    output.insertconditionBegin(x+1, token.i+1)
                    output.insertconditionEnd(x, token.i-1)
    return output


## function that iterates through the doc to check for words with special properties ############################################################
#returns first item found.
def checkForDetails(doc, item, option):
    idList = []
    if option == "tag_":
        for token in doc:
            if (token.tag_ == item):
                id = token.i
                idList.append(id)
    if option == "dep_":
        for token in doc:
            if (token.dep_ == item):
                idList.append(id)
                idList.append(id)
    if option == "pos_":
        for token in doc:
            if (token.pos_ == item):
                id = token.i
                idList.append(id)
    return idList

## Cleanup of noun phrases: Check the leftover nounchunks. If they overlap conditions or aspects remove them #################################################################
def checkExtractionNeatness(output):
    if output.state["conditions"]:
        for x in range(len(output.conditionBegin)):
            for nc in output.noun_chunks:
                if output.conditionBegin[x] <= nc[0] <= output.conditionEnd[x] or output.conditionBegin[x] <= nc[1] <= output.conditionEnd[x] or nc[0] <= output.conditionBegin[x] <= nc[1] or nc[0] <= output.conditionEnd[x] <= nc[1]:
                    print("Auto", end= "-")
                    output.deleteNoun_Chunk(nc[0])
                    output = checkExtractionNeatness(output)
    if output.state["aspect"]:
        for nc in output.noun_chunks:
            if output.aspectBegin <= nc[0] <= output.aspectEnd or output.aspectBegin <= nc[1] <= output.aspectEnd:
                print("Auto", end= "-")
                output.deleteNoun_Chunk(nc[0])
                output = checkExtractionNeatness(output)
    return output

## Find noun_chunk where id (id = position of token in doc) is in range ########################################################################
    #Input: Noun_Chunks and id
    #output: list (if nothing found: [-1,-1])
def getRightNounChunk(id, noun_chunks):
    for nounChunk in noun_chunks:
        if nounChunk[0]<=id<=nounChunk[1]:
            return nounChunk
    return (-1,-1)

## Find noun_chunk where 'id' is between two noun chunks #######################################################################################
    # Input: Noun_Chunks and id [(5,10), (12,16)]
    #output: list (if nothing found: [(-1,-1),(-1,-1)]), if no nounchunk after id: [x,(-1,-1)])
def getNounChunks(id, noun_chunks):
    tmp1 = (-1,-1)
    for nounChunk in noun_chunks:
        if nounChunk[0]<=nounChunk[1]<=id:
            tmp1 = nounChunk
        if id<=nounChunk[0]<=nounChunk[1]:
            return (tmp1, nounChunk)
    return [tmp1,(-1,-1)]


## Helpfunction for debugging of noun_phrasing ###############################
#prints out all the children of specific token y
def getChildren(y):
    for x in y:
        print (x.text)

## Helpfunction: get the Root of the doc object #################################################################################
def getRootIndice(doc):
    rootId=-1
    for token in doc:
        if (token.dep_ == "ROOT"):
            rootId = token.i
    return rootId

#### Output Functions ########################################################################################################################
#Function for output of PoS-Tags as table
def outputSentenceData(doc):
    t = texttable.Texttable()
    t.add_row(['Nr', 'Text', 'dep_', 'pos_', 'tag_', 'depEx', 'posEx', 'tagEx'])
    iWord = 0
    for token in doc:
        t.add_row([iWord, token.text, token.dep_, token.pos_, token.tag_,spacy.explain(token.dep_), spacy.explain(token.pos_), spacy.explain(token.tag_)])
        iWord+=1
    print(t.draw())

def outputPartOfDoc(doc, nounChunk):
    span = doc[nounChunk[0]:nounChunk[1]]
    print("{}:".format(nounChunk), end = " ")
    for token in span:
        print(token.text, end = " ")
    print(doc[nounChunk[1]], end = " ")
    print(" ")

def outputDocText(doc):
    text=""
    for token in doc:
        text = text + " " +token.text
    print (text)

## Load Sentences ###########################################################################
def loadTXTtoList():
    with open ("sampleSentences.txt", "r") as myfile:
        data=myfile.readlines()
    return data

#output: List of extracted objects. Read out sentence string with listObjects[x].sentence
#alternative datasource: "extractedSamples.json"
def loadJSONtoList():
    return pap.loadExtracted("extracted.json")