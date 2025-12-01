import numpy as np
import math
import json
import os 

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


    def get_emission_log_prob(self, dirty_word, intended_word):
        '''
        Retorna log(P(dirty|intended)) basado en la distancia euclidiana de
        teclas
        '''

        if len(dirty_word) != len(intended_word):
            return -100.0

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

        print(self.keyboard_map.keys())


        return log_prob_total

    def get_candidates(self, dirty_word, limit=20):
        '''
        Retorna una lista de palabras reales del diccionario que 
        podrían ser lo que el usuario quiso decir.
        Filtrar por longitud similar o primeras letras.
        '''




        return 0.0


if __name__ == "__main__":
    # Mock de vocabulario
    vocab = ["gato", "pato", "casa", "perro", "gusto"]
    km = KeyboardModel(vocab)
    
    dirty = "gato" # Usuario quiso poner "gato" (la 's' está al lado de la 'a')
    clean = "gsto"
    
    score = km.get_emission_log_prob(dirty, clean)
    print(score)

    '''
    print(f"Input: {dirty}")
    candidates = km.get_candidates(dirty)
    
    for word in candidates:
        score = km.get_emission_log_prob(dirty, word)
        print(f"Candidato: {word} | Score: {score:.4f}")
    '''
    # Deberías ver que 'gato' tiene un score más alto (menos negativo) que 'pato'


