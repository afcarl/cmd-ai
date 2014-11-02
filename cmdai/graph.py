"""This files stores public knowledge.
Eventually we want to be able to programmatically update this.

We process input through a series of rule-based transforms that will hopefully
become increasingly sophisticated. Rules are represented as a graph of
meta-edges from list of nodes to various actions, and are stored as a
hierarchal lookup tree.

TODO add support for non-Windows OS
"""
from subprocess import call
import os

def ls(x):
    """
    Lists the files and directories in the given directory

    Parameters:
        params (dict): Path from current directory to directory to list
        files / directories from
    Returns:
        listing (list): A list of the files and directories in params
    """
    try:
        os.chdir(x)
    except FileNotFoundError:
        output("I couldn't find file " + x)


def text2int(textnum, numwords={}):
    """
    Returns integer number from its string representation, or False if the
    string doesn't represent a number.
    """
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          return False

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

"""
_t: transform: replace this match with a different list of nodes,
    which can include variable references
    TODO transforms would be easier to write and more useful if input structure
         reflects grammar (graph rather than naive list)
_e: execute command, passing a dictionary {variable: matched node}
_v: variable node named _vv, which matches anything.
_c: constraint function
    TODO constraints should be nodes too => branching = backtracking.
         allows commands to query variables
TODO handle questions in the interpreter
TODO allow references to dynamically computed groups of nodes e.g. number
"""
transforms = { # TODO automatically add commands
    "show": {"_t": ["display"]},
    "see": {"_t": ["display"]},
    "folder": {"_t": ["directory"]},
    "level": {"_t": ["directory"]},
    "contents": {"_t": ["directory"]},
    "list": {"_t": ["display"]},
    "'s": {"_t": ["is"]},
    "display": {
        "files": {"_e": lambda: call('dir', shell=True)},
        "my": {"files": {"_t": ["display", "files"]}},
        "me": {"my": {"files": {"_t": ["display", "files"]}}},
        "_v": {"_vv": 'x', "_t": ["go", "to", "x"]}
    },
    "go": {
        "to": {
            "_v": {
                "_vv": 'x', "_e": ls,
                "_t": ["display", "files"]
            }
        },
        "up": {
            "_t": ["go", "up", "one", "directory"],
            "a": {"directory": {"_t": ["go", "up", "one", "directory"]}},
            "_v": {
                "_vv": 'x', "_c": lambda x: text2int(x), "directory": {"_t": ["go", "up", "one", "directories"]},
                "_vv": 'x', "_c": lambda x: text2int(x), "directories": {
                    "_e": lambda x: os.chdir("../" * text2int(x)),
                    "_t": ["display", "files"]}
                }
        },
        "down": {"a": {"level": {"_e": lambda p: output('Which directory?')}}}
    },
    "open": {"_v": {"_vv": 'x', "_e": lambda p: call(p['x'], shell=True)}},
    "give": {"me": {"my": {"files": {"_t": ["display", "files"]}}}},
    "what": {"is": {"here": {"_t": ["display", "files"]}}},
    "which": {"files": {"are": {"here": {"_t": ["display", "files"]}}}},
}