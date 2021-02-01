from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import sys
import requests
import os


map_url = 'http://static-maps.yandex.ru/1.x/?'
geocoder_url = 'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b'
WINDOW_SIZE = 750, 550
MAP_SIZE = 600, 450


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 15
        self.coords = [37.530887, 55.703118]
        self.layout = 'sat'
        self.points = []
        self.get_image()
        self.initUI()
        self.connect_actioins()

    def get_image(self):
        size = ','.join(map(str, MAP_SIZE))
        coords = ','.join(map(str, self.coords))
        z = str(self.z)

        map_request = \
            map_url +\
            'll=' + coords +\
            '&z=' + z +\
            '&size=' + size +\
            '&l=' + self.layout +\
            '&pt=' + '~'.join(self.points)
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def render_image(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def get_geocoder_data(self):
        try:
            data = self.search_bar.toPlainText()
            geocoder_request = geocoder_url +\
                '&geocode=' + data +\
                '&format=json'
            response = requests.get(geocoder_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
            else:
                json_response = response.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_pos = toponym["Point"]["pos"]
                self.points.append(toponym_pos.replace(' ', ',') + ',pm2rdm')
                print(self.points)
                self.change_coords(toponym_pos)
        except Exception as e:
            print(e)

    def change_coords(self, coords):
        self.coords = list(map(float, coords.split()))
        self.get_image()
        self.render_image()

    def initUI(self):
        # Окно
        self.setWindowTitle('Отображение карты')
        self.setGeometry(500, 250, *WINDOW_SIZE)

        # Изображение
        self.image = QLabel(self)
        self.image.move(10, 10)
        self.image.resize(*MAP_SIZE)
        self.render_image()

        # Кнопки
        self.scheme_btn = QPushButton('Схема', self)
        self.scheme_btn.move(650, 30)
        self.scheme_btn.resize(70, 30)

        self.sat_btn = QPushButton('Спутник', self)
        self.sat_btn.move(650, 60)
        self.sat_btn.resize(70, 30)

        self.hybrid_btn = QPushButton('Гибрид', self)
        self.hybrid_btn.move(650, 90)
        self.hybrid_btn.resize(70, 30)

        # Поиск
        self.search_bar = QTextEdit(self)
        self.search_bar.move(10, 480)
        self.search_bar.resize(300, 30)

        self.search_btn = QPushButton('Искать', self)
        self.search_btn.move(320, 480)
        self.search_btn.resize(70, 30)

    def connect_actioins(self):
        self.scheme_btn.clicked.connect(lambda: self.change_layout('map'))
        self.sat_btn.clicked.connect(lambda: self.change_layout('sat'))
        self.hybrid_btn.clicked.connect(lambda: self.change_layout('sat,skl'))

        self.search_btn.clicked.connect(self.get_geocoder_data)

    def change_layout(self, layout):
        if self.layout != layout:
            self.layout = layout
            self.get_image()
            self.render_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if self.z < 17:
                self.z += 1
                self.get_image()
                self.render_image()
        if event.key() == Qt.Key_PageUp:
            if self.z > 1:
                self.z -= 1
                self.get_image()
                self.render_image()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
