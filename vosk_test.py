import json
import math
import struct
import wave
from vosk import KaldiRecognizer, Model, SetLogLevel

# Ativa mensagens informativas do Vosk
SetLogLevel(0)

AUDIO_PATH = "entrada_vosk4.wav"
MODEL_PATH = "vosk-model-small-pt-0.3"


def calcular_rms(dados_brutos: bytes) -> float:
    """Calcula o volume RMS de um áudio PCM 16-bit sem depender de bibliotecas externas."""
    total_amostras = len(dados_brutos) // 2
    if total_amostras == 0:
        return 0.0

    # Desempacota os bytes como inteiros com sinal de 16-bit (short - 'h')
    amostras = struct.unpack(f"<{total_amostras}h", dados_brutos)
    soma_quadrados = sum(amostra**2 for amostra in amostras)
    return math.sqrt(soma_quadrados / total_amostras)


# 1. Inspeciona o arquivo de áudio
with wave.open(AUDIO_PATH, "rb") as wf:
    canais = wf.getnchannels()
    largura_amostra = wf.getsampwidth()
    taxa = wf.getframerate()
    frames = wf.getnframes()
    duracao = frames / float(taxa) if taxa > 0 else 0
    conteudo_bruto = wf.readframes(frames)

    rms = (
        calcular_rms(conteudo_bruto)
        if largura_amostra == 2
        else "N/A (não é 16-bit)"
    )

print("=" * 40)
print(f"Duração: {duracao:.2f} segundos")
print(f"Canais: {canais} (Esperado: 1)")
print(f"Taxa: {taxa} Hz (Esperado: 16000)")
print(f"Sample Width: {largura_amostra * 8}-bit (Esperado: 16-bit)")
print(
    f"Volume RMS: {rms:.1f} (Se for menor que ~300, o microfone gravou muito baixo)"
)
print("=" * 40)

# 2. Executa a transcrição acumulando blocos intermediários e finais
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, taxa)

wf = wave.open(AUDIO_PATH, "rb")
frases_detectadas = []

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        texto = res.get("text", "")
        if texto:
            frases_detectadas.append(texto)

# Captura o residual final
res_final = json.loads(rec.FinalResult())
texto_final = res_final.get("text", "")
if texto_final:
    frases_detectadas.append(texto_final)

wf.close()

transcricao_completa = " ".join(frases_detectadas).strip()
print(f"Transcrição Completa: '{transcricao_completa}'")