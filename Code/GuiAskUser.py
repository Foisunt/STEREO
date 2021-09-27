#!/usr/bin/env python
# coding: utf-8
import ThreadingRule as tr
import loadPaper as pap
import re
import webbrowser
import sys
from tkinter import *
from tkinter import messagebox
from pathlib import Path

R_MINUS = "rMinus"
R_PLUS = "rPlus"
CORRECT = "Correct"
FAIL = "Not Correct"
subRulesList = []
newSubList = []
skip = False
evalAnswer = False
evalUncovered = ""
answerList = []


#alle modelle in einem Dialog oder einzeln anzeigen?
#1 satz + 15 strings mti jew. correct/false
def showEvaluateABAEDialog(sentence, argList):
    #show dialog window to add rule for given sentence
    evalWindow = Tk()
    evalWindow.title("Evaluation of ABAE")

    w = 1920  # width for window
    h = 1000 # height for window

    canvas = Canvas(evalWindow, width=w, height=h)
    canvas.pack()

    #========================================= Pane ====================================================================
    showPane = Frame(evalWindow)
    showPane.place(relx=0.05, rely=0.05, relwidth=0.8, relheight=0.1)

    offset = 0.06
    paneList = []
    for _ in argList:
        pane = Frame(evalWindow)
        pane.place(relx=0.05, rely=0.05+offset, relwidth=0.7, relheight=0.05)
        paneList.append(pane)
        offset += 0.06

    buttonPane = Frame(evalWindow)
    buttonPane.place(relx=0.8, rely=0.15, relwidth=0.1, relheight=0.1)

    #========================================= showPane ================================================================
    #ok button got invoked
    def button_ok():
        global answerList
        answerList = [selectedSet[k].get() for k in range(len(selectedSet))]
        evalWindow.destroy()

    def button_cancel():
        if messagebox.askokcancel("Quit", "Are you sure you want to cancel the evaluation?"):
            evalWindow.destroy()
            sys.exit()

    #========================================= showPane ================================================================
    sentenceText = Text(showPane, wrap=WORD, width=evalWindow.winfo_screenwidth(), height=3)
    sentenceText.insert(INSERT, sentence)
    sentenceText.pack(side="top")
    sentenceText["state"] = DISABLED

    #========================================= paneList ================================================================
    selectedSet = [BooleanVar() for _ in argList]

    radioButtonList = []
    for i in range(len(paneList)):
        lab = Label(paneList[i], text="Model "+str(i)+" : "+str(argList[i])).pack(side="left")
        rbC = Radiobutton(paneList[i], text="Correct", variable=selectedSet[i], value=True)
        rbC.pack(side="right")
        rbnC = Radiobutton(paneList[i], text="Not Correct", variable=selectedSet[i], value=False)
        rbnC.pack(side="right")
        rbnC.invoke()
        radioButtonList.append((rbC,rbnC))

    #========================================= buttonPane ================================================================
    add_button = Button(buttonPane, text="OK", command=button_ok, padx=20)
    add_button.pack(side="top", fill='x')
    cancel_button = Button(buttonPane, text="Close", command=button_cancel, padx=20)
    cancel_button.pack(side="bottom", fill='x')


    #this will trigger when the window is close with the 'X' in the upper right corner
    evalWindow.protocol("WM_DELETE_WINDOW", button_cancel)    #terminate program

    mainloop()

