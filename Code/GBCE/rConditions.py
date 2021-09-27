from helpFunctions import *

## Check if there is a relative clause in the doc. ################################################################################
#If there is, the nounChunk is part of a condition
    #In: spaCy Doc object, Result object
    #out: Result object
def findwhWords(doc, output):
    for token in doc:
        print(token.text + " " + token.tag_)
        if token.tag_ == "WDT" or token.tag_ == "WP" or token.tag_ == "WP$":
            if(token.nbor(-1).tag_) == ",":
                head = token.nbor(-2)
            else:
                head = token.nbor(-1)
            i = 0
            for token in doc:
                if head.is_ancestor(token):
                    i+=1
                if i == 2 or (token.is_ancestor(head) and i==1):
                    if token.is_punct:
                        continue
                    end = token.i-1
                    condition = getRightNounChunk(end, output.noun_chunks)
                    if condition == [-1,-1]:
                        print("wh-word not in a Noun phrase")
                    elif condition[0] <=head.i:
                        #check if head-end is in a nounchunk.
                        output.setconditionBegin(condition[0])
                        output.setconditionEnd(condition[1])
                        output.deleteNoun_Chunk(condition[0])
                        print( "Condition found in 'findWHWords' between {} and {}".format(condition[0], condition[1]))
                        return output
                        
                    else:
                        # if not merge the noun_chunks to one.
                        print("Warning: NounChunks should be merged from {} to {}".format(condition[0], end))
                        return output
                    i=2
                    break
            if i < 2:
                end = len(doc)-1
                print("Warning: End of relative clause not detected.")
                return output
        else:
            print("No Relative Clause")
            return output

def bagOfWordsSetCondition(doc, output):
    keywords = ["vs", "either", "compared", "among"]
    for token in doc:

        #vs -----------------------------------------------------------------------------------------------------
        if (keywords[0] == token.lower_ or "versus" == token.lower_):
            #print(token.i, output.noun_chunks)
            rightChunk = getRightNounChunk(token.i, output.noun_chunks)
            #print(rightChunk)
            if rightChunk == (-1, -1):
                [x, y] = getNounChunks(token.i, output.noun_chunks)
                output.deleteNoun_Chunk(x[0])
                output.setconditionBegin(x[0])
                output.setconditionEnd(x[1])
                output.deleteNoun_Chunk(y[0])
                output.setconditionBegin(y[0])
                output.setconditionEnd(y[1])
            else:
                print("not between")
        #either -----------------------------------------------------------------------------------------------------
        if keywords[1] == token.lower_ and token.nbor(1).text == "in":
            i = token.i
            while i < len(doc):
                tmpI = 0
                if doc[i].text == "in":
                    #write condition1Begin i+1
                    output.setconditionBegin(i+1)
                    tmpI +=1
                if doc[i].text == "or":
                    #write conditionEnd i-1
                    output.setconditionEnd(i-1)
                    #write conditionBegin i+1
                    output.setconditionBegin(i+1)
                    tmpI +=1
                i+=1
            output.setconditionEnd(i-1)
            output.deleteNoun_Chunk(i-1)
            
        #compared to     -----------------------------------------------------------------------------------------------
        if keywords[2] == token.lower_:
            for child in token.children:
                if child.text == "to":
                    token.nbor(-1).i
                    wasteChunk, rightChunk = getNounChunks(child.nbor(+1).i, output.noun_chunks)
                    #print(doc[token.nbor(-1).i].text)
                    #print(doc[child.nbor(+1)].text)
                    print(doc[token.i].text)
                    leftChunk = getRightNounChunk(token.nbor(-1).i, output.noun_chunks)
                    print("Leftchunk: " + str(leftChunk))
                    print("Rightchunk: " + str(rightChunk))
                    if rightChunk == leftChunk == (-1, -1):
                        print("keyword 'compared' found, but could not find fitting noun phrases")
                    elif leftChunk == (-1, -1):
                        #if leftChunk is already assigned, assign rightchunk
                        output.deleteNoun_Chunk(rightChunk[0])
                        output.setconditionBegin(rightChunk[0])
                        output.setconditionEnd(rightChunk[1])
                    elif rightChunk == (-1, -1):
                        #if rightchunk is already assigned, assign leftchunk
                        output.deleteNoun_Chunk(leftChunk[0])
                        output.setconditionBegin(leftChunk[0])
                        output.setconditionEnd(leftChunk[1])
                    else:
                        #right
                        output.deleteNoun_Chunk(rightChunk[0])
                        output.setconditionBegin(rightChunk[0])
                        output.setconditionEnd(rightChunk[1])
                        #left
                        output.deleteNoun_Chunk(leftChunk[0])
                        output.setconditionBegin(leftChunk[0])
                        output.setconditionEnd(leftChunk[1])

        #among --------------------------------------------------------------------------------------------------------
        if keywords[3] == token.lower_ or token.lower_ == "amongst":
            amongNC = getRightNounChunk(token.i, noun_chunks)
            if amongNC == (-1,-1):
                continue
            else:
                output.deleteNoun_Chunk(amongNC[0])
                output.setconditionBegin(token.i+1)
                output.setconditionEnd(amongNC[1])

    return output