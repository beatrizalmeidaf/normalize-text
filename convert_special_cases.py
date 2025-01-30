from normalizar_numeros import Extenso
import re
import inflect


def normalize_special_characters(text):
    # Substituir "&" por " e "
    text = re.sub(r'(?<=\S)&(?=\S)', ' e ', text)
    text = re.sub(r'(?<=\s)&(?=\s)', 'e', text)

    # Substituir "+" por " mais " ou "mais"
    text = re.sub(r'(?<=\S)\+(?=\S)', ' mais ', text)
    text = re.sub(r'(?<=\s)\+(?=\s)', 'mais', text)

    # Normalizar valores monetários
    text = normalize_monetary_value(text)

    # Substituir "²" por "ao quadrado"
    text = re.sub(r'\b(\w+?)²\b', lambda m: f"{m.group(1)} ao quadrado", text)

    # Substitui numeros com '²' para "número ao quadrado" 
    text = re.sub(r'(\d+)²', lambda m: f"{m.group(1)} ao quadrado", text)

    # Substituir "§" por "parágrafo"
    text = re.sub(r'§\s*(\d+)', r'parágrafo \1', text)

    # Substituir "π" por "pi"
    text = re.sub(r'(?<=\d)π', ' pi', text)
    text = re.sub(r'(?<=\s)π(?=\s)', 'pi', text)

    # Substituir "€" por "euros"
    text = re.sub(r'(\d+[\d,\.]*)\s*€', r'\1 euros', text)

    # Substituir ordinais
    text = re.sub(r'(\d+)(º|ª)', lambda match: transcribe_ordinal(int(match.group(1)), match.group(2)), text)


    text = normalize_square_units(text)

    return text

def normalize_monetary_value(text):
    # Substituir "R$" seguido de valor com ponto ou vírgula
    text = re.sub(r'R\$\s*(\d+[,\.]?\d*)', lambda m: f"{normalize_number(m.group(1))} reais", text)
    # Substituir "US$" seguido de valor com ponto ou vírgula 
    #text = re.sub(r'US\$\s*(\d+[\w\s]*)', r'\1 dólares', text)
    text = re.sub(r'US\$\s*(\d+[,\.]?\d*)', lambda m: f"{normalize_number(m.group(1))} dólares", text)
    return text

def normalize_number(number_str):
    ex = Extenso()
    parts = number_str.replace('.', ',').split(',')

    if len(parts) == 1:
        return ex.escrever(int(parts[0]))
    elif len(parts) == 2:
        decimal_part = parts[1] if parts[1] else '0'  
        return f"{ex.escrever(int(parts[0]))} vírgula {ex.escrever(int(decimal_part))}"
    else:
        raise ValueError(f"Unexpected format for number: {number_str}")


def normalize_square_units(text):
    # Expressões regulares para capturar números ao quadrado e unidades ao quadrado
    number_square_pattern = re.compile(r'(\d+(\.\d+)?)\s*²')
    unit_square_pattern = re.compile(r'\b(\w+)²\b')

    # Dicionário de unidades ao quadrado e suas normalizações
    units_dict = {
        'm²': 'metro ao quadrado',
        'km²': 'quilômetro ao quadrado',
        'g²': 'grama ao quadrado',
        'kg²': 'quilograma ao quadrado',
        'l²': 'litro ao quadrado',
        'cm²': 'centímetro ao quadrado',
        'mm²': 'milímetro ao quadrado',
        'ml²': 'mililitro ao quadrado',
        't²': 'tonelada ao quadrado'
    }

    # Função para substituir números ao quadrado
    def replace_number_square(match):
        number = match.group(1)
        return f"{number} ao quadrado"

    # Função para substituir unidades ao quadrado
    def replace_unit_square(match):
        unit = match.group(0)  # Inclui a unidade completa com "²"
        return units_dict.get(unit, unit)

    # Primeiro, substituímos os números ao quadrado
    text = number_square_pattern.sub(replace_number_square, text)
    # Depois, substituímos as unidades de medida ao quadrado
    text = unit_square_pattern.sub(replace_unit_square, text)

    return text



