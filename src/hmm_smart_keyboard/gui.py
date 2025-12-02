import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from wordfreq import top_n_list

from hmm_smart_keyboard.GUI.layout_colorwidget import Color
from hmm_smart_keyboard.keyboard_model import KeyboardModel
from hmm_smart_keyboard.language_model import LanguageModel
from hmm_smart_keyboard.viterbi_decoder import ViterbiDecoder


class MainWindow(QMainWindow):
    results = None
    historial = None

    def __init__(self):
        super().__init__()

        # Variables
        self.results = {
            "corrected_text": "",
            "original_text": "",
            "best_score": 00000,
            "audit_data": [],
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

        ## LCD Panel
        lcdpanel = QLCDNumber()
        lcdpanel.setDigitCount(10)
        lcdpanel.display(round(9999, 2))

        ## Salida tipo consola
        consola = QPlainTextEdit("Null")
        consola.setReadOnly(True)
        consola.setFont(QFont("Consolas", 11))

        ## Original
        originallabel = QPlainTextEdit(self.results["original_text"])
        originallabel.setReadOnly(True)

        ## Corregido
        corregidolabel = QPlainTextEdit(self.results["corrected_text"])
        corregidolabel.setReadOnly(True)

        # Ventana

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
            self.results = decoder.solve(texto)
            self.results["original_text"] = texto
            resultado = Resultado(
                self.results["corrected_text"],
                self.results["original_text"],
                self.results["best_score"],
                self.results["audit_data"],
            )

            actualizar_resultados(resultado)
            actualizar_interfaz(resultado)
            limpiarentrada()

        def limpiarentrada():
            """Limpia la entrada de texto."""
            entrada.setText("")

        def actualizar_resultados(resultado):
            """Actualiza elementos de interfaz."""
            self.historial.append(resultado)
            ficharesultado = QLabel()
            temp = (
                resultado.original_text[:20]
                if len(resultado.original_text) > 20
                else resultado.original_text
            )
            temp2 = (
                resultado.corrected_text[:20]
                if len(resultado.corrected_text) > 20
                else resultado.corrected_text
            )
            ficharesultado.setText(
                f"{resultado.id} - {temp} - {temp2} - {round(resultado.best_score,3)}"
            )
            item = QListWidgetItem()
            item.setSizeHint(ficharesultado.sizeHint())
            listahistorico.addItem(item)
            listahistorico.setItemWidget(item, ficharesultado)

        def actualizar_interfaz(resultado):
            """Actualiza elementos de interfaz."""

            original = resultado.original_text
            corregido = resultado.corrected_text
            score = resultado.best_score
            ranking = resultado.ranking

            originallabel.setPlainText(original)
            corregidolabel.setPlainText(corregido)
            lcdpanel.display(round(score,3))
            mostrarranking(ranking)

        def itemclicked(item):
            widget = listahistorico.itemWidget(item)
            resultadoid = widget.text().split(" - ")[0]
            resultadoid = buscar_por_id(int(resultadoid))
            actualizar_interfaz(resultadoid)

        listahistorico.itemClicked.connect(itemclicked)

        def buscar_por_id(id_buscado):
            """
            Busca un resultado por su id.

            :param lista_objetos: lista de objetos que tienen un atributo 'id'
            :param id_buscado: id que se quiere buscar
            :return: el objeto que coincide o None si no se encuentra
            """
            for obj in self.historial:
                if obj.id == id_buscado:
                    return obj
            return None

        def mostrarranking(ranking):
            texto = ""
            for item in ranking:
                for a in item:
                    texto += f"{a['palabra']} CTX:{round(a['ctx'],3)} KBD:{round(a['kbd'],3)} TOTAL:{a['total']}\n"
                texto += "\n\n"
            consola.setPlainText(texto)
            return texto

        consola.setPlainText(mostrarranking(self.results["audit_data"]))

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
        col2.addWidget(QLabel("Score"))
        col2.addWidget(lcdpanel, stretch=1)
        col2.addWidget(QLabel("Ranking"))
        col2.addWidget(consola, stretch=6)
        col2.addWidget(QLabel("Texto Original"))
        col2.addWidget(originallabel, stretch=1)
        col2.addWidget(QLabel("Texto Corregido"))
        col2.addWidget(corregidolabel, stretch=1)

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

    def __init__(self, corrected_text, original_text, best_score, audit_data):
        self.id = Resultado._id_counter  # asigna el ID actual
        Resultado._id_counter += 1  # aumenta para la próxima instancia

        self.corrected_text = corrected_text
        self.original_text = original_text
        self.best_score = best_score
        self.original_text = original_text
        self.ranking = []
        if isinstance(audit_data, list):
            for a in audit_data:
                self.ranking.append(a["ranking"])
        else:
            self.ranking.append(audit_data["ranking"])

# 1. Inicializar modelo
vocab = top_n_list("es", 20000)
km = KeyboardModel(vocab)
lm = LanguageModel()  # usa data/P_matrix_transicion.json

decoder = ViterbiDecoder(language_model=lm, keyboard_model=km)

# QT INIT
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

