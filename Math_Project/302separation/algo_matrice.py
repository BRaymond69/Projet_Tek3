#!/usr/bin/python3
#Benjamin RAYMOND

import sys, math, os

def matrix(list_name, Friends1, Friends2, his_name, his_friend, len_argv, nb):
    """
    Matrix function who will increment 3 times,
    Its a double array
    Display in terms of number of 
    """
    ###Matrix 1
    w = len(list_name)
    matrice = [[0 for x in range(w)] for y in range(w)]
    y = 0
    for inc in list_name :
        x = 0
        for name in list_name :
            i = 0
            found = 0
            while i < len(Friends1) and found != 1:
                if Friends1[i] == name and Friends2[i] == inc:
                    found = 1
                    matrice[y][x] = 1
                if Friends2[i] == name and Friends1[i] == inc:
                    found = 1
                    matrice[y][x] = 1
                i+=1
            if found == 0:
                matrice[y][x] = 0
            x+=1
        y+=1
 
    ####Matrix adjacente   
    matrice_adjacente = [[0 for x in range(w)] for y in range(w)] 
    for x in range(len(list_name)):
        for y in range(len(list_name)):
            matrice_adjacente[x][y] = nb + 1
        for y in range(len(list_name)):
            if (matrice[x][y] > 0):
                matrice_adjacente[x][y] = 1
        matrice_adjacente[x][x] = 0
    for z in range(len(list_name)):
        for x in range(len(list_name)):
            for y in range(len(list_name)):
                matrice_adjacente[x][y] = min(matrice_adjacente[x][y], matrice_adjacente[x][z] + matrice_adjacente[z][y])
    for x in range(len(list_name)):
        for y in range(len(list_name)):
            if (matrice_adjacente[x][y] > nb):
                matrice_adjacente[x][y] = 0

    if len_argv == 4:
        x = -1
        y = -1
        i = 0
        degree = -1
        for inc in list_name:
            if (inc == his_name) :
                x = i
            if (inc == his_friend) :
                y = i
            i+= 1
        if (x == -1 or y == -1) :
            degree = -1
        else:
            degree = matrice_adjacente[y][x]
        print("Degree of separation between", his_name, "and", his_friend, end="")
        print(":", degree)

    if len_argv == 3:
        for name in list_name:
            print(name)
        print()
        y = 0
        while y < len(list_name):
            x = 0
            while x < len(list_name):
                sys.stdout.write(str(matrice[y][x])) #Oblige to use stdout.write cause print put automaticly a '\n' and the end
                if (x != len(list_name)-1):
                    sys.stdout.write(" ");
                x+=1
            print()
            y+=1
        print()
        y = 0
        while y < len(list_name):
            x = 0
            while x < len(list_name):
                sys.stdout.write(str(matrice_adjacente[y][x]))
                if (x != len(list_name)-1):
                    sys.stdout.write(" ");
                x+=1
            print()
            y+=1