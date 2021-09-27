from helpFunctions import *

## Bag of Words: check specific keywords from training that show special patterns ############################################################################
    #In: spaCy Doc object, Result object
    #out: Result object
def bagOfWordsSetFull(doc, output):
    print("bagOfWordsSetFull started")
    keywords = ["between", "correlated"]
    for token in doc:
        #between -----------------------------------------------------------------------------------------------------
        if keywords[0] in token.lower_: #token.lower_ == token.text.lower()
            output = handleBetween(doc, output)
        #correlated -----------------------------------------------------------------------------------------------------
        if keywords[1] in token.lower_:
            pearsonCorrelation(doc, output)
    return output

# if the word between is in a noun chunk: The part before "between". i=Aspect, after: conditions
#output: aspect, 1 sequence with condition(s)
#Results indicated that there were differences in satisfaction between pretest and posttest
def handleBetween(doc, output):
    for token in doc:
        #3. Basic Pattern: X between Y and Z
        if token.lower_ == "between":
            #aspect
            if token.nbor(-1).dep_ == "ROOT" and token.nbor(-2).dep_ == "auxpass":
                for nC in output.noun_chunks:
                    if nC[1]<token.i-2:
                        output.setaspect(nC[0], nC[1])
                        output.deleteNoun_Chunk(nC[0])
                        
                        output.setconditionBegin(token.i+1)
                        output.setconditionEnd(len(doc)-1)
                        output = checkExtractionNeatness(output)
                        output.printOutput(doc)

            for sequence in output.noun_chunks:
                if sequence[0] <= token.i <= sequence[1]:
                    if sequence[0] < 2:
                        output.setaspect(sequence[0], token.i-1)

                    #4. check if aspect goes even over verb
                    elif doc[sequence[0]].nbor(-1).dep_ == "ccomp" and doc[sequence[0]].nbor(-2).dep_ == "nsubj":
                        nC = getRightNounChunk(sequence[0]-2, output.noun_chunks)
                        if not nC == [-1,-1]:
                            output.setaspect(nC[0], token.i-1)
                            output.deleteNoun_Chunk(nC[0])
                    else:
                        #delete noun_chunks & add sequence to output object
                        output.setaspect(sequence[0], token.i-1)
                    output.deleteNoun_Chunk(sequence[0])
                    output.setconditionBegin(token.i+1)
                    output.setconditionEnd(sequence[1])
                    output.deleteNoun_Chunk(token.i+1)
    return output

#identify pearson correlations: Find: "correlated to" or "correlation with" in text
def pearsonCorrelation(doc, output):
    toggle = 0
    for toke2 in doc:
        if (toke2.text != "correlated" or toke2.text != "correlation") and toggle == 0:
            continue
        else:
            toggle = 1
        #1. & 2. two rules combined
        if toggle == 1 and (toke2.text == "with" or toke2.text == "to"):
            #aspect is from nounchunk before 'correlated' until 'with'
            conditionNC,wasteNC = getNounChunks(toke2.i, output.noun_chunks)
            output.setconditionBegin(conditionNC[0])
            output.setconditionEnd(toke2.i-1)
            output.setconditionBegin(toke2.i+1)
            output.setconditionEnd(len(doc)-1)
            for nc in output.noun_chunks:
                if nc[0]<=toke2.i:
                    continue
                else:
                    output.deleteNoun_Chunk(nc[0])  
                    output.printOutput(doc)
            #delete all nounChunks included
            output = checkExtractionNeatness(output)
            return output

