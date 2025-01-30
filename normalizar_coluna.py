import os
import argparse
from typing import List
import re 
from typing import Tuple
import pandas as pd
from tqdm import tqdm

from normalizar_numeros import Extenso
from convert_special_cases import Switcher, normalize_special_characters, transcribe_ordinal

import unicodedata


punctuation_pattern = ['…', '...', '"', "'", ';', ',', '.', '!', '?', ')', '(', '-', '–', '—', '“', '”', '‘', '’', '´', '¨', '˜', '´', '´´', '``', '´´´', '´´´´', '´´´´´', '´´´´´´', '´´´´´´´', '´´´´´´´´', '´´´´´´´´´']

def parse_arguments():
    """
    Parse command line arguments for input and output file paths
    """
    parser = argparse.ArgumentParser(description='Text normalization script for podcast transcriptions')
    parser.add_argument('--input', '-i', type=str, required=True,
                      help='Input CSV file path containing podcast transcriptions')
    parser.add_argument('--output', '-o', type=str, required=True,
                      help='Output path for the normalized CSV file')
    return parser.parse_args()

def normalize_text(text):
    """
    Função para normalizar caracteres especiais e acentuados em texto.
    """
    normalized_text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_text


def correct_encoding_issues(text):
    """
    Corrige problemas de encoding, como substituição de caracteres mal codificados.
    """
    text = text.replace('Ã©', 'é').replace('Ã¡', 'á').replace('Ãª', 'ê')
    text = text.replace('Ã£', 'ã').replace('Ã³', 'ó').replace('Ã', 'à')
    text = text.replace('Ã§', 'ç').replace('Ãº', 'ú').replace('Ãµ', 'õ')
    text = text.replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã¼', 'ü')
    text = text.replace('Ã¢', 'â').replace('Ã®', 'î').replace('Ã´', 'ô')
    text = text.replace('Â', '').replace('â', 'a')  
    return text

def normalize_units(text):
    units_map = {
        r'\bkm\b': 'quilômetros', 
        r'\bml\b': 'mililitros', 
        r'\bkg\b': 'quilogramas',
        r'\bcm\b': 'centímetros', 
        r'\bmm\b': 'milímetros', 
        r'\bºC\b': 'graus Celsius',
        r'\bkm/h\b': 'quilômetros por hora', 
        r'\bm/s\b': 'metros por segundo'
    }
    
    for unit_pattern, full_unit in units_map.items():
        text = re.sub(unit_pattern, full_unit, text)
    
    return text

def treat_specific_cases(text):
    """
    Função baseada e adaptada de normalizar números
    Converte casos específicos, incluindo a normalização de números e unidades de medida.
    """
   
    text = normalize_special_characters(text)
    
    
    punctuation = ['…', '...', '"', "'", ';', ',', '.', '!', '?', ')', '(', '-', '_', '$']

    past_word = []
    conv_word = []

    ex = Extenso()
    had_changed = False
    numbers_list = dict()

    for word in text.split(' '):
        for p in punctuation:
            word = word.replace(p, '')
        if word.isdigit():
            had_changed = True
            try:
                if int(word) <= ex._numero_maximo:
                    numbers_list[word] = ex.escrever(int(word))
                else:
                    print(f"Skipping large number: {word}")
            except ValueError:
                continue

        else:
            for i in range(2):
                for p in punctuation:
                    word = word.lstrip(p)
                    word = word.rstrip(p)
            if word and word[0].isdigit():
                switch = Switcher(word)
                new_word, modified = switch.switch()
                if new_word is not None:
                    new_word = ' '.join(new_word.split())
                    if modified:
                        past_word.append(word)
                        conv_word.append(new_word)

    if had_changed:
        for number, string_number in numbers_list.items():
            text = text.replace(number, string_number.strip())

    if past_word and conv_word:
        for past, conv in zip(past_word, conv_word):
            text = text.replace(past, conv)
    
    text = normalize_units(text)

    return text