#input: sentence, aspect (string), conditions (list of strings)
#output: correct, fail
def showEvaluateExpConDialog(sentence, aspect, conditions):
    #show dialog window to add rule for given sentence
    evalWindow = Tk()
    evalWindow.title("Evaluation of ABAE")

    w = 800  # width for window
    h = 700 # height for window

    canvas = Canvas(evalWindow, width=w, height=h)
    canvas.pack()

    #========================================= Pane ====================================================================
    showPane = Frame(evalWindow)
    showPane.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.2)

    aspectPane = Frame(evalWindow)
    aspectPane.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.1)

    offset = 0.05
    paneList = []
    for _ in conditions:
        pane = Frame(evalWindow)
        pane.place(relx=0.05, rely=0.25+offset, relwidth=0.9, relheight=0.05)
        paneList.append(pane)
        offset += 0.05
    
    failReasonPane = Frame(evalWindow)
    failReasonPane.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.1)
    
    solutionPane = Frame(evalWindow)
    solutionPane.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.1)

    evalPane = Frame(evalWindow)
    evalPane.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.1)

    buttonPane = Frame(evalWindow)
    buttonPane.place(relx=0.05, rely=0.8, relwidth=0.9, relheight=0.05)

    #========================================== Actions ================================================================
    #ok button got invoked
    def button_ok():
        global evalAnswer
        global solution
        global failReason
        evalAnswer = selectedVar.get()
        failReason = eFailReason.get()
        solution   = eSolution.get()
        evalWindow.destroy()

    def button_cancel():
        if messagebox.askokcancel("Quit", "Are you sure you want to cancel the evaluation?"):
            evalWindow.destroy()
            sys.exit()

    #========================================= showPane ================================================================
    sentenceText = Text(showPane, wrap=WORD, width=evalWindow.winfo_screenwidth(), height=8)
    sentenceText.insert(INSERT, sentence)
    sentenceText.pack(side="top")
    sentenceText.config(font=("Courier", 12))
    sentenceText["state"] = DISABLED

    #========================================= AspectPane ==============================================================
    aspectText = Label(aspectPane, text="Aspect: " + aspect)
    aspectText.pack(side="left")
    aspectText.config(font=("Courier", 12))

    #========================================= ConditionPane ===========================================================
    for i in range(len(conditions)):
        lab = Label(paneList[i],text="Condition "+str(i+1)+" : "+conditions[i])
        lab.pack(side="left")
        lab.config(font=("Courier", 12))
    
    #========================================= FailReasonPane ===========================================================
    eFailReason = Entry(failReasonPane, width = 100)
    eFailReason.pack(side="right")
    labelFailReason = Label(failReasonPane, text = "Reason Failure: ")
    labelFailReason.pack(side="left")
    #========================================= SolutionPane ===========================================================
    eSolution = Entry(solutionPane, width = 100)
    eSolution.pack(side="right")
    labelSolution = Label(solutionPane, text = "Model Solution: ")
    labelSolution.pack(side="left")

    #========================================== EvalPane ===============================================================
    selectedVar = BooleanVar()
    rbC = Radiobutton(evalPane, text="Correct", variable=selectedVar, value=True)
    rbC.pack(side="left")
    rbC.config(font=("Courier", 12))
    rbC.invoke()
    rbnC = Radiobutton(evalPane, text="Not Correct", variable=selectedVar, value=False)
    rbnC.pack(side="right")
    rbnC.config(font=("Courier", 12))

    #========================================= buttonPane ================================================================
    add_button = Button(buttonPane, text="OK", command=button_ok, padx=20)
    add_button.pack(side="left")
    add_button.config(font=("Courier", 12))
    cancel_button = Button(buttonPane, text="Close", command=button_cancel, padx=20)
    cancel_button.pack(side="right")
    cancel_button.config(font=("Courier", 12))

    #this will trigger when the window is close with the 'X' in the upper right corner
    evalWindow.protocol("WM_DELETE_WINDOW", button_cancel)    #terminate program

    mainloop()


