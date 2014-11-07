import nltk
import sys
from graph import *
from personal import *

def process_input(user_input):
    """
    Processes text user input into a list of nodes, which is then executed on the graph.

    Parameters:
       user_input (string): user's input
    """
    nodes = nltk.word_tokenize(user_input.lower())
    run(nodes)


def run(nodes):
    """
    Iteratively matches transforms to nodes and applies actions.
    Supports variables and constraints, as well as transforms and commands.
    Only actions for the most specific transform are applied.
    Constraints are always evaluated; variables are evaluated before constraints.

    Parameters:
        nodes (list of string): string representations of graph elements, ordered
    """
    changed, command = True, False
    while changed: # search through nodes
        changed = False
        for i, node in enumerate(nodes):
            if node in transforms:
                j, transform, frame, newt = i, transforms[node], {}, False
                while True: # match candidate transform
                    if j+1 < len(nodes) and nodes[j+1] in transform: # next match
                        if "_c" in transform and not transform["_c"](**frame):
                            break
                        j, transform = j+1, transform[nodes[j+1]]
                        continue
                    if "_v" in transform and j+1 < len(nodes): # variable
                        j = j+1
                        temp = transform["_v"]["_vv"]
                        transform = transform["_v"]
                        frame[temp] = nodes[j]
                        if "_c" in transform and not transform["_c"](**frame):
                            break
                        continue
                    if "_c" in transform and not transform["_c"](**frame): # constraint
                        break
                    if "_e" in transform: # command
                        command = True
                        transform["_e"](**frame)
                    if "_t" in transform: # transform
                        newt = transform["_t"]
                        for var in frame:
                            newt = [frame[var] if node == var else node for node in newt]
                    break
                if newt:
                    nodes[i:j+1], changed = newt, True
                    break
    if command == False:
        output("Sorry, I didn't recognize that command.") # TODO autocorrect
    return nodes


def output(text):
    if kbank["output"] == "text":
        print(text)
    #else call('nircmd speak text "' + text + '"')

output("Hello. How may I help you?")
while True:
    string = sys.stdin.readline()
    process_input(string)
