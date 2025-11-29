import numpy as np
import math

from .utils import distance



class KeyboardModel:

    def __init__():
        with open("data/keyboard_es.json", r, encoding='utf-8') as f:
            self.keyboard_map = json.load(f)




    def get_emission_log_prob(self, char_pressed, char_intended):
        '''
        Retorna log(P(dirty|intendend)) basado en la distancia euclidiana de
        teclas
        '''
        clean_char_pressed = char_pressed.lower()
        clean_char_intended = char_intended.lower()

        d_chars = distance.euclidean_distance(clean_char_pressed, clean_char_intended)
        rate = 0.25
        exp_prob = (rate * np.e) ** (-rate * d_chars)

        return np.log(exp_prob)

    def get_candidates(self, dirty_word, limit=5):
        '''
        Retorna una lista de palabras reales del diccionario que 
        podrían ser lo que el usuario quiso decir.
        Filtrar por longitud similar o primeras letras.
        '''
        

        return

