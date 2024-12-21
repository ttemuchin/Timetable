from datetime import time, timedelta
import numpy as np

class Driver:
    def __init__(self, id):
        self.id = id
        self.T = time(1,0)
        self.schedule = { #тут храним время отправления водителя на маршрут
            'Понедельник': [],
            'Вторник': [],
            'Среда': [],
            'Четверг': [],
            'Пятница': [],
            'Суббота': [],
            'Воскресенье': []
        }

    def getSchedule(self):
        raise NotImplementedError("unknown")       
        
    def calculateSpacesInDay(self, week, day):
        if day not in week.days:
            return [], []
        
        daily_data = week.days[day]
        # daily_data.pop(time(1, 0), None)
        # daily_data.pop(time(5, 0), None)
        # print(daily_data)

        sorted_hours = sorted(daily_data.items(), key=lambda item: item[1])
        hours = [hour for hour, value in sorted_hours[:3]]

        sum_dict = {}
        for key, value in week.days.items():
            sum_dict[key] = sum(value.values())

        sorted_days = sorted(sum_dict.items(), key=lambda item: item[1])
        days = [sorted_days[0][0], sorted_days[1][0]] if len(sorted_days) > 1 else [sorted_days[0][0]]

        return hours, days #([datetime.time(6, 0), datetime.time(9, 0), datetime.time(10, 0)], ['Понедельник', 'Суббота'])

    def calcNextDay(self, day):
        match day:
            case "Понедельник":
                return "Вторник"
            case "Вторник":
                return "Среда"
            case "Среда":
                return "Четверг"
            case "Четверг":
                return "Пятница"
            case "Пятница":
                return "Суббота"
            case "Суббота":
                return "Воскресенье"
            case "Воскресенье":
                return "Понедельник"
            
    def calcDay(self, day):
        match day:
            case "Понедельник":
                return 0
            case "Вторник":
                return 1
            case "Среда":
                return 2
            case "Четверг":
                return 3
            case "Пятница":
                return 4
            case "Суббота":
                return 5
            case "Воскресенье":
                return 6
    
    def getScheduleToday(self, day):
        if len(self.schedule[day]) >= 3: 
            for i in range(3):     
                start_time = self.schedule[day][i]
                if start_time > time(2,0):
                    break
                # print(start_time)
        else:
            start_time = 0

        return [self.id, self.type, self.getCapacityToday(day), start_time]
    
    def getCapacityToday(self, day):#вычисляем, сколько водитель перевёз
        capacity = 0
        if day not in self.schedule:
            raise ValueError("Not a day of week")
        # c_per_hour = []
        for t in self.schedule[day]:
            if (time(7, 0) <= t < time(9, 0)) or (time(17, 0) <= t < time(19, 0)):
                c = 5 * self.cost
                capacity += c
            elif (time(0, 0) <= t < time(7, 0)):
                c = 0.8 * self.cost
                capacity += c              
            else:
                c = self.cost
                capacity += c
            # c_per_hour.append(c)    
        return capacity
        
    def modelWorkingHours(self): 
        raise NotImplementedError("unknown")

