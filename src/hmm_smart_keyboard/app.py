from wordfreq import top_n_list

from hmm_smart_keyboard.keyboard_model import KeyboardModel
from hmm_smart_keyboard.language_model import LanguageModel
from hmm_smart_keyboard.viterbi_decoder import ViterbiDecoder


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

        # Compatibilidad: `audit` puede ser un dict (caso single-word)
        # o una lista con una entrada por palabra (nuevo comportamiento).
        if isinstance(audit, list):
            print("\nAuditoría (por palabra):")
            for entry in audit:
                idx = entry.get("index")
                inp = entry.get("input_original", "")
                winner = entry.get("ganador", "")

                header = f" Palabra {idx}: input='{inp}' ganador='{winner}'"
                print(header)
                print("  Ranking top 5:")
                for item in entry.get("ranking", []):
                    print(
                        f"    {item.get('palabra',''):>12} | "
                        f"ctx={item.get('ctx',0.0):.2f} | "
                        f"kbd={item.get('kbd',0.0):.2f} | "
                        f"total={item.get('total',0.0):.2f}",
                    )
                print()
        else:
            # Forma antigua (dict con un solo resumen)
            print("\nAuditoría (última palabra):")
            print("  Input original:", audit.get("input_original"))
            print("  Ganador:       ", audit.get("ganador"))
            print("  Ranking top 5:")
            for item in audit.get("ranking", []):
                print(
                    f"    {item.get('palabra',''):>12} | "
                    f"ctx={item.get('ctx',0.0):.2f} | "
                    f"kbd={item.get('kbd',0.0):.2f} | "
                    f"total={item.get('total',0.0):.2f}",
                )
            print("\n")


if __name__ == "__main__":
    main()