def showUncoveredEvaluateDialog(sentence, samplesToGo):
    #show dialog window to add rule for given sentence
    evalWindow = Tk()
    evalWindow.title("Evaluation of uncovered sentences")

    w = 800 # width for window
    h = 650 # height for window

    # get screen width and height
    ws = evalWindow.winfo_screenwidth() # width of the screen
    hs = evalWindow.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    evalWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))

    canvas = Canvas(evalWindow, width=800, height=600)
    canvas.pack()

    #contains sentence and the radiobuttons for classifying the ruleset -> evaluate
    showPane = Frame(evalWindow)
    showPane.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.5)

    evalPane = Frame(evalWindow)
    evalPane.place(relx=0.1, rely=0.6, relwidth=0.8, relheight=0.2)

    #contains the Cancel and Ok button
    buttonPane = Frame(evalWindow)
    buttonPane.place(relx=0.1, rely=0.8, relwidth=0.8, relheight=0.1)

    #======================= Actions =================================
    #ok button got invoked
    def ok():
        answer = selectedSet.get()
        global evalUncovered
        evalUncovered = answer
        evalWindow.destroy()

    def cancel():
        if messagebox.askokcancel("Quit", "Are you sure you want to cancel the evaluation?"):
            evalWindow.destroy()
            sys.exit()

    #action when users clicks X
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the evaluation?"):
            evalWindow.destroy()
            sys.exit()

    #======================= showPane ================================
    sentenceText = Text(showPane, wrap=WORD, height=10)
    sentenceText.insert(INSERT, sentence)
    sentenceText["state"] = DISABLED
    sentenceText.config(font=("Courier", 12))
    sentenceText.pack(side="top")

    rulesetLabel = Label(showPane, text="Classified as: Uncovered \nSentences left: "+ str(samplesToGo))
    rulesetLabel.config(font=("Courier", 12))
    rulesetLabel.pack(side="left")

    #======================= evalPane ================================
    selectedSet = StringVar()
    #Define the radiobuttons
    rb1 = Radiobutton(evalPane, text="Statistic", variable=selectedSet, value="Stat", font=("Courier", 12))
    rb1.place(relx=0.01, rely=0.1)
    rb2 = Radiobutton(evalPane, text="Non-Statistic", variable=selectedSet, value="NonStat", font=("Courier", 12))
    rb2.place(relx=0.01, rely=0.4)
    rb2.invoke()
    rb3 = Radiobutton(evalPane, text="Parse error", variable=selectedSet, value="ParseError", font=("Courier", 12))
    rb3.place(relx=0.01, rely=0.7)
    #======================= buttonPane ================================
    ok_button = Button(buttonPane, text="OK", command=ok, padx=20)
    ok_button.pack(side="left")
    cancel_button = Button(buttonPane, text="Cancel", command=cancel, padx=20)
    cancel_button.pack(side="right")

    #this will trigger when the window is close with the 'X' in the upper right corner
    evalWindow.protocol("WM_DELETE_WINDOW", on_closing)    #terminate program

    mainloop()


#this dialog will get sentence and the classification, generated by the program
# -> the then needs to evaluate this pair of information accordingly
def showEvaluateDialog(sentence, samplesToGo, rulesetMinus=False, exData=None):
    #show dialog window to add rule for given sentence
    evalWindow = Tk()
    evalWindow.title("Evaluation")

    w = 800 # width for window
    h = 650 # height for window

    # get screen width and height
    ws = evalWindow.winfo_screenwidth() # width of the screen
    hs = evalWindow.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    evalWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))

    canvas = Canvas(evalWindow, width=800, height=600)
    canvas.pack()

    #contains sentence, ruleset and if given, the extracted values
    showPane = Frame(evalWindow)
    showPane.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.6)

    #contains the radiobuttons for classifying the ruleset -> evaluate
    evalPane = Frame(evalWindow, bd=10)
    evalPane.place(relx=0.1, rely=0.7, relwidth=0.8, relheight=0.1)

    #contains the Cancel and Ok button
    buttonPane = Frame(evalWindow)
    buttonPane.place(relx=0.1, rely=0.8, relwidth=0.8, relheight=0.1)

    #======================= Actions =================================
    #ok button got invoked
    def ok():
        answer = selectedSet.get()
        global evalAnswer
        if answer == FAIL:
            evalAnswer = False
        else:
            evalAnswer = True
        evalWindow.destroy()

    def cancel():
        if messagebox.askokcancel("Quit", "Are you sure you want to cancel the evaluation?"):
            evalWindow.destroy()

    #action when users clicks X
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the evaluation?"):
            evalWindow.destroy()
            sys.exit()

    #======================= showPane ================================
    sentenceText = Text(showPane, wrap=WORD, height=10)
    sentenceText.insert(INSERT, sentence)
    sentenceText["state"] = DISABLED
    sentenceText.config(font=("Courier", 12))
    sentenceText.pack(side="top")


    #check, what kind of rule is given
    if rulesetMinus:
        ruleSet = R_MINUS
    else:
        ruleSet = exData.statisticType
    rulesetLabel = Label(showPane, text="Classified as: " + ruleSet + " \nSentences left: "+ str(samplesToGo))
    rulesetLabel.config(font=("Courier", 12))
    rulesetLabel.pack(side="left")

    values = "\n"
    if exData is None:
        values = "None"
    else:
        dictRecord = exData.record
        for key in dictRecord.keys():
            if dictRecord[key] is None:
                values = values + key + " : None \n"
            else:
                values = values + key + " : " + dictRecord[key] + "\n"
    valuesLabel = Label(showPane, text="Extracted values: "+values)
    valuesLabel.config(font=("Courier", 12))
    valuesLabel.pack(side="right")

    #======================= evalPane ================================
    selectedSet = StringVar()
    #Define the radiobuttons
    rb1 = Radiobutton(evalPane, text="Not Correct", variable=selectedSet, value=FAIL, font=("Courier", 12))
    rb1.pack(side="left")
    rb2 = Radiobutton(evalPane, text="Correct", variable=selectedSet, value=CORRECT, font=("Courier", 12))
    rb2.pack(side="right")
    rb2.invoke()
    #======================= buttonPane ================================
    ok_button = Button(buttonPane, text="OK", command=ok, padx=20)
    ok_button.pack(side="left")
    cancel_button = Button(buttonPane, text="Cancel", command=cancel, padx=20)
    cancel_button.pack(side="right")

    #this will trigger when the window is close with the 'X' in the upper right corner
    evalWindow.protocol("WM_DELETE_WINDOW", on_closing)    #terminate program

    mainloop()

