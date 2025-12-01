from hmm_smart_keyboard.utils import normalize_text


def main() -> None:
    print('Hello from hmm-smart-keyboard!')
    text = input('Text to normalize: ')
    print(normalize_text(text))
