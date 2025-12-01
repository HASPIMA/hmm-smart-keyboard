import bz2
import math
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import mwxml
import ujson as json

from hmm_smart_keyboard.utils.text_processing import normalize_text, tokenize

# --- 1. CONFIGURACIÓN Y ARCHIVOS ---

START_TOKEN = "<START>"

# Solución para rutas absolutas: Garantiza encontrar el dump sin importar el CWD
script_path = Path(__file__).resolve()
BASE_DIR = script_path.parent.parent.parent
DUMP_PATH = BASE_DIR / "eswiki-latest-pages-articles-multistream.xml.bz2"

# Guardar la matriz en el directorio data del proyecto
current_dir = Path(__file__).parent
data_dir = current_dir / "data"
OUTPUT_FILENAME = data_dir / "P_matrix_transicion.json"


# --- 2. PRE-PROCESAMIENTO Y LIMPIEZA ---


def clean_wiki_markup(text: str) -> str:
    """Elimina rudimentariamente el wiki-markup de un texto."""
    # Eliminar llamadas a plantillas (ej: {{cita web|...}})
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    # Eliminar enlaces internos con formato (ej: [[inteligencia artificial|IA]])
    text = re.sub(r"\[\[[^|]*\|", "[[", text)
    # Eliminar texto entre corchetes (a menudo referencias)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    # Eliminar tags HTML
    text = re.sub(r"<[^>]+>", "", text)
    return text


def extract_and_clean_tokens(dump_path: str | Path) -> Iterator[str]:
    """Usa mwxml para extraer texto, lo limpia y produce un flujo de tokens."""
    dump_path = Path(dump_path)

    print(f"Iniciando el parseo del dump: {dump_path}")

    try:
        # Solución para el AttributeError y manejo del bz2
        with bz2.open(dump_path, "rb") as f:
            # mwxml ahora recibe el objeto de archivo abierto y descomprimido
            for page in mwxml.Dump.from_file(f).pages:
                # Solo procesar artículos (namespace 0) y que tengan contenido
                if page.namespace == 0 and page.redirect is None:
                    # ⬇️ CORRECCIÓN: Iterar sobre page directamente
                    # mwxml.Page es un iterable de revisiones.

                    for revision in page:
                        # Si el dump es pages-articles, solo hay una revisión (la actual)

                        if revision.text:
                            # 1. Limpieza de Wiki Markup
                            clean_text = clean_wiki_markup(revision.text)

                            # 2. Conversión a minúsculas
                            clean_text = normalize_text(clean_text)

                            # 3. Eliminar caracteres que no sean alfabéticos/espacios
                            # Corregido: Se reemplaza por un espacio ' ' (Sintaxis de re.sub)
                            clean_text = re.sub(r"[^a-záéíóúüñ\s]", " ", clean_text)

                            # 4. Tokenización
                            tokens = tokenize(clean_text)

                            # Usar yield para devolver tokens uno por uno
                            yield from tokens
                            break  # Salir del bucle de revisión después de la primera (actual)

        print("Finalizado el procesamiento de artículos.")

    except FileNotFoundError:
        print(f"❌ ERROR: El archivo del dump NO se encontró en: {dump_path}")

    except Exception as e:
        # Captura errores de parsing XML (not well-formed)
        print(f"❌ ERROR CRÍTICO durante el parsing XML: {e}")
        print(
            "El archivo podría estar corrupto o no es un dump válido de artículos. Deteniendo.",
        )


# --- 3. CONTEO DE FRECUENCIAS ---


def count_frequencies(token_generator: Iterator[str]) -> tuple[Counter, Counter]:
    """Cuenta bigramas y unigramas a partir de un flujo de tokens."""
    print("Iniciando el conteo de frecuencias (esto puede tardar horas)...")
    unigram_counts = Counter()
    bigram_counts = Counter()

    # Guardamos el token anterior para formar el bigrama
    prev_token = None

    for total_tokens, token in enumerate(token_generator, start=1):
        # 1. Contar Unigramas
        unigram_counts[token] += 1

        # 2. Contar Bigramas
        if prev_token is not None:
            bigram_counts[(prev_token, token)] += 1

        prev_token = token

        if total_tokens % 1000000 == 0:
            print(f"  -> {total_tokens // 1000000} millones de tokens procesados.")

    return unigram_counts, bigram_counts


# --- 4. CÁLCULO DE PROBABILIDADES Y SUAVIZADO ---


def calculate_probabilities(
    unigram_counts: Counter,
    bigram_counts: Counter,
) -> dict[str, dict[str, float]]:
    """Calcula P(W_n | W_{n-1}) y aplica Suavizado de Laplace."""
    print("Calculando probabilidades de transición...")

    # 1. Calcular el tamaño del vocabulario (V) para el Suavizado de Laplace
    vocab = len(unigram_counts)

    # 2. Estructura final: {word1: {word2: prob, ...}}
    transition_matrix = {}

    # Iterar sobre todos los posibles bigramas
    for (word1, word2), count in bigram_counts.items():
        count_word1 = unigram_counts[word1]

        # Aplicar el Suavizado de Laplace
        probability = (count + 1) / (count_word1 + vocab)

        if word1 not in transition_matrix:
            transition_matrix[word1] = {}

        transition_matrix[word1][word2] = probability

    return transition_matrix