def showHelp():
    webbrowser.open_new_tab(Path('helpPage.html'))

def fixSubRules(exData, subList, rule, idn):
    fixWindow = Tk()
    fixWindow.title("Fix subrules")

    w = 800 # width for window
    h = 700 # height for window

    # get screen width and height
    ws = fixWindow.winfo_screenwidth() # width of the screen
    hs = fixWindow.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    fixWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))

    canvas = Canvas(fixWindow, width=800, height=600)
    canvas.pack()

    printPane = Frame(fixWindow)
    printPane.place(relx=0.1, rely=0.01, relwidth=0.8, relheight=0.3)

    showPane = Frame(fixWindow, bd=10)
    showPane.place(relx=0.1, rely=0.4, relwidth=0.5, relheight=0.35)

    buttonPane = Frame(fixWindow)
    buttonPane.place(relx=0.7, rely=0.4, relwidth=0.2, relheight=0.25)

    entryPane = Frame(fixWindow)
    entryPane.place(relx=0.1, rely=0.8, relwidth=0.8, relheight=0.1)

    #======================= Buttons =================================
    def finishSub():
        global newSubList
        if not newSubList:
            errorField.config(text="Please add a sub-rule first.")
        else:
            overwrite = True
            for newSub in newSubList:
                pap.updateSubRule(newSub, idn, overwrite) #need new method to modify sub-rules
                overwrite = False
            fixWindow.destroy()

    def addSub():
        global newSubList
        matchedSentence = re.search(rule, exData.sentence)[0]
        if entryField.get() == "":
            errorField.config(text="Please enter a sub-rule first.")
        else:
            try:
                #re.compile(entryField.get())
                pap.validityCheckRule(entryField.get(), exData.statisticType)
                match = re.search(entryField.get(), matchedSentence)
                if match is None:
                    errorField.config(text="No match found. Please adjust sub-rule.")
                else:
                    errorField.config(text="")
                    newSubList.append(entryField.get())
                    updateList(newSubBox, newSubList)
                    newSubBox.pack()
            except re.error:
                errorField.config(text="Syntax error. Please adjust rule.")

    def delSub():
        global newSubList
        tupelIndex = newSubBox.curselection()
        if not tupelIndex:
            errorField.config(text="Please select the sub-rule you want to delete first.")
        else:
            errorField.config(text="")
            element = newSubBox.get(tupelIndex)
            newSubBox.delete(tupelIndex)
            print(newSubList)
            newSubList.remove(element)
            updateList(newSubBox, newSubList)

    def testSub():
        listElement = newSubBox.curselection()
        matchedSentence = re.search(rule, exData.sentence)[0]
        if not listElement:
            errorField.config(text="Please select a sub-rule first.")
        else:
            errorField.config(text="")
            newRule = newSubBox.get(listElement)
            #show match for the given rule
            match = re.search(newRule, matchedSentence)
            matchList = [match]
            showMatch(matchList, matchedSentence)

    #set global skip and close the window
    def skip():
        global skip
        skip = True
        fixWindow.destroy()


    #======================= printPane ===============================
    match = re.search(rule, exData.sentence)
    start = "1."+str(match.start())
    end = "1."+str(match.end())

    entryCaption = Label(printPane, text="It was not possible to extract all values with the defined sub-rules.\n"\
            "Please adjust the sub-rules given below.\n\n")
    entryCaption.pack(side="top")
    sentenceText = Text(printPane, wrap=WORD, height=3)
    sentenceText.insert(INSERT, exData.sentence)
    sentenceText.pack(side="top")
    sentenceText.tag_add("match", start, end)
    sentenceText.tag_config("match", foreground="red")
    sentenceText.configure(font=("Courier", 10))
    sentenceText["state"] = DISABLED

    failedSubsLabel = "\nFollowing sub-rules are missing:\n"
    for key in exData.record.keys():
        if exData.record[key] is None:
            failedSubsLabel = failedSubsLabel + key+"\n"

    failedSubsField = Label(printPane, text=failedSubsLabel)
    failedSubsField.pack(side="bottom")

    matchLabel = Label(printPane, text="Rule: "+rule)
    matchLabel.pack(side="bottom", fill="x")

    #======================= showPane ================================
    #captionLabel = Label(showPane, text="Defined sub-rules:")
    #captionLabel.config(font=("Courier", 12, "bold"))
    #captionLabel.pack(side="top", fill="both")

    #definedSubsText = ""
    #for sub in subList:
        #definedSubsText = definedSubsText + str(sub) + "\n"
    #definedSubs = Label(showPane, text=definedSubsText)
    #definedSubs.pack(side="top", fill="both")
    #definedSubs.config(font=("Courier", 12))

    captionLabel2 = Label(showPane, text="Sub-rules:")
    captionLabel2.config(font=("Courier", 12, "bold"))
    captionLabel2.pack(side="top", fill="both")

    newSubBox = Listbox(showPane, selectmode=SINGLE)
    newSubBox.pack(side="top", fill="both")
    #newSubBox.config(font=("Courier", 12))

    global newSubList
    newSubList = subList
    updateList(newSubBox, newSubList)
    newSubBox.pack()

    #====================== buttonPane ================================
    add_button = Button(buttonPane, text="Add Sub-Rule", command=addSub, padx=20)
    add_button.pack(side="top", fill="both")

    del_button = Button(buttonPane, text="Delete Sub-Rule", command=delSub, padx=20)
    del_button.pack(side="top", fill="both")

    test_button = Button(buttonPane, text="Test", command=testSub, padx=20)
    test_button.pack(side="top", fill="both")

    help_button = Button(buttonPane, text="Help", command=showHelp, padx=20)
    help_button.pack(side="bottom", fill='both')

    finish_button = Button(buttonPane, text="Finish", command=finishSub, padx=20)
    finish_button.pack(side="bottom", fill="both")

    skip_button = Button(buttonPane, text="Skip", command=skip, padx=20)
    skip_button.pack(side="bottom", fill="both")

    #====================== entryPane ==================================
    entryField = Entry(entryPane, bd=7, width=500)
    entryField.pack(side="top")
    entryField.config(font=("Courier", 12))

    errorField = Label(entryPane, text="")
    errorField.pack(side="bottom")
    errorField.config(font=("Courier", 9))

    mainloop()


