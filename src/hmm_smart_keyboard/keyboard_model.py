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

        self.buckets = {}
        for word in self.vocabulary:
            if not word: continue

            key = (word[0].lower(), len(word))
            if key not in self.buckets:
                self.buckets[key] = []
            self.buckets[key].append(word)

    def get_emission_log_prob(self, dirty_word, intended_word):
        '''
        Retorna log(P(dirty|intended)) basado en la distancia euclidiana de
        teclas
        '''


        log_prob_total = 0.0

        for dirty_char, intended_char in zip(dirty_word, intended_word):

            c1 = dirty_char.lower()
            c2 = intended_char.lower()

            if dirty_char not in self.keyboard_map.keys():
                return 2.0

            c1_coords = self.keyboard_map[c1]
            c2_coords = self.keyboard_map[c2]

            x1, y1 = c1_coords['x'], c1_coords['y']
            x2, y2 = c2_coords['x'], c2_coords['y']


            dist = distance.euclidean_distance([x1, y1], [x2, y2])

            char_log_prob = - (dist ** 2)/(2 * self.variance) #gaussian error
            log_prob_total += char_log_prob

        return log_prob_total

    def get_candidates(self, dirty_word, limit=20):
        '''
        Retorna una lista de palabras reales del diccionario que 
        podrían ser lo que el usuario quiso decir.
        Filtrar por longitud similar o primeras letras.
        '''
        if not dirty_word: return []
        
        dirty_word = dirty_word.lower()
        first_char = dirty_word[0]
        length = len(dirty_word)
        
        candidates = []
        
        target_keys = [
            (first_char, length),     # Misma longitud
            (first_char, length + 1), # Se comió una letra
            (first_char, length - 1)  # Puso una letra de más
        ]
        
        for key in target_keys:
            if key in self.buckets:
                candidates.extend(self.buckets[key])

        return candidates


if __name__ == "__main__":
    vocab = top_n_list("es", 20000)
    km = KeyboardModel(vocab)
    
    dirty = "givson" # Usuario quiso poner "gato" (la 's' está al lado de la 'a')

    print(f"Input: {dirty}")
    candidates = km.get_candidates(dirty)
    
    top_score = -100.0
    top_candidate = "no candidate"
    
    for word in candidates:
        score = km.get_emission_log_prob(dirty, word)
        print(f"Candidato: {word} | Score: {score:.4f}")
        if top_score < score:
            top_score = score
            top_candidate = word

    print(f"Candidato elegido: {top_candidate} | Score {top_score:.4f}" )
            
    # Deberías ver que 'gato' tiene un score más alto (menos negativo) que 'pato'


