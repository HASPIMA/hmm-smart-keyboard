import sys
# QT IMPORTS
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from .GUI.layout_colorwidget import Color

# Apps Imports
from .language_model import LanguageModel
from .keyboard_model import KeyboardModel
from .viterbi_decoder import ViterbiDecoder

from wordfreq import top_n_list

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Campop de entrada
        entrada = QLineEdit()
        entrada.setPlaceholderText("Escribe tu texto")
        

        # Botón de enviar
        botonEnviar = QPushButton("Enviar")
        
        #Hace lo mismo que el click al presionar enter
        entrada.returnPressed.connect(botonEnviar.click)
        # Acción del botón
        botonEnviar.clicked.connect(lambda: print(entrada.text()))


        form = QHBoxLayout()
        form.addWidget(entrada, stretch=5)
        form.addWidget(botonEnviar, stretch=1)


        # Columna 1
        col1 = QVBoxLayout()
        col1.addWidget(QListWidget(), stretch=3)
        col1.addLayout(form, stretch=2)

        # Columna 2
        col2 = QVBoxLayout()
        col2.addWidget(QLCDNumber().setNumDigits(3), stretch=1)
        col2.addWidget(QLabel("Ranking"), stretch=6)
        col2.addWidget(QLabel("Hello"),stretch=2)

        #Main Layout
        layout = QHBoxLayout()
        layout.addLayout(col1,stretch=1)
        layout.addLayout(col2,stretch=1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


        self.setWindowTitle("Smart KeyBoard")
        self.setFixedSize(QSize(800, 600))


# 1. Inicializar modelos (esto es lo “pesado” una sola vez)
vocab = top_n_list("es", 20000)
km = KeyboardModel(vocab)
lm = LanguageModel()  # usa data/P_matrix_transicion.json
decoder = ViterbiDecoder(language_model=lm, keyboard_model=km)

# QT INIT
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()