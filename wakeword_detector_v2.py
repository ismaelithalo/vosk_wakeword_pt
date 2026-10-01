import json
import os
import sys
import wave
from vosk import KaldiRecognizer, Model, SetLogLevel

# Suprime logs de depuração do Kaldi
SetLogLevel(-1)

# ================= CONFIGURAÇÕES =================
MODEL_PATH = "vosk-model-small-pt-0.3"
AUDIO_PATH = "entrada_vosk4.wav"

# Frases validadas no vocabulário do modelo
WAKEWORDS = [
    "comando de voz",
    "modo de escuta",
    "protocolo ouvir",
    "ativar modo de escuta",
    "ativar comando de voz",
    "iniciar protocolo ouvir",
]
# =================================================


def verificar_audio(wf: wave.Wave_read) -> bool:
    if wf.getnchannels() != 1:
        print("Erro: O áudio deve ser Mono (1 canal).", file=sys.stderr)
        return False
    if wf.getsampwidth() != 2:
        print("Erro: O áudio deve ser PCM 16-bit.", file=sys.stderr)
        return False
    return True


def detectar_wakeword(
    audio_file: str, model_dir: str, wakewords: list[str]
) -> bool:
    if not os.path.exists(model_dir):
        print(f"Erro: Modelo '{model_dir}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(audio_file):
        print(f"Erro: Áudio '{audio_file}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    model = Model(model_dir)

    with wave.open(audio_file, "rb") as wf:
        if not verificar_audio(wf):
            sys.exit(1)

        taxa_amostragem = wf.getframerate()

        # Monta a gramática restrita com as frases completas + [unk]
        # O [unk] absorve qualquer outra fala para não gerar falso positivo
        grammar = json.dumps(wakewords + ["[unk]"])
        rec = KaldiRecognizer(model, taxa_amostragem, grammar)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                texto = res.get("text", "")
                if any(w in texto for w in wakewords):
                    return True

        res_final = json.loads(rec.FinalResult())
        texto_final = res_final.get("text", "")
        if any(w in texto_final for w in wakewords):
            return True

    return False


if __name__ == "__main__":
    if detectar_wakeword(AUDIO_PATH, MODEL_PATH, WAKEWORDS):
        print("SIM")
    else:
        print("NÃO")