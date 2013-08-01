# -*- coding: utf-8 -*-

def read_file(filePath):
    """Read containt of filePath"""

    fileWanted=open(filePath, mode='r')
    string=fileWanted.read().decode("utf-8")
    fileWanted.close()
    return string

def _ask_user(question, function):
    """Ask to the user if he wants to apply a function or not. Use with CAUTION!"""

    answer = None
    answer=raw_input("Do you want to {0}? y/N ".format(question)).lower()
    if answer == "y":
        return function()
    else:
        return None
    
