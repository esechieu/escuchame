import os

import sounddevice as sd
from faster_whisper import WhisperModel
from scipy.io.wavfile import write

# ==============================
# CONFIGURACIÓN
# ==============================

DURACION = 5  # duración de grabación en segundos
FS = 16000  # frecuencia de muestreo
ARCHIVO_SALIDA = "temp_audio/mic_input.wav"

# ==============================
# GRABACIÓN DE AUDIO
# ==============================

os.makedirs("temp_audio", exist_ok=True)
print(f"🎙️ Grabando audio del micrófono durante {DURACION} segundos...")

audio = sd.rec(int(DURACION * FS), samplerate=FS, channels=1, dtype="int16")
sd.wait()

write(ARCHIVO_SALIDA, FS, audio)
print(f"✅ Audio guardado en: {ARCHIVO_SALIDA}")

# ==============================
# TRANSCRIPCIÓN CON WHISPER
# ==============================

print("🤖 Transcribiendo audio...")

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(ARCHIVO_SALIDA, beam_size=5)

print("🌍 Idioma detectado:", info.language)

print("\n📋 Subtítulos:")
for segment in segments:
    print(f"[{segment.start:.2f} → {segment.end:.2f}] {segment.text}")


def format_time(seconds):
    """Convierte segundos a formato SRT: hh:mm:ss,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# Guardar como archivo .srt
srt_path = "temp_audio/subtitulos.srt"
with open(srt_path, "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments, start=1):
        f.write(f"{i}\n")
        f.write(f"{format_time(segment.start)} --> {format_time(segment.end)}\n")
        f.write(f"{segment.text.strip()}\n\n")

print(f"\n📄 Subtítulos guardados en formato .srt: {srt_path}")