## Check for comparative adjectives in doc #########################################################################
#If this rule fits, extracts Aspect(RMinus) & Conditions.
# specialcase jjrid-1
def comparativeAdjective(doc, output):
    print("Starting comparativeAdjectives")
    sconjId=-1
    aspectId = -1
    condition1Id = -1
    condition2Id = -1
    jjridList = checkForDetails(doc, "JJR", "tag_")
    if len(jjridList) == 1: 
        # 5. Integrade R- Rule: "Granger analysis" is a name, but Granger gets recognized as a jjr by PoS-tagger
        if doc[jjridList[0]].lower_ == "granger":
            print("Manual fix: Granger is not a jjr")
            jjrid = -1
        else:
            jjrid = jjridList[0]
    elif len(jjridList):
        print("Warning comparativeAdjectives: ambiguous results")
        jjrid = jjridList[0]
    else:
        jjrid = -1
    sconjIdList = checkForDetails(doc, "SCONJ", "pos_")
    if len(sconjIdList) == 1:
        sconjId = sconjIdList[0]
    else: 
        for token in sconjIdList:
            #if token.dep_ == "mark":
            if doc[token].dep_ == "prep":
                sconjId = token
                condition1Id = sconjIdList[0]+1
    if(jjrid == -1):# or doc[jjrid].dep_ == "advmod"
        for token in doc: #6. Exlusionrule: "more" is a jjr, but it is not for the usage of comparative adjectives
            if token.text == "more" and token.nbor(1).i ==sconjId:
                jjrid = token.i
        if jjrid != -1:
            print("Warning: JJR is probably 'more'")
        else:
            return output
    if(sconjId is -1):
        #7.-8. Rule: e.g. if at (... lower ... than ...) the 'than' is missing.
        output = compAdjwithoutSCONJ(doc, output, jjrid)
        return output
    else:
        #9. Basic Pattern: The head of the comparative adjective is the aspect, sconj is the second part of the adj: higher ... THAN"
        aspectId = doc[jjrid].head.i
        if doc[aspectId].n_lefts:
            aspectId = doc[aspectId].left_edge.i
        rootId = getRootIndice(doc)
        #10. Check if it is not the normal pattern, where the root is only an auxiliary verb. Find the real verb
        if doc[rootId].pos_ is not "VERB":
            tmp = findVerbOfAux(doc, rootId)
            if tmp is not -1:
                rootId = tmp
            else: #11. No Root Verb: Dependency Parser Error or corrupted example
                print("Error at finding the root (verb). This sentence is probably corrupted.")
        if condition1Id == -1: 
            if rootId == 1:
                condition1Id = 0
            else:
                condition1Id = doc[rootId].left_edge.i
        x = True
        for token in doc[sconjId].head.lefts:
            if token.text == doc[sconjId].text:
                #12. what to do if e.g. "than found in ..." then the sconj is longer than one word and we go in "else" later
                for token in doc[sconjId].head.rights:
                    if x:
                        sconj = (sconjId, token.i)
                        x = False
        if x:
            condition2Id = sconjId+1
        else:
            condition2Id = sconj[1]+1
        if sconjId is not -1:
            output.setaspect(aspectId, sconjId-1)
        else: #13. ExtraRule: No second NounChunk
            tmpListAspect = getRightNounChunk(aspectId, output.getNoun_Chunks())
            if tmpListAspect == [-1,-1]:
                print("Did not find end of aspect")
                output.setaspect(aspectId, tmpListAspect[1])
            else:
                output.setaspect(aspectId, tmpListAspect[1])
        #Combine all information in condition 1 and condition 2:
        #14. Condition1 :Get End of condition1 & finish the tuple
        for sequence in output.getNoun_Chunks():
            if sequence[0] <= condition1Id <= sequence[1]:
                if sequence[0] is not condition1Id:
                    condition1Id = sequence[0]
                    print("The aspect does not start at the beginning of the noun chunk! Fixed statically")
                output.setconditionBegin(condition1Id)
                output.setconditionEnd(sequence[1])
                output.deleteNoun_Chunk(condition1Id)
        #Condition2
        for sequence in output.getNoun_Chunks():
            if sequence[0] <= condition2Id <= sequence[1]:
                output.setconditionBegin(condition2Id)
                output.setconditionEnd(sequence[1])
                output.deleteNoun_Chunk(condition2Id)
        return output    
    

## Special case of comparativeAdjective: missing compoundpart to jjrid ######################################################
#a. if comparativeadjective part of a nounChunk -> = aspect & the one before is condition
#b. if comparative adjective between noun Chunks: condition is the nounchunk after the comparative adjective

def compAdjwithoutSCONJ(doc, output, jjrid):
    print("comparative adjective found, but no compound part") #cmpound part = sconj
    #print(output.noun_chunks,jjrid)
    [x, y] = getNounChunks(jjrid, output.noun_chunks)
    if y == []:
        y = getRightNounChunk(jjrid, output.noun_chunks)
        output.deleteNoun_Chunk(y[0])
        output.setaspect(y[0], y[1])
        output.deleteNoun_Chunk(x[0])
        output.setconditionBegin(x[0])
        output.setconditionEnd(x[1])
    else:
        output.printOutput(doc)
        output.deleteNoun_Chunk(y[0])
        output.setconditionBegin(y[0])
        output.setconditionEnd(y[1])
    return output

## if the root is an auxiliary verb, we want to find the verb, the auxiliary refers to ##############################
def findVerbOfAux(doc, auxId):
    root = -1
    get_children = doc[auxId].children
    if not get_children:
        print('No children found for {} the auxiliary as root.'.format(doc[rootSubTreeId]))
        return root    
    for child in doc[auxId].children:
        if child.is_punct:
            continue
            #print("Child is punctuation -> ignore")
        if child.pos_ == "VERB":
            #print('Child "{}" is the verb.'.format(doc[child.i]))
            return child.i
        else:
            if root == -1:
                root = findVerbOfAux(doc, child.i)
    return root