import random
import matplotlib.pyplot as plt
from TT import TIMETABLE 
import time as timer
import numpy as np
# Особь - кортеж (А,В,А,А,А,В,А,В,В,А) И РАСПИСАНИЕ ПО ЭТОЙ КОМБИНАЦИИ
# РАЗМЕР популяции - N таких особей
# N0a - длина кортежа, одной особи
# Кроссинговер - скрещивание кортежей
# Мутация - меняем A / B
# Фитнес Функция - N<, нагрузка>
# константы задачи

class GA:
    def __init__(self, N, generations, p_cr, p_mut, s):
        # константы генетического алгоритма           
        self.POPULATION_SIZE = N   # количество индивидуумов в популяции
        self.P_CROSSOVER = p_cr        # вероятность скрещивания
        self.P_MUTATION = p_mut        # вероятность мутации индивидуума
        self.MAX_GENERATIONS = generations    # максимальное количество поколений
        self.tt = TIMETABLE(stream=s)
        self.tt.startSearching()
        self.IND_LENGTH = self.tt.nA0  # длина подлежащей оптимизации битовой строки    

    class FitnessMax():
        def __init__(self):
            self.values = [0]
    
    class Individual(list):
        def __init__(self, *args):
            super().__init__(*args)
            self.fitness = GA.FitnessMax()           
    
    def oneMaxFitness(self, individual):
        combination = self.translateInd(individual)      
        n, capacity = self.tt.buildCombination(combination)
        return capacity, 

    def individualCreator(self):
        return GA.Individual([random.randint(0, 1) for i in range(self.IND_LENGTH)])
 
    def populationCreator(self, n = 0):
        return list([self.individualCreator() for i in range(n)])
    
    def translateInd(self, bits_ind):
        return tuple('A' if bit == 0 else 'B' for bit in bits_ind)

    def start(self):
        start_time = timer.time()
        p_comb = tuple('B' for _ in range(self.IND_LENGTH+1) )
        n0, max_capacity = self.tt.buildCombination(p_comb)

        population = self.populationCreator(n=self.POPULATION_SIZE) 
        generationCounter = 0

        fitnessValues = list(map(self.oneMaxFitness, population))
    
        for individual, fitnessValue in zip(population, fitnessValues):
            individual.fitness.values = fitnessValue

        maxFitnessValues = []
        meanFitnessValues = []

        fitnessValues = [individual.fitness.values[0] for individual in population]

        while max(fitnessValues) < max_capacity and generationCounter < self.MAX_GENERATIONS:
            generationCounter += 1
            offspring = self.selTournament(population, len(population))
            offspring = list(map(self.clone, offspring))
        
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.P_CROSSOVER:
                    self.cxOnePoint(child1, child2)
        
            for mutant in offspring:
                if random.random() < self.P_MUTATION:
                    self.mutFlipBit(mutant, indpb=1.0/self.IND_LENGTH)
        
            freshFitnessValues = list(map(self.oneMaxFitness, offspring))
            for individual, fitnessValue in zip(offspring, freshFitnessValues):
                individual.fitness.values = fitnessValue
        
            population[:] = offspring
        
            fitnessValues = [ind.fitness.values[0] for ind in population]
        
            maxFitness = max(fitnessValues)
            meanFitness = sum(fitnessValues) / len(population)
            maxFitnessValues.append(maxFitness)
            meanFitnessValues.append(meanFitness)
        
        
            best_index = fitnessValues.index(max(fitnessValues))
            order = population[best_index]
            driver_list = self.translateInd(order)
            # print(f"Поколение {generationCounter}: Макс приспособ. = {maxFitness}, Средняя приспособ.= {meanFitness}")
            # print("Лучший индивидуум = ", *population[best_index], "\n")
            # print("Лучший индивидуум = ", driver_list, "\n")
        print(f"Поколение {generationCounter}: Макс приспособ. = {maxFitness}, Средняя приспособ.= {meanFitness}")
        print("Лучший индивидуум =", driver_list, "\n")
        end_time = timer.time()
        execution_time = end_time - start_time
        print(f"Время выполнения: {np.round(execution_time,3)} секунд")
        # plt.plot(maxFitnessValues, color='red')
        # plt.plot(meanFitnessValues, color='green')
        # plt.xlabel('Поколение')
        # plt.ylabel('Макс/средняя приспособленность')
        # plt.title('Зависимость максимальной и средней приспособленности от поколения')
        # plt.show()
        return driver_list

    def clone(self, value):
        ind = GA.Individual(value[:])
        ind.fitness.values[0] = value.fitness.values[0]
        return ind
    
    
    def selTournament(self, population, p_len):
        offspring = []
        for n in range(p_len):
            i1 = i2 = i3 = 0
            while i1 == i2 or i1 == i3 or i2 == i3:
                i1, i2, i3 = random.randint(0, p_len-1), random.randint(0, p_len-1), random.randint(0, p_len-1)
            # подходит, потому что B(1) эффективнее
            offspring.append(max([population[i1], population[i2], population[i3]], key=lambda ind: ind.fitness.values[0]))
    
        return offspring
    
    def cxOnePoint(self, child1, child2):
        s = random.randint(2, len(child1)-3)
        child1[s:], child2[s:] = child2[s:], child1[s:]
    
    
    def mutFlipBit(self, mutant, indpb=0.01):
        for indx in range(len(mutant)):
            if random.random() < indpb:
                mutant[indx] = 0 if mutant[indx] == 1 else 1
# generations = 10
# p_cr = 0.9
# p_mut = 0.1
# N_ind = 11
# ga = GA(N_ind, generations, p_cr, p_mut, s=10000)    
# print(ga.start())
