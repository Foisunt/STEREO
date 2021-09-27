from helpFunctions import *


############################################################################################################################################
## Preprocessing Input: Text ###############################################################################################################

## Removing all statistics token ("RPLUS MATCH") and brackets since they cause problems for dependency parsing #############################
#Magnitude = |opening brackets| - |closing brackets|
#magnitude is necessary to also handle nested brackets.
    #In: String
    #Out: String
def handleRPLUSMATCH(text):
    text = checkForBrackets(text)
    startWindow = -1
    magnitude = 0
    sRPLUS = " RPLUS MATCH "
    badRPLUS = "  RPLUS MATCH )"
    matchBadRPLUS = text.find(badRPLUS)+1
    matchRPLUS = text.find(sRPLUS)
    for i in range(0,len(text)-1):
        if i == matchRPLUS:
            if startWindow == -1:
                if matchRPLUS == matchBadRPLUS:
                    rplusMatches, sText = handleRPLUSMATCH(text[0:matchRPLUS]+text[matchRPLUS+1+len(sRPLUS):len(text)])
                    rplusMatches.insert(0, matchRPLUS-2)
                else:
                    rplusMatches, sText = handleRPLUSMATCH(text[0:matchRPLUS]+text[matchRPLUS+len(sRPLUS):len(text)])
                    rplusMatches.insert(0, matchRPLUS-1)
                return [rplusMatches, sText]
        #opening bracket found -> magnitude ++
        if text[i] == "(":
            if magnitude == 0:
                startWindow = i
            magnitude += 1
        #even number of opening and closing brackets -> remove bracket
        if magnitude == 1 and text[i] == ")":
            newString = text[0:startWindow]+text[i+1:len(text)]
            rplusMatches, sText = handleRPLUSMATCH(newString)
            #RPLUS match in brackets
            if startWindow < matchRPLUS < i:
                rplusMatches.insert(0, startWindow-1)
            return [rplusMatches, sText]
        #more opening brackets, now one closing found  -> magnitude --
        elif magnitude > 1 and text[i] == ")":
            magnitude -= 1
    #if less closing brackets at the end -> delete everything from the opening of the bracket
    if magnitude > 0:
        rplusMatches = []
        sText = (text[0:startWindow])
        #RPLUS match in brackets
        if startWindow < matchRPLUS:
            rplusMatches.insert(0, startWindow-1)
        #print([rplusMatches, sText])
        return [rplusMatches, sText]
    #if nothing found, return empty
    return [[], text]

## Unifies all brackets to curved ones "()" ##########################################################################
    #In: String
    #Out: String
def checkForBrackets(text):
    if "[" in text:
        text = text.replace("[", "(")
        text = text.replace("]", ")")
    if "{" in text:
        text = text.replace("{", "(")
        text = text.replace("}", ")")
    return text

## Remove duplicate whitespaces ######################################################################################
    #In: String
    #Out: String
def whitespaceReduction(text):
    while "  " in text:
        text = text.replace("  ", " ")
    text.replace(" ,", ",")
    return text


## delete everything after a semicolon. (So far) no valuable information was excluded by doing so #####################
    #In: String
    #Out: String
def deleteSemicolon(text):
    semiColonPos = text.find(';')
    text = text[0:semiColonPos]
    return text


## check the input text two statistics combined in one sentence. Ask user to pick the prefered sentence ##############
    #In: String
    #Out: String
def checkAmountOfSentences(text):
    pivot = text.find("and there was")
    if pivot is not -1:
        while True:
            print(text)
            toggle = input("Two statistics detected. Which one to extract? Input: 1 or 2.")
            iToggle = int(toggle)
            if iToggle == 1: 
                return text[0:pivot-1]
            if iToggle == 2:
                return text[pivot+4 :len(text)]
    return text

##############################################################################################################################
##Preprocessing Input: Doc object ############################################################################################
    #in: spaCy Doc object
    #out: spaCy Doc object
