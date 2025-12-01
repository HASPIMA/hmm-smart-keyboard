from wordfreq import top_n_list

from hmm_smart_keyboard.keyboard_model import KeyboardModel
from hmm_smart_keyboard.language_model import LanguageModel
from hmm_smart_keyboard.viterbi_decoder import ViterbiDecoder


def main() -> None:
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
    print("Auditoría:", result["audit_data"])

if __name__ == "__main__":
    main()
