#!/usr/bin/python3
#Benjamin RAYMOND

import sys, math, os

def check_name(name, tab):
    if name in tab:
        return True
    return False

def check_friend(name, tab):
    if name in tab:
        return True
    return False

def getNames(tab):
    names = []
    for i in range(0, len(tab), 1) :
        duo = tab[i].split(" is ")
        names.append(duo[0])
        names.append(tab[i].split(" with ")[1])
    names = list(set(names)) #Remove duplicate name
    names.sort() #All names in a one array sort by alphabetic order
    return (names)

def get_Friend1(tab):
    Friend1 = []
    for i in range (0, len(tab), 1):
        duo = tab[i].split(" is friends with")
        Friend1.append(duo[0])
    Friend1.sort()
    return (Friend1)

def get_Friend2(file):
    Friend2 = []
    tmps = []
    for line in file:
        tmps.append(line.replace(" is friends with ", "-").replace("\n", ""));
    tmps.sort()
    for i in tmps:
        fr1, fr2 = i.split('-')
        Friend2.append(fr2)
    return (Friend2)