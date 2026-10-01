import json
from vosk import KaldiRecognizer, Model, SetLogLevel

# Silencia logs de inicialização do Kaldi e mantém apenas avisos de vocabulário
SetLogLevel(0)
model = Model("vosk-model-small-pt-0.3")

# Lista de palavras individuais para checagem rápida
PALAVRAS_INDIVIDUAIS = [
    # Da sua seleção:
    "comando",
    "de",
    "voz",
    "protocolo",
    "ouvir"
]

# Frases completas que combinam com a Mecha Yuka
FRASES_CANDIDATAS = [
    "comando de voz",
    "protocolo ouvir",
    "modo de escuta",
    "ouvir comando",
    "ativar modo de escuta",
    "iniciar protoclo ouvir",
    "ativar comando de voz"
]

print("=" * 55)
print("1. TESTANDO PALAVRAS INDIVIDUAIS:")
print("=" * 55)

palavras_validas = set()
for palavra in PALAVRAS_INDIVIDUAIS:
    # Se a palavra faltar, o Vosk cospe WARNING no terminal
    rec = KaldiRecognizer(model, 16000, json.dumps([palavra, "[unk]"]))
    # Se não houver crash/aviso crítico, consideramos o termo
    palavras_validas.add(palavra)

print("\n" + "=" * 55)
print("2. TESTANDO FRASES COMPLETAS:")
print("=" * 55)

for frase in FRASES_CANDIDATAS:
    print(f"\n[Verificando frase]: '{frase}'")
    rec = KaldiRecognizer(
        model, 16000, json.dumps(frase.split() + ["[unk]"])
    )

print("\n" + "=" * 55)
print("Fim do teste. As frases sem WARNING podem ser usadas direto.")
print("=" * 55)