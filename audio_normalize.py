import subprocess
import sys
from pathlib import Path


def converter_para_vosk(
    arquivo_entrada: str, arquivo_saida: str, sample_rate: int = 16000
) -> bool:
    """Converte um arquivo de áudio para PCM 16-bit mono no sample rate

    especificado (padrão Vosk: 16 kHz).
    """
    caminho_in = Path(arquivo_entrada)
    caminho_out = Path(arquivo_saida)

    if not caminho_in.exists():
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
        return False

    # Parâmetros FFmpeg para compatibilidade com Vosk:
    # -y: sobrescreve se o arquivo já existir
    # -i: arquivo de entrada
    # -vn: desativa faixas de vídeo (caso a entrada seja um .mp4/.mkv)
    # -acodec pcm_s16le: codificação PCM signed 16-bit little-endian
    # -ac 1: mono (1 canal de áudio)
    # -ar: taxa de amostragem (16000 Hz)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(caminho_in),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(caminho_out),
    ]

    try:
        resultado = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        print(f"Áudio convertido com sucesso: '{caminho_out}'")
        return True
    except FileNotFoundError:
        print(
            "Erro: O executável 'ffmpeg' não está instalado ou não está no PATH do sistema."
        )
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erro na conversão pelo FFmpeg:\n{e.stderr}")
        return False


if __name__ == "__main__":
    # Exemplo de uso:
    # python converter_vosk.py audio_original.wav audio_pronto_vosk.wav
    if len(sys.argv) >= 3:
        entrada = sys.argv[1]
        saida = sys.argv[2]
    else:
        entrada = "entrada_com.m4a"
        saida = "entrada_vosk2.wav"

    converter_para_vosk(entrada, saida)