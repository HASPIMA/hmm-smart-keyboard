import math

from hmm_smart_keyboard.constants import START_TOKEN


class ViterbiDecoder:
    def __init__(self, language_model, keyboard_model):
        self.lm = language_model
        self.km = keyboard_model

        # Token especial para inicio de frase
        self.START_TOKEN = START_TOKEN

        # Hiperparámetro: Balance entre contexto y teclado
        # Si alpha=1.0, ambos pesan igual
        # Si alpha=2.0, el contexto pesa el doble
        self.alpha = 1.0  # Peso del Language Model
        self.beta = 2.0   # Peso del Keyboard Model

    def solve(self, sentence_dirty):
        """
        Ejecuta el algoritmo de Viterbi para encontrar la mejor corrección.

        :param sentence_dirty: String con errores, ej: "el gsto come"
        :return: Dict con texto corregido y datos de auditoría
        """
        words = sentence_dirty.strip().lower().split()

        if not words:
            return {"corrected_text": "", "audit_data": []}

        # Caso especial: Una sola palabra
        if len(words) == 1:
            return self._solve_single_word(words[0])

        # PASO 1: Preparar estructuras de Viterbi
        # viterbi[t][word] = (score, backpointer)
        # t = índice de tiempo (posición en la frase)
        # word = candidato en ese paso
        # score = log-probabilidad acumulada hasta ese punto
        # backpointer = palabra del paso anterior que llevó a este camino

        viterbi = [{}]  # Lista de diccionarios

        # PASO 2: Inicialización (t=0, primera palabra)
        first_word_dirty = words[0]
        first_candidates = self.km.get_candidates(first_word_dirty)

        for candidate in first_candidates:
            # Transición: desde START hacia la primera palabra

            # Emisión: ¿Qué tan probable es que escribiera esto?
            emission = self.km.get_emission_log_prob(first_word_dirty, candidate)

            # Score combinado (ponderado)
            score = self.beta * emission

            viterbi[0][candidate] = (score, self.START_TOKEN)

        # PASO 3: Recursión (resto de las palabras)
        for t in range(1, len(words)):
            viterbi.append({})
            current_word_dirty = words[t]
            current_candidates = self.km.get_candidates(current_word_dirty)

            for current_candidate in current_candidates:
                # Calcular emisión para esta palabra
                emission = self.km.get_emission_log_prob(
                    current_word_dirty,
                    current_candidate,
                )

                # Encontrar el mejor camino previo
                max_score = -math.inf
                best_prev = None

                # Iteramos sobre TODOS los candidatos del paso anterior
                for prev_candidate in viterbi[t-1]:
                    prev_score, _ = viterbi[t-1][prev_candidate]

                    # Transición: ¿Qué tan común es esta secuencia?
                    transition = self.lm.get_transition_log_prob(
                        prev_candidate,
                        current_candidate,
                    )

                    # Score acumulado hasta este punto
                    total_score = prev_score + (self.alpha * transition) + (self.beta * emission)

                    # ¿Es este el mejor camino hasta ahora?
                    if total_score > max_score:
                        max_score = total_score
                        best_prev = prev_candidate

                # Guardamos el mejor resultado
                viterbi[t][current_candidate] = (max_score, best_prev)

        # PASO 4: Backtracking - Reconstruir el camino ganador
        # Encontramos el estado final con mayor score
        last_step = viterbi[-1]
        best_final_word = max(last_step, key=lambda w: last_step[w][0])
        best_score = last_step[best_final_word][0]

        # Reconstruimos el camino hacia atrás
        corrected_words = [best_final_word]
        backpointer = last_step[best_final_word][1]

        for t in range(len(words) - 2, -1, -1):
            corrected_words.insert(0, backpointer)
            backpointer = viterbi[t][backpointer][1]

        # PASO 5: Generar datos de auditoría para la UI
        audit_data = self._generate_audit_data(words, viterbi, corrected_words)

        return {
            "corrected_text": " ".join(corrected_words),
            "best_score": best_score,
            "audit_data": audit_data,
        }

    def _solve_single_word(self, word_dirty):
        """Caso especial optimizado para una sola palabra."""
        candidates = self.km.get_candidates(word_dirty)

        best_word = word_dirty
        best_score = -math.inf
        ranking = []

        for candidate in candidates:
            emission = self.km.get_emission_log_prob(word_dirty, candidate)
            transition = self.lm.get_transition_log_prob(self.START_TOKEN, candidate)
            total = (self.alpha * transition) + (self.beta * emission)

            ranking.append({
                "palabra": candidate,
                "ctx": float(transition),
                "kbd": float(emission),
                "total": float(total),
            })


            if total > best_score:
                best_score = total
                best_word = candidate

        # Ordenar por score total descendente
        ranking.sort(key=lambda x: x["total"], reverse=True)

        return {
            "corrected_text": best_word,
            "best_score": best_score,
            "audit_data": {
                "input_original": word_dirty,
                "ganador": best_word,
                "ranking": ranking[:5],  # Top 5
            },
        }

    def _generate_audit_data(self, dirty_words, viterbi, corrected_words):
        """
        Genera los datos para la tabla de auditoría de la UI.
        Ahora devuelve una entrada por cada palabra de la frase, con su ranking.
        """
        audit_per_word = []

        for t in range(len(dirty_words)):
            dirty = dirty_words[t]
            corrected = corrected_words[t]
            step = viterbi[t]
            prev_word = corrected_words[t - 1] if t > 0 else self.START_TOKEN

            ranking = []
            for candidate, (score_total, _) in step.items():
                emission = self.km.get_emission_log_prob(dirty, candidate)
                transition = self.lm.get_transition_log_prob(prev_word, candidate)

                ranking.append({
                    "palabra": candidate,
                    "ctx": float(round(transition, 2)),
                    "kbd": float(round(emission, 2)),
                    "total": float(round(score_total, 2)),
                })

            ranking.sort(key=lambda x: x["total"], reverse=True)

            audit_per_word.append({
                "index": t,
                "input_original": dirty,
                "ganador": corrected,
                "ranking": ranking[:5],  # top 5 por palabra
            })

        return audit_per_word


# --- PRUEBA UNITARIA (Equipo B debe correr esto) ---
if __name__ == "__main__":
    # Mock simple para testing sin depender de A y C
    class MockLM:
        def get_transition_log_prob(self, prev, curr):
            # Simulamos que "el gato" es común, "el pato" menos
            if prev == "<START>" and curr == "el":
                return -0.1
            if prev == "el" and curr == "gato":
                return -0.5
            if prev == "el" and curr == "pato":
                return -3.0
            return -10.0

    class MockKM:
        def get_candidates(self, word):
            if word == "dl":
                return ["el", "al"]
            if word == "gato":
                return ["gato", "pato"]
            return [word]

        def get_emission_log_prob(self, dirty, intended):
            if dirty == intended:
                return 0.0
            if dirty == "dl" and intended == "el":
                return -1.0  # Cerca en el teclado
            if dirty == "dl" and intended == "al":
                return -2.0  # Más lejos
            return -5.0

    lm = MockLM()
    km = MockKM()
    decoder = ViterbiDecoder(lm, km)

    result = decoder.solve("dl gato")
    print("=== RESULTADO ===")
    print("Texto original: dl gato")
    print(f"Corrección: {result['corrected_text']}")
    print(f"Score: {result['best_score']}")
    print(f"Auditoría: {result['audit_data']}")
