from tkinter import *
from tkinter import messagebox
from pathlib import Path

import codecs 


#Input Format: Pointer: Correctness, conditions, real conditions, reason Failure
def appendSen(evalSen_path, i, isCorrect, conditions, solution, failure):
    sCondition = ', '.join(conditions)+"]"

    sResult = '{}: {}, ["{}", "{}", "{}"\n'.format(i, isCorrect, sCondition, solution, failure)
    print(sResult)
    
    file = codecs.open(evalSen_path, 'a', 'utf-8')
    file.write(sResult)
    file.close()


## GUI for Eval #####################################################################################
evalAnswer = False

def callEvaluateExpConDialog(sentence, conditions):
    global evalAnswer
    global solution
    global failReason
    
    showEvaluateExpConDialog(sentence, conditions)
    return [evalAnswer, solution, failReason]


#input: sentence, conditions (list of strings)
#output: correct, fail
def showEvaluateExpConDialog(sentence, conditions):
    #show dialog window to add rule for given sentence
    evalWindow = Tk()
    evalWindow.title("Evaluation of GBCE")

    w = 800 # width for window
    h = 700 # height for window

    canvas = Canvas(evalWindow, width=w, height=h)
    canvas.pack()

    #========================================= Pane ====================================================================
    showPane = Frame(evalWindow)
    showPane.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.2)

    topicPane = Frame(evalWindow)
    topicPane.place(relx=0.05, rely=0.225, relwidth=0.9, relheight=0.1)

    scrollbarPane = Frame(evalWindow)
    scrollbarPane.place(relx=0.05, rely=0.3, relwidth=0.9, relheight=0.25)

    scrollbar = Scrollbar(scrollbarPane)
    scrollbar.pack( side = RIGHT, fill = Y )
    mylist = Listbox(scrollbarPane, yscrollcommand = scrollbar.set)    
    for condition in conditions:
        mylist.insert(END, condition)
    mylist.pack(fill = BOTH )
    scrollbar.config( command = mylist.yview )

    
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

    #========================================= topicPane ==============================================================
    topicText = Label(topicPane, text="Conditions: \n")

    topicText.pack(side="left")
    topicText.config(font=("Courier", 12))

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
    rbnC = Radiobutton(evalPane, text="Not Correct", variable=selectedVar, value=False)
    rbnC.pack(side="right")
    rbnC.config(font=("Courier", 12))
    rbnC.invoke()


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
