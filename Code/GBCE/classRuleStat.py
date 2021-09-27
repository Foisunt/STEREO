from helpFunctions import *

class RuleStat:
    def __init__(self, aspectBegin, aspectEnd, conditionBegin, conditionEnd, noun_chunks):
        self.noun_chunks = noun_chunks
        self.aspectBegin = aspectBegin
        self.aspectEnd = aspectEnd
        self.conditionBegin = conditionBegin
        self.conditionEnd = conditionEnd
        self.state = {"noun_chunks": 1, "aspect": 1, "conditions": 1}

    def __init__(self, noun_chunks):
        self.noun_chunks = noun_chunks
        self.aspectBegin = -1
        self.aspectEnd = -1
        self.conditionBegin = []
        self.conditionEnd = []
        #ease of use to check which attributes were already assigned
        self.state = {"noun_chunks": 1, "aspect": 0, "conditions": 0}
        
        
    #check if experimental data already found and for the transition from spans of indices to the output object
    def updateState(noun_chunks):
        #check noun_Chunks (should never be the case)
        if not noun_chunks:
            self.state["noun_chunks"] = 0
        else:
            self.state["noun_chunks"] = 1
        #check aspect 
        if getaspectBegin == -1:
            self.state["aspect"] = 0
        else:
            self.state["aspect"] = 1
        #check condition(s)
        if not getconditionBegin:
            self.state["conditions"] = 0
        else:
            self.state["conditions"] = 1
    
    #catch error from dependency parser with irregular noun phrases
    def checkNounChunks(self):
        for x in range(len(self.noun_chunks)-1):
            tmpNC = self.noun_chunks[x]
            nextNC = self.noun_chunks[x+1]
            if tmpNC[1] > nextNC[1]:
                print("Error: Dependecy Tree is not valid. Static fix.")
                nextNC = self.noun_chunks[x+1]
                newNoun = (tmpNC[0], nextNC[0]-1)
                self.deleteNoun_Chunk(tmpNC[0])
                self.noun_chunks.insert(x, newNoun)
        return self

    
    def getState(self):
        print(self.state["aspect"])
        return self.state
    def getaspectBegin(self):
        return self.aspectBegin
    def getaspectEnd(self):
        return self.aspectEnd
    def getconditionBegin(self):
        return self.conditionBegin
    def getconditionEnd(self):
        return self.conditionEnd
    def getConditionQuantity(self):
        return len(conditionBegin)
    def getNoun_Chunks(self):
        return self.noun_chunks
    def aspectToString(self, doc):
        span = doc[self.aspectBegin:(self.aspectEnd+1)]
        sVal = ""
        for token in span:
            sVal = sVal + token.text + " "
        return sVal
    def conditionsToStringList(self, doc):
        listSVals = []
        for x in range(len(self.conditionBegin)):
            span = doc[self.conditionBegin[x]:(self.conditionEnd[x]+1)]
            sVal = ""
            for token in span:
                sVal = sVal + token.text + " "
                print(token)
            listSVals.append(sVal)
        return listSVals

    def printOutput(self, doc):
        if self.state["aspect"]:
            print("Aspect from {} to {}".format(self.aspectBegin, self.aspectEnd))
            outputDocText(doc[self.aspectBegin:self.aspectEnd+1])
        else: 
            print("No Aspect found")
        if self.state["conditions"]:
            for x in range(len(self.conditionBegin)):
                print("Condition{} from {} to {}".format(x, self.conditionBegin[x], self.conditionEnd[x]))
                outputDocText(doc[self.conditionBegin[x]:self.conditionEnd[x]+1])
        else:
            print("No Conditions found")
        if self.state["noun_chunks"]:
            print("{} Noun_Phrases not assigned:".format(len(self.noun_chunks)))
            for noun in self.noun_chunks:
                outputPartOfDoc(doc, noun)
        else: 
            print("All noun phrases assigned")


    # replace a complete attribute with another
    def setaspectBegin(self, aspectBegin):
        self.aspectBegin = aspectBegin
        self.updateAspectState()
    def setaspectEnd(self, aspectEnd):
        self.aspectEnd = aspectEnd
        self.updateAspectState()
    def setaspect(self, aspectBegin, aspectEnd):
        if aspectBegin <= aspectEnd:
            self.aspectBegin = aspectBegin
            self.aspectEnd = aspectEnd
            self.updateAspectState()
        else:
            print("Error: Aspectbegin > Aspectend")

    def setconditionBegin(self, conditionBegin):
        self.conditionBegin.append(conditionBegin)
        self.updateConditionState()
    def setconditionEnd(self, conditionEnd):
        self.conditionEnd.append(conditionEnd)
        self.updateConditionState()
    def updateNoun_Chunks(self, noun_chunks):
        self.noun_chunks = noun_chunks
        self.updateNoun_ChunksState()


    #insert/append parameters in list attributes
    def insertCondition(self, indicator, conditionBegin, conditionEnd):
        self.conditionBegin.insert(indicator, conditionBegin)
        self.conditionEnd.insert(indicator, conditionEnd)
    def appendCondition(self, conditionBegin, conditionEnd):
        self.conditionEnd.append(conditionEnd)
        self.conditionBegin.append(conditionBegin)
    def insertconditionBegin(self, indicator, conditionBegin):
        self.conditionBegin.insert(indicator, conditionBegin)
    def insertconditionEnd(self, indicator, conditionEnd):
        self.conditionEnd.insert(indicator, conditionEnd)
    
    #delete  Noun_Chunk in which token x is included
    def deleteNoun_Chunk(self, x):
        if len(self.noun_chunks) == 1:
            print(self.noun_chunks)
            self.noun_chunks = []
            self.updateNoun_ChunksState()
           # print("Removed last Noun Chunk")
        else:
            for sequence in self.noun_chunks:
                if sequence[0] <= x <= sequence[1]:
                    self.noun_chunks.remove((sequence[0], sequence[1]))
                    self.updateNoun_ChunksState()
                    print("Removed ({}, {}) resulting in {}".format(sequence[0], sequence[1], self.noun_chunks))
                    break

    #delete  Noun_Chunk with span start-end
    def deleteNoun_Chunk2(self, start, end):
        for sequence in self.noun_chunks:
            if sequence[0] == start and sequence[1] == end:
                self.noun_chunks.remove((sequence[0], sequence[1]))
                self.updateNoun_ChunksState()

    def deleteAllHigherLowerNounChunks(self, pivot, toggle):
        #toggle = 1: all higher nounCHunks deleted, else all lower
        for sequence in self.noun_chunks:
            if toggle == 1:
                if i <= sequence[0] <= sequence[1]:
                    self.noun_chunks.remove((sequence[0], sequence[1]))
                    self.updateNoun_ChunksState()
                    print("Removed all higher Nouns ({}, {}) resulting in {}".format(sequence[0], sequence[1], noun_chunks))
                    self.deleteAllHigherLowerNounChunks(pivot, toggle)
            elif toggle == 2:
                if sequence[0] <= sequence[1] <= i:
                    self.noun_chunks.remove((sequence[0], sequence[1]))
                    self.updateNoun_ChunksState()
                    print("Removed all lower Nouns ({}, {}) resulting in {}".format(sequence[0], sequence[1], noun_chunks))
                    self.deleteAllHigherLowerNounChunks(pivot, toggle)
            else:
                prin("Error, wrong toggle in 'deleteAllHigherLowerNounChunks'")
                
    #only a helpfunction when splitting a condition
    def deleteconditionBegin(self, item):
        self.conditionBegin.remove(item)
    def updateAspectState(self):
        self.state["aspect"] = 1
    def updateConditionState(self):
        self.state["conditions"] = 1
    def updateNoun_ChunksState1(self, x):
        self.state["noun_chunks"] = x    
    def updateNoun_ChunksState(self):
        if len(self.noun_chunks):
            self.state["noun_chunks"] = 1
        else:
            self.state["noun_chunks"] = 0