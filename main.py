import numpy as np
import random
import copy
import matplotlib.pyplot as plt
import os
import imageio
## Paths to files with matrix: distance and cost 
mainDir = "data/cities-47-"
distanceDir = mainDir + "distance.txt"
costDir = mainDir + "cost.txt"
paretoFrontDir = "results/paretoFront12.txt"
delim = " "
matricesNumber = 2

# Parameters
movie = 0
maxCycle = 300

wildebeest = 500
zebras = 80
gazelles = 40
crocodiles = 6

starving = 3

## Read data from files
distance = np.genfromtxt(distanceDir, delimiter=delim)

#cost = np.genfromtxt(costDir, delimiter=delim)
cost = np.genfromtxt(costDir, delimiter=delim).T

print("Distance matrix:")
print(distance)
print("\nCost matrix:")
print(cost)

## Init variables
matrices = [distance, cost]
cities = cost.shape[0]

paretoFront = []
paretoPath = []

###
if movie == 1:
    points = []
    filenames = []
###

class Animal:
    tabooList = []
    target = []
    def __init__(self, start, species):
        self.solution = start
        self.species = species
        self.die = 0
        self.starve = starving
        
    def calculatePerformance(self):
        global paretoFront
        global paretoPath
        path = np.linspace(0,0,matricesNumber)
        for i in range(cities):
            index = i-1
            for j in range(matricesNumber):
                path[j] += matrices[j][self.solution[index]][self.solution[i]]
        indexes = []
        flagAdd = 1
        for i in range(len(paretoFront)):
            validArray = np.linspace(0,0,matricesNumber)
            for j in range(matricesNumber):
                if path[j] < paretoFront[i][j]:
                    validArray[j] = 1
                elif path[j] > paretoFront[i][j]:
                    validArray[j] = -1
            if 1 in validArray and not -1 in validArray:
                indexes.append(i)
            if -1 in validArray and not 1 in validArray:
                flagAdd = 0
            if not 1 in validArray and not -1 in validArray:
                flagAdd = 0
        paretoFront = [i for j,i in enumerate(paretoFront) if j not in indexes]
        paretoPath = [i for j,i in enumerate(paretoPath) if j not in indexes]
        if flagAdd == 1:
            paretoFront.append(path)
            paretoPath.append(self.solution)

        ###
        if movie == 1:
            points.append(path)
        ###

    def move(self):
        permutationsCounter = 0
        if self.species == "wildebeest":
            permutationsCounter = 1 
        elif self.species == "zebra":
            permutationsCounter = 2
        elif self.species == "gazelle":
            permutationsCounter = 3
            
        if Animal.target in Animal.tabooList:
            while permutationsCounter > 0:
                a = np.random.randint(cities)
                b = np.random.randint(cities)
                t = self.solution[a]
                self.solution[a] = self.solution[b]
                self.solution[b] = t
                permutationsCounter -= 1
            if not self.solution in Animal.tabooList:
                Animal.tabooList.append(copy.copy(self.solution))
            else:
                self.starve -= 1
                if self.starve == 0:
                    self.die = 1
        else:
            for i in random.sample(range(cities), cities):
                if self.solution[i] == Animal.target[i]:
                    continue
                a = np.where(np.array(self.solution) == Animal.target[i])
                t = self.solution[i]
                self.solution[i] = self.solution[a[0][0]]
                self.solution[a[0][0]] = t
                permutationsCounter -= 1
                if permutationsCounter == 0:
                    break
            if not self.solution in Animal.tabooList:
                Animal.tabooList.append(copy.copy(self.solution))
            else:
                self.starve -= 1
                if self.starve == 0:
                    self.die = 1
                    
        
animals = []
for k in range(maxCycle):
    ###
    if movie == 1:
        kk = 1
    ### 
    if k%10 == 9:
        print(f"Iter: {k+1}")
        np.savetxt(paretoFrontDir, paretoFront, delimiter='\t')

    Animal.tabooList.clear()
    Animal.target = []
    animals.clear()
    if len(paretoFront) == 0:
        Animal.target = random.sample(range(cities), cities)
    else:
        Animal.target = paretoPath[np.random.randint(len(paretoPath))]
    
    start = random.sample(range(cities), cities)
    Animal.tabooList.append(start)

    for i in range(wildebeest):
        animals.append(Animal(copy.copy(start), "wildebeest"))
    for i in range(zebras):
        animals.append(Animal(copy.copy(start), "zebra"))
    for i in range(gazelles):
        animals.append(Animal(copy.copy(start), "gazelle"))

    while len(animals) > 0:
        ###
        if movie == 1:
            points.clear()
            fig = plt.figure(figsize=(10,10))
            ax = fig.add_subplot()
            ax.set_title(f"Animals coords, herd {k+1}, step {kk}")
            filename = f'frames/{k}--{kk}.png'
            filenames.append(filename)
            ax.set_xlim([0,10000])
            ax.set_ylim([0,10000])
        ###
        
        random.shuffle(animals)
        for animal in animals:
            animal.calculatePerformance()
            animal.move()
            if animal.die == 1:
                animals.remove(animal)
        for i in range(crocodiles):
            if len(animals) > 0:
                animals.pop(0)
        ###
        if movie == 1:
            for point in points:
                ax.scatter(point[0], point[1], c = "blue", alpha = 0.2)
            for point in paretoFront:
                ax.scatter(point[0], point[1], c = "red", alpha = 0.2)
            plt.savefig(filename)
            plt.close()
            kk+=1
        ###

        
for elem, elem2 in zip(paretoFront, paretoPath):
    print(f"Path: {elem2}")
    print(f"Cost: {elem}")       
np.savetxt(paretoFrontDir, paretoFront, delimiter='\t')

###
if movie == 1:
    images = []
    for file_path in filenames:
            images.append(imageio.imread(file_path))

    file_path = filenames[-1]

    for _ in range(10):
        images.append(imageio.imread(file_path))

    imageio.mimsave('gifs/movie.gif', images, fps=20)

    for filename in set(filenames):
        os.remove(filename)
###
