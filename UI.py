import sys
from TT import TIMETABLE
from GA import GA
from datetime import time, timedelta
from PySide6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QLineEdit,QPushButton,QTabWidget,QTableView, QCheckBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

class TimetableTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 22

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
        
            if row < len(self._data):
                item = self._data[row]
                key = list(item.keys())[0]

                if col == 0:
                    return key
                else:
                    values = list(item.values())[0]#массив значений .strftime("%H:%M")
                    if col - 1 < len(values):
                        return values[col - 1].strftime("%H:%M")          
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(section) if section > 0 else "id"
            return None
        
    def update_data(self, new_data):
        self._data = new_data
        self.beginResetModel()
        self.endResetModel()    

class DriversTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 4  # id, тип, нагрузка, время

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:      
            return self._data[index.row()][list(self._data[index.row()].keys())[index.column()]]
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["ID водителя", "Тип", "Нагрузка", "Время начала работы"]
            return headers[section] if section < len(headers) else None
        return None
    
    def update_data(self, new_data):
        self._data = new_data
        self.beginResetModel()     
        self.endResetModel()

#######################################################################################################
class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timetable UI")
        self.main_layout = QVBoxLayout()
        title = QLabel("ИП Градов", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.tt = TIMETABLE(stream=10000)
        self.tt.startSearching()

        self.checkbox = QCheckBox("Использовать новейшие Генетические алгоритмы")
        subtitle = QLabel("Здесь вы можете задать параметры автопарка и алгоритма", alignment=Qt.AlignLeft)       
        checkbox_layout = QVBoxLayout()
        cb_hbox = QHBoxLayout()
        cb_hbox.addWidget(subtitle)
        cb_hbox.addWidget(self.checkbox)
        checkbox_layout.addLayout(cb_hbox)

        # edit fields
        self.fields = []
        self.fields.append(QLineEdit("20"))
        self.fields.append(QLineEdit("10000"))
        self.fields.append(QLineEdit("40/70"))
        self.fields.append(QLineEdit("15000"))
        self.fields.append(QLineEdit("10"))
        self.fields.append(QLineEdit("11"))
        self.fields.append(QLineEdit("0.1"))
        self.fields.append(QLineEdit("0.9"))

        fields_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox1.addWidget(QLabel("N автобусов"))
        hbox1.addWidget(self.fields[0])
        hbox1.addWidget(QLabel("Стоимость проезда"))
        hbox1.addWidget(self.fields[2])
        hbox1.addWidget(QLabel("Количество эпох"))
        hbox1.addWidget(self.fields[4])
        hbox1.addWidget(QLabel("Коэф.мутации"))
        hbox1.addWidget(self.fields[6])

        hbox2.addWidget(QLabel("Поток людей"))
        hbox2.addWidget(self.fields[1])
        hbox2.addWidget(QLabel("Аренда"))
        hbox2.addWidget(self.fields[3])
        hbox2.addWidget(QLabel("Х индивидов в популяции"))
        hbox2.addWidget(self.fields[5])
        hbox2.addWidget(QLabel("Коэф.селекции"))
        hbox2.addWidget(self.fields[7])
        fields_layout.addLayout(hbox1)
        fields_layout.addLayout(hbox2)

        ok_button = QPushButton("РАССЧИТАТЬ")
        ok_button.clicked.connect(self.on_ok)      

        self.main_layout.addWidget(title)
        self.main_layout.addLayout(checkbox_layout)
        self.main_layout.addLayout(fields_layout)
        self.main_layout.addWidget(ok_button)
        self.createTable([])

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def createTable(self, inputs):
        self.mocked_data1 = self.tt.days
        self.mocked_data2 = {
            'Понедельник': self.tt.showDriverSchedule("Понедельник"),
            'Вторник': self.tt.showDriverSchedule("Вторник"),
            'Среда': self.tt.showDriverSchedule("Среда"),
            'Четверг': self.tt.showDriverSchedule("Четверг"),
            'Пятница': self.tt.showDriverSchedule("Пятница"),
            'Суббота': self.tt.showDriverSchedule("Суббота"),
            'Воскресенье': self.tt.showDriverSchedule("Воскресенье")
            }
        # tabs
        self.tabs = QTabWidget()
        self.tab_widgets = {
            "Понедельник": self.create_tab("Понедельник"),
            "Вторник": self.create_tab("Вторник"),
            "Среда": self.create_tab("Среда"),
            "Четверг": self.create_tab("Четверг"),
            "Пятница": self.create_tab("Пятница"),
            "Суббота": self.create_tab("Суббота"),
            "Воскресенье": self.create_tab("Воскресенье"),
        }

        for day, widget in self.tab_widgets.items():
            self.tabs.addTab(widget, day)
        self.main_layout.addWidget(self.tabs)

    def create_tab(self, day):
        tab_layout = QVBoxLayout()
        self.table1 = QTableView()
        self.table2 = QTableView()
        # TT таблица
        timetable_data = self.mocked_data1.get(day, [])
        self.model1 = TimetableTableModel(timetable_data)
        self.table1.setModel(self.model1)
        tab_layout.addWidget(self.table1)

        # Drivers таблица      
        driver_data = self.mocked_data2.get(day, [])       
        self.model2 = DriversTableModel(driver_data)
        self.table2.setModel(self.model2)   
        tab_layout.addWidget(self.table2)

        tab_widget = QWidget()
        tab_widget.setLayout(tab_layout)
        return tab_widget
    
    def update_tables(self):
        for day in self.tab_widgets.items():
            # Получаем новые данные
            timetable_data = self.mocked_data1.get(day, [])
            driver_data = self.mocked_data2.get(day, [])    
            self.model1.update_data(timetable_data)
            # self.table1.setModel(self.model1)  
            self.model2.update_data(driver_data)
            # self.table2.setModel(self.model2)     
            self.table1.repaint()
            self.table2.repaint() 

        self.tabs.repaint()
        
    def on_ok(self): 
        self.main_layout.removeWidget(self.tabs)
        self.tabs.deleteLater()
        if self.checkbox.isChecked():
            print("Подключаем ГА")
            values = [field.text() for field in self.fields]
            generations = int(values[4])
            p_cr = float(values[7])
            p_mut = float(values[6])
            N_ind = int(values[5])
            ga = GA(N_ind, generations, p_cr, p_mut, s=int(values[1]))    
            
            self.tt.buildCombination(ga.start())
            self.mocked_data1 = self.tt.days
            self.mocked_data2 = {
                'Понедельник': self.tt.showDriverSchedule("Понедельник"),
                'Вторник': self.tt.showDriverSchedule("Вторник"),
                'Среда': self.tt.showDriverSchedule("Среда"),
                'Четверг': self.tt.showDriverSchedule("Четверг"),
                'Пятница': self.tt.showDriverSchedule("Пятница"),
                'Суббота': self.tt.showDriverSchedule("Суббота"),
                'Воскресенье': self.tt.showDriverSchedule("Воскресенье")
            }
            self.createTable([])
        else:
            print("Перебор")
            values = [self.fields[i].text() for i in range(0,4)]
            self.tt.buildCombination(self.tt.findBestCombination())
            self.mocked_data1 = self.tt.days
            self.mocked_data2 = {
                'Понедельник': self.tt.showDriverSchedule("Понедельник"),
                'Вторник': self.tt.showDriverSchedule("Вторник"),
                'Среда': self.tt.showDriverSchedule("Среда"),
                'Четверг': self.tt.showDriverSchedule("Четверг"),
                'Пятница': self.tt.showDriverSchedule("Пятница"),
                'Суббота': self.tt.showDriverSchedule("Суббота"),
                'Воскресенье': self.tt.showDriverSchedule("Воскресенье")
            }
            self.createTable([])
        # print(values)
 
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())