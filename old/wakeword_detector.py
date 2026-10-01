import json
import os
import sys
import wave
from vosk import KaldiRecognizer, Model, SetLogLevel

# Reduz logs desnecessários da engine Kaldi/Vosk (0 desativa avisos comuns)
SetLogLevel(-1)

# ================= CONFIGURAÇÕES =================
MODEL_PATH = "vosk-model-small-pt-0.3"
AUDIO_PATH = "entrada_vosk2.wav"

# Palavras-chave desejadas (devem estar no vocabulário do modelo)
WAKEWORDS = ["ei iuca", "hey iuca", "hey yuka", "ei yuka"]
# =================================================


def verificar_audio(wf: wave.Wave_read) -> bool:
    """Valida se o áudio atende aos padrões exigidos pelo Vosk."""
    if wf.getnchannels() != 1:
        print(
            "Erro: O áudio deve ser Mono (1 canal).",
            file=sys.stderr,
        )
        return False
    if wf.getsampwidth() != 2:
        print(
            "Erro: O áudio deve ser PCM 16-bit.",
            file=sys.stderr,
        )
        return False
    return True


def detectar_wakeword(
    audio_file: str, model_dir: str, wakewords: list[str]
) -> bool:
    if not os.path.exists(model_dir):
        print(
            f"Erro: Modelo não encontrado na pasta '{model_dir}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.exists(audio_file):
        print(
            f"Erro: Arquivo '{audio_file}' não encontrado.",
            file=sys.stderr,
        )
        sys.exit(1)

    model = Model(model_dir)

    with wave.open(audio_file, "rb") as wf:
        if not verificar_audio(wf):
            sys.exit(1)

        taxa_amostragem = wf.getframerate()

        # Define a gramática restrita em JSON.
        # '[unk]' absorve qualquer som/fala que não seja a wakeword
        grammar = json.dumps(wakewords + ["[unk]"])
        rec = KaldiRecognizer(model, taxa_amostragem, grammar)

        # Processa o áudio em chunks (blocos de 4000 frames)
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                resultado = json.loads(rec.Result())
                texto = resultado.get("text", "")
                if any(w in texto for w in wakewords):
                    return True

        # Checa o resultado final residual
        resultado_final = json.loads(rec.FinalResult())
        texto_final = resultado_final.get("text", "")
        if any(w in texto_final for w in wakewords):
            return True

    return False


if __name__ == "__main__":
    detectou = detectar_wakeword(AUDIO_PATH, MODEL_PATH, WAKEWORDS)

    if detectou:
        print("SIM")
    else:
        print("NÃO")