from .language_model import LanguageModel
from .keyboard_model import KeyboardModel
from .viterbi_decoder import ViterbiDecoder
from wordfreq import top_n_list


def main():
    # 1. Inicializar modelos (esto es lo “pesado” una sola vez)
    vocab = top_n_list("es", 20000)
    km = KeyboardModel(vocab)
    lm = LanguageModel()  # usa data/P_matrix_transicion.json

    decoder = ViterbiDecoder(language_model=lm, keyboard_model=km)

    print("=== HMM Smart Keyboard ===")
    print("Escribe una frase con errores y la corregimos.")
    print("Escribe 'salir' para terminar.\n")

    # 2. Loop interactivo
    while True:
        sentence = input("Frase con errores: ").strip()
        if not sentence:
            continue
        if sentence.lower() in {"salir", "exit", "quit"}:
            break

        result = decoder.solve(sentence)

        print("\n--- Resultado ---")
        print("Original:  ", sentence)
        print("Corregida: ", result["corrected_text"])
        print("Score:     ", result["best_score"])

        audit = result["audit_data"]
        print("\nAuditoría (última palabra):")
        print("  Input original:", audit["input_original"])
        print("  Ganador:       ", audit["ganador"])
        print("  Ranking top 5:")
        for item in audit["ranking"]:
            print(
                f"    {item['palabra']:>12} | "
                f"ctx={item['ctx']:.2f} | "
                f"kbd={item['kbd']:.2f} | "
                f"total={item['total']:.2f}"
            )
        print("\n")


if __name__ == "__main__":
    main()
