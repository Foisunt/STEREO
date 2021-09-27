from helpFunctions import *

## R Minus Rules: Rules, that remove noun phrases without assigning them as conditions ##################################################################################
def rMinus(doc, output):
    noun_chunks = output.getNoun_Chunks()
    for token in doc:
        #if the statistic is not regular in brackets, the "p" of "p-value" is seen as a noun phrase. delete it.
        if token.text == "p":
            tmp = getRightNounChunk(token.i, noun_chunks)
            if tmp != (-1,-1) and tmp[0] == tmp[1]:
                output.deleteNoun_Chunk(token.i)
        #Noun phrases often include the word 'result' but it's never a condition, e.g. "Result of ..."
        if token.lemma_ == "result" and token.pos_ == "NOUN":
            output.deleteNoun_Chunk(token.i)
        # t-test is often part of a noun phrase but never includes the conditions in that specific noun phrase
        if token.dep_ == "compound" and token.text == "t":
            tmp = getRightNounChunk(token.i-1, noun_chunks)
            if tmp[1]-tmp[0] < 5:
                output.deleteNoun_Chunk(token.i)
        # BSP: X confirmed that ... ; delete the noun phrase 'X'
        if (token.text == "confirmed" or token.text =="showed" or token.text =="indicates" or token.text =="reveal") and token.nbor(1).text == "that":
            output.deleteNoun_Chunk(token.nbor(-1).i)
        #Noun phrases that include figure references
        if token.lower_ == "figure":
            tmp = getRightNounChunk(token.i, noun_chunks)
            if tmp != (-1,-1):
                output.deleteNoun_Chunk(token.i)
        #Delete e.g: "We found ...", where noun phrase is only the word we or another personal pronoun
        if token.pos_ == "VERB" and token.i >=1 and token.nbor(-1).tag_ == "PRP":
            tmp = getRightNounChunk(token.i-1, noun_chunks)
            if tmp != (-1,-1) and tmp[0] == tmp[1]:
                output.deleteNoun_Chunk(token.i-1)
        #According to x, ...
        if token.lower_ == "according" and token.nbor(1).text == "to":
            output.deleteNoun_Chunk(token.i)
        #Delete noun phrase referencing table
        if token.lower_ == "table":
            tmp = getRightNounChunk(token.i-1, noun_chunks)
            if tmp[1]-tmp[0] < 4:
                output.deleteNoun_Chunk(token.i)
        # Pendant to t-test
        if token.lower_ == "cochran":
            tmp = getRightNounChunk(token.i, noun_chunks)
            if tmp != (-1,-1):
                output.deleteNoun_Chunk(token.i)
    return output


####Extract Aspects ######################################################################################################################################################
#Since our approach is to extract experimental conditions, assigning the aspect is nothing more than another reduced noun phrase.
#check if a verb has an auxiliary verb. If this is the case, the aspect is right before and behind. 
    #Except when there is "to be" after the verb or the VBN is at the end of the sentence and there is only one noun Chunk.
    #Then the aspect is only beforehand.
def passiveAuxiliary(doc, output):
    lengthDoc = len(doc)
    for token in doc:
        if token.tag_ == "VBN" and token.i >1:
            if (token.nbor(-1).dep_ == "auxpass" and token.nbor(-1).tag_ == "VBD") or (token.nbor(-2).dep_ == "auxpass" and token.nbor(-2).tag_ == "VBD"):
                [x,y] = getNounChunks(token.i, output.noun_chunks)
                if x == () or x == (-1,-1): continue
                if token.i == lengthDoc-1:
                    #crash preventing
                    if y == () or y == (-1,-1):
                        output.deleteNoun_Chunk(x[0])
                        output.setaspect(x[0], x[1])
                    else:
                        output.deleteNoun_Chunk(x[0])
                        output.setaspect(x[0], y[1])
                        output.deleteNoun_Chunk(y[1])
                elif token.nbor(1).text == "to" and token.nbor(2).text == "be":
                    #Except case:
                    output.deleteNoun_Chunk(x[0])
                    output.setaspect(x[0],x[1])
                else:
                    if y == () or y == (-1,-1):
                        output.deleteNoun_Chunk(x[0])
                        output.setaspect(x[0], x[1])
                    else:
                        output.deleteNoun_Chunk(x[0])
                        output.setaspect(x[0], y[1])
                        output.deleteNoun_Chunk(y[1])
    return output

def significantExcluder(doc, output):
    keywords = ["significant"]
    for token in doc:
        #significant -------------------------------------------------------------------------------------------------
        #In the PfSWIB vs PfSWIB∆ comparison, the qPCR data showed a significant linear correlation with the RNA-seq data (r (44) = 0.6281, P < 0.0001)
        if keywords[0] == token.lower_:
            if token.i > 1 and (token.nbor(-1).text == "a" 
                                            or (token.nbor(-1).dep_ == "advmod" and token.nbor(-2).text == "a")):
                print(token.i, output.noun_chunks)

                [x, y] = getRightNounChunk(token.i, output.noun_chunks)
                #print(rightChunk)
                if [x, y] == [-1, -1]:
                    print("Warning: 'significant' is not inside a nounChunk.")
                else:
                    print("bagofwords: 'a significant' found")
                    output.setaspect(x, y)
                    output.deleteNoun_Chunk(x)
    return output