## Check for root, if root not found, just return '[]'. Can be compressed into getRootIndice in iterateTree.
def modifyNounChunks(doc):
    rootId = -1
    noun_chunks = []
    rootId = getRootIndice(doc)
    #Help for bugfixing: getChildren(doc[rootId].children)
    if rootId >=0:
            noun_chunks = iterateTree(doc, rootId, noun_chunks)
    noun_chunks = combineNounChunks(doc, noun_chunks)
    #print("before: {}".format(noun_chunks))
    noun_chunks = extendQuotations(doc, noun_chunks)
    #print("after: {}".format(noun_chunks))
    return noun_chunks

## iterate topdown the tree to find nouns & nsubj & clausal subjects for noun_chunks #############################################
    #If sth is found: Noun phrase = from leftest child to rightest child of token 
    #Else, recursive call on child.
def iterateTree(doc, rootSubTreeId, noun_chunks):
    modList = ["nummod", "prep", "nmod", "appos", "acl", "advcl", "advmod", "amod"]
    get_children = doc[rootSubTreeId].children
    if not get_children:
        return noun_chunks    
    for child in doc[rootSubTreeId].children:
        if child.is_punct:
            continue
        if child.pos_ == "NOUN" or child.dep_=="nsubj" or child.tag_ == "NNP" or child.dep_ == "csubj":
            left = child.left_edge.i
            right = child.right_edge.i
            if left == 0:
                tmp = False
            else:
                tmp = True
            while tmp == True:
                tmp = False
                for mod in modList:
                    if doc[left].nbor(-1).dep_ == mod:
                        left -=1
                        if left == 0:
                            ...
                        else:
                            tmp = True
                        break
            tuple = (left, right)
            noun_chunks.append(tuple)
        else:
            iterateTree(doc, child.i, noun_chunks)
    return noun_chunks

##combine NounChunks that are only split by a modifier ##########################################################################
    #In: spaCy Doc object, List of tuples [(x,y)]
    #out: [(x,y)]
def combineNounChunks(doc, noun_chunks):
    modList = ["nummod", "prep", "nmod", "appos", "acl", "advcl", "advmod", "amod"]
    i=0
    while i < len(noun_chunks)-1:
        curr = noun_chunks[i]
        nex = noun_chunks[i+1]
        i+=1
        newNouns = []
        if nex[0]-curr[1] == 1:
            for mod in modList:
                if doc[curr[1]+1].dep_ == mod:
                    print(doc[curr[1]+1].text)
                    for nC in noun_chunks:
                        if nC[1] == curr[1]:
                            newNouns.append((curr[0],nex[1]))
                            continue
                        #dont add the next noun chunk 
                        if nC[1] == nex[1]:
                            continue
                        else: 
                            newNouns.append(nC)
        if newNouns == []:
            ...
        else:
            noun_chunks = newNouns
    return noun_chunks

## check doc for quotation marks and adapt noun phrases according to that ##############################################################
    #In: spaCy Doc object, List of tuples [(x,y)]
    #out: [(x,y)]
def extendQuotations(doc, noun_chunks):
    left = -1
    right = -1
    newNouns = []
    new2Nouns = []
    for token in doc:
        if (token.tag_ == "``" or token.tag_ == "''") and left == -1:
            left = token.i
            #print("set left {}".format(left))
            continue
        if (token.tag_ == "``" or token.tag_ == "''") and left != -1:
            right = token.i
            #print("set right {}".format(right))
        if left != -1 and right != -1:
            #print(left, right)
            for nC in noun_chunks:
                if nC[0] <=  left <= right <= nC[1]:
                    left = -1
                    right = -1
                    newNouns = []
                    break
                if left <= nC[0] <= nC[1] <= right:
                    newNouns.append((left,right))
                    continue
                #dont add the right noun chunk 
                else: 
                    newNouns.append(nC)
            #if there were 2 noun chunks inside quotations marks, the entry is now doubled. delete one of them:
            pre = (-1, -1)
            if newNouns == []:
                ...
            else:
                for nC in newNouns:
                    if pre == (-1, -1):
                        pre =nC
                        new2Nouns.append(nC)
                        continue
                    elif pre != nC:
                        pre = nC
                        new2Nouns.append(nC)
            left = -1
            right = -1
        if new2Nouns == []:
            ...
        else:
            noun_chunks = new2Nouns
            newNouns = []
            new2Nouns = []
    return noun_chunks