def transcribe_ordinal(number, gender):
 
    base_ordinals_m = {
        1: "primeiro", 2: "segundo", 3: "terceiro", 4: "quarto",
        5: "quinto", 6: "sexto", 7: "sétimo", 8: "oitavo", 9: "nono",
        10: "décimo", 20: "vigésimo", 30: "trigésimo", 40: "quadragésimo",
        50: "quinquagésimo", 60: "sexagésimo", 70: "septuagésimo",
        80: "octogésimo", 90: "nonagésimo", 100: "centésimo",
        200: "ducentésimo", 300: "tricentésimo", 400: "quadringentésimo",
        500: "quingentésimo", 600: "sexcentésimo", 700: "septingentésimo",
        800: "octingentésimo", 900: "noningentésimo", 1000: "milésimo"
    }

    base_ordinals_f = {k: v[:-1] + 'a' for k, v in base_ordinals_m.items()}
    base_ordinals_f[1] = "primeira"  

    base_ordinals = base_ordinals_m if gender == 'm' else base_ordinals_f

    def get_ordinal(n):
        if n in base_ordinals:
            return base_ordinals[n]
        elif n < 100:
            tens = n // 10 * 10
            units = n % 10
            return base_ordinals[tens] + ' ' + get_ordinal(units)
        elif n < 1000:
            hundreds = n // 100 * 100
            remainder = n % 100
            if remainder:
                return base_ordinals[hundreds] + ' ' + get_ordinal(remainder)
            else:
                return base_ordinals[hundreds]

    return get_ordinal(number)