#list for printing already defined subrules for editing
def updateList(listSub, subRulesList):
    i = 0
    listSub.delete(0, len(subRulesList))
    if len(subRulesList) != 0:
        for k in subRulesList:
            ++i
            listSub.insert(i, k)

#for defining the subrules for the given statistic type
def defineSubRules(sentence):
    subWindow = Tk()
    subWindow.title("Define subrules")
    w = 700 # width for window
    h = 650 # height for window

    # get screen width and height
    ws = subWindow.winfo_screenwidth() # width of the screen
    hs = subWindow.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    subWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))
    canvas = Canvas(subWindow, width=700, height=600)
    canvas.pack()

    def addSubRule():
        global subRulesList
        if subRuleEntry.get() == "":
            errorField.config(text="Please enter a sub-rule first.")
        else:
            try:
                re.compile(subRuleEntry.get())
                match = re.search(subRuleEntry.get(), sentence)
                if match is None:
                    errorField.config(text="No match found. Please adjust sub-rule.")
                else:
                    errorField.config(text="")
                    subRulesList.append(subRuleEntry.get())
                    updateList(listSub, subRulesList)
                    listSub.pack()
            except re.error:
                errorField.config(text="Syntax error. Please adjust rule.")

    def deleteSubRule():
        global subRulesList
        tupelIndex = listSub.curselection()
        if not tupelIndex:
            errorField.config(text="Please select the sub-rule you want to delete first.")
        else:
            errorField.config(text="")
            element = listSub.get(tupelIndex)
            listSub.delete(tupelIndex)
            subRulesList.remove(element)
            updateList(listSub, subRulesList)

    def button_testSub():
        listElement = listSub.curselection()
        if not listElement:
            errorField.config(text="Please select a sub-rule first.")
        else:
            errorField.config(text="")
            newRule = listSub.get(listElement)
            #show match for the given rule
            match = re.search(newRule, sentence)
            showMatch([match], sentence, True)

    matchPane = Frame(subWindow)
    matchPane.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.15)

    rulePane = Frame(subWindow)
    rulePane.place(relx=0.1, rely=0.2, relwidth=0.4, relheight=0.55)

    choosePane = Frame(subWindow)
    choosePane.place(relx=0.5, rely=0.2, relwidth=0.4, relheight=0.55)

    errorFrame = Frame(subWindow)
    errorFrame.place(relx=0.1, rely=0.65, relwidth=0.8, relheight=0.1)

    buttonPane = Frame(subWindow)
    buttonPane.place(relx=0.1, rely=0.75, relwidth=0.8, relheight=0.1)

    listSub = Listbox(choosePane, selectmode=SINGLE)

    global subRulesList
    updateList(listSub, subRulesList)
    listSub.pack(side="top", fill="x")

    #sentenceText = Message(matchPane, text=sentence, justify="left", width=320)
    #sentenceText.pack(side="top")
    sentenceText = Text(matchPane, wrap=WORD)
    sentenceText.place(relx=0, rely=0, relwidth=1, relheight=0.5)
    sentenceText.insert(INSERT, sentence)
    sentenceText["state"] = DISABLED

    enterRuleLabel = Label(rulePane, text="Enter sub rule")
    enterRuleLabel.pack()
    subRuleEntry = Entry(rulePane, bd=5, width=160)
    subRuleEntry.pack()

    errorField = Label(errorFrame)
    errorField.pack(side="bottom")
    errorField.config(font=("Courier", 12))

    add_button = Button(buttonPane, text="Add", command=addSubRule, padx=20)
    add_button.pack(side="left")
    exit_button = Button(buttonPane, text="OK", command=subWindow.destroy, padx=20)
    exit_button.pack(side="left")
    del_button = Button(buttonPane, text="Delete", command=deleteSubRule, padx=20)
    del_button.pack(side="right")
    testSub_button = Button(buttonPane, text="Test", command=button_testSub, padx=20)
    testSub_button.pack(side="right")


