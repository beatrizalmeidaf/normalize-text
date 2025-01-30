# Normalização de Texto para Transcrições

Esse repositório contém um script Python para normalização de transcrições em português. O script processa transcrições do Whisper, normaliza números, unidades de medida e caracteres especiais, além de realizar várias operações de limpeza de texto.

## Funcionalidades

- Normaliza números para sua forma escrita em português
- Converte unidades abreviadas (km, ml, kg, etc.) para sua forma escrita completa
- Trata caracteres especiais e problemas de codificação
- Remove transcrições com caracteres inválidos
- Filtra transcrições com menos de 3 palavras
- Processa arquivos CSV usando pipe (|) como delimitador

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/beatrizalmeidaf/normalize-text.git
cd normalize-text
```

2. Instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

## Como Usar

Execute o script pela linha de comando especificando os caminhos dos arquivos de entrada e saída:

```bash
python normalizar_coluna.py -i arquivo_entrada.csv -o arquivo_saida.csv
```

Ou usando os nomes completos dos argumentos:

```bash
python normalizar_coluna.py --input arquivo_entrada.csv --output arquivo_saida.csv
```

### Requisitos do Arquivo de Entrada

- O arquivo de entrada deve ser um CSV com pipe (|) como delimitador
- Deve conter uma coluna 'transcription-whisper' com as transcrições com Whisper
- O arquivo deve estar codificado em UTF-8

### Saída

O script criará um novo arquivo CSV contendo:
- Todas as colunas originais do arquivo de entrada
- Uma nova coluna 'whisper_normalizado' com o texto normalizado
- Linhas com caracteres inválidos ou menos de 3 palavras serão removidas