class DriverА(Driver):
    def __init__(self, id):
        super().__init__(id)
        self.type = 'A'
        self.cost = 70

        self.days_in_work = 5
        self.hours_per_day = 8  # 9 часов с одним перерывом
        
    def modelWorkingHours(self, week):
        # если нас ставят на день и там уже кто-то есть, надо вычислить когда можно спокойно уйти на перерыв
        # если день чистый то не вычисляем, а просто запускаем моделирование дня
        freeHours, freeDays = self.calculateSpacesInDay(week, 'Понедельник')
        # тут уже нет 5 ам в пн
        # print(week)
        for day in week.days:
            if day not in freeDays:
                # print(day)
                if week.empty[self.calcDay(day)] == 1:
                    freeHours, freeDays = self.calculateSpacesInDay(week, 'Понедельник')
                else:
                    freeHours = None
                # print(day)
                # с 5 до 14 с 6 до 15 с 7 до 16 / c 17 до 02 с 15 до 00 с 16 до 01
                startDayTime = self.chooseStartTime(week, day)
                # print("\n",startDayTime) 

                lunchHour = self.calcLunch(startDayTime, freeHours)
                # start = time(startDayTime.hour, np.random.randint(9)) 

                for i in range(9):
                    # здесь уже прибавляем от стартдей, получаем старт тайм и аппендим в шедул          
                    startTime = time((startDayTime.hour+i)%24, np.random.randint(1,14))   
                    if startDayTime.hour+i != lunchHour:                                
                        if (time(0, 0) <= startTime < time(5, 0)):
                            self.schedule[self.calcNextDay(day)].append(startTime)
                        else:
                            self.schedule[day].append(startTime)

    def chooseStartTime(self, week, day):
        # считаем час где максимальный поток в дне недели выбирая из 5 6 7  23, 00, 01(след день)
        for_starts = [time(5,0),time(6,0),time(7,0),time(23,0),time(0,0),time(1,0)]
        
        all_caps = week.days[day]
        # print("!!!", all_caps)
        all_caps_next = week.days[self.calcNextDay(day)]
        caps_of_hours = [all_caps[for_starts[0]], all_caps[for_starts[1]], all_caps[for_starts[2]], all_caps[for_starts[3]]]
        caps_of_hours.append(all_caps_next[for_starts[4]])
        # print(day, all_caps_next[time(1,0)])

        caps_of_hours.append(all_caps[for_starts[5]])###
        max_index = caps_of_hours.index(max(caps_of_hours))
        if max_index == 5:
            return time(17,0)
        elif max_index == 4:
            return time(16,0)
        elif max_index == 3:
            return time(15,0)
        else:
            return for_starts[max_index]

    def calcLunch(self, startDayTime, freeHours):
        # когда обед считаем сразу из списка часов которые попадают в промежуток
        # если есть совпадения с фриОурс, то берем его и не едем в этот час 
        startH = startDayTime.hour
        allHours = [startH+3, startH+4, startH+5]
        tabu = [7,8,18,17]
        if freeHours is not None:
            for h in freeHours:
                h = h.hour
                if h in allHours:
                    lunch_hour = h
        for i in allHours:
                if i not in tabu:
                    lunch_hour = i
        return lunch_hour

class DriverB(Driver):
    def __init__(self, id):
        super().__init__(id)
        self.type = 'B'
        self.cost = 45

        self.days_in_work = 3
        self.hours_per_day = 16# from 5 to 1 -4h for rest
        
    def calculateFreeDays(self, week):
        d1 = ["Понедельник", "Среда", "Пятница", "Воскресенье"]
        d2 = ["Вторник", "Четверг", "Суббота"]
        c1 = 0
        c2 = 0
        for day in week.days:
            if day in d1:
                sum = 0
                for time in week.days[day].keys():
                    sum += week.days[day][time]
                c1 += sum
            if day in d2:
                sum = 0
                for time in week.days[day].keys():
                    sum += week.days[day][time]
                c2 += sum
        if c1 > c2:
            return d2
        else: 
            return d1
    
    def calcLunches(self, week, day):
        # находим 4 минимальных нагрузки в дне недели, передаем ключи 
        hours = [time(5,0),time(6,0),time(9,0),time(10,0),time(11,0),
                 time(12,0),time(13,0),time(14,0),time(15,0),time(16,0),
                 time(19,0),time(20,0),time(21,0),time(22,0),time(23,0)]
        # hours_next = [time(0,0),time(1,0)]
        hours_small_capacities = sorted(week.days[day], key=week.days[day].get)
        count = 0
        lunches = []
        for t in hours_small_capacities:
            if t in hours:
                lunches.append(t)
                count += 1
            if count >= 4:
                break
        return lunches #4 часа когда можно пойти на обед time
    
    def modelWorkingHours(self, week):
        freeDays = self.calculateFreeDays(week)

        for day in week.days:
            if day not in freeDays:
                # с 5 до 1(2 de facto)next day
                startDayTime = time(5,0)               
                lunchHours = self.calcLunches(week, day)

                for i in range(21):
                    # здесь уже прибавляем от стартдей, получаем старт тайм и аппендим в шедул          
                    startTime = time((startDayTime.hour+i)%24, np.random.randint(1,20))   
                    if startDayTime.hour+i not in lunchHours:                                
                        if (time(0, 0) <= startTime < time(5, 0)):
                            self.schedule[self.calcNextDay(day)].append(startTime)
                        else:
                            self.schedule[day].append(startTime)        