def get_words(texts: List[str]) -> List[str]:
    """
    Funcao baseada e adaptada de normalizar números

    Separa as palavras de um texto e as retorna em uma lista
    """

    new_texts = []
    for text in tqdm(texts):
        new_texts.append(treat_specific_cases(text))

    return new_texts

def main():
   
    args = parse_arguments()
    
    punctuation_pattern = ['…', '...', '"', "'", ';', ',', ':', '.', '!', '?', ')', '(', '-', '–', '—', '"', '"', ''', ''', '´', '¨', '˜', '´', '´´', '`', '´´´', '´´´´', '´´´´´', '´´´´´´', '´´´´´´´', '´´´´´´´´', '´´´´´´´´´']
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
             "\u00a1\u00a3\u00b7\u00b8\u00c0\u00c1\u00c2\u00c3\u00c4\u00c5\u00c7" \
             "\u00c8\u00c9\u00ca\u00cb\u00cc\u00cd\u00ce\u00cf\u00d1\u00d2\u00d3" \
             "\u00d4\u00d5\u00d6\u00d9\u00da\u00db\u00dc\u00df\u00e0\u00e1\u00e2" \
             "\u00e3\u00e4\u00e5\u00e7\u00e8\u00e9\u00ea\u00eb\u00ec\u00ed\u00ee" \
             "\u00ef\u00f1\u00f2\u00f3\u00f4\u00f5\u00f6\u00f9\u00fa\u00fb\u00fc" \
             "\u0101\u0104\u0105\u0106\u0107\u010b\u0119\u0141\u0142\u0143\u0144" \
             "\u0152\u0153\u015a\u015b\u0161\u0178\u0179\u017a\u017b\u017c\u020e" \
             "\u04e7\u05c2\u1b20&+*§π€$²" 

    character_list = [char for char in characters]

    
    try:
        df = pd.read_csv(args.input, sep="|", encoding="UTF-8")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
    except Exception as e:
        print(f"Erro ao ler o arquivo de entrada: {e}")
        return

    
    if 'transcription-whisper' not in df.columns:
        print("Erro: Coluna 'transcription-whisper' não encontrada no arquivo CSV.")
        return

    texts = df["transcription-whisper"].tolist()

    counter = 0
    for idx, text in tqdm(enumerate(texts), total=len(texts), desc="Verificando arquivos .wav"):
        if ".wav" in text:
            print(f"idx: {idx} | text: {text}")
            counter += 1
            break
    print(f"Counter: {counter}")

    # Normalizar sentenças
    whisper_normalized = get_words(texts)
    df['whisper_normalizado'] = whisper_normalized

    if len(whisper_normalized) != len(texts):
        print("Erro: Inconsistência no comprimento dos dados normalizados.")
        return

    compromised_rows = []
    for idx, row in tqdm(enumerate(whisper_normalized), total=len(whisper_normalized), desc="Verificando caracteres inválidos"):
        for word in row.split(' '):
            for letter in word:
                if letter not in character_list and letter not in punctuation_pattern:
                    compromised_rows.append(idx)
    print(f"Linhas comprometidas: {len(list(set(compromised_rows)))}")

    df_cleaned = df.drop(index=list(set(compromised_rows)))

    few_words = []
    for idx, row in tqdm(enumerate(df_cleaned["whisper_normalizado"]), total=len(df_cleaned), desc="Verificando quantidade de palavras"):
        if len(row.split(' ')) < 3:
            few_words.append(idx)
    print(f"Linhas com poucas palavras: {len(list(set(few_words)))}")


    df_cleaned = df_cleaned.drop(index=list(set(few_words)), errors='ignore')

    try:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df_cleaned.to_csv(args.output, sep="|", index=False)
        print(f"Arquivo normalizado salvo em: {args.output}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de saída: {e}")

if __name__ == "__main__":
    main()

 