#show match produced by the entered rule, invoked by the test button
def showMatch(matchList, sentence, showValues=False):
    testFenster = Tk()
    testFenster.title("Found Match for new Rule")

    w = 600 # width for window
    h = 450 # height for window

    # get screen width and height
    ws = testFenster.winfo_screenwidth() # width of the screen
    hs = testFenster.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    testFenster.geometry('%dx%d+%d+%d' % (w, h, x, y))
    canvas = Canvas(testFenster, width=600, height=400)
    canvas.pack()

    frameText = Frame(testFenster)
    frameText.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.6)

    buttonPane = Frame(testFenster)
    buttonPane.place(relx=0.1, rely=0.6, relwidth=0.8, relheight=0.2)

    #used in subrules dialog -> show which valeus would be extracted along with match
    if showValues:
        #if called from subrules dialog, there will always be just one match
        dictn = matchList[0].groupdict()
        for key in dictn.keys():
            sentence = sentence + "\n\nExtracted value: " + key + " : " + matchList[0].groupdict()[key]
    textBox = Text(frameText, wrap=WORD)
    textBox.insert(INSERT, sentence)
    textBox.pack(side="left")
    textBox.config(font=("Courier", 12))

    for match in matchList:
        start = "1."+str(match.start())
        end = "1."+str(match.end())
        textBox.tag_add("match", start, end)
        textBox.tag_config("match", foreground="red")

    textBox["state"] = DISABLED

    exit_button = Button(buttonPane, text="OK", command=testFenster.destroy, padx=20)
    exit_button.pack(side="right")


