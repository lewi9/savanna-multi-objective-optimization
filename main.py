import numpy as np
import random
import copy
import matplotlib.pyplot as plt
import os
import imageio

import math
from tqdm import tqdm

## set3 - used i = 1, n = 1

## set5 - ZDT 3

## Variables with directories
paretoFrontDir = "results/paretoFront5.txt"
gifDir = "gifs/set5.gif"
argsDir = "results/args5.txt"
frameDir = "frames/"

## Functions to minimze
#set4
#f1 = lambda x: x[0]**2-x[1]
#f2 = lambda x: -0.5*x[0]-x[1]-1

f1 = lambda x : x[0]
g1 = lambda x : 1 + 9/29 * np.sum(x[1:])
h1 = lambda x : 1 - math.sqrt(f1(x)/g1(x))
f2 = lambda x : g1(x) * h1(x)
## Constraints of functions <= 0
#set4
#g1 = lambda x: -6.5 + x[0]/6 + x[1]
#g2 = lambda x: -7.5 + 0.5*x[0] + x[1]
#g3 = lambda x: -30 + 5*x[0] + x[1]
    
functions = [f1, f2]
constraints = []

## Lims of variables: x1, x2, x3 ...
lims = [[0,1] for i in range(30)]
print(lims)

## Expected values of f1(x1, x2, ...), f2(x1, x2, ...)
## Only when created gifs are needed
expectedResultLims = [[-4,12], [-7,-5]]


## !! Parameters of algorithm !!
maxCycles = 1200

wildebeest = 120
zebras = 25
gazelles = 10
predators = 4

epsylon = gazellaSearchArea = standardDeviation = 0.01
#default bins = 10, more bins - more chances to search optima of one function
bins = areaExplore = 20

## default rho = 0, rho > 0 - worse solutions, but less
rho = densityOfParetoFront = 0

## Create gif or not, only for 2 functions f1(x1,x2), f2(x1,x2)
record = 0

## Init variables
paretoFront = []
paretoArgs = []


### Create gif - init variables
if record == 1:
    points1 = []
    points2 = []
    filenames1 = []
    filenames2 = []
###

## Main class of different animals, simple, because fast to write
class Animal:
    target = []
    def __init__(self, start, species):
        self.solution = start
        self.species = species

    ## Calc that solution is pareto solution of not
    def calculatePerformance(self):
        global paretoFront
        global paretoArgs

        ## Check tahat solution is valid
        for i in range(len(self.solution)):
            if not lims[i][0] <= self.solution[i] <= lims[i][1]: 
                return
        valid = [g(self.solution) for g in constraints]
        for elem in valid:
            if elem > 0:
                return
        
        path = [f(self.solution) for f in functions]

        ## Update paretoFront list
        ## Weak point - slow the algorithm
        indexes = []
        flagAdd = 1
        for i in range(len(paretoFront)):
            validArray = np.linspace(0,0,len(functions))
            for j in range(len(functions)):
                if path[j] + rho < paretoFront[i][j]:
                    validArray[j] = 1
                elif path[j] + rho > paretoFront[i][j]:
                    validArray[j] = -1
            if 1 in validArray and not -1 in validArray:
                indexes.append(i)
            elif -1 in validArray and not 1 in validArray:
                flagAdd = 0
            elif not 1 in validArray and not -1 in validArray:
                flagAdd = 0
        paretoFront = [i for j,i in enumerate(paretoFront) if j not in indexes]
        paretoArgs = [i for j,i in enumerate(paretoArgs) if j not in indexes]
        if flagAdd == 1:
            paretoFront.append(path)
            paretoArgs.append(copy.copy(self.solution))
            
        ### Create gif - add animals coords
        if record == 1:
            points1.append(copy.copy(self.solution))
            points2.append(path)
        ###

    ## Move of different species (it will be better if will be abstract class for every animal)
    def move(self):
        ## Main search power
        if self.species == "wildebeest":
            for i in range(len(self.solution)):
                self.solution[i] = np.random.normal( (self.solution[i] + Animal.target[i])/2, abs(self.solution[i]-Animal.target[i]))
        ## Another move for zebras - probably can be better
        elif self.species == "zebra":
            for i in range(len(self.solution)):
                self.solution[i] = np.random.uniform( min(self.solution[i],Animal.target[i]), max(self.solution[i],Animal.target[i]))
        ## Search around targeted solution
        elif self.species == "gazelle":
            for i in range(len(self.solution)):
                self.solution[i] = np.random.normal(Animal.target[i], epsylon)
            
## Init variable
animals = []

