import pandas as pd
from datetime import time, timedelta
import numpy as np
from DriverClasses import DriverА, DriverB
from itertools import product, combinations_with_replacement
import time as timer

class TIMETABLE:
    def __init__(self, stream):
        self.stream = stream
        self.nA0 = 0
        self.nB0 = 0
        self.drivers = [] #храним объекты водителей
        self.days = { #тут в каждом массиве лежат shedule каждого водителя по дню
            'Понедельник': [],
            'Вторник': [],
            'Среда': [],
            'Четверг': [],
            'Пятница': [],
            'Суббота': [],
            'Воскресенье': []
        }
        self.stream_per_day = {
            'Понедельник': 10000,
            'Вторник': 10000,
            'Среда': 10000,
            'Четверг': 10000,
            'Пятница': 10000,
            'Суббота': 10000,
            'Воскресенье': 10000
        }
        self.setStream(self.stream)
        self.week = self.Week(self.stream_per_day)

    def setStream(self, stream):
        for day in self.stream_per_day.keys():
            self.stream_per_day[day] = stream

    def startSearching(self):
        self.nA0 = self.distributeDrivers("A")
        self.nB0 = self.distributeDrivers("B")
        if self.nA0 > self.nB0:
            print("Оптимальнее набрать водителей типа Б")
        if self.nA0 < self.nB0:
            print("Nooo Оптимальнее набрать водителей типа A")
        print(f"A - {self.nA0}, B - {self.nB0}")

    def findBestCombination(self):
        n_best = None
        capacity_best = None
        comb_best = ()
        combinations = self.generateCombinations()

        for c in combinations:
            n, capacity = self.buildCombination(c)
            if n_best is not None:
                if n < n_best:
                    n_best = n
                    capacity_best = capacity
                    comb_best = c
                elif n == n_best:
                    if capacity > capacity_best:
                        capacity_best = capacity
                        n_best = n
                        comb_best = c
            else:
                n_best = n
                capacity_best = capacity
                comb_best = c
            # по наим н и наиб нагрузке
        return comb_best
    
    def buildCombination(self, combination):
        # аналогично методу distribute
        for day in self.days.keys():
            self.days[day] = []
        self.week = self.Week(self.stream_per_day)
        self.drivers = []
        
        sumCapacity = 0
        count = 0

        for item in combination:
            if item == "A":
                driver = DriverА(f"{count}dA")
            else:
                driver = DriverB(f"{count}dB")
            driver.modelWorkingHours(self.week) #составляет график на неделю одному водителю
            self.week._decreaseWH(driver) #  КАК ВОДИТЕЛИ ПОКРЫВАЮТ НАГРУЗКУ - вычитаем нагрузку из Week
            self.addScheduleToTimetable(driver)
            self.addDriver(driver)
            for d in self.week.days.keys():
                sumCapacity += driver.getCapacityToday(d)
            count += 1
        return len(self.drivers), sumCapacity

    def generateCombinations(self):
        A = 'A'
        B = 'B'
        n = self.nA0
        # Генерация всех комбинаций
        # combinations = list(combinations_with_replacement([A, B], n))
        combinations = list(product([A, B], repeat=n))
        return combinations

    class Week:
        def __init__(self, stream_per_day):
            self.days = {          # 176.47, 1750, 500
                'Понедельник': {}, #{datetime.time(7, 0): 175.0, datetime.time(5, 0): 17.647)
                'Вторник': {},
                'Среда': {},
                'Четверг': {},
                'Пятница': {},
                'Суббота': {},
                'Воскресенье': {}
            }
            self.empty = [1,1,1,1,1,1,1]
            self.distributeStream(stream_per_day)
        
        def __str__(self):
            output = ""
            for day, hours in self.days.items():
                output += f"{day}:\n"
                for hour, stream in sorted(hours.items()):
                    output += f"  {hour.strftime('%H:%M')} - {stream:.2f}\n"
            return output
        
        def distributeStream(self, stream_per_day):
            for day, stream in stream_per_day.items():
                if day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
                    self._distributeWeekday(stream, day)
                else:
                    self._distributeWeekend(stream, day)

        def _distributeWeekend(self, stream, day):
             # 20ч в день
            for hour in [time(h, 0) for h in range(5, 24)] + [time(h, 0) for h in range(0, 2)]:
                self.days[day][hour] = stream / 20

        def _distributeWeekday(self, stream, day):           
            peak_hours_stream = stream * 0.55 / 4
            # Нагрузка для пиковых временных промежутков
            self.days[day][time(7, 0)] = peak_hours_stream
            self.days[day][time(8, 0)] = peak_hours_stream
            self.days[day][time(17, 0)] = peak_hours_stream
            self.days[day][time(18, 0)] = peak_hours_stream

            rest_hours_stream = stream * 0.45
            rest_hours = [time(h, 0) for h in range(5, 24)] + [time(h, 0) for h in range(0, 2)]
            rest_hours.remove(time(7, 0))
            rest_hours.remove(time(8, 0))
            rest_hours.remove(time(17, 0))
            rest_hours.remove(time(18, 0))
            rest_hours_stream = float(np.round(rest_hours_stream / len(rest_hours), 3))

            for hour in rest_hours:
                self.days[day][hour] = rest_hours_stream
        
        def _decreaseWH(self, driver):
            for day in driver.schedule.keys():
                day_capacities = self.days[day]
                times = driver.schedule[day]
                self._setDayIsNotEmpty(day)
                for t in times:
                    if t.minute > 40:
                        t_n = time(t.hour+1, 0)
                    else:
                        t_n = time(t.hour, 0)
                    dCapacity = driver.cost
                    if (time(7, 0) <= t_n < time(9, 0)) or (time(17, 0) <= t_n < time(19, 0)):
                        dCapacity = 5 * dCapacity              
                    elif (time(0, 0) <= t_n < time(7, 0)):
                        dCapacity = 0.8 * dCapacity
                    day_capacities[t_n] -= dCapacity  
        
        def _setDayIsNotEmpty(self, day):
            match day:             
                case "Понедельник":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Вторник":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Среда":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Четверг":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Пятница":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Суббота":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
                case "Воскресенье":
                    if self.empty[0] == 1:
                        self.empty[0] = 0
    ############################
    def addDriver(self, driver):
        self.drivers.append(driver)

    def distributeDrivers(self, type):
        # Сбрасываем расписание
        for day in self.days.keys():
            self.days[day] = []
        self.week = self.Week(self.stream_per_day)
        self.drivers = []
        
        sumCapacity = 0
        totalSum = 0
        count = 0
        for key in self.stream_per_day.keys():
            totalSum += self.stream_per_day[key]
        while sumCapacity < 0.9*totalSum:
            if type == "A":
                driver = DriverА(f"{count}dA")
            else:
                driver = DriverB(f"{count}dB")
            driver.modelWorkingHours(self.week) #составляет график на неделю одному водителю
            self.week._decreaseWH(driver) #  КАК ВОДИТЕЛИ ПОКРЫВАЮТ НАГРУЗКУ - вычитаем нагрузку из Week
            self.addScheduleToTimetable(driver)
            self.addDriver(driver)
            for d in self.week.days.keys():
                sumCapacity += driver.getCapacityToday(d)
            count += 1
        return len(self.drivers)

    def addScheduleToTimetable(self, driver):
        for day, times in driver.schedule.items():
            self.days[day].append({driver.id: times})

    def showTimetable(self): #tabl 1 - id водителя / время отправления(datetime) на маршрут * 7 дней
        # ВЫВОДИМ СОДЕРЖИМОЕ self.days
        # print(self.days)
        for day in self.days.keys():
            print(f"{day}:")
            if not self.days[day] or len(self.days[day]) == 0:
                print("  Нет расписания.") ## CHANGE MAYBE
            else:
                for dict in self.days[day]:
                    for driver_id, times in dict.items():
                        times = [t.strftime("%H:%M") for t in times]
                        print(f"  {driver_id}: {times}")
            print()

    def showDriverSchedule(self, day): #tabl 2 - id водителя / тип водителя / нагрузка на день / время начала работы
        # ВЫВОДИМ getScheduleToday КАЖДОГО ВОДИТЕЛЯ
        shedule = []
        for driver in self.drivers:
            driver_data = driver.getScheduleToday(day)
            
            if driver_data[3] == 0:
                start_time = 0
            else:
                start_time = driver_data[3].strftime("%H:%M")

            shedule.append({
                'id': driver_data[0],
                'Тип': driver_data[1],
                'Общая нагрузка': driver_data[2],
                'Начало работы': start_time,
            })
        # df = pd.DataFrame(shedule)
        # print(f"\nСмены водителей на {day}:")
        # print(df)
        return shedule



#######################