# --- 5. ORQUESTACIÓN Y GUARDADO ---


def main():
    # 1. Pipeline de Extracción y Conteo
    token_stream = extract_and_clean_tokens(DUMP_PATH)

    # Manejar el caso donde el generador no produce tokens (ej. error en el parseo)
    try:
        unigrams, bigrams = count_frequencies(token_stream)
    except Exception:
        # Si el error ocurrió dentro de extract_and_clean_tokens, ya se imprimió un error crítico.
        # Salimos de main.
        return

    if not unigrams:
        print(
            "\n❌ Error: No se pudo extraer texto del dump. Verifique la ruta y el archivo.",
        )
        return

    print(f"\nResumen del Corpus:")
    print(f"  - Vocabulario (Unigramas únicos): {len(unigrams):,}")
    print(f"  - Bigramas únicos: {len(bigrams):,}")

    # 2. Cálculo de la Matriz P
    p_matrix = calculate_probabilities(unigrams, bigrams)

    # 3. Guardado en Disco (UJSON para archivos grandes)
    print(f"Guardando la matriz de {len(p_matrix)} entradas...")

    # Crear el directorio data si no existe
    data_dir.mkdir(parents=True, exist_ok=True)

    try:
        with OUTPUT_FILENAME.open("w", encoding="utf-8") as f:
            # indent=4 para legibilidad; si la matriz es gigante, quítalo
            json.dump(p_matrix, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡Proceso completado! Matriz guardada en: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"Error al guardar el archivo: {e}")


class LanguageModel:
    """
    Carga la matriz P_matrix_transicion.json y expone
    get_transition_log_prob(prev, curr) que devuelve log P(curr | prev).

    Esta es la interfaz que necesita ViterbiDecoder.
    """

    def __init__(
        self,
        matrix_path: Path | str | None = None,
        unk_log_prob: float = -15.0,
    ):
        """
        :param matrix_path: ruta al archivo P_matrix_transicion.json.
                            Si es None, usa OUTPUT_FILENAME definido arriba.
        :param unk_log_prob: log-probabilidad por defecto para bigramas no vistos.
        """
        self.unk_log_prob = unk_log_prob
        self.START_TOKEN = START_TOKEN

        # Usar la ruta por defecto si no recibimos una específica
        if matrix_path is None:
            matrix_path = OUTPUT_FILENAME
        elif isinstance(matrix_path, str):
            matrix_path = Path(matrix_path)

        if not Path(matrix_path).exists():
            raise FileNotFoundError(
                f"No se encontró la matriz de transición en: {matrix_path}",
            )

        # Cargar la matriz de transición generada por main()
        with Path(matrix_path).open("r", encoding="utf-8") as f:
            transition_matrix: dict[str, dict[str, float]] = json.load(f)

        # Pasar a log-probs para trabajar en espacio logarítmico
        # Estructura interna: self.bigram_log_probs[prev][curr] = log P(curr | prev)
        self.bigram_log_probs: dict[str, dict[str, float]] = {}
        vocab = set()

        for prev_word, next_dict in transition_matrix.items():
            prev_word = prev_word.strip().lower()
            inner: dict[str, float] = {}

            for next_word, p in next_dict.items():
                next_word = next_word.strip().lower()

                log_p = self.unk_log_prob if p <= 0.0 else math.log(p)

                inner[next_word] = log_p
                vocab.add(prev_word)
                vocab.add(next_word)

            self.bigram_log_probs[prev_word] = inner

        self.vocab = vocab
        # Distribución inicial aproximada para <START>: uniforme sobre el vocabulario
        if self.vocab:
            self.start_log_prob = -math.log(len(self.vocab))
        else:
            self.start_log_prob = self.unk_log_prob

    def get_transition_log_prob(self, prev_word: str, curr_word: str) -> float:
        """
        Devuelve log P(curr_word | prev_word).

        - Si prev_word == <START>: usamos una distribución inicial uniforme.
        - Si el bigrama existe en la matriz: devolvemos log(p) cargado.
        - Si no existe: devolvemos unk_log_prob (backoff muy bajo).
        """
        prev_word = prev_word.strip().lower()
        curr_word = curr_word.strip().lower()

        # Caso especial: inicio de frase
        if prev_word == self.START_TOKEN:
            return self.start_log_prob

        # Bigrama observado
        if prev_word in self.bigram_log_probs:
            inner = self.bigram_log_probs[prev_word]
            if curr_word in inner:
                return inner[curr_word]

        # Bigrama no visto
        return self.unk_log_prob


if __name__ == "__main__":
    main()
