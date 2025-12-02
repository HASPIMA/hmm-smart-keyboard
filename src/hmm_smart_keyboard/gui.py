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
            "best_score": 9999,
            "audit_data": {
                "input_original": "",
                "ganador": "",
                "ranking": [
                    {
                        "palabra": "",
                        "ctx": "",
                        "kbd": "",
                        "total": "",
                    }
                ],
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

        ## LCD Panel
        lcdpanel = QLCDNumber()
        lcdpanel.setDigitCount(10)
        lcdpanel.display(round(9999, 2))

        ## Salida tipo consola
        consola = QPlainTextEdit("Null")
        consola.setReadOnly(True)
        consola.setFont(QFont("Consolas", 11))

        ## Original
        originallabel = QPlainTextEdit(self.results["audit_data"]["input_original"])
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

            self.results["audit_data"]["input_original"] = texto
            resultado = Resultado(
                self.results["corrected_text"], 156, self.results["audit_data"]
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
                f"{resultado.id} - {temp} - {temp2} - {resultado.best_score}"
            )
            item = QListWidgetItem()
            item.setSizeHint(ficharesultado.sizeHint())
            listahistorico.addItem(item)
            listahistorico.setItemWidget(item, ficharesultado)
            for a in self.historial:
                print(a.id, a.original_text, a.best_score)

        def actualizar_interfaz(resultado):
            """Actualiza elementos de interfaz."""

            original = resultado.original_text
            corregido = resultado.corrected_text
            score = resultado.best_score
            ranking = resultado.ranking

            originallabel.setPlainText(original)
            corregidolabel.setPlainText(corregido)
            lcdpanel.display(round(score))
            mostrarranking(ranking)

        def itemclicked(item):
            widget = listahistorico.itemWidget(item)
            resultadoid = widget.text().split(" - ")[0]
            resultadoid = buscar_por_id(int(resultadoid))
            actualizar_interfaz(resultadoid)
            if widget:
                print("Contenido del QLabel:", widget.text())

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

        #  "ranking": {
        #     "palabra": "Palabra",
        #     "ctx": "Ctx",
        #     "kbd": "Kbd",
        #     "total": "Total",
        # },
        def mostrarranking(ranking):
            texto = ""
            for pos in ranking:
                texto = (
                    texto
                    + f"Palabra: {pos['palabra']} - Ctx: {pos['ctx']} - Kbd: {pos['kbd']} - Total: {pos['total']} \n"
                )
            consola.setPlainText(texto)
            return texto

        consola.setPlainText(mostrarranking(self.results["audit_data"]["ranking"]))

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

        # app.setStyleSheet("""
        #     QWidget {
        #         background-color: #2b2b2b;
        #         color: #f0f0f0;
        #         font-family: Consolas, Courier, monospace;
        #         font-size: 12px;
        #     }
        #     QPushButton {
        #         background-color: #3c3f41;
        #         border: 1px solid #5c5c5c;
        #         padding: 5px;
        #     }
        #     QPushButton:hover {
        #         background-color: #505354;
        #     }
        #     QLineEdit, QPlainTextEdit, QTextEdit {
        #         background-color: #353535;
        #         color: #f0f0f0;
        #         border: 1px solid #5c5c5c;
        #     }
        # """)

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
        self.id = Resultado._id_counter  # asigna el ID actual
        Resultado._id_counter += 1  # aumenta para la próxima instancia

        self.corrected_text = corrected_text
        self.best_score = best_score
        self.original_text = audit_data["input_original"]
        self.ganador = audit_data["ganador"]
        self.ranking = audit_data["ranking"]


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
