import mwxml
import re
import ujson as json
from collections import Counter
from typing import Iterator, Tuple, Dict
from utils.text_processing import tokenize, normalize_text, remove_punctuation
import os 
import bz2 


# --- 1. CONFIGURACIÓN Y ARCHIVOS ---

# Solución para rutas absolutas: Garantiza encontrar el dump sin importar el CWD
script_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
DUMP_PATH = os.path.join(BASE_DIR, 'eswiki-latest-pages-articles-multistream.xml.bz2')
OUTPUT_FILENAME = "P_matrix_transicion.json"


# --- 2. PRE-PROCESAMIENTO Y LIMPIEZA ---

def clean_wiki_markup(text: str) -> str:
    """Elimina rudimentariamente el wiki-markup de un texto."""
    # Eliminar llamadas a plantillas (ej: {{cita web|...}})
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    # Eliminar enlaces internos con formato (ej: [[inteligencia artificial|IA]])
    text = re.sub(r'\[\[[^|]*\|', '[[', text) 
    # Eliminar texto entre corchetes (a menudo referencias)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text) 
    # Eliminar tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    return text

def extract_and_clean_tokens(dump_path: str) -> Iterator[str]:
    """
    Usa mwxml para extraer texto, lo limpia y produce un flujo de tokens.
    """
    print(f"Iniciando el parseo del dump: {dump_path}")
    
    try:
        # Solución para el AttributeError y manejo del bz2
        with bz2.open(dump_path, 'rb') as f:
            # mwxml ahora recibe el objeto de archivo abierto y descomprimido
            for page in mwxml.Dump.from_file(f): 
                
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
                            clean_text = re.sub(r'[^a-záéíóúüñ\s]', ' ', clean_text)
                            
                            # 4. Tokenización
                            tokens = tokenize(clean_text)
                            
                            # Usar yield para devolver tokens uno por uno
                            yield from tokens
                            break # Salir del bucle de revisión después de la primera (actual)

        print("Finalizado el procesamiento de artículos.")
    
    except FileNotFoundError:
        print(f"❌ ERROR: El archivo del dump NO se encontró en: {dump_path}")
    
    except Exception as e:
        # Captura errores de parsing XML (not well-formed)
        print(f"❌ ERROR CRÍTICO durante el parsing XML: {e}")
        print("El archivo podría estar corrupto o no es un dump válido de artículos. Deteniendo.")
        
# --- 3. CONTEO DE FRECUENCIAS ---

def count_frequencies(token_generator: Iterator[str]) -> Tuple[Counter, Counter]:
    """
    Cuenta bigramas y unigramas a partir de un flujo de tokens.
    """
    print("Iniciando el conteo de frecuencias (esto puede tardar horas)...")
    unigram_counts = Counter()
    bigram_counts = Counter()
    
    # Guardamos el token anterior para formar el bigrama
    prev_token = None
    total_tokens = 0
    
    for token in token_generator:
        # 1. Contar Unigramas
        unigram_counts[token] += 1
        
        # 2. Contar Bigramas
        if prev_token is not None:
            bigram_counts[(prev_token, token)] += 1
        
        prev_token = token
        total_tokens += 1
        
        if total_tokens % 1000000 == 0:
            print(f"  -> {total_tokens // 1000000} millones de tokens procesados.")
            
    return unigram_counts, bigram_counts

# --- 4. CÁLCULO DE PROBABILIDADES Y SUAVIZADO ---

def calculate_probabilities(unigram_counts: Counter, bigram_counts: Counter) -> Dict[str, Dict[str, float]]:
    """
    Calcula P(W_n | W_{n-1}) y aplica Suavizado de Laplace.
    """
    print("Calculando probabilidades de transición...")
    
    # 1. Calcular el tamaño del vocabulario (V) para el Suavizado de Laplace
    V = len(unigram_counts)
    
    # 2. Estructura final: {word1: {word2: prob, ...}}
    transition_matrix = {}
    
    # Iterar sobre todos los posibles bigramas
    for (word1, word2), count in bigram_counts.items():
        count_word1 = unigram_counts[word1]
        
        # Aplicar el Suavizado de Laplace 
        probability = (count + 1) / (count_word1 + V)
        
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
        print("\n❌ Error: No se pudo extraer texto del dump. Verifique la ruta y el archivo.")
        return

    print(f"\nResumen del Corpus:")
    print(f"  - Vocabulario (Unigramas únicos): {len(unigrams):,}")
    print(f"  - Bigramas únicos: {len(bigrams):,}")

    # 2. Cálculo de la Matriz P
    P_matrix = calculate_probabilities(unigrams, bigrams)

    # 3. Guardado en Disco (UJSON para archivos grandes)
    print(f"Guardando la matriz de {len(P_matrix)} entradas...")
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            # indent=4 para legibilidad; si la matriz es gigante, quítalo
            json.dump(P_matrix, f, ensure_ascii=False, indent=4) 
        print(f"✅ ¡Proceso completado! Matriz guardada en: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"Error al guardar el archivo: {e}")

if __name__ == "__main__":
    main()