def showDialog(sentence, idn, spanList, patternList):
    global R_MINUS, R_PLUS
    #show dialog window to add rule for given sentence
    fenster = Tk()
    fenster.title("Add rule")

    w = 800 # width for window
    h = 650 # height for window

    # get screen width and height
    ws = fenster.winfo_screenwidth() # width of the screen
    hs = fenster.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    fenster.geometry('%dx%d+%d+%d' % (w, h, x, y))

    #Write the rule into the respective file and close this window to go on with the next sentence
    def button_add():
        newRule = eingabefeld.get()
        if newRule == "":
            errorField.config(text="Please add rule first.")
        else:
            #check if rule set is defined
            if ruleSet == "":
                errorField.config(text="Please enter rule set first.")
            else:
                #add rule for the respective stat type
                if ruleSet == R_MINUS:
                    pap.updateRminus(newRule)
                else:
                    idn = len(pap.readRules('rPlus'))
                    pap.updateRplus(newRule, idn)
                    global subRulesList
                    if subRulesList:
                        for sub in subRulesList:
                            pap.updateSubRule(sub, idn)
                fenster.destroy()

    #Show match for the given rule, if a rule is entered in the respective field
    def button_test():
        global ruleSet
        newRule = eingabefeld.get()
        if newRule == "":
            errorField.config(text="Please add rule first.")
        else:
            #show match for the given rule
            try:
                pap.validityCheckRule(newRule, ruleSet)
                #check for all possible matches
                matches = re.finditer(newRule, sentence)
                matchList = []
                for match in matches:
                    matchList.append(match)
                if matchList == []:
                    errorField.config(text="No match found.")
                else:
                    errorField.config(text="")
                    add_button["state"] = ACTIVE
                    showMatch(matchList, sentence)
            except re.error:
                errorField.config(text="Syntax error. Please adjust rule.")

    #Set the subrules invoke Button to disabled when R- is choosen
    def selRadio():
        global ruleSet
        ruleSet = selectedSet.get()
        if ruleSet == R_MINUS:
            subRule_button["state"] = "disabled"
        else:
            subRule_button["state"] = "normal"

    #Invoke dialog for defining subrules, but only when R+ is marked
    def button_subRule():
        newRule = eingabefeld.get()
        if newRule == "":
            errorField.config(text="Please enter a rule first.")
        else:
            try:
                re.compile(newRule)
                errorField.config(text="")
                match = re.search(newRule, sentence)
                if match:
                    defineSubRules(match[0])
                else:
                    errorField.config(text="No match found.")
            except re.error:
                errorField.config(text="Syntax error. Please adjust rule.")

    #Test how many matches the defined rule will have in limited and randomly selected documents
    def button_applyRule():
        newRule = eingabefeld.get()
        #Print something, so the user knows that the programm is processing
        errorField.config(text="Processing...")
        canvas.update_idletasks()       #this is needed, so the user can see the new label before the threads finish
        if newRule == "":
            errorField.config(text="Please enter rule first.")
        else:
            try:
                re.compile(newRule)
                (amountSentences, result) = tr.tryRule(newRule)
                errorField.config(text="In "+str(amountSentences)+" sentences from random selected documents,\n"\
                                       +str(result)+" matches have been found.")
            except re.error:
                errorField.config(text="Syntax error. Please adjust rule.")

    #write the global variable skip to communicate with the calling programm
    def button_skip():
        global skip
        skip = True
        fenster.destroy()

    #action when users clicks X
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit STEREO?"):
            fenster.destroy()
            sys.exit()

    #configure patternLabel so that the pattern for the given rule (mouse hover)
    #will be shown
    def showPattern(pattern):
        patternField["state"] = NORMAL
        patternField.delete("1.0", END)
        patternField.insert("1.0", "Used rule: "+pattern)
        patternField["state"] = DISABLED

    canvas = Canvas(fenster, width=800, height=600)
    canvas.pack()

    #Define the structure inside the window for labels/buttons/etc.
    labelFrame = Frame(fenster)
    labelFrame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.55)

    selectFrame = Frame(fenster)
    selectFrame.place(relx=0.1, rely=0.65, relwidth=0.8, relheight=0.2)

    buttonFrame = Frame(fenster)
    buttonFrame.place(relx=0.1, rely=0.85, relwidth=0.8, relheight=0.1)

    #Here, the sentence will be printed
    sentenceText = Text(labelFrame, wrap=WORD)
    sentenceText.insert(INSERT, sentence)
    sentenceText.place(relx=0, rely=0, relwidth=1, relheight=0.65)

    i = 0   #set a counter variable
    #mark rules, which already matched
    for (s, e) in spanList:
        start = "1."+str(s)
        end = "1."+str(e)
        sentenceText.tag_add(str(i), start, end)
        sentenceText.tag_config(str(i), foreground="green")
        def handlerEnter(event, text=patternList[i][0]):
            return showPattern(text)
        sentenceText.tag_bind(str(i), "<Enter>", handlerEnter)
        i += 1

    sentenceText["state"] = DISABLED

    #In this field the user will define rules
    eingabefeld = Entry(labelFrame)
    eingabefeld.place(relx=0, rely=0.7, relwidth=1, relheight=0.1)
    eingabefeld.config(font=("Courier", 12))

    #Label for displaying any errors that might occur
    errorField = Label(labelFrame)
    errorField.place(relx=0, rely=0.8, relwidth=1, relheight=0.1)
    errorField.config(font=("Courier", 12))

    #Label for displaying the pattern, used for match, the user is hovering above
    patternField = Text(labelFrame)
    patternField.place(relx=0, rely=0.9, relwidth=1, relheight=0.1)
    patternField.config(font=("Courier", 12))
    patternField.insert(INSERT, "Used rule: None")
    #patternField["state"] = DISABLED
    selectedSet = StringVar()

    #Defining Buttons and their place and action
    add_button = Button(buttonFrame, text="Add", command=button_add, padx=20)
    add_button.pack(side="left", fill='x')
    add_button["state"] = DISABLED
    testy_button = Button(buttonFrame, text="Test", command=button_test, padx=20)
    testy_button.pack(side="left", fill='x')
    help_button = Button(buttonFrame, text="Help", command=showHelp, padx=20)
    help_button.pack(side="left", fill='x')
    exit_button = Button(buttonFrame, text="Skip", command= button_skip, padx=20)
    exit_button.pack(side="right", fill='x')
    subRule_button = Button(buttonFrame, text="Sub-Rules", command=button_subRule, padx=20, state="disabled")
    subRule_button.pack(side="right", fill='x')
    apply_button = Button(selectFrame, text="Apply Rule", command=button_applyRule, padx=20)
    apply_button.pack(side="right", fill='x')

    #Define the radiobuttons
    rb1 = Radiobutton(selectFrame, text="R-", variable=selectedSet, value=R_MINUS, command=selRadio)
    rb1.place(relx=0.01, rely=0.1)
    rb1.invoke()    #R- is the default value
    rb2 = Radiobutton(selectFrame, text="R+", variable=selectedSet, value=R_PLUS, command=selRadio)
    rb2.place(relx=0.01, rely=0.5)

    #this will trigger when the window is close with the 'X' in the upper right corner
    fenster.protocol("WM_DELETE_WINDOW", on_closing)    #terminate program

    mainloop()