## Main loop
for k in tqdm(range(maxCycles), ascii=True, desc="Main"):
    ### Create gif - iterator for filenames
    if record == 1:
        kk = 1
    ###

    ## Helpfull print and data save after each iteration
    print(f"Iter: {k+1}")
    np.savetxt(paretoFrontDir, paretoFront, delimiter='\t')
    np.savetxt(argsDir, paretoArgs, delimiter='\t')

    ## Clear variables
    Animal.target = []
    animals.clear()

    ## Init target of herd - when are not solutions
    if len(paretoFront) == 0:
        Animal.target = [ np.random.sample() * (lims[i][1] - lims[i][0]) + lims[i][0] for i in range(len(lims)) ]
    ## Choose target of herd - try to explore area, where a few solutions are
    else:
        ## Choose value to create histogram
        index = np.random.randint(len(functions))

        ## Create sublist of that values
        paretoFrontSubList = [ x[index] for x in paretoFront ]
        
        ## Calc base on histogram
        hist, bin_edges = np.histogram(paretoFrontSubList, bins=20)

        ## Calc probability of being chosen (if lower points in histogram bin, the higher probablity is
        hist = [1/x if x != 0 else 0 for x in hist]
        sumTotal = np.sum(hist)
        hist /= sumTotal

        ## Choose the edges
        binIndex = int(np.random.choice(np.linspace(1,len(bin_edges)-1,len(bin_edges)-1), 1, p=hist))

        upperValue = bin_edges[binIndex]
        lowerValue = bin_edges[binIndex-1]

        ## Shuffle list and choose first solution between edges to mark as herd target
        copyParetoFrontSubList = copy.copy(paretoFrontSubList)
        random.shuffle(copyParetoFrontSubList)
        elem = 0
        for x in copyParetoFrontSubList:
            if lowerValue <= x <= upperValue:
                elem = x
                break
        argsIndex = paretoFrontSubList.index(elem)

        ## Set target of herd
        Animal.target = paretoArgs[argsIndex]

    ## Aply random start position of herd
    start = [ np.random.sample() * (lims[i][1] - lims[i][0]) + lims[i][0] for i in range(len(lims)) ]

    ## Create animals (solutions)
    for i in range(wildebeest):
        animals.append(Animal(copy.copy(start), "wildebeest"))
    for i in range(zebras):
        animals.append(Animal(copy.copy(start), "zebra"))
    for i in range(gazelles):
        animals.append(Animal(copy.copy(start), "gazelle"))

    ## While any animal alives
    while len(animals) > 0:
        ### Create gif - create plots
        if record == 1:
            points1.clear()
            points2.clear()
            fig = plt.figure(figsize=(12,6))
            ax = fig.add_subplot(121)
            ax.set_title(f"Animals coords, herd {k+1}, step {kk}")
            filename = f'{frameDir}{k}--{kk}.png'
            filenames1.append(filename)
            ax.set_xlim(lims[0])
            ax.set_ylim(lims[1])
            ax.scatter(Animal.target[0], Animal.target[1], c = "green", alpha = 0.2, s = 200)
            ax.grid(True)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

            ax2 = fig.add_subplot(122)
            ax2.set_title(f"Pareto Front of solutions")
            ax2.set_xlim(expectedResultLims[0])
            ax2.set_ylim(expectedResultLims[1])
            ax2.scatter(functions[0](Animal.target), functions[1](Animal.target), c = "green", alpha = 0.2, s = 200)
            ax2.grid(True)
            ax2.set_xlabel("f1(x,y)")
            ax2.set_ylabel("f2(x,y)")
        ###

        ## Animals move in random order
        random.shuffle(animals)
        for animal in tqdm(animals, ascii=True, desc="Moving animals"):
            animal.calculatePerformance()
            animal.move()
        ## Preadator are eating animals
        for i in range(predators):
            if len(animals) > 0:
                animals.pop(0)
        ### Create gif - plotting data
        if record == 1:
            for point in points1:
                ax.scatter(point[0], point[1], c = "blue", alpha = 0.2)
            for point in paretoArgs:
                ax.scatter(point[0], point[1], c = "red", alpha = 0.2)
            for point in points2:
                ax2.scatter(point[0], point[1], c = "blue", alpha = 0.2)
            for point in paretoFront:
                ax2.scatter(point[0], point[1], c = "red", alpha = 0.2)
                
            plt.savefig(filename)
            plt.close()
            kk+=1
        ###

## Show pareto solutions in console

for elem, elem2 in zip(paretoFront, paretoArgs):
    print(f"Args: {elem2}")
    print(f"Value: {elem}")

## Save pareto solutions and args of them to files
np.savetxt(paretoFrontDir, paretoFront, delimiter='\t')
np.savetxt(argsDir, paretoArgs, delimiter='\t')

### Create gif - creating gif from plots
if record == 1:
    images = []
    for file_path in filenames1:
            images.append(imageio.imread(file_path))

    file_path = filenames1[-1]

    for _ in range(10):
        images.append(imageio.imread(file_path))

    imageio.mimsave(gifDir, images, fps=3)

    ## remove files
    for filename in set(filenames1):
        os.remove(filename)
###
