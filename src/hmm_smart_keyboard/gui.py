import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from wordfreq import top_n_list

from .GUI.layout_colorwidget import Color
from .keyboard_model import KeyboardModel
from .language_model import LanguageModel
from .viterbi_decoder import ViterbiDecoder


class MainWindow(QMainWindow):
    results = None
    historial = None

    def __init__(self):
        super().__init__()

        # Variables
        self.results = {
            "corrected_text": "hola",
            "best_score": 100,
            "audit_data": {
                "input_original": "iOriginal",
                "ganador": "Ganador",
                "ranking": {
                    "palabra": "Palabra",
                    "ctx": "Ctx",
                    "kbd": "Kbd",
                    "total": "Total",
                },
            },
        }
        self.historial = []

        # Objetos
        ## Campop de entrada
        entrada = QLineEdit()
        entrada.setPlaceholderText("Escribe tu texto")

        ## Botón de enviar
        botonenviar = QPushButton("Enviar")

        ## Hitorial
        listahistorico = QListWidget()

        # Acciones de obje1tos
        ## Hace lo mismo que el click al presionar enter
        entrada.returnPressed.connect(botonenviar.click)

        ## Activa la funcion principal
        botonenviar.clicked.connect(lambda: sendtext())

        # Funciones
        def sendtext():
            """
            Enviar texto a procesar, es la funcion principal
            No requiere argumentos.
            Actualiza y limpia la interfaz.
            """
            texto = entrada.text().strip()
            if texto == "":
                return

            # Enviar texto a modelo de lenguaje
            # Aca falta tomar el dato dado por el modelo y pasarlo a objeto Resultado
            resultado = Resultado(texto, 156, {})
            print(texto)
            actualizar_resultados(resultado)
            actualizar_interfaz(resultado)
            limpiarentrada()
            print(self.historial)

        def limpiarentrada():
            """Limpia la entrada de texto."""
            entrada.setText("")

        def actualizar_resultados(resultado):
            """Actualiza elementos de interfaz."""
            self.historial.append(resultado)
            print("Actualizar Resultados")

        def actualizar_interfaz(resultado):
            """Actualiza elementos de interfaz."""
            ficharesultado = QLabel()
            ficharesultado.setText(f"{resultado.id} - {resultado.corrected_text} - {resultado.best_score}")

            item = QListWidgetItem()
            item.setSizeHint(ficharesultado.sizeHint())
            listahistorico.addItem(item)
            listahistorico.setItemWidget(item, ficharesultado)
            print("Actualizar Interfaz")

        def itemclicked(item):
            print("Item clickeado!")
            widget = listahistorico.itemWidget(item)

            if widget:
                print("Contenido del QLabel:", widget.text())
        listahistorico.itemClicked.connect(itemclicked)

        def buscar_por_id(lista_objetos, id_buscado):
            """
            Busca un objeto en una lista por su id.

            :param lista_objetos: lista de objetos que tienen un atributo 'id'
            :param id_buscado: id que se quiere buscar
            :return: el objeto que coincide o None si no se encuentra
            """
            for obj in lista_objetos:
                if obj.id == id_buscado:
                    return obj
            return None

        # Layouts
        ## Form
        form = QHBoxLayout()
        form.addWidget(entrada, stretch=5)
        form.addWidget(botonenviar, stretch=1)

        ## Columna 1
        col1 = QVBoxLayout()
        col1.addWidget(listahistorico, stretch=3)
        col1.addLayout(form, stretch=2)

        ## Columna 2
        col2 = QVBoxLayout()
        col2.addWidget(QLCDNumber(), stretch=1)
        col2.addWidget(QLabel("Ranking"), stretch=6)
        col2.addWidget(QLabel("Hello"), stretch=2)

        ## Main Layout
        layout = QHBoxLayout()
        layout.addLayout(col1, stretch=1)
        layout.addLayout(col2, stretch=1)

        # Main Config
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setWindowTitle("Smart KeyBoard")
        self.setFixedSize(QSize(800, 600))

class Resultado:
    # Variable de clase (compartida entre todas las instancias)
    _id_counter = 1

    def __init__(self, corrected_text, best_score, audit_data):
        self.id = Resultado._id_counter   # asigna el ID actual
        Resultado._id_counter += 1        # aumenta para la próxima instancia

        self.corrected_text = corrected_text
        self.best_score = best_score
        self.audit_data = audit_data

# 1. Inicializar modelos (esto es lo “pesado” una sola vez)

# vocab = top_n_list("es", 20000)
# km = KeyboardModel(vocab)
# lm = LanguageModel()  # usa data/P_matrix_transicion.json
# decoder = ViterbiDecoder(language_model=lm, keyboard_model=km)

# QT INIT
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()