#this will invoke the main GUI dialog and will read out the global skip variable
def callGui(sentence, idn, matchList):
    global skip, subRulesList
    subRulesList = []
    skip = False
    patternList = list(map(lambda match:[match.re.pattern], matchList))
    spanList = list(map(lambda match: [match.span(0)[0], match.span(0)[1]], matchList))
    showDialog(sentence, idn, spanList, patternList)
    return skip     #skip cointains boolean value, saying if the current sentence needs to be skipped


#call the evaluation dialog
def callEval(sentence, samplesToGo, rulesetMinus=False, exData=None):
    global evalAnswer
    showEvaluateDialog(sentence, samplesToGo, rulesetMinus, exData)
    return evalAnswer 

#call the evaluation dialog for uncovered sentences -> sentences in which nether a R+ rule nor a R- rule matches
def callEvalUncovered(sentence, samplesToGo):
    global evalUncovered
    evalUncovered = ""
    showUncoveredEvaluateDialog(sentence, samplesToGo)
    return evalUncovered

#call fixSubRules dialog and retrieve skip flag
def callFixSubRules(exData, subList, rule, idn):
    global skip, newSubList
    newSubList = []
    skip = False
    fixSubRules(exData, subList, rule, idn)
    return skip

#call fixSubRules dialog and retrieve skip flag
def callEvalABAE(sentence, argList):
    global answerList
    answerList = []
    showEvaluateABAEDialog(sentence, argList)
    print(answerList)
    return answerList

def callEvaluateExpConDialog(sentence, aspect, conditions):
    global evalAnswer
    global solution
    global failReason
	
    showEvaluateExpConDialog(sentence, aspect, conditions)
    return [evalAnswer, solution, failReason]
