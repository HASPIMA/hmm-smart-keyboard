import math
import json
import os

import numpy as np
from wordfreq import top_n_list
from utils import distance


class KeyboardModel:

    def __init__(self, vocab):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = dir_path + "/data/keyboard_es.json"

        self.vocabulary = set(vocab)

        with open(file_path, "r", encoding="utf-8") as f:
            self.keyboard_map = json.load(f)

        self.sigma = 2
        self.variance = self.sigma ** 2

        # Buckets por (primera_letra, longitud)
        self.buckets = {}
        for word in self.vocabulary:
            if not word:
                continue
            key = (word[0].lower(), len(word))
            if key not in self.buckets:
                self.buckets[key] = []
            self.buckets[key].append(word)

    def get_emission_log_prob(self, dirty_word, intended_word):
        """
        Retorna log P(dirty | intended) basado en la distancia euclidiana
        entre teclas. Valores cercanos a 0 => error muy plausible.
        Valores muy negativos => error raro.
        """
        if not dirty_word or not intended_word:
            return -1e9  # casi imposible

        log_prob_total = 0.0

        for dirty_char, intended_char in zip(dirty_word, intended_word):
            c1 = dirty_char.lower()
            c2 = intended_char.lower()

            # Si no conocemos alguno de los caracteres, penalizamos fuerte
            if c1 not in self.keyboard_map or c2 not in self.keyboard_map:
                return -50.0

            c1_coords = self.keyboard_map[c1]
            c2_coords = self.keyboard_map[c2]

            x1, y1 = c1_coords["x"], c1_coords["y"]
            x2, y2 = c2_coords["x"], c2_coords["y"]

            dist = distance.euclidean_distance([x1, y1], [x2, y2])

            # Error gaussiano (sin constante de normalización, para ranking basta)
            char_log_prob = - (dist ** 2) / (2 * self.variance)
            log_prob_total += char_log_prob

        # Penalizar diferencia de longitudes (inserciones/borrados)
        len_diff = abs(len(dirty_word) - len(intended_word))
        if len_diff > 0:
            log_prob_total -= 2.0 * len_diff

        return log_prob_total

    def get_candidates(self, dirty_word, limit=20):
        """
        Retorna una lista de palabras reales del diccionario que podrían ser
        lo que el usuario quiso decir.

        - Filtra por longitud similar (L, L+1, L-1) y misma primera letra.
        - Usa get_emission_log_prob para puntuar y se queda con las top `limit`.
        """
        if not dirty_word:
            return []

        dirty_word = dirty_word.lower()
        first_char = dirty_word[0]
        length = len(dirty_word)

        candidates_raw = []

        target_keys = [
            (first_char, length),      # Misma longitud
            (first_char, length + 1),  # Se comió una letra
            (first_char, length - 1),  # Puso una letra de más
        ]

        for key in target_keys:
            if key in self.buckets:
                candidates_raw.extend(self.buckets[key])

        # Quitar duplicados
        candidates_raw = list(set(candidates_raw))

        # Si no hay nada, devolvemos al menos la palabra original
        if not candidates_raw:
            return [dirty_word]

        # Puntuar con el modelo de teclado
        scored = []
        for w in candidates_raw:
            score = self.get_emission_log_prob(dirty_word, w)
            scored.append((w, score))

        # Ordenar por score (de mayor a menor: menos negativo => más probable)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Devolver solo las palabras, respetando el límite
        top_words = [w for (w, _) in scored[:limit]]
        return top_words


if __name__ == "__main__":
    vocab = top_n_list("es", 20000)
    km = KeyboardModel(vocab)

    dirty = "givson"

    print(f"Input: {dirty}")
    candidates = km.get_candidates(dirty, limit=10)

    top_score = -1e9
    top_candidate = None

    for word in candidates:
        score = km.get_emission_log_prob(dirty, word)
        print(f"Candidato: {word} | Score: {score:.4f}")
        if score > top_score:
            top_score = score
            top_candidate = word

    print(f"Candidato elegido: {top_candidate} | Score {top_score:.4f}")
