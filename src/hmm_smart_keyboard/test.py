from .language_model import LanguageModel
from .keyboard_model import KeyboardModel
from .viterbi_decoder import ViterbiDecoder
from wordfreq import top_n_list

if __name__ == "__main__":
    vocab = top_n_list("es", 20000)
    km = KeyboardModel(vocab)
    lm = LanguageModel()  # lee data/P_matrix_transicion.json

    decoder = ViterbiDecoder(language_model=lm, keyboard_model=km)

    frase_sucia = "la imqgen de la bqndera"
    result = decoder.solve(frase_sucia)

    print("Original: ", frase_sucia)
    print("Corregido:", result["corrected_text"])
    print("Score:    ", result["best_score"])
    print("Auditoría:", result["audit_data"])