class Switcher():
    def __init__(self, text):
        self.text = text
        self.pattern = None
        self.method_name = None

    def switch(self):

         # Milhar com ponto
        chiliad_pattern = re.compile(r'^(\d+)\.(\d{3})$')

        # Horas e minutos
        time_pattern = re.compile(r'^(\d+)[h\:](\d{0,2})(m|min)?$')

        # Quilometros
        kilometers_pattern = re.compile(r'^(\d+)[kK][mM]$')

        # Metros
        meters_pattern = re.compile(r'^(\d+)m$')

        # Milímetros
        millimeters_pattern = re.compile(r'^(\d+)mm$')

        # Porcentagem
        percentage_pattern = re.compile(r'^(\d+)\%$')

        # Valores flutuantes
        float_pattern = re.compile(r'^(\d+)([.,])(\d+)$')

        # Ordinais
        ordinal_pattern = re.compile(r'^(\d+)(º|ª)$')

        # Graus
        degree_pattern = re.compile(r'^(\d+)°$')

        # Tecnologia
        dimension_technology_pattern = re.compile(r'^(\d+)(D|G|g|X)$')

        # Multiplication
        multiplication_pattern = re.compile(r'^(\d+)x(\d+)$')

        # Kilograms
        kilograms_pattern = re.compile(r'^(\d+)[kK][gG]$')

        # Bits
        bits_pattern = re.compile(r'^(\d+)bits$')

        # Numero seguido de letra maiscula
        num_letter_pattern = re.compile(r'^(\d+)([A-Z])$')

        # Números ordinais em inglês
        english_ordinal_pattern = re.compile(r'^(\d+)(st|nd|rd|th)$')

        square_units_pattern = re.compile(r'^(\d+)?(m²|km²)$')

        if chiliad_pattern.match(self.text):
            self.method_name = 'conv_chiliad'
            self.pattern = chiliad_pattern

        elif time_pattern.match(self.text):
            self.method_name = 'conv_time'
            self.pattern = time_pattern

        elif kilometers_pattern.match(self.text):
            self.method_name = 'conv_kilometers'
            self.pattern = kilometers_pattern

        elif meters_pattern.match(self.text):
            self.method_name = 'conv_meters'
            self.pattern = meters_pattern

        elif millimeters_pattern.match(self.text):  # New case for millimeters
            self.method_name = 'conv_millimeters'
            self.pattern = millimeters_pattern

        elif percentage_pattern.match(self.text):
            self.method_name = 'conv_percentage'
            self.pattern = percentage_pattern

        elif float_pattern.match(self.text):
            self.method_name = 'conv_float'
            self.pattern = float_pattern

        elif ordinal_pattern.match(self.text):  # Handling for ordinal numbers
            self.method_name = 'conv_ordinal'
            self.pattern = ordinal_pattern

        elif degree_pattern.match(self.text):
            self.method_name = 'conv_degrees'
            self.pattern = degree_pattern

        elif dimension_technology_pattern.match(self.text):
            self.method_name = 'conv_dimension_technology'
            self.pattern = dimension_technology_pattern

        elif multiplication_pattern.match(self.text):
            self.method_name = 'conv_multiplication'
            self.pattern = multiplication_pattern

        elif kilograms_pattern.match(self.text):
            self.method_name = 'conv_kilograms'
            self.pattern = kilograms_pattern

        elif bits_pattern.match(self.text):
            self.method_name = 'conv_bits'
            self.pattern = bits_pattern

        elif num_letter_pattern.match(self.text):  # Check the new pattern
            self.method_name = 'conv_num_letter'
            self.pattern = num_letter_pattern
            
        elif square_units_pattern.match(self.text):
            self.method_name = 'conv_square_units'
            self.pattern = square_units_pattern

        elif english_ordinal_pattern.match(self.text):
            self.method_name = 'conv_english_ordinal_pattern'
            self.pattern = english_ordinal_pattern

        if self.method_name:

            method = getattr(self, self.method_name, lambda: 'Invalido')

            return method()

        return self.text, False

    def conv_meters(self):
        """
        Converte expressoes de medida para o seu correspondente por extenso

        ----------------------------

        Exemplos: '3m' para 'três metros'
        """

        ex = Extenso()

        conv_meters = self.pattern.findall(self.text)

        return ex.escrever(int(conv_meters[0])) + ' ' + 'metros', True

    def conv_chiliad(self):
        """
        Converte expressoes de milhar para o seu correspondente por extenso

        ----------------------------

        Exemplos: '5.000' para 'cinco mil'
        """

        ex = Extenso()

        conv_num = self.pattern.findall(self.text)

        num = conv_num[0][0]+conv_num[0][1]

        return ex.escrever(int(num)), True

    def conv_time(self):
        """
        Converte expressoes de tempo para o seu correspondente por extenso

        ----------------------------

        Exemplos: '2:15' ou '2h15' para 'duas horas e quinze minutos' ou
        '2h' para 'duas horas'
        """
        ex = Extenso()

        hour_plural = 'horas'
        hour_singular = 'hora'
        minute_plural = 'minutos'
        minute_singular = 'minuto'

        final = ''
        hours = ''
        minutes = ''

        conv_time = self.pattern.findall(self.text)

        hours = int(conv_time[0][0])
        hours = ex.escrever(hours).replace('um', 'uma').replace('dois', 'duas')

        if conv_time[0][1]:
            minutes = int(conv_time[0][1])
            minutes = ex.escrever(minutes)

            if minutes == 'um':
                second_part = minutes + ' ' + minute_singular
            else:
                second_part = minutes + ' ' + minute_plural

        if hours == 'uma':
            first_part = hours + ' ' + hour_singular
        else:
            first_part = hours + ' ' + hour_plural

        if minutes:
            phrase =  first_part + ' e ' + second_part
        else:
            phrase = first_part

        return phrase, True

    def conv_percentage(self):
        """
        Converte expressoes de porcentagem para o seu correspondente por extenso

        ----------------------------

        Exemplos: '2%' para 'dois por cento'
        """

        ex = Extenso()

        num = self.pattern.findall(self.text)

        return ex.escrever(int(num[0])) + ' ' + 'por cento', True

    def conv_float(self):
        # Converte expressões flutuantes
        ex = Extenso()
        broken_values = self.pattern.findall(self.text)
        first_num = ex.escrever(int(broken_values[0][0]))
        second_num = ex.escrever(int(broken_values[0][1]))
        punctuation = 'ponto' if '.' in self.text else 'vírgula'
        return first_num + ' ' + punctuation + ' ' + second_num, True
    
    
    def conv_ordinal(self):
        """
        Converte expressões numéricas ordinais para o seu correspondente por extenso
        Exemplos: '1º' para 'primeiro', '4ª' para 'quarta'
        """
        ex = Extenso()
        match = self.pattern.findall(self.text)
        num = int(match[0][0])
        gender = match[0][1]

        if gender == 'º':  # ordinal masculino
            return transcribe_ordinal(num, 'm'), True
        else:  # ordinal feminino
            return transcribe_ordinal(num, 'f'), True

    def conv_degrees(self):
        """
        Converte expressões de graus para o seu correspondente por extenso

        ----------------------------

        Exemplos: '360°' para 'trezentos e sessenta graus'
        """
        ex = Extenso()
        degrees = self.pattern.findall(self.text)

        return ex.escrever(int(degrees[0])) + ' graus', True

    def conv_dimension_technology(self):
        """
        Converts expressions with numbers followed by 'D' or 'G' into their full-word equivalents with the letter retained.

        Examples: '2D' to 'dois D', '5G' to 'cinco G'
        """

        ex = Extenso()

        matched = self.pattern.findall(self.text)
        number = int(matched[0][0])
        letter = matched[0][1]

        number_in_full = ex.escrever(number)

        return number_in_full + ' ' + letter, True

    def conv_multiplication(self):
        """
        Converts multiplication expressions into their word form

        ----------------------------

        Examples: '1x1' to 'um por um', '7x8' to 'sete por oito'
        """
        ex = Extenso()

        # Find the numbers in the expression
        nums = self.pattern.findall(self.text)

        # Convert each number to its word form
        first_num = ex.escrever(int(nums[0][0]))
        second_num = ex.escrever(int(nums[0][1]))

        # Combine with 'por' in between
        return first_num + ' por ' + second_num, True

    def conv_kilograms(self):
        """
        Converte expressões de quilogramas para o seu correspondente por extenso
        Exemplos: '2kg' para 'dois quilogramas'
        """
        ex = Extenso()
        num = self.pattern.findall(self.text)
        return ex.escrever(int(num[0])) + ' quilogramas', True

    def conv_bits(self):
        """
        Converte expressões de dados digitais para o seu correspondente por extenso

        Exemplos: '8bits' para 'oito bits'
        """
        ex = Extenso()

        match = self.pattern.findall(self.text)
        number = int(match[0])  # Extract the number from the pattern
        return ex.escrever(number) + ' bits', True

    def conv_num_letter(self):
        """
        Converts an expression of a number followed by a capital letter
        to its corresponding words.

        Example: '4A' to 'quatro A'
        """
        ex = Extenso()
        match = self.pattern.findall(self.text)
        number = int(match[0][0])
        letter = match[0][1]
        return ex.escrever(number) + ' ' + letter, True

    def conv_millimeters(self):
        """
        Converte expressões de milímetros para o seu correspondente por extenso

        ----------------------------

        Exemplos: '9mm' para 'nove milímetros'
        """
        ex = Extenso()
        mm = self.pattern.findall(self.text)
        if mm:
            number = int(mm[0])
            return ex.escrever(number) + ' milímetros', True

    def conv_kilometers(self):
        """
        Converte expressões de quilômetros para o seu correspondente por extenso

        ----------------------------

        Exemplos: '5km' para 'cinco quilômetros'
        """
        ex = Extenso()
        km = self.pattern.findall(self.text)
        if km:
            number = int(km[0])
            return ex.escrever(number) + ' quilômetros', True

    def conv_english_ordinal_pattern(self):
        """
        Converte expressões numéricas ordinais para o seu correspondente por extenso em inglês

        ----------------------------

        Exemplos: '21st' para 'twenty-first'
        """
        p = inflect.engine()
        conv_num = self.pattern.findall(self.text)
        number = int(conv_num[0][0])
        ordinal_word = p.number_to_words(number)
        return ordinal_word, True
    
    def conv_square_units(self):
        # Converte medidas ao quadrado
        ex = Extenso()
        match = self.pattern.findall(self.text)
        number = match[0][0] if match[0][0] else 'um'
        unit = match[0][1]
        number_in_full = ex.escrever(int(number)) if number.isdigit() else number
        unit_in_full = 'metros quadrados' if unit == 'm²' else 'quilômetros quadrados'
        return f"{number_in_full} {unit_in